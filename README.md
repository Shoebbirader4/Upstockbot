# Production-Grade Intraday Nifty ML Trading Bot

## Overview
Complete production-ready intraday trading system for Nifty Futures using XGBoost/LightGBM with 3-minute bars.

## Features
- Real-time data ingestion with validation
- Rolling-window feature engineering (no lookahead bias)
- ML-based signal generation (Buy/Sell/Hold)
- Risk management and position sizing
- Live execution with Zerodha/Upstox
- Comprehensive monitoring and alerting
- Docker-based deployment

## Architecture
```
├── data_ingestion/      # Historical & live data pipeline
├── feature_pipeline/    # Feature engineering modules
├── model_training/      # ML training & registry
├── signal_engine/       # Real-time signal generation
├── risk_manager/        # Risk controls & position sizing
├── execution_engine/    # Order placement & management
├── backtester/          # Strategy backtesting
├── monitoring/          # Logging, alerts, dashboards
├── utils/               # Shared utilities
├── config/              # Configuration files
└── docker/              # Docker deployment files
```

## Quick Start

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp config/config.yaml.template config/config.yaml
cp config/secrets.env.template config/secrets.env
# Edit with your API keys and settings
```

### 3. Run Backtest
```bash
python -m backtester.run_backtest --config config/config.yaml
```

### 4. Train Model
```bash
python -m model_training.train --config config/config.yaml
```

### 5. Live Trading (Paper/Live)
```bash
python main.py --mode live --config config/config.yaml
```

## Safety Features
- Max daily loss limit
- Max trades per day
- Volatility spike filter
- Auto-flatten on errors
- Idempotent order placement
- Cooldown on consecutive losses

## Monitoring
- FastAPI dashboard: http://localhost:8000
- Telegram alerts
- Email notifications
- Real-time PnL tracking

## Environment Variables
See `config/secrets.env.template` for required API keys and credentials.

## License
MIT
