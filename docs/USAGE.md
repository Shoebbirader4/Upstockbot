# Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repo_url>
cd nifty-trading-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy configuration templates
cp config/config.yaml.template config/config.yaml
cp config/secrets.env.template config/secrets.env

# Edit config files with your settings
nano config/config.yaml
nano config/secrets.env
```

**Important**: Add your broker API credentials to `config/secrets.env`

### 3. Train Model

```bash
# Train on 90 days of historical data
python -m model_training.train --config config/config.yaml --days 90

# Model will be saved to ./models/
```

### 4. Run Backtest

```bash
# Backtest the trained model
python -m backtester.run_backtest \
    --config config/config.yaml \
    --model models/model_xgboost_20240101_120000.pkl \
    --days 30
```

### 5. Paper Trading

```bash
# Start in paper trading mode (no real money)
python main.py \
    --config config/config.yaml \
    --model models/model_xgboost_20240101_120000.pkl \
    --mode paper
```

### 6. Live Trading

```bash
# Start live trading (REAL MONEY - BE CAREFUL!)
python main.py \
    --config config/config.yaml \
    --model models/model_xgboost_20240101_120000.pkl \
    --mode live
```

## Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f trading-bot

# Stop services
docker-compose down
```

## Monitoring

### Dashboard
Access the web dashboard at: http://localhost:8000

Endpoints:
- `/` - Home
- `/status` - Current trading status
- `/metrics` - Performance metrics
- `/orders` - Order history
- `/equity` - Equity curve

### Logs
Logs are stored in `./logs/`:
- `trading_YYYY-MM-DD.log` - Daily trading logs
- `errors_YYYY-MM-DD.log` - Error logs only

### Alerts
Configure Telegram/Email alerts in `config/secrets.env`:
- Trade executions
- Daily loss limit reached
- System errors
- Daily summary

## Configuration Options

### Trading Parameters
```yaml
trading:
  asset: NIFTY_FUT
  timeframe: 3min
  market_hours:
    start: "09:15"
    end: "15:30"
```

### Risk Management
```yaml
risk:
  max_daily_loss: 20000  # ₹20,000
  max_trades_per_day: 20
  max_position_size: 2  # lots
  volatility_spike_threshold: 3.0
  cooldown_after_losses: 3
  cooldown_minutes: 30
```

### Model Parameters
```yaml
model:
  type: xgboost  # or lightgbm
  train_split: 0.8
  max_depth: 6
  learning_rate: 0.05
  n_estimators: 200
```

## Common Tasks

### Update Model
```bash
# Train new model
python -m model_training.train --days 90

# Test with backtest
python -m backtester.run_backtest --model models/new_model.pkl --days 30

# Deploy if performance is good
# Update docker-compose.yml or restart with new model path
```

### Check Performance
```bash
# View dashboard
curl http://localhost:8000/metrics

# Check logs
tail -f logs/trading_$(date +%Y-%m-%d).log
```

### Emergency Stop
```bash
# Stop via API
curl -X POST http://localhost:8000/stop

# Or press Ctrl+C in terminal
# Or kill process
pkill -f "python main.py"
```

## Troubleshooting

### No Data Fetched
- Check broker API credentials in `config/secrets.env`
- Verify market is open
- Check network connectivity

### Model Not Loading
- Verify model file exists
- Check file path is correct
- Ensure model was trained with same feature set

### Orders Not Executing
- Check broker API credentials
- Verify account has sufficient balance
- Check if in paper trading mode
- Review risk limits (may be blocking trades)

### High Memory Usage
- Reduce historical data retention
- Use Parquet instead of in-memory storage
- Restart service periodically

## Best Practices

1. **Always start with paper trading** before going live
2. **Backtest thoroughly** on out-of-sample data
3. **Monitor daily** - check dashboard and logs
4. **Set conservative risk limits** initially
5. **Keep models updated** - retrain monthly
6. **Test configuration changes** in paper mode first
7. **Have emergency stop procedures** ready
8. **Monitor broker account** separately
9. **Keep logs** for audit trail
10. **Review performance** weekly

## Safety Checklist

Before going live:
- [ ] Backtested on recent data (>30 days)
- [ ] Paper traded successfully (>1 week)
- [ ] Risk limits configured appropriately
- [ ] Broker API credentials verified
- [ ] Monitoring and alerts working
- [ ] Emergency stop procedure tested
- [ ] Sufficient account balance
- [ ] Understand all configuration settings
- [ ] Logs and dashboard accessible
- [ ] Backup plan if system fails

## Support

For issues or questions:
1. Check logs in `./logs/`
2. Review configuration in `config/config.yaml`
3. Test in paper mode first
4. Check broker API documentation
