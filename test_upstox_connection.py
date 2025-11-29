#!/usr/bin/env python
"""Test Upstox API connection"""

from data_ingestion.upstox_client import UpstoxClient
from datetime import datetime, timedelta
from utils.logger import log

def test_connection():
    """Test Upstox API connection"""
    
    print("=" * 60)
    print("TESTING UPSTOX API CONNECTION")
    print("=" * 60)
    
    try:
        # Initialize client
        print("\n1. Initializing Upstox client...")
        client = UpstoxClient()
        
        # Test profile
        print("\n2. Testing profile access...")
        profile = client.get_profile()
        
        if profile:
            print(f"✓ Connected successfully!")
            print(f"  User: {profile.get('user_name', 'N/A')}")
            print(f"  Email: {profile.get('email', 'N/A')}")
            print(f"  User ID: {profile.get('user_id', 'N/A')}")
        else:
            print("✗ Failed to get profile")
            print("  Check your access token in config/secrets.env")
            return False
        
        # Test positions
        print("\n3. Testing positions access...")
        positions = client.get_positions()
        print(f"✓ Current positions: {len(positions)}")
        
        # Test historical data
        print("\n4. Testing historical data fetch...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        # Note: You need to update the instrument_key in upstox_client.py
        # with the actual Nifty Futures instrument key
        instrument_key = client.get_instrument_key("NIFTY")
        print(f"  Using instrument key: {instrument_key}")
        
        df = client.get_historical_data(
            instrument_key=instrument_key,
            interval='3minute',
            from_date=start_date,
            to_date=end_date
        )
        
        if not df.empty:
            print(f"✓ Fetched {len(df)} candles")
            print(f"\n  Sample data:")
            print(df.head())
            print(f"\n  Latest price: {df['close'].iloc[-1]:.2f}")
        else:
            print("✗ No data fetched")
            print("  This might be because:")
            print("  1. Instrument key is incorrect (update in upstox_client.py)")
            print("  2. Market is closed")
            print("  3. No data available for the date range")
        
        print("\n" + "=" * 60)
        print("CONNECTION TEST COMPLETE")
        print("=" * 60)
        
        if profile and not df.empty:
            print("\n✓ All tests passed! You're ready to use Upstox.")
            return True
        elif profile:
            print("\n⚠ Connection works but data fetch needs configuration.")
            print("  Update the instrument_key in data_ingestion/upstox_client.py")
            return True
        else:
            print("\n✗ Connection failed. Check your credentials.")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check config/secrets.env has correct credentials")
        print("2. Verify access token is valid (they expire)")
        print("3. Check internet connection")
        print("4. Verify Upstox API is accessible")
        return False

if __name__ == "__main__":
    import sys
    success = test_connection()
    sys.exit(0 if success else 1)
