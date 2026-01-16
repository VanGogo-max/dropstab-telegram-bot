"""
Base Strategy with Partial Take Profit
All trading strategies inherit from this class
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)


class PartialTakeProfitMixin:
    """
    Mixin for Partial Take Profit functionality
    Implements TP1, TP2, TP3 with configurable profiles
    """
    
    def __init__(self, tp_profile: str = 'conservative'):
        """
        Initialize Partial TP
        
        Args:
            tp_profile: 'conservative', 'balanced', or 'aggressive'
        """
        self.tp_profile_name = tp_profile
        self.tp_profile = config.get_tp_profile(tp_profile)
        
        # TP levels configuration
        self.tp_levels = [
            {
                'name': 'TP1',
                'ratio': self.tp_profile['tp1']['ratio'],
                'percentage': self.tp_profile['tp1']['percentage'],
                'multiplier': config.TP1_MULTIPLIER,
                'filled': False,
                'price': None
            },
            {
                'name': 'TP2',
                'ratio': self.tp_profile['tp2']['ratio'],
                'percentage': self.tp_profile['tp2']['percentage'],
                'multiplier': config.TP2_MULTIPLIER,
                'filled': False,
                'price': None
            },
            {
                'name': 'TP3',
                'ratio': self.tp_profile['tp3']['ratio'],
                'percentage': self.tp_profile['tp3']['percentage'],
                'multiplier': config.TP3_MULTIPLIER,
                'filled': False,
                'price': None,
                'trailing': config.TP3_TRAILING_STOP
            }
        ]
        
        # Tracking
        self.position_opened = False
        self.position_quantity = 0
        self.remaining_quantity = 0
        self.entry_price = 0
        self.stop_loss_price = 0
        self.side = None  # 'buy' or 'sell'
        
        # TP3 trailing stop tracking
        self.tp3_highest_price = 0
        self.tp3_trailing_active = False
        
        logger.info(f"Partial TP initialized: {tp_profile} profile")
        logger.info(f"TP1: {self.tp_levels[0]['percentage']}% | "
                   f"TP2: {self.tp_levels[1]['percentage']}% | "
                   f"TP3: {self.tp_levels[2]['percentage']}%")
    
    def calculate_tp_prices(
        self,
        entry_price: float,
        stop_loss_price: float,
        side: str
    ) -> List[Dict]:
        """
        Calculate TP prices based on risk/reward
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            side: 'buy' or 'sell'
        
        Returns:
            List of TP levels with prices
        """
        try:
            risk = abs(entry_price - stop_loss_price)
            
            for level in self.tp_levels:
                reward = risk * level['multiplier']
                
                if side == 'buy':
                    level['price'] = entry_price + reward
                else:  # sell
                    level['price'] = entry_price - reward
            
            logger.info(f"TP Prices calculated for {side} position:")
            for level in self.tp_levels:
                logger.info(f"  {level['name']}: ${level['price']:.2f} "
                          f"({level['percentage']}% of position)")
            
            return self.tp_levels
            
        except Exception as e:
            logger.error(f"TP calculation error: {e}")
            return []
    
    def open_position_with_partial_tp(
        self,
        entry_price: float,
        stop_loss_price: float,
        total_quantity: float,
        side: str,
        symbol: str
    ) -> Dict:
        """
        Open position and set partial TP orders
        
        Returns:
            Dictionary with position and TP orders details
        """
        try:
            self.position_opened = True
            self.entry_price = entry_price
            self.stop_loss_price = stop_loss_price
            self.position_quantity = total_quantity
            self.remaining_quantity = total_quantity
            self.side = side
            
            # Calculate TP prices
            self.calculate_tp_prices(entry_price, stop_loss_price, side)
            
            # Prepare TP orders
            tp_orders = []
            
            for level in self.tp_levels:
                tp_quantity = total_quantity * level['ratio']
                
                tp_orders.append({
                    'name': level['name'],
                    'price': level['price'],
                    'quantity': tp_quantity,
                    'percentage': level['percentage'],
                    'status': 'pending'
                })
            
            position_info = {
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'stop_loss': stop_loss_price,
                'total_quantity': total_quantity,
                'tp_orders': tp_orders,
                'tp_profile': self.tp_profile_name
            }
            
            logger.info(f"Position opened with Partial TP:")
            logger.info(f"  Entry: ${entry_price:.2f} | SL: ${stop_loss_price:.2f}")
            logger.info(f"  Quantity: {total_quantity:.4f} {symbol}")
            logger.info(f"  TP Profile: {self.tp_profile_name}")
            
            return position_info
            
        except Exception as e:
            logger.error(f"Open position error: {e}")
            return {}
    
    def check_and_execute_tp(
        self,
        current_price: float,
        execute_order_callback: callable
    ) -> Optional[Dict]:
        """
        Check if any TP level is hit and execute
        
        Args:
            current_price: Current market price
            execute_order_callback: Function to execute order(symbol, side, quantity, price)
        
        Returns:
            Info about executed TP level or None
        """
        if not self.position_opened:
            return None
        
        try:
            for level in self.tp_levels:
                if level['filled']:
                    continue
                
                # Check if TP hit
                tp_hit = False
                
                if self.side == 'buy':
                    tp_hit = current_price >= level['price']
                else:  # sell
                    tp_hit = current_price <= level['price']
                
                if tp_hit:
                    # Execute TP order
                    tp_quantity = self.position_quantity * level['ratio']
                    close_side = 'sell' if self.side == 'buy' else 'buy'
                    
                    # Call the exchange order execution
                    order_result = execute_order_callback(
                        side=close_side,
                        quantity=tp_quantity,
                        price=current_price
                    )
                    
                    if order_result:
                        # Mark as filled
                        level['filled'] = True
                        self.remaining_quantity -= tp_quantity
                        
                        # Calculate profit for this TP
                        if self.side == 'buy':
                            profit = (current_price - self.entry_price) * tp_quantity
                        else:
                            profit = (self.entry_price - current_price) * tp_quantity
                        
                        tp_info = {
                            'level': level['name'],
                            'price': current_price,
                            'quantity': tp_quantity,
                            'profit': profit,
                            'remaining_quantity': self.remaining_quantity,
                            'percentage_closed': level['percentage']
                        }
                        
                        logger.info(f"✅ {level['name']} HIT!")
                        logger.info(f"  Closed: {level['percentage']}% at ${current_price:.2f}")
                        logger.info(f"  Profit: ${profit:.2f}")
                        logger.info(f"  Remaining: {self.remaining_quantity:.4f}")
                        
                        # Activate trailing stop for TP3
                        if level['name'] == 'TP3' and level.get('trailing'):
                            self.tp3_trailing_active = True
                            self.tp3_highest_price = current_price
                            logger.info(f"🎯 TP3 Trailing Stop activated")
                        
                        return tp_info
            
            # Check TP3 trailing stop
            if self.tp3_trailing_active:
                return self._check_tp3_trailing(current_price, execute_order_callback)
            
            return None
            
        except Exception as e:
            logger.error(f"TP check error: {e}")
            return None
    
    def _check_tp3_trailing(
        self,
        current_price: float,
        execute_order_callback: callable
    ) -> Optional[Dict]:
        """Check and execute TP3 trailing stop"""
        try:
            # Update highest price
            if self.side == 'buy':
                if current_price > self.tp3_highest_price:
                    self.tp3_highest_price = current_price
                
                # Check if trailing stop hit
                trailing_stop = self.tp3_highest_price * (1 - config.TP3_TRAILING_PERCENT / 100)
                
                if current_price <= trailing_stop:
                    # Close remaining position
                    return self._close_remaining_position(
                        current_price,
                        execute_order_callback,
                        reason="TP3 Trailing Stop"
                    )
            
            else:  # sell
                if current_price < self.tp3_highest_price:
                    self.tp3_highest_price = current_price
                
                trailing_stop = self.tp3_highest_price * (1 + config.TP3_TRAILING_PERCENT / 100)
                
                if current_price >= trailing_stop:
                    return self._close_remaining_position(
                        current_price,
                        execute_order_callback,
                        reason="TP3 Trailing Stop"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"TP3 trailing check error: {e}")
            return None
    
    def _close_remaining_position(
        self,
        current_price: float,
        execute_order_callback: callable,
        reason: str = "Manual Close"
    ) -> Dict:
        """Close all remaining position"""
        try:
            if self.remaining_quantity <= 0:
                return {}
            
            close_side = 'sell' if self.side == 'buy' else 'buy'
            
            order_result = execute_order_callback(
                side=close_side,
                quantity=self.remaining_quantity,
                price=current_price
            )
            
            if order_result:
                # Calculate final profit
                if self.side == 'buy':
                    profit = (current_price - self.entry_price) * self.remaining_quantity
                else:
                    profit = (self.entry_price - current_price) * self.remaining_quantity
                
                result = {
                    'reason': reason,
                    'price': current_price,
                    'quantity': self.remaining_quantity,
                    'profit': profit
                }
                
                # Reset position
                self.position_opened = False
                self.remaining_quantity = 0
                self.tp3_trailing_active = False
                
                logger.info(f"🏁 Position fully closed: {reason}")
                logger.info(f"  Price: ${current_price:.2f}")
                logger.info(f"  Final Profit: ${profit:.2f}")
                
                return result
            
            return {}
            
        except Exception as e:
            logger.error(f"Close remaining error: {e}")
            return {}
    
    def check_stop_loss(
        self,
        current_price: float,
        execute_order_callback: callable
    ) -> Optional[Dict]:
        """Check if stop loss is hit"""
        if not self.position_opened:
            return None
        
        try:
            sl_hit = False
            
            if self.side == 'buy':
                sl_hit = current_price <= self.stop_loss_price
            else:  # sell
                sl_hit = current_price >= self.stop_loss_price
            
            if sl_hit:
                return self._close_remaining_position(
                    current_price,
                    execute_order_callback,
                    reason="Stop Loss"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Stop loss check error: {e}")
            return None
    
    def get_position_status(self) -> Dict:
        """Get current position status"""
        if not self.position_opened:
            return {'status': 'no_position'}
        
        tp_status = []
        for level in self.tp_levels:
            tp_status.append({
                'level': level['name'],
                'price': level['price'],
                'percentage': level['percentage'],
                'filled': level['filled']
            })
        
        return {
            'status': 'open',
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss_price,
            'total_quantity': self.position_quantity,
            'remaining_quantity': self.remaining_quantity,
            'side': self.side,
            'tp_levels': tp_status,
            'tp3_trailing_active': self.tp3_trailing_active,
            'tp3_highest_price': self.tp3_highest_price if self.tp3_trailing_active else None
        }


class BaseStrategy(PartialTakeProfitMixin):
    """
    Base Strategy Class
    All bot strategies inherit from this
    """
    
    def __init__(
        self,
        user_id: int,
        symbol: str,
        tp_profile: str = 'conservative'
    ):
        """
        Initialize base strategy
        
        Args:
            user_id: User ID
            symbol: Trading pair (e.g., 'BTC/USDT')
            tp_profile: 'conservative', 'balanced', or 'aggressive'
        """
        super().__init__(tp_profile)
        
        self.user_id = user_id
        self.symbol = symbol
        self.running = False
        
        logger.info(f"Base Strategy initialized for user {user_id}")
        logger.info(f"Symbol: {symbol} | TP Profile: {tp_profile}")
    
    def start(self):
        """Start strategy"""
        self.running = True
        logger.info(f"Strategy started for {self.symbol}")
    
    def stop(self):
        """Stop strategy"""
        self.running = False
        logger.info(f"Strategy stopped for {self.symbol}")
    
    def run(self):
        """
        Main strategy logic - OVERRIDE THIS
        This is called periodically by BotManager
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    def execute_order(self, side: str, quantity: float, price: float = None) -> Dict:
        """
        Execute order on exchange - OVERRIDE THIS
        
        Args:
            side: 'buy' or 'sell'
            quantity: Order quantity
            price: Order price (None for market order)
        
        Returns:
            Order result dictionary
        """
        raise NotImplementedError("Subclasses must implement execute_order()")
