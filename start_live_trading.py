#!/usr/bin/env python
"""Quick start script for live trading with WebSocket"""

import sys
import time
from datetime import datetime
from utils.logger import log
from utils.config_loader import config

def check_prerequisites():
    """Check if system is ready for live trading"""
    
    log.info("=" * 60)
    log.info("Live Trading System - Pre-flight Check")
    log.info("=" * 60)
    
    checks_passed = True
    
    # Check 1: Model exists
    log.info("\n1. Checking for trained model...")
    try:
        import os
        model_path = config.get('model.registry_path', './models')
        model_files = [f for f in os.listdir(model_path) if f.endswith('.pkl')]
        
        if model_files:
            log.info(f"   ✓ Found {len(model_files)} model(s)")
            latest_model = sorted(model_files)[-1]
            log.info(f"   ✓ Latest: {latest_model}")
        else:
            log.error("   ✗ No trained models found!")
            log.error("   → Run: python train_improved_model.py")
            checks_passed = False
    except Exception as e:
        log.error(f"   ✗ Error checking models: {e}")
        checks_passed = False
    
    # Check 2: Configuration
    log.info("\n2. Checking configuration...")
    try:
        use_websocket = config.get('data.use_websocket', False)
        data_source = config.get('data.source', 'upstox')
        
        log.info(f"   • Data source: {data_source}")
        log.info(f"   • Live feed enabled: {use_websocket}")
        
        if use_websocket:
            log.info("   ✓ Live data feed configured")
        else:
            log.warning("   ! Live feed disabled (will use REST API only)")
    except Exception as e:
        log.error(f"   ✗ Configuration error: {e}")
        checks_passed = False
    
    # Check 3: Access token
    log.info("\n3. Checking API credentials...")
    try:
        access_token = config.get_secret('UPSTOX_ACCESS_TOKEN')
        if access_token and len(access_token) > 10:
            log.info("   ✓ Access token found")
        else:
            log.error("   ✗ Access token missing or invalid!")
            log.error("   → Set UPSTOX_ACCESS_TOKEN in config/secrets.env")
            log.error("   → Get token from Upstox API dashboard")
            checks_passed = False
    except Exception as e:
        log.error(f"   ✗ Credentials error: {e}")
        checks_passed = False
    
    # Check 4: Dependencies
    log.info("\n4. Checking dependencies...")
    try:
        import pandas
        import numpy
        import xgboost
        import websocket
        log.info("   ✓ All dependencies installed")
    except ImportError as e:
        log.error(f"   ✗ Missing dependency: {e}")
        log.error("   → Run: pip install -r requirements.txt")
        checks_passed = False
    
    return checks_passed

def start_trading():
    """Start the trading bot"""
    
    log.info("\n" + "=" * 60)
    log.info("Starting Live Trading System")
    log.info("=" * 60)
    
    # Import here to avoid issues if checks fail
    from main import TradingBot
    
    # Get latest model
    import os
    model_path = config.get('model.registry_path', './models')
    model_files = [f for f in os.listdir(model_path) if f.endswith('.pkl')]
    latest_model = os.path.join(model_path, sorted(model_files)[-1])
    
    log.info(f"\nUsing model: {latest_model}")
    log.info(f"Mode: Paper Trading")
    log.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create and start bot
    bot = TradingBot(model_path=latest_model, mode="paper")
    
    log.info("\n" + "=" * 60)
    log.info("System Starting...")
    log.info("=" * 60)
    log.info("\nPress Ctrl+C to stop\n")
    
    try:
        bot.start()
    except KeyboardInterrupt:
        log.info("\n\nShutting down gracefully...")
        bot.stop()
        log.info("System stopped.")
    except Exception as e:
        log.error(f"\nError: {e}")
        log.error("System stopped due to error.")
        sys.exit(1)

def main():
    """Main entry point"""
    
    print("\n" + "=" * 60)
    print("  NIFTY FUTURES TRADING BOT - LIVE MODE")
    print("=" * 60)
    
    # Run pre-flight checks
    if not check_prerequisites():
        log.error("\n" + "=" * 60)
        log.error("Pre-flight checks FAILED!")
        log.error("Please fix the issues above before starting.")
        log.error("=" * 60)
        sys.exit(1)
    
    log.info("\n" + "=" * 60)
    log.info("✓ All pre-flight checks PASSED!")
    log.info("=" * 60)
    
    # Ask for confirmation
    log.info("\nReady to start live trading (paper mode)")
    response = input("\nContinue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        start_trading()
    else:
        log.info("Cancelled by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
