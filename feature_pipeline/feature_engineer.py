import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from utils.logger import log

class FeatureEngineer:
    def __init__(self):
        self.scaler = RobustScaler()
        self.scaler_fitted = False
        self.features_to_scale = []
    
    def create_features(self, df: pd.DataFrame, fit_scaler: bool = False) -> pd.DataFrame:
        """Create all features from OHLCV data"""
        if df.empty or len(df) < 50:
            log.warning("Insufficient data for feature creation")
            return df
        
        df = df.copy()
        
        # Momentum features
        df = self._add_momentum_features(df)
        
        # Trend features
        df = self._add_trend_features(df)
        
        # Volatility features
        df = self._add_volatility_features(df)
        
        # Mean reversion features
        df = self._add_mean_reversion_features(df)
        
        # Volume features
        df = self._add_volume_features(df)
        
        # Time context features
        df = self._add_time_features(df)
        
        # Drop NaN rows created by rolling windows
        initial_len = len(df)
        df = df.dropna()
        if len(df) < initial_len:
            log.info(f"Dropped {initial_len - len(df)} rows with NaN after feature creation")
        
        # Scale features
        if fit_scaler or not self.scaler_fitted:
            df = self._fit_and_scale_features(df)
        else:
            df = self._scale_features(df)
        
        return df
    
    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based features"""
        df['EMA_5'] = df['close'].ewm(span=5, adjust=False).mean()
        df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['EMA_Cross'] = (df['EMA_5'] - df['EMA_10']) / df['close']
        df['EMA_Slope'] = df['EMA_5'].diff(3) / df['close']
        return df
    
    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend-based features"""
        # Handle zero volume (e.g., for indices) - use simple moving average instead
        if (df['volume'] == 0).all():
            # If all volume is zero, use SMA instead of VWAP
            df['VWAP'] = df['close'].rolling(window=20).mean()
        else:
            volume_sum = df['volume'].rolling(window=20).sum()
            df['VWAP'] = (df['close'] * df['volume']).rolling(window=20).sum() / \
                         volume_sum.replace(0, 1)  # Avoid division by zero
        
        df['VWAP_Distance'] = (df['close'] - df['VWAP']) / df['close']
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based features"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift(1))
        low_close = abs(df['low'] - df['close'].shift(1))
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR_14'] = true_range.rolling(window=14).mean()
        df['Normalized_ATR'] = df['ATR_14'] / df['close']
        return df
    
    def _add_mean_reversion_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add mean reversion features"""
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))
        
        # Z-Score of returns
        returns = df['close'].pct_change()
        df['Rolling_ZScore_Return'] = (returns - returns.rolling(window=20).mean()) / \
                                       returns.rolling(window=20).std()
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        # Handle zero volume (e.g., for indices)
        volume_mean = df['volume'].rolling(window=20).mean()
        volume_mean = volume_mean.replace(0, 1)  # Avoid division by zero
        df['Volume_Ratio_20'] = df['volume'] / volume_mean
        df['Volume_Ratio_20'] = df['Volume_Ratio_20'].replace([np.inf, -np.inf], 1.0)  # Handle inf
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time context features"""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Cyclic encoding
        df['Hour_Cyclic_Sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['Hour_Cyclic_Cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['Day_Cyclic_Sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['Day_Cyclic_Cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        df = df.drop(['hour', 'day_of_week'], axis=1)
        return df
    
    def _fit_and_scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit scaler and scale features"""
        self.features_to_scale = [
            'EMA_Cross', 'EMA_Slope', 'VWAP_Distance', 'Normalized_ATR',
            'RSI_14', 'Rolling_ZScore_Return', 'Volume_Ratio_20'
        ]
        
        available_features = [f for f in self.features_to_scale if f in df.columns]
        
        if available_features:
            df[available_features] = self.scaler.fit_transform(df[available_features])
            self.scaler_fitted = True
            log.info(f"Fitted scaler on {len(available_features)} features")
        
        return df
    
    def _scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale features using fitted scaler"""
        available_features = [f for f in self.features_to_scale if f in df.columns]
        
        if available_features and self.scaler_fitted:
            df[available_features] = self.scaler.transform(df[available_features])
        
        return df
    
    def get_feature_columns(self) -> list:
        """Get list of feature column names"""
        return [
            'EMA_5', 'EMA_10', 'EMA_Cross', 'EMA_Slope',
            'VWAP', 'VWAP_Distance',
            'ATR_14', 'Normalized_ATR',
            'RSI_14', 'Rolling_ZScore_Return',
            'Volume_Ratio_20',
            'Hour_Cyclic_Sin', 'Hour_Cyclic_Cos',
            'Day_Cyclic_Sin', 'Day_Cyclic_Cos'
        ]
