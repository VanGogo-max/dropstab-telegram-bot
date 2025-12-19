# portfolio_bot.py - Portfolio Rebalancing Bot
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class PortfolioBot:
    """
    Conservative portfolio management
    - Maintains target allocation (e.g. 50% BTC, 30% ETH, 20% SOL)
    - Rebalances when deviation exceeds threshold
    - Protects against concentration risk
    """
    
    def __init__(self, exchange_api, risk_manager, config: Dict):
        self.exchange = exchange_api
        self.risk = risk_manager
        self.config = config
        
        # Portfolio configuration
        self.target_allocation = config.get('target_allocation', {
            'BTC/USDT': 0.50,  # 50%
            'ETH/USDT': 0.30,  # 30%
            'SOL/USDT': 0.20   # 20%
        })
        
        self.rebalance_threshold = config.get('rebalance_threshold', 0.05)  # 5% deviation
        self.rebalance_interval_hours = config.get('rebalance_interval', 24)  # Daily check
        self.min_trade_value = config.get('min_trade_value', 20)  # $20 minimum
        
        # State
        self.active = False
        self.last_rebalance = None
        self.current_allocation = {}
        self.rebalance_history = []
    
    async def start(self):
        """Start portfolio bot"""
        self.active = True
        logger.info("Portfolio Bot started")
        
        while self.active:
            try:
                await self._check_and_rebalance()
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Portfolio bot error: {e}")
                await asyncio.sleep(300)
    
    def stop(self):
        """Stop portfolio bot"""
        self.active = False
        logger.info("Portfolio Bot stopped")
    
    async def _check_and_rebalance(self):
        """Check if rebalancing needed"""
        # Check time since last rebalance
        if not self._should_rebalance():
            return
        
        # Get current portfolio
        portfolio = await self._get_current_portfolio()
        if not portfolio:
            logger.warning("Could not fetch portfolio")
            return
        
        # Calculate deviations
        deviations = self._calculate_deviations(portfolio)
        
        # Check if rebalance needed
        needs_rebalance = any(
            abs(dev) > self.rebalance_threshold 
            for dev in deviations.values()
        )
        
        if needs_rebalance:
            logger.info("Rebalancing needed")
            await self._execute_rebalance(portfolio, deviations)
        else:
            logger.info("Portfolio within target allocation")
    
    def _should_rebalance(self) -> bool:
        """Check if enough time passed since last rebalance"""
        if self.last_rebalance is None:
            return True
        
        time_since = datetime.now() - self.last_rebalance
        return time_since >= timedelta(hours=self.rebalance_interval_hours)
    
    async def _get_current_portfolio(self) -> Dict:
        """Get current portfolio value and allocation"""
        portfolio = {}
        total_value = 0
        
        try:
            for symbol in self.target_allocation.keys():
                # Get balance
                base_currency = symbol.split('/')[0]
                balance = await self.exchange.get_balance(base_currency)
                
                if balance['total'] == 0:
                    portfolio[symbol] = {'amount': 0, 'value': 0}
                    continue
                
                # Get current price
                ticker = await self.exchange.get_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate value
                value = balance['total'] * current_price
                total_value += value
                
                portfolio[symbol] = {
                    'amount': balance['total'],
                    'price': current_price,
                    'value': value
                }
            
            # Calculate current allocation percentages
            for symbol in portfolio:
                if total_value > 0:
                    portfolio[symbol]['allocation'] = portfolio[symbol]['value'] / total_value
                else:
                    portfolio[symbol]['allocation'] = 0
            
            portfolio['total_value'] = total_value
            return portfolio
        
        except Exception as e:
            logger.error(f"Get portfolio error: {e}")
            return {}
    
    def _calculate_deviations(self, portfolio: Dict) -> Dict:
        """Calculate deviation from target allocation"""
        deviations = {}
        
        for symbol, target_percent in self.target_allocation.items():
            current_percent = portfolio.get(symbol, {}).get('allocation', 0)
            deviation = current_percent - target_percent
            deviations[symbol] = deviation
            
            logger.info(f"{symbol}: Target {target_percent:.1%}, Current {current_percent:.1%}, Deviation {deviation:+.1%}")
        
        return deviations
    
    async def _execute_rebalance(self, portfolio: Dict, deviations: Dict):
        """Execute rebalancing trades"""
        total_value = portfolio['total_value']
        trades = []
        
        # Calculate required trades
        for symbol, deviation in deviations.items():
            if abs(deviation) < self.rebalance_threshold:
                continue
            
            target_value = total_value * self.target_allocation[symbol]
            current_value = portfolio[symbol]['value']
            value_diff = target_value - current_value
            
            # Skip small trades
            if abs(value_diff) < self.min_trade_value:
                continue
            
            if value_diff > 0:
                # Need to buy
                trades.append({
                    'symbol': symbol,
                    'side': 'buy',
                    'value': value_diff,
                    'reason': f'Underweight by {deviation:.1%}'
                })
            else:
                # Need to sell
                trades.append({
                    'symbol': symbol,
                    'side': 'sell',
                    'value': abs(value_diff),
                    'reason': f'Overweight by {deviation:.1%}'
                })
        
        # Execute trades
        executed_trades = []
        for trade in trades:
            success = await self._execute_trade(trade, portfolio)
            if success:
                executed_trades.append(trade)
        
        # Save rebalance record
        if executed_trades:
            self.rebalance_history.append({
                'timestamp': datetime.now(),
                'trades': executed_trades,
                'portfolio_before': portfolio,
                'deviations': deviations
            })
            
            self.last_rebalance = datetime.now()
            logger.info(f"Rebalancing completed: {len(executed_trades)} trades executed")
    
    async def _execute_trade(self, trade: Dict, portfolio: Dict) -> bool:
        """Execute single rebalancing trade"""
        symbol = trade['symbol']
        side = trade['side']
        value = trade['value']
        
        try:
            price = portfolio[symbol]['price']
            amount = value / price
            
            # Check risk limits
            balance = await self.exchange.get_balance('USDT')
            if not self.risk.check_daily_loss_limit(balance['total']):
                logger.warning("Risk limit reached, skipping trade")
                return False
            
            # Execute order
            order = await self.exchange.create_order(
                symbol=symbol,
                side=side,
                order_type='market',
                amount=amount
            )
            
            if 'error' not in order:
                logger.info(f"Rebalance trade: {side.upper()} {amount:.8f} {symbol} (${value:.2f})")
                return True
            else:
                logger.error(f"Trade failed: {order['error']}")
                return False
        
        except Exception as e:
            logger.error(f"Execute trade error: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get portfolio status"""
        return {
            'active': self.active,
            'target_allocation': self.target_allocation,
            'current_allocation': self.current_allocation,
            'last_rebalance': self.last_rebalance.isoformat() if self.last_rebalance else None,
            'rebalance_count': len(self.rebalance_history),
            'next_check_in_hours': self._time_until_next_check()
        }
    
    def _time_until_next_check(self) -> float:
        """Time until next rebalance check"""
        if self.last_rebalance is None:
            return 0
        
        next_check = self.last_rebalance + timedelta(hours=self.rebalance_interval_hours)
        time_left = next_check - datetime.now()
        return max(0, time_left.total_seconds() / 3600)
    
    async def get_portfolio_performance(self) -> Dict:
        """Get portfolio performance metrics"""
        portfolio = await self._get_current_portfolio()
        
        if not portfolio or len(self.rebalance_history) == 0:
            return {
                'total_value': portfolio.get('total_value', 0),
                'performance': 'N/A'
            }
        
        # Compare with first rebalance
        first_rebalance = self.rebalance_history[0]
        initial_value = first_rebalance['portfolio_before']['total_value']
        current_value = portfolio['total_value']
        
        performance = (current_value - initial_value) / initial_value if initial_value > 0 else 0
        
        return {
            'initial_value': initial_value,
            'current_value': current_value,
            'performance': performance,
            'performance_percent': performance * 100,
            'rebalances': len(self.rebalance_history),
            'allocation': {k: v['allocation'] for k, v in portfolio.items() if k != 'total_value'}
        }
    
    def set_target_allocation(self, new_allocation: Dict):
        """Update target allocation"""
        # Validate allocation sums to 1.0
        total = sum(new_allocation.values())
        if abs(total - 1.0) > 0.01:
            logger.error(f"Invalid allocation: total = {total}")
            return False
        
        self.target_allocation = new_allocation
        logger.info(f"Target allocation updated: {new_allocation}")
        return True
