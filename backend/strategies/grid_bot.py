"""
Grid Bot with Partial Take Profit
Example implementation showing how to use BaseStrategy
"""

import logging
from typing import Dict, List
from base_strategy import BaseStrategy
from config import config

logger = logging.getLogger(__name__)


class GridBot(BaseStrategy):
    """
    Grid Trading Bot with Partial TP
    
    Features:
    - Places buy/sell orders in grid
    - Each grid position uses Partial TP (TP1, TP2, TP3)
    - Adjustable TP profile (conservative/balanced/aggressive)
    """
    
    def __init__(
        self,
        user_id: int,
        symbol: str,
        upper_price: float,
        lower_price: float,
        grids: int,
        amount_per_grid: float,
        tp_profile: str = 'conservative'
    ):
        """
        Initialize Grid Bot
        
        Args:
            user_id: User ID
            symbol: Trading pair
            upper_price: Upper grid price
            lower_price: Lower grid price
            grids: Number of grid levels
            amount_per_grid: Amount per grid (USD)
            tp_profile: 'conservative', 'balanced', or 'aggressive'
        """
        super().__init__(user_id, symbol, tp_profile)
        
        self.upper_price = upper_price
        self.lower_price = lower_price
        self.grids = grids
        self.amount_per_grid = amount_per_grid
        
        # Calculate grid levels
        self.grid_levels = self._calculate_grid_levels()
        
        # Track grid orders
        self.grid_orders = []
        self.active_positions = {}  # grid_level -> position_info
        
        logger.info(f"Grid Bot initialized:")
        logger.info(f"  Range: ${lower_price:.2f} - ${upper_price:.2f}")
        logger.info(f"  Grids: {grids}")
        logger.info(f"  Amount per grid: ${amount_per_grid}")
        logger.info(f"  TP Profile: {tp_profile}")
    
    def _calculate_grid_levels(self) -> List[float]:
        """Calculate grid price levels"""
        step = (self.upper_price - self.lower_price) / (self.grids + 1)
        levels = []
        
        for i in range(self.grids):
            price = self.lower_price + (step * (i + 1))
            levels.append(round(price, 2))
        
        logger.info(f"Grid levels: {levels}")
        return levels
    
    def run(self):
        """Main grid bot logic with Partial TP"""
        try:
            if not self.running:
                return
            
            # Get current price
            current_price = self._get_current_price()
            
            logger.info(f"Grid Bot tick: {self.symbol} @ ${current_price:.2f}")
            
            # 1. Check existing positions for TP/SL
            self._check_existing_positions(current_price)
            
            # 2. Place new grid orders if needed
            self._place_grid_orders(current_price)
            
        except Exception as e:
            logger.error(f"Grid bot run error: {e}")
    
    def _check_existing_positions(self, current_price: float):
        """Check all active positions for TP/SL hits"""
        for grid_level, position_data in list(self.active_positions.items()):
            try:
                # Check Take Profit
                tp_result = self.check_and_execute_tp(
                    current_price=current_price,
                    execute_order_callback=lambda **kwargs: self.execute_order(**kwargs)
                )
                
                if tp_result:
                    logger.info(f"Grid {grid_level} - TP executed: {tp_result}")
                    
                    # If position fully closed, remove from active
                    if self.remaining_quantity == 0:
                        del self.active_positions[grid_level]
                        logger.info(f"Grid {grid_level} - Position fully closed")
                
                # Check Stop Loss
                sl_result = self.check_stop_loss(
                    current_price=current_price,
                    execute_order_callback=lambda **kwargs: self.execute_order(**kwargs)
                )
                
                if sl_result:
                    logger.warning(f"Grid {grid_level} - Stop Loss hit: {sl_result}")
                    del self.active_positions[grid_level]
                    
            except Exception as e:
                logger.error(f"Position check error for grid {grid_level}: {e}")
    
    def _place_grid_orders(self, current_price: float):
        """Place grid orders at appropriate levels"""
        try:
            for grid_price in self.grid_levels:
                # Skip if already have position at this level
                if grid_price in self.active_positions:
                    continue
                
                # Buy if current price is near grid level (within 0.5%)
                price_diff_percent = abs(current_price - grid_price) / grid_price
                
                if price_diff_percent < 0.005:  # Within 0.5%
                    self._open_grid_position(grid_price, current_price)
                    
        except Exception as e:
            logger.error(f"Place grid orders error: {e}")
    
    def _open_grid_position(self, grid_price: float, current_price: float):
        """Open a new grid position with Partial TP"""
        try:
            # Calculate position size
            quantity = self.amount_per_grid / current_price
            
            # Calculate stop loss (2% below entry)
            stop_loss = current_price * 0.98
            
            # Open position with Partial TP
            position_info = self.open_position_with_partial_tp(
                entry_price=current_price,
                stop_loss_price=stop_loss,
                total_quantity=quantity,
                side='buy',
                symbol=self.symbol
            )
            
            if position_info:
                # Store position
                self.active_positions[grid_price] = position_info
                
                # Execute buy order
                order_result = self.execute_order(
                    side='buy',
                    quantity=quantity,
                    price=current_price
                )
                
                logger.info(f"✅ Grid position opened at ${current_price:.2f}")
                logger.info(f"   Quantity: {quantity:.4f}")
                logger.info(f"   TP1: ${position_info['tp_orders'][0]['price']:.2f} ({self.tp_levels[0]['percentage']}%)")
                logger.info(f"   TP2: ${position_info['tp_orders'][1]['price']:.2f} ({self.tp_levels[1]['percentage']}%)")
                logger.info(f"   TP3: ${position_info['tp_orders'][2]['price']:.2f} ({self.tp_levels[2]['percentage']}%)")
                
        except Exception as e:
            logger.error(f"Open grid position error: {e}")
    
    def execute_order(self, side: str, quantity: float, price: float = None) -> Dict:
        """
        Execute order on exchange
        TODO: Implement real exchange integration
        """
        logger.info(f"[MOCK ORDER] {side.upper()} {quantity:.4f} {self.symbol} @ ${price:.2f}")
        
        # Mock successful order
        return {
            'success': True,
            'order_id': f'mock_{side}_{int(time.time())}',
            'side': side,
            'quantity': quantity,
            'price': price,
            'symbol': self.symbol
        }
    
    def _get_current_price(self) -> float:
        """
        Get current market price
        TODO: Implement real exchange API
        """
        import random
        # Mock price within grid range
        return random.uniform(self.lower_price, self.upper_price)
    
    def get_statistics(self) -> Dict:
        """Get bot statistics"""
        return {
            'symbol': self.symbol,
            'upper_price': self.upper_price,
            'lower_price': self.lower_price,
            'total_grids': self.grids,
            'active_positions': len(self.active_positions),
            'tp_profile': self.tp_profile_name,
            'grid_levels': self.grid_levels
        }


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    import logging
    import time
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Grid Bot with Partial Take Profit - Test")
    print("=" * 60)
    
    # Create grid bot with conservative TP profile
    bot = GridBot(
        user_id=1,
        symbol='BTC/USDT',
        upper_price=32000,
        lower_price=28000,
        grids=10,
        amount_per_grid=50,
        tp_profile='conservative'  # 62% / 31% / 8%
    )
    
    print(f"\nBot configured:")
    print(f"  TP Profile: Conservative")
    print(f"  TP1: 62% of position")
    print(f"  TP2: 31% of position")
    print(f"  TP3: 8% of position (with trailing stop)")
    
    # Start bot
    bot.start()
    
    print("\nSimulating 5 bot cycles...")
    print("-" * 60)
    
    # Run a few cycles
    for i in range(5):
        print(f"\n[Cycle {i+1}]")
        bot.run()
        time.sleep(2)
    
    # Stop bot
    bot.stop()
    
    # Print statistics
    stats = bot.get_statistics()
    print("\n" + "=" * 60)
    print("Bot Statistics:")
    print("-" * 60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
