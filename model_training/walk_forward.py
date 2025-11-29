"""Walk-forward optimization for robust model validation"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List, Dict
from model_training.trainer import ModelTrainer
from feature_pipeline.feature_engineer import FeatureEngineer
from feature_pipeline.target_labeler import TargetLabeler
from backtester.backtest_engine import BacktestEngine
from utils.logger import log

class WalkForwardOptimizer:
    """Perform walk-forward analysis"""
    
    def __init__(self, train_window_days: int = 60, test_window_days: int = 15):
        self.train_window_days = train_window_days
        self.test_window_days = test_window_days
        self.results = []
    
    def run(self, df: pd.DataFrame, model_params: dict) -> Dict:
        """
        Run walk-forward optimization
        
        Args:
            df: DataFrame with OHLCV data
            model_params: Model hyperparameters
        
        Returns:
            Dictionary with aggregated results
        """
        
        log.info(f"Starting walk-forward optimization")
        log.info(f"Train window: {self.train_window_days} days, Test window: {self.test_window_days} days")
        
        # Ensure data is sorted by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate number of folds
        total_days = (df['timestamp'].max() - df['timestamp'].min()).days
        n_folds = (total_days - self.train_window_days) // self.test_window_days
        
        log.info(f"Total days: {total_days}, Number of folds: {n_folds}")
        
        engineer = FeatureEngineer()
        labeler = TargetLabeler()
        
        fold_results = []
        
        for fold in range(n_folds):
            log.info(f"\n{'='*60}")
            log.info(f"Fold {fold + 1}/{n_folds}")
            log.info(f"{'='*60}")
            
            # Calculate date ranges
            train_start_date = df['timestamp'].min() + timedelta(days=fold * self.test_window_days)
            train_end_date = train_start_date + timedelta(days=self.train_window_days)
            test_start_date = train_end_date
            test_end_date = test_start_date + timedelta(days=self.test_window_days)
            
            # Split data
            train_df = df[(df['timestamp'] >= train_start_date) & 
                         (df['timestamp'] < train_end_date)].copy()
            test_df = df[(df['timestamp'] >= test_start_date) & 
                        (df['timestamp'] < test_end_date)].copy()
            
            if len(train_df) < 100 or len(test_df) < 20:
                log.warning(f"Insufficient data for fold {fold + 1}, skipping")
                continue
            
            log.info(f"Train: {train_start_date.date()} to {train_end_date.date()} ({len(train_df)} bars)")
            log.info(f"Test: {test_start_date.date()} to {test_end_date.date()} ({len(test_df)} bars)")
            
            try:
                # Feature engineering
                train_df = engineer.create_features(train_df, fit_scaler=True)
                test_df = engineer.create_features(test_df, fit_scaler=False)
                
                # Label targets
                train_df = labeler.create_labels(train_df)
                test_df = labeler.create_labels(test_df)
                
                if len(train_df) < 50 or len(test_df) < 10:
                    log.warning(f"Insufficient data after processing, skipping fold {fold + 1}")
                    continue
                
                # Train model
                trainer = ModelTrainer(model_type=model_params.get('type', 'xgboost'))
                feature_columns = engineer.get_feature_columns()
                
                metrics = trainer.train(
                    train_df,
                    feature_columns=feature_columns,
                    train_split=1.0,  # Use all training data
                    **model_params
                )
                
                # Test on out-of-sample data
                X_test = test_df[feature_columns].values
                y_test = test_df['target'].values
                
                y_pred_proba = trainer.predict_proba(X_test)
                y_pred = y_pred_proba.argmax(axis=1)
                
                # Calculate test metrics
                from sklearn.metrics import f1_score, accuracy_score
                
                test_f1_macro = f1_score(y_test, y_pred, average='macro')
                test_accuracy = accuracy_score(y_test, y_pred)
                
                # Run backtest on test period
                backtest_engine = BacktestEngine()
                backtest_metrics = backtest_engine.run(test_df, y_pred)
                
                fold_result = {
                    'fold': fold + 1,
                    'train_start': train_start_date,
                    'train_end': train_end_date,
                    'test_start': test_start_date,
                    'test_end': test_end_date,
                    'train_samples': len(train_df),
                    'test_samples': len(test_df),
                    'test_f1_macro': test_f1_macro,
                    'test_accuracy': test_accuracy,
                    'backtest_pnl': backtest_metrics.get('net_pnl', 0),
                    'backtest_win_rate': backtest_metrics.get('win_rate', 0),
                    'backtest_sharpe': backtest_metrics.get('sharpe_ratio', 0),
                    'backtest_trades': backtest_metrics.get('total_trades', 0)
                }
                
                fold_results.append(fold_result)
                
                log.info(f"Fold {fold + 1} Results:")
                log.info(f"  Test F1: {test_f1_macro:.4f}, Accuracy: {test_accuracy:.4f}")
                log.info(f"  Backtest PnL: {backtest_metrics.get('net_pnl', 0):.2f}, "
                        f"Win Rate: {backtest_metrics.get('win_rate', 0):.2%}")
                
            except Exception as e:
                log.error(f"Error in fold {fold + 1}: {e}")
                continue
        
        # Aggregate results
        if not fold_results:
            log.error("No successful folds completed")
            return {}
        
        results_df = pd.DataFrame(fold_results)
        
        aggregated = {
            'n_folds': len(fold_results),
            'avg_test_f1': results_df['test_f1_macro'].mean(),
            'std_test_f1': results_df['test_f1_macro'].std(),
            'avg_test_accuracy': results_df['test_accuracy'].mean(),
            'avg_backtest_pnl': results_df['backtest_pnl'].mean(),
            'total_backtest_pnl': results_df['backtest_pnl'].sum(),
            'avg_win_rate': results_df['backtest_win_rate'].mean(),
            'avg_sharpe': results_df['backtest_sharpe'].mean(),
            'total_trades': results_df['backtest_trades'].sum(),
            'fold_results': fold_results
        }
        
        log.info(f"\n{'='*60}")
        log.info("WALK-FORWARD OPTIMIZATION RESULTS")
        log.info(f"{'='*60}")
        log.info(f"Completed Folds: {aggregated['n_folds']}")
        log.info(f"Avg Test F1: {aggregated['avg_test_f1']:.4f} ± {aggregated['std_test_f1']:.4f}")
        log.info(f"Avg Test Accuracy: {aggregated['avg_test_accuracy']:.4f}")
        log.info(f"Total Backtest PnL: ₹{aggregated['total_backtest_pnl']:.2f}")
        log.info(f"Avg Win Rate: {aggregated['avg_win_rate']:.2%}")
        log.info(f"Avg Sharpe: {aggregated['avg_sharpe']:.2f}")
        log.info(f"{'='*60}")
        
        return aggregated
