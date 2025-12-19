# arbitrage_bot.py - Cross-Exchange Arbitrage Bot
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ArbitrageBot:
    """
    Conservative arbitrage trading
    - Finds price differences between exchanges
    - Executes low-risk arbitrage opportunities
    - Accounts for fees and slippage
    """
    
    def __init__(self, exchanges: Dict, risk_manager, config: Dict):
        self.exchanges = exchanges  # Dict of exchange_name: ExchangeAPI
        self.risk = risk_manager
        self.config = config
        
        # Arbitrage settings
        self.symbols = config.get('symbols', ['BTC/USDT', 'ETH/USDT'])
        self.min_profit_percent = config.get('min_profit', 0.005)  # 0.5% min profit
        self.max_position_size = config.get('max_position', 1000)  # $1000 max
        self.check_interval = config.get('check_interval', 30)  # 30 seconds
        
        # State
        self.active = False
        self.opportunities = []
        self.executed_trades = []
        self.total_profit = 0
    
    async def start(self):
        """Start arbitrage bot"""
        self.active = True
        logger.info("Arbitrage Bot started")
        
        while self.active:
            try:
                for symbol in self.symbols:
                    await self._scan_arbitrage(symbol)
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Arbitrage bot error: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop arbitrage bot"""
        self.active = False
        logger.info("Arbitrage Bot stopped")
    
    async def _scan_arbitrage(self, symbol: str):
        """Scan for arbitrage opportunities"""
        try:
            # Get prices from all exchanges
            prices = await self._get_all_prices(symbol)
            
            if len(prices) < 2:
                return
            
            # Find best buy and sell exchanges
            opportunity = self._find_best_opportunity(symbol, prices)
            
            if opportunity and opportunity['profit_percent'] >= self.min_profit_percent:
                logger.info(f"Arbitrage opportunity found: {opportunity}")
                self.opportunities.append(opportunity)
                
                # Execute if profitable after fees
                if self._is_profitable_after_fees(opportunity):
                    await self._execute_arbitrage(opportunity)
        
        except Exception as e:
            logger.error(f"Scan arbitrage error for {symbol}: {e}")
    
    async def _get_all_prices(self, symbol: str) -> Dict:
        """Get current prices from all exchanges"""
        prices = {}
        
        for exchange_name, exchange_api in self.exchanges.items():
            try:
                ticker = await exchange_api.get_ticker(symbol)
                if ticker:
                    prices[exchange_name] = {
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'last': ticker['last'],
                        'volume': ticker['volume']
                    }
            except Exception as e:
                logger.debug(f"Could not get price from {exchange_name}: {e}")
        
        return prices
    
    def _find_best_opportunity(self, symbol: str, prices: Dict) -> Dict:
        """Find best arbitrage opportunity"""
        best_opportunity = None
        max_profit = 0
        
        # Compare all exchange pairs
        exchange_names = list(prices.keys())
        
        for i, buy_exchange in enumerate(exchange_names):
            for sell_exchange in exchange_names[i+1:]:
                # Calculate profit buying on buy_exchange, selling on sell_exchange
                buy_price = prices[buy_exchange]['ask']
                sell_price = prices[sell_exchange]['bid']
                profit_percent = (sell_price - buy_price) / buy_price
                
                if profit_percent > max_profit:
                    max_profit = profit_percent
                    best_opportunity = {
                        'symbol': symbol,
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_percent': profit_percent,
                        'timestamp': datetime.now()
                    }
                
                # Also check reverse direction
                profit_percent_reverse = (buy_price - sell_price) / sell_price
                
                if profit_percent_reverse > max_profit:
                    max_profit = profit_percent_reverse
                    best_opportunity = {
                        'symbol': symbol,
                        'buy_exchange': sell_exchange,
                        'sell_exchange': buy_exchange,
                        'buy_price': sell_price,
                        'sell_price': buy_price,
                        'profit_percent': profit_percent_reverse,
                        'timestamp': datetime.now()
                    }
        
        return best_opportunity
    
    def _is_profitable_after_fees(self, opportunity: Dict) -> bool:
        """Check if opportunity is profitable after fees"""
        buy_exchange_api = self.exchanges[opportunity['buy_exchange']]
        sell_exchange_api = self.exchanges[opportunity['sell_exchange']]
        
        # Calculate fees
        amount = self.max_position_size / opportunity['buy_price']
        
        buy_fees = buy_exchange_api.calculate_fees(amount, opportunity['buy_price'])
        sell_fees = sell_exchange_api.calculate_fees(amount, opportunity['sell_price'])
        
        # Total fees as percent
        buy_cost = amount * opportunity['buy_price']
        sell_revenue = amount * opportunity['sell_price']
        
        total_fees = buy_fees['taker_fee'] + sell_fees['taker_fee']
        gross_profit = sell_revenue - buy_cost
        net_profit = gross_profit - total_fees
        net_profit_percent = net_profit / buy_cost
        
        logger.info(f"Gross profit: {opportunity['profit_percent']:.2%}, Fees: ${total_fees:.2f}, Net profit: {net_profit_percent:.2%}")
        
        return net_profit_percent >= self.min_profit_percent
    
    async def _execute_arbitrage(self, opportunity: Dict):
        """Execute arbitrage trade"""
        buy_exchange = self.exchanges[opportunity['buy_exchange']]
        sell_exchange = self.exchanges[opportunity['sell_exchange']]
        symbol = opportunity['symbol']
        
        try:
            # Calculate position size
            position_value = min(self.max_position_size, 
                               self.risk.calculate_position_size(self.max_position_size))
            amount = position_value / opportunity['buy_price']
            
            # Check balances
            buy_balance = await buy_exchange.get_balance('USDT')
            sell_balance = await sell_exchange.get_balance(symbol.split('/')[0])
            
            if buy_balance['free'] < position_value:
                logger.warning(f"Insufficient balance on {opportunity['buy_exchange']}")
                return
            
            # Execute buy order
            buy_order = await buy_exchange.create_order(
                symbol=symbol,
                side='buy',
                order_type='market',
                amount=amount
            )
            
            if 'error' in buy_order:
                logger.error(f"Buy order failed: {buy_order['error']}")
                return
            
            logger.info(f"Buy executed on {opportunity['buy_exchange']}: {amount} @ ${buy_order['price']}")
            
            # Wait a moment for balance update
            await asyncio.sleep(2)
            
            # Execute sell order
            sell_order = await sell_exchange.create_order(
                symbol=symbol,
                side='sell',
                order_type='market',
                amount=amount
            )
            
            if 'error' in sell_order:
                logger.error(f"Sell order failed: {sell_order['error']}")
                # TODO: Handle stuck position
                return
            
            logger.info(f"Sell executed on {opportunity['sell_exchange']}: {amount} @ ${sell_order['price']}")
            
            # Calculate actual profit
            buy_cost = buy_order['amount'] * buy_order['price']
            sell_revenue = sell_order['amount'] * sell_order['price']
            profit = sell_revenue - buy_cost
            profit_percent = profit / buy_cost
            
            # Record trade
            trade_record = {
                'symbol': symbol,
                'buy_exchange': opportunity['buy_exchange'],
                'sell_exchange': opportunity['sell_exchange'],
                'buy_price': buy_order['price'],
                'sell_price': sell_order['price'],
                'amount': amount,
                'profit': profit,
                'profit_percent': profit_percent,
                'timestamp': datetime.now()
            }
            
            self.executed_trades.append(trade_record)
            self.total_profit += profit
            
            # Update risk manager
            self.risk.update_pnl(profit)
            
            logger.info(f"Arbitrage completed: Profit ${profit:.2f} ({profit_percent:.2%})")
        
        except Exception as e:
            logger.error(f"Execute arbitrage error: {e}")
    
    def get_status(self) -> Dict:
        """Get bot status"""
        recent_opportunities = [
            {
                'symbol': opp['symbol'],
                'buy_from': opp['buy_exchange'],
                'sell_to': opp['sell_exchange'],
                'profit': f"{opp['profit_percent']:.2%}",
                'time': opp['timestamp'].strftime('%H:%M:%S')
            }
            for opp in self.opportunities[-10:]
        ]
        
        return {
            'active': self.active,
            'exchanges': list(self.exchanges.keys()),
            'symbols': self.symbols,
            'total_opportunities': len(self.opportunities),
            'executed_trades': len(self.executed_trades),
            'total_profit': self.total_profit,
            'recent_opportunities': recent_opportunities
        }
    
    def get_performance(self) -> Dict:
        """Get performance statistics"""
        if not self.executed_trades:
            return {
                'total_trades': 0,
                'total_profit': 0,
                'avg_profit': 0,
                'success_rate': 0
            }
        
        successful = [t for t in self.executed_trades if t['profit'] > 0]
        
        return {
            'total_trades': len(self.executed_trades),
            'successful_trades': len(successful),
            'total_profit': self.total_profit,
            'avg_profit': self.total_profit / len(self.executed_trades),
            'avg_profit_percent': sum(t['profit_percent'] for t in self.executed_trades) / len(self.executed_trades),
            'success_rate': len(successful) / len(self.executed_trades),
            'best_trade': max(self.executed_trades, key=lambda x: x['profit'])['profit'] if self.executed_trades else 0,
            'profit_by_pair': self._calculate_profit_by_pair()
        }
    
    def _calculate_profit_by_pair(self) -> Dict:
        """Calculate profit by symbol"""
        profit_by_symbol = {}
        
        for trade in self.executed_trades:
            symbol = trade['symbol']
            if symbol not in profit_by_symbol:
                profit_by_symbol[symbol] = 0
            profit_by_symbol[symbol] += trade['profit']
        
        return profit_by_symbol
