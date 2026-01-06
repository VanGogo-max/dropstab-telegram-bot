"""
Unified Strategy Manager
Manages all trading strategies: Liquidity, Turtle, Arbitrage
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from liquidity_strategy_improved import EnhancedLiquidityStrategy
from turtle_strategy import TurtleStrategy
from dex_arbitrage_strategy import (
    PriceArbitrageStrategy,
    FundingRateArbitrageStrategy,
    TriangularArbitrageStrategy
)
from exchange_api import MultiExchangeAPI
from config import *

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Strategy types"""
    LIQUIDITY = "liquidity"
    TURTLE = "turtle"
    PRICE_ARBITRAGE = "price_arbitrage"
    FUNDING_ARBITRAGE = "funding_arbitrage"
    TRIANGULAR_ARBITRAGE = "triangular_arbitrage"


class UnifiedStrategyManager:
    """
    Central manager for all trading strategies
    Handles:
    - Strategy initialization
    - Capital allocation
    - Risk management
    - Performance monitoring
    - Portfolio rebalancing
    """
    
    def __init__(
        self,
        total_capital: float = 10000.0,
        testnet: bool = True
    ):
        self.total_capital = total_capital
        self.testnet = testnet
        
        # Initialize exchange API
        self.exchange_api = MultiExchangeAPI(testnet=testnet)
        
        # Strategy instances
        self.strategies = {}
        
        # Capital allocation (default: balanced)
        self.capital_allocation = {
            StrategyType.LIQUIDITY: 0.20,  # 20% - Active trading
            StrategyType.TURTLE: 0.20,      # 20% - Trend following
            StrategyType.PRICE_ARBITRAGE: 0.30,  # 30% - Low risk
            StrategyType.FUNDING_ARBITRAGE: 0.25,  # 25% - Passive income
            StrategyType.TRIANGULAR_ARBITRAGE: 0.05  # 5% - Experimental
        }
        
        # Performance tracking
        self.performance = {
            'total_pnl': 0.0,
            'total_trades': 0,
            'strategies': {}
        }
        
        # Risk limits
        self.max_daily_loss = MAX_DAILY_LOSS
        self.max_position_size = MAX_POSITION_SIZE
        self.daily_pnl = 0.0
        self.last_reset = datetime.utcnow().date()
        
        logger.info(
            f"Unified Strategy Manager initialized: "
            f"Capital ${total_capital}, Testnet={testnet}"
        )
    
    def initialize_strategies(
        self,
        enabled_strategies: Optional[List[StrategyType]] = None
    ):
        """
        Initialize selected strategies with allocated capital
        """
        if enabled_strategies is None:
            enabled_strategies = list(StrategyType)
        
        for strategy_type in enabled_strategies:
            allocated_capital = self.total_capital * self.capital_allocation[strategy_type]
            
            if strategy_type == StrategyType.LIQUIDITY:
                self.strategies[strategy_type] = EnhancedLiquidityStrategy(
                    initial_capital=allocated_capital,
                    risk_percent=FUTURES_POSITION_RISK * 100
                )
                logger.info(f"✅ Liquidity Strategy initialized: ${allocated_capital:.2f}")
            
            elif strategy_type == StrategyType.TURTLE:
                self.strategies[strategy_type] = TurtleStrategy(
                    initial_capital=allocated_capital,
                    system=TURTLE_SYSTEM,
                    breakout_period=TURTLE_BREAKOUT_PERIOD,
                    exit_period=TURTLE_EXIT_PERIOD,
                    atr_period=TURTLE_ATR_PERIOD,
                    max_units=TURTLE_MAX_UNITS,
                    unit_risk=TURTLE_UNIT_RISK
                )
                logger.info(f"✅ Turtle Strategy initialized: ${allocated_capital:.2f}")
            
            elif strategy_type == StrategyType.PRICE_ARBITRAGE:
                self.strategies[strategy_type] = PriceArbitrageStrategy(
                    api=self.exchange_api,
                    min_profit_pct=PRICE_ARB_MIN_PROFIT_PCT
                )
                logger.info(f"✅ Price Arbitrage initialized: ${allocated_capital:.2f}")
            
            elif strategy_type == StrategyType.FUNDING_ARBITRAGE:
                self.strategies[strategy_type] = FundingRateArbitrageStrategy(
                    api=self.exchange_api,
                    min_rate_diff=FUNDING_ARB_MIN_RATE_DIFF
                )
                logger.info(f"✅ Funding Arbitrage initialized: ${allocated_capital:.2f}")
            
            elif strategy_type == StrategyType.TRIANGULAR_ARBITRAGE:
                self.strategies[strategy_type] = TriangularArbitrageStrategy(
                    api=self.exchange_api
                )
                logger.info(f"✅ Triangular Arbitrage initialized: ${allocated_capital:.2f}")
            
            # Initialize performance tracking
            self.performance['strategies'][strategy_type] = {
                'trades': 0,
                'pnl': 0.0,
                'win_rate': 0.0,
                'last_trade': None
            }
    
    def check_risk_limits(self) -> bool:
        """
        Check if we can open new positions
        Returns: True if within limits, False otherwise
        """
        # Reset daily P&L if new day
        current_date = datetime.utcnow().date()
        if current_date > self.last_reset:
            self.daily_pnl = 0.0
            self.last_reset = current_date
            logger.info("Daily P&L reset")
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            logger.warning(f"⛔ Daily loss limit reached: ${self.daily_pnl:.2f}")
            return False
        
        # Check total capital
        current_capital = sum(
            getattr(strategy, 'capital', 0) 
            for strategy in self.strategies.values()
        )
        
        if current_capital < self.total_capital * 0.5:
            logger.warning(f"⚠️ Capital dropped below 50%: ${current_capital:.2f}")
            return False
        
        return True
    
    def run_liquidity_strategy(
        self,
        symbol: str,
        h1_data: List[Dict],
        m5_data: List[Dict]
    ) -> Optional[Dict]:
        """
        Execute liquidity strategy
        """
        if StrategyType.LIQUIDITY not in self.strategies:
            return None
        
        strategy = self.strategies[StrategyType.LIQUIDITY]
        
        # Evaluate strategy
        signal = strategy.evaluate(h1_data, m5_data)
        
        if signal:
            logger.info(
                f"💡 Liquidity signal: {signal['direction'].upper()} {symbol} "
                f"@ ${signal['entry_price']:.2f}"
            )
            
            # Update performance
            self._update_performance(StrategyType.LIQUIDITY, signal)
        
        return signal
    
    def run_turtle_strategy(
        self,
        symbol: str,
        daily_data: List[Dict]
    ) -> Optional[Dict]:
        """
        Execute turtle strategy
        """
        if StrategyType.TURTLE not in self.strategies:
            return None
        
        strategy = self.strategies[StrategyType.TURTLE]
        
        # Evaluate strategy
        action = strategy.evaluate(symbol, daily_data)
        
        if action:
            logger.info(
                f"🐢 Turtle {action['action'].upper()}: {symbol} "
                f"@ ${action.get('entry_price', action.get('exit_price', 0)):.2f}"
            )
            
            # Update performance
            if action['action'] == 'close':
                self._update_performance(
                    StrategyType.TURTLE,
                    {'pnl': action['pnl']}
                )
        
        return action
    
    def run_arbitrage_strategies(
        self,
        symbols: List[str]
    ) -> List[Dict]:
        """
        Execute all arbitrage strategies
        """
        opportunities = []
        
        # Price Arbitrage
        if StrategyType.PRICE_ARBITRAGE in self.strategies:
            price_arb = self.strategies[StrategyType.PRICE_ARBITRAGE]
            price_opps = price_arb.find_opportunities(symbols)
            opportunities.extend(price_opps)
        
        # Funding Arbitrage
        if StrategyType.FUNDING_ARBITRAGE in self.strategies:
            funding_arb = self.strategies[StrategyType.FUNDING_ARBITRAGE]
            funding_opps = funding_arb.find_funding_opportunities(symbols)
            opportunities.extend(funding_opps)
        
        # Triangular Arbitrage
        if StrategyType.TRIANGULAR_ARBITRAGE in self.strategies:
            tri_arb = self.strategies[StrategyType.TRIANGULAR_ARBITRAGE]
            tri_opps = tri_arb.find_triangular_opportunities()
            opportunities.extend(tri_opps)
        
        # Log opportunities
        for opp in opportunities:
            logger.info(
                f"🔄 Arbitrage: {opp.get('type', 'unknown')} - "
                f"Profit: {opp.get('profit_pct', 0):.2f}%"
            )
        
        return opportunities
    
    def execute_trade(
        self,
        strategy_type: StrategyType,
        signal: Dict
    ) -> bool:
        """
        Execute trade signal
        Returns: True if successful, False otherwise
        """
        # Check risk limits
        if not self.check_risk_limits():
            logger.warning("Risk limits exceeded - trade rejected")
            return False
        
        try:
            # Route to appropriate exchange
            if 'exchange' in signal:
                exchange = self.exchange_api.exchanges.get(signal['exchange'])
            else:
                # Default to best available
                exchange = self.exchange_api.get_futures_exchange()
            
            # Execute order
            if signal['direction'] in ['long', 'buy']:
                result = exchange.create_futures_order(
                    symbol=signal.get('symbol', 'BTC/USDT'),
                    side='buy',
                    size=signal['position_size'],
                    leverage=FUTURES_MAX_LEVERAGE
                )
            else:
                result = exchange.create_futures_order(
                    symbol=signal.get('symbol', 'BTC/USDT'),
                    side='sell',
                    size=signal['position_size'],
                    leverage=FUTURES_MAX_LEVERAGE
                )
            
            if 'error' not in result:
                logger.info(f"✅ Trade executed: {signal['direction']} {signal['position_size']}")
                return True
            else:
                logger.error(f"❌ Trade failed: {result['error']}")
                return False
        
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False
    
    def _update_performance(self, strategy_type: StrategyType, result: Dict):
        """Update performance metrics"""
        perf = self.performance['strategies'][strategy_type]
        
        perf['trades'] += 1
        perf['last_trade'] = datetime.utcnow()
        
        if 'pnl' in result:
            pnl = result['pnl']
            perf['pnl'] += pnl
            self.performance['total_pnl'] += pnl
            self.daily_pnl += pnl
            
            # Update win rate
            if pnl > 0:
                perf['winning_trades'] = perf.get('winning_trades', 0) + 1
            
            perf['win_rate'] = perf.get('winning_trades', 0) / perf['trades']
        
        self.performance['total_trades'] += 1
    
    def get_portfolio_status(self) -> Dict:
        """Get current portfolio status"""
        total_capital = sum(
            getattr(strategy, 'capital', 0) 
            for strategy in self.strategies.values()
        )
        
        strategy_status = {}
        for strategy_type, strategy in self.strategies.items():
            strategy_status[strategy_type.value] = {
                'capital': getattr(strategy, 'capital', 0),
                'active_positions': len(getattr(strategy, 'positions', {})),
                'performance': self.performance['strategies'][strategy_type]
            }
        
        return {
            'total_capital': total_capital,
            'initial_capital': self.total_capital,
            'total_pnl': self.performance['total_pnl'],
            'roi': ((total_capital - self.total_capital) / self.total_capital) * 100,
            'daily_pnl': self.daily_pnl,
            'total_trades': self.performance['total_trades'],
            'strategies': strategy_status,
            'risk_status': 'OK' if self.check_risk_limits() else 'EXCEEDED',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def rebalance_portfolio(self):
        """
        Rebalance capital allocation based on performance
        Allocate more to winning strategies, less to losing ones
        """
        logger.info("🔄 Rebalancing portfolio...")
        
        # Calculate strategy performance scores
        scores = {}
        for strategy_type in self.strategies:
            perf = self.performance['strategies'][strategy_type]
            
            # Score based on: ROI * win_rate * (trades > 20 ? 1 : 0.5)
            roi = perf['pnl'] / (self.total_capital * self.capital_allocation[strategy_type])
            win_rate = perf.get('win_rate', 0)
            maturity_factor = 1.0 if perf['trades'] > 20 else 0.5
            
            scores[strategy_type] = roi * win_rate * maturity_factor
        
        # Adjust allocations
        total_score = sum(abs(s) for s in scores.values())
        
        if total_score > 0:
            for strategy_type, score in scores.items():
                # Adjust allocation proportionally
                old_allocation = self.capital_allocation[strategy_type]
                new_allocation = max(0.05, min(0.40, abs(score) / total_score))
                
                self.capital_allocation[strategy_type] = new_allocation
                
                logger.info(
                    f"  {strategy_type.value}: {old_allocation:.2%} → {new_allocation:.2%}"
                )
        
        logger.info("Portfolio rebalanced")
    
    def stop_all_strategies(self):
        """Emergency stop - close all positions"""
        logger.warning("🛑 EMERGENCY STOP - Closing all positions")
        
        for strategy_type, strategy in self.strategies.items():
            if hasattr(strategy, 'positions'):
                for symbol in list(strategy.positions.keys()):
                    logger.info(f"Closing position: {symbol}")
                    # Implement position closing logic here
        
        logger.info("All positions closed")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize manager
    manager = UnifiedStrategyManager(
        total_capital=10000,
        testnet=True
    )
    
    # Initialize strategies
    manager.initialize_strategies([
        StrategyType.LIQUIDITY,
        StrategyType.TURTLE,
        StrategyType.PRICE_ARBITRAGE
    ])
    
    # Get portfolio status
    status = manager.get_portfolio_status()
    print("\n📊 Portfolio Status:")
    print(f"Total Capital: ${status['total_capital']:.2f}")
    print(f"Total P&L: ${status['total_pnl']:.2f}")
    print(f"ROI: {status['roi']:.2f}%")
    print(f"Total Trades: {status['total_trades']}")
    
    print("\nStrategy Manager ready!")
