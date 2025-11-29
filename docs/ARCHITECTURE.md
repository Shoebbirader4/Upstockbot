# System Architecture

## Overview
Production-grade intraday trading system for Nifty Futures using ML-based signal generation with comprehensive risk management and monitoring.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Pipeline                            │
├─────────────────────────────────────────────────────────────┤
│  Data Fetcher → Validator → Storage (Parquet/TimescaleDB)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Feature Engineering                         │
├─────────────────────────────────────────────────────────────┤
│  Momentum | Trend | Volatility | Mean Reversion | Volume   │
│  Time Context | RobustScaler                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ML Model (XGBoost/LightGBM)              │
├─────────────────────────────────────────────────────────────┤
│  Training → Validation → Model Registry → Versioning       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Signal Generation                          │
├─────────────────────────────────────────────────────────────┤
│  Real-time Features → Model Inference → Signal (Buy/Sell/Hold)│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Risk Management                           │
├─────────────────────────────────────────────────────────────┤
│  Daily Loss Limit | Max Trades | Volatility Filter         │
│  Position Sizing | Cooldown Logic                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Order Execution                            │
├─────────────────────────────────────────────────────────────┤
│  Zerodha/Upstox API | Retry Logic | Idempotent Orders      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Monitoring & Alerts                         │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Dashboard | Telegram | Email | Logging            │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Pipeline
- **Ingestion**: Fetches 3-minute OHLCV bars from Zerodha/Upstox
- **Validation**: Removes duplicates, validates OHLC relationships
- **Storage**: Parquet files (local) or TimescaleDB (production)
- **No Forward Bias**: Strict chronological ordering

### 2. Feature Engineering
- **Momentum**: EMA_5, EMA_10, EMA_Cross, EMA_Slope
- **Trend**: VWAP, VWAP_Distance
- **Volatility**: ATR_14, Normalized_ATR
- **Mean Reversion**: RSI_14, Rolling_ZScore_Return
- **Volume**: Volume_Ratio_20
- **Time Context**: Hour/Day cyclic encoding
- **Scaling**: RobustScaler for outlier resistance

### 3. Target Labeling
- **Horizon**: 3 bars (9 minutes)
- **Classes**: 
  - Buy: future_return > +0.1%
  - Hold: -0.1% ≤ future_return ≤ +0.1%
  - Sell: future_return < -0.1%
- **No Leakage**: Uses shift(-horizon) correctly

### 4. ML Model
- **Type**: XGBoost or LightGBM Classifier
- **Training**: Chronological 80/20 split
- **Class Weights**: Balanced for imbalanced classes
- **Early Stopping**: Prevents overfitting
- **Registry**: Versioned model artifacts with metadata

### 5. Backtesting
- **Realistic Simulation**: Transaction costs, slippage, latency
- **Position Sizing**: ATR-based
- **Stop Loss/Target**: 2x ATR / 3x ATR
- **Metrics**: PnL, Win Rate, Max Drawdown, Sharpe Ratio

### 6. Risk Management
- **Daily Loss Limit**: Auto-flatten at threshold
- **Max Trades/Day**: Prevents overtrading
- **Volatility Filter**: Blocks trades during spikes
- **Cooldown**: After consecutive losses
- **Position Sizing**: Risk-adjusted based on ATR

### 7. Execution Engine
- **Broker Integration**: Zerodha Kite / Upstox API
- **Retry Logic**: 3 attempts with exponential backoff
- **Idempotent Orders**: Prevents duplicate executions
- **Auto Square-off**: Before market close (15:20)

### 8. Monitoring
- **Dashboard**: FastAPI web interface (port 8000)
- **Alerts**: Telegram + Email
- **Logging**: Structured logs with rotation
- **Metrics**: Real-time PnL, positions, signals

## Data Flow

1. **Training Phase**:
   - Fetch historical data → Create features → Label targets
   - Train model with cross-validation → Save to registry
   - Run backtest → Validate performance

2. **Live Trading Phase**:
   - Fetch latest 3-min bars every 3 minutes
   - Generate features (no lookahead)
   - Model inference → Signal generation
   - Risk checks → Order execution
   - Monitor & alert

## Safety Mechanisms

1. **No Lookahead Bias**: All features use only past data
2. **Risk Limits**: Multiple layers of protection
3. **Paper Trading Mode**: Test without real money
4. **Auto-Flatten**: On errors or loss limits
5. **Idempotent Orders**: Prevent duplicate trades
6. **Monitoring**: Real-time alerts on issues

## Deployment

### Development
```bash
python main.py --model models/model.pkl --mode paper
```

### Production (Docker)
```bash
docker-compose up -d
```

### Monitoring
- Dashboard: http://localhost:8000
- Logs: ./logs/
- Metrics: http://localhost:8000/metrics

## Configuration

All settings in `config/config.yaml`:
- Trading parameters
- Risk limits
- Model hyperparameters
- Broker credentials (in secrets.env)

## Assumptions & Limitations

1. **Data Source**: Mock data used by default - integrate real broker API
2. **Broker API**: Placeholder implementations - needs actual integration
3. **Slippage**: Fixed 0.02% - may vary in reality
4. **Latency**: 100ms assumed - measure actual latency
5. **Market Impact**: Not modeled for large orders
6. **Holidays**: Not automatically handled - add holiday calendar
7. **Corporate Actions**: Not handled - add logic for splits/dividends

## Future Enhancements

1. Multi-timeframe analysis
2. Ensemble models
3. Reinforcement learning
4. Advanced order types (limit, stop-limit)
5. Portfolio optimization
6. Real-time model retraining
7. A/B testing framework
8. Advanced risk metrics (VaR, CVaR)
