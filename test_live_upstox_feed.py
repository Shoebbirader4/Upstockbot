"""Test live Upstox data feed"""

import time
from datetime import datetime
from data_ingestion.upstox_websocket import UpstoxWebSocket
from utils.logger import log

def test_live_upstox_feed():
    """Test the live Upstox data feed"""
    
    log.info("=" * 60)
    log.info("Testing Live Upstox Data Feed")
    log.info("=" * 60)
    
    # Initialize feed
    feed = UpstoxWebSocket()
    
    # Start the feed
    log.info("\n1. Starting live data feed...")
    log.info("   This will fetch real market data from Upstox")
    log.info("   Polling every 3 minutes for fresh data")
    
    feed.start(instrument_key="NSE_INDEX|Nifty 50")
    
    # Wait for initial data
    log.info("\n2. Waiting for initial data (30 seconds)...")
    time.sleep(30)
    
    # Check connection status
    log.info(f"\n3. Connection Status: {'Connected' if feed.is_connected else 'Disconnected'}")
    
    # Check if ready
    log.info(f"4. Data Ready: {feed.is_ready()}")
    
    # Get current price
    current_price = feed.get_current_price()
    log.info(f"5. Current Price: {current_price:.2f}")
    
    # Get latest bars
    log.info("\n6. Getting latest 10 bars...")
    bars = feed.get_live_bars(n=10)
    
    if not bars.empty:
        log.info(f"\nTotal bars available: {len(bars)}")
        log.info("\nLatest 5 bars:")
        log.info(bars.tail(5).to_string())
        
        # Show statistics
        log.info(f"\nPrice Statistics:")
        log.info(f"  High: {bars['high'].max():.2f}")
        log.info(f"  Low: {bars['low'].min():.2f}")
        log.info(f"  Last Close: {bars['close'].iloc[-1]:.2f}")
        log.info(f"  Avg Volume: {bars['volume'].mean():.0f}")
        
        # Show time range
        log.info(f"\nTime Range:")
        log.info(f"  From: {bars['timestamp'].iloc[0]}")
        log.info(f"  To: {bars['timestamp'].iloc[-1]}")
    else:
        log.warning("No bars available yet")
        log.info("This might be because:")
        log.info("  1. Market is closed")
        log.info("  2. Access token is invalid")
        log.info("  3. Network connectivity issues")
    
    # Monitor for 3 minutes to see updates
    log.info("\n7. Monitoring for updates (3 minutes)...")
    log.info("Press Ctrl+C to stop early")
    
    try:
        for i in range(18):  # 18 * 10 seconds = 3 minutes
            time.sleep(10)
            
            current_price = feed.get_current_price()
            bars = feed.get_live_bars(n=5)
            
            if not bars.empty:
                latest_bar = bars.iloc[-1]
                log.info(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"Price: {current_price:.2f} | "
                    f"Bars: {len(bars)} | "
                    f"Latest: {latest_bar['timestamp']} - Close: {latest_bar['close']:.2f}"
                )
            else:
                log.info(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for data...")
    
    except KeyboardInterrupt:
        log.info("\nStopped by user")
    
    # Stop the feed
    log.info("\n8. Stopping live data feed...")
    feed.stop()
    
    log.info("\n" + "=" * 60)
    log.info("Test completed!")
    log.info("=" * 60)
    
    if not bars.empty:
        log.info("\n✅ SUCCESS: Live data feed is working!")
        log.info(f"   Received {len(bars)} bars of real market data")
    else:
        log.warning("\n⚠️  WARNING: No data received")
        log.warning("   Check:")
        log.warning("   1. Market hours (9:15 AM - 3:30 PM IST)")
        log.warning("   2. Access token in config/secrets.env")
        log.warning("   3. Network connectivity")

if __name__ == "__main__":
    test_live_upstox_feed()
