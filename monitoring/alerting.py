import os
from typing import Optional
from utils.logger import log
from utils.config_loader import config

class AlertManager:
    def __init__(self):
        self.telegram_enabled = config.get('monitoring.enable_telegram', False)
        self.email_enabled = config.get('monitoring.enable_email', False)
        
        if self.telegram_enabled:
            self.telegram_token = config.get_secret('TELEGRAM_BOT_TOKEN')
            self.telegram_chat_id = config.get_secret('TELEGRAM_CHAT_ID')
    
    def send_alert(self, message: str, level: str = "INFO"):
        """Send alert via configured channels"""
        
        formatted_message = f"[{level}] {message}"
        log.info(f"Alert: {formatted_message}")
        
        if self.telegram_enabled:
            self._send_telegram(formatted_message)
        
        if self.email_enabled:
            self._send_email(formatted_message, level)
    
    def _send_telegram(self, message: str):
        """Send Telegram alert"""
        try:
            import requests
            
            if not self.telegram_token or not self.telegram_chat_id:
                log.warning("Telegram credentials not configured")
                return
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=5)
            
            if response.status_code == 200:
                log.debug("Telegram alert sent successfully")
            else:
                log.error(f"Telegram alert failed: {response.text}")
                
        except Exception as e:
            log.error(f"Error sending Telegram alert: {e}")
    
    def _send_email(self, message: str, level: str):
        """Send email alert"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            smtp_host = config.get_secret('EMAIL_SMTP_HOST')
            smtp_port = int(config.get_secret('EMAIL_SMTP_PORT', '587'))
            from_email = config.get_secret('EMAIL_FROM')
            password = config.get_secret('EMAIL_PASSWORD')
            to_email = config.get_secret('EMAIL_TO')
            
            if not all([smtp_host, from_email, password, to_email]):
                log.warning("Email credentials not configured")
                return
            
            msg = MIMEText(message)
            msg['Subject'] = f"Trading Alert - {level}"
            msg['From'] = from_email
            msg['To'] = to_email
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(from_email, password)
                server.send_message(msg)
            
            log.debug("Email alert sent successfully")
            
        except Exception as e:
            log.error(f"Error sending email alert: {e}")
    
    def alert_trade_executed(self, order: dict):
        """Alert when trade is executed"""
        message = (f"🔔 Trade Executed\n"
                  f"Direction: {order['direction']}\n"
                  f"Quantity: {order['quantity']}\n"
                  f"Price: ₹{order.get('execution_price', 0):.2f}")
        self.send_alert(message, "INFO")
    
    def alert_daily_loss_limit(self, daily_pnl: float):
        """Alert when daily loss limit is reached"""
        message = f"⚠️ Daily Loss Limit Reached\nPnL: ₹{daily_pnl:.2f}"
        self.send_alert(message, "WARNING")
    
    def alert_error(self, error_message: str):
        """Alert on system error"""
        message = f"❌ System Error\n{error_message}"
        self.send_alert(message, "ERROR")
    
    def alert_daily_summary(self, metrics: dict):
        """Send daily summary"""
        message = (f"📊 Daily Summary\n"
                  f"Trades: {metrics.get('trades', 0)}\n"
                  f"PnL: ₹{metrics.get('pnl', 0):.2f}\n"
                  f"Win Rate: {metrics.get('win_rate', 0):.1%}")
        self.send_alert(message, "INFO")
