# trailing_bot.py - Trailing Stop Loss Bot
import asyncio
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TrailingStopBot:
    """
    Protects profits with dynamic stop loss
    - Follows price up, locks in gains
    - Automatically sells when price drops by threshold
    - Conservative profit protection
    """
    
    def __init__(self, exchange_api, risk_manager, config: Dict):
        self.exchange = exchange_api
        self.risk = risk_manager
        self.config = config
        
        # Trailing settings
        self.symbol = config.get('symbol', 'BTC/USDT')
        self.trailing_percent = config.get('trailing_percent', 0.03)  # 3% trailing
        self.activation_profit = config.get('activation_profit', 0.05)  # Activate at 5% profit
        self.check_interval = config.get('check_interval', 60)  # Check every minute
        
        # State
        self.active = False
        self.position = None
        self.highest_price = 0
        self.trailing_stop_price = 0
        self.trades_history = []
    
    async def start(self, entry_price: float, amount: float):
        """Start trailing stop for a position"""
        self.position = {
            'symbol': self.symbol,
            'entry_price': entry_price,
            'amount': amount,
            'entry_time': datetime.now()
        }
        
        self.highest_price = entry_price
        self.trailing_stop_price = entry_price * (1 - self.trailing_percent)
        self.active = True
        
        logger.info(f"Trailing stop activated for {amount} {self.symbol} @ ${entry_price:.2f}")
        
        # Start monitoring loop
        asyncio.create_task(self._monitor_position())
    
    def stop(self):
        """Stop trailing bot"""
        self.active = False
        logger.info("Trailing Stop Bot stopped")
    
    async def _monitor_position(self):
        """Monitor position and update trailing stop"""
        while self.active and self.position:
            try:
                await self._check_price()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_price(self):
        """Check current price and update stop"""
        try:
            # Get current price
            ticker = await self.exchange.get_ticker(self.symbol)
            current_price = ticker['last']
            
            # Calculate current profit
            profit_percent = (current_price - self.position['entry_price']) / self.position['entry_price']
            
            # Update highest price
            if current_price > self.highest_price:
                self.highest_price = current_price
                
                # Only activate trailing after reaching profit target
                if profit_percent >= self.activation_profit:
                    # Update trailing stop
                    new_stop = current_price * (1 - self.trailing_percent)
                    if new_stop > self.trailing_stop_price:
                        self.trailing_stop_price = new_stop
                        logger.info(f"Trailing stop updated: ${self.trailing_stop_price:.2f} (Price: ${current_price:.2f}, Profit: {profit_percent:.2%})")
            
            # Check if stop hit
            if current_price <= self.trailing_stop_price and profit_percent >= self.activation_profit:
                logger.info(f"Trailing stop triggered at ${current_price:.2f}")
                await self._execute_stop_loss(current_price)
        
        except Exception as e:
            logger.error(f"Check price error: {e}")
    
    async def _execute_stop_loss(self, current_price: float):
        """Execute stop loss sell order"""
        try:
            # Create market sell order
            order = await self.exchange.create_order(
                symbol=self.symbol,
                side='sell',
                order_type='market',
                amount=self.position['amount']
            )
            
            if 'error' not in order:
                # Calculate profit
                entry_value = self.position['amount'] * self.position['entry_price']
                exit_value = self.position['amount'] * current_price
                profit = exit_value - entry_value
                profit_percent = profit / entry_value
                
                # Save trade
                trade_record = {
                    'symbol': self.symbol,
                    'entry_price': self.position['entry_price'],
                    'exit_price': current_price,
                    'highest_price': self.highest_price,
                    'amount': self.position['amount'],
                    'profit': profit,
                    'profit_percent': profit_percent,
                    'entry_time': self.position['entry_time'],
                    'exit_time': datetime.now(),
                    'exit_reason': 'trailing_stop'
                }
                
                self.trades_history.append(trade_record)
                
                logger.info(f"Position closed: Profit ${profit:.2f} ({profit_percent:.2%})")
                logger.info(f"Entry: ${self.position['entry_price']:.2f}, Exit: ${current_price:.2f}, Peak: ${self.highest_price:.2f}")
                
                # Update risk manager
                self.risk.update_pnl(profit)
                
                # Reset position
                self.position = None
                self.active = False
            else:
                logger.error(f"Stop loss order failed: {order['error']}")
        
        except Exception as e:
            logger.error(f"Execute stop loss error: {e}")
    
    def get_status(self) -> Dict:
        """Get current status"""
        if not self.position:
            return {
                'active': False,
                'position': None
            }
        
        current_profit = 0
        current_price = 0
        
        try:
            ticker = self.exchange.get_ticker(self.symbol)
            current_price = ticker['last']
            current_profit = (current_price - self.position['entry_price']) / self.position['entry_price']
        except:
            pass
        
        return {
            'active': self.active,
            'symbol': self.symbol,
            'entry_price': self.position['entry_price'],
            'current_price': current_price,
            'highest_price': self.highest_price,
            'trailing_stop': self.trailing_stop_price,
            'current_profit': current_profit,
            'amount': self.position['amount'],
            'distance_to_stop': (current_price - self.trailing_stop_price) / current_price if current_price > 0 else 0,
            'trailing_active': current_profit >= self.activation_profit
        }
    
    def get_performance(self) -> Dict:
        """Get performance statistics"""
        if not self.trades_history:
            return {
                'total_trades': 0,
                'total_profit': 0,
                'avg_profit': 0,
                'win_rate': 0
            }
        
        total_profit = sum(t['profit'] for t in self.trades_history)
        winning_trades = [t for t in self.trades_history if t['profit'] > 0]
        
        return {
            'total_trades': len(self.trades_history),
            'winning_trades': len(winning_trades),
            'total_profit': total_profit,
            'avg_profit': total_profit / len(self.trades_history),
            'avg_profit_percent': sum(t['profit_percent'] for t in self.trades_history) / len(self.trades_history),
            'win_rate': len(winning_trades) / len(self.trades_history),
            'best_trade': max(self.trades_history, key=lambda x: x['profit'])['profit'],
            'worst_trade': min(self.trades_history, key=lambda x: x['profit'])['profit']
        }
    
    def update_settings(self, trailing_percent: float = None, activation_profit: float = None):
        """Update trailing settings"""
        if trailing_percent:
            self.trailing_percent = trailing_percent
            logger.info(f"Trailing percent updated: {trailing_percent:.1%}")
        
        if activation_profit:
            self.activation_profit = activation_profit
            logger.info(f"Activation profit updated: {activation_profit:.1%}")

class MultiTrailingStopManager:
    """Manage multiple trailing stop positions"""
    
    def __init__(self, exchange_api, risk_manager):
        self.exchange = exchange_api
        self.risk = risk_manager
        self.positions: Dict[str, TrailingStopBot] = {}
    
    async def add_position(self, symbol: str, entry_price: float, 
                          amount: float, config: Dict = None):
        """Add new position to track"""
        if config is None:
            config = {'symbol': symbol}
        
        bot = TrailingStopBot(self.exchange, self.risk, config)
        await bot.start(entry_price, amount)
        
        self.positions[symbol] = bot
        logger.info(f"Added trailing stop for {symbol}")
    
    def remove_position(self, symbol: str):
        """Remove position"""
        if symbol in self.positions:
            self.positions[symbol].stop()
            del self.positions[symbol]
            logger.info(f"Removed trailing stop for {symbol}")
    
    def get_all_positions(self) -> Dict:
        """Get status of all positions"""
        return {
            symbol: bot.get_status() 
            for symbol, bot in self.positions.items()
        }
    
    def get_total_performance(self) -> Dict:
        """Get combined performance"""
        all_trades = []
        for bot in self.positions.values():
            all_trades.extend(bot.trades_history)
        
        if not all_trades:
            return {'total_profit': 0, 'total_trades': 0}
        
        total_profit = sum(t['profit'] for t in all_trades)
        winning = [t for t in all_trades if t['profit'] > 0]
        
        return {
            'total_trades': len(all_trades),
            'winning_trades': len(winning),
            'total_profit': total_profit,
            'win_rate': len(winning) / len(all_trades),
            'active_positions': len(self.positions)
        }
