import pandas as pd
import numpy as np
from typing import Dict, List
from utils.logger import log

class BacktestEngine:
    def __init__(self, initial_capital: float = 1000000,
                 transaction_cost_bps: float = 5,
                 slippage_bps: float = 2,
                 latency_ms: int = 100):
        self.initial_capital = initial_capital
        self.transaction_cost_bps = transaction_cost_bps
        self.slippage_bps = slippage_bps
        self.latency_ms = latency_ms
        
        self.capital = initial_capital
        self.position = 0  # 0=flat, 1=long, -1=short
        self.entry_price = 0
        self.trades = []
        self.equity_curve = []
    
    def run(self, df: pd.DataFrame, signals: np.ndarray, 
            atr_values: np.ndarray = None) -> Dict:
        """Run backtest simulation"""
        
        if len(df) != len(signals):
            log.error("Data and signals length mismatch")
            return {}
        
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            signal = signals[i]  # 0=Sell, 1=Hold, 2=Buy
            atr = atr_values[i] if atr_values is not None else row.get('ATR_14', 50)
            
            # Process signal
            self._process_signal(row, signal, atr)
            
            # Track equity
            current_equity = self._calculate_equity(row['close'])
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'equity': current_equity,
                'position': self.position
            })
        
        # Close any open position at end
        if self.position != 0:
            last_row = df.iloc[-1]
            self._close_position(last_row['close'], last_row['timestamp'], 'end_of_backtest')
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        return metrics
    
    def _process_signal(self, row, signal: int, atr: float):
        """Process trading signal"""
        price = row['close']
        timestamp = row['timestamp']
        
        # Apply slippage
        if signal == 2:  # Buy
            execution_price = price * (1 + self.slippage_bps / 10000)
        elif signal == 0:  # Sell
            execution_price = price * (1 - self.slippage_bps / 10000)
        else:
            execution_price = price
        
        # Current position logic
        if self.position == 0:  # Flat
            if signal == 2:  # Buy signal
                self._open_position(execution_price, timestamp, 'long', atr)
            elif signal == 0:  # Sell signal
                self._open_position(execution_price, timestamp, 'short', atr)
        
        elif self.position == 1:  # Long
            if signal == 0:  # Sell signal - close long
                self._close_position(execution_price, timestamp, 'signal')
            else:
                # Check stop loss and target
                self._check_exit_conditions(price, timestamp, atr)
        
        elif self.position == -1:  # Short
            if signal == 2:  # Buy signal - close short
                self._close_position(execution_price, timestamp, 'signal')
            else:
                # Check stop loss and target
                self._check_exit_conditions(price, timestamp, atr)
    
    def _open_position(self, price: float, timestamp, direction: str, atr: float):
        """Open a new position"""
        self.position = 1 if direction == 'long' else -1
        self.entry_price = price
        
        # Calculate stop loss and target based on ATR
        if direction == 'long':
            self.stop_loss = price - (2.0 * atr)
            self.target = price + (3.0 * atr)
        else:
            self.stop_loss = price + (2.0 * atr)
            self.target = price - (3.0 * atr)
        
        log.debug(f"Opened {direction} at {price:.2f}, SL: {self.stop_loss:.2f}, Target: {self.target:.2f}")
    
    def _close_position(self, price: float, timestamp, reason: str):
        """Close current position"""
        if self.position == 0:
            return
        
        # Calculate PnL
        if self.position == 1:  # Long
            pnl = price - self.entry_price
        else:  # Short
            pnl = self.entry_price - price
        
        # Apply transaction costs
        transaction_cost = (self.entry_price + price) * (self.transaction_cost_bps / 10000)
        net_pnl = pnl - transaction_cost
        
        # Update capital
        self.capital += net_pnl
        
        # Record trade
        self.trades.append({
            'entry_time': timestamp,
            'exit_time': timestamp,
            'direction': 'long' if self.position == 1 else 'short',
            'entry_price': self.entry_price,
            'exit_price': price,
            'gross_pnl': pnl,
            'net_pnl': net_pnl,
            'reason': reason
        })
        
        log.debug(f"Closed {self.position} at {price:.2f}, PnL: {net_pnl:.2f}, Reason: {reason}")
        
        # Reset position
        self.position = 0
        self.entry_price = 0
    
    def _check_exit_conditions(self, price: float, timestamp, atr: float):
        """Check stop loss and target conditions"""
        if self.position == 1:  # Long
            if price <= self.stop_loss:
                self._close_position(price, timestamp, 'stop_loss')
            elif price >= self.target:
                self._close_position(price, timestamp, 'target')
        
        elif self.position == -1:  # Short
            if price >= self.stop_loss:
                self._close_position(price, timestamp, 'stop_loss')
            elif price <= self.target:
                self._close_position(price, timestamp, 'target')
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate current equity"""
        if self.position == 0:
            return self.capital
        
        # Calculate unrealized PnL
        if self.position == 1:
            unrealized_pnl = current_price - self.entry_price
        else:
            unrealized_pnl = self.entry_price - current_price
        
        return self.capital + unrealized_pnl
    
    def _calculate_metrics(self) -> Dict:
        """Calculate backtest performance metrics"""
        if not self.trades:
            log.warning("No trades executed")
            return {}
        
        trades_df = pd.DataFrame(self.trades)
        equity_df = pd.DataFrame(self.equity_curve)
        
        # PnL metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['net_pnl'] > 0])
        losing_trades = len(trades_df[trades_df['net_pnl'] < 0])
        
        gross_pnl = trades_df['gross_pnl'].sum()
        net_pnl = trades_df['net_pnl'].sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Average win/loss
        avg_win = trades_df[trades_df['net_pnl'] > 0]['net_pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['net_pnl'] < 0]['net_pnl'].mean() if losing_trades > 0 else 0
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 else 0
        
        # Drawdown
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = equity_df['equity'] - equity_df['peak']
        max_drawdown = equity_df['drawdown'].min()
        max_drawdown_pct = (max_drawdown / self.initial_capital) * 100
        
        # Returns
        total_return = ((equity_df['equity'].iloc[-1] - self.initial_capital) / 
                       self.initial_capital) * 100
        
        # Calculate daily returns for Sharpe/Sortino
        equity_df['returns'] = equity_df['equity'].pct_change()
        daily_returns = equity_df['returns'].dropna()
        
        # Sharpe Ratio (assuming 252 trading days, 6% risk-free rate)
        risk_free_rate = 0.06 / 252
        excess_returns = daily_returns - risk_free_rate
        sharpe_ratio = (excess_returns.mean() / excess_returns.std() * np.sqrt(252)) if excess_returns.std() > 0 else 0
        
        # Sortino Ratio (only downside deviation)
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = downside_returns.std()
        sortino_ratio = (excess_returns.mean() / downside_std * np.sqrt(252)) if downside_std > 0 else 0
        
        # Calmar Ratio (return / max drawdown)
        calmar_ratio = abs(total_return / max_drawdown_pct) if max_drawdown_pct != 0 else 0
        
        # Recovery Factor
        recovery_factor = abs(net_pnl / max_drawdown) if max_drawdown != 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'gross_pnl': gross_pnl,
            'net_pnl': net_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'total_return_pct': total_return,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'recovery_factor': recovery_factor,
            'final_capital': equity_df['equity'].iloc[-1],
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        log.info(f"Backtest Results - Trades: {total_trades}, Win Rate: {win_rate:.2%}, "
                f"Net PnL: {net_pnl:.2f}, Sharpe: {sharpe_ratio:.2f}, "
                f"Sortino: {sortino_ratio:.2f}, Calmar: {calmar_ratio:.2f}")
        
        return metrics
