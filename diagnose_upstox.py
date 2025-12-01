"""Diagnose Upstox API connection issues"""

import requests
from utils.config_loader import config
from utils.logger import log

def diagnose_upstox():
    """Run comprehensive diagnostics"""
    
    print("=" * 60)
    print("UPSTOX API DIAGNOSTICS")
    print("=" * 60)
    
    # Get credentials
    api_key = config.get_secret('UPSTOX_API_KEY')
    access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')
    
    print(f"\n1. Credentials Check:")
    print(f"   API Key: {api_key[:10]}..." if api_key else "   API Key: NOT SET")
    print(f"   Access Token: {access_token[:20]}..." if access_token else "   Access Token: NOT SET")
    
    if not access_token:
        print("\n❌ Access token not configured!")
        print("   Set UPSTOX_ACCESS_TOKEN in config/secrets.env")
        return
    
    # Test 1: Profile endpoint
    print(f"\n2. Testing Profile Endpoint:")
    url = "https://api.upstox.com/v2/user/profile"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("   ✅ Profile access successful!")
            data = response.json()
            if 'data' in data:
                print(f"   User: {data['data'].get('user_name', 'N/A')}")
        elif response.status_code == 401:
            print("   ❌ Unauthorized - Token may be invalid or expired")
            print("   Generate new token from: https://api.upstox.com/")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Historical data endpoint
    print(f"\n3. Testing Historical Data Endpoint:")
    instrument_key = "NSE_INDEX|Nifty 50"
    from datetime import datetime, timedelta
    
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/1minute/{to_date}/{from_date}"
    
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'candles' in data['data']:
                candles = data['data']['candles']
                print(f"   ✅ Received {len(candles)} candles")
                if candles:
                    print(f"   Latest candle: {candles[0]}")
            else:
                print(f"   ⚠️  No candles in response: {data}")
        elif response.status_code == 401:
            print("   ❌ Unauthorized - Token may be invalid")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Check token expiry
    print(f"\n4. Token Expiry Check:")
    try:
        import base64
        import json
        
        payload = json.loads(base64.urlsafe_b64decode(access_token.split('.')[1] + '==').decode())
        exp_timestamp = payload.get('exp', 0)
        
        from datetime import datetime
        exp_time = datetime.fromtimestamp(exp_timestamp)
        now = datetime.now()
        
        print(f"   Issued: {datetime.fromtimestamp(payload.get('iat', 0))}")
        print(f"   Expires: {exp_time}")
        print(f"   Current: {now}")
        
        if now > exp_time:
            print(f"   ❌ Token EXPIRED!")
        else:
            time_left = exp_time - now
            print(f"   ✅ Token valid for {time_left}")
    except Exception as e:
        print(f"   ⚠️  Could not decode token: {e}")
    
    # Test 4: Network connectivity
    print(f"\n5. Network Connectivity:")
    try:
        response = requests.get("https://api.upstox.com", timeout=5)
        print(f"   ✅ Can reach api.upstox.com (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Cannot reach api.upstox.com: {e}")
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    print("\n📋 Summary:")
    print("   If you see 401 Unauthorized:")
    print("   1. Generate new access token from https://api.upstox.com/")
    print("   2. Update config/secrets.env with new token")
    print("   3. Restart the trading bot")
    print("\n   If you see network errors:")
    print("   1. Check internet connection")
    print("   2. Check firewall settings")
    print("   3. Try from different network")

if __name__ == "__main__":
    diagnose_upstox()
