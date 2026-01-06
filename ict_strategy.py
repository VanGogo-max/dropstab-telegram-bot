"""
ICT (Inner Circle Trader) Strategy Implementation
Smart Money Concepts: Order Blocks, FVG, Liquidity Sweeps, CISD

Based on the methodology popularized by Michael J. Huddleston (ICT)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class OrderBlockType(Enum):
    """Types of order blocks"""
    BULLISH = "bullish"
    BEARISH = "bearish"


class FVGType(Enum):
    """Fair Value Gap types"""
    BULLISH = "bullish_fvg"
    BEARISH = "bearish_fvg"


class ICTStrategy:
    """
    ICT (Inner Circle Trader) Strategy
    
    Concepts:
    1. Order Blocks (OB) - Where institutions placed orders
    2. Fair Value Gaps (FVG) - Price inefficiencies
    3. Liquidity Sweeps - Stop hunt before reversals
    4. Change in State of Delivery (CISD) - Market structure shifts
    5. Balanced Price Range (BPR) - Consolidation zones
    6. Mean Threshold (50%) - Equilibrium price
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        risk_percent: float = 1.0,
        min_fvg_size_pct: float = 0.3,
        ob_lookback: int = 20,
        use_displacement: bool = True
    ):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.risk_percent = risk_percent
        self.min_fvg_size_pct = min_fvg_size_pct  # Minimum FVG size (0.3%)
        self.ob_lookback = ob_lookback
        self.use_displacement = use_displacement
        
        # Position tracking
        self.active_positions = {}
        self.trade_history = []
        
        # Market structure
        self.market_structure = None  # 'bullish', 'bearish', 'ranging'
        self.last_swing_high = None
        self.last_swing_low = None
        
        logger.info("ICT Strategy initialized")
    
    def detect_order_blocks(
        self, 
        candles: List[Dict],
        ob_type: OrderBlockType
    ) -> List[Dict]:
        """
        Detect Order Blocks (OB)
        
        Bullish OB: Last bearish candle before strong bullish move
        Bearish OB: Last bullish candle before strong bearish move
        """
        df = pd.DataFrame(candles[-self.ob_lookback:])
        order_blocks = []
        
        for i in range(2, len(df) - 2):
            if ob_type == OrderBlockType.BULLISH:
                # Look for bearish candle followed by bullish displacement
                is_bearish = df.iloc[i]['close'] < df.iloc[i]['open']
                
                # Check for displacement (strong move up)
                next_candles = df.iloc[i+1:i+3]
                displacement = all(
                    row['close'] > row['open'] and 
                    (row['close'] - row['open']) > (df.iloc[i]['high'] - df.iloc[i]['low'])
                    for _, row in next_candles.iterrows()
                )
                
                if is_bearish and displacement:
                    order_blocks.append({
                        'type': 'bullish_ob',
                        'high': df.iloc[i]['high'],
                        'low': df.iloc[i]['low'],
                        'index': i,
                        'strength': self._calculate_ob_strength(df, i, 'bullish')
                    })
            
            elif ob_type == OrderBlockType.BEARISH:
                # Look for bullish candle followed by bearish displacement
                is_bullish = df.iloc[i]['close'] > df.iloc[i]['open']
                
                next_candles = df.iloc[i+1:i+3]
                displacement = all(
                    row['close'] < row['open'] and 
                    (row['open'] - row['close']) > (df.iloc[i]['high'] - df.iloc[i]['low'])
                    for _, row in next_candles.iterrows()
                )
                
                if is_bullish and displacement:
                    order_blocks.append({
                        'type': 'bearish_ob',
                        'high': df.iloc[i]['high'],
                        'low': df.iloc[i]['low'],
                        'index': i,
                        'strength': self._calculate_ob_strength(df, i, 'bearish')
                    })
        
        # Sort by strength
        order_blocks.sort(key=lambda x: x['strength'], reverse=True)
        return order_blocks[:3]  # Top 3 strongest OBs
    
    def _calculate_ob_strength(self, df: pd.DataFrame, index: int, direction: str) -> float:
        """Calculate Order Block strength based on volume and displacement"""
        volume = df.iloc[index].get('volume', 0)
        avg_volume = df['volume'].mean()
        
        # Displacement magnitude
        if direction == 'bullish':
            displacement = sum(
                df.iloc[i]['close'] - df.iloc[i]['open'] 
                for i in range(index+1, min(index+4, len(df)))
            )
        else:
            displacement = sum(
                df.iloc[i]['open'] - df.iloc[i]['close']
                for i in range(index+1, min(index+4, len(df)))
            )
        
        strength = (volume / avg_volume) * displacement
        return strength
    
    def detect_fair_value_gaps(self, candles: List[Dict]) -> List[Dict]:
        """
        Detect Fair Value Gaps (FVG)
        
        Bullish FVG: Gap between candle[i-1].high and candle[i+1].low
        Bearish FVG: Gap between candle[i-1].low and candle[i+1].high
        """
        df = pd.DataFrame(candles[-50:])
        fvgs = []
        
        for i in range(1, len(df) - 1):
            # Bullish FVG
            if df.iloc[i-1]['high'] < df.iloc[i+1]['low']:
                gap_size = df.iloc[i+1]['low'] - df.iloc[i-1]['high']
                gap_size_pct = (gap_size / df.iloc[i]['close']) * 100
                
                if gap_size_pct >= self.min_fvg_size_pct:
                    fvgs.append({
                        'type': 'bullish_fvg',
                        'high': df.iloc[i+1]['low'],
                        'low': df.iloc[i-1]['high'],
                        'ce': (df.iloc[i+1]['low'] + df.iloc[i-1]['high']) / 2,  # 50% level
                        'size_pct': gap_size_pct,
                        'index': i
                    })
            
            # Bearish FVG
            if df.iloc[i-1]['low'] > df.iloc[i+1]['high']:
                gap_size = df.iloc[i-1]['low'] - df.iloc[i+1]['high']
                gap_size_pct = (gap_size / df.iloc[i]['close']) * 100
                
                if gap_size_pct >= self.min_fvg_size_pct:
                    fvgs.append({
                        'type': 'bearish_fvg',
                        'high': df.iloc[i-1]['low'],
                        'low': df.iloc[i+1]['high'],
                        'ce': (df.iloc[i-1]['low'] + df.iloc[i+1]['high']) / 2,
                        'size_pct': gap_size_pct,
                        'index': i
                    })
        
        return fvgs
    
    def detect_liquidity_sweep(self, candles: List[Dict]) -> Optional[Dict]:
        """
        Detect Liquidity Sweep (stop hunt)
        
        Buy-side sweep: Price breaks above recent high, then reverses down
        Sell-side sweep: Price breaks below recent low, then reverses up
        """
        df = pd.DataFrame(candles[-20:])
        
        if len(df) < 10:
            return None
        
        recent_high = df['high'].iloc[-10:-2].max()
        recent_low = df['low'].iloc[-10:-2].min()
        
        # Check last 2 candles
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Buy-side liquidity sweep (bullish reversal signal)
        if (prev_candle['high'] > recent_high and 
            last_candle['close'] < prev_candle['low']):
            return {
                'type': 'buy_side_sweep',
                'direction': 'short',  # Expect price to go down
                'swept_level': recent_high,
                'current_price': last_candle['close']
            }
        
        # Sell-side liquidity sweep (bearish reversal signal)
        if (prev_candle['low'] < recent_low and 
            last_candle['close'] > prev_candle['high']):
            return {
                'type': 'sell_side_sweep',
                'direction': 'long',  # Expect price to go up
                'swept_level': recent_low,
                'current_price': last_candle['close']
            }
        
        return None
    
    def detect_cisd(self, candles: List[Dict]) -> Optional[str]:
        """
        Detect Change in State of Delivery (CISD)
        
        CISD = Market structure shift (break of structure)
        Bullish CISD: Price breaks above previous swing high
        Bearish CISD: Price breaks below previous swing low
        """
        df = pd.DataFrame(candles[-30:])
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(df) - 2):
            # Swing high
            if (df.iloc[i]['high'] > df.iloc[i-1]['high'] and 
                df.iloc[i]['high'] > df.iloc[i-2]['high'] and
                df.iloc[i]['high'] > df.iloc[i+1]['high'] and 
                df.iloc[i]['high'] > df.iloc[i+2]['high']):
                swing_highs.append(df.iloc[i]['high'])
            
            # Swing low
            if (df.iloc[i]['low'] < df.iloc[i-1]['low'] and 
                df.iloc[i]['low'] < df.iloc[i-2]['low'] and
                df.iloc[i]['low'] < df.iloc[i+1]['low'] and 
                df.iloc[i]['low'] < df.iloc[i+2]['low']):
                swing_lows.append(df.iloc[i]['low'])
        
        if not swing_highs or not swing_lows:
            return None
        
        current_price = df.iloc[-1]['close']
        last_swing_high = swing_highs[-1] if swing_highs else None
        last_swing_low = swing_lows[-1] if swing_lows else None
        
        # Bullish CISD
        if last_swing_high and current_price > last_swing_high:
            self.market_structure = 'bullish'
            return 'bullish_cisd'
        
        # Bearish CISD
        if last_swing_low and current_price < last_swing_low:
            self.market_structure = 'bearish'
            return 'bearish_cisd'
        
        return None
    
    def find_balanced_price_range(self, candles: List[Dict]) -> Optional[Dict]:
        """
        Find Balanced Price Range (BPR) - consolidation zone
        """
        df = pd.DataFrame(candles[-50:])
        
        # Look for consolidation (low volatility)
        for i in range(10, len(df) - 10):
            window = df.iloc[i-10:i+10]
            
            high = window['high'].max()
            low = window['low'].min()
            range_size = high - low
            avg_price = window['close'].mean()
            range_pct = (range_size / avg_price) * 100
            
            # BPR = tight range (< 2%)
            if range_pct < 2.0:
                return {
                    'high': high,
                    'low': low,
                    'ce': (high + low) / 2,  # 50% equilibrium
                    'range_pct': range_pct
                }
        
        return None
    
    def generate_entry_signal(self, candles: List[Dict]) -> Optional[Dict]:
        """
        Generate ICT entry signal based on confluence of factors
        """
        current_price = candles[-1]['close']
        
        # 1. Check market structure (CISD)
        cisd = self.detect_cisd(candles)
        
        # 2. Detect Order Blocks
        if cisd == 'bullish_cisd':
            order_blocks = self.detect_order_blocks(candles, OrderBlockType.BULLISH)
        elif cisd == 'bearish_cisd':
            order_blocks = self.detect_order_blocks(candles, OrderBlockType.BEARISH)
        else:
            return None
        
        if not order_blocks:
            return None
        
        strongest_ob = order_blocks[0]
        
        # 3. Check if price is in OB zone
        ob_high = strongest_ob['high']
        ob_low = strongest_ob['low']
        
        if not (ob_low <= current_price <= ob_high):
            return None
        
        # 4. Look for FVG confirmation
        fvgs = self.detect_fair_value_gaps(candles)
        fvg_confirmation = any(
            fvg['low'] <= current_price <= fvg['high']
            for fvg in fvgs
            if fvg['type'] == strongest_ob['type'].replace('_ob', '_fvg')
        )
        
        # 5. Check for liquidity sweep
        sweep = self.detect_liquidity_sweep(candles)
        
        # Generate signal if confluence is met
        if cisd == 'bullish_cisd' and strongest_ob['type'] == 'bullish_ob':
            # Calculate stops based on OB
            entry_price = current_price
            stop_loss = ob_low * 0.998  # Just below OB
            take_profit = entry_price + (entry_price - stop_loss) * 2  # 1:2 RR
            
            return {
                'direction': 'long',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'ob_zone': (ob_low, ob_high),
                'cisd': cisd,
                'fvg_confirmation': fvg_confirmation,
                'liquidity_sweep': sweep is not None,
                'risk_reward': 2.0,
                'strategy': 'ICT'
            }
        
        elif cisd == 'bearish_cisd' and strongest_ob['type'] == 'bearish_ob':
            entry_price = current_price
            stop_loss = ob_high * 1.002  # Just above OB
            take_profit = entry_price - (stop_loss - entry_price) * 2
            
            return {
                'direction': 'short',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'ob_zone': (ob_low, ob_high),
                'cisd': cisd,
                'fvg_confirmation': fvg_confirmation,
                'liquidity_sweep': sweep is not None,
                'risk_reward': 2.0,
                'strategy': 'ICT'
            }
        
        return None
    
    def calculate_position_size(self, entry: float, stop_loss: float) -> float:
        """Calculate position size based on risk"""
        risk_amount = self.capital * (self.risk_percent / 100)
        price_risk = abs(entry - stop_loss)
        
        if price_risk == 0:
            return 0
        
        size = risk_amount / price_risk
        return size
    
    def evaluate(self, candles: List[Dict]) -> Optional[Dict]:
        """
        Main evaluation method
        Returns: ICT signal or None
        """
        if len(candles) < 50:
            return None
        
        # Generate signal
        signal = self.generate_entry_signal(candles)
        
        if not signal:
            return None
        
        # Calculate position size
        size = self.calculate_position_size(
            signal['entry_price'],
            signal['stop_loss']
        )
        
        if size <= 0:
            return None
        
        signal['position_size'] = size
        signal['capital_used'] = self.capital
        
        logger.info(
            f"📈 ICT {signal['direction'].upper()} signal: "
            f"Entry ${signal['entry_price']:.2f}, "
            f"SL ${signal['stop_loss']:.2f}, "
            f"TP ${signal['take_profit']:.2f}, "
            f"CISD: {signal['cisd']}"
        )
        
        return signal
    
    def update_capital_after_trade(self, pnl: float):
        """Update capital after trade"""
        self.capital += pnl
        self.trade_history.append({
            'pnl': pnl,
            'timestamp': datetime.utcnow(),
            'capital_after': self.capital
        })
        
        logger.info(f"Capital updated: ${self.capital:.2f} (P&L: ${pnl:.2f})")
    
    def get_performance_stats(self) -> Dict:
        """Get strategy performance"""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'total_pnl': 0,
                'roi': 0,
                'win_rate': 0
            }
        
        pnls = [t['pnl'] for t in self.trade_history]
        winning_trades = [p for p in pnls if p > 0]
        
        return {
            'total_trades': len(pnls),
            'winning_trades': len(winning_trades),
            'total_pnl': sum(pnls),
            'roi': ((self.capital - self.initial_capital) / self.initial_capital) * 100,
            'win_rate': len(winning_trades) / len(pnls) if pnls else 0,
            'avg_win': np.mean(winning_trades) if winning_trades else 0,
            'avg_loss': np.mean([p for p in pnls if p < 0]) if any(p < 0 for p in pnls) else 0
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    strategy = ICTStrategy(initial_capital=10000, risk_percent=1.0)
    
    # Example candles (replace with real data)
    # signal = strategy.evaluate(candles)
    
    print("ICT Strategy ready!")
