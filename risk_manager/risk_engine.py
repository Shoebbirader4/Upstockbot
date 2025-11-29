from datetime import datetime, timedelta
from typing import Dict, Optional
from utils.logger import log
from utils.config_loader import config

class RiskEngine:
    def __init__(self):
        self.max_daily_loss = config.get('risk.max_daily_loss', 20000)
        self.max_trades_per_day = config.get('risk.max_trades_per_day', 20)
        self.max_position_size = config.get('risk.max_position_size', 2)
        self.volatility_spike_threshold = config.get('risk.volatility_spike_threshold', 3.0)
        self.cooldown_after_losses = config.get('risk.cooldown_after_losses', 3)
        self.cooldown_minutes = config.get('risk.cooldown_minutes', 30)
        
        self.daily_pnl = 0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.last_trade_time = None
        self.cooldown_until = None
        self.current_date = datetime.now().date()
    
    def reset_daily_counters(self):
        """Reset daily counters at start of new day"""
        today = datetime.now().date()
        if today != self.current_date:
            log.info(f"Resetting daily counters. Previous PnL: {self.daily_pnl:.2f}")
            self.daily_pnl = 0
            self.daily_trades = 0
            self.consecutive_losses = 0
            self.current_date = today
    
    def can_trade(self, signal: int, current_price: float, atr: float, 
                  avg_atr: float) -> tuple[bool, str]:
        """Check if trade is allowed based on risk rules"""
        
        self.reset_daily_counters()
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False, f"Daily loss limit reached: {self.daily_pnl:.2f}"
        
        # Check max trades per day
        if self.daily_trades >= self.max_trades_per_day:
            return False, f"Max trades per day reached: {self.daily_trades}"
        
        # Check cooldown period
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            remaining = (self.cooldown_until - datetime.now()).seconds // 60
            return False, f"In cooldown period. {remaining} minutes remaining"
        
        # Check volatility spike
        if atr > avg_atr * self.volatility_spike_threshold:
            return False, f"Volatility spike detected. ATR: {atr:.2f}, Avg: {avg_atr:.2f}"
        
        # Check if signal is actionable (not Hold)
        if signal == 1:  # Hold
            return False, "Signal is Hold"
        
        return True, "Trade allowed"
    
    def calculate_position_size(self, capital: float, atr: float, 
                               risk_per_trade: float = 0.02) -> int:
        """Calculate position size based on ATR and risk"""
        
        # Risk amount per trade
        risk_amount = capital * risk_per_trade
        
        # Position size based on ATR (stop loss = 2 * ATR)
        stop_loss_amount = 2 * atr
        position_size = int(risk_amount / stop_loss_amount)
        
        # Cap at max position size
        position_size = min(position_size, self.max_position_size)
        position_size = max(position_size, 1)  # At least 1 lot
        
        return position_size
    
    def record_trade(self, pnl: float):
        """Record trade result and update counters"""
        self.daily_pnl += pnl
        self.daily_trades += 1
        self.last_trade_time = datetime.now()
        
        if pnl < 0:
            self.consecutive_losses += 1
            log.warning(f"Loss recorded. Consecutive losses: {self.consecutive_losses}")
            
            # Trigger cooldown after consecutive losses
            if self.consecutive_losses >= self.cooldown_after_losses:
                self.cooldown_until = datetime.now() + timedelta(minutes=self.cooldown_minutes)
                log.warning(f"Cooldown triggered until {self.cooldown_until}")
        else:
            self.consecutive_losses = 0
        
        log.info(f"Trade recorded. Daily PnL: {self.daily_pnl:.2f}, "
                f"Daily Trades: {self.daily_trades}")
    
    def should_flatten_all(self) -> tuple[bool, str]:
        """Check if all positions should be flattened"""
        
        # Flatten if daily loss limit breached
        if self.daily_pnl <= -self.max_daily_loss:
            return True, "Daily loss limit breached"
        
        return False, ""
    
    def get_status(self) -> Dict:
        """Get current risk status"""
        return {
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'consecutive_losses': self.consecutive_losses,
            'in_cooldown': self.cooldown_until is not None and datetime.now() < self.cooldown_until,
            'cooldown_until': self.cooldown_until.isoformat() if self.cooldown_until else None,
            'max_daily_loss': self.max_daily_loss,
            'max_trades_per_day': self.max_trades_per_day
        }
