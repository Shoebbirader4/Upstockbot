# Broker API Integration Guide

## Overview

This guide explains how to integrate real broker APIs (Zerodha Kite and Upstox) to replace the mock data implementations.

## Zerodha Kite API Integration

### 1. Get API Credentials

1. Visit https://kite.trade
2. Sign up for Kite Connect
3. Create a new app
4. Note down:
   - API Key
   - API Secret
5. Generate access token (valid for 1 day)

### 2. Install Kite Connect SDK

```bash
pip install kiteconnect
```

### 3. Update `data_ingestion/data_fetcher.py`

Replace the `_fetch_zerodha_historical` method:

```python
from kiteconnect import KiteConnect
from utils.config_loader import config

def _fetch_zerodha_historical(self, symbol: str, start_date: datetime,
                              end_date: datetime, interval: str) -> pd.DataFrame:
    """Fetch from Zerodha Kite API"""
    
    # Initialize Kite Connect
    api_key = config.get_secret('ZERODHA_API_KEY')
    access_token = config.get_secret('ZERODHA_ACCESS_TOKEN')
    
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    
    # Map symbol to instrument token
    # For Nifty Futures, you need to get the correct instrument token
    # Example: NIFTY24JANFUT
    instrument_token = self._get_instrument_token(kite, symbol)
    
    # Fetch historical data
    # Kite interval format: "3minute"
    data = kite.historical_data(
        instrument_token=instrument_token,
        from_date=start_date,
        to_date=end_date,
        interval=interval,
        continuous=False
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df = df.rename(columns={
        'date': 'timestamp',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    })
    
    return df

def _get_instrument_token(self, kite, symbol: str) -> int:
    """Get instrument token for symbol"""
    
    # Download instruments list
    instruments = kite.instruments("NFO")  # NFO for Nifty Futures
    
    # Find current month Nifty Futures
    # This is simplified - you need to handle expiry logic
    for instrument in instruments:
        if instrument['tradingsymbol'].startswith('NIFTY') and \
           instrument['instrument_type'] == 'FUT':
            return instrument['instrument_token']
    
    raise ValueError(f"Instrument not found: {symbol}")
```

### 4. Update `execution_engine/order_manager.py`

Replace the `_execute_zerodha_order` method:

```python
def _execute_zerodha_order(self, order: Dict) -> Dict:
    """Execute order via Zerodha Kite API"""
    
    from kiteconnect import KiteConnect
    
    api_key = config.get_secret('ZERODHA_API_KEY')
    access_token = config.get_secret('ZERODHA_ACCESS_TOKEN')
    
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    
    try:
        # Get instrument token
        instrument_token = self._get_instrument_token(kite, order['symbol'])
        
        # Place order
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NFO,
            tradingsymbol=order['symbol'],
            transaction_type=order['direction'],  # BUY or SELL
            quantity=order['quantity'],
            product=order['product_type'],  # MIS for intraday
            order_type=order['order_type'],  # MARKET or LIMIT
            price=order.get('price'),
            validity=kite.VALIDITY_DAY
        )
        
        # Get order details
        order_info = kite.order_history(order_id)[-1]
        
        return {
            'success': True,
            'execution_price': order_info['average_price'],
            'order_id': order_id,
            'status': order_info['status']
        }
        
    except Exception as e:
        log.error(f"Zerodha order execution failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

### 5. Handle Access Token Generation

Zerodha access tokens expire daily. You need to regenerate them:

```python
# Add to utils/zerodha_auth.py

from kiteconnect import KiteConnect
import webbrowser

def generate_access_token():
    """Generate Zerodha access token (run manually daily)"""
    
    api_key = input("Enter API Key: ")
    api_secret = input("Enter API Secret: ")
    
    kite = KiteConnect(api_key=api_key)
    
    # Get login URL
    login_url = kite.login_url()
    print(f"Open this URL in browser:\n{login_url}")
    webbrowser.open(login_url)
    
    # After login, you'll be redirected to a URL with request_token
    request_token = input("Enter request_token from redirect URL: ")
    
    # Generate session
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    
    print(f"\nAccess Token: {access_token}")
    print("\nAdd this to config/secrets.env:")
    print(f"ZERODHA_ACCESS_TOKEN={access_token}")
    
    return access_token

if __name__ == "__main__":
    generate_access_token()
```

Run daily before market open:
```bash
python utils/zerodha_auth.py
```

## Upstox API Integration

### 1. Get API Credentials

1. Visit https://upstox.com/developer/
2. Create an app
3. Note down:
   - API Key
   - API Secret
4. Generate access token

### 2. Install Upstox SDK

```bash
pip install upstox-python
```

### 3. Update `data_ingestion/data_fetcher.py`

```python
from upstox_api.api import Upstox

def _fetch_upstox_historical(self, symbol: str, start_date: datetime,
                            end_date: datetime, interval: str) -> pd.DataFrame:
    """Fetch from Upstox API"""
    
    api_key = config.get_secret('UPSTOX_API_KEY')
    access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')
    
    upstox = Upstox(api_key, access_token)
    
    # Get instrument key
    instrument_key = self._get_upstox_instrument_key(symbol)
    
    # Fetch historical data
    data = upstox.get_ohlc(
        instrument=instrument_key,
        interval=interval,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(data['data']['candles'])
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi']
    df = df.drop('oi', axis=1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df
```

### 4. Update `execution_engine/order_manager.py`

```python
def _execute_upstox_order(self, order: Dict) -> Dict:
    """Execute order via Upstox API"""
    
    from upstox_api.api import Upstox
    
    api_key = config.get_secret('UPSTOX_API_KEY')
    access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')
    
    upstox = Upstox(api_key, access_token)
    
    try:
        # Place order
        response = upstox.place_order(
            transaction_type=order['direction'],
            instrument=self._get_upstox_instrument_key(order['symbol']),
            quantity=order['quantity'],
            order_type=order['order_type'],
            product_type=order['product_type'],
            price=order.get('price', 0),
            trigger_price=None,
            disclosed_quantity=0,
            duration='DAY',
            stop_loss=None,
            square_off=None,
            trailing_ticks=None
        )
        
        return {
            'success': True,
            'execution_price': response['data']['average_price'],
            'order_id': response['data']['order_id']
        }
        
    except Exception as e:
        log.error(f"Upstox order execution failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

## WebSocket for Live Data

For real-time data streaming, use WebSocket connections:

### Zerodha WebSocket

```python
# Add to data_ingestion/live_feed.py

from kiteconnect import KiteTicker

class LiveDataFeed:
    def __init__(self):
        self.api_key = config.get_secret('ZERODHA_API_KEY')
        self.access_token = config.get_secret('ZERODHA_ACCESS_TOKEN')
        self.kws = KiteTicker(self.api_key, self.access_token)
        
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        
        self.latest_tick = None
    
    def on_ticks(self, ws, ticks):
        """Callback for tick data"""
        self.latest_tick = ticks[0]
        log.debug(f"Tick: {self.latest_tick}")
    
    def on_connect(self, ws, response):
        """Callback on connection"""
        # Subscribe to instruments
        instrument_tokens = [256265]  # Nifty Futures token
        ws.subscribe(instrument_tokens)
        ws.set_mode(ws.MODE_FULL, instrument_tokens)
        log.info("WebSocket connected")
    
    def on_close(self, ws, code, reason):
        """Callback on close"""
        log.warning(f"WebSocket closed: {code} - {reason}")
    
    def start(self):
        """Start WebSocket connection"""
        self.kws.connect(threaded=True)
    
    def stop(self):
        """Stop WebSocket connection"""
        self.kws.close()
    
    def get_latest_price(self):
        """Get latest price"""
        if self.latest_tick:
            return self.latest_tick['last_price']
        return None
```

## Testing Broker Integration

### 1. Test Data Fetching

```python
# test_broker_integration.py

from data_ingestion.data_fetcher import DataFetcher
from datetime import datetime, timedelta

def test_zerodha_data():
    fetcher = DataFetcher(source='zerodha')
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    df = fetcher.fetch_historical('NIFTY_FUT', start_date, end_date)
    
    print(f"Fetched {len(df)} bars")
    print(df.head())
    print(df.tail())
    
    assert not df.empty
    assert 'close' in df.columns
    print("✓ Data fetching works!")

if __name__ == "__main__":
    test_zerodha_data()
```

### 2. Test Order Placement (Paper)

```python
def test_order_placement():
    from execution_engine.order_manager import OrderManager
    
    manager = OrderManager(broker='zerodha')
    
    # Place a test order (will fail if not in trading hours)
    order = manager.place_order(
        symbol='NIFTY_FUT',
        direction='BUY',
        quantity=1,
        price=19500
    )
    
    print(f"Order status: {order['status']}")
    print(f"Order ID: {order.get('order_id')}")
    
    if order['status'] == 'EXECUTED':
        print("✓ Order placement works!")
    else:
        print("✗ Order placement failed")

if __name__ == "__main__":
    test_order_placement()
```

## Important Considerations

### 1. Instrument Tokens
- Nifty Futures have different tokens each month
- Need to handle expiry and rollover
- Download instruments list daily

### 2. Rate Limits
- Zerodha: 3 requests/second
- Upstox: 10 requests/second
- Implement rate limiting

### 3. Error Handling
- Network errors
- API errors
- Order rejection
- Insufficient funds
- Market closed

### 4. Order Types
- **MARKET**: Immediate execution at best price
- **LIMIT**: Execute at specified price or better
- **SL**: Stop loss order
- **SL-M**: Stop loss market order

### 5. Product Types
- **MIS**: Margin Intraday Square-off (auto square-off)
- **NRML**: Normal (carry forward)
- **CNC**: Cash and Carry (equity delivery)

### 6. Position Management
- Track open positions
- Handle partial fills
- Monitor margin requirements
- Auto square-off before 3:20 PM

## Security Best Practices

1. **Never hardcode credentials**
2. **Use environment variables**
3. **Rotate access tokens daily**
4. **Limit API permissions** to trading only
5. **Monitor API usage**
6. **Log all API calls**
7. **Implement rate limiting**
8. **Handle errors gracefully**
9. **Test in paper trading first**
10. **Keep SDK updated**

## Troubleshooting

### Issue: "Invalid access token"
**Solution**: Regenerate access token (expires daily)

### Issue: "Instrument not found"
**Solution**: Update instrument tokens, handle expiry

### Issue: "Order rejected"
**Solution**: Check margin, market hours, order parameters

### Issue: "Rate limit exceeded"
**Solution**: Implement rate limiting, reduce API calls

### Issue: "Connection timeout"
**Solution**: Implement retry logic, check network

## Additional Resources

### Zerodha Kite
- Documentation: https://kite.trade/docs/connect/v3/
- Python SDK: https://github.com/zerodhatech/pykiteconnect
- Forum: https://kite.trade/forum/

### Upstox
- Documentation: https://upstox.com/developer/api-documentation/
- Python SDK: https://github.com/upstox/upstox-python
- Support: https://upstox.com/support/

## Next Steps

1. Get API credentials from broker
2. Install broker SDK
3. Update data fetcher
4. Update order manager
5. Test data fetching
6. Test order placement (paper)
7. Run full backtest with real data
8. Paper trade for 1 week
9. Go live with small capital

---

**Remember**: Test thoroughly with paper trading before using real money!
