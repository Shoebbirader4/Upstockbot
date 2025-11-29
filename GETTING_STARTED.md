# Getting Started with Your Upstox Trading Bot

## ✅ What's Already Done

You've successfully:
- ✓ Added Upstox API credentials to `config/secrets.env`
- ✓ Configuration files are in place
- ✓ System is configured to use Upstox

## 🚀 Next Steps

### Step 1: Install Python Packages (5 minutes)

```bash
# Install all required packages
pip install -r requirements.txt
```

This will install:
- pandas, numpy (data processing)
- xgboost, lightgbm (ML models)
- scikit-learn (preprocessing)
- fastapi (web dashboard)
- requests (API calls)
- And all other dependencies

### Step 2: Verify Upstox Connection (2 minutes)

```bash
# Test your Upstox API connection
python test_upstox_connection.py
```

This will:
- Connect to Upstox API
- Show your profile information
- Test data fetching
- Verify everything works

**Expected output:**
```
============================================================
TESTING UPSTOX API CONNECTION
============================================================

1. Initializing Upstox client...

2. Testing profile access...
✓ Connected successfully!
  User: Your Name
  Email: your@email.com
  User ID: ABC123

3. Testing positions access...
✓ Current positions: 0

4. Testing historical data fetch...
  Using instrument key: NSE_FO|43650
✓ Fetched 500 candles

============================================================
CONNECTION TEST COMPLETE
============================================================

✓ All tests passed! You're ready to use Upstox.
```

### Step 3: Update Instrument Key (Important!)

The system uses a placeholder instrument key. You need to update it with the actual Nifty Futures contract:

1. Open `data_ingestion/upstox_client.py`
2. Find the `get_instrument_key()` method
3. Replace the placeholder with the actual instrument key

**How to find the correct instrument key:**
- Go to Upstox API documentation
- Download the instrument list
- Find the current month Nifty Futures contract
- Use that instrument key

Or use this API call:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.upstox.com/v2/market-quote/instruments
```

### Step 4: Train Your First Model (10 minutes)

```bash
# Train model with 90 days of historical data
python -m model_training.train --days 90
```

This will:
- Fetch historical data from Upstox (or use mock data if instrument key not configured)
- Create technical indicators
- Train XGBoost model
- Save model to `models/` folder

### Step 5: Run Backtest (5 minutes)

```bash
# Backtest the trained model
python -m backtester.run_backtest \
    --model models/model_xgboost_*.pkl \
    --days 30
```

This will show you:
- Total trades
- Win rate
- PnL
- Max drawdown
- Performance metrics

### Step 6: Paper Trading (Recommended - 1 week)

```bash
# Start paper trading (no real money)
python main.py \
    --model models/model_xgboost_*.pkl \
    --mode paper
```

**What happens:**
- Bot runs during market hours (9:15-15:30 IST)
- Generates signals every 3 minutes
- Simulates order execution
- Tracks PnL
- Dashboard available at http://localhost:8000

**Let it run for at least 1 week** to verify everything works correctly.

### Step 7: Live Trading (When Ready)

⚠️ **WARNING: This trades with real money!**

Only proceed after:
- Paper trading successfully for 1+ week
- Understanding all risk parameters
- Having emergency stop procedures ready

```bash
# Start live trading (REAL MONEY!)
python main.py \
    --model models/model_xgboost_*.pkl \
    --mode live
```

## 📊 Monitoring

### Web Dashboard
Open browser: http://localhost:8000

Endpoints:
- `/status` - Current trading status
- `/metrics` - Performance metrics
- `/orders` - Order history
- `/equity` - Equity curve

### Logs
```bash
# View today's logs
tail -f logs/trading_$(date +%Y-%m-%d).log

# View errors
tail -f logs/errors_$(date +%Y-%m-%d).log
```

## ⚙️ Configuration

### Risk Limits (config/config.yaml)
```yaml
risk:
  max_daily_loss: 20000      # ₹20,000 max loss per day
  max_trades_per_day: 20     # Max 20 trades per day
  max_position_size: 2       # Max 2 lots
```

**Adjust these based on your risk tolerance!**

### Trading Hours
```yaml
trading:
  market_hours:
    start: "09:15"
    end: "15:30"
```

## 🛑 Emergency Stop

If something goes wrong:

```bash
# Method 1: API
curl -X POST http://localhost:8000/stop

# Method 2: Keyboard
Press Ctrl+C in terminal

# Method 3: Kill process
pkill -f "python main.py"
```

## 📞 Troubleshooting

### Issue: "Upstox connection failed"
**Solution:**
- Check your access token is valid (they expire)
- Verify credentials in `config/secrets.env`
- Check internet connection

### Issue: "No data fetched"
**Solution:**
- Update instrument key in `upstox_client.py`
- Check if market is open
- Verify date range is valid

### Issue: "Order placement failed"
**Solution:**
- Check account has sufficient balance
- Verify margin requirements
- Check if in trading hours
- Review risk limits

## 📚 Documentation

- **Quick Reference**: `QUICK_REFERENCE.md`
- **Complete Setup**: `SETUP_GUIDE.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Usage Guide**: `docs/USAGE.md`
- **Broker Integration**: `docs/BROKER_INTEGRATION.md`

## ✅ Checklist

Before going live:
- [ ] Packages installed (`pip install -r requirements.txt`)
- [ ] Upstox connection tested (`python test_upstox_connection.py`)
- [ ] Instrument key updated in `upstox_client.py`
- [ ] Model trained successfully
- [ ] Backtest shows positive results
- [ ] Paper traded for 1+ week
- [ ] Risk limits configured appropriately
- [ ] Emergency procedures understood
- [ ] Monitoring dashboard accessible
- [ ] Sufficient account balance

## 🎯 Quick Commands

```bash
# Verify setup
python verify_setup.py

# Test Upstox connection
python test_upstox_connection.py

# Train model
python -m model_training.train --days 90

# Backtest
python -m backtester.run_backtest --model models/model_*.pkl --days 30

# Paper trade
python main.py --model models/model_*.pkl --mode paper

# Live trade (careful!)
python main.py --model models/model_*.pkl --mode live
```

## 💡 Tips

1. **Start small** - Use minimal position sizes initially
2. **Monitor closely** - Especially the first week
3. **Keep logs** - Review daily for any issues
4. **Update model** - Retrain monthly with latest data
5. **Adjust risk** - Based on your comfort level
6. **Have backup** - Manual trading plan if bot fails
7. **Test changes** - Always in paper mode first
8. **Stay informed** - Monitor market news and events

## 🔐 Security

- Never share your `config/secrets.env` file
- Keep access tokens secure
- Rotate credentials regularly
- Monitor for unauthorized access
- Review logs for suspicious activity

---

**You're all set!** Start with Step 1 (install packages) and work your way through. Good luck! 🚀
