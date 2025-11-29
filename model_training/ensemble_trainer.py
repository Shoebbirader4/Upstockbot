"""Ensemble model trainer for improved predictions"""

import numpy as np
import pandas as pd
from sklearn.ensemble import VotingClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.neural_network import MLPClassifier
from utils.logger import log

class EnsembleTrainer:
    """Train ensemble of multiple models"""
    
    def __init__(self, registry_path: str = "./models"):
        self.registry_path = registry_path
        self.ensemble = None
        self.feature_columns = None
    
    def train(self, df: pd.DataFrame, feature_columns: list, target_column: str = 'target',
              train_split: float = 0.8, **model_params) -> dict:
        """Train ensemble of models"""
        
        self.feature_columns = feature_columns
        X = df[feature_columns].values
        y = df[target_column].values
        
        # Chronological split
        split_idx = int(len(X) * train_split)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        log.info(f"Training ensemble - Train: {len(X_train)}, Val: {len(X_val)}")
        
        # Calculate class weights
        class_weights = self._calculate_class_weights(y_train)
        sample_weights = np.array([class_weights[int(y)] for y in y_train])
        
        # Create individual models
        xgb_model = xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            max_depth=model_params.get('max_depth', 6),
            learning_rate=model_params.get('learning_rate', 0.05),
            n_estimators=model_params.get('n_estimators', 200),
            random_state=42
        )
        
        lgb_model = lgb.LGBMClassifier(
            objective='multiclass',
            num_class=3,
            max_depth=model_params.get('max_depth', 6),
            learning_rate=model_params.get('learning_rate', 0.05),
            n_estimators=model_params.get('n_estimators', 200),
            random_state=42,
            verbose=-1
        )
        
        mlp_model = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            max_iter=200,
            random_state=42,
            early_stopping=True
        )
        
        # Create ensemble
        self.ensemble = VotingClassifier(
            estimators=[
                ('xgb', xgb_model),
                ('lgb', lgb_model),
                ('mlp', mlp_model)
            ],
            voting='soft',  # Use probability voting
            weights=[2, 2, 1]  # Give more weight to tree models
        )
        
        # Train ensemble
        log.info("Training ensemble models...")
        self.ensemble.fit(X_train, y_train, sample_weight=sample_weights)
        
        # Evaluate
        metrics = self._evaluate(X_val, y_val)
        
        log.info(f"Ensemble trained - F1 Macro: {metrics['f1_macro']:.4f}")
        
        return metrics
    
    def _calculate_class_weights(self, y: np.ndarray) -> dict:
        """Calculate balanced class weights"""
        unique, counts = np.unique(y, return_counts=True)
        total = len(y)
        weights = {int(cls): total / (len(unique) * count) for cls, count in zip(unique, counts)}
        return weights
    
    def _evaluate(self, X_val, y_val) -> dict:
        """Evaluate ensemble performance"""
        from sklearn.metrics import classification_report, confusion_matrix, f1_score
        
        y_pred = self.ensemble.predict(X_val)
        
        report = classification_report(y_val, y_pred, output_dict=True,
                                      target_names=['Sell', 'Hold', 'Buy'])
        cm = confusion_matrix(y_val, y_pred)
        
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
        
        return metrics
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get probability predictions"""
        if self.ensemble is None:
            log.error("Ensemble not trained")
            return np.array([])
        return self.ensemble.predict_proba(X)
    
    def save_model(self, version: str = None) -> str:
        """Save ensemble model"""
        import joblib
        from pathlib import Path
        from datetime import datetime
        
        if self.ensemble is None:
            log.error("No ensemble to save")
            return ""
        
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_path = Path(self.registry_path) / f"ensemble_model_{version}.pkl"
        
        model_artifact = {
            'model': self.ensemble,
            'feature_columns': self.feature_columns,
            'model_type': 'ensemble',
            'version': version,
            'timestamp': datetime.now().isoformat()
        }
        
        joblib.dump(model_artifact, model_path)
        log.info(f"Ensemble saved to {model_path}")
        
        return str(model_path)
    
    def load_model(self, model_path: str):
        """Load ensemble model"""
        import joblib
        from pathlib import Path
        
        if not Path(model_path).exists():
            log.error(f"Model file not found: {model_path}")
            return False
        
        model_artifact = joblib.load(model_path)
        self.ensemble = model_artifact['model']
        self.feature_columns = model_artifact['feature_columns']
        
        log.info(f"Ensemble loaded from {model_path}")
        return True
