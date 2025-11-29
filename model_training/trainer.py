import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import xgboost as xgb
import lightgbm as lgb
import joblib
from pathlib import Path
from datetime import datetime
from utils.logger import log

class ModelTrainer:
    def __init__(self, model_type: str = "xgboost", registry_path: str = "./models"):
        self.model_type = model_type
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.feature_columns = None
    
    def train(self, df: pd.DataFrame, feature_columns: list, target_column: str = 'target',
              train_split: float = 0.8, **model_params) -> dict:
        """Train classification model"""
        
        if df.empty or target_column not in df.columns:
            log.error("Invalid training data")
            return {}
        
        self.feature_columns = feature_columns
        X = df[feature_columns].values
        y = df[target_column].values
        
        # Chronological split (no shuffle)
        split_idx = int(len(X) * train_split)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        log.info(f"Training set: {len(X_train)}, Validation set: {len(X_val)}")
        
        # Calculate class weights
        class_weights = self._calculate_class_weights(y_train)
        
        # Train model
        if self.model_type == "xgboost":
            self.model = self._train_xgboost(X_train, y_train, X_val, y_val, 
                                             class_weights, **model_params)
        elif self.model_type == "lightgbm":
            self.model = self._train_lightgbm(X_train, y_train, X_val, y_val,
                                              class_weights, **model_params)
        else:
            log.error(f"Unsupported model type: {self.model_type}")
            return {}
        
        # Evaluate
        metrics = self._evaluate(X_val, y_val)
        
        return metrics
    
    def _train_xgboost(self, X_train, y_train, X_val, y_val, class_weights, **params):
        """Train XGBoost classifier"""
        default_params = {
            'objective': 'multi:softprob',
            'num_class': 3,
            'max_depth': params.get('max_depth', 6),
            'learning_rate': params.get('learning_rate', 0.05),
            'n_estimators': params.get('n_estimators', 200),
            'eval_metric': 'mlogloss',
            'early_stopping_rounds': params.get('early_stopping_rounds', 50),
            'random_state': 42
        }
        
        # Apply class weights
        sample_weights = np.array([class_weights[int(y)] for y in y_train])
        
        model = xgb.XGBClassifier(**default_params)
        model.fit(
            X_train, y_train,
            sample_weight=sample_weights,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        log.info(f"XGBoost training completed. Best iteration: {model.best_iteration}")
        return model
    
    def _train_lightgbm(self, X_train, y_train, X_val, y_val, class_weights, **params):
        """Train LightGBM classifier"""
        default_params = {
            'objective': 'multiclass',
            'num_class': 3,
            'max_depth': params.get('max_depth', 6),
            'learning_rate': params.get('learning_rate', 0.05),
            'n_estimators': params.get('n_estimators', 200),
            'metric': 'multi_logloss',
            'random_state': 42,
            'verbose': -1
        }
        
        sample_weights = np.array([class_weights[int(y)] for y in y_train])
        
        model = lgb.LGBMClassifier(**default_params)
        model.fit(
            X_train, y_train,
            sample_weight=sample_weights,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(stopping_rounds=params.get('early_stopping_rounds', 50))]
        )
        
        log.info(f"LightGBM training completed")
        return model
    
    def _calculate_class_weights(self, y: np.ndarray) -> dict:
        """Calculate balanced class weights"""
        unique, counts = np.unique(y, return_counts=True)
        total = len(y)
        weights = {int(cls): total / (len(unique) * count) for cls, count in zip(unique, counts)}
        log.info(f"Class weights: {weights}")
        return weights
    
    def _evaluate(self, X_val, y_val) -> dict:
        """Evaluate model performance"""
        y_pred = self.model.predict(X_val)
        y_proba = self.model.predict_proba(X_val)
        
        # Classification metrics
        report = classification_report(y_val, y_pred, output_dict=True, 
                                      target_names=['Sell', 'Hold', 'Buy'])
        cm = confusion_matrix(y_val, y_pred)
        
        # F1 scores
        f1_macro = f1_score(y_val, y_pred, average='macro')
        f1_buy = report['Buy']['f1-score']
        f1_sell = report['Sell']['f1-score']
        
        metrics = {
            'f1_macro': f1_macro,
            'f1_buy': f1_buy,
            'f1_sell': f1_sell,
            'accuracy': report['accuracy'],
            'confusion_matrix': cm.tolist(),
            'classification_report': report
        }
        
        log.info(f"Validation Metrics - F1 Macro: {f1_macro:.4f}, "
                f"F1 Buy: {f1_buy:.4f}, F1 Sell: {f1_sell:.4f}")
        
        return metrics
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get probability predictions"""
        if self.model is None:
            log.error("Model not trained")
            return np.array([])
        return self.model.predict_proba(X)
    
    def save_model(self, version: str = None) -> str:
        """Save model to registry"""
        if self.model is None:
            log.error("No model to save")
            return ""
        
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_path = self.registry_path / f"model_{self.model_type}_{version}.pkl"
        
        model_artifact = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'model_type': self.model_type,
            'version': version,
            'timestamp': datetime.now().isoformat()
        }
        
        joblib.dump(model_artifact, model_path)
        log.info(f"Model saved to {model_path}")
        
        return str(model_path)
    
    def load_model(self, model_path: str):
        """Load model from registry"""
        if not Path(model_path).exists():
            log.error(f"Model file not found: {model_path}")
            return False
        
        model_artifact = joblib.load(model_path)
        self.model = model_artifact['model']
        self.feature_columns = model_artifact['feature_columns']
        self.model_type = model_artifact['model_type']
        
        log.info(f"Model loaded from {model_path}")
        return True
