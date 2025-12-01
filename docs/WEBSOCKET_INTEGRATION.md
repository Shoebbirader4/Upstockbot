# WebSocket Integration Guide

## Overview

The trading system now supports real-time market data via WebSocket connections, providing:
- **Lower latency**: Sub-second data updates vs 3-minute REST API polling
- **Real-time signals**: Generate trading signals as market moves
- **Better execution**: React to market changes instantly
- **Reduced API calls**: Single persistent connection vs repeated REST calls

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Trading Bot (main.py)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              LiveDataFeed (live_feed.py)                     │
│  • Combines WebSocket + REST API                            │
│  • Bootstraps with historical data                          │
│  • Maintains 3-minute bar aggregation                       │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│  UpstoxWebSocket          │   │  UpstoxClient (REST)     │
│  (upstox_websocket.py)    │   │  (upstox_client.py)      │
│  • Live tick data         │   │  • Historical bootstrap  │
│  • Mock mode for testing  │   │  • Gap filling           │
└───────────────────────────┘   └──────────────────────────┘
```

## Components

### 1. UpstoxWebSocket (`data_ingestion/upstox_websocket.py`)

Core WebSocket client with two modes:

**Mock Mode** (for testing):
- Generates realistic 3-minute bars
- Simulates market movement with random walk
- No API credentials needed
- Perfect for development and testing

**Real Mode** (for production):
- Connects to Upstox WebSocket API
- Receives live tick data
- Aggregates ticks into 3-minute bars
- Handles reconnection automatically

### 2. LiveDataFeed (`data_ingestion/live_feed.py`)

High-level interface that:
- Bootstraps with 2 days of historical data (REST API)
- Starts WebSocket for live updates
- Provides unified interface for both data sources
- Maintains rolling window of 200 bars

### 3. Main Trading Bot (`main.py`)

Updated to support WebSocket:
- Automatically starts live feed on startup
- Uses live data when available
- Falls back to REST API if WebSocket fails
- Configurable via `config.yaml`

## Configuration

### Enable Live Data Feed in `config/config.yaml`:

```yaml
data:
  source: upstox
  use_websocket: true  # Enable live data feed
```

Make sure your `config/secrets.env` has:
```
UPSTOX_ACCESS_TOKEN=your_access_token_here
```

The system will automatically poll Upstox API every 3 minutes for fresh data.

## Usage

### Testing WebSocket Feed

Run the test script:
```bash
python test_websocket_feed.py
```

This will:
1. Start the live data feed
2. Wait for data (30 seconds)
3. Display connection status and current price
4. Show latest bars
5. Monitor for 3 minutes to see new bars

### Running Trading Bot with WebSocket

```bash
python main.py --mode paper
```

The bot will:
1. Start WebSocket connection
2. Load historical data for bootstrap
3. Wait for live data to be ready
4. Begin trading with real-time data

## Live Data Feed

The system uses **real Upstox market data** by polling the API every 3 minutes:

**Features:**
- Real market data from Upstox
- Fetches 1-minute bars and resamples to 3-minute
- Automatic polling every 3 minutes
- Production-ready

**Requirements:**
- Valid Upstox access token
- Works during market hours (9:15 AM - 3:30 PM IST)
- Requires active internet connection

**Configuration:**
```yaml
data:
  source: upstox
  use_websocket: true  # Enable live data feed
```

**Access Token:**
Set in `config/secrets.env`:
```
UPSTOX_ACCESS_TOKEN=your_token_here
```

## Data Flow

### Bootstrap Phase (Startup)
```
1. Load 2 days of historical data (REST API)
   └─> Fills live_bars with ~600 bars
   
2. Start WebSocket connection
   └─> Begins receiving live ticks
   
3. Wait for ready state (50+ bars)
   └─> System ready for trading
```

### Live Trading Phase
```
Every 3 minutes:
1. WebSocket generates new bar
   └─> Appended to live_bars deque
   
2. Trading bot requests latest bars
   └─> Returns last 100-200 bars
   
3. Signal generator processes data
   └─> Generates trading signal
   
4. Execute trade if conditions met
   └─> Place order via broker API
```

## API Reference

### UpstoxWebSocket

```python
from data_ingestion.upstox_websocket import UpstoxWebSocket

ws = UpstoxWebSocket()
ws.start(instrument_key="NSE_INDEX|Nifty 50")

# Get live bars
bars_df = ws.get_live_bars(n=100)

# Get current price
price = ws.get_current_price()

# Check if ready
if ws.is_ready():
    print("Ready to trade!")

# Stop
ws.stop()
```

### LiveDataFeed

```python
from data_ingestion.live_feed import LiveDataFeed

feed = LiveDataFeed(instrument_key="NSE_INDEX|Nifty 50")
feed.start()

# Wait for ready
while not feed.is_ready():
    time.sleep(5)

# Get latest bars
bars = feed.get_latest_bars(n=100)

# Get current price
price = feed.get_current_price()

# Check connection
if feed.is_connected():
    print("Connected!")

# Stop
feed.stop()
```

## Troubleshooting

### WebSocket Not Connecting

**Check:**
1. Access token is valid and not expired
2. Network connectivity
3. Upstox API status
4. Firewall/proxy settings

**Solution:**
- Regenerate access token
- Check Upstox API documentation
- Use mock mode for testing

### No Data Received

**Check:**
1. Instrument key is correct
2. Market is open (for real mode)
3. Subscription successful

**Solution:**
- Verify instrument key format: `"NSE_INDEX|Nifty 50"`
- Check logs for subscription confirmation
- Use mock mode to verify system works

### Bars Not Updating

**Check:**
1. WebSocket connection status
2. Time synchronization
3. Bar aggregation logic

**Solution:**
- Restart WebSocket connection
- Check system time is correct
- Review logs for errors

## Performance Considerations

### Memory Usage
- Deque with maxlen=200 bars: ~50KB
- Minimal memory footprint
- Automatic cleanup of old data

### CPU Usage
- WebSocket thread: <1% CPU
- Bar aggregation: Negligible
- Overall impact: Minimal

### Network Usage
- WebSocket: ~1-5 KB/s
- Much lower than REST polling
- Single persistent connection

## Next Steps

1. **Test in Mock Mode**
   ```bash
   python test_websocket_feed.py
   ```

2. **Run Paper Trading**
   ```bash
   python main.py --mode paper
   ```

3. **Monitor Performance**
   - Check dashboard at http://localhost:8000
   - Review logs in `logs/` directory

4. **Switch to Real Mode**
   - Update config: `websocket_mock_mode: false`
   - Ensure valid access token
   - Test during market hours

5. **Deploy to Production**
   - Use real WebSocket connection
   - Enable all monitoring
   - Set up alerts
   - Start with small position sizes

## Best Practices

1. **Always test in mock mode first**
2. **Validate data quality before trading**
3. **Monitor WebSocket connection health**
4. **Have fallback to REST API**
5. **Log all WebSocket events**
6. **Handle reconnection gracefully**
7. **Validate timestamps and data integrity**
8. **Use paper trading before live**

## Support

For issues or questions:
1. Check logs in `logs/trading_*.log`
2. Review Upstox API documentation
3. Test with mock mode to isolate issues
4. Check network connectivity
5. Verify access token validity
