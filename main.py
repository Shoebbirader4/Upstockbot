#!/usr/bin/env python
"""Main trading bot entry point"""

import argparse
import time
from datetime import datetime, timedelta
import pandas as pd
from threading import Thread

from data_ingestion.data_fetcher import DataFetcher
from data_ingestion.data_storage import DataStorage
from data_ingestion.live_feed import LiveDataFeed
from signal_engine.signal_generator import SignalGenerator
from risk_manager.risk_engine import RiskEngine
from execution_engine.order_manager import OrderManager
from monitoring.alerting import AlertManager
from monitoring.dashboard import run_dashboard, update_state
from utils.config_loader import config
from utils.logger import log
from utils.time_utils import is_market_open, get_ist_now

class TradingBot:
    def __init__(self, model_path: str, mode: str = "paper"):
        self.mode = mode  # paper or live
        self.model_path = model_path
        
        # Initialize components
        self.signal_generator = SignalGenerator(model_path)
        self.risk_engine = RiskEngine()
        self.order_manager = OrderManager(broker=config.get('execution.broker', 'zerodha'))
        self.alert_manager = AlertManager()
        self.data_fetcher = DataFetcher(source=config.get('data.source', 'zerodha'))
        self.data_storage = DataStorage(
            storage_path=config.get('data.storage_path', './data'),
            storage_type=config.get('data.storage_type', 'parquet')
        )
        
        # Live data feed (WebSocket)
        self.live_feed = None
        self.use_websocket = config.get('data.use_websocket', True)
        
        # Trading state
        self.symbol = config.get('trading.asset', 'NIFTY_FUT')
        self.current_position = 0  # 0=flat, 1=long, -1=short
        self.entry_price = 0
        self.capital = config.get('backtesting.initial_capital', 1000000)
        self.running = False
        
        log.info(f"Trading bot initialized in {mode} mode")
    
    def start(self):
        """Start trading bot"""
        self.running = True
        log.info("Starting trading bot...")
        
        # Start live data feed if using WebSocket
        if self.use_websocket:
            log.info("Starting WebSocket live data feed...")
            self.live_feed = LiveDataFeed(instrument_key="NSE_INDEX|Nifty 50")
            self.live_feed.start()
            
            # Wait for data to be ready
            log.info("Waiting for live data to be ready...")
            while not self.live_feed.is_ready():
                time.sleep(5)
            log.info("Live data feed ready!")
        
        # Start dashboard in separate thread
        dashboard_thread = Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        
        self.alert_manager.send_alert("Trading bot started", "INFO")
        
        # Main trading loop
        while self.running:
            try:
                if is_market_open():
                    self.trading_cycle()
                else:
                    log.info("Market closed. Waiting...")
                    time.sleep(60)
                
                # Sleep between cycles
                time.sleep(180)  # 3 minutes
                
            except KeyboardInterrupt:
                log.info("Keyboard interrupt received")
                self.stop()
                break
            except Exception as e:
                log.error(f"Error in trading cycle: {e}")
                self.alert_manager.alert_error(str(e))
                time.sleep(60)
    
    def trading_cycle(self):
        """Execute one trading cycle"""
        
        # Get data (WebSocket or REST API)
        if self.use_websocket and self.live_feed:
            # Use live WebSocket data
            df = self.live_feed.get_latest_bars(n=200)
            
            if df.empty or len(df) < 50:
                log.warning("Insufficient live data for trading")
                return
            
            log.info(f"Using live WebSocket data: {len(df)} bars")
        else:
            # Fallback to REST API
            end_date = get_ist_now()
            start_date = end_date - timedelta(days=5)
            
            df = self.data_fetcher.fetch_historical(self.symbol, start_date, end_date)
            
            if df.empty or len(df) < 50:
                log.warning("Insufficient data for trading")
                return
            
            log.info(f"Using REST API data: {len(df)} bars")
        
        # Save data
        self.data_storage.save_ohlcv(df, self.symbol)
        
        # Generate signal
        signal_result = self.signal_generator.generate_signal(df)
        signal = signal_result['signal']
        confidence = signal_result['confidence']
        
        update_state('last_signal', signal_result)
        
        # Get current price and ATR
        if self.use_websocket and self.live_feed:
            current_price = self.live_feed.get_current_price()
        else:
            current_price = df['close'].iloc[-1]
        
        atr = df['ATR_14'].iloc[-1] if 'ATR_14' in df.columns else 50
        avg_atr = df['ATR_14'].mean() if 'ATR_14' in df.columns else 50
        
        # Check risk constraints
        can_trade, reason = self.risk_engine.can_trade(signal, current_price, atr, avg_atr)
        
        if not can_trade:
            log.info(f"Trade blocked: {reason}")
            return
        
        # Execute trade logic
        self.execute_trade_logic(signal, current_price, atr, confidence)
        
        # Update dashboard state
        update_state('current_position', self.current_position)
        update_state('daily_pnl', self.risk_engine.daily_pnl)
        update_state('daily_trades', self.risk_engine.daily_trades)
    
    def execute_trade_logic(self, signal: int, current_price: float, 
                           atr: float, confidence: float):
        """Execute trading logic based on signal"""
        
        # Minimum confidence threshold
        if confidence < 0.5:
            log.info(f"Confidence too low: {confidence:.2%}")
            return
        
        # Calculate position size
        position_size = self.risk_engine.calculate_position_size(self.capital, atr)
        
        # Trading logic
        if self.current_position == 0:  # Flat
            if signal == 2:  # Buy
                self.open_position('BUY', position_size, current_price)
            elif signal == 0:  # Sell
                self.open_position('SELL', position_size, current_price)
        
        elif self.current_position > 0:  # Long
            if signal == 0:  # Sell signal - close long
                self.close_position(current_price)
        
        elif self.current_position < 0:  # Short
            if signal == 2:  # Buy signal - close short
                self.close_position(current_price)
    
    def open_position(self, direction: str, quantity: int, price: float):
        """Open new position"""
        
        if self.mode == "paper":
            log.info(f"[PAPER] Opening {direction} position: {quantity} @ {price:.2f}")
            self.current_position = quantity if direction == 'BUY' else -quantity
            self.entry_price = price
        else:
            order = self.order_manager.place_order(self.symbol, direction, quantity, price)
            
            if order['status'] == 'EXECUTED':
                self.current_position = quantity if direction == 'BUY' else -quantity
                self.entry_price = order['execution_price']
                self.alert_manager.alert_trade_executed(order)
                update_state('orders', self.order_manager.get_executed_orders())
    
    def close_position(self, price: float):
        """Close current position"""
        
        if self.current_position == 0:
            return
        
        direction = 'SELL' if self.current_position > 0 else 'BUY'
        quantity = abs(self.current_position)
        
        # Calculate PnL
        if self.current_position > 0:
            pnl = (price - self.entry_price) * quantity
        else:
            pnl = (self.entry_price - price) * quantity
        
        if self.mode == "paper":
            log.info(f"[PAPER] Closing position: {direction} {quantity} @ {price:.2f}, PnL: {pnl:.2f}")
        else:
            order = self.order_manager.place_order(self.symbol, direction, quantity, price)
            
            if order['status'] == 'EXECUTED':
                self.alert_manager.alert_trade_executed(order)
                update_state('orders', self.order_manager.get_executed_orders())
        
        # Update risk engine
        self.risk_engine.record_trade(pnl)
        self.capital += pnl
        
        # Reset position
        self.current_position = 0
        self.entry_price = 0
        
        # Check if should flatten all
        should_flatten, reason = self.risk_engine.should_flatten_all()
        if should_flatten:
            log.warning(f"Flattening all positions: {reason}")
            self.alert_manager.alert_daily_loss_limit(self.risk_engine.daily_pnl)
    
    def stop(self):
        """Stop trading bot"""
        self.running = False
        
        # Close any open positions
        if self.current_position != 0:
            log.warning("Closing open position before shutdown")
            if self.mode == "live":
                self.order_manager.flatten_position(self.symbol, self.current_position)
        
        self.alert_manager.send_alert("Trading bot stopped", "INFO")
        log.info("Trading bot stopped")

def main():
    parser = argparse.ArgumentParser(description='Nifty Trading Bot')
    parser.add_argument('--config', type=str, default='config/config.yaml')
    parser.add_argument('--model', type=str, required=True, help='Path to trained model')
    parser.add_argument('--mode', type=str, default='paper', choices=['paper', 'live'])
    args = parser.parse_args()
    
    log.info("=" * 60)
    log.info("NIFTY INTRADAY TRADING BOT")
    log.info("=" * 60)
    log.info(f"Mode: {args.mode.upper()}")
    log.info(f"Model: {args.model}")
    log.info("=" * 60)
    
    bot = TradingBot(model_path=args.model, mode=args.mode)
    bot.start()

if __name__ == "__main__":
    main()
