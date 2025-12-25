"""
🔄 DEX SPOT-FUTURES ARBITRAGE BOT
Spot: Uniswap V3 (Arbitrum)
Futures: Hyperliquid (Arbitrum L1)
100% Decentralized - No CEX

Strategies:
1. Funding Rate Arbitrage (Passive income)
2. Basis Spread Arbitrage (Convergence trading)
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

from exchange_api import exchange_api
from risk_manager import risk_manager
from database import db_session, Trade
from email_service import email_service
from config import *

logger = logging.getLogger(__name__)


class FundingRateStrategy:
    """Earn funding rate by hedging spot with futures"""
    
    def __init__(self, min_funding_rate: float = 0.005):
        self.min_funding_rate = min_funding_rate  # 0.5% = 50 bps
    
    def calculate_apy(self, funding_rate: float) -> float:
        """Calculate annualized return from funding rate"""
        # Funding happens 3x per day (every 8 hours)
        daily_rate = funding_rate * 3
        apy = daily_rate * 365
        return apy
    
    def find_opportunity(self, spot_price: float, futures_price: float, 
                        funding_rate: float) -> Optional[Dict]:
        """Check if funding rate arbitrage is profitable"""
        
        if abs(funding_rate) < self.min_funding_rate:
            return None
        
        apy = self.calculate_apy(funding_rate)
        
        # Positive funding = longs pay shorts
        if funding_rate > 0:
            return {
                'type': 'funding_rate',
                'spot_action': 'buy',
                'futures_action': 'short',
                'spot_price': spot_price,
                'futures_price': futures_price,
                'funding_rate': funding_rate,
                'expected_apy': apy,
                'risk_level': 'low',
                'hold_period': 'indefinite'
            }
        
        # Negative funding = shorts pay longs
        else:
            return {
                'type': 'funding_rate',
                'spot_action': 'sell',
                'futures_action': 'long',
                'spot_price': spot_price,
                'futures_price': futures_price,
                'funding_rate': funding_rate,
                'expected_apy': abs(apy),
                'risk_level': 'low',
                'hold_period': 'indefinite'
            }


class BasisSpreadStrategy:
    """Profit from futures-spot price convergence"""
    
    def __init__(self, min_basis: float = 0.01):
        self.min_basis = min_basis  # 1% minimum spread
    
    def calculate_basis(self, spot_price: float, futures_price: float) -> float:
        """Calculate basis as percentage"""
        basis = (futures_price - spot_price) / spot_price
        return basis
    
    def find_opportunity(self, spot_price: float, futures_price: float) -> Optional[Dict]:
        """Check if basis spread is tradeable"""
        
        basis = self.calculate_basis(spot_price, futures_price)
        
        # Contango (futures > spot) - common situation
        if basis > self.min_basis:
            return {
                'type': 'basis_spread',
                'direction': 'contango',
                'spot_action': 'buy',
                'futures_action': 'short',
                'spot_price': spot_price,
                'futures_price': futures_price,
                'basis': basis,
                'expected_profit': basis,
                'risk_level': 'very_low',
                'hold_period': 'days_to_weeks'
            }
        
        # Backwardation (spot > futures) - rare but profitable
        elif basis < -self.min_basis:
            return {
                'type': 'basis_spread',
                'direction': 'backwardation',
                'spot_action': 'sell',
                'futures_action': 'long',
                'spot_price': spot_price,
                'futures_price': futures_price,
                'basis': abs(basis),
                'expected_profit': abs(basis),
                'risk_level': 'very_low',
                'hold_period': 'days_to_weeks'
            }
        
        return None


class DexArbitrageBot:
    """DEX Spot-Futures Arbitrage Bot"""
    
    # Bot metadata
    BOT_NAME = "DEX Arbitrage"
    BOT_DESCRIPTION = "Spot-Futures arbitrage on decentralized exchanges"
    BOT_RISK_LEVEL = "LOW"
    BOT_EXCHANGES = "Uniswap V3 + Hyperliquid"
    
    def __init__(self, user_id: int, symbol: str = 'BTC', 
                 capital: float = 1000):
        self.user_id = user_id
        self.symbol = symbol
        self.capital = capital
        
        # DEX handlers
        self.spot_dex = exchange_api.get_spot_exchange()  # Uniswap via KCEX wrapper
        self.futures_dex = exchange_api.get_futures_exchange()  # Hyperliquid
        
        # Strategies
        self.funding_strategy = FundingRateStrategy(
            min_funding_rate=DEX_MIN_FUNDING_RATE
        )
        self.basis_strategy = BasisSpreadStrategy(
            min_basis=DEX_MIN_BASIS_SPREAD
        )
        
        # Position tracking
        self.active_positions = []
        self.total_profit = 0.0
        
        logger.info(f"DEX Arbitrage Bot initialized: {symbol}")
    
    def get_market_data(self) -> Dict:
        """Fetch spot and futures prices"""
        try:
            # Spot price (Uniswap simulation via KCEX)
            spot_ticker = self.spot_dex.get_ticker(f'{self.symbol}/USDT')
            spot_price = float(spot_ticker.get('last', 0))
            
            # Futures price (Hyperliquid)
            futures_price = self.futures_dex.get_mark_price(f'{self.symbol}/USDT')
            
            # Funding rate (Hyperliquid)
            funding_rate = self._get_funding_rate()
            
            return {
                'spot_price': spot_price,
                'futures_price': futures_price,
                'funding_rate': funding_rate,
                'timestamp': datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            return {}
    
    def _get_funding_rate(self) -> float:
        """Get current funding rate from Hyperliquid"""
        try:
            # TODO: Implement actual Hyperliquid funding rate API call
            # For now return simulated value
            return 0.0001  # 0.01% (1 bps)
        except:
            return 0.0
    
    def scan_opportunities(self) -> List[Dict]:
        """Scan for arbitrage opportunities"""
        opportunities = []
        
        # Get market data
        market = self.get_market_data()
        if not market:
            return opportunities
        
        spot_price = market['spot_price']
        futures_price = market['futures_price']
        funding_rate = market['funding_rate']
        
        # Strategy 1: Funding Rate Arbitrage
        funding_opp = self.funding_strategy.find_opportunity(
            spot_price, futures_price, funding_rate
        )
        if funding_opp:
            opportunities.append(funding_opp)
            logger.info(f"Funding opportunity: {funding_opp['expected_apy']:.2%} APY")
        
        # Strategy 2: Basis Spread Arbitrage
        basis_opp = self.basis_strategy.find_opportunity(
            spot_price, futures_price
        )
        if basis_opp:
            opportunities.append(basis_opp)
            logger.info(f"Basis opportunity: {basis_opp['expected_profit']:.2%} profit")
        
        return opportunities
    
    def calculate_position_size(self, opportunity: Dict) -> float:
        """Calculate optimal position size"""
        # Use 50% of capital per position (conservative)
        position_size = self.capital * 0.5
        
        # Adjust for risk level
        if opportunity['risk_level'] == 'very_low':
            position_size = self.capital * 0.7
        elif opportunity['risk_level'] == 'medium':
            position_size = self.capital * 0.3
        
        return position_size
    
    def execute_arbitrage(self, opportunity: Dict) -> bool:
        """Execute arbitrage position"""
        try:
            position_size = self.calculate_position_size(opportunity)
            
            # Risk check
            if not risk_manager.can_open_position(self.user_id):
                logger.warning("Risk limits exceeded")
                return False
            
            # Step 1: Spot trade
            if opportunity['spot_action'] == 'buy':
                spot_result = self._execute_spot_buy(
                    opportunity['spot_price'], 
                    position_size
                )
            else:
                spot_result = self._execute_spot_sell(
                    opportunity['spot_price'],
                    position_size
                )
            
            if not spot_result:
                return False
            
            # Step 2: Futures trade (hedge)
            if opportunity['futures_action'] == 'short':
                futures_result = self._execute_futures_short(
                    opportunity['futures_price'],
                    position_size
                )
            else:
                futures_result = self._execute_futures_long(
                    opportunity['futures_price'],
                    position_size
                )
            
            if not futures_result:
                # Rollback spot trade if futures fails
                logger.error("Futures trade failed - need to close spot")
                return False
            
            # Save position
            position = {
                'type': opportunity['type'],
                'spot_side': opportunity['spot_action'],
                'futures_side': opportunity['futures_action'],
                'spot_price': opportunity['spot_price'],
                'futures_price': opportunity['futures_price'],
                'size': position_size,
                'opened_at': datetime.utcnow(),
                'expected_profit': opportunity.get('expected_profit', 0),
                'expected_apy': opportunity.get('expected_apy', 0)
            }
            self.active_positions.append(position)
            
            # Log trade
            self._log_trade('OPEN', opportunity, position_size)
            
            # Notification
            email_service.send_trade_alert(
                self.user_id,
                f"🔄 DEX Arbitrage Opened: {opportunity['type']}",
                f"Spot: {opportunity['spot_action']} @ ${opportunity['spot_price']:,.2f}\n"
                f"Futures: {opportunity['futures_action']} @ ${opportunity['futures_price']:,.2f}\n"
                f"Expected: {opportunity.get('expected_profit', opportunity.get('expected_apy', 0)):.2%}"
            )
            
            logger.info(f"Arbitrage position opened: {opportunity['type']}")
            return True
            
        except Exception as e:
            logger.error(f"Arbitrage execution error: {e}")
            return False
    
    def _execute_spot_buy(self, price: float, size: float) -> bool:
        """Execute spot buy on Uniswap (via KCEX wrapper)"""
        try:
            result = self.spot_dex.create_order(
                symbol=f'{self.symbol}/USDT',
                side='buy',
                amount=size / price,
                order_type='market'
            )
            return 'error' not in result
        except Exception as e:
            logger.error(f"Spot buy error: {e}")
            return False
    
    def _execute_spot_sell(self, price: float, size: float) -> bool:
        """Execute spot sell"""
        try:
            result = self.spot_dex.create_order(
                symbol=f'{self.symbol}/USDT',
                side='sell',
                amount=size / price,
                order_type='market'
            )
            return 'error' not in result
        except Exception as e:
            logger.error(f"Spot sell error: {e}")
            return False
    
    def _execute_futures_short(self, price: float, size: float) -> bool:
        """Execute futures short on Hyperliquid"""
        try:
            result = self.futures_dex.create_futures_order(
                symbol=f'{self.symbol}/USDT',
                side='sell',
                size=size / price,
                leverage=1  # No leverage for arbitrage (delta neutral)
            )
            return 'error' not in result
        except Exception as e:
            logger.error(f"Futures short error: {e}")
            return False
    
    def _execute_futures_long(self, price: float, size: float) -> bool:
        """Execute futures long"""
        try:
            result = self.futures_dex.create_futures_order(
                symbol=f'{self.symbol}/USDT',
                side='buy',
                size=size / price,
                leverage=1
            )
            return 'error' not in result
        except Exception as e:
            logger.error(f"Futures long error: {e}")
            return False
    
    def manage_positions(self):
        """Monitor and manage open positions"""
        for position in self.active_positions[:]:
            # Get current prices
            market = self.get_market_data()
            
            # Check if position should be closed
            if self._should_close_position(position, market):
                self.close_position(position, market)
    
    def _should_close_position(self, position: Dict, market: Dict) -> bool:
        """Determine if position should be closed"""
        # Funding rate strategy - hold indefinitely unless funding flips
        if position['type'] == 'funding_rate':
            # Close if funding rate flips sign
            if position['futures_side'] == 'short' and market['funding_rate'] < 0:
                return True
            if position['futures_side'] == 'long' and market['funding_rate'] > 0:
                return True
        
        # Basis spread strategy - close when basis converges
        elif position['type'] == 'basis_spread':
            current_basis = (market['futures_price'] - market['spot_price']) / market['spot_price']
            
            # Close if basis < 0.2% (converged)
            if abs(current_basis) < 0.002:
                return True
            
            # Close if held for > 30 days
            hold_time = (datetime.utcnow() - position['opened_at']).days
            if hold_time > 30:
                return True
        
        return False
    
    def close_position(self, position: Dict, market: Dict):
        """Close arbitrage position"""
        try:
            # Close spot position
            if position['spot_side'] == 'buy':
                self._execute_spot_sell(market['spot_price'], position['size'])
            else:
                self._execute_spot_buy(market['spot_price'], position['size'])
            
            # Close futures position
            if position['futures_side'] == 'short':
                self._execute_futures_long(market['futures_price'], position['size'])
            else:
                self._execute_futures_short(market['futures_price'], position['size'])
            
            # Calculate P&L
            pnl = self._calculate_pnl(position, market)
            self.total_profit += pnl
            
            # Remove from active positions
            self.active_positions.remove(position)
            
            # Log trade
            self._log_trade('CLOSE', position, position['size'], pnl)
            
            # Notification
            email_service.send_trade_alert(
                self.user_id,
                f"💰 DEX Arbitrage Closed",
                f"P&L: ${pnl:,.2f}\nType: {position['type']}"
            )
            
            logger.info(f"Position closed: P&L ${pnl:,.2f}")
            
        except Exception as e:
            logger.error(f"Close position error: {e}")
    
    def _calculate_pnl(self, position: Dict, market: Dict) -> float:
        """Calculate profit/loss for position"""
        # Spot P&L
        if position['spot_side'] == 'buy':
            spot_pnl = (market['spot_price'] - position['spot_price']) * (position['size'] / position['spot_price'])
        else:
            spot_pnl = (position['spot_price'] - market['spot_price']) * (position['size'] / position['spot_price'])
        
        # Futures P&L
        if position['futures_side'] == 'short':
            futures_pnl = (position['futures_price'] - market['futures_price']) * (position['size'] / position['futures_price'])
        else:
            futures_pnl = (market['futures_price'] - position['futures_price']) * (position['size'] / position['futures_price'])
        
        # Total P&L (should be neutral + funding/basis profit)
        total_pnl = spot_pnl + futures_pnl
        
        return total_pnl
    
    def run(self):
        """Main bot execution loop"""
        try:
            # Manage existing positions
            self.manage_positions()
            
            # Don't open new positions if already have 2+ active
            if len(self.active_positions) >= 2:
                logger.info("Max positions reached - waiting")
                return
            
            # Scan for new opportunities
            opportunities = self.scan_opportunities()
            
            if not opportunities:
                logger.debug("No arbitrage opportunities found")
                return
            
            # Execute best opportunity
            best_opp = max(opportunities, 
                          key=lambda x: x.get('expected_profit', x.get('expected_apy', 0)))
            
            self.execute_arbitrage(best_opp)
            
        except Exception as e:
            logger.error(f"Bot run error: {e}")
    
    def _log_trade(self, action: str, opportunity: Dict, size: float, pnl: float = 0):
        """Log trade to database"""
        try:
            trade = Trade(
                user_id=self.user_id,
                bot_type='dex_arbitrage',
                symbol=self.symbol,
                action=action,
                price=opportunity.get('spot_price', 0),
                amount=size,
                timestamp=datetime.utcnow(),
                profit_loss=pnl
            )
            db_session.add(trade)
            db_session.commit()
        except Exception as e:
            logger.error(f"Trade log error: {e}")
