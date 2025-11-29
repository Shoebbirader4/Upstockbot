#!/usr/bin/env python
"""Verify system setup"""

import sys
import os
from pathlib import Path

def check_files():
    """Check if required files exist"""
    print("Checking configuration files...")
    
    required_files = [
        'config/config.yaml',
        'config/secrets.env'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING!")
            all_exist = False
    
    return all_exist

def check_credentials():
    """Check if credentials are configured"""
    print("\nChecking Upstox credentials...")
    
    from dotenv import load_dotenv
    load_dotenv('config/secrets.env')
    
    api_key = os.getenv('UPSTOX_API_KEY')
    api_secret = os.getenv('UPSTOX_API_SECRET')
    access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
    
    if api_key and api_key != 'your_api_key_here':
        print(f"  ✓ UPSTOX_API_KEY configured")
    else:
        print(f"  ✗ UPSTOX_API_KEY not configured")
        return False
    
    if api_secret and api_secret != 'your_api_secret_here':
        print(f"  ✓ UPSTOX_API_SECRET configured")
    else:
        print(f"  ✗ UPSTOX_API_SECRET not configured")
        return False
    
    if access_token and access_token != 'your_access_token_here':
        print(f"  ✓ UPSTOX_ACCESS_TOKEN configured")
    else:
        print(f"  ✗ UPSTOX_ACCESS_TOKEN not configured")
        return False
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking Python packages...")
    
    required_packages = [
        'pandas',
        'numpy',
        'xgboost',
        'lightgbm',
        'sklearn',
        'fastapi',
        'requests'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED!")
            all_installed = False
    
    return all_installed

def main():
    print("=" * 60)
    print("SYSTEM SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    files_ok = check_files()
    creds_ok = check_credentials()
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if files_ok and creds_ok and deps_ok:
        print("\n✓ All checks passed! System is ready.")
        print("\nNext steps:")
        print("1. Test Upstox connection: python test_upstox_connection.py")
        print("2. Train model: python -m model_training.train --days 90")
        print("3. Run backtest: python -m backtester.run_backtest --model models/model_*.pkl")
        print("4. Start paper trading: python main.py --model models/model_*.pkl --mode paper")
        return True
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        
        if not files_ok:
            print("\nTo fix missing files:")
            print("  cp config/config.yaml.template config/config.yaml")
            print("  cp config/secrets.env.template config/secrets.env")
        
        if not creds_ok:
            print("\nTo fix credentials:")
            print("  Edit config/secrets.env and add your Upstox credentials")
        
        if not deps_ok:
            print("\nTo fix missing packages:")
            print("  pip install -r requirements.txt")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
