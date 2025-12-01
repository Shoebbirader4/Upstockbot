"""Debug why we're not getting today's data"""

import requests
from datetime import datetime, timedelta
from utils.config_loader import config

token = config.get_secret('UPSTOX_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

print("=" * 60)
print("DEBUGGING UPSTOX API - TODAY'S DATA")
print("=" * 60)

now = datetime.now()
print(f"\nCurrent time: {now}")

# Try different date formats and ranges
test_cases = [
    ("Today only", "2025-12-01", "2025-12-01"),
    ("Today from yesterday", "2025-12-01", "2025-11-30"),
    ("Last 2 days", "2025-12-01", "2025-11-29"),
    ("Last 3 days", "2025-12-01", "2025-11-28"),
]

for name, to_date, from_date in test_cases:
    print(f"\n{name}: from {from_date} to {to_date}")
    url = f'https://api.upstox.com/v2/historical-candle/NSE_INDEX|Nifty 50/1minute/{to_date}/{from_date}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            candles = data.get('data', {}).get('candles', [])
            print(f"  Status: {response.status_code}")
            print(f"  Candles: {len(candles)}")
            
            if candles:
                # Show first and last candle
                print(f"  First: {candles[-1][:2]}")  # Timestamp and open
                print(f"  Last: {candles[0][:2]}")
        else:
            print(f"  Error: {response.status_code}")
            print(f"  Response: {data}")
    except Exception as e:
        print(f"  Exception: {e}")

# Check if there's intraday data endpoint
print("\n" + "=" * 60)
print("CHECKING INTRADAY DATA ENDPOINT")
print("=" * 60)

# Try intraday endpoint (if exists)
intraday_url = f'https://api.upstox.com/v2/historical-candle/intraday/NSE_INDEX|Nifty 50/1minute'

print(f"\nTrying intraday endpoint...")
try:
    response = requests.get(intraday_url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        candles = data.get('data', {}).get('candles', [])
        print(f"Candles: {len(candles)}")
        if candles:
            print(f"Latest: {candles[0]}")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 60)
print("POSSIBLE ISSUES")
print("=" * 60)
print("\n1. Upstox API might have delay in publishing today's data")
print("2. Historical endpoint might not include current day")
print("3. Need to use different endpoint for intraday/live data")
print("4. API might require different parameters for current day")
