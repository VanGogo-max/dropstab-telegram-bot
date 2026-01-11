
"""
demo_mode.py - Paper Trading System
Allows users to test all strategies with virtual money
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import json

# Import from your existing database
from database import (
    get_demo_portfolio,
    update_demo_portfolio,
    reset_demo_portfolio,
    get_connection
)

logger = logging.getLogger(__name__)


class DemoMode:
    """
    Paper trading system for risk-free bot testing
    
    Features:
    - Virtual $10,000 starting balance
    - Real market prices (simulated execution)
    - All strategies available
    - Persistent state (saved in database)
    - Can reset anytime
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.portfolio = self._load_portfolio()
        logger.info(f"Demo Mode initialized for user {user_id}")
    
    def _load_portfolio(self) -> Dict:
        """Load user's demo portfolio from database"""
        portfolio = get_demo_portfolio(self.user_id)
        
        if portfolio is None:
            # Create new demo portfolio
            portfolio = {
                'balance_usdt': 10000.0,
                'positions': {},
                'trades': [],
                'total_pnl': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0
            }
            logger.info(f"Created new demo portfolio: {self.user_id}")
        
        return portfolio
    
    def get_balance(self) -> float:
        """Get current USDT balance"""
        return self.portfolio['balance_usdt']
    
    def get_positions(self) -> Dict:
        """Get all open positions"""
        return self.portfolio['positions']
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value
        
        Args:
            current_prices: Dict of {symbol: current_price}
        
        Returns:
            Total value in USDT
        """
        total = self.portfolio['balance_usdt']
        
        for symbol, position in self.portfolio['positions'].items():
            if symbol in current_prices:
                position_value = position['size'] * current_prices[symbol]
                total += position_value
        
        return total
    
    def execute_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        order_type: str = 'market'
    ) -> Dict:
        """
        Execute a paper trading order
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            size: Order size (in base currency)
            price: Execution price
            order_type: 'market' or 'limit'
        
        Returns:
            Order result dict
        """
        try:
            if side == 'buy':
                return self._execute_buy(symbol, size, price)
            elif side == 'sell':
                return self._execute_sell(symbol, size, price)
            else:
                return {'success': False, 'error': 'Invalid side'}
        
        except Exception as e:
            logger.error(f"Order execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_buy(self, symbol: str, size: float, price: float) -> Dict:
        """Execute buy order"""
        cost = size * price
        
        # Check balance
        if self.portfolio['balance_usdt'] < cost:
            return {
                'success': False,
                'error': 'Insufficient demo balance',
                'required': cost,
                'available': self.portfolio['balance_usdt']
            }
        
        # Deduct from balance
        self.portfolio['balance_usdt'] -= cost
        
        # Add to positions
        if symbol in self.portfolio['positions']:
            # Average price calculation
            existing = self.portfolio['positions'][symbol]
            total_size = existing['size'] + size
            avg_price = (
                (existing['size'] * existing['entry_price']) + (size * price)
            ) / total_size
            
            self.portfolio['positions'][symbol] = {
                'size': total_size,
                'entry_price': avg_price,
                'side': 'long'
            }
        else:
            # New position
            self.portfolio['positions'][symbol] = {
                'size': size,
                'entry_price': price,
                'side': 'long'
            }
        
        # Save to database
        self._save_portfolio()
        
        logger.info(f"Demo BUY: {size} {symbol} @ ${price}")
        
        return {
            'success': True,
            'symbol': symbol,
            'side': 'buy',
            'size': size,
            'price': price,
            'cost': cost,
            'balance_remaining': self.portfolio['balance_usdt']
        }
    
    def _execute_sell(self, symbol: str, size: float, price: float) -> Dict:
        """Execute sell order"""
        # Check position
        if symbol not in self.portfolio['positions']:
            return {
                'success': False,
                'error': f'No position for {symbol}'
            }
        
        position = self.portfolio['positions'][symbol]
        
        if position['size'] < size:
            return {
                'success': False,
                'error': 'Insufficient position size',
                'available': position['size'],
                'requested': size
            }
        
        # Calculate P&L
        entry_price = position['entry_price']
        pnl = (price - entry_price) * size
        pnl_percent = ((price - entry_price) / entry_price) * 100
        
        # Add to balance
        revenue = size * price
        self.portfolio['balance_usdt'] += revenue
        
        # Update position
        if position['size'] == size:
            # Close entire position
            del self.portfolio['positions'][symbol]
        else:
            # Reduce position
            self.portfolio['positions'][symbol]['size'] -= size
        
        # Update stats
        self.portfolio['total_pnl'] += pnl
        self.portfolio['total_trades'] += 1
        
        if pnl > 0:
            self.portfolio['winning_trades'] += 1
        else:
            self.portfolio['losing_trades'] += 1
        
        # Record trade
        trade = {
            'symbol': symbol,
            'side': 'sell',
            'size': size,
            'entry_price': entry_price,
            'exit_price': price,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'timestamp': datetime.now().isoformat()
        }
        self.portfolio['trades'].append(trade)
        
        # Save to database
        self._save_portfolio()
        
        logger.info(f"Demo SELL: {size} {symbol} @ ${price}, P&L: ${pnl:.2f}")
        
        return {
            'success': True,
            'symbol': symbol,
            'side': 'sell',
            'size': size,
            'price': price,
            'entry_price': entry_price,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'balance': self.portfolio['balance_usdt']
        }
    
    def close_position(self, symbol: str, current_price: float) -> Dict:
        """Close entire position at market price"""
        if symbol not in self.portfolio['positions']:
            return {'success': False, 'error': 'No position'}
        
        position = self.portfolio['positions'][symbol]
        return self._execute_sell(symbol, position['size'], current_price)
    
    def close_all_positions(self, current_prices: Dict[str, float]) -> Dict:
        """Close all open positions"""
        results = []
        
        for symbol in list(self.portfolio['positions'].keys()):
            if symbol in current_prices:
                result = self.close_position(symbol, current_prices[symbol])
                results.append(result)
        
        return {
            'success': True,
            'closed_positions': len(results),
            'results': results
        }
    
    def reset(self) -> bool:
        """Reset demo account to $10,000"""
        try:
            success = reset_demo_portfolio(self.user_id)
            
            if success:
                # Reload portfolio
                self.portfolio = self._load_portfolio()
                logger.info(f"Demo portfolio reset: {self.user_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Reset error: {e}")
            return False
    
    def _save_portfolio(self):
        """Save portfolio to database"""
        try:
            update_demo_portfolio(self.user_id, self.portfolio)
        except Exception as e:
            logger.error(f"Portfolio save error: {e}")
    
    def get_stats(self) -> Dict:
        """Get trading statistics"""
        total_trades = self.portfolio['total_trades']
        
        if total_trades == 0:
            win_rate = 0.0
        else:
            win_rate = (self.portfolio['winning_trades'] / total_trades) * 100
        
        return {
            'balance': self.portfolio['balance_usdt'],
            'total_pnl': self.portfolio['total_pnl'],
            'total_trades': total_trades,
            'winning_trades': self.portfolio['winning_trades'],
            'losing_trades': self.portfolio['losing_trades'],
            'win_rate': win_rate,
            'open_positions': len(self.portfolio['positions']),
            'recent_trades': self.portfolio['trades'][-10:]  # Last 10 trades
        }


class DemoExchange:
    """
    Wrapper that makes bots think they're using a real exchange,
    but actually using DemoMode
    
    This allows ALL existing bots to work in demo mode
    WITHOUT changing their code!
    """
    
    def __init__(self, user_id: str):
        self.demo = DemoMode(user_id)
        self.name = "Demo Exchange"
    
    def create_order(self, symbol: str, side: str, amount: float, **kwargs) -> Dict:
        """
        Create order (compatible with exchange API)
        
        This method signature matches real exchange APIs,
        so bots can use it without modifications
        """
        # Get current price (in real implementation, fetch from market)
        # For now, using a placeholder
        price = kwargs.get('price', self._get_market_price(symbol))
        
        return self.demo.execute_order(symbol, side, amount, price)
    
    def create_market_order(self, symbol: str, side: str, amount: float) -> Dict:
        """Create market order"""
        price = self._get_market_price(symbol)
        return self.demo.execute_order(symbol, side, amount, price, 'market')
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float
    ) -> Dict:
        """Create limit order"""
        return self.demo.execute_order(symbol, side, amount, price, 'limit')
    
    def get_balance(self, currency: str = 'USDT') -> float:
        """Get balance for currency"""
        if currency == 'USDT':
            return self.demo.get_balance()
        else:
            # Check if we have position in this currency
            positions = self.demo.get_positions()
            for symbol, pos in positions.items():
                if symbol.startswith(currency):
                    return pos['size']
            return 0.0
    
    def get_positions(self) -> Dict:
        """Get all positions"""
        return self.demo.get_positions()
    
    def close_position(self, symbol: str) -> Dict:
        """Close position"""
        price = self._get_market_price(symbol)
        return self.demo.close_position(symbol, price)
    
    def _get_market_price(self, symbol: str) -> float:
        """
        Get current market price
        
        In real implementation, this would fetch from exchange API.
        For demo, we can use a simple placeholder or cached prices.
        """
        # Placeholder prices (in real implementation, fetch live data)
        default_prices = {
            'BTC/USDT': 43000.0,
            'ETH/USDT': 2300.0,
            'SOL/USDT': 100.0,
            'BNB/USDT': 310.0
        }
        
        return default_prices.get(symbol, 1.0)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create demo mode for user
    demo = DemoMode('user_123')
    
    # Check balance
    print(f"Balance: ${demo.get_balance()}")
    
    # Execute demo trade
    result = demo.execute_order('BTC/USDT', 'buy', 0.1, 43000)
    print(f"Buy result: {result}")
    
    # Check positions
    print(f"Positions: {demo.get_positions()}")
    
    # Sell
    result = demo.execute_order('BTC/USDT', 'sell', 0.1, 44000)
    print(f"Sell result: {result}")
    
    # Stats
    print(f"Stats: {demo.get_stats()}")
