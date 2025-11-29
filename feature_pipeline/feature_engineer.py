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
        
        # Advanced features
        df = self._add_advanced_momentum_features(df)
        df = self._add_advanced_volatility_features(df)
        df = self._add_price_action_features(df)
        df = self._add_multi_timeframe_features(df)
        
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
            'RSI_14', 'Rolling_ZScore_Return', 'Volume_Ratio_20',
            'MACD', 'MACD_Signal', 'MACD_Histogram', 'ROC_5', 'ROC_10',
            'Momentum_10', 'BB_Width', 'BB_Position', 'Historical_Volatility',
            'Body_Size', 'Upper_Shadow', 'Lower_Shadow', 'High_Low_Range',
            'Price_vs_SMA50', 'Price_vs_SMA200', 'ADX'
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
    
    def _add_advanced_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced momentum indicators"""
        # MACD
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Rate of Change
        df['ROC_5'] = df['close'].pct_change(5)
        df['ROC_10'] = df['close'].pct_change(10)
        
        # Momentum
        df['Momentum_10'] = df['close'] - df['close'].shift(10)
        
        return df
    
    def _add_advanced_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced volatility indicators"""
        # Bollinger Bands
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        df['BB_Upper'] = sma_20 + (std_20 * 2)
        df['BB_Lower'] = sma_20 - (std_20 * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / sma_20
        df['BB_Position'] = (df['close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Historical Volatility
        returns = df['close'].pct_change()
        df['Historical_Volatility'] = returns.rolling(window=20).std() * np.sqrt(252)
        
        return df
    
    def _add_price_action_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price action features"""
        # Candle patterns
        df['Body_Size'] = abs(df['close'] - df['open']) / df['close']
        df['Upper_Shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close']
        df['Lower_Shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['close']
        
        # Price position
        df['High_Low_Range'] = (df['high'] - df['low']) / df['close']
        df['Close_Position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        return df
    
    def _add_multi_timeframe_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add multi-timeframe features"""
        # Longer timeframe trends
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['SMA_200'] = df['close'].rolling(window=200).mean()
        df['Price_vs_SMA50'] = (df['close'] - df['SMA_50']) / df['close']
        df['Price_vs_SMA200'] = (df['close'] - df['SMA_200']) / df['close']
        
        # Trend strength
        df['ADX'] = self._calculate_adx(df)
        
        return df
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Directional Movement
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_dm = pd.Series(plus_dm, index=df.index).rolling(window=period).mean()
        minus_dm = pd.Series(minus_dm, index=df.index).rolling(window=period).mean()
        
        # Directional Indicators
        plus_di = 100 * (plus_dm / atr)
        minus_di = 100 * (minus_dm / atr)
        
        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    def get_feature_columns(self) -> list:
        """Get list of feature column names"""
        return [
            # Original features
            'EMA_5', 'EMA_10', 'EMA_Cross', 'EMA_Slope',
            'VWAP', 'VWAP_Distance',
            'ATR_14', 'Normalized_ATR',
            'RSI_14', 'Rolling_ZScore_Return',
            'Volume_Ratio_20',
            'Hour_Cyclic_Sin', 'Hour_Cyclic_Cos',
            'Day_Cyclic_Sin', 'Day_Cyclic_Cos',
            # Advanced momentum
            'MACD', 'MACD_Signal', 'MACD_Histogram',
            'ROC_5', 'ROC_10', 'Momentum_10',
            # Advanced volatility
            'BB_Width', 'BB_Position', 'Historical_Volatility',
            # Price action
            'Body_Size', 'Upper_Shadow', 'Lower_Shadow',
            'High_Low_Range', 'Close_Position',
            # Multi-timeframe
            'Price_vs_SMA50', 'Price_vs_SMA200', 'ADX'
        ]
