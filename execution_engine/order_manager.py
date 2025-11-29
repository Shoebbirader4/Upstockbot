from typing import Dict, Optional
from datetime import datetime
import time
from utils.logger import log
from utils.config_loader import config

class OrderManager:
    def __init__(self, broker: str = "zerodha"):
        self.broker = broker
        self.retry_attempts = config.get('execution.retry_attempts', 3)
        self.retry_delay = config.get('execution.retry_delay_seconds', 2)
        self.order_type = config.get('execution.order_type', 'MARKET')
        self.product_type = config.get('execution.product_type', 'MIS')
        
        self.pending_orders = {}
        self.executed_orders = []
        self.order_id_counter = 1
    
    def place_order(self, symbol: str, direction: str, quantity: int, 
                   price: Optional[float] = None) -> Dict:
        """Place order with retry logic"""
        
        order_id = f"ORD_{self.order_id_counter:06d}"
        self.order_id_counter += 1
        
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'direction': direction,  # BUY or SELL
            'quantity': quantity,
            'order_type': self.order_type,
            'product_type': self.product_type,
            'price': price,
            'status': 'PENDING',
            'timestamp': datetime.now(),
            'attempts': 0
        }
        
        # Attempt to place order with retries
        for attempt in range(1, self.retry_attempts + 1):
            order['attempts'] = attempt
            
            try:
                result = self._execute_order(order)
                
                if result['success']:
                    order['status'] = 'EXECUTED'
                    order['execution_price'] = result.get('execution_price', price)
                    order['execution_time'] = datetime.now()
                    self.executed_orders.append(order)
                    
                    log.info(f"Order executed: {order_id} - {direction} {quantity} {symbol} "
                            f"@ {order['execution_price']:.2f}")
                    return order
                else:
                    log.warning(f"Order attempt {attempt} failed: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                log.error(f"Order execution error on attempt {attempt}: {e}")
            
            if attempt < self.retry_attempts:
                time.sleep(self.retry_delay)
        
        # All attempts failed
        order['status'] = 'FAILED'
        log.error(f"Order failed after {self.retry_attempts} attempts: {order_id}")
        
        return order
    
    def _execute_order(self, order: Dict) -> Dict:
        """Execute order via broker API"""
        
        # Placeholder - implement actual broker API integration
        if self.broker == "zerodha":
            return self._execute_zerodha_order(order)
        elif self.broker == "upstox":
            return self._execute_upstox_order(order)
        else:
            return {'success': False, 'error': 'Unsupported broker'}
    
    def _execute_zerodha_order(self, order: Dict) -> Dict:
        """Execute order via Zerodha Kite API"""
        # Placeholder - implement actual Kite API integration
        log.warning("Zerodha API not implemented - simulating order execution")
        
        # Simulate execution
        return {
            'success': True,
            'execution_price': order.get('price', 19500),
            'order_id': order['order_id']
        }
    
    def _execute_upstox_order(self, order: Dict) -> Dict:
        """Execute order via Upstox API"""
        try:
            from data_ingestion.upstox_client import UpstoxClient
            
            client = UpstoxClient()
            
            # Get instrument key
            instrument_key = client.get_instrument_key(order['symbol'])
            
            if not instrument_key:
                log.error("Could not get instrument key")
                return {'success': False, 'error': 'Invalid instrument'}
            
            # Place order
            result = client.place_order(
                instrument_key=instrument_key,
                quantity=order['quantity'],
                transaction_type=order['direction'],
                order_type=order['order_type'],
                product='I',  # Intraday
                price=order.get('price', 0)
            )
            
            if result['success']:
                # Get order details to get execution price
                order_status = client.get_order_status(result['order_id'])
                execution_price = order_status.get('average_price', order.get('price', 0))
                
                return {
                    'success': True,
                    'execution_price': execution_price,
                    'order_id': result['order_id']
                }
            else:
                return result
                
        except Exception as e:
            log.error(f"Upstox order execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order"""
        if order_id in self.pending_orders:
            order = self.pending_orders[order_id]
            order['status'] = 'CANCELLED'
            log.info(f"Order cancelled: {order_id}")
            return True
        
        log.warning(f"Order not found for cancellation: {order_id}")
        return False
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get status of an order"""
        for order in self.executed_orders:
            if order['order_id'] == order_id:
                return order
        
        if order_id in self.pending_orders:
            return self.pending_orders[order_id]
        
        return None
    
    def get_executed_orders(self) -> list:
        """Get all executed orders"""
        return self.executed_orders
    
    def flatten_position(self, symbol: str, current_position: int) -> Dict:
        """Flatten current position"""
        if current_position == 0:
            log.info("No position to flatten")
            return {'success': True, 'message': 'No position'}
        
        direction = 'SELL' if current_position > 0 else 'BUY'
        quantity = abs(current_position)
        
        log.warning(f"Flattening position: {direction} {quantity} {symbol}")
        return self.place_order(symbol, direction, quantity)
