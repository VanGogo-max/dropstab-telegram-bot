"""
Risk Manager - Position Sizing & Risk Control
Manages daily loss limits, position sizes, and risk per trade
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from database import get_connection

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Central risk management system
    - Daily loss limits
    - Position sizing
    - Max concurrent positions
    - Risk per trade calculations
    """
    
    def __init__(self):
        self.max_daily_loss = 100.0  # USD
        self.max_position_size = 1000.0  # USD
        self.max_open_positions = 3
        self.default_risk_per_trade = 0.02  # 2% of capital
        
        logger.info("Risk Manager initialized")
    
    def can_open_position(self, user_id: int) -> bool:
        """Check if user can open new position"""
        try:
            # 1. Check daily loss limit
            daily_loss = self.get_daily_loss(user_id)
            if daily_loss >= self.max_daily_loss:
                logger.warning(f"User {user_id} hit daily loss limit: ${daily_loss:.2f}")
                return False
            
            # 2. Check max open positions
            open_positions = self.get_open_positions_count(user_id)
            if open_positions >= self.max_open_positions:
                logger.warning(f"User {user_id} has max positions: {open_positions}")
                return False
            
            # 3. Check subscription status
            if not self.has_active_subscription(user_id):
                logger.warning(f"User {user_id} has no active subscription")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Risk check error: {e}")
            return False
    
    def get_daily_loss(self, user_id: int) -> float:
        """Calculate user's loss for today"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().date()
            
            cursor.execute("""
                SELECT COALESCE(SUM(profit_loss), 0)
                FROM trades
                WHERE user_id = ?
                AND DATE(closed_at) = ?
                AND profit_loss < 0
            """, (str(user_id), today))
            
            result = cursor.fetchone()
            daily_loss = abs(result[0]) if result else 0
            
            conn.close()
            return daily_loss
            
        except Exception as e:
            logger.error(f"Daily loss calculation error: {e}")
            return 0
    
    def get_open_positions_count(self, user_id: int) -> int:
        """Count user's open positions"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM trades
                WHERE user_id = ?
                AND status = 'open'
            """, (str(user_id),))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Open positions count error: {e}")
            return 0
    
    def has_active_subscription(self, user_id: int) -> bool:
        """Check if user has active subscription"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT subscription_status, subscription_expires_at
                FROM users
                WHERE user_id = ?
            """, (str(user_id),))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
            
            status, expires_at = result
            
            if status != 'active':
                conn.close()
                return False
            
            # Check expiration
            if expires_at:
                expiry = datetime.fromisoformat(expires_at)
                if expiry < datetime.now():
                    conn.close()
                    return False
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Subscription check error: {e}")
            return False
    
    def calculate_position_size(
        self,
        capital: float,
        risk_percent: float,
        entry_price: float,
        stop_loss_price: float
    ) -> float:
        """
        Calculate position size based on risk
        
        Args:
            capital: Total capital
            risk_percent: Risk per trade (0.02 = 2%)
            entry_price: Entry price
            stop_loss_price: Stop loss price
        
        Returns:
            Position size in base currency
        """
        try:
            risk_amount = capital * risk_percent
            price_difference = abs(entry_price - stop_loss_price)
            
            if price_difference == 0:
                logger.warning("Stop loss equals entry price")
                return 0
            
            position_size = risk_amount / price_difference
            
            # Cap at max position size
            max_units = self.max_position_size / entry_price
            position_size = min(position_size, max_units)
            
            logger.info(f"Position size calculated: {position_size:.4f} units")
            return position_size
            
        except Exception as e:
            logger.error(f"Position size calculation error: {e}")
            return 0
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        side: str,
        atr: float,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Calculate stop loss based on ATR
        
        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'
            atr: Average True Range
            atr_multiplier: ATR multiplier for stop distance
        
        Returns:
            Stop loss price
        """
        try:
            stop_distance = atr * atr_multiplier
            
            if side == 'buy':
                stop_loss = entry_price - stop_distance
            else:  # sell
                stop_loss = entry_price + stop_distance
            
            logger.info(f"Stop loss calculated: {stop_loss:.2f}")
            return stop_loss
            
        except Exception as e:
            logger.error(f"Stop loss calculation error: {e}")
            return entry_price * 0.95 if side == 'buy' else entry_price * 1.05
    
    def get_risk_metrics(self, user_id: int) -> Dict:
        """Get user's current risk metrics"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Get all closed trades
            cursor.execute("""
                SELECT profit_loss, profit_loss_percent
                FROM trades
                WHERE user_id = ?
                AND status = 'closed'
                ORDER BY closed_at DESC
                LIMIT 100
            """, (str(user_id),))
            
            trades = cursor.fetchall()
            conn.close()
            
            if not trades:
                return {
                    'total_trades': 0,
                    'win_rate': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'profit_factor': 0,
                    'max_drawdown': 0
                }
            
            wins = [t for t in trades if t[0] > 0]
            losses = [t for t in trades if t[0] < 0]
            
            win_rate = len(wins) / len(trades) if trades else 0
            avg_win = sum(t[0] for t in wins) / len(wins) if wins else 0
            avg_loss = sum(t[0] for t in losses) / len(losses) if losses else 0
            
            total_wins = sum(t[0] for t in wins)
            total_losses = abs(sum(t[0] for t in losses))
            profit_factor = total_wins / total_losses if total_losses > 0 else 0
            
            # Calculate max drawdown
            cumulative_pnl = 0
            peak = 0
            max_drawdown = 0
            
            for trade in trades:
                cumulative_pnl += trade[0]
                if cumulative_pnl > peak:
                    peak = cumulative_pnl
                drawdown = peak - cumulative_pnl
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            return {
                'total_trades': len(trades),
                'win_rate': round(win_rate * 100, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'profit_factor': round(profit_factor, 2),
                'max_drawdown': round(max_drawdown, 2)
            }
            
        except Exception as e:
            logger.error(f"Risk metrics error: {e}")
            return {}
    
    def validate_trade(
        self,
        user_id: int,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Tuple[bool, str]:
        """
        Validate trade before execution
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # 1. Check if can open position
            if not self.can_open_position(user_id):
                return False, "Cannot open position: risk limits exceeded"
            
            # 2. Check position size
            position_value = quantity * price
            if position_value > self.max_position_size:
                return False, f"Position size ${position_value:.2f} exceeds limit ${self.max_position_size}"
            
            # 3. Check minimum size
            if position_value < 10:
                return False, "Position size too small (min $10)"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Trade validation error: {e}")
            return False, str(e)
    
    def update_limits(
        self,
        max_daily_loss: Optional[float] = None,
        max_position_size: Optional[float] = None,
        max_open_positions: Optional[int] = None
    ):
        """Update risk limits"""
        if max_daily_loss is not None:
            self.max_daily_loss = max_daily_loss
            logger.info(f"Max daily loss updated: ${max_daily_loss}")
        
        if max_position_size is not None:
            self.max_position_size = max_position_size
            logger.info(f"Max position size updated: ${max_position_size}")
        
        if max_open_positions is not None:
            self.max_open_positions = max_open_positions
            logger.info(f"Max open positions updated: {max_open_positions}")


# Global instance
risk_manager = RiskManager()
