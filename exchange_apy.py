"""
Multi-Exchange API Integration - Extended Version
Supports: KCEX, Hyperliquid, dYdX, GMX, Kwenta, Vertex, Apex
With arbitrage capabilities and unified interface
"""

import ccxt
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import requests
from web3 import Web3
import time
from config import *

logger = logging.getLogger(__name__)


class KCEXExchange:
    """KCEX Spot Trading (Primary Spot Exchange)"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.session = requests.Session()
        self.base_url = KCEX_BASE_URL
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-KEY': KCEX_API_KEY
        })
        
        logger.info(f"KCEX initialized (testnet={testnet})")
    
    def get_balance(self, currency: str = 'USDT') -> Decimal:
        try:
            response = self.session.get(f"{self.base_url}{KCEX_BALANCE_ENDPOINT}")
            data = response.json()
            
            for balance in data.get('balances', []):
                if balance['currency'] == currency:
                    return Decimal(str(balance['available']))
            return Decimal('0')
        except Exception as e:
            logger.error(f"KCEX balance error: {e}")
            return Decimal('0')
    
    def create_order(self, symbol: str, side: str, amount: float, 
                     order_type: str = 'market', price: float = None) -> Dict:
        try:
            payload = {
                'symbol': symbol,
                'side': side.lower(),
                'type': order_type,
                'amount': amount
            }
            
            if order_type == 'limit' and price:
                payload['price'] = price
            
            response = self.session.post(
                f"{self.base_url}{KCEX_ORDER_ENDPOINT}",
                json=payload
            )
            
            result = response.json()
            logger.info(f"KCEX order created: {result.get('orderId')}")
            return result
        except Exception as e:
            logger.error(f"KCEX order error: {e}")
            return {'error': str(e)}
    
    def get_ticker(self, symbol: str) -> Dict:
        try:
            response = self.session.get(
                f"{self.base_url}{KCEX_TICKER_ENDPOINT}",
                params={'symbol': symbol}
            )
            return response.json()
        except Exception as e:
            logger.error(f"KCEX ticker error: {e}")
            return {}


class HyperliquidExchange:
    """Hyperliquid Futures Trading (Arbitrum)"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.session = requests.Session()
        
        if testnet:
            self.base_url = HYPERLIQUID_TESTNET_URL
        else:
            self.base_url = HYPERLIQUID_MAINNET_URL
        
        self.wallet_address = HYPERLIQUID_WALLET
        
        logger.info(f"Hyperliquid initialized (testnet={testnet})")
    
    def get_futures_balance(self) -> Decimal:
        try:
            response = self.session.post(
                f"{self.base_url}{HYPERLIQUID_INFO_ENDPOINT}",
                json={
                    'type': 'clearinghouseState',
                    'user': self.wallet_address
                }
            )
            
            data = response.json()
            balance = data.get('marginSummary', {}).get('accountValue', '0')
            return Decimal(str(balance))
        except Exception as e:
            logger.error(f"Hyperliquid balance error: {e}")
            return Decimal('0')
    
    def create_futures_order(self, symbol: str, side: str, size: float,
                            leverage: int = 1, reduce_only: bool = False) -> Dict:
        try:
            order = {
                'coin': symbol.replace('/USDT', ''),
                'is_buy': side.lower() == 'buy',
                'sz': size,
                'limit_px': None,
                'order_type': {'limit': {'tif': 'Ioc'}},
                'reduce_only': reduce_only
            }
            
            payload = {
                'type': 'order',
                'orders': [order],
                'grouping': 'na'
            }
            
            response = self.session.post(
                f"{self.base_url}{HYPERLIQUID_EXCHANGE_ENDPOINT}",
                json=payload
            )
            
            return response.json()
        except Exception as e:
            logger.error(f"Hyperliquid order error: {e}")
            return {'error': str(e)}
    
    def get_mark_price(self, symbol: str) -> float:
        try:
            response = self.session.post(
                f"{self.base_url}{HYPERLIQUID_INFO_ENDPOINT}",
                json={'type': 'allMids'}
            )
            
            data = response.json()
            coin = symbol.replace('/USDT', '')
            return float(data.get(coin, 0))
        except Exception as e:
            logger.error(f"Hyperliquid price error: {e}")
            return 0.0


class DYDXExchange:
    """dYdX v4 - Leading DeFi Perpetuals"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.session = requests.Session()
        
        if testnet:
            self.base_url = DYDX_TESTNET_URL
        else:
            self.base_url = DYDX_MAINNET_URL
        
        self.api_key = DYDX_API_KEY
        
        logger.info(f"dYdX v4 initialized (testnet={testnet})")
    
    def get_account(self) -> Dict:
        """Get account info including balance"""
        try:
            response = self.session.get(
                f"{self.base_url}/v4/addresses/{DYDX_WALLET}/subaccounts/0",
                headers={'X-API-KEY': self.api_key}
            )
            return response.json()
        except Exception as e:
            logger.error(f"dYdX account error: {e}")
            return {}
    
    def get_balance(self) -> Decimal:
        """Get USDC balance"""
        try:
            account = self.get_account()
            equity = account.get('subaccount', {}).get('equity', '0')
            return Decimal(str(equity))
        except Exception as e:
            logger.error(f"dYdX balance error: {e}")
            return Decimal('0')
    
    def create_order(self, symbol: str, side: str, size: float, 
                     order_type: str = 'MARKET', price: float = None) -> Dict:
        """Place perpetual order"""
        try:
            order = {
                'market': symbol,
                'side': side.upper(),
                'type': order_type,
                'size': str(size),
                'postOnly': False
            }
            
            if order_type == 'LIMIT' and price:
                order['price'] = str(price)
            
            response = self.session.post(
                f"{self.base_url}/v4/orders",
                json=order,
                headers={'X-API-KEY': self.api_key}
            )
            
            return response.json()
        except Exception as e:
            logger.error(f"dYdX order error: {e}")
            return {'error': str(e)}
    
    def get_market_price(self, symbol: str) -> float:
        """Get current market price"""
        try:
            response = self.session.get(
                f"{self.base_url}/v4/perpetualMarkets/{symbol}"
            )
            data = response.json()
            return float(data.get('markets', {}).get(symbol, {}).get('oraclePrice', 0))
        except Exception as e:
            logger.error(f"dYdX price error: {e}")
            return 0.0
    
    def get_funding_rate(self, symbol: str) -> float:
        """Get current funding rate"""
        try:
            response = self.session.get(
                f"{self.base_url}/v4/perpetualMarkets/{symbol}"
            )
            data = response.json()
            funding = data.get('markets', {}).get(symbol, {}).get('nextFundingRate', 0)
            return float(funding)
        except Exception as e:
            logger.error(f"dYdX funding rate error: {e}")
            return 0.0


class GMXExchange:
    """GMX v2 - Arbitrum & Avalanche"""
    
    def __init__(self, network: str = 'arbitrum', testnet: bool = False):
        self.network = network
        self.testnet = testnet
        
        # Web3 setup
        if network == 'arbitrum':
            rpc_url = GMX_ARBITRUM_RPC if not testnet else GMX_ARBITRUM_TESTNET_RPC
        else:  # avalanche
            rpc_url = GMX_AVALANCHE_RPC
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallet_address = GMX_WALLET
        
        # GMX v2 contract addresses (update with actual)
        self.reader_contract = self.w3.eth.contract(
            address=GMX_READER_CONTRACT,
            abi=GMX_READER_ABI  # Load from file
        )
        
        logger.info(f"GMX initialized (network={network}, testnet={testnet})")
    
    def get_balance(self) -> Decimal:
        """Get account balance"""
        try:
            balance = self.w3.eth.get_balance(self.wallet_address)
            return Decimal(str(self.w3.from_wei(balance, 'ether')))
        except Exception as e:
            logger.error(f"GMX balance error: {e}")
            return Decimal('0')
    
    def get_market_price(self, token: str) -> float:
        """Get token price from GMX oracle"""
        try:
            # Call GMX Reader contract
            price = self.reader_contract.functions.getPrice(token).call()
            return float(price) / 1e30  # GMX uses 30 decimals
        except Exception as e:
            logger.error(f"GMX price error: {e}")
            return 0.0
    
    def create_order(self, market: str, side: str, size: float, 
                     leverage: int = 1) -> Dict:
        """Create position order (simplified - actual implementation needs more)"""
        try:
            # This is a simplified version
            # Real implementation would interact with GMX Router contract
            logger.info(f"GMX order: {side} {size} {market} with {leverage}x")
            return {'status': 'pending', 'note': 'GMX integration requires contract interaction'}
        except Exception as e:
            logger.error(f"GMX order error: {e}")
            return {'error': str(e)}


class KwentaExchange:
    """Kwenta - Synthetix Perps on Optimism"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.session = requests.Session()
        
        # Kwenta API (Optimism)
        if testnet:
            self.base_url = KWENTA_TESTNET_URL
        else:
            self.base_url = KWENTA_MAINNET_URL
        
        self.wallet_address = KWENTA_WALLET
        
        logger.info(f"Kwenta initialized (testnet={testnet})")
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        try:
            response = self.session.get(
                f"{self.base_url}/positions",
                params={'account': self.wallet_address}
            )
            return response.json().get('positions', [])
        except Exception as e:
            logger.error(f"Kwenta positions error: {e}")
            return []
    
    def get_market_price(self, market: str) -> float:
        """Get market price"""
        try:
            response = self.session.get(
                f"{self.base_url}/markets/{market}"
            )
            data = response.json()
            return float(data.get('price', 0))
        except Exception as e:
            logger.error(f"Kwenta price error: {e}")
            return 0.0
    
    def create_order(self, market: str, side: str, size: float) -> Dict:
        """Submit market order"""
        try:
            payload = {
                'market': market,
                'sizeDelta': size if side.lower() == 'long' else -size,
                'desiredFillPrice': 0  # Market order
            }
            
            response = self.session.post(
                f"{self.base_url}/orders",
                json=payload
            )
            return response.json()
        except Exception as e:
            logger.error(f"Kwenta order error: {e}")
            return {'error': str(e)}


class VertexExchange:
    """Vertex Protocol - Arbitrum Hybrid DEX"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.session = requests.Session()
        
        if testnet:
            self.base_url = VERTEX_TESTNET_URL
        else:
            self.base_url = VERTEX_MAINNET_URL
        
        logger.info(f"Vertex initialized (testnet={testnet})")
    
    def get_balance(self, subaccount: str) -> Dict:
        """Get subaccount balances"""
        try:
            response = self.session.post(
                f"{self.base_url}/query",
                json={
                    'type': 'subaccount_info',
                    'subaccount': subaccount
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Vertex balance error: {e}")
            return {}
    
    def get_market_price(self, product_id: int) -> float:
        """Get market price"""
        try:
            response = self.session.post(
                f"{self.base_url}/query",
                json={'type': 'market_price', 'product_id': product_id}
            )
            return float(response.json().get('price', 0))
        except Exception as e:
            logger.error(f"Vertex price error: {e}")
            return 0.0


class ApexExchange:
    """Apex Protocol - Multi-chain Perps"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.session = requests.Session()
        
        if testnet:
            self.base_url = APEX_TESTNET_URL
        else:
            self.base_url = APEX_MAINNET_URL
        
        logger.info(f"Apex initialized (testnet={testnet})")
    
    def get_account(self) -> Dict:
        """Get account info"""
        try:
            response = self.session.get(
                f"{self.base_url}/v1/account",
                headers={'APEX-API-KEY': APEX_API_KEY}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Apex account error: {e}")
            return {}
    
    def get_market_price(self, symbol: str) -> float:
        """Get market price"""
        try:
            response = self.session.get(
                f"{self.base_url}/v1/ticker",
                params={'symbol': symbol}
            )
            return float(response.json().get('data', {}).get('p', 0))
        except Exception as e:
            logger.error(f"Apex price error: {e}")
            return 0.0


class MultiExchangeAPI:
    """Unified API for all 7 exchanges"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        
        # Initialize all exchanges
        self.kcex = KCEXExchange(testnet)
        self.hyperliquid = HyperliquidExchange(testnet)
        self.dydx = DYDXExchange(testnet)
        self.gmx = GMXExchange('arbitrum', testnet)
        self.kwenta = KwentaExchange(testnet)
        self.vertex = VertexExchange(testnet)
        self.apex = ApexExchange(testnet)
        
        # Exchange mapping
        self.exchanges = {
            'kcex': self.kcex,
            'hyperliquid': self.hyperliquid,
            'dydx': self.dydx,
            'gmx': self.gmx,
            'kwenta': self.kwenta,
            'vertex': self.vertex,
            'apex': self.apex
        }
        
        logger.info("Multi-Exchange API initialized with 7 exchanges")
    
    def get_best_price(self, symbol: str, side: str) -> Tuple[str, float]:
        """
        Find best price across all exchanges
        Returns: (exchange_name, price)
        """
        prices = {}
        
        for name, exchange in self.exchanges.items():
            try:
                if hasattr(exchange, 'get_mark_price'):
                    price = exchange.get_mark_price(symbol)
                elif hasattr(exchange, 'get_market_price'):
                    price = exchange.get_market_price(symbol)
                else:
                    continue
                
                if price > 0:
                    prices[name] = price
            except Exception as e:
                logger.error(f"Error getting price from {name}: {e}")
        
        if not prices:
            return None, 0.0
        
        # For buy orders, find lowest price
        # For sell orders, find highest price
        if side.lower() == 'buy':
            best_exchange = min(prices, key=prices.get)
        else:
            best_exchange = max(prices, key=prices.get)
        
        return best_exchange, prices[best_exchange]
    
    def get_funding_rates(self, symbol: str) -> Dict[str, float]:
        """Get funding rates from all perpetual exchanges"""
        rates = {}
        
        # dYdX
        try:
            rates['dydx'] = self.dydx.get_funding_rate(symbol)
        except:
            pass
        
        # Add other exchanges that support funding rates
        
        return rates
    
    def execute_arbitrage(self, symbol: str, size: float) -> Dict:
        """
        Execute arbitrage trade across exchanges
        Buy on cheapest, sell on most expensive
        """
        try:
            # Get prices
            buy_exchange, buy_price = self.get_best_price(symbol, 'buy')
            sell_exchange, sell_price = self.get_best_price(symbol, 'sell')
            
            # Calculate profit
            profit_pct = ((sell_price - buy_price) / buy_price) * 100
            
            logger.info(f"Arbitrage opportunity: Buy {buy_exchange}@{buy_price}, "
                       f"Sell {sell_exchange}@{sell_price}, Profit: {profit_pct:.2f}%")
            
            # Only execute if profit > threshold (e.g., 0.5% after fees)
            if profit_pct > 0.5:
                # Execute buy
                buy_order = self.exchanges[buy_exchange].create_order(
                    symbol, 'buy', size
                )
                
                # Execute sell
                sell_order = self.exchanges[sell_exchange].create_order(
                    symbol, 'sell', size
                )
                
                return {
                    'success': True,
                    'buy_exchange': buy_exchange,
                    'sell_exchange': sell_exchange,
                    'profit_pct': profit_pct,
                    'buy_order': buy_order,
                    'sell_order': sell_order
                }
            else:
                return {'success': False, 'reason': 'Profit too low'}
                
        except Exception as e:
            logger.error(f"Arbitrage execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict[str, bool]:
        """Check all exchanges connectivity"""
        health = {}
        
        for name, exchange in self.exchanges.items():
            try:
                if hasattr(exchange, 'get_balance'):
                    exchange.get_balance()
                    health[name] = True
                else:
                    health[name] = True  # Assume healthy if no balance method
            except:
                health[name] = False
        
        return health


# Initialize global API instance
exchange_api = MultiExchangeAPI(testnet=True)
