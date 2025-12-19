# signal_bot.py - Technical Analysis Signal Bot
import asyncio
from datetime import datetime
from typing import Dict, List
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SignalBot:
    """
    Conservative signal-based trading
    - Technical indicators (RSI, MACD, Bollinger Bands)
    - Multiple confirmations required
    - Sends notifications for manual trading or auto-trades
    """
    
    def __init__(self, exchange_api, risk_manager, config: Dict):
        self.exchange = exchange_api
        self.risk = risk_manager
        self.config = config
        
        # Signal settings
        self.symbols = config.get('symbols', ['BTC/USDT', 'ETH/USDT'])
        self.timeframe = config.get('timeframe', '1h')
        self.auto_trade = config.get('auto_trade', False)
        self.position_size_percent = config.get('position_size', 0.05)  # 5%
        
        # Indicator thresholds (conservative)
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.min_confirmations = 2  # Need 2+ indicators to agree
        
        # State
        self.active = False
        self.signals = []
        self.open_positions = {}
    
    async def start(self):
        """Start signal bot"""
        self.active = True
        logger.info("Signal Bot started")
        
        while self.active:
            try:
                for symbol in self.symbols:
                    await self._analyze_symbol(symbol)
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Signal bot error: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop signal bot"""
        self.active = False
        logger.info("Signal Bot stopped")
    
    async def _analyze_symbol(self, symbol: str):
        """Analyze symbol and generate signals"""
        try:
            # Get candle data
            klines = await self.exchange.get_klines(symbol, self.timeframe, limit=100)
            if len(klines) < 50:
                return
            
            closes = np.array([k['close'] for k in klines])
            highs = np.array([k['high'] for k in klines])
            lows = np.array([k['low'] for k in klines])
            
            # Calculate indicators
            rsi = self._calculate_rsi(closes)
            macd_signal = self._calculate_macd(closes)
            bb_signal = self._calculate_bollinger(closes)
            volume_signal = self._check_volume(klines)
            
            # Generate signal
            signal = self._generate_signal(
                symbol, rsi, macd_signal, bb_signal, volume_signal, closes[-1]
            )
            
            if signal:
                self.signals.append(signal)
                logger.info(f"Signal generated: {signal}")
                
                if self.auto_trade:
                    await self._execute_signal(signal)
        
        except Exception as e:
            logger.error(f"Analysis error for {symbol}: {e}")
    
    def _calculate_rsi(self, closes: np.ndarray, period: int = 14) -> float:
        """Calculate RSI indicator"""
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, closes: np.ndarray) -> str:
        """Calculate MACD signal"""
        # EMA 12 and 26
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd_line = ema12 - ema26
        
        # Signal line (EMA 9 of MACD)
        signal_line = self._ema(macd_line, 9)
        
        # Current vs previous
        current_diff = macd_line[-1] - signal_line[-1]
        prev_diff = macd_line[-2] - signal_line[-2]
        
        if current_diff > 0 and prev_diff <= 0:
            return 'bullish'
        elif current_diff < 0 and prev_diff >= 0:
            return 'bearish'
        return 'neutral'
    
    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(data))
        ema[0] = data[0]
        
        for i in range(1, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        
        return ema
    
    def _calculate_bollinger(self, closes: np.ndarray, period: int = 20) -> str:
        """Calculate Bollinger Bands signal"""
        sma = np.mean(closes[-period:])
        std = np.std(closes[-period:])
        
        upper = sma + (2 * std)
        lower = sma - (2 * std)
        current = closes[-1]
        
        if current <= lower:
            return 'oversold'
        elif current >= upper:
            return 'overbought'
        return 'neutral'
    
    def _check_volume(self, klines: List[Dict]) -> str:
        """Check volume trend"""
        volumes = [k['volume'] for k in klines[-20:]]
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]
        
        if current_volume > avg_volume * 1.5:
            return 'high'
        elif current_volume < avg_volume * 0.5:
            return 'low'
        return 'normal'
    
    def _generate_signal(self, symbol: str, rsi: float, macd: str, 
                        bb: str, volume: str, price: float) -> Dict:
        """Generate trading signal with confirmations"""
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        # RSI signals
        if rsi < self.rsi_oversold:
            buy_signals += 1
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > self.rsi_overbought:
            sell_signals += 1
            reasons.append(f"RSI overbought ({rsi:.1f})")
        
        # MACD signals
        if macd == 'bullish':
            buy_signals += 1
            reasons.append("MACD bullish crossover")
        elif macd == 'bearish':
            sell_signals += 1
            reasons.append("MACD bearish crossover")
        
        # Bollinger signals
        if bb == 'oversold':
            buy_signals += 1
            reasons.append("Price at lower Bollinger Band")
        elif bb == 'overbought':
            sell_signals += 1
            reasons.append("Price at upper Bollinger Band")
        
        # Volume confirmation
        if volume == 'high':
            reasons.append("High volume confirmation")
        
        # Generate signal if enough confirmations
        if buy_signals >= self.min_confirmations:
            return {
                'symbol': symbol,
                'type': 'BUY',
                'price': price,
                'confirmations': buy_signals,
                'reasons': reasons,
                'timestamp': datetime.now(),
                'strength': 'STRONG' if buy_signals >= 3 else 'MODERATE'
            }
        elif sell_signals >= self.min_confirmations:
            return {
                'symbol': symbol,
                'type': 'SELL',
                'price': price,
                'confirmations': sell_signals,
                'reasons': reasons,
                'timestamp': datetime.now(),
                'strength': 'STRONG' if sell_signals >= 3 else 'MODERATE'
            }
        
        return None
    
    async def _execute_signal(self, signal: Dict):
        """Execute trading signal automatically"""
        symbol = signal['symbol']
        
        # Check if already have position
        if symbol in self.open_positions and signal['type'] == 'BUY':
            logger.info(f"Already have position in {symbol}, skipping buy")
            return
        
        try:
            balance = await self.exchange.get_balance('USDT')
            position_size = self.risk.calculate_position_size(
                balance['free'], self.position_size_percent
            )
            
            if signal['type'] == 'BUY':
                amount = position_size / signal['price']
                order = await self.exchange.create_order(
                    symbol=symbol,
                    side='buy',
                    order_type='market',
                    amount=amount
                )
                
                if 'error' not in order:
                    # Calculate stop loss and take profit
                    stop_loss = self.risk.calculate_stop_loss(signal['price'], 'buy')
                    take_profit = self.risk.calculate_take_profit(signal['price'], 'buy')
                    
                    self.open_positions[symbol] = {
                        'entry_price': signal['price'],
                        'amount': amount,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'timestamp': datetime.now()
                    }
                    
                    logger.info(f"Signal executed: BUY {amount:.8f} {symbol} @ ${signal['price']:.2f}")
            
            elif signal['type'] == 'SELL' and symbol in self.open_positions:
                position = self.open_positions[symbol]
                order = await self.exchange.create_order(
                    symbol=symbol,
                    side='sell',
                    order_type='market',
                    amount=position['amount']
                )
                
                if 'error' not in order:
                    profit = (signal['price'] - position['entry_price']) * position['amount']
                    self.risk.update_pnl(profit)
                    del self.open_positions[symbol]
                    
                    logger.info(f"Signal executed: SELL {position['amount']:.8f} {symbol}, Profit: ${profit:.2f}")
        
        except Exception as e:
            logger.error(f"Execute signal error: {e}")
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'active': self.active,
            'symbols': self.symbols,
            'auto_trade': self.auto_trade,
            'signals_count': len(self.signals),
            'open_positions': len(self.open_positions),
            'recent_signals': self.signals[-10:]
        }
