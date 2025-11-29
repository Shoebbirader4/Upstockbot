# Paper Trading Status

## 🎯 Current Status: ACTIVE

**Started:** November 29, 2025 at 5:41 PM IST
**Mode:** PAPER TRADING (No real money)
**Model:** Improved model with 32 features
**Training Data:** 90 days of real Upstox data (7,645 bars)

## ✅ Bot Configuration

### Model Details:
- **File:** `models/model_xgboost_20251129_174005.pkl`
- **Features:** 32 advanced features
  - MACD, Bollinger Bands, ADX
  - RSI, ATR, ROC, Momentum
  - Price action patterns
  - Multi-timeframe indicators
- **Training:** 90 days real Nifty data
- **Class Balance:** 35% Sell, 27% Hold, 38% Buy

### Risk Limits:
- **Max Daily Loss:** ₹20,000
- **Max Trades/Day:** 20
- **Max Position Size:** 2 lots
- **Volatility Filter:** 3x ATR
- **Cooldown:** 30 min after 3 losses

### Trading Schedule:
- **Market Hours:** 9:15 AM - 3:30 PM IST
- **Signal Frequency:** Every 3 minutes
- **Auto Square-off:** 3:20 PM

## 📊 Monitoring

### Web Dashboard:
```
http://localhost:8000
```

**Endpoints:**
- `/` - Home page
- `/status` - Current trading status
- `/metrics` - Performance metrics
- `/orders` - Order history
- `/equity` - Equity curve
- `/health` - System health

### Logs:
```
logs/trading_2025-11-29.log  - All activity
logs/errors_2025-11-29.log   - Errors only
```

### View Logs:
```bash
# Real-time logs
tail -f logs/trading_2025-11-29.log

# Last 20 lines
tail -20 logs/trading_2025-11-29.log

# Search for signals
grep "Signal:" logs/trading_*.log
```

## 🔄 What Happens During Market Hours

### Every 3 Minutes (9:15 AM - 3:30 PM):

1. **Fetch Data** - Latest Nifty bars from Upstox
2. **Calculate Features** - 32 technical indicators
3. **Generate Signal** - Model predicts Buy/Sell/Hold
4. **Check Risk** - Verify all risk limits
5. **Execute Trade** - Simulate order (paper mode)
6. **Update Dashboard** - Real-time metrics
7. **Log Activity** - Record everything

### Automatic Actions:

✅ **Start trading** at 9:15 AM
✅ **Generate signals** every 3 minutes
✅ **Manage positions** automatically
✅ **Square off** all positions at 3:20 PM
✅ **Stop trading** at 3:30 PM
✅ **Reset counters** daily

## 📈 Expected Behavior

### First Day:
- Bot will start trading at 9:15 AM tomorrow
- Expect 5-15 trades during the day
- Signals will be logged and simulated
- No real money involved

### Monitoring Checklist:

**Morning (9:00 AM):**
- [ ] Check bot is running
- [ ] Verify dashboard accessible
- [ ] Review yesterday's performance

**During Market (10 AM, 12 PM, 2 PM):**
- [ ] Check dashboard for activity
- [ ] Verify signals being generated
- [ ] Monitor PnL (simulated)

**Evening (4:00 PM):**
- [ ] Review day's trades
- [ ] Check logs for errors
- [ ] Analyze performance

## 🎯 Success Criteria (After 1 Week)

✅ **System Stability:**
- No crashes or errors
- Signals generated consistently
- Risk limits respected

✅ **Signal Quality:**
- Reasonable number of trades (5-15/day)
- Mix of Buy/Sell/Hold signals
- Confidence scores make sense

✅ **Performance (Simulated):**
- Win rate > 45%
- Max drawdown < 10%
- Consistent behavior

## ⚠️ Important Notes

### This is Paper Trading:
- ❌ NO real money used
- ❌ NO real orders placed
- ❌ NO connection to your Upstox trading account
- ✅ Only simulated trades
- ✅ Safe for testing

### Before Going Live:
1. Paper trade for at least 1 week
2. Verify performance is acceptable
3. Check no system errors
4. Understand all risk parameters
5. Start with minimal capital (₹10,000-20,000)

## 🛑 How to Stop

### Emergency Stop:
```bash
# Method 1: Press Ctrl+C in terminal

# Method 2: API
curl -X POST http://localhost:8000/stop

# Method 3: Kill process
pkill -f "python main.py"
```

### Normal Stop:
- Bot will automatically stop at 3:30 PM
- Or press Ctrl+C anytime

## 📞 Troubleshooting

### Bot Not Trading:
- Check if market is open (9:15 AM - 3:30 PM IST)
- Verify bot is running: `curl http://localhost:8000/health`
- Check logs for errors

### No Signals Generated:
- Check data fetching is working
- Verify model loaded correctly
- Review risk limits (might be blocking trades)

### Dashboard Not Accessible:
- Check bot is running
- Verify port 8000 is not blocked
- Try: `curl http://localhost:8000`

## 📊 Daily Routine

### Every Trading Day:

**8:45 AM:**
- Check bot is running
- Verify internet connection
- Check Upstox API is accessible

**9:00 AM:**
- Review bot status
- Check dashboard is accessible
- Verify no errors in logs

**9:15 AM:**
- Market opens
- Bot starts trading automatically
- Monitor first few signals

**During Day:**
- Check dashboard periodically
- Monitor for any errors
- Let bot run automatically

**3:30 PM:**
- Market closes
- Bot stops automatically
- Review day's performance

**4:00 PM:**
- Analyze trades
- Check logs
- Note any issues

## 🎯 Next Steps

1. **Let it run** - Bot will trade automatically tomorrow
2. **Monitor daily** - Check dashboard and logs
3. **Analyze weekly** - Review performance after 1 week
4. **Decide** - Continue paper trading or consider live (with caution)

---

**Status:** ✅ PAPER TRADING ACTIVE
**Model:** Improved (32 features, 90 days data)
**Safety:** NO REAL MONEY - Paper mode only
**Dashboard:** http://localhost:8000
**Logs:** logs/trading_2025-11-29.log

**Last Updated:** November 29, 2025 at 5:41 PM IST
