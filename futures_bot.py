"""
Futures Bot - Turtle Trading Strategy
Exchange: Hyperliquid (Arbitrum Network)
Strategy: Conservative Turtle Trading with Pyramiding
Max Leverage: 3x | Risk per trade: 2%
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass

from exchange_api import exchange_api
from risk_manager import risk_manager
from database import db_session, Trade, BotStatus
from email_service import email_service
from config import *

logger = logging.getLogger(__name__)


@dataclass
class TurtleUnit:
    """Single pyramid unit"""
    entry_price: float
    size: float
    stop_loss: float
    entry_time: datetime


class TurtleStrategy:
    """Turtle Trading Strategy Implementation"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.breakout_period = TURTLE_BREAKOUT_PERIOD  # 55 days
        self.exit_period = TURTLE_EXIT_PERIOD  # 10 days
        self.atr_period = TURTLE_ATR_PERIOD  # 20 days
        self.max_units = TURTLE_MAX_UNITS  # 4 positions
        self.unit_risk = TURTLE_UNIT_RISK  # 1% per unit
    
    def calculate_atr(self, candles: List[Dict]) -> float:
        """Calculate Average True Range (volatility)"""
        if len(candles) < self.atr_period:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i]['high']
            low = candles[i]['low']
            prev_close = candles[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        # ATR = average of last N true ranges
        atr = np.mean(true_ranges[-self.atr_period:])
        return float(atr)
    
    def check_breakout(self, candles: List[Dict], direction: str) -> bool:
        """Check if price breaks out of channel"""
        if len(candles) < self.breakout_period + 1:
            return False
        
        current_price = candles[-1]['close']
        historical = candles[-self.breakout_period-1:-1]
        
        if direction == 'long':
            highest = max(c['high'] for c in historical)
            return current_price > highest
        else:
            lowest = min(c['low'] for c in historical)
            return current_price < lowest
        
        return False
    
    def check_exit_signal(self, candles: List[Dict], direction: str) -> bool:
        """Check exit signal (10-day low for longs)"""
        if len(candles) < self.exit_period + 1:
            return False
        
        current_price = candles[-1]['close']
        historical = candles[-self.exit_period-1:-1]
        
        if direction == 'long':
            lowest = min(c['low'] for c in historical)
            return current_price < lowest
        else:
            highest = max(c['high'] for c in historical)
            return current_price > highest
        
        return False
    
    def calculate_position_size(self, account_balance: float, 
                                atr: float, price: float) -> float:
        """Calculate position size based on ATR"""
        if atr == 0:
            return 0.0
        
        # Risk amount per unit
        risk_amount = account_balance * self.unit_risk
        
        # Position size = Risk / (2 * ATR)
        # 2 ATR = stop loss distance
        size = risk_amount / (2 * atr)
        
        # Convert to contracts
        contracts = size / price
        
        return round(contracts, 3)


class FuturesBot:
    """Futures Trading Bot with Turtle Strategy"""
    
    def __init__(self, user_id: int, symbol: str = 'BTC/USDT'):
        self.user_id = user_id
        self.symbol = symbol
        self.exchange = exchange_api.get_futures_exchange()
        self.strategy = TurtleStrategy(symbol)
        
        # Active positions (pyramiding)
        self.units: List[TurtleUnit] = []
        self.direction: Optional[str] = None  # 'long' or 'short'
        
        # Performance tracking
        self.consecutive_losses = 0
        self.total_profit = 0.0
        self.peak_balance = 0.0
        
        # Risk limits
        self.max_drawdown = 0.10  # 10%
        self.emergency_stop = False
        
        logger.info(f"Futures Bot initialized: {symbol} (Hyperliquid/Arbitrum)")
    
    def get_candles(self, timeframe: str = '1d', limit: int = 100) -> List[Dict]:
        """Fetch historical candles (mock for now)"""
        # TODO: Implement actual Hyperliquid candle fetching
        # For now return mock data
        return []
    
    def get_account_balance(self) -> float:
        """Get futures account balance"""
        balance = self.exchange.get_futures_balance()
        return float(balance)
    
    def open_position(self, direction: str, size: float, 
                     atr: float, price: float) -> bool:
        """Open new position (first unit)"""
        try:
            # Set conservative leverage
            self.exchange.set_leverage(self.symbol, FUTURES_MAX_LEVERAGE)
            
            # Calculate stop loss (2 ATR)
            if direction == 'long':
                stop_loss = price - (2 * atr)
                side = 'buy'
            else:
                stop_loss = price + (2 * atr)
                side = 'sell'
            
            # Place order
            result = self.exchange.create_futures_order(
                symbol=self.symbol,
                side=side,
                size=size,
                leverage=FUTURES_MAX_LEVERAGE
            )
            
            if 'error' in result:
                logger.error(f"Order failed: {result['error']}")
                return False
            
            # Save unit
            unit = TurtleUnit(
                entry_price=price,
                size=size,
                stop_loss=stop_loss,
                entry_time=datetime.utcnow()
            )
            self.units.append(unit)
            self.direction = direction
            
            # Log trade
            self._log_trade('OPEN', price, size, stop_loss)
            
            # Send notification
            email_service.send_trade_alert(
                self.user_id,
                f"🐢 Turtle Entry: {direction.upper()} {self.symbol}",
                f"Price: ${price:,.2f} | Size: {size} | SL: ${stop_loss:,.2f}"
            )
            
            logger.info(f"Position opened: {direction} {size} @ {price}")
            return True
            
        except Exception as e:
            logger.error(f"Open position error: {e}")
            return False
    
    def add_pyramid_unit(self, atr: float, current_price: float) -> bool:
        """Add pyramid position (0.5 ATR profit)"""
        if len(self.units) >= self.max_units:
            return False
        
        last_unit = self.units[-1]
        
        # Check if price moved 0.5 ATR in profit direction
        if self.direction == 'long':
            profit_distance = current_price - last_unit.entry_price
            if profit_distance < (0.5 * atr):
                return False
        else:
            profit_distance = last_unit.entry_price - current_price
            if profit_distance < (0.5 * atr):
                return False
        
        # Calculate new unit size
        balance = self.get_account_balance()
        size = self.strategy.calculate_position_size(balance, atr, current_price)
        
        if size == 0:
            return False
        
        # Place order
        side = 'buy' if self.direction == 'long' else 'sell'
        result = self.exchange.create_futures_order(
            symbol=self.symbol,
            side=side,
            size=size,
            leverage=FUTURES_MAX_LEVERAGE
        )
        
        if 'error' in result:
            return False
        
        # Calculate new stop loss (2 ATR from new entry)
        if self.direction == 'long':
            stop_loss = current_price - (2 * atr)
        else:
            stop_loss = current_price + (2 * atr)
        
        # Save unit
        unit = TurtleUnit(
            entry_price=current_price,
            size=size,
            stop_loss=stop_loss,
            entry_time=datetime.utcnow()
        )
        self.units.append(unit)
        
        logger.info(f"Pyramid added: Unit {len(self.units)} @ {current_price}")
        return True
    
    def close_all_positions(self, reason: str, current_price: float):
        """Close all open units"""
        if not self.units:
            return
        
        total_size = sum(u.size for u in self.units)
        
        # Place closing order
        side = 'sell' if self.direction == 'long' else 'buy'
        result = self.exchange.create_futures_order(
            symbol=self.symbol,
            side=side,
            size=total_size,
            reduce_only=True
        )
        
        # Calculate P&L
        avg_entry = np.mean([u.entry_price for u in self.units])
        if self.direction == 'long':
            pnl = (current_price - avg_entry) * total_size
        else:
            pnl = (avg_entry - current_price) * total_size
        
        self.total_profit += pnl
        
        # Track losses
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Log trade
        self._log_trade('CLOSE', current_price, total_size, 0, pnl)
        
        # Notification
        email_service.send_trade_alert(
            self.user_id,
            f"🐢 Turtle Exit: {reason}",
            f"P&L: ${pnl:,.2f} | Price: ${current_price:,.2f}"
        )
        
        # Reset
        self.units = []
        self.direction = None
        
        logger.info(f"Position closed: {reason} | P&L: ${pnl:,.2f}")
    
    def check_emergency_stop(self) -> bool:
        """Check if emergency stop triggered"""
        # 3 consecutive losses
        if self.consecutive_losses >= 3:
            logger.warning("Emergency stop: 3 consecutive losses")
            self.emergency_stop = True
            return True
        
        # Max drawdown (10%)
        balance = self.get_account_balance()
        if self.peak_balance > 0:
            drawdown = (self.peak_balance - balance) / self.peak_balance
            if drawdown > self.max_drawdown:
                logger.warning(f"Emergency stop: {drawdown:.1%} drawdown")
                self.emergency_stop = True
                return True
        else:
            self.peak_balance = balance
        
        # Update peak
        if balance > self.peak_balance:
            self.peak_balance = balance
        
        return False
    
    def run(self):
        """Main trading loop"""
        if self.emergency_stop:
            logger.warning("Bot stopped due to emergency conditions")
            return
        
        # Check emergency stop
        if self.check_emergency_stop():
            if self.units:
                price = self.exchange.get_mark_price(self.symbol)
                self.close_all_positions("EMERGENCY_STOP", price)
            return
        
        # Get market data
        candles = self.get_candles(limit=100)
        if len(candles) < self.strategy.breakout_period:
            logger.info("Not enough historical data")
            return
        
        current_price = candles[-1]['close']
        atr = self.strategy.calculate_atr(candles)
        
        # If no position - check for entry
        if not self.units:
            # Check long breakout
            if self.strategy.check_breakout(candles, 'long'):
                balance = self.get_account_balance()
                size = self.strategy.calculate_position_size(balance, atr, current_price)
                if size > 0:
                    self.open_position('long', size, atr, current_price)
            
            # Check short breakout
            elif self.strategy.check_breakout(candles, 'short'):
                balance = self.get_account_balance()
                size = self.strategy.calculate_position_size(balance, atr, current_price)
                if size > 0:
                    self.open_position('short', size, atr, current_price)
        
        # If position exists - manage it
        else:
            # Check exit signal
            if self.strategy.check_exit_signal(candles, self.direction):
                self.close_all_positions("EXIT_SIGNAL", current_price)
                return
            
            # Check stop loss (any unit)
            for unit in self.units:
                if self.direction == 'long' and current_price <= unit.stop_loss:
                    self.close_all_positions("STOP_LOSS", current_price)
                    return
                elif self.direction == 'short' and current_price >= unit.stop_loss:
                    self.close_all_positions("STOP_LOSS", current_price)
                    return
            
            # Check for pyramid opportunity
            if len(self.units) < self.strategy.max_units:
                self.add_pyramid_unit(atr, current_price)
    
    def _log_trade(self, action: str, price: float, size: float, 
                   stop_loss: float, pnl: float = 0):
        """Log trade to database"""
        try:
            trade = Trade(
                user_id=self.user_id,
                bot_type='futures',
                symbol=self.symbol,
                action=action,
                price=price,
                amount=size,
                timestamp=datetime.utcnow(),
                profit_loss=pnl
            )
            db_session.add(trade)
            db_session.commit()
        except Exception as e:
            logger.error(f"Trade log error: {e}")
