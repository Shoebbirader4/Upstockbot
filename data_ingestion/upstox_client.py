"""Upstox API client for data fetching and order execution"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from utils.logger import log
from utils.config_loader import config

class UpstoxClient:
    """Upstox API client"""
    
    BASE_URL = "https://api.upstox.com/v2"
    
    def __init__(self):
        self.api_key = config.get_secret('UPSTOX_API_KEY')
        self.api_secret = config.get_secret('UPSTOX_API_SECRET')
        self.access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')
        
        if not all([self.api_key, self.access_token]):
            log.warning("Upstox credentials not fully configured")
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
    
    def get_historical_data(self, instrument_key: str, interval: str, 
                           from_date: datetime, to_date: datetime) -> pd.DataFrame:
        """
        Fetch historical candle data
        
        Args:
            instrument_key: e.g., 'NSE_INDEX|Nifty 50' or 'NSE_FO|43650'
            interval: '1minute', '30minute', 'day', 'week', 'month' (Upstox supported intervals)
            from_date: Start date
            to_date: End date
        """
        try:
            # Upstox has limits on date range - fetch in chunks if needed
            days_diff = (to_date - from_date).days
            
            if days_diff > 30:
                # Fetch in 30-day chunks
                log.info(f"Fetching {days_diff} days in chunks (Upstox limit: 30 days per request)")
                all_dfs = []
                current_start = from_date
                
                while current_start < to_date:
                    current_end = min(current_start + timedelta(days=30), to_date)
                    
                    log.info(f"  Fetching chunk: {current_start.date()} to {current_end.date()}")
                    chunk_df = self._fetch_single_chunk(instrument_key, interval, current_start, current_end)
                    
                    if not chunk_df.empty:
                        all_dfs.append(chunk_df)
                    
                    current_start = current_end + timedelta(days=1)
                
                if not all_dfs:
                    log.error("No data fetched from any chunk")
                    return pd.DataFrame()
                
                # Combine all chunks
                df = pd.concat(all_dfs, ignore_index=True)
                df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp']).reset_index(drop=True)
                
                log.info(f"Combined {len(all_dfs)} chunks into {len(df)} total candles")
                return df
            else:
                # Single request for <= 30 days
                return self._fetch_single_chunk(instrument_key, interval, from_date, to_date)
                
        except Exception as e:
            log.error(f"Error fetching Upstox data: {e}")
            return pd.DataFrame()
    
    def _fetch_single_chunk(self, instrument_key: str, interval: str,
                           from_date: datetime, to_date: datetime) -> pd.DataFrame:
        """Fetch a single chunk of historical data"""
        try:
            # Map interval to Upstox format
            # Upstox only supports: 1minute, 30minute, day, week, month
            interval_map = {
                '3minute': '1minute',  # We'll fetch 1min and resample to 3min
                '5minute': '1minute',
                '10minute': '1minute',
                '15minute': '1minute',
                '1minute': '1minute',
                '30minute': '30minute',
                'day': 'day',
                'week': 'week',
                'month': 'month'
            }
            
            upstox_interval = interval_map.get(interval, '1minute')
            
            # Check if requesting today's data - use intraday endpoint
            today = datetime.now().date()
            if to_date.date() == today:
                log.info("Fetching intraday data for today...")
                return self._fetch_intraday(instrument_key, upstox_interval, interval)
            
            # Upstox API endpoint for historical data
            url = f"{self.BASE_URL}/historical-candle/{instrument_key}/{upstox_interval}/{to_date.strftime('%Y-%m-%d')}/{from_date.strftime('%Y-%m-%d')}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success' and 'data' in data:
                candles = data['data']['candles']
                
                # Convert to DataFrame
                df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)  # Remove timezone
                df = df.drop('oi', axis=1)  # Drop open interest
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                # Filter market hours (9:15 - 15:30 IST)
                df = df[
                    (df['timestamp'].dt.time >= pd.Timestamp("09:15").time()) &
                    (df['timestamp'].dt.time <= pd.Timestamp("15:30").time()) &
                    (df['timestamp'].dt.dayofweek < 5)  # Monday-Friday
                ]
                
                # Resample if needed (e.g., 1min to 3min)
                if interval == '3minute' and upstox_interval == '1minute':
                    df = self._resample_to_3min(df)
                
                return df
            else:
                log.error(f"Upstox API error: {data}")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            log.error(f"Upstox API request failed: {e}")
            return pd.DataFrame()
        except Exception as e:
            log.error(f"Error in chunk fetch: {e}")
            return pd.DataFrame()
    
    def _fetch_intraday(self, instrument_key: str, upstox_interval: str, original_interval: str) -> pd.DataFrame:
        """Fetch intraday data for current day"""
        try:
            # Intraday endpoint
            url = f"{self.BASE_URL}/historical-candle/intraday/{instrument_key}/{upstox_interval}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success' and 'data' in data:
                candles = data['data']['candles']
                
                if not candles:
                    log.warning("No intraday candles available")
                    return pd.DataFrame()
                
                # Convert to DataFrame
                df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)  # Remove timezone
                df = df.drop('oi', axis=1)  # Drop open interest
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                # Filter market hours (9:15 - 15:30 IST)
                df = df[
                    (df['timestamp'].dt.time >= pd.Timestamp("09:15").time()) &
                    (df['timestamp'].dt.time <= pd.Timestamp("15:30").time())
                ]
                
                # Resample if needed (e.g., 1min to 3min)
                if original_interval == '3minute' and upstox_interval == '1minute':
                    df = self._resample_to_3min(df)
                
                log.info(f"Fetched {len(df)} intraday bars for today")
                return df
            else:
                log.error(f"Upstox intraday API error: {data}")
                return pd.DataFrame()
                
        except Exception as e:
            log.error(f"Error fetching intraday data: {e}")
            return pd.DataFrame()
    
    def get_instrument_key(self, symbol: str = "NIFTY") -> str:
        """
        Get instrument key for a symbol
        
        Returns instrument_key like 'NSE_INDEX|Nifty 50' or 'NSE_FO|43650'
        """
        try:
            # Using Nifty 50 Index (works with Upstox API)
            # For Nifty Futures, you need to find the current month contract from Upstox platform
            
            if symbol in ["NIFTY", "NIFTY_FUT", "NIFTY50"]:
                # Use Nifty Index - this works!
                return "NSE_INDEX|Nifty 50"
            
            # For other symbols, implement lookup
            log.warning(f"Unknown symbol: {symbol}, using Nifty Index")
            return "NSE_INDEX|Nifty 50"
            
        except Exception as e:
            log.error(f"Error getting instrument key: {e}")
            return "NSE_INDEX|Nifty 50"
    
    def place_order(self, instrument_key: str, quantity: int, 
                   transaction_type: str, order_type: str = "MARKET",
                   product: str = "I", price: float = 0) -> Dict:
        """
        Place an order
        
        Args:
            instrument_key: Instrument key
            quantity: Order quantity
            transaction_type: 'BUY' or 'SELL'
            order_type: 'MARKET' or 'LIMIT'
            product: 'I' for Intraday, 'D' for Delivery
            price: Limit price (for LIMIT orders)
        """
        try:
            url = f"{self.BASE_URL}/order/place"
            
            payload = {
                'instrument_token': instrument_key,
                'quantity': quantity,
                'transaction_type': transaction_type,
                'order_type': order_type,
                'product': product,
                'validity': 'DAY',
                'price': price if order_type == 'LIMIT' else 0,
                'trigger_price': 0,
                'disclosed_quantity': 0
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success':
                log.info(f"Order placed successfully: {data['data']['order_id']}")
                return {
                    'success': True,
                    'order_id': data['data']['order_id'],
                    'message': 'Order placed'
                }
            else:
                log.error(f"Order placement failed: {data}")
                return {
                    'success': False,
                    'error': data.get('message', 'Unknown error')
                }
                
        except requests.exceptions.RequestException as e:
            log.error(f"Order placement request failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            log.error(f"Error placing order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        try:
            url = f"{self.BASE_URL}/order/history"
            params = {'order_id': order_id}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success':
                return data['data']
            else:
                log.error(f"Failed to get order status: {data}")
                return {}
                
        except Exception as e:
            log.error(f"Error getting order status: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            url = f"{self.BASE_URL}/portfolio/short-term-positions"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success':
                return data['data']
            else:
                log.error(f"Failed to get positions: {data}")
                return []
                
        except Exception as e:
            log.error(f"Error getting positions: {e}")
            return []
    
    def _resample_to_3min(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resample 1-minute data to 3-minute bars"""
        df = df.set_index('timestamp')
        
        resampled = df.resample('3min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        resampled = resampled.reset_index()
        return resampled
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        try:
            url = f"{self.BASE_URL}/user/profile"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success':
                log.info(f"Connected to Upstox as: {data['data']['user_name']}")
                return data['data']
            else:
                log.error(f"Failed to get profile: {data}")
                return {}
                
        except Exception as e:
            log.error(f"Error getting profile: {e}")
            return {}
