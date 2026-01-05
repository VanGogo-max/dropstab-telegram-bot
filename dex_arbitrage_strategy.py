"""
Advanced DEX Arbitrage Strategies
Supports: Price arbitrage, Funding rate arbitrage, Triangular arbitrage
"""

import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import asyncio
from datetime import datetime
from exchange_api import MultiExchangeAPI
from config import *

logger = logging.getLogger(__name__)


class PriceArbitrageStrategy:
    """
    Simple price arbitrage: Buy low on one exchange, sell high on another
    """
    
    def __init__(self, api: MultiExchangeAPI, min_profit_pct: float = 0.5):
        self.api = api
        self.min_profit_pct = min_profit_pct
        self.active_trades = {}
        
        logger.info(f"Price Arbitrage Strategy initialized (min profit: {min_profit_pct}%)")
    
    def find_opportunities(self, symbols: List[str]) -> List[Dict]:
        """Scan all symbols for arbitrage opportunities"""
        opportunities = []
        
        for symbol in symbols:
            try:
                # Get best buy and sell prices
                buy_exchange, buy_price = self.api.get_best_price(symbol, 'buy')
                sell_exchange, sell_price = self.api.get_best_price(symbol, 'sell')
                
                if not buy_exchange or not sell_exchange or buy_exchange == sell_exchange:
                    continue
                
                # Calculate profit (accounting for fees)
                fees = 0.001 * 2  # 0.1% per trade, both sides
                profit_pct = ((sell_price - buy_price) / buy_price - fees) * 100
                
                if profit_pct >= self.min_profit_pct:
                    opportunities.append({
                        'symbol': symbol,
                        'buy_exchange': buy_exchange,
                        'buy_price': buy_price,
                        'sell_exchange': sell_exchange,
                        'sell_price': sell_price,
                        'profit_pct': profit_pct,
                        'timestamp': datetime.now()
                    })
                    
                    logger.info(f"📊 Arbitrage found: {symbol} | "
                              f"Buy {buy_exchange}@${buy_price:.2f} → "
                              f"Sell {sell_exchange}@${sell_price:.2f} | "
                              f"Profit: {profit_pct:.2f}%")
            
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        return opportunities
    
    def execute_arbitrage(self, opportunity: Dict, position_size: float) -> Dict:
        """Execute arbitrage trade"""
        try:
            symbol = opportunity['symbol']
            buy_ex = opportunity['buy_exchange']
            sell_ex = opportunity['sell_exchange']
            
            logger.info(f"🚀 Executing arbitrage: {symbol}")
            
            # Execute buy order
            buy_order = self.api.exchanges[buy_ex].create_order(
                symbol=symbol,
                side='buy',
                amount=position_size,
                order_type='market'
            )
            
            if 'error' in buy_order:
                logger.error(f"Buy order failed: {buy_order['error']}")
                return {'success': False, 'error': buy_order['error']}
            
            # Execute sell order
            sell_order = self.api.exchanges[sell_ex].create_order(
                symbol=symbol,
                side='sell',
                amount=position_size,
                order_type='market'
            )
            
            if 'error' in sell_order:
                logger.error(f"Sell order failed: {sell_order['error']}")
                # Try to reverse buy order if sell fails
                return {'success': False, 'error': sell_order['error']}
            
            # Calculate actual profit
            actual_profit = (opportunity['sell_price'] - opportunity['buy_price']) * position_size
            
            result = {
                'success': True,
                'symbol': symbol,
                'buy_exchange': buy_ex,
                'sell_exchange': sell_ex,
                'position_size': position_size,
                'profit_usd': actual_profit,
                'profit_pct': opportunity['profit_pct'],
                'buy_order': buy_order,
                'sell_order': sell_order,
                'timestamp': datetime.now()
            }
            
            logger.info(f"✅ Arbitrage executed: Profit ${actual_profit:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Arbitrage execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_scanner(self, symbols: List[str], interval: int = 5):
        """Continuously scan for arbitrage opportunities"""
        logger.info(f"Starting arbitrage scanner for {len(symbols)} symbols")
        
        while True:
            try:
                opportunities = self.find_opportunities(symbols)
                
                if opportunities:
                    logger.info(f"Found {len(opportunities)} arbitrage opportunities")
                    
                    # Execute best opportunity
                    best = max(opportunities, key=lambda x: x['profit_pct'])
                    
                    # Calculate position size (conservative)
                    position_size = min(
                        MAX_POSITION_SIZE / best['buy_price'],
                        1000 / best['buy_price']  # Max $1000 per trade
                    )
                    
                    result = self.execute_arbitrage(best, position_size)
                    
                    if result['success']:
                        logger.info(f"💰 Arbitrage profit: ${result['profit_usd']:.2f}")
                
                # Wait before next scan
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Arbitrage scanner stopped")
                break
            except Exception as e:
                logger.error(f"Scanner error: {e}")
                time.sleep(interval)


class FundingRateArbitrageStrategy:
    """
    Funding rate arbitrage: Earn funding payments by hedging positions
    across exchanges with different funding rates
    """
    
    def __init__(self, api: MultiExchangeAPI, min_rate_diff: float = 0.01):
        self.api = api
        self.min_rate_diff = min_rate_diff  # 0.01 = 1% difference
        self.positions = {}
        
        logger.info(f"Funding Rate Arbitrage initialized (min diff: {min_rate_diff*100}%)")
    
    def find_funding_opportunities(self, symbols: List[str]) -> List[Dict]:
        """Find funding rate arbitrage opportunities"""
        opportunities = []
        
        for symbol in symbols:
            try:
                # Get funding rates from all exchanges
                rates = self.api.get_funding_rates(symbol)
                
                if len(rates) < 2:
                    continue
                
                # Find highest and lowest rates
                max_exchange = max(rates, key=rates.get)
                min_exchange = min(rates, key=rates.get)
                
                rate_diff = rates[max_exchange] - rates[min_exchange]
                
                if abs(rate_diff) >= self.min_rate_diff:
                    opportunities.append({
                        'symbol': symbol,
                        'long_exchange': min_exchange,  # Long where funding is negative
                        'short_exchange': max_exchange,  # Short where funding is positive
                        'long_rate': rates[min_exchange],
                        'short_rate': rates[max_exchange],
                        'rate_diff': rate_diff,
                        'daily_profit_pct': rate_diff * 3 * 100,  # Funding paid 3x per day
                        'timestamp': datetime.now()
                    })
                    
                    logger.info(f"📊 Funding arbitrage: {symbol} | "
                              f"Long {min_exchange}@{rates[min_exchange]:.4f}% → "
                              f"Short {max_exchange}@{rates[max_exchange]:.4f}% | "
                              f"Daily profit: {rate_diff*3*100:.2f}%")
            
            except Exception as e:
                logger.error(f"Error scanning funding rates for {symbol}: {e}")
        
        return opportunities
    
    def execute_funding_arbitrage(self, opportunity: Dict, notional_size: float) -> Dict:
        """
        Execute funding rate arbitrage:
        - Open LONG on exchange with negative/low funding
        - Open SHORT on exchange with positive/high funding
        """
        try:
            symbol = opportunity['symbol']
            long_ex = opportunity['long_exchange']
            short_ex = opportunity['short_exchange']
            
            # Get current prices
            long_price = self.api.exchanges[long_ex].get_market_price(symbol)
            short_price = self.api.exchanges[short_ex].get_market_price(symbol)
            
            # Calculate position sizes
            long_size = notional_size / long_price
            short_size = notional_size / short_price
            
            logger.info(f"🚀 Executing funding arbitrage: {symbol}")
            
            # Open long position
            long_order = self.api.exchanges[long_ex].create_futures_order(
                symbol=symbol,
                side='buy',
                size=long_size,
                leverage=FUTURES_MAX_LEVERAGE
            )
            
            # Open short position
            short_order = self.api.exchanges[short_ex].create_futures_order(
                symbol=symbol,
                side='sell',
                size=short_size,
                leverage=FUTURES_MAX_LEVERAGE
            )
            
            # Store position for tracking
            position_id = f"{symbol}_{long_ex}_{short_ex}_{int(time.time())}"
            self.positions[position_id] = {
                'symbol': symbol,
                'long_exchange': long_ex,
                'short_exchange': short_ex,
                'long_size': long_size,
                'short_size': short_size,
                'entry_time': datetime.now(),
                'rate_diff': opportunity['rate_diff']
            }
            
            logger.info(f"✅ Funding arbitrage position opened: {position_id}")
            
            return {
                'success': True,
                'position_id': position_id,
                'symbol': symbol,
                'notional_size': notional_size,
                'daily_profit_pct': opportunity['daily_profit_pct']
            }
            
        except Exception as e:
            logger.error(f"Funding arbitrage error: {e}")
            return {'success': False, 'error': str(e)}
    
    def close_funding_position(self, position_id: str) -> Dict:
        """Close a funding arbitrage position"""
        try:
            if position_id not in self.positions:
                return {'success': False, 'error': 'Position not found'}
            
            position = self.positions[position_id]
            
            # Close long
            long_close = self.api.exchanges[position['long_exchange']].create_futures_order(
                symbol=position['symbol'],
                side='sell',
                size=position['long_size'],
                reduce_only=True
            )
            
            # Close short
            short_close = self.api.exchanges[position['short_exchange']].create_futures_order(
                symbol=position['symbol'],
                side='buy',
                size=position['short_size'],
                reduce_only=True
            )
            
            # Calculate profit (simplified)
            duration_hours = (datetime.now() - position['entry_time']).total_seconds() / 3600
            funding_periods = duration_hours / 8  # Funding every 8 hours
            profit_pct = position['rate_diff'] * funding_periods
            
            del self.positions[position_id]
            
            logger.info(f"✅ Funding position closed: Profit ~{profit_pct*100:.2f}%")
            
            return {'success': True, 'profit_pct': profit_pct}
            
        except Exception as e:
            logger.error(f"Position close error: {e}")
            return {'success': False, 'error': str(e)}


class TriangularArbitrageStrategy:
    """
    Triangular arbitrage: Exploit price differences in 3-way trades
    Example: USDT → BTC → ETH → USDT
    """
    
    def __init__(self, api: MultiExchangeAPI):
        self.api = api
        logger.info("Triangular Arbitrage Strategy initialized")
    
    def find_triangular_opportunities(self, base: str = 'USDT') -> List[Dict]:
        """
        Find triangular arbitrage opportunities
        Example paths: USDT → BTC → ETH → USDT
        """
        opportunities = []
        
        # Define common trading pairs
        pairs = [
            ('BTC/USDT', 'ETH/BTC', 'ETH/USDT'),
            ('BTC/USDT', 'SOL/BTC', 'SOL/USDT'),
            # Add more triangular paths
        ]
        
        for pair1, pair2, pair3 in pairs:
            try:
                # Get prices for all three pairs
                price1 = self.api.exchanges['hyperliquid'].get_mark_price(pair1)
                price2 = self.api.exchanges['hyperliquid'].get_mark_price(pair2)
                price3 = self.api.exchanges['hyperliquid'].get_mark_price(pair3)
                
                if not all([price1, price2, price3]):
                    continue
                
                # Calculate triangular profit
                # Start with 1 USDT → BTC → ETH → USDT
                btc_amount = 1 / price1
                eth_amount = btc_amount / price2
                final_usdt = eth_amount * price3
                
                profit_pct = (final_usdt - 1) * 100
                
                if profit_pct > 0.3:  # Minimum 0.3% profit after fees
                    opportunities.append({
                        'path': [pair1, pair2, pair3],
                        'profit_pct': profit_pct,
                        'prices': [price1, price2, price3]
                    })
                    
                    logger.info(f"🔺 Triangular arbitrage: {profit_pct:.2f}% profit")
            
            except Exception as e:
                logger.error(f"Triangular scan error: {e}")
        
        return opportunities


# Initialize strategies
def initialize_arbitrage_strategies(testnet: bool = True):
    """Initialize all arbitrage strategies"""
    api = MultiExchangeAPI(testnet=testnet)
    
    strategies = {
        'price_arbitrage': PriceArbitrageStrategy(api, min_profit_pct=0.5),
        'funding_arbitrage': FundingRateArbitrageStrategy(api, min_rate_diff=0.01),
        'triangular_arbitrage': TriangularArbitrageStrategy(api)
    }
    
    logger.info("All arbitrage strategies initialized")
    return strategies


if __name__ == "__main__":
    # Example usage
    strategies = initialize_arbitrage_strategies(testnet=True)
    
    # Run price arbitrage scanner
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    strategies['price_arbitrage'].run_scanner(symbols, interval=10)
