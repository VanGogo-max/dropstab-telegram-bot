# exchange_api.py - Universal Exchange API Handler
import ccxt
import asyncio
from typing import Dict, List, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ExchangeAPI:
    """Unified interface for multiple exchanges"""
    
    def __init__(self, exchange_name: str, api_key: str, api_secret: str, testnet: bool = False):
        self.exchange_name = exchange_name.lower()
        self.testnet = testnet
        
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_name)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        if testnet:
            self.exchange.set_sandbox_mode(True)
    
    async def get_balance(self, currency: str = None) -> Dict:
        """Get account balance"""
        try:
            balance = await self.exchange.fetch_balance()
            if currency:
                return {
                    'free': float(balance['free'].get(currency, 0)),
                    'used': float(balance['used'].get(currency, 0)),
                    'total': float(balance['total'].get(currency, 0))
                }
            return balance
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")
            return {}
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': float(ticker['last']),
                'bid': float(ticker['bid']),
                'ask': float(ticker['ask']),
                'volume': float(ticker['baseVolume']),
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.error(f"Ticker fetch error for {symbol}: {e}")
            return {}
    
    async def create_order(self, symbol: str, side: str, order_type: str, 
                          amount: float, price: float = None) -> Dict:
        """Create order (buy/sell)"""
        try:
            if order_type == 'market':
                order = await self.exchange.create_market_order(symbol, side, amount)
            else:
                order = await self.exchange.create_limit_order(symbol, side, amount, price)
            
            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'amount': float(order['amount']),
                'price': float(order['price']) if order['price'] else None,
                'status': order['status'],
                'timestamp': order['timestamp']
            }
        except Exception as e:
            logger.error(f"Order creation error: {e}")
            return {'error': str(e)}
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order"""
        try:
            await self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Order cancel error: {e}")
            return False
    
    async def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get all open orders"""
        try:
            orders = await self.exchange.fetch_open_orders(symbol)
            return [{
                'id': o['id'],
                'symbol': o['symbol'],
                'side': o['side'],
                'type': o['type'],
                'amount': float(o['amount']),
                'price': float(o['price']) if o['price'] else None,
                'status': o['status']
            } for o in orders]
        except Exception as e:
            logger.error(f"Open orders fetch error: {e}")
            return []
    
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List[Dict]:
        """Get order history"""
        try:
            orders = await self.exchange.fetch_closed_orders(symbol, limit=limit)
            return [{
                'id': o['id'],
                'symbol': o['symbol'],
                'side': o['side'],
                'amount': float(o['amount']),
                'price': float(o['price']) if o['price'] else None,
                'cost': float(o['cost']),
                'status': o['status'],
                'timestamp': o['timestamp']
            } for o in orders]
        except Exception as e:
            logger.error(f"Order history fetch error: {e}")
            return []
    
    async def get_klines(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List:
        """Get candlestick data"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return [{
                'timestamp': k[0],
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in ohlcv]
        except Exception as e:
            logger.error(f"Klines fetch error: {e}")
            return []
    
    async def get_markets(self) -> List[str]:
        """Get available trading pairs"""
        try:
            markets = await self.exchange.load_markets()
            return list(markets.keys())
        except Exception as e:
            logger.error(f"Markets fetch error: {e}")
            return []
    
    def calculate_fees(self, amount: float, price: float) -> Dict:
        """Calculate trading fees"""
        maker_fee = self.exchange.fees['trading']['maker']
        taker_fee = self.exchange.fees['trading']['taker']
        cost = amount * price
        
        return {
            'maker_fee': cost * maker_fee,
            'taker_fee': cost * taker_fee,
            'maker_percent': maker_fee * 100,
            'taker_percent': taker_fee * 100
        }

class MultiExchangeManager:
    """Manage multiple exchange connections"""
    
    def __init__(self):
        self.exchanges: Dict[str, ExchangeAPI] = {}
    
    def add_exchange(self, name: str, api_key: str, api_secret: str, testnet: bool = False):
        """Add exchange connection"""
        self.exchanges[name] = ExchangeAPI(name, api_key, api_secret, testnet)
    
    def get_exchange(self, name: str) -> Optional[ExchangeAPI]:
        """Get exchange by name"""
        return self.exchanges.get(name)
    
    async def get_all_balances(self) -> Dict:
        """Get balances from all exchanges"""
        balances = {}
        for name, exchange in self.exchanges.items():
            balances[name] = await exchange.get_balance()
        return balances
    
    async def get_best_price(self, symbol: str, side: str) -> Dict:
        """Find best price across exchanges"""
        prices = {}
        for name, exchange in self.exchanges.items():
            ticker = await exchange.get_ticker(symbol)
            if ticker:
                price = ticker['ask'] if side == 'buy' else ticker['bid']
                prices[name] = price
        
        if not prices:
            return {}
        
        best_exchange = min(prices, key=prices.get) if side == 'buy' else max(prices, key=prices.get)
        return {
            'exchange': best_exchange,
            'price': prices[best_exchange],
            'all_prices': prices
        }р
