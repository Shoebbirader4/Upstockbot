#!/usr/bin/env python
"""Train improved model with advanced features and ensemble"""

import argparse
from datetime import datetime, timedelta
from data_ingestion.data_fetcher import DataFetcher
from data_ingestion.data_storage import DataStorage
from feature_pipeline.feature_engineer import FeatureEngineer
from feature_pipeline.target_labeler import TargetLabeler
from model_training.ensemble_trainer import EnsembleTrainer
from model_training.walk_forward import WalkForwardOptimizer
from utils.config_loader import config
from utils.logger import log

def main():
    parser = argparse.ArgumentParser(description='Train improved Nifty trading model')
    parser.add_argument('--config', type=str, default='config/config.yaml')
    parser.add_argument('--days', type=int, default=90, help='Days of historical data')
    parser.add_argument('--use-ensemble', action='store_true', help='Use ensemble model')
    parser.add_argument('--walk-forward', action='store_true', help='Run walk-forward optimization')
    args = parser.parse_args()
    
    log.info("="*70)
    log.info("IMPROVED MODEL TRAINING PIPELINE")
    log.info("="*70)
    log.info(f"Training days: {args.days}")
    log.info(f"Use ensemble: {args.use_ensemble}")
    log.info(f"Walk-forward: {args.walk_forward}")
    log.info("="*70)
    
    # Load configuration
    symbol = config.get('trading.asset', 'NIFTY_FUT')
    model_type = config.get('model.type', 'xgboost')
    
    # Fetch historical data (more data = better model)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    log.info(f"\n1. Fetching data from {start_date.date()} to {end_date.date()}")
    fetcher = DataFetcher(source=config.get('data.source', 'upstox'))
    df = fetcher.fetch_historical(symbol, start_date, end_date)
    
    if df.empty:
        log.error("No data fetched. Exiting.")
        return
    
    log.info(f"   ✓ Fetched {len(df)} bars")
    
    # Save to storage
    storage = DataStorage(
        storage_path=config.get('data.storage_path', './data'),
        storage_type=config.get('data.storage_type', 'parquet')
    )
    storage.save_ohlcv(df, symbol)
    
    # Feature engineering with advanced features
    log.info("\n2. Creating advanced features")
    engineer = FeatureEngineer()
    df = engineer.create_features(df, fit_scaler=True)
    log.info(f"   ✓ Created {len(engineer.get_feature_columns())} features")
    log.info(f"   ✓ Data shape after features: {df.shape}")
    
    # Create labels with dynamic thresholds
    log.info("\n3. Creating target labels (dynamic thresholds)")
    labeler = TargetLabeler(
        horizon_bars=config.get('target.horizon_bars', 3),
        buy_threshold=config.get('target.buy_threshold', 0.001),
        sell_threshold=config.get('target.sell_threshold', -0.001),
        use_dynamic_thresholds=True  # Use volatility-based thresholds
    )
    df = labeler.create_labels(df)
    
    if df.empty:
        log.error("No data after feature engineering. Exiting.")
        return
    
    log.info(f"   ✓ Final data shape: {df.shape}")
    
    # Walk-forward optimization (if requested)
    if args.walk_forward:
        log.info("\n4. Running walk-forward optimization")
        wf_optimizer = WalkForwardOptimizer(train_window_days=60, test_window_days=15)
        
        model_params = {
            'type': model_type,
            'max_depth': config.get('model.max_depth', 6),
            'learning_rate': config.get('model.learning_rate', 0.05),
            'n_estimators': config.get('model.n_estimators', 200),
            'early_stopping_rounds': config.get('model.early_stopping_rounds', 50)
        }
        
        wf_results = wf_optimizer.run(df, model_params)
        
        if wf_results:
            log.info(f"\n   Walk-Forward Results:")
            log.info(f"   ✓ Avg F1: {wf_results['avg_test_f1']:.4f}")
            log.info(f"   ✓ Total PnL: ₹{wf_results['total_backtest_pnl']:.2f}")
            log.info(f"   ✓ Avg Sharpe: {wf_results['avg_sharpe']:.2f}")
    
    # Train model (ensemble or single)
    if args.use_ensemble:
        log.info("\n5. Training ensemble model (XGBoost + LightGBM + MLP)")
        trainer = EnsembleTrainer(registry_path=config.get('model.registry_path', './models'))
    else:
        log.info(f"\n5. Training {model_type} model")
        from model_training.trainer import ModelTrainer
        trainer = ModelTrainer(
            model_type=model_type,
            registry_path=config.get('model.registry_path', './models')
        )
    
    feature_columns = engineer.get_feature_columns()
    
    metrics = trainer.train(
        df,
        feature_columns=feature_columns,
        train_split=config.get('model.train_split', 0.8),
        max_depth=config.get('model.max_depth', 6),
        learning_rate=config.get('model.learning_rate', 0.05),
        n_estimators=config.get('model.n_estimators', 200),
        early_stopping_rounds=config.get('model.early_stopping_rounds', 50)
    )
    
    # Save model
    model_path = trainer.save_model()
    
    log.info("\n" + "="*70)
    log.info("TRAINING COMPLETED")
    log.info("="*70)
    log.info(f"Model saved: {model_path}")
    log.info(f"\nValidation Metrics:")
    log.info(f"  F1 Macro: {metrics.get('f1_macro', 0):.4f}")
    log.info(f"  F1 Buy: {metrics.get('f1_buy', 0):.4f}")
    log.info(f"  F1 Sell: {metrics.get('f1_sell', 0):.4f}")
    log.info(f"  Accuracy: {metrics.get('accuracy', 0):.4f}")
    log.info("="*70)
    
    log.info("\nNext steps:")
    log.info(f"1. Backtest: python -m backtester.run_backtest --model {model_path}")
    log.info(f"2. Paper trade: python main.py --model {model_path} --mode paper")

if __name__ == "__main__":
    main()
