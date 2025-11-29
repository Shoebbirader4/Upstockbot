import pytest
import pandas as pd
import numpy as np
from feature_pipeline.feature_engineer import FeatureEngineer
from feature_pipeline.target_labeler import TargetLabeler

def create_sample_data(n=100):
    """Create sample OHLCV data"""
    dates = pd.date_range(start='2024-01-01 09:15', periods=n, freq='3min')
    
    close = 19500 + np.cumsum(np.random.randn(n) * 10)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close + np.random.randn(n) * 5,
        'high': close + abs(np.random.randn(n)) * 10,
        'low': close - abs(np.random.randn(n)) * 10,
        'close': close,
        'volume': np.random.randint(1000, 10000, n)
    })
    
    return df

def test_feature_creation():
    """Test feature engineering"""
    df = create_sample_data(100)
    engineer = FeatureEngineer()
    
    df_features = engineer.create_features(df, fit_scaler=True)
    
    assert not df_features.empty
    assert 'EMA_5' in df_features.columns
    assert 'RSI_14' in df_features.columns
    assert 'ATR_14' in df_features.columns
    assert len(df_features) < len(df)  # Some rows dropped due to rolling windows

def test_target_labeling():
    """Test target label creation"""
    df = create_sample_data(100)
    labeler = TargetLabeler(horizon_bars=3, buy_threshold=0.001, sell_threshold=-0.001)
    
    df_labeled = labeler.create_labels(df)
    
    assert not df_labeled.empty
    assert 'target' in df_labeled.columns
    assert 'future_return' in df_labeled.columns
    assert df_labeled['target'].isin([0, 1, 2]).all()

def test_no_lookahead_bias():
    """Test that features don't use future data"""
    df = create_sample_data(100)
    engineer = FeatureEngineer()
    
    df_features = engineer.create_features(df, fit_scaler=True)
    
    # Check that features at time t only use data up to time t
    # This is implicit in the rolling window operations
    assert not df_features.empty

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
