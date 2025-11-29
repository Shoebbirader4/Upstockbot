import pandas as pd
import numpy as np
from typing import Dict
from model_training.trainer import ModelTrainer
from feature_pipeline.feature_engineer import FeatureEngineer
from utils.logger import log

class SignalGenerator:
    def __init__(self, model_path: str):
        self.trainer = ModelTrainer()
        self.engineer = FeatureEngineer()
        
        if not self.trainer.load_model(model_path):
            raise ValueError(f"Failed to load model from {model_path}")
        
        log.info(f"Signal generator initialized with model: {model_path}")
    
    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """Generate trading signal from latest data"""
        
        if df.empty or len(df) < 50:
            log.warning("Insufficient data for signal generation")
            return {
                'signal': 1,  # Hold
                'confidence': 0.0,
                'probabilities': [0.33, 0.34, 0.33],
                'error': 'Insufficient data'
            }
        
        # Create features
        df_features = self.engineer.create_features(df.copy(), fit_scaler=False)
        
        if df_features.empty:
            log.error("Feature creation failed")
            return {
                'signal': 1,
                'confidence': 0.0,
                'probabilities': [0.33, 0.34, 0.33],
                'error': 'Feature creation failed'
            }
        
        # Get latest row features
        latest_features = df_features[self.trainer.feature_columns].iloc[-1:].values
        
        # Predict
        probas = self.trainer.predict_proba(latest_features)[0]
        signal = int(np.argmax(probas))
        confidence = float(np.max(probas))
        
        result = {
            'signal': signal,  # 0=Sell, 1=Hold, 2=Buy
            'confidence': confidence,
            'probabilities': probas.tolist(),
            'timestamp': df_features['timestamp'].iloc[-1],
            'close_price': df_features['close'].iloc[-1]
        }
        
        signal_name = ['SELL', 'HOLD', 'BUY'][signal]
        log.info(f"Signal: {signal_name}, Confidence: {confidence:.2%}, "
                f"Probas: {probas}")
        
        return result
