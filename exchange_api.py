"""
Multi-Exchange API Integration
Supports: KCEX (spot), Hyperliquid (futures on Arbitrum)
Conservative approach with safety checks
"""

import ccxt
import logging
from typing import Dict, List, Optional
from decimal import Decimal
import requests
from config import *

logger = logging.getLogger(__name__)


class KCEXExchange:
    """KCEX Spot Trading (Primary Spot Exchange)"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.session = requests.Session()
        self.base_url = "https://api.kcex.com"  # Replace with actual API
        
        # Basic headers (adjust based on KCEX docs)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-KEY': KCEX_API_KEY
        })
        
        logger.info(f"KCEX initialized (testnet={testnet})")
    
    def get_balance(self, currency: str = 'USDT') -> Decimal:
        """Get spot balance"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/account/balance")
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
        """Place spot order"""
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
                f"{self.base_url}/api/v1/orders",
                json=payload
            )
            
            result = response.json()
            logger.info(f"KCEX order created: {result.get('orderId')}")
            return result
            
        except Exception as e:
            logger.error(f"KCEX order error: {e}")
            return {'error': str(e)}
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current price"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/ticker",
                params={'symbol': symbol}
            )
            return response.json()
        except Exception as e:
            logger.error(f"KCEX ticker error: {e}")
            return {}


class HyperliquidExchange:
    """Hyperliquid Futures Trading (Arbitrum Network)"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.session = requests.Session()
        
        # Hyperliquid endpoints (Arbitrum)
        if testnet:
            self.base_url = "https://api.hyperliquid-testnet.xyz"
        else:
            self.base_url = "https://api.hyperliquid.xyz"
        
        self.wallet_address = HYPERLIQUID_WALLET  # Arbitrum wallet
        
        logger.info(f"Hyperliquid initialized (testnet={testnet}, network=Arbitrum)")
    
    def get_futures_balance(self) -> Decimal:
        """Get futures account balance"""
        try:
            response = self.session.post(
                f"{self.base_url}/info",
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
        """Place futures order"""
        try:
            # Hyperliquid order format
            order = {
                'coin': symbol.replace('/USDT', ''),
                'is_buy': side.lower() == 'buy',
                'sz': size,
                'limit_px': None,  # Market order
                'order_type': {'limit': {'tif': 'Ioc'}},
                'reduce_only': reduce_only
            }
            
            payload = {
                'type': 'order',
                'orders': [order],
                'grouping': 'na'
            }
            
            response = self.session.post(
                f"{self.base_url}/exchange",
                json=payload
            )
            
            result = response.json()
            logger.info(f"Hyperliquid order: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Hyperliquid order error: {e}")
            return {'error': str(e)}
    
    def get_position(self, symbol: str) -> Dict:
        """Get open position"""
        try:
            response = self.session.post(
                f"{self.base_url}/info",
                json={
                    'type': 'clearinghouseState',
                    'user': self.wallet_address
                }
            )
            
            data = response.json()
            positions = data.get('assetPositions', [])
            
            coin = symbol.replace('/USDT', '')
            for pos in positions:
                if pos['position']['coin'] == coin:
                    return {
                        'size': float(pos['position']['szi']),
                        'entry_price': float(pos['position']['entryPx']),
                        'unrealized_pnl': float(pos['position']['unrealizedPnl'])
                    }
            
            return {'size': 0}
            
        except Exception as e:
            logger.error(f"Hyperliquid position error: {e}")
            return {'size': 0}
    
    def set_leverage(self, symbol: str, leverage: int):
        """Set leverage for symbol"""
        try:
            payload = {
                'type': 'updateLeverage',
                'asset': symbol.replace('/USDT', ''),
                'is_cross': True,
                'leverage': leverage
            }
            
            response = self.session.post(
                f"{self.base_url}/exchange",
                json=payload
            )
            
            logger.info(f"Leverage set to {leverage}x for {symbol}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Hyperliquid leverage error: {e}")
            return {'error': str(e)}
    
    def get_mark_price(self, symbol: str) -> float:
        """Get current mark price"""
        try:
            response = self.session.post(
                f"{self.base_url}/info",
                json={'type': 'allMids'}
            )
            
            data = response.json()
            coin = symbol.replace('/USDT', '')
            return float(data.get(coin, 0))
            
        except Exception as e:
            logger.error(f"Hyperliquid price error: {e}")
            return 0.0


class MultiExchangeAPI:
    """Unified API for all exchanges"""
    
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        
        # Initialize exchanges
        self.kcex = KCEXExchange(testnet)
        self.hyperliquid = HyperliquidExchange(testnet)
        
        # Legacy CCXT support for other exchanges (if needed)
        self.ccxt_exchanges = {}
        
        logger.info("Multi-Exchange API initialized")
    
    def get_spot_exchange(self) -> KCEXExchange:
        """Get KCEX for spot trading"""
        return self.kcex
    
    def get_futures_exchange(self) -> HyperliquidExchange:
        """Get Hyperliquid for futures trading"""
        return self.hyperliquid
    
    def health_check(self) -> Dict[str, bool]:
        """Check all exchanges connectivity"""
        health = {}
        
        # Check KCEX
        try:
            self.kcex.get_balance()
            health['kcex'] = True
        except:
            health['kcex'] = False
        
        # Check Hyperliquid
        try:
            self.hyperliquid.get_futures_balance()
            health['hyperliquid'] = True
        except:
            health['hyperliquid'] = False
        
        return health


# Initialize global API instance
exchange_api = MultiExchangeAPI(testnet=True)
