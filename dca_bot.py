# dca_bot.py - Dollar Cost Averaging Bot
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DCABot:
    """
    Conservative DCA strategy
    - Buys fixed amount at regular intervals
    - Reduces risk of bad entry timing
    - Accumulates position over time
    """
    
    def __init__(self, exchange_api, risk_manager, config: Dict):
        self.exchange = exchange_api
        self.risk = risk_manager
        self.config = config
        
        # DCA settings
        self.symbol = config.get('symbol', 'BTC/USDT')
        self.interval_hours = config.get('interval_hours', 24)  # Daily
        self.amount_per_order = config.get('amount_per_order', 50)  # $50
        self.max_total_investment = config.get('max_total_investment', 1000)  # $1000 max
        self.take_profit_percent = config.get('take_profit_percent', 0.15)  # 15% profit
        
        # State
        self.total_invested = 0
        self.total_coins = 0
        self.average_entry = 0
        self.last_buy_time = None
        self.active = False
        self.orders_history = []
    
    async def start(self):
        """Start DCA bot"""
        self.active = True
        logger.info(f"DCA Bot started for {self.symbol}")
        
        while self.active:
            try:
                await self._execute_dca_cycle()
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"DCA cycle error: {e}")
                await asyncio.sleep(300)  # Wait 5 min on error
    
    def stop(self):
        """Stop DCA bot"""
        self.active = False
        logger.info("DCA Bot stopped")
    
    async def _execute_dca_cycle(self):
        """Execute one DCA cycle"""
        # Check if it's time to buy
        if not self._should_buy():
            return
        
        # Check risk limits
        balance = await self.exchange.get_balance('USDT')
        if not self.risk.check_daily_loss_limit(balance['total']):
            logger.warning("Daily loss limit reached, skipping DCA")
            return
        
        # Check investment limit
        if self.total_invested >= self.max_total_investment:
            logger.info(f"Max investment reached: ${self.total_invested}")
            await self._check_take_profit()
            return
        
        # Execute buy order
        await self._execute_buy()
        
        # Check take profit
        await self._check_take_profit()
    
    def _should_buy(self) -> bool:
        """Check if it's time to buy"""
        if self.last_buy_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_buy_time
        return time_since_last >= timedelta(hours=self.interval_hours)
    
    async def _execute_buy(self):
        """Execute DCA buy order"""
        try:
            # Get current price
            ticker = await self.exchange.get_ticker(self.symbol)
            current_price = ticker['last']
            
            # Calculate amount to buy
            amount_to_invest = min(
                self.amount_per_order,
                self.max_total_investment - self.total_invested
            )
            
            coins_to_buy = amount_to_invest / current_price
            
            # Create market buy order
            order = await self.exchange.create_order(
                symbol=self.symbol,
                side='buy',
                order_type='market',
                amount=coins_to_buy
            )
            
            if 'error' not in order:
                # Update state
                self.total_invested += amount_to_invest
                self.total_coins += coins_to_buy
                self.average_entry = self.total_invested / self.total_coins
                self.last_buy_time = datetime.now()
                
                # Save order
                self.orders_history.append({
                    'type': 'buy',
                    'price': current_price,
                    'amount': coins_to_buy,
                    'cost': amount_to_invest,
                    'timestamp': datetime.now()
                })
                
                logger.info(f"DCA Buy executed: {coins_to_buy:.8f} {self.symbol.split('/')[0]} @ ${current_price:.2f}")
                logger.info(f"Total invested: ${self.total_invested:.2f}, Avg entry: ${self.average_entry:.2f}")
            else:
                logger.error(f"Buy order failed: {order['error']}")
        
        except Exception as e:
            logger.error(f"Execute buy error: {e}")
    
    async def _check_take_profit(self):
        """Check if take profit target reached"""
        if self.total_coins == 0:
            return
        
        try:
            ticker = await self.exchange.get_ticker(self.symbol)
            current_price = ticker['last']
            
            # Calculate profit
            current_value = self.total_coins * current_price
            profit_percent = (current_value - self.total_invested) / self.total_invested
            
            if profit_percent >= self.take_profit_percent:
                logger.info(f"Take profit target reached: {profit_percent:.2%}")
                await self._execute_sell()
        
        except Exception as e:
            logger.error(f"Check take profit error: {e}")
    
    async def _execute_sell(self):
        """Execute sell all position"""
        try:
            ticker = await self.exchange.get_ticker(self.symbol)
            current_price = ticker['last']
            
            # Create market sell order
            order = await self.exchange.create_order(
                symbol=self.symbol,
                side='sell',
                order_type='market',
                amount=self.total_coins
            )
            
            if 'error' not in order:
                # Calculate profit
                sell_value = self.total_coins * current_price
                profit = sell_value - self.total_invested
                profit_percent = profit / self.total_invested
                
                # Save order
                self.orders_history.append({
                    'type': 'sell',
                    'price': current_price,
                    'amount': self.total_coins,
                    'revenue': sell_value,
                    'profit': profit,
                    'profit_percent': profit_percent,
                    'timestamp': datetime.now()
                })
                
                logger.info(f"DCA Sell executed: {self.total_coins:.8f} @ ${current_price:.2f}")
                logger.info(f"Profit: ${profit:.2f} ({profit_percent:.2%})")
                
                # Update risk manager
                self.risk.update_pnl(profit)
                
                # Reset state
                self._reset_state()
            else:
                logger.error(f"Sell order failed: {order['error']}")
        
        except Exception as e:
            logger.error(f"Execute sell error: {e}")
    
    def _reset_state(self):
        """Reset bot state after sell"""
        self.total_invested = 0
        self.total_coins = 0
        self.average_entry = 0
        self.last_buy_time = None
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        current_value = 0
        unrealized_pnl = 0
        
        if self.total_coins > 0:
            try:
                ticker = self.exchange.get_ticker(self.symbol)
                current_price = ticker['last']
                current_value = self.total_coins * current_price
                unrealized_pnl = current_value - self.total_invested
            except:
                pass
        
        return {
            'active': self.active,
            'symbol': self.symbol,
            'total_invested': self.total_invested,
            'total_coins': self.total_coins,
            'average_entry': self.average_entry,
            'current_value': current_value,
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_percent': unrealized_pnl / self.total_invested if self.total_invested > 0 else 0,
            'orders_count': len(self.orders_history),
            'last_buy': self.last_buy_time.isoformat() if self.last_buy_time else None,
            'next_buy_in_hours': self._time_until_next_buy()
        }
    
    def _time_until_next_buy(self) -> float:
        """Calculate time until next buy"""
        if self.last_buy_time is None:
            return 0
        
        next_buy = self.last_buy_time + timedelta(hours=self.interval_hours)
        time_left = next_buy - datetime.now()
        return max(0, time_left.total_seconds() / 3600)
    
    def get_performance(self) -> Dict:
        """Get performance statistics"""
        buy_orders = [o for o in self.orders_history if o['type'] == 'buy']
        sell_orders = [o for o in self.orders_history if o['type'] == 'sell']
        
        total_profit = sum(o['profit'] for o in sell_orders)
        winning_trades = len([o for o in sell_orders if o['profit'] > 0])
        
        return {
            'total_orders': len(self.orders_history),
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
            'total_profit': total_profit,
            'winning_trades': winning_trades,
            'win_rate': winning_trades / len(sell_orders) if sell_orders else 0,
            'average_profit': total_profit / len(sell_orders) if sell_orders else 0
        }
