"""Real-time live data feed using Upstox WebSocket"""

from datetime import datetime
import pandas as pd
from data_ingestion.upstox_websocket import UpstoxWebSocket
from data_ingestion.upstox_client import UpstoxClient
from utils.logger import log

class LiveDataFeed:
    """Real-time market data feed combining WebSocket and REST API"""
    
    def __init__(self, instrument_key: str = "NSE_INDEX|Nifty 50"):
        self.instrument_key = instrument_key
        
        # WebSocket for live data
        self.ws_client = UpstoxWebSocket()
        
        # REST API for historical data (to fill gaps)
        self.rest_client = UpstoxClient()
        
        # Combined data
        self.historical_loaded = False
        
        log.info(f"LiveDataFeed initialized for {instrument_key}")
    
    def start(self):
        """Start live data feed"""
        
        log.info("Starting live data feed...")
        
        # Step 1: Load recent historical data (last 2 days)
        log.info("Loading historical data to bootstrap...")
        self._load_historical_bootstrap()
        
        # Step 2: Start WebSocket for live updates
        log.info("Starting WebSocket for live data...")
        self.ws_client.start(self.instrument_key)
        
        log.info("Live data feed started successfully")
    
    def stop(self):
        """Stop live data feed"""
        self.ws_client.stop()
        log.info("Live data feed stopped")
    
    def _load_historical_bootstrap(self):
        """Load recent historical data to bootstrap the system"""
        try:
            # Get last 7 days of 3-minute data (to cover weekends) - EXCLUDING today
            from_date = datetime.now() - pd.Timedelta(days=7)
            to_date = datetime.now() - pd.Timedelta(days=1)  # Yesterday
            
            df = self.rest_client.get_historical_data(
                instrument_key=self.instrument_key,
                interval='3minute',
                from_date=from_date,
                to_date=to_date
            )
            
            if not df.empty:
                # Add historical bars to WebSocket client
                for _, row in df.iterrows():
                    bar = {
                        'timestamp': row['timestamp'],
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'volume': row['volume']
                    }
                    self.ws_client.live_bars.append(bar)
                
                self.historical_loaded = True
                log.info(f"Loaded {len(df)} historical bars for bootstrap")
            else:
                log.warning("No historical data loaded")
                
        except Exception as e:
            log.error(f"Error loading historical bootstrap: {e}")
    

    
    def get_latest_bars(self, n: int = 100) -> pd.DataFrame:
        """Get latest 3-minute bars (historical + live)"""
        return self.ws_client.get_live_bars(n)
    
    def get_current_price(self) -> float:
        """Get current market price"""
        return self.ws_client.get_current_price()
    
    def is_ready(self) -> bool:
        """Check if feed has enough data for trading"""
        return self.ws_client.is_ready()
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.ws_client.is_connected
