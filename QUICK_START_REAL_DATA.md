# Quick Start Guide - Real Data Trading

## ✅ System Status

The trading system is now configured to use **real Upstox market data**!

## Prerequisites

### 1. Upstox Access Token
Get your access token from: https://api.upstox.com/

Add to `config/secrets.env`:
```bash
UPSTOX_ACCESS_TOKEN=your_token_here
```

### 2. Trained Model
Make sure you have a trained model in the `models/` directory.

Check available models:
```bash
# Windows
dir models\*.pkl

# Linux/Mac
ls models/*.pkl
```

## Running the System

### Option 1: Use start_live_trading.py (Recommended)

```bash
python start_live_trading.py
```

This will:
- Run pre-flight checks
- Verify model exists
- Check access token
- Start trading bot automatically

### Option 2: Use main.py directly

```bash
# Use the latest model
python main.py --model models/model_xgboost_20251129_174005.pkl --mode paper
```

**Note**: Replace the model filename with your actual model file.

## Expected Behavior

### During Market Hours (9:15 AM - 3:30 PM IST, Mon-Fri)

```
Starting live data feed...
Loading historical data to bootstrap...
Loaded 600 historical bars for bootstrap
Starting WebSocket for live data...
Fetching live data from Upstox...
New live bar: 14:23:00 - Close: 26215.34
Live data updated: 600 bars, Current price: 26215.34
Live data feed started successfully
✅ System ready for trading!
```

### Outside Market Hours

```
Starting live data feed...
Loading historical data to bootstrap...
No historical data loaded
Starting WebSocket for live data...
Fetching live data from Upstox...
⚠️  WARNING: No data received from Upstox
Waiting for live data to be ready...
```

**This is normal!** The system will:
1. Keep polling every 3 minutes
2. Wait for market to open
3. Start trading when data is available

## Market Hours

| Day | Trading Hours (IST) |
|-----|---------------------|
| Monday - Friday | 9:15 AM - 3:30 PM |
| Saturday - Sunday | Closed |
| Holidays | Closed |

## Troubleshooting

### Issue: "No data received from Upstox"

**Possible Causes:**
1. ✅ **Market is closed** (most common)
2. ❌ Invalid access token
3. ❌ Network connectivity issues
4. ❌ Upstox API is down

**Solutions:**

**1. Check Market Hours**
```bash
# Current time in IST
python -c "from datetime import datetime; import pytz; print(datetime.now(pytz.timezone('Asia/Kolkata')))"
```

**2. Verify Access Token**
```bash
# Check if token is set
cat config/secrets.env | grep UPSTOX_ACCESS_TOKEN

# Or on Windows
type config\secrets.env | findstr UPSTOX_ACCESS_TOKEN
```

**3. Test Upstox Connection**
```bash
python test_upstox_connection.py
```

**4. Check Logs**
```bash
# View latest logs
tail -f logs/trading_*.log

# Or on Windows
Get-Content logs\trading_*.log -Tail 50 -Wait
```

### Issue: "Model file not found"

**Solution:**
```bash
# List available models
dir models\*.pkl

# Use the exact filename
python main.py --model models/model_xgboost_20251129_174005.pkl --mode paper
```

### Issue: "Access token missing"

**Solution:**
1. Get token from https://api.upstox.com/
2. Create/edit `config/secrets.env`:
   ```bash
   UPSTOX_ACCESS_TOKEN=your_token_here
   ```
3. Restart the system

## Testing During Market Hours

### 1. Start the System
```bash
python start_live_trading.py
```

### 2. Monitor Dashboard
Open browser: http://localhost:8000

### 3. Watch Logs
```bash
# Real-time log monitoring
tail -f logs/trading_*.log

# Or on Windows
Get-Content logs\trading_*.log -Tail 50 -Wait
```

### 4. Expected Output
```
[14:23:00] Fetching live data from Upstox...
[14:23:01] New live bar: 14:23:00 - Close: 26215.34
[14:23:01] Live data updated: 150 bars, Current price: 26215.34
[14:26:00] Fetching live data from Upstox...
[14:26:01] New live bar: 14:26:00 - Close: 26218.50
[14:26:01] Signal: BUY, Confidence: 0.75
[14:26:01] [PAPER] Opening BUY position: 1 @ 26218.50
```

## What Happens When Market Opens

When market opens (9:15 AM IST):
1. System fetches historical data (last 2 days)
2. Bootstraps with ~600 bars
3. Starts polling every 3 minutes
4. Generates trading signals
5. Executes paper trades

## Stopping the System

Press `Ctrl+C` to stop gracefully:
```
^C
Keyboard interrupt received
Stopping live data feed...
Live data feed stopped
System stopped.
```

## Performance Monitoring

### Dashboard
- URL: http://localhost:8000
- Shows: Current position, PnL, signals, trades

### Logs
- Location: `logs/trading_*.log`
- Level: INFO (configurable)
- Rotation: Daily

### Metrics
- Data updates: Every 3 minutes
- Signal generation: Every 3 minutes
- API calls: ~160 per day (market hours)

## Next Steps

### 1. Paper Trading (Current)
- ✅ Test with real data
- ✅ No real money at risk
- ✅ Validate strategy
- ⏳ Run for 1+ week

### 2. Performance Analysis
- Monitor win rate
- Check Sharpe ratio
- Analyze drawdowns
- Review trade logs

### 3. Optimization
- Tune model parameters
- Adjust risk limits
- Optimize position sizing
- Refine entry/exit rules

### 4. Live Trading (Future)
- ⚠️ Only after successful paper trading
- ⚠️ Start with small positions
- ⚠️ Monitor closely
- ⚠️ Have stop-loss in place

## Support

### Documentation
- Quick Start: This file
- Setup Guide: `WEBSOCKET_SETUP.md`
- Detailed Guide: `docs/WEBSOCKET_INTEGRATION.md`
- Migration Guide: `LIVE_DATA_MIGRATION.md`

### Testing
- Live Feed Test: `python test_live_upstox_feed.py`
- Connection Test: `python test_upstox_connection.py`
- Full System: `python start_live_trading.py`

### Logs
- Trading logs: `logs/trading_*.log`
- Error logs: `logs/errors_*.log`

---

## 🎉 You're Ready!

The system is configured and ready to trade with real Upstox data. Just wait for market hours to see it in action!

**Current Status**: ✅ Configured  
**Data Source**: Real Upstox API  
**Mode**: Paper Trading  
**Next**: Wait for market hours or test during trading session  

**Happy Trading! 📈**
