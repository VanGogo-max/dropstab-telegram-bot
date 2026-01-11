"""
signal_grid_bot.py - Telegram Signal Follower with Grid Entry/Exit
Safer implementation with lower leverage and grid strategy
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class SignalGridBot:
    """
    Telegram signal follower with grid entry/exit strategy
    
    Features:
    - Follows Telegram signals (e.g., "BTC LONG", "ETH SHORT")
    - Grid entry: splits entry into 5 levels
    - Grid exit: 5 TP zones (20%, 20%, 20%, 20%, 20%)
    - Emergency stop loss (15%)
    - Lower leverage (2x-5x vs original 10-50x)
    - Volatility-based grid spacing
    
    Safety improvements over original:
    - Max leverage capped at 5x (configurable)
    - Emergency stop loss always set
    - Position sizing based on account risk
    - Grid entry reduces average entry price
    """
    
    def __init__(
        self,
        user_id: str,
        exchange,
        leverage: int = 3,
        risk_per_trade_percent: float = 2.0,
        grid_levels: int = 5
    ):
        self.user_id = user_id
        self.exchange = exchange
        self.leverage = min(leverage, 5)  # Cap at 5x for safety
        self.risk_per_trade_percent = risk_per_trade_percent
        self.grid_levels = grid_levels
        
        # Active positions
        self.positions = {}
        
        logger.info(
            f"Signal Grid Bot initialized: "
            f"Leverage={self.leverage}x, Risk={self.risk_per_trade_percent}%"
        )
    
    def process_signal(self, signal_text: str) -> Optional[Dict]:
        """
        Parse and execute Telegram signal
        
        Args:
            signal_text: Raw signal text (e.g., "BTC LONG", "ETH SHORT")
        
        Returns:
            Execution result or None if invalid signal
        """
        # Parse signal
        parsed = self._parse_signal(signal_text)
        
        if not parsed:
            logger.warning(f"Failed to parse signal: {signal_text}")
            return None
        
        # Validate signal
        if not self._validate_signal(parsed):
            logger.warning(f"Invalid signal: {parsed}")
            return None
        
        # Execute with grid entry
        result = self._execute_grid_entry(parsed)
        
        return result
    
    def _parse_signal(self, text: str) -> Optional[Dict]:
        """
        Parse signal text
        
        Supported formats:
        - "BTC LONG"
        - "ETH SHORT"
        - "BTC/USDT LONG"
        - "BTCUSDT LONG"
        """
        text = text.upper().strip()
        
        # Try to extract symbol and direction
        # Pattern 1: "BTC LONG" or "ETH SHORT"
        match = re.search(r'(BTC|ETH|SOL|BNB|MATIC|AVAX|DOT|LINK|UNI|AAVE)\s+(LONG|SHORT)', text)
        
        if match:
            symbol = match.group(1)
            direction = match.group(2).lower()
            
            # Format as trading pair
            if '/' not in symbol:
                symbol = f"{symbol}/USDT"
            
            return {
                'symbol': symbol,
                'direction': direction,
                'raw_text': text,
                'confidence': 0.8,  # High confidence for clear format
                'timestamp': datetime.now()
            }
        
        # Pattern 2: "BTC/USDT LONG"
        match = re.search(r'([A-Z]+/[A-Z]+)\s+(LONG|SHORT)', text)
        
        if match:
            return {
                'symbol': match.group(1),
                'direction': match.group(2).lower(),
                'raw_text': text,
                'confidence': 0.9,
                'timestamp': datetime.now()
            }
        
        # Could not parse
        return None
    
    def _validate_signal(self, signal: Dict) -> bool:
        """Validate parsed signal"""
        # Check required fields
        if not signal.get('symbol') or not signal.get('direction'):
            return False
        
        # Check direction
        if signal['direction'] not in ['long', 'short']:
            return False
        
        # Check confidence threshold
        if signal.get('confidence', 0) < 0.5:
            return False
        
        # Check if already have position for this symbol
        if signal['symbol'] in self.positions:
            logger.warning(f"Already have position for {signal['symbol']}")
            return False
        
        return True
    
    def _execute_grid_entry(self, signal: Dict) -> Dict:
        """
        Execute grid entry strategy
        
        Splits entry into 5 levels:
        - Level 1: Current price
        - Level 2: -0.5% from current
        - Level 3: -1.0% from current
        - Level 4: -1.5% from current
        - Level 5: -2.0% from current
        
        Each level: 20% of position size
        """
        symbol = signal['symbol']
        direction = signal['direction']
        
        try:
            # Get current price
            current_price = self._get_market_price(symbol)
            
            if not current_price:
                return {'success': False, 'error': 'Could not fetch price'}
            
            # Calculate position size
            account_balance = self.exchange.get_balance('USDT')
            position_size_usdt = account_balance * (self.risk_per_trade_percent / 100)
            
            # Apply leverage
            position_size_usdt *= self.leverage
            
            # Calculate base currency amount
            total_amount = position_size_usdt / current_price
            amount_per_level = total_amount / self.grid_levels
            
            # Grid entry prices (adjust based on volatility in real implementation)
            grid_percentages = [-0.0, -0.5, -1.0, -1.5, -2.0]  # Percentage from current
            
            entries = []
            total_cost = 0
            
            for i, pct in enumerate(grid_percentages):
                entry_price = current_price * (1 + pct / 100)
                
                # Execute order
                order_result = self.exchange.create_limit_order(
                    symbol=symbol,
                    side='buy' if direction == 'long' else 'sell',
                    amount=amount_per_level,
                    price=entry_price
                )
                
                if order_result.get('success'):
                    entries.append({
                        'level': i + 1,
                        'price': entry_price,
                        'amount': amount_per_level,
                        'order_id': order_result.get('order_id')
                    })
                    total_cost += amount_per_level * entry_price
                else:
                    logger.error(f"Grid level {i+1} failed: {order_result}")
            
            if not entries:
                return {'success': False, 'error': 'No grid levels executed'}
            
            # Calculate average entry price
            avg_entry_price = total_cost / (amount_per_level * len(entries))
            
            # Set stop loss (15% from average entry)
            stop_loss_price = avg_entry_price * (0.85 if direction == 'long' else 1.15)
            
            # Set take profit levels (5 levels, 20% each)
            tp_levels = self._calculate_tp_levels(avg_entry_price, direction)
            
            # Save position
            self.positions[symbol] = {
                'direction': direction,
                'entries': entries,
                'avg_entry_price': avg_entry_price,
                'total_amount': amount_per_level * len(entries),
                'stop_loss': stop_loss_price,
                'take_profits': tp_levels,
                'filled_levels': len(entries),
                'closed_levels': 0,
                'timestamp': datetime.now()
            }
            
            logger.info(
                f"Grid entry executed: {symbol} {direction.upper()}, "
                f"Avg entry: ${avg_entry_price:.2f}, "
                f"Levels: {len(entries)}/{self.grid_levels}"
            )
            
            return {
                'success': True,
                'symbol': symbol,
                'direction': direction,
                'avg_entry_price': avg_entry_price,
                'entries': entries,
                'stop_loss': stop_loss_price,
                'take_profits': tp_levels
            }
        
        except Exception as e:
            logger.error(f"Grid entry error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_tp_levels(self, entry_price: float, direction: str) -> List[Dict]:
        """
        Calculate take profit levels
        
        5 TP levels with progressive targets:
        TP1: +1% (20% position)
        TP2: +2% (20% position)
        TP3: +3% (20% position)
        TP4: +5% (20% position)
        TP5: +8% (20% position)
        """
        tp_percentages = [1.0, 2.0, 3.0, 5.0, 8.0]
        
        tp_levels = []
        
        for i, pct in enumerate(tp_percentages):
            if direction == 'long':
                tp_price = entry_price * (1 + pct / 100)
            else:  # short
                tp_price = entry_price * (1 - pct / 100)
            
            tp_levels.append({
                'level': i + 1,
                'price': tp_price,
                'percentage': 20,  # 20% of position
                'filled': False
            })
        
        return tp_levels
    
    def monitor_positions(self) -> List[Dict]:
        """
        Monitor open positions and execute TP/SL
        
        Should be called periodically (e.g., every minute)
        """
        results = []
        
        for symbol, position in list(self.positions.items()):
            # Get current price
            current_price = self._get_market_price(symbol)
            
            if not current_price:
                continue
            
            # Check stop loss
            if self._check_stop_loss(symbol, position, current_price):
                result = self._execute_stop_loss(symbol, position, current_price)
                results.append(result)
                continue
            
            # Check take profit levels
            tp_result = self._check_take_profits(symbol, position, current_price)
            if tp_result:
                results.append(tp_result)
        
        return results
    
    def _check_stop_loss(self, symbol: str, position: Dict, current_price: float) -> bool:
        """Check if stop loss hit"""
        direction = position['direction']
        stop_loss = position['stop_loss']
        
        if direction == 'long':
            return current_price <= stop_loss
        else:  # short
            return current_price >= stop_loss
    
    def _execute_stop_loss(self, symbol: str, position: Dict, current_price: float) -> Dict:
        """Execute stop loss - close entire position"""
        try:
            # Close position
            close_result = self.exchange.close_position(symbol)
            
            # Calculate P&L
            entry_price = position['avg_entry_price']
            amount = position['total_amount']
            
            if position['direction'] == 'long':
                pnl = (current_price - entry_price) * amount
            else:
                pnl = (entry_price - current_price) * amount
            
            # Remove from positions
            del self.positions[symbol]
            
            logger.warning(
                f"STOP LOSS HIT: {symbol}, "
                f"Entry: ${entry_price:.2f}, Exit: ${current_price:.2f}, "
                f"P&L: ${pnl:.2f}"
            )
            
            return {
                'type': 'stop_loss',
                'symbol': symbol,
                'pnl': pnl,
                'entry_price': entry_price,
                'exit_price': current_price
            }
        
        except Exception as e:
            logger.error(f"Stop loss execution error: {e}")
            return {'type': 'stop_loss', 'error': str(e)}
    
    def _check_take_profits(self, symbol: str, position: Dict, current_price: float) -> Optional[Dict]:
        """Check and execute take profit levels"""
        direction = position['direction']
        tp_levels = position['take_profits']
        
        for tp in tp_levels:
            if tp['filled']:
                continue
            
            # Check if TP hit
            tp_hit = False
            
            if direction == 'long':
                tp_hit = current_price >= tp['price']
            else:  # short
                tp_hit = current_price <= tp['price']
            
            if tp_hit:
                # Execute partial close
                close_amount = position['total_amount'] * (tp['percentage'] / 100)
                
                try:
                    # Close partial position
                    result = self.exchange.create_market_order(
                        symbol=symbol,
                        side='sell' if direction == 'long' else 'buy',
                        amount=close_amount
                    )
                    
                    # Mark TP as filled
                    tp['filled'] = True
                    position['closed_levels'] += 1
                    
                    # Calculate P&L for this level
                    entry_price = position['avg_entry_price']
                    
                    if direction == 'long':
                        pnl = (current_price - entry_price) * close_amount
                    else:
                        pnl = (entry_price - current_price) * close_amount
                    
                    logger.info(
                        f"TP{tp['level']} HIT: {symbol}, "
                        f"Price: ${current_price:.2f}, P&L: ${pnl:.2f}"
                    )
                    
                    # If all TPs filled, remove position
                    if position['closed_levels'] >= len(tp_levels):
                        del self.positions[symbol]
                    
                    return {
                        'type': 'take_profit',
                        'symbol': symbol,
                        'level': tp['level'],
                        'pnl': pnl,
                        'exit_price': current_price
                    }
                
                except Exception as e:
                    logger.error(f"TP execution error: {e}")
        
        return None
    
    def _get_market_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price
        
        In real implementation, fetch from exchange API
        """
        try:
            # Placeholder - in real implementation, use exchange API
            default_prices = {
                'BTC/USDT': 43000.0,
                'ETH/USDT': 2300.0,
                'SOL/USDT': 100.0,
                'BNB/USDT': 310.0
            }
            
            return default_prices.get(symbol, None)
        
        except Exception as e:
            logger.error(f"Price fetch error: {e}")
            return None
    
    def get_active_positions(self) -> Dict:
        """Get all active positions"""
        return self.positions
    
    def close_all_positions(self) -> List[Dict]:
        """Emergency close all positions"""
        results = []
        
        for symbol in list(self.positions.keys()):
            try:
                result = self.exchange.close_position(symbol)
                results.append({
                    'symbol': symbol,
                    'result': result
                })
                del self.positions[symbol]
            except Exception as e:
                logger.error(f"Close error for {symbol}: {e}")
        
        return results


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Mock exchange for testing
    class MockExchange:
        def get_balance(self, currency):
            return 10000.0
        
        def create_limit_order(self, symbol, side, amount, price):
            return {'success': True, 'order_id': 'mock_123'}
        
        def create_market_order(self, symbol, side, amount):
            return {'success': True, 'order_id': 'mock_456'}
        
        def close_position(self, symbol):
            return {'success': True}
    
    # Create bot
    bot = SignalGridBot(
        user_id='user_123',
        exchange=MockExchange(),
        leverage=3,
        risk_per_trade_percent=2.0
    )
    
    # Process signal
    result = bot.process_signal("BTC LONG")
    print(f"Signal result: {result}")
    
    # Monitor positions
    monitor_results = bot.monitor_positions()
    print(f"Monitor results: {monitor_results}")
          
