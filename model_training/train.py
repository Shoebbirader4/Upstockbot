#!/usr/bin/env python
"""Training script for ML model"""

import argparse
from datetime import datetime, timedelta
from data_ingestion.data_fetcher import DataFetcher
from data_ingestion.data_storage import DataStorage
from feature_pipeline.feature_engineer import FeatureEngineer
from feature_pipeline.target_labeler import TargetLabeler
from model_training.trainer import ModelTrainer
from utils.config_loader import config
from utils.logger import log

def main():
    parser = argparse.ArgumentParser(description='Train Nifty trading model')
    parser.add_argument('--config', type=str, default='config/config.yaml')
    parser.add_argument('--days', type=int, default=90, help='Days of historical data')
    args = parser.parse_args()
    
    log.info("Starting model training pipeline")
    
    # Load configuration
    symbol = config.get('trading.asset', 'NIFTY_FUT')
    model_type = config.get('model.type', 'xgboost')
    
    # Fetch historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    log.info(f"Fetching data from {start_date} to {end_date}")
    fetcher = DataFetcher(source=config.get('data.source', 'zerodha'))
    df = fetcher.fetch_historical(symbol, start_date, end_date)
    
    if df.empty:
        log.error("No data fetched. Exiting.")
        return
    
    # Save to storage
    storage = DataStorage(
        storage_path=config.get('data.storage_path', './data'),
        storage_type=config.get('data.storage_type', 'parquet')
    )
    storage.save_ohlcv(df, symbol)
    
    # Feature engineering
    log.info("Creating features")
    engineer = FeatureEngineer()
    df = engineer.create_features(df, fit_scaler=True)
    
    # Create labels
    log.info("Creating target labels")
    labeler = TargetLabeler(
        horizon_bars=config.get('target.horizon_bars', 3),
        buy_threshold=config.get('target.buy_threshold', 0.001),
        sell_threshold=config.get('target.sell_threshold', -0.001)
    )
    df = labeler.create_labels(df)
    
    if df.empty:
        log.error("No data after feature engineering. Exiting.")
        return
    
    # Train model
    log.info("Training model")
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
    log.info(f"Training completed. Model saved to {model_path}")
    log.info(f"Metrics: {metrics}")

if __name__ == "__main__":
    main()
