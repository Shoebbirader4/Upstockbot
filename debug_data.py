#!/usr/bin/env python
"""Debug data fetching"""

from datetime import datetime, timedelta
from data_ingestion.data_fetcher import DataFetcher
from feature_pipeline.feature_engineer import FeatureEngineer

# Fetch data
end_date = datetime.now()
start_date = end_date - timedelta(days=5)

fetcher = DataFetcher(source='upstox')
df = fetcher.fetch_historical('NIFTY_FUT', start_date, end_date)

print(f"Fetched data shape: {df.shape}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nLast 5 rows:")
print(df.tail())
print(f"\nData types:")
print(df.dtypes)
print(f"\nNull values:")
print(df.isnull().sum())
print(f"\nDuplicate timestamps:")
print(df['timestamp'].duplicated().sum())

# Try feature engineering step by step
print("\n" + "="*70)
print("Creating features step by step...")
engineer = FeatureEngineer()

df_test = df.copy()
print(f"Initial shape: {df_test.shape}")

# Add features one by one
df_test = engineer._add_momentum_features(df_test)
print(f"After momentum: {df_test.shape}, NaN: {df_test.isnull().sum().sum()}")

df_test = engineer._add_trend_features(df_test)
print(f"After trend: {df_test.shape}, NaN: {df_test.isnull().sum().sum()}")

df_test = engineer._add_volatility_features(df_test)
print(f"After volatility: {df_test.shape}, NaN: {df_test.isnull().sum().sum()}")

df_test = engineer._add_mean_reversion_features(df_test)
print(f"After mean reversion: {df_test.shape}, NaN: {df_test.isnull().sum().sum()}")

df_test = engineer._add_volume_features(df_test)
print(f"After volume: {df_test.shape}, NaN: {df_test.isnull().sum().sum()}")

df_test = engineer._add_time_features(df_test)
print(f"After time: {df_test.shape}, NaN: {df_test.isnull().sum().sum()}")

print(f"\nNull values by column:")
print(df_test.isnull().sum())

print(f"\nDropping NaN...")
df_test = df_test.dropna()
print(f"After dropna: {df_test.shape}")
