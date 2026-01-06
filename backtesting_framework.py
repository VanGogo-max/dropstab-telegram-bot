"""
Universal Backtesting Framework
Supports: Liquidity Strategy, Turtle Strategy, Arbitrage Strategies
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """Container for backtest results"""
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    roi: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_trade_duration: float  # hours
    trades: List[Dict]
    equity_curve: List[float]
    drawdown_curve: List[float]


class Backtester:
    """
    Universal backtesting engine for trading strategies
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,  # 0.1% per trade
        slippage: float = 0.0005  # 0.05% slippage
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        logger.info(
            f"Backtester initialized: Capital ${initial_capital}, "
            f"Commission {commission*100}%, Slippage {slippage*100}%"
        )
    
    def apply_costs(self, entry_price: float, exit_price: float, size: float) -> float:
        """
        Apply commission and slippage to trade
        Returns: net P&L after costs
        """
        # Entry costs
        entry_commission = entry_price * size * self.commission
        entry_slippage = entry_price * size * self.slippage
        
        # Exit costs
        exit_commission = exit_price * size * self.commission
        exit_slippage = exit_price * size * self.slippage
        
        # Total costs
        total_costs = entry_commission + exit_commission + entry_slippage + exit_slippage
        
        return -total_costs
    
    def calculate_metrics(
        self,
        trades: List[Dict],
        equity_curve: List[float]
    ) -> Dict:
        """
        Calculate comprehensive performance metrics
        """
        if not trades:
            return self._empty_metrics()
        
        # Basic stats
        total_trades = len(trades)
        pnls = [t['pnl'] for t in trades]
        winning_trades = [p for p in pnls if p > 0]
        losing_trades = [p for p in pnls if p < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_pnl = sum(pnls)
        roi = (total_pnl / self.initial_capital) * 100
        
        # Win/Loss stats
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        largest_win = max(winning_trades) if winning_trades else 0
        largest_loss = min(losing_trades) if losing_trades else 0
        
        # Profit factor
        total_wins = sum(winning_trades) if winning_trades else 0
        total_losses = abs(sum(losing_trades)) if losing_trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Drawdown
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Sharpe Ratio (annualized)
        returns = np.diff(equity) / equity[:-1]
        if len(returns) > 0 and returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)  # Assuming daily
        else:
            sharpe = 0
        
        # Sortino Ratio (only downside volatility)
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0 and negative_returns.std() > 0:
            sortino = (returns.mean() / negative_returns.std()) * np.sqrt(252)
        else:
            sortino = 0
        
        # Average trade duration
        durations = [t.get('duration', 0) for t in trades if 'duration' in t]
        avg_duration = np.mean(durations) if durations else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'roi': roi,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'avg_trade_duration': avg_duration
        }
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics when no trades"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'roi': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'profit_factor': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'avg_trade_duration': 0
        }
    
    def backtest_liquidity_strategy(
        self,
        strategy,
        h1_data: List[Dict],
        m5_data: List[Dict],
        symbol: str = 'BTC/USDT'
    ) -> BacktestResult:
        """
        Backtest liquidity strategy with multi-timeframe data
        """
        logger.info(f"Starting backtest: Liquidity Strategy on {symbol}")
        
        trades = []
        equity_curve = [self.initial_capital]
        active_position = None
        
        # Convert to DataFrames
        h1_df = pd.DataFrame(h1_data)
        m5_df = pd.DataFrame(m5_data)
        
        # Iterate through M5 candles
        for i in range(100, len(m5_df)):  # Start after warm-up
            current_m5 = m5_data[:i+1]
            current_h1 = h1_data[:i//12+1]  # Approximate H1 alignment
            
            current_price = current_m5[-1]['close']
            
            # Check active position
            if active_position:
                # Update trailing stop
                position_id = f"{symbol}_{active_position['entry_time']}"
                strategy.active_positions[position_id] = active_position
                strategy.update_trailing_stop(position_id, current_price)
                
                # Check exit
                exit_info = strategy.check_exit(position_id, current_price)
                if exit_info:
                    # Apply costs
                    costs = self.apply_costs(
                        active_position['entry_price'],
                        exit_info['exit_price'],
                        active_position['position_size']
                    )
                    
                    net_pnl = exit_info['pnl'] + costs
                    
                    trades.append({
                        'symbol': symbol,
                        'direction': active_position['direction'],
                        'entry_price': active_position['entry_price'],
                        'exit_price': exit_info['exit_price'],
                        'size': active_position['position_size'],
                        'pnl': net_pnl,
                        'reason': exit_info['reason'],
                        'entry_time': active_position['entry_time'],
                        'exit_time': i,
                        'duration': (i - active_position['entry_time']) * 5 / 60  # hours
                    })
                    
                    strategy.update_capital_after_trade(net_pnl)
                    equity_curve.append(strategy.capital)
                    
                    active_position = None
                    del strategy.active_positions[position_id]
            
            # Check for new signal
            if not active_position:
                signal = strategy.evaluate(current_h1, current_m5)
                
                if signal:
                    active_position = {
                        'direction': signal['direction'],
                        'entry_price': signal['entry_price'],
                        'stop_loss': signal['stop_loss'],
                        'take_profit': signal['take_profit'],
                        'position_size': signal['position_size'],
                        'atr': signal['atr'],
                        'entry_time': i,
                        'status': 'active'
                    }
                    
                    logger.debug(
                        f"Position opened: {signal['direction']} @ ${signal['entry_price']:.2f}"
                    )
        
        # Calculate metrics
        metrics = self.calculate_metrics(trades, equity_curve)
        drawdown_curve = self._calculate_drawdown_curve(equity_curve)
        
        result = BacktestResult(
            strategy_name='Enhanced Liquidity Strategy',
            trades=trades,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            **metrics
        )
        
        logger.info(
            f"Backtest complete: {result.total_trades} trades, "
            f"Win rate: {result.win_rate:.2%}, ROI: {result.roi:.2f}%"
        )
        
        return result
    
    def backtest_turtle_strategy(
        self,
        strategy,
        daily_data: List[Dict],
        symbol: str = 'BTC/USDT'
    ) -> BacktestResult:
        """
        Backtest Turtle strategy on daily data
        """
        logger.info(f"Starting backtest: Turtle Strategy on {symbol}")
        
        equity_curve = [self.initial_capital]
        
        # Iterate through daily candles
        for i in range(strategy.breakout_period + 1, len(daily_data)):
            current_data = daily_data[:i+1]
            
            # Evaluate strategy
            action = strategy.evaluate(symbol, current_data)
            
            if action:
                if action['action'] == 'close':
                    # Apply costs
                    pos = strategy.positions.get(symbol)
                    if pos:
                        costs = self.apply_costs(
                            pos['avg_entry_price'],
                            action['exit_price'],
                            pos['total_size']
                        )
                        
                        # Adjust P&L
                        action['pnl'] += costs
                
                equity_curve.append(strategy.capital)
        
        # Get trades from strategy
        trades = strategy.trade_history
        
        # Calculate metrics
        metrics = self.calculate_metrics(trades, equity_curve)
        drawdown_curve = self._calculate_drawdown_curve(equity_curve)
        
        result = BacktestResult(
            strategy_name=f'Turtle Strategy System {strategy.system}',
            trades=trades,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            **metrics
        )
        
        logger.info(
            f"Backtest complete: {result.total_trades} trades, "
            f"Win rate: {result.win_rate:.2%}, ROI: {result.roi:.2f}%"
        )
        
        return result
    
    def _calculate_drawdown_curve(self, equity_curve: List[float]) -> List[float]:
        """Calculate drawdown curve"""
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = ((equity - running_max) / running_max) * 100
        return drawdown.tolist()
    
    def plot_results(self, result: BacktestResult, save_path: Optional[str] = None):
        """
        Plot backtest results
        """
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle(f'{result.strategy_name} - Backtest Results', fontsize=16)
        
        # 1. Equity Curve
        axes[0, 0].plot(result.equity_curve, label='Equity', linewidth=2)
        axes[0, 0].axhline(y=self.initial_capital, color='r', linestyle='--', alpha=0.5)
        axes[0, 0].set_title('Equity Curve')
        axes[0, 0].set_xlabel('Trade #')
        axes[0, 0].set_ylabel('Capital ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)
        
        # 2. Drawdown
        axes[0, 1].fill_between(
            range(len(result.drawdown_curve)),
            result.drawdown_curve,
            alpha=0.3,
            color='red'
        )
        axes[0, 1].plot(result.drawdown_curve, color='red', linewidth=1)
        axes[0, 1].set_title(f'Drawdown (Max: {result.max_drawdown:.2f}%)')
        axes[0, 1].set_xlabel('Trade #')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(alpha=0.3)
        
        # 3. Trade P&L Distribution
        pnls = [t['pnl'] for t in result.trades]
        axes[1, 0].hist(pnls, bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].axvline(x=0, color='r', linestyle='--', alpha=0.5)
        axes[1, 0].set_title('Trade P&L Distribution')
        axes[1, 0].set_xlabel('P&L ($)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(alpha=0.3)
        
        # 4. Win/Loss Ratio
        win_loss_data = [result.winning_trades, result.losing_trades]
        axes[1, 1].pie(
            win_loss_data,
            labels=['Wins', 'Losses'],
            autopct='%1.1f%%',
            colors=['green', 'red'],
            startangle=90
        )
        axes[1, 1].set_title(f'Win Rate: {result.win_rate:.2%}')
        
        # 5. Cumulative P&L
        cumulative_pnl = np.cumsum(pnls)
        axes[2, 0].plot(cumulative_pnl, linewidth=2)
        axes[2, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[2, 0].set_title('Cumulative P&L')
        axes[2, 0].set_xlabel('Trade #')
        axes[2, 0].set_ylabel('Cumulative P&L ($)')
        axes[2, 0].grid(alpha=0.3)
        
        # 6. Performance Metrics Table
        axes[2, 1].axis('off')
        metrics_text = f"""
        Total Trades: {result.total_trades}
        Win Rate: {result.win_rate:.2%}
        Total P&L: ${result.total_pnl:.2f}
        ROI: {result.roi:.2f}%
        Max Drawdown: {result.max_drawdown:.2f}%
        Sharpe Ratio: {result.sharpe_ratio:.2f}
        Sortino Ratio: {result.sortino_ratio:.2f}
        Profit Factor: {result.profit_factor:.2f}
        Avg Win: ${result.avg_win:.2f}
        Avg Loss: ${result.avg_loss:.2f}
        Avg Duration: {result.avg_trade_duration:.1f}h
        """
        axes[2, 1].text(0.1, 0.5, metrics_text, fontsize=12, verticalalignment='center',
                       family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def compare_strategies(
        self,
        results: List[BacktestResult]
    ) -> pd.DataFrame:
        """
        Compare multiple strategy results
        """
        comparison = []
        
        for result in results:
            comparison.append({
                'Strategy': result.strategy_name,
                'Trades': result.total_trades,
                'Win Rate': f"{result.win_rate:.2%}",
                'ROI': f"{result.roi:.2f}%",
                'Max DD': f"{result.max_drawdown:.2f}%",
                'Sharpe': f"{result.sharpe_ratio:.2f}",
                'Sortino': f"{result.sortino_ratio:.2f}",
                'Profit Factor': f"{result.profit_factor:.2f}",
                'Avg Duration': f"{result.avg_trade_duration:.1f}h"
            })
        
        df = pd.DataFrame(comparison)
        return df


# Utility function for loading historical data
def load_historical_data(
    filepath: str,
    timeframe: str = '5m'
) -> List[Dict]:
    """
    Load historical data from CSV
    Expected columns: timestamp, open, high, low, close, volume
    """
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df.to_dict('records')


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Load data
    # h1_data = load_historical_data('data/BTCUSDT_1h.csv', '1h')
    # m5_data = load_historical_data('data/BTCUSDT_5m.csv', '5m')
    
    # Initialize backtester
    backtester = Backtester(initial_capital=10000, commission=0.001)
    
    # Example: Backtest liquidity strategy
    # from liquidity_strategy_improved import EnhancedLiquidityStrategy
    # strategy = EnhancedLiquidityStrategy(initial_capital=10000)
    # result = backtester.backtest_liquidity_strategy(strategy, h1_data, m5_data)
    # backtester.plot_results(result, save_path='backtest_liquidity.png')
    
    print("Backtesting framework ready!")
