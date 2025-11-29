#!/usr/bin/env python
"""Run backtest on trained model"""

import argparse
from datetime import datetime, timedelta
import pandas as pd
from data_ingestion.data_storage import DataStorage
from feature_pipeline.feature_engineer import FeatureEngineer
from model_training.trainer import ModelTrainer
from backtester.backtest_engine import BacktestEngine
from utils.config_loader import config
from utils.logger import log

def main():
    parser = argparse.ArgumentParser(description='Run backtest')
    parser.add_argument('--config', type=str, default='config/config.yaml')
    parser.add_argument('--model', type=str, required=True, help='Path to trained model')
    parser.add_argument('--days', type=int, default=30, help='Days to backtest')
    args = parser.parse_args()
    
    log.info("Starting backtest")
    
    # Load data
    symbol = config.get('trading.asset', 'NIFTY_FUT')
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    storage = DataStorage(
        storage_path=config.get('data.storage_path', './data'),
        storage_type=config.get('data.storage_type', 'parquet')
    )
    
    df = storage.load_ohlcv(symbol, start_date, end_date)
    
    if df.empty:
        log.error("No data loaded. Exiting.")
        return
    
    # Feature engineering
    log.info("Creating features")
    engineer = FeatureEngineer()
    df = engineer.create_features(df, fit_scaler=True)
    
    # Load model
    log.info(f"Loading model from {args.model}")
    trainer = ModelTrainer()
    if not trainer.load_model(args.model):
        log.error("Failed to load model. Exiting.")
        return
    
    # Generate signals
    log.info("Generating signals")
    X = df[trainer.feature_columns].values
    probas = trainer.predict_proba(X)
    signals = probas.argmax(axis=1)
    
    # Run backtest
    log.info("Running backtest")
    engine = BacktestEngine(
        initial_capital=config.get('backtesting.initial_capital', 1000000),
        transaction_cost_bps=config.get('backtesting.transaction_cost_bps', 5),
        slippage_bps=config.get('backtesting.slippage_bps', 2),
        latency_ms=config.get('backtesting.latency_ms', 100)
    )
    
    atr_values = df['ATR_14'].values if 'ATR_14' in df.columns else None
    metrics = engine.run(df, signals, atr_values)
    
    # Display results
    log.info("=" * 70)
    log.info("BACKTEST RESULTS")
    log.info("=" * 70)
    log.info(f"\nTrading Performance:")
    log.info(f"  Total Trades: {metrics.get('total_trades', 0)}")
    log.info(f"  Winning Trades: {metrics.get('winning_trades', 0)}")
    log.info(f"  Losing Trades: {metrics.get('losing_trades', 0)}")
    log.info(f"  Win Rate: {metrics.get('win_rate', 0):.2%}")
    
    log.info(f"\nProfitability:")
    log.info(f"  Gross PnL: ₹{metrics.get('gross_pnl', 0):,.2f}")
    log.info(f"  Net PnL: ₹{metrics.get('net_pnl', 0):,.2f}")
    log.info(f"  Avg Win: ₹{metrics.get('avg_win', 0):,.2f}")
    log.info(f"  Avg Loss: ₹{metrics.get('avg_loss', 0):,.2f}")
    log.info(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
    log.info(f"  Expectancy: ₹{metrics.get('expectancy', 0):.2f}")
    
    log.info(f"\nReturns & Risk:")
    log.info(f"  Total Return: {metrics.get('total_return_pct', 0):.2f}%")
    log.info(f"  Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
    log.info(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    log.info(f"  Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}")
    log.info(f"  Calmar Ratio: {metrics.get('calmar_ratio', 0):.2f}")
    log.info(f"  Recovery Factor: {metrics.get('recovery_factor', 0):.2f}")
    
    log.info(f"\nCapital:")
    log.info(f"  Initial: ₹{config.get('backtesting.initial_capital', 1000000):,.2f}")
    log.info(f"  Final: ₹{metrics.get('final_capital', 0):,.2f}")
    log.info("=" * 70)
    
    # Performance rating
    sharpe = metrics.get('sharpe_ratio', 0)
    if sharpe > 2:
        rating = "Excellent"
    elif sharpe > 1:
        rating = "Good"
    elif sharpe > 0.5:
        rating = "Fair"
    else:
        rating = "Poor"
    
    log.info(f"\nPerformance Rating: {rating} (Sharpe: {sharpe:.2f})")
    log.info("=" * 70)

if __name__ == "__main__":
    main()
