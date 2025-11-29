#!/usr/bin/env python
"""Test Upstox historical data API"""

import requests
from datetime import datetime, timedelta
from utils.config_loader import config

access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

print("Testing Upstox Historical Data API\n")
print("="*70)

# Test with Nifty 50 Index (we know this works)
instrument_key = "NSE_INDEX|Nifty 50"
interval = "1minute"  # Upstox supports: 1minute, 30minute, day, week, month
to_date = datetime.now()
from_date = to_date - timedelta(days=5)

print(f"\nInstrument: {instrument_key}")
print(f"Interval: {interval}")
print(f"From: {from_date.strftime('%Y-%m-%d')}")
print(f"To: {to_date.strftime('%Y-%m-%d')}")

url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/{interval}/{to_date.strftime('%Y-%m-%d')}/{from_date.strftime('%Y-%m-%d')}"

print(f"\nURL: {url}\n")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response Status: {data.get('status')}")
        
        if data.get('status') == 'success' and 'data' in data:
            candles = data['data']['candles']
            print(f"\n✓ SUCCESS! Fetched {len(candles)} candles")
            
            print("\nFirst 3 candles:")
            for i, candle in enumerate(candles[:3], 1):
                print(f"  {i}. Time: {candle[0]}, O: {candle[1]}, H: {candle[2]}, L: {candle[3]}, C: {candle[4]}, V: {candle[5]}")
            
            print("\nLast 3 candles:")
            for i, candle in enumerate(candles[-3:], 1):
                print(f"  {i}. Time: {candle[0]}, O: {candle[1]}, H: {candle[2]}, L: {candle[3]}, C: {candle[4]}, V: {candle[5]}")
            
            print("\n" + "="*70)
            print("✓ Historical data API is working!")
            print("="*70)
            print("\nYou can use Nifty Index data for training:")
            print(f'  Instrument Key: "{instrument_key}"')
            print("\nOr find the correct Nifty Futures instrument key from Upstox platform")
        else:
            print(f"✗ No data: {data}")
    else:
        print(f"✗ Error: {response.text}")
        
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)
print("\nOption 1: Use Nifty Index for now (works!)")
print('  Update upstox_client.py: return "NSE_INDEX|Nifty 50"')
print("\nOption 2: Find Nifty Futures key manually")
print("  1. Login to Upstox web/app")
print("  2. Search for 'NIFTY FUT'")
print("  3. Check the instrument details")
print("  4. Use that instrument key")
