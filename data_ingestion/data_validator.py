import pandas as pd
import numpy as np
from utils.logger import log

class DataValidator:
    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean OHLCV data"""
        if df.empty:
            log.warning("Empty dataframe received")
            return df
        
        # Remove duplicates
        initial_len = len(df)
        df = df.drop_duplicates(subset=['timestamp'], keep='last')
        if len(df) < initial_len:
            log.warning(f"Removed {initial_len - len(df)} duplicate rows")
        
        # Validate OHLC relationships
        invalid_ohlc = (df['high'] < df['low']) | (df['high'] < df['open']) | \
                       (df['high'] < df['close']) | (df['low'] > df['open']) | \
                       (df['low'] > df['close'])
        
        if invalid_ohlc.any():
            log.warning(f"Found {invalid_ohlc.sum()} rows with invalid OHLC relationships")
            df = df[~invalid_ohlc]
        
        # Remove rows with zero or negative prices
        invalid_prices = (df[['open', 'high', 'low', 'close']] <= 0).any(axis=1)
        if invalid_prices.any():
            log.warning(f"Removed {invalid_prices.sum()} rows with invalid prices")
            df = df[~invalid_prices]
        
        # Remove rows with negative volume
        if (df['volume'] < 0).any():
            log.warning(f"Removed {(df['volume'] < 0).sum()} rows with negative volume")
            df = df[df['volume'] >= 0]
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    @staticmethod
    def fill_missing_bars(df: pd.DataFrame, freq: str = '3min') -> pd.DataFrame:
        """Fill missing bars with forward fill"""
        if df.empty:
            return df
        
        df = df.set_index('timestamp')
        
        # Create complete time range
        full_range = pd.date_range(
            start=df.index.min(),
            end=df.index.max(),
            freq=freq
        )
        
        # Reindex and forward fill
        df = df.reindex(full_range)
        missing_count = df['close'].isna().sum()
        
        if missing_count > 0:
            log.warning(f"Filling {missing_count} missing bars with forward fill")
            df = df.fillna(method='ffill')
        
        df = df.reset_index().rename(columns={'index': 'timestamp'})
        return df
