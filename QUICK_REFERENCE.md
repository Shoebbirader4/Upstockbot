# Quick Reference Card

## 🚀 Essential Commands

### Setup
```bash
# Install
pip install -r requirements.txt

# Configure
cp config/config.yaml.template config/config.yaml
cp config/secrets.env.template config/secrets.env
```

### Training
```bash
# Train model (90 days of data)
python -m model_training.train --days 90
```

### Backtesting
```bash
# Backtest model
python -m backtester.run_backtest --model models/model_*.pkl --days 30
```

### Trading
```bash
# Paper trading (no real money)
python main.py --model models/model_*.pkl --mode paper

# Live trading (REAL MONEY!)
python main.py --model models/model_*.pkl --mode live
```

### Docker
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f trading-bot
```

## 📊 Dashboard URLs

- **Home**: http://localhost:8000
- **Status**: http://localhost:8000/status
- **Metrics**: http://localhost:8000/metrics
- **Orders**: http://localhost:8000/orders
- **Health**: http://localhost:8000/health

## 📁 Important Files

| File | Purpose |
|------|---------|
| `config/config.yaml` | Main configuration |
| `config/secrets.env` | API credentials |
| `logs/trading_*.log` | Daily logs |
| `models/*.pkl` | Trained models |
| `data/*.parquet` | Historical data |

## 🔧 Configuration Quick Edit

### Risk Limits
```yaml
risk:
  max_daily_loss: 20000      # Max loss per day (₹)
  max_trades_per_day: 20     # Max trades per day
  max_position_size: 2       # Max lots
```

### Trading Hours
```yaml
trading:
  market_hours:
    start: "09:15"
    end: "15:30"
```

### Model Settings
```yaml
model:
  type: xgboost              # xgboost or lightgbm
  learning_rate: 0.05
  max_depth: 6
  n_estimators: 200
```

## 🎯 Signal Interpretation

| Signal | Value | Action |
|--------|-------|--------|
| BUY | 2 | Open long position |
| HOLD | 1 | No action |
| SELL | 0 | Open short position |

## 📈 Key Metrics

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Win Rate | >55% | 45-55% | <45% |
| Max Drawdown | <5% | 5-10% | >10% |
| Daily PnL | Positive | Break-even | Negative |
| Sharpe Ratio | >1.5 | 1.0-1.5 | <1.0 |

## ⚠️ Risk Parameters

### Position Sizing
- Based on ATR (Average True Range)
- Risk per trade: 2% of capital
- Stop loss: 2 × ATR
- Target: 3 × ATR

### Safety Limits
- Daily loss limit: ₹20,000 (default)
- Max trades/day: 20
- Cooldown after 3 losses: 30 minutes
- Volatility spike threshold: 3× average ATR

## 🔍 Monitoring Checklist

### Before Market Open
- [ ] System running
- [ ] No errors in logs
- [ ] Model loaded correctly
- [ ] Broker connection active
- [ ] Risk limits configured

### During Trading
- [ ] Dashboard accessible
- [ ] Signals generating
- [ ] Orders executing
- [ ] No error alerts
- [ ] PnL tracking

### After Market Close
- [ ] Review trades
- [ ] Check daily PnL
- [ ] Analyze errors
- [ ] Backup logs
- [ ] Plan adjustments

## 🛑 Emergency Procedures

### Stop Trading Immediately
```bash
# Method 1: API
curl -X POST http://localhost:8000/stop

# Method 2: Keyboard
Press Ctrl+C in terminal

# Method 3: Kill process
pkill -f "python main.py"
```

### Flatten All Positions
```bash
# Via broker platform manually
# Or restart bot - it will auto-flatten on shutdown
```

### Check System Status
```bash
# View logs
tail -f logs/trading_$(date +%Y-%m-%d).log

# Check dashboard
curl http://localhost:8000/status

# Check processes
ps aux | grep python
```

## 📞 Alert Channels

### Telegram
- Trade executions
- Daily loss limit
- System errors
- Daily summary

### Email
- Critical errors
- Daily reports
- Weekly summaries

### Dashboard
- Real-time status
- Live metrics
- Order history
- Equity curve

## 🔄 Maintenance Schedule

### Daily
- Monitor dashboard
- Check logs
- Verify trades

### Weekly
- Review performance
- Analyze losing trades
- Check system health

### Monthly
- Retrain model
- Update risk parameters
- Optimize features
- Archive logs

## 💡 Pro Tips

1. **Always start with paper trading**
2. **Backtest on recent data** (last 30 days minimum)
3. **Monitor the first week closely**
4. **Start with conservative risk limits**
5. **Keep detailed notes** of changes
6. **Test configuration changes** in paper mode
7. **Have emergency stop ready**
8. **Review trades daily**
9. **Update model monthly**
10. **Never risk more than you can afford to lose**

## 🐛 Common Issues & Fixes

| Issue | Quick Fix |
|-------|-----------|
| No data | Check API credentials |
| Model not loading | Verify file path |
| Port in use | Change port or kill process |
| Orders not executing | Check broker connection |
| High memory | Reduce data retention |
| Slow training | Use LightGBM or reduce data |

## 📚 Documentation

- **Setup**: `SETUP_GUIDE.md`
- **Usage**: `docs/USAGE.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Summary**: `PROJECT_SUMMARY.md`
- **README**: `README.md`

## 🔐 Security Reminders

- ✅ Never commit `secrets.env`
- ✅ Use strong API keys
- ✅ Rotate credentials regularly
- ✅ Monitor for unauthorized access
- ✅ Keep dependencies updated
- ✅ Backup model files
- ✅ Audit logs periodically

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| Win Rate | 50-60% |
| Risk/Reward | 1:1.5 |
| Max Drawdown | <10% |
| Daily Trades | 5-15 |
| Holding Period | 9-30 min |
| Monthly Return | 5-10% |

## 🎓 Learning Resources

1. Review backtest results carefully
2. Analyze winning vs losing trades
3. Study feature importance
4. Monitor model confidence scores
5. Track market conditions
6. Keep trading journal
7. Learn from mistakes
8. Iterate and improve

---

**Remember**: This is a production trading system. Test thoroughly, start small, and monitor closely!
