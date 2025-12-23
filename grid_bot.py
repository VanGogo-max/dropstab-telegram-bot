"""
Grid Trading Bot - Automated Buy Low, Sell High
Exchange: KCEX (Spot Trading)
Strategy: Place buy/sell orders in grid pattern
Best for: Ranging/sideways markets
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass

from exchange_api import exchange_api
from risk_manager import risk_manager
from database import db_session, Trade, BotStatus
from email_service import email_service
from config import *

logger = logging.getLogger(__name__)


@dataclass
class GridLevel:
    """Single grid level"""
    price: float
    buy_order_id: Optional[str] = None
    sell_order_id: Optional[str] = None
    filled: bool = False


class GridBot:
    """Grid Trading Bot for ranging markets"""
    
    def __init__(self, user_id: int, symbol: str = 'BTC/USDT',
                 upper_price: float = 50000, lower_price: float = 40000,
                 grids: int = 10, amount_per_grid: float = 50):
        """
        Initialize Grid Bot
        
        Args:
            user_id: User ID
            symbol: Trading pair (e.g. BTC/USDT)
            upper_price: Upper price boundary
            lower_price: Lower price boundary
            grids: Number of grid levels (default: 10)
            amount_per_grid: USDT amount per grid level
        """
        self.user_id = user_id
        self.symbol = symbol
        self.exchange = exchange_api.get_spot_exchange()
        
        # Grid configuration
        self.upper_price = upper_price
        self.lower_price = lower_price
        self.grids = grids
        self.amount_per_grid = amount_per_grid
        
        # Calculate grid levels
        self.grid_levels: List[GridLevel] = []
        self._calculate_grid_levels()
        
        # Performance tracking
        self.total_profit = 0.0
        self.completed_cycles = 0
        
        logger.info(f"Grid Bot initialized: {symbol} "
                   f"[{lower_price}-{upper_price}] with {grids} grids")
    
    def _calculate_grid_levels(self):
        """Calculate all grid price levels"""
        if self.upper_price <= self.lower_price:
            raise ValueError("Upper price must be > lower price")
        
        if self.grids < 2:
            raise ValueError("Need at least 2 grids")
        
        # Calculate price step between grids
        price_range = self.upper_price - self.lower_price
        step = price_range / (self.grids - 1)
        
        # Create grid levels
        self.grid_levels = []
        for i in range(self.grids):
            price = self.lower_price + (step * i)
            self.grid_levels.append(GridLevel(price=round(price, 2)))
        
        logger.info(f"Grid levels: {[g.price for g in self.grid_levels]}")
    
    def get_current_price(self) -> float:
        """Get current market price"""
        try:
            ticker = self.exchange.get_ticker(self.symbol)
            price = float(ticker.get('last', 0))
            return price
        except Exception as e:
            logger.error(f"Price fetch error: {e}")
            return 0.0
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size in base currency"""
        # Amount in USDT / price = amount in BTC (or other base)
        size = self.amount_per_grid / price
        return round(size, 6)
    
    def place_grid_orders(self):
        """Place initial grid of buy/sell orders"""
        current_price = self.get_current_price()
        if current_price == 0:
            logger.error("Cannot place orders: invalid price")
            return
        
        logger.info(f"Placing grid orders around price: ${current_price:,.2f}")
        
        for level in self.grid_levels:
            # Place buy orders below current price
            if level.price < current_price:
                self._place_buy_order(level)
            
            # Place sell orders above current price
            elif level.price > current_price:
                self._place_sell_order(level)
        
        # Send notification
        email_service.send_bot_started(
            self.user_id,
            'grid',
            f"KCEX - {self.grids} grids placed"
        )
    
    def _place_buy_order(self, level: GridLevel) -> bool:
        """Place buy limit order at grid level"""
        try:
            size = self.calculate_position_size(level.price)
            
            # Risk check
            if not risk_manager.can_open_position(self.user_id):
                logger.warning("Risk limit reached - skipping buy order")
                return False
            
            # Place order
            result = self.exchange.create_order(
                symbol=self.symbol,
                side='buy',
                amount=size,
                order_type='limit',
                price=level.price
            )
            
            if 'error' not in result:
                level.buy_order_id = result.get('orderId')
                logger.info(f"Buy order placed: {size} @ ${level.price:,.2f}")
                return True
            else:
                logger.error(f"Buy order failed: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Place buy order error: {e}")
            return False
    
    def _place_sell_order(self, level: GridLevel) -> bool:
        """Place sell limit order at grid level"""
        try:
            size = self.calculate_position_size(level.price)
            
            # Place order
            result = self.exchange.create_order(
                symbol=self.symbol,
                side='sell',
                amount=size,
                order_type='limit',
                price=level.price
            )
            
            if 'error' not in result:
                level.sell_order_id = result.get('orderId')
                logger.info(f"Sell order placed: {size} @ ${level.price:,.2f}")
                return True
            else:
                logger.error(f"Sell order failed: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Place sell order error: {e}")
            return False
    
    def check_filled_orders(self):
        """Check which grid orders have been filled"""
        for level in self.grid_levels:
            # Check buy order
            if level.buy_order_id and not level.filled:
                if self._check_order_status(level.buy_order_id):
                    logger.info(f"Buy filled @ ${level.price:,.2f}")
                    self._handle_buy_filled(level)
            
            # Check sell order
            if level.sell_order_id and not level.filled:
                if self._check_order_status(level.sell_order_id):
                    logger.info(f"Sell filled @ ${level.price:,.2f}")
                    self._handle_sell_filled(level)
    
    def _check_order_status(self, order_id: str) -> bool:
        """Check if order is filled (mock for now)"""
        # TODO: Implement actual KCEX order status check
        # For now return False
        return False
    
    def _handle_buy_filled(self, level: GridLevel):
        """Handle buy order filled - place sell above"""
        level.filled = True
        
        # Find next level above to place sell
        current_idx = self.grid_levels.index(level)
        if current_idx < len(self.grid_levels) - 1:
            next_level = self.grid_levels[current_idx + 1]
            self._place_sell_order(next_level)
        
        # Log trade
        self._log_trade('BUY', level.price, 
                       self.calculate_position_size(level.price))
        
        # Calculate profit (grid step)
        if current_idx < len(self.grid_levels) - 1:
            profit = self.grid_levels[current_idx + 1].price - level.price
            self.total_profit += profit
    
    def _handle_sell_filled(self, level: GridLevel):
        """Handle sell order filled - place buy below"""
        level.filled = True
        
        # Find next level below to place buy
        current_idx = self.grid_levels.index(level)
        if current_idx > 0:
            prev_level = self.grid_levels[current_idx - 1]
            self._place_buy_order(prev_level)
        
        # Log trade
        self._log_trade('SELL', level.price,
                       self.calculate_position_size(level.price))
        
        # Increment completed cycles
        self.completed_cycles += 1
    
    def cancel_all_orders(self):
        """Cancel all open grid orders"""
        logger.info("Cancelling all grid orders...")
        
        for level in self.grid_levels:
            if level.buy_order_id:
                try:
                    # TODO: Implement actual KCEX cancel order
                    logger.info(f"Cancelled buy order: {level.buy_order_id}")
                except Exception as e:
                    logger.error(f"Cancel buy error: {e}")
            
            if level.sell_order_id:
                try:
                    # TODO: Implement actual KCEX cancel order
                    logger.info(f"Cancelled sell order: {level.sell_order_id}")
                except Exception as e:
                    logger.error(f"Cancel sell error: {e}")
    
    def get_statistics(self) -> Dict:
        """Get grid bot performance statistics"""
        active_orders = sum(
            1 for g in self.grid_levels 
            if g.buy_order_id or g.sell_order_id
        )
        
        filled_orders = sum(1 for g in self.grid_levels if g.filled)
        
        return {
            'total_grids': self.grids,
            'active_orders': active_orders,
            'filled_orders': filled_orders,
            'completed_cycles': self.completed_cycles,
            'total_profit': self.total_profit,
            'grid_range': f"${self.lower_price:,.0f} - ${self.upper_price:,.0f}"
        }
    
    def run(self):
        """Main bot execution loop"""
        try:
            # Check if grid needs initialization
            if not any(g.buy_order_id or g.sell_order_id 
                      for g in self.grid_levels):
                logger.info("Initializing grid...")
                self.place_grid_orders()
            
            # Check for filled orders and replace them
            self.check_filled_orders()
            
            # Log statistics
            stats = self.get_statistics()
            logger.info(f"Grid Stats: {stats}")
            
        except Exception as e:
            logger.error(f"Grid bot run error: {e}")
            
            # Send alert
            email_service.send_error_alert(
                self.user_id,
                "Grid Bot Error",
                str(e)
            )
    
    def _log_trade(self, action: str, price: float, amount: float):
        """Log trade to database"""
        try:
            # Calculate profit for this trade
            profit = 0
            if action == 'SELL':
                # Profit = (sell_price - buy_price) * amount
                # Simplified: assume buy was one grid below
                grid_step = (self.upper_price - self.lower_price) / (self.grids - 1)
                profit = grid_step * amount
            
            trade = Trade(
                user_id=self.user_id,
                bot_type='grid',
                symbol=self.symbol,
                action=action,
                price=price,
                amount=amount,
                timestamp=datetime.utcnow(),
                profit_loss=profit
            )
            db_session.add(trade)
            db_session.commit()
            
        except Exception as e:
            logger.error(f"Trade log error: {e}")
