import pandas as pd
import numpy as np
from utils.logger import log

class TargetLabeler:
    def __init__(self, horizon_bars: int = 3, buy_threshold: float = 0.001, 
                 sell_threshold: float = -0.001, use_dynamic_thresholds: bool = True):
        self.horizon_bars = horizon_bars
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.use_dynamic_thresholds = use_dynamic_thresholds
    
    def create_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target labels for classification"""
        if df.empty or len(df) < self.horizon_bars + 1:
            log.warning("Insufficient data for label creation")
            return df
        
        df = df.copy()
        
        # Calculate future return (no lookahead bias - using shift(-horizon))
        df['future_close'] = df['close'].shift(-self.horizon_bars)
        df['future_return'] = (df['future_close'] - df['close']) / df['close']
        
        # Use dynamic thresholds based on volatility
        if self.use_dynamic_thresholds:
            # Calculate rolling volatility
            returns = df['close'].pct_change()
            rolling_std = returns.rolling(window=20).std()
            
            # Set thresholds as multiples of volatility
            buy_threshold_dynamic = rolling_std * 0.5  # 0.5 std for buy
            sell_threshold_dynamic = -rolling_std * 0.5  # -0.5 std for sell
            
            # Create labels with dynamic thresholds
            df['target'] = 1  # Hold
            df.loc[df['future_return'] > buy_threshold_dynamic, 'target'] = 2  # Buy
            df.loc[df['future_return'] < sell_threshold_dynamic, 'target'] = 0  # Sell
        else:
            # Use fixed thresholds
            df['target'] = 1  # Hold
            df.loc[df['future_return'] > self.buy_threshold, 'target'] = 2  # Buy
            df.loc[df['future_return'] < self.sell_threshold, 'target'] = 0  # Sell
        
        # Drop rows where we can't calculate future return
        df = df.dropna(subset=['future_return'])
        
        # Log class distribution
        class_counts = df['target'].value_counts().sort_index()
        total = len(df)
        log.info(f"Label distribution - Sell: {class_counts.get(0, 0)} ({class_counts.get(0, 0)/total*100:.1f}%), "
                f"Hold: {class_counts.get(1, 0)} ({class_counts.get(1, 0)/total*100:.1f}%), "
                f"Buy: {class_counts.get(2, 0)} ({class_counts.get(2, 0)/total*100:.1f}%)")
        
        # Check for severe class imbalance
        min_class_pct = min(class_counts) / total * 100
        if min_class_pct < 5:
            log.warning(f"Severe class imbalance detected! Minimum class: {min_class_pct:.1f}%")
            log.warning("Consider adjusting thresholds or using SMOTE for balancing")
        
        # Drop temporary columns
        df = df.drop(['future_close'], axis=1)
        
        return df
    
    def get_signal_from_proba(self, proba: np.ndarray) -> int:
        """Convert probability array to signal (0=Sell, 1=Hold, 2=Buy)"""
        return int(np.argmax(proba))
    
    def get_confidence(self, proba: np.ndarray) -> float:
        """Get confidence of prediction"""
        return float(np.max(proba))
