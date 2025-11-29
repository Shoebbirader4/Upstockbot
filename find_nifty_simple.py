#!/usr/bin/env python
"""Simple script to find Nifty Futures using Upstox API"""

import requests
from utils.config_loader import config

access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

print("Testing Nifty Futures instrument keys...\n")

# Try getting a quote for Nifty 50 index first
print("1. Getting Nifty 50 Index quote...")
try:
    url = "https://api.upstox.com/v2/market-quote/quotes?symbol=NSE_INDEX|Nifty 50"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            print("✓ Nifty Index accessible")
            for key, value in data['data'].items():
                print(f"  Current Nifty: {value.get('last_price', 'N/A')}")
except Exception as e:
    print(f"✗ Error: {e}")

# Try some common Nifty Futures symbols
print("\n2. Searching for Nifty Futures...")

# December 2024 and January 2025 contracts
test_symbols = [
    "NSE_FO:NIFTY24DECFUT",
    "NSE_FO:NIFTY25JANFUT",
    "NSE_FO:NIFTY25FEBFUT",
]

for symbol in test_symbols:
    try:
        url = f"https://api.upstox.com/v2/market-quote/quotes?symbol={symbol}"
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and data.get('data'):
                print(f"\n✓ FOUND: {symbol}")
                for key, value in data['data'].items():
                    print(f"  Instrument Key: {key}")
                    print(f"  Last Price: {value.get('last_price', 'N/A')}")
                    print(f"  Volume: {value.get('volume', 'N/A')}")
                    
                    # This is the one to use!
                    print(f"\n  👉 USE THIS: {key}")
                    break
        else:
            print(f"✗ Not found: {symbol}")
    except Exception as e:
        print(f"✗ Error with {symbol}: {e}")

print("\n" + "="*70)
print("INSTRUCTIONS:")
print("="*70)
print("\nIf you found an instrument key above:")
print("1. Copy the instrument key (e.g., NSE_FO|26000)")
print("2. Open: data_ingestion/upstox_client.py")
print("3. Find method: get_instrument_key()")
print("4. Replace the return value with your instrument key")
print("\nExample:")
print('  return "NSE_FO|26000"  # Replace with actual key')
