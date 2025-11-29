#!/usr/bin/env python
"""Find Nifty Futures instrument key from Upstox"""

import requests
from datetime import datetime
from utils.config_loader import config

def get_nifty_futures_instrument():
    """Get current month Nifty Futures instrument key"""
    
    access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    print("Fetching instrument list from Upstox...")
    print("This may take a moment...\n")
    
    try:
        # Get instruments using Upstox API v2
        # We'll search for Nifty using market quotes
        
        # First, let's try some known Nifty Futures instrument keys
        # Format: NSE_FO|<instrument_token>
        
        # Let's search by getting market data for Nifty index first
        print("Searching for Nifty Futures contracts...")
        
        # Try to get instrument details via search
        # Common Nifty Futures patterns
        test_symbols = [
            "NIFTY24DECFUT",
            "NIFTY24JANFUT", 
            "NIFTY25JANFUT",
            "NIFTY25FEBFUT",
            "NIFTY25MARFUT"
        ]
        
        found_instruments = []
        
        for symbol in test_symbols:
            try:
                # Try to get quote for this symbol
                quote_url = f"https://api.upstox.com/v2/market-quote/quotes?symbol=NSE_FO:{symbol}"
                quote_response = requests.get(quote_url, headers=headers, timeout=10)
                
                if quote_response.status_code == 200:
                    data = quote_response.json()
                    if data.get('status') == 'success' and data.get('data'):
                        for key, value in data['data'].items():
                            found_instruments.append({
                                'instrument_key': key,
                                'trading_symbol': symbol,
                                'last_price': value.get('last_price', 'N/A')
                            })
                            print(f"✓ Found: {symbol} -> {key}")
            except:
                pass
        
        if not found_instruments:
            print("\n⚠️  Could not auto-detect instrument keys.")
            print("\nManual method:")
            print("1. Go to Upstox web/app")
            print("2. Search for 'NIFTY FUT'")
            print("3. Find current month contract")
            print("4. Note the trading symbol (e.g., NIFTY25JANFUT)")
            print("\nOr use this placeholder for testing:")
            placeholder_key = "NSE_FO|26000"  # Common format
            print(f"   Instrument Key: {placeholder_key}")
            return placeholder_key
        
        # Return the first found instrument
        response = type('obj', (object,), {'text': ''})()  # Dummy response
        response.raise_for_status()
        
        nifty_futures = found_instruments
        
        print("=" * 70)
        print("NIFTY FUTURES CONTRACTS FOUND:")
        print("=" * 70)
        
        for i, fut in enumerate(nifty_futures[:5], 1):
            print(f"\n{i}. Trading Symbol: {fut['trading_symbol']}")
            print(f"   Instrument Key: {fut['instrument_key']}")
            print(f"   Expiry: {fut['expiry']}")
            
            if i == 1:
                print("   👉 CURRENT MONTH (Use this one)")
        
        print("\n" + "=" * 70)
        
        # Return current month contract
        current_month = nifty_futures[0]
        
        print(f"\n✅ Current Month Nifty Futures:")
        print(f"   Instrument Key: {current_month['instrument_key']}")
        print(f"   Trading Symbol: {current_month['trading_symbol']}")
        print(f"   Expiry: {current_month['expiry']}")
        
        print(f"\n📝 Update this in data_ingestion/upstox_client.py:")
        print(f"   Line ~60: return \"{current_month['instrument_key']}\"")
        
        return current_month['instrument_key']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching instruments: {e}")
        return None
    except Exception as e:
        print(f"❌ Error parsing instruments: {e}")
        return None

if __name__ == "__main__":
    instrument_key = get_nifty_futures_instrument()
    
    if instrument_key:
        print("\n" + "=" * 70)
        print("NEXT STEP:")
        print("=" * 70)
        print("\nCopy the instrument key above and update:")
        print("  File: data_ingestion/upstox_client.py")
        print("  Method: get_instrument_key()")
        print(f"  Replace: return \"NSE_FO|43650\"")
        print(f"  With: return \"{instrument_key}\"")
