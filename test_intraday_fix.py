"""Test if intraday fix works"""

from data_ingestion.upstox_client import UpstoxClient
from datetime import datetime

client = UpstoxClient()

print("Testing intraday data fetch...")
print("=" * 60)

# Fetch today's data
df = client.get_historical_data(
    'NSE_INDEX|Nifty 50',
    '3minute',
    datetime.now(),
    datetime.now()
)

print(f"\nBars fetched: {len(df)}")

if not df.empty:
    print(f"\n✅ SUCCESS! Got today's data!")
    print(f"\nDate range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"\nLatest 5 bars:")
    print(df.tail(5))
    print(f"\nCurrent price: {df['close'].iloc[-1]:.2f}")
else:
    print("\n❌ No data fetched")
