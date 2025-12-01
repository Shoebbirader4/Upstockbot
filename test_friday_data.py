"""Test fetching data from last Friday"""

import requests
from utils.config_loader import config

token = config.get_secret('UPSTOX_ACCESS_TOKEN')

# Try Friday Nov 29, 2025
url = 'https://api.upstox.com/v2/historical-candle/NSE_INDEX|Nifty 50/1minute/2025-11-29/2025-11-28'

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json'
}

print(f"Fetching data from: {url}")
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    candles = data.get('data', {}).get('candles', [])
    print(f"Candles received: {len(candles)}")
    if candles:
        print(f"First candle: {candles[0]}")
        print(f"Last candle: {candles[-1]}")
else:
    print(f"Error: {response.text}")
