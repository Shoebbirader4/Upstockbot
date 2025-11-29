import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from utils.logger import log
from utils.config_loader import config
from data_ingestion.data_validator import DataValidator

class DataFetcher:
    def __init__(self, source: str = "zerodha"):
        self.source = source
        self.validator = DataValidator()
    
    def fetch_historical(self, symbol: str, start_date: datetime, 
                        end_date: datetime, interval: str = "3minute") -> pd.DataFrame:
        """Fetch historical OHLCV data"""
        try:
            if self.source == "zerodha":
                df = self._fetch_zerodha_historical(symbol, start_date, end_date, interval)
            elif self.source == "upstox":
                df = self._fetch_upstox_historical(symbol, start_date, end_date, interval)
            else:
                df = self._fetch_fallback_data(symbol, start_date, end_date)
            
            df = self.validator.validate_ohlcv(df)
            log.info(f"Fetched {len(df)} bars for {symbol}")
            return df
            
        except Exception as e:
            log.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def _fetch_zerodha_historical(self, symbol: str, start_date: datetime,
                                  end_date: datetime, interval: str) -> pd.DataFrame:
        """Fetch from Zerodha Kite API"""
        # Placeholder - implement actual Kite API integration
        log.warning("Zerodha API not implemented - using mock data")
        return self._generate_mock_data(start_date, end_date)
    
    def _fetch_upstox_historical(self, symbol: str, start_date: datetime,
                                end_date: datetime, interval: str) -> pd.DataFrame:
        """Fetch from Upstox API"""
        try:
            from data_ingestion.upstox_client import UpstoxClient
            
            client = UpstoxClient()
            
            # Get instrument key for symbol
            instrument_key = client.get_instrument_key(symbol)
            
            if not instrument_key:
                log.error("Could not get instrument key, using mock data")
                return self._generate_mock_data(start_date, end_date)
            
            # Fetch historical data
            df = client.get_historical_data(
                instrument_key=instrument_key,
                interval=interval,
                from_date=start_date,
                to_date=end_date
            )
            
            if df.empty:
                log.warning("No data from Upstox, using mock data")
                return self._generate_mock_data(start_date, end_date)
            
            return df
            
        except Exception as e:
            log.error(f"Upstox fetch failed: {e}, using mock data")
            return self._generate_mock_data(start_date, end_date)
    
    def _fetch_fallback_data(self, symbol: str, start_date: datetime,
                            end_date: datetime) -> pd.DataFrame:
        """Fallback data source"""
        log.warning("Using fallback mock data")
        return self._generate_mock_data(start_date, end_date)
    
    def _generate_mock_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate mock OHLCV data for testing"""
        dates = pd.date_range(start=start_date, end=end_date, freq='3min')
        
        # Filter market hours (9:15 - 15:30)
        dates = dates[
            (dates.time >= pd.Timestamp("09:15").time()) &
            (dates.time <= pd.Timestamp("15:30").time()) &
            (dates.dayofweek < 5)
        ]
        
        n = len(dates)
        base_price = 19500
        
        # Generate realistic price movements
        import numpy as np
        returns = pd.Series(index=dates, data=0.0)
        returns.iloc[0] = 0
        for i in range(1, n):
            returns.iloc[i] = returns.iloc[i-1] * 0.95 + np.random.randn() * 0.0005
        
        close = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close * (1 + np.random.randn(n) * 0.0002),
            'high': close * (1 + abs(np.random.randn(n)) * 0.0003),
            'low': close * (1 - abs(np.random.randn(n)) * 0.0003),
            'close': close,
            'volume': np.random.randint(1000, 10000, n)
        })
        
        # Ensure OHLC consistency
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        return df
