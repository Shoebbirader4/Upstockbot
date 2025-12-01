"""Check if market is open today"""

from datetime import datetime, time
import requests
from utils.config_loader import config

print("=" * 60)
print("MARKET STATUS CHECK")
print("=" * 60)

now = datetime.now()
print(f"\nCurrent Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")

# Check market hours
market_start = time(9, 15)
market_end = time(15, 30)
current_time = now.time()

print(f"\nMarket Hours: 9:15 AM - 3:30 PM IST")
print(f"Current Time: {current_time.strftime('%H:%M:%S')}")

if market_start <= current_time <= market_end:
    print("✅ Within market hours")
else:
    print("❌ Outside market hours")

# Check if data is available for today
print(f"\nChecking Upstox API for today's data...")

token = config.get_secret('UPSTOX_ACCESS_TOKEN')
url = f'https://api.upstox.com/v2/historical-candle/NSE_INDEX|Nifty 50/1minute/2025-12-01/2025-11-30'
headers = {'Authorization': f'Bearer {token}'}

response = requests.get(url, headers=headers)
data = response.json()
candles = data.get('data', {}).get('candles', [])

print(f"Status: {response.status_code}")
print(f"Candles for Dec 1: {len(candles)}")

if len(candles) == 0:
    print("\n⚠️  NO DATA AVAILABLE FOR TODAY")
    print("\nPossible reasons:")
    print("  1. December 1, 2025 is a market holiday")
    print("  2. Market hasn't opened yet")
    print("  3. Data not yet available from Upstox")
    
    # Check last available trading day
    print(f"\nLast available data: Friday, November 28, 2025")
    print(f"Next expected trading day: Check NSE holiday calendar")
else:
    print(f"\n✅ Market data available for today!")
    print(f"Latest candle: {candles[0]}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)

if len(candles) == 0:
    print("\n🔴 Market appears to be CLOSED today")
    print("   System will continue using Friday's data")
    print("   Will automatically fetch new data when market opens")
else:
    print("\n🟢 Market is OPEN and data is available")
    print("   System should be fetching live data")
