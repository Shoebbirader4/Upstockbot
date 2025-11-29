# Complete Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Docker & Docker Compose (optional, for containerized deployment)
- Zerodha Kite or Upstox account with API access

## Step-by-Step Setup

### 1. Clone or Download Project

```bash
# If using git
git clone <repository_url>
cd nifty-trading-bot

# Or extract the zip file and navigate to directory
```

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- pandas, numpy (data processing)
- xgboost, lightgbm (ML models)
- scikit-learn (preprocessing)
- fastapi, uvicorn (web dashboard)
- loguru (logging)
- And other dependencies

### 4. Configure the System

#### A. Main Configuration

```bash
# Copy template
cp config/config.yaml.template config/config.yaml

# Edit with your preferred editor
nano config/config.yaml  # or vim, code, notepad++
```

**Key settings to review:**
```yaml
trading:
  asset: NIFTY_FUT  # Your trading instrument
  
risk:
  max_daily_loss: 20000  # Adjust based on your risk tolerance
  max_trades_per_day: 20
  max_position_size: 2  # Number of lots
  
model:
  type: xgboost  # or lightgbm
  
execution:
  broker: zerodha  # or upstox
```

#### B. Secrets Configuration

```bash
# Copy template
cp config/secrets.env.template config/secrets.env

# Edit with your credentials
nano config/secrets.env
```

**Required credentials:**
```bash
# Zerodha API (get from https://kite.trade)
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_ACCESS_TOKEN=your_access_token_here

# Telegram (optional, for alerts)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email (optional, for alerts)
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=alert_recipient@gmail.com
```

**Getting Zerodha API Credentials:**
1. Go to https://kite.trade
2. Sign up for Kite Connect
3. Create an app
4. Note down API Key and Secret
5. Generate access token (valid for 1 day)

**Getting Telegram Bot Token:**
1. Open Telegram and search for @BotFather
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Start a chat with your bot
5. Get your chat ID from https://api.telegram.org/bot<TOKEN>/getUpdates

### 5. Create Required Directories

```bash
mkdir -p data logs models
```

### 6. Test Installation

```bash
# Test imports
python -c "import pandas, numpy, xgboost, lightgbm, fastapi; print('All imports successful!')"

# Run tests
pytest tests/ -v
```

## Training Your First Model

### Step 1: Fetch and Prepare Data

The system will automatically fetch data when you run training. For the first run:

```bash
python -m model_training.train --config config/config.yaml --days 90
```

This will:
- Fetch 90 days of historical data (or generate mock data if API not configured)
- Create features
- Label targets
- Train XGBoost model
- Save model to `./models/` directory

**Expected output:**
```
[INFO] Starting model training pipeline
[INFO] Fetching data from 2024-01-01 to 2024-03-31
[INFO] Fetched 8000 bars for NIFTY_FUT
[INFO] Creating features
[INFO] Creating target labels
[INFO] Label distribution - Sell: 1200, Hold: 5600, Buy: 1200
[INFO] Training set: 6400, Validation set: 1600
[INFO] XGBoost training completed. Best iteration: 145
[INFO] Validation Metrics - F1 Macro: 0.6234, F1 Buy: 0.5891, F1 Sell: 0.6012
[INFO] Model saved to ./models/model_xgboost_20240401_120000.pkl
```

### Step 2: Backtest the Model

```bash
python -m backtester.run_backtest \
    --config config/config.yaml \
    --model models/model_xgboost_20240401_120000.pkl \
    --days 30
```

**Expected output:**
```
============================================================
BACKTEST RESULTS
============================================================
Total Trades: 45
Win Rate: 55.56%
Gross PnL: ₹45,230.00
Net PnL: ₹42,150.00
Total Return: 4.22%
Max Drawdown: -2.15%
Final Capital: ₹1,042,150.00
============================================================
```

**Interpreting Results:**
- **Win Rate > 50%**: Good sign
- **Net PnL > 0**: Profitable after costs
- **Max Drawdown < 10%**: Acceptable risk
- **Total Return**: Should beat risk-free rate

## Running the Trading Bot

### Paper Trading (Recommended First)

Paper trading simulates trades without real money:

```bash
python main.py \
    --config config/config.yaml \
    --model models/model_xgboost_20240401_120000.pkl \
    --mode paper
```

**What happens:**
- Bot starts and waits for market hours (9:15-15:30 IST)
- Fetches data every 3 minutes
- Generates signals
- Simulates order execution
- Logs all activity
- Dashboard available at http://localhost:8000

**Let it run for at least 1 week** to verify:
- No errors occur
- Signals are generated correctly
- Risk limits work as expected
- Monitoring and alerts function

### Live Trading (Real Money - Be Careful!)

**⚠️ WARNING: This trades with real money. Only proceed if:**
- You've backtested thoroughly
- You've paper traded successfully for 1+ week
- You understand all risk parameters
- You have emergency stop procedures ready
- You're monitoring actively

```bash
python main.py \
    --config config/config.yaml \
    --model models/model_xgboost_20240401_120000.pkl \
    --mode live
```

**Start with minimal capital and conservative risk limits!**

## Monitoring Your Bot

### Web Dashboard

Open browser to: http://localhost:8000

**Available endpoints:**
- `/` - Home page
- `/status` - Current trading status
- `/metrics` - Performance metrics
- `/orders` - Order history
- `/equity` - Equity curve
- `/health` - System health check

### Logs

```bash
# View today's logs
tail -f logs/trading_$(date +%Y-%m-%d).log

# View errors only
tail -f logs/errors_$(date +%Y-%m-%d).log

# Search for specific events
grep "Trade Executed" logs/trading_*.log
```

### Alerts

If configured, you'll receive:
- **Telegram messages** for trades, errors, daily summary
- **Email alerts** for critical events

## Docker Deployment (Production)

### Build and Start

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f trading-bot

# Check status
docker-compose ps
```

### Services Started
- `trading-bot`: Main trading application
- `redis`: State management
- `postgres`: Database (TimescaleDB)

### Stop Services

```bash
docker-compose down
```

## Troubleshooting

### Issue: "No module named 'xgboost'"
**Solution:** Activate virtual environment and reinstall
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Config file not found"
**Solution:** Copy template files
```bash
cp config/config.yaml.template config/config.yaml
cp config/secrets.env.template config/secrets.env
```

### Issue: "No data fetched"
**Solution:** 
- Check if using mock data (default behavior)
- Verify broker API credentials in secrets.env
- Check network connectivity
- Verify market is open

### Issue: "Model not loading"
**Solution:**
- Check model file path is correct
- Ensure model was trained successfully
- Verify file permissions

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process or change port in config
```

### Issue: "Permission denied" on scripts
**Solution:**
```bash
chmod +x scripts/*.sh
```

## Daily Operations

### Morning Routine (Before Market Open)
1. Check system is running
2. Review previous day's performance
3. Check for any errors in logs
4. Verify broker account balance
5. Ensure model is up to date

### During Market Hours
1. Monitor dashboard periodically
2. Check for alert notifications
3. Verify trades are executing
4. Watch for unusual behavior

### Evening Routine (After Market Close)
1. Review day's trades
2. Check PnL and metrics
3. Analyze any errors
4. Backup logs if needed
5. Plan any adjustments

### Weekly Maintenance
1. Review weekly performance
2. Analyze losing trades
3. Check system resource usage
4. Update dependencies if needed
5. Consider model retraining

### Monthly Maintenance
1. Retrain model with latest data
2. Backtest new model thoroughly
3. Update risk parameters if needed
4. Review and optimize features
5. Archive old logs

## Performance Optimization

### For Faster Training
- Use LightGBM instead of XGBoost
- Reduce n_estimators
- Use fewer features
- Reduce historical data days

### For Lower Memory Usage
- Use Parquet storage (default)
- Reduce data retention days
- Clear old logs periodically
- Use Redis for state management

### For Better Predictions
- Add more features
- Increase training data
- Tune hyperparameters
- Use ensemble models
- Implement walk-forward optimization

## Security Best Practices

1. **Never commit secrets.env to git**
2. **Use strong API keys**
3. **Rotate credentials regularly**
4. **Limit API permissions** to trading only
5. **Monitor for unauthorized access**
6. **Keep dependencies updated**
7. **Use HTTPS for dashboard** in production
8. **Backup model files** regularly
9. **Audit logs periodically**
10. **Test disaster recovery**

## Getting Help

1. **Check logs** first: `logs/trading_*.log`
2. **Review documentation**: `docs/` folder
3. **Test in paper mode** before asking
4. **Provide error messages** when seeking help
5. **Check configuration** is correct

## Next Steps

After successful setup:
1. ✅ Run paper trading for 1-2 weeks
2. ✅ Monitor and analyze performance
3. ✅ Adjust risk parameters as needed
4. ✅ Consider live trading with small capital
5. ✅ Gradually increase position sizes
6. ✅ Continuously monitor and improve

---

**Remember**: Trading involves risk. Start small, monitor closely, and never risk more than you can afford to lose.
