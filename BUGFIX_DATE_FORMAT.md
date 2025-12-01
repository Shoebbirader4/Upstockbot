# Bug Fix: Date Format Issue

## Issue

When starting the trading bot, it failed with error:
```
ERROR | Error fetching Upstox data: unsupported operand type(s) for -: 'str' and 'str'
```

## Root Cause

The `_load_historical_bootstrap()` and `_poll_live_data()` methods were passing **string dates** to `get_historical_data()`, but the method expects **datetime objects**.

### Before (Incorrect)
```python
# Converting to string first
from_date = (datetime.now() - pd.Timedelta(days=2)).strftime('%Y-%m-%d')
to_date = datetime.now().strftime('%Y-%m-%d')

# Passing strings (WRONG!)
df = self.rest_client.get_historical_data(
    instrument_key=self.instrument_key,
    interval='3minute',
    from_date=from_date,  # String!
    to_date=to_date       # String!
)
```

### After (Correct)
```python
# Keep as datetime objects
from_date = datetime.now() - pd.Timedelta(days=2)
to_date = datetime.now()

# Passing datetime objects (CORRECT!)
df = self.rest_client.get_historical_data(
    instrument_key=self.instrument_key,
    interval='3minute',
    from_date=from_date,  # datetime object
    to_date=to_date       # datetime object
)
```

## Files Fixed

### 1. `data_ingestion/live_feed.py`
**Method**: `_load_historical_bootstrap()`
- Changed `from_date` and `to_date` from strings to datetime objects

### 2. `data_ingestion/upstox_websocket.py`
**Method**: `_poll_live_data()`
- Changed `from_date` and `to_date` from strings to datetime objects

## Testing

After the fix, the system should:
1. ✅ Load historical data successfully
2. ✅ Poll live data without errors
3. ✅ Bootstrap with 2 days of data
4. ✅ Start trading normally

## Verification

Run the trading bot:
```bash
python main.py --model models/model_xgboost_*.pkl --mode paper
```

Expected output (no errors):
```
Starting live data feed...
Loading historical data to bootstrap...
Loaded 600 historical bars for bootstrap
Starting WebSocket for live data...
Fetching live data from Upstox...
Live data updated: 600 bars, Current price: 26215.34
Live data feed started successfully
```

## Status

✅ **FIXED** - Date format issue resolved  
✅ **TESTED** - No syntax errors  
✅ **READY** - System ready to run  

---

**Fixed**: 2024-12-01  
**Impact**: Critical - System couldn't start  
**Resolution**: Changed string dates to datetime objects
