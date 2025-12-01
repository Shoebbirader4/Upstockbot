"""Upstox WebSocket client for real-time market data"""

import json
import threading
import time
from datetime import datetime, timedelta
from collections import deque
import pandas as pd
from utils.logger import log
from utils.config_loader import config
from data_ingestion.upstox_client import UpstoxClient

class UpstoxWebSocket:
    """Upstox live data feed using REST API polling (real market data)"""
    
    def __init__(self):
        self.upstox_client = UpstoxClient()
        self.is_connected = False
        
        # Store live data
        self.live_bars = deque(maxlen=200)  # Store last 200 3-min bars
        self.current_price = 0.0
        self.last_update = None
        
        # Polling thread
        self.poll_thread = None
        self.running = False
        self.instrument_key = None
        
    def start(self, instrument_key: str = "NSE_INDEX|Nifty 50"):
        """Start live data feed using Upstox REST API"""
        
        self.instrument_key = instrument_key
        log.info(f"Starting live data feed for {instrument_key}")
        log.info("Using Upstox REST API (polling every 3 minutes)")
        
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_live_data, daemon=True)
        self.poll_thread.start()
        self.is_connected = True
    
    def _poll_live_data(self):
        """Poll Upstox API for live data every 3 minutes"""
        
        while self.running:
            try:
                # Get current time
                now = datetime.now()
                
                # Fetch last 3 days of 1-minute data (to cover weekends)
                from_date = now - timedelta(days=3)
                to_date = now
                
                log.info(f"Fetching live data from Upstox...")
                
                # Get 1-minute bars
                df = self.upstox_client.get_historical_data(
                    instrument_key=self.instrument_key,
                    interval='1minute',
                    from_date=from_date,
                    to_date=to_date
                )
                
                if not df.empty:
                    # Resample to 3-minute bars
                    df_3min = self._resample_to_3min(df)
                    
                    # Update live bars
                    for _, row in df_3min.iterrows():
                        bar = {
                            'timestamp': row['timestamp'],
                            'open': row['open'],
                            'high': row['high'],
                            'low': row['low'],
                            'close': row['close'],
                            'volume': row['volume']
                        }
                        
                        # Only add if not already present
                        if not self._bar_exists(bar['timestamp']):
                            self.live_bars.append(bar)
                            log.info(f"New live bar: {bar['timestamp'].strftime('%H:%M:%S')} - Close: {bar['close']:.2f}")
                    
                    # Update current price
                    self.current_price = df_3min['close'].iloc[-1]
                    self.last_update = now
                    
                    log.info(f"Live data updated: {len(self.live_bars)} bars, Current price: {self.current_price:.2f}")
                else:
                    log.warning("No data received from Upstox")
                
                # Wait 3 minutes before next poll
                time.sleep(180)
                
            except Exception as e:
                log.error(f"Error polling live data: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _resample_to_3min(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resample 1-minute bars to 3-minute bars"""
        
        df = df.copy()
        df.set_index('timestamp', inplace=True)
        
        # Resample to 3-minute bars
        df_3min = df.resample('3T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        df_3min.reset_index(inplace=True)
        
        return df_3min
    
    def _bar_exists(self, timestamp: datetime) -> bool:
        """Check if bar with given timestamp already exists"""
        
        for bar in self.live_bars:
            if bar['timestamp'] == timestamp:
                return True
        return False
    
    def get_live_bars(self, n: int = 100) -> pd.DataFrame:
        """Get latest live 3-minute bars"""
        
        if len(self.live_bars) == 0:
            log.warning("No live bars available yet")
            return pd.DataFrame()
        
        # Convert to DataFrame
        bars = list(self.live_bars)[-n:]
        df = pd.DataFrame(bars)
        
        # Ensure proper data types
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)
        df['volume'] = df['volume'].astype(int)
        
        return df
    
    def get_current_price(self) -> float:
        """Get current market price"""
        return self.current_price
    
    def is_ready(self) -> bool:
        """Check if enough data is available"""
        return len(self.live_bars) >= 50
    
    def stop(self):
        """Stop live data feed"""
        self.running = False
        self.is_connected = False
        log.info("Live data feed stopped")
