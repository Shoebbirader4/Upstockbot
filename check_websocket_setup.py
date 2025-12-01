#!/usr/bin/env python
"""Quick check if WebSocket setup is complete"""

import sys

def check_dependencies():
    """Check if all required packages are installed"""
    
    print("Checking WebSocket dependencies...")
    print("-" * 50)
    
    missing = []
    
    # Check websocket-client
    try:
        import websocket
        print("✓ websocket-client installed")
    except ImportError:
        print("✗ websocket-client NOT installed")
        missing.append("websocket-client")
    
    # Check other key dependencies
    deps = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'xgboost': 'xgboost',
    }
    
    for name, module in deps.items():
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            missing.append(name)
    
    print("-" * 50)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True

def check_files():
    """Check if all WebSocket files exist"""
    
    print("\nChecking WebSocket files...")
    print("-" * 50)
    
    import os
    
    files = [
        'data_ingestion/upstox_websocket.py',
        'data_ingestion/live_feed.py',
        'test_websocket_feed.py',
        'start_live_trading.py',
        'docs/WEBSOCKET_INTEGRATION.md',
        'WEBSOCKET_SETUP.md',
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} NOT FOUND")
            all_exist = False
    
    print("-" * 50)
    
    if all_exist:
        print("\n✅ All files present!")
        return True
    else:
        print("\n❌ Some files missing!")
        return False

def check_imports():
    """Check if WebSocket modules can be imported"""
    
    print("\nChecking WebSocket imports...")
    print("-" * 50)
    
    try:
        from data_ingestion.upstox_websocket import UpstoxWebSocket
        print("✓ UpstoxWebSocket imported")
    except Exception as e:
        print(f"✗ UpstoxWebSocket import failed: {e}")
        return False
    
    try:
        from data_ingestion.live_feed import LiveDataFeed
        print("✓ LiveDataFeed imported")
    except Exception as e:
        print(f"✗ LiveDataFeed import failed: {e}")
        return False
    
    print("-" * 50)
    print("\n✅ All imports successful!")
    return True

def main():
    """Run all checks"""
    
    print("\n" + "=" * 50)
    print("  WebSocket Setup Verification")
    print("=" * 50 + "\n")
    
    deps_ok = check_dependencies()
    files_ok = check_files()
    
    if not deps_ok:
        print("\n⚠️  Install dependencies first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    if not files_ok:
        print("\n⚠️  Some files are missing!")
        sys.exit(1)
    
    imports_ok = check_imports()
    
    if not imports_ok:
        print("\n⚠️  Import errors detected!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("  ✅ WebSocket Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Test WebSocket: python test_websocket_feed.py")
    print("  2. Start trading: python start_live_trading.py")
    print("\nDocumentation:")
    print("  • Quick Setup: WEBSOCKET_SETUP.md")
    print("  • Detailed Guide: docs/WEBSOCKET_INTEGRATION.md")
    print()

if __name__ == "__main__":
    main()
