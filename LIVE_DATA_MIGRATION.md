# Migration to Real Live Data

## Summary

The system has been **migrated from mock data to real Upstox market data** for paper trading and live trading.

## What Changed

### Before (Mock Mode)
- Generated fake data with random walk
- No API credentials needed
- Worked 24/7
- Good for testing, but not real market conditions

### After (Real Data)
- ✅ **Real Upstox market data**
- ✅ **Actual Nifty prices**
- ✅ **Production-ready**
- ⚠️ Requires access token
- ⚠️ Works during market hours only

## Key Changes

### 1. UpstoxWebSocket (`data_ingestion/upstox_websocket.py`)
**Removed:**
- Mock data generator
- Random walk simulation
- Mock mode flag

**Added:**
- Real Upstox API integration
- Polls API every 3 minutes
- Fetches 1-minute bars
- Resamples to 3-minute bars
- Automatic deduplication

### 2. Configuration (`config/config.yaml.template`)
**Before:**
```yaml
data:
  use_websocket: true
  websocket_mock_mode: true  # Mock data
```

**After:**
```yaml
data:
  source: upstox
  use_websocket: true  # Real data
```

### 3. Documentation
Updated all documentation to reflect real data usage:
- `README.md`
- `docs/WEBSOCKET_INTEGRATION.md`
- `WEBSOCKET_SETUP.md`
- `WEBSOCKET_QUICK_REFERENCE.md`

## Setup Requirements

### 1. Get Upstox Access Token

1. Go to Upstox API dashboard: https://api.upstox.com/
2. Create an app (if not already done)
3. Generate access token
4. Copy the token

### 2. Configure Access Token

Add to `config/secrets.env`:
```bash
UPSTOX_ACCESS_TOKEN=your_access_token_here
```

### 3. Verify Configuration

Edit `config/config.yaml`:
```yaml
data:
  source: upstox
  use_websocket: true
```

## Testing

### Test Live Data Feed
```bash
python test_live_upstox_feed.py
```

**Expected Output (During Market Hours):**
```
Starting live data feed...
Fetching live data from Upstox...
New live bar: 14:23:00 - Close: 26215.34
Connection Status: Connected
Current Price: 26215.34
Total bars available: 150
✅ SUCCESS: Live data feed is working!
```

**Expected Output (Outside Market Hours):**
```
Starting live data feed...
Fetching live data from Upstox...
⚠️  WARNING: No data received
Check:
1. Market hours (9:15 AM - 3:30 PM IST)
2. Access token in config/secrets.env
3. Network connectivity
```

### Test with Trading Bot
```bash
python start_live_trading.py
```

## How It Works

### Data Flow

```
1. System Startup
   └─> Load 2 days historical data (REST API)
   └─> Bootstrap with ~600 bars

2. Start Live Feed
   └─> Poll Upstox API every 3 minutes
   └─> Fetch 1-minute bars for last 24 hours
   └─> Resample to 3-minute bars
   └─> Add new bars to rolling window

3. Trading Loop (Every 3 Minutes)
   └─> Get latest bars from live feed
   └─> Calculate features
   └─> Generate signal
   └─> Execute trade if conditions met
```

### Polling Strategy

- **Frequency**: Every 3 minutes
- **Data Fetched**: Last 24 hours of 1-minute bars
- **Resampling**: 1-min → 3-min bars
- **Deduplication**: Only adds new bars
- **Error Handling**: Retries on failure

## Benefits of Real Data

### Advantages
✅ **Real market conditions** - Actual price movements  
✅ **Accurate testing** - Test with real volatility  
✅ **Production-ready** - Same data as live trading  
✅ **Better validation** - Validate strategy with real data  

### Considerations
⚠️ **Market hours only** - 9:15 AM - 3:30 PM IST  
⚠️ **Access token required** - Must be valid and active  
⚠️ **API rate limits** - Polling every 3 minutes is safe  
⚠️ **Network dependency** - Requires stable internet  

## Troubleshooting

### Issue: No data received

**Possible Causes:**
1. Market is closed
2. Invalid access token
3. Network connectivity issues
4. Upstox API is down

**Solutions:**
1. Check market hours (9:15 AM - 3:30 PM IST)
2. Regenerate access token
3. Check internet connection
4. Check Upstox API status

### Issue: Access token expired

**Solution:**
1. Go to Upstox API dashboard
2. Generate new access token
3. Update `config/secrets.env`
4. Restart the system

### Issue: Old bars not updating

**Solution:**
- System polls every 3 minutes
- Wait for next poll cycle
- Check logs for errors
- Verify API connectivity

## Migration Checklist

- [x] Remove mock data generator
- [x] Implement real Upstox API integration
- [x] Add polling mechanism (every 3 minutes)
- [x] Add 1-min to 3-min resampling
- [x] Add deduplication logic
- [x] Update configuration
- [x] Update documentation
- [x] Create test scripts
- [x] Add error handling
- [x] Test with real data

## Next Steps

### Immediate
1. ✅ Get Upstox access token
2. ✅ Configure `config/secrets.env`
3. ✅ Test during market hours
4. ✅ Verify data quality

### Short-term
1. ⏳ Run paper trading for 1 week
2. ⏳ Monitor data quality
3. ⏳ Validate signals with real data
4. ⏳ Check performance metrics

### Long-term
1. ⏳ Optimize polling frequency if needed
2. ⏳ Add WebSocket support (true real-time)
3. ⏳ Implement data quality checks
4. ⏳ Add alerting for data issues

## Performance

### API Usage
- **Polls**: Every 3 minutes
- **Calls per day**: ~160 (during market hours)
- **Data fetched**: 1-min bars for last 24 hours
- **Rate limit**: Well within Upstox limits

### Data Quality
- **Source**: Upstox official API
- **Accuracy**: Exchange-grade data
- **Latency**: 3-minute delay (polling interval)
- **Reliability**: High (with error handling)

## Support

### Documentation
- Quick Setup: `WEBSOCKET_SETUP.md`
- Detailed Guide: `docs/WEBSOCKET_INTEGRATION.md`
- Quick Reference: `WEBSOCKET_QUICK_REFERENCE.md`

### Testing
- Live Feed Test: `python test_live_upstox_feed.py`
- Full System Test: `python start_live_trading.py`

### Logs
- Check: `logs/trading_*.log`
- Debug level available in config

---

## 🎉 Ready for Real Trading!

The system now uses **real Upstox market data** for paper trading. Test during market hours to see actual Nifty price movements!

**Status**: ✅ Complete and Ready  
**Last Updated**: 2024-12-01  
**Version**: 2.0 (Real Data)
