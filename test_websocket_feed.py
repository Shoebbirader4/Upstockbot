"""Test WebSocket live data feed"""

import time
from datetime import datetime
from data_ingestion.live_feed import LiveDataFeed
from utils.logger import log

def test_live_feed():
    """Test the live data feed with WebSocket"""
    
    log.info("=" * 60)
    log.info("Testing Live Data Feed (WebSocket)")
    log.info("=" * 60)
    
    # Initialize live feed
    feed = LiveDataFeed(instrument_key="NSE_INDEX|Nifty 50")
    
    # Start the feed
    log.info("\n1. Starting live data feed...")
    feed.start()
    
    # Wait for connection and data
    log.info("\n2. Waiting for data (30 seconds)...")
    time.sleep(30)
    
    # Check connection status
    log.info(f"\n3. Connection Status: {'Connected' if feed.is_connected() else 'Disconnected'}")
    
    # Check if ready
    log.info(f"4. Data Ready: {feed.is_ready()}")
    
    # Get current price
    current_price = feed.get_current_price()
    log.info(f"5. Current Price: {current_price:.2f}")
    
    # Get latest bars
    log.info("\n6. Getting latest 10 bars...")
    bars = feed.get_latest_bars(n=10)
    
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
    else:
        log.warning("No bars available yet")
    
    # Monitor for 3 minutes to see new bars
    log.info("\n7. Monitoring for new bars (3 minutes)...")
    log.info("Press Ctrl+C to stop early")
    
    try:
        for i in range(18):  # 18 * 10 seconds = 3 minutes
            time.sleep(10)
            
            current_price = feed.get_current_price()
            bars = feed.get_latest_bars(n=5)
            
            if not bars.empty:
                latest_bar = bars.iloc[-1]
                log.info(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"Price: {current_price:.2f} | "
                    f"Bars: {len(bars)} | "
                    f"Latest: {latest_bar['timestamp']} - Close: {latest_bar['close']:.2f}"
                )
    
    except KeyboardInterrupt:
        log.info("\nStopped by user")
    
    # Stop the feed
    log.info("\n8. Stopping live data feed...")
    feed.stop()
    
    log.info("\n" + "=" * 60)
    log.info("Test completed!")
    log.info("=" * 60)

if __name__ == "__main__":
    test_live_feed()
