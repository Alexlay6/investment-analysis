import pandas as pd
import numpy as np
from typing import Dict, Any, List
import streamlit as st
import talib
from scipy import stats

class TechnicalAnalyzer:
    def __init__(self):
        self.ma_periods = [20, 50, 200]
        self.rsi_period = 14
        self.macd_params = {
            'fastperiod': 12,
            'slowperiod': 26,
            'signalperiod': 9
        }
        
    @st.cache_data(ttl=1800)  # 30 minutes cache
    def analyze_price_action(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive technical analysis."""
        try:
            analysis = {
                'trends': self._analyze_trends(data),
                'momentum': self._analyze_momentum(data),
                'volatility': self._analyze_volatility(data),
                'volume': self._analyze_volume(data),
                'patterns': self._identify_patterns(data),
                'support_resistance': self._find_support_resistance(data),
                'signals': self._generate_signals(data)
            }
            return analysis
        except Exception as e:
            st.error(f"Error in technical analysis: {str(e)}")
            return {}

    def _analyze_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price trends using multiple indicators."""
        try:
            close = data['Close'].values
            trends = {}
            
            # Moving Averages
            for period in self.ma_periods:
                ma = talib.SMA(close, timeperiod=period)
                trends[f'MA_{period}'] = {
                    'values': ma,
                    'current': ma[-1],
                    'trend': 'up' if ma[-1] > ma[-2] else 'down'
                }
            
            # ADX (Average Directional Index)
            adx = talib.ADX(data['High'].values, data['Low'].values, close, timeperiod=14)
            
            # Trend strength classification
            trend_strength = 'weak'
            if adx[-1] > 25:
                trend_strength = 'moderate'
            if adx[-1] > 50:
                trend_strength = 'strong'
            
            trends['adx'] = {
                'value': adx[-1],
                'strength': trend_strength
            }
            
            # Overall trend assessment
            price_position = close[-1]
            ma_alignment = all(price_position > ma[-1] for ma in 
                             [trends[f'MA_{period}']['values'] for period in self.ma_periods])
            
            trends['overall'] = {
                'direction': 'bullish' if ma_alignment else 'bearish',
                'strength': trend_strength,
                'price_position': 'above_ma' if ma_alignment else 'below_ma'
            }
            
            return trends
        except Exception as e:
            st.error(f"Error analyzing trends: {str(e)}")
            return {}

    def _analyze_momentum(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze momentum indicators."""
        try:
            close = data['Close'].values
            momentum = {}
            
            # RSI
            rsi = talib.RSI(close, timeperiod=self.rsi_period)
            momentum['rsi'] = {
                'value': rsi[-1],
                'condition': 'overbought' if rsi[-1] > 70 else 'oversold' if rsi[-1] < 30 else 'neutral'
            }
            
            # MACD
            macd, signal, hist = talib.MACD(
                close,
                fastperiod=self.macd_params['fastperiod'],
                slowperiod=self.macd_params['slowperiod'],
                signalperiod=self.macd_params['signalperiod']
            )
            
            momentum['macd'] = {
                'macd': macd[-1],
                'signal': signal[-1],
                'histogram': hist[-1],
                'trend': 'bullish' if hist[-1] > 0 else 'bearish'
            }
            
            # Stochastic
            slowk, slowd = talib.STOCH(
                data['High'].values,
                data['Low'].values,
                close,
                fastk_period=14,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0
            )
            
            momentum['stochastic'] = {
                'k': slowk[-1],
                'd': slowd[-1],
                'condition': 'overbought' if slowk[-1] > 80 else 'oversold' if slowk[-1] < 20 else 'neutral'
            }
            
            return momentum
        except Exception as e:
            st.error(f"Error analyzing momentum: {str(e)}")
            return {}

    def _analyze_volatility(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volatility indicators."""
        try:
            volatility = {}
            
            # Bollinger Bands
            upper, middle, lower = talib.BBANDS(
                data['Close'].values,
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            
            volatility['bollinger'] = {
                'upper': upper[-1],
                'middle': middle[-1],
                'lower': lower[-1],
                'bandwidth': (upper[-1] - lower[-1]) / middle[-1],
                'position': self._get_bb_position(data['Close'].iloc[-1], upper[-1], lower[-1])
            }
            
            # ATR (Average True Range)
            atr = talib.ATR(
                data['High'].values,
                data['Low'].values,
                data['Close'].values,
                timeperiod=14
            )
            
            volatility['atr'] = {
                'value': atr[-1],
                'percent': (atr[-1] / data['Close'].iloc[-1]) * 100
            }
            
            return volatility
        except Exception as e:
            st.error(f"Error analyzing volatility: {str(e)}")
            return {}

    def _analyze_volume(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns and indicators."""
        try:
            volume = {}
            
            # On-Balance Volume (OBV)
            obv = talib.OBV(data['Close'].values, data['Volume'].values)
            
            # Volume Moving Average
            volume_ma = talib.SMA(data['Volume'].values, timeperiod=20)
            
            volume['indicators'] = {
                'obv': obv[-1],
                'obv_trend': 'up' if obv[-1] > obv[-2] else 'down',
                'volume_ma': volume_ma[-1],
                'current_volume': data['Volume'].iloc[-1],
                'volume_trend': 'up' if data['Volume'].iloc[-1] > volume_ma[-1] else 'down'
            }
            
            # Volume Profile
            volume['profile'] = self._calculate_volume_profile(data)
            
            return volume
        except Exception as e:
            st.error(f"Error analyzing volume: {str(e)}")
            return {}

    def _identify_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify chart patterns."""
        try:
            patterns = {}
            high, low, close = data['High'].values, data['Low'].values, data['Close'].values
            
            # Candlestick Patterns
            patterns['candlestick'] = self._identify_candlestick_patterns(high, low, close)
            
            # Chart Patterns
            patterns['chart'] = self._identify_chart_patterns(data)
            
            return patterns
        except Exception as e:
            st.error(f"Error identifying patterns: {str(e)}")
            return {}

    def _find_support_resistance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Find support and resistance levels."""
        try:
            # Calculate pivot points
            pivot = self._calculate_pivot_points(data)
            
            # Find swing highs and lows
            swings = self._find_swing_points(data)
            
            return {
                'pivot_points': pivot,
                'swing_levels': swings,
                'key_levels': self._identify_key_levels(data, pivot, swings)
            }
        except Exception as e:
            st.error(f"Error finding support/resistance: {str(e)}")
            return {}

    def _generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """Generate trading signals based on technical analysis."""
        try:
            analysis = self.analyze_price_action(data)
            signals = {}
            
            # Trend Signals
            signals['trend'] = self._generate_trend_signals(analysis['trends'])
            
            # Momentum Signals
            signals['momentum'] = self._generate_momentum_signals(analysis['momentum'])
            
            # Volume Signals
            signals['volume'] = self._generate_volume_signals(analysis['volume'])
            
            # Overall Signal
            signals['overall'] = self._combine_signals(signals)
            
            return signals
        except Exception as e:
            st.error(f"Error generating signals: {str(e)}")
            return {}

    def _get_bb_position(self, price: float, upper: float, lower: float) -> str:
        """Determine price position relative to Bollinger Bands."""
        if price > upper:
            return 'above'
        elif price < lower:
            return 'below'
        return 'inside'

    def _calculate_volume_profile(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate volume profile metrics."""
        try:
            price_buckets = pd.qcut(data['Close'], q=10)
            volume_profile = data.groupby(price_buckets)['Volume'].sum()
            
            return {
                'poc_price': volume_profile.idxmax().mid,  # Point of Control
                'volume_by_price': volume_profile.to_dict(),
                'high_volume_range': [
                    volume_profile.nlargest(3).index[0].left,
                    volume_profile.nlargest(3).index[0].right
                ]
            }
        except Exception as e:
            st.error(f"Error calculating volume profile: {str(e)}")
            return {}

    def _identify_candlestick_patterns(self, high: np.ndarray, low: np.ndarray, 
                                     close: np.ndarray) -> List[str]:
        """Identify candlestick patterns."""
        patterns = []
        
        # Define pattern recognition functions
        pattern_functions = {
            'Doji': talib.CDLDOJI,
            'Hammer': talib.CDLHAMMER,
            'Engulfing': talib.CDLENGULFING,
            'Morning Star': talib.CDLMORNINGSTAR,
            'Evening Star': talib.CDLEVENINGSTAR
        }
        
        for pattern_name, pattern_func in pattern_functions.items():
            try:
                result = pattern_func(high, low, close)
                if result[-1] != 0:
                    patterns.append(pattern_name)
            except:
                continue
                
        return patterns

    def _combine_signals(self, signals: Dict[str, str]) -> str:
        """Combine different signals into overall signal."""
        # Weight different signals
        weights = {
            'trend': 0.4,
            'momentum': 0.3,
            'volume': 0.3
        }
        
        # Convert signals to numerical scores
        scores = {
            'bullish': 1,
            'neutral': 0,
            'bearish': -1
        }
        
        total_score = 0
        for signal_type, weight in weights.items():
            if signal_type in signals:
                score = scores.get(signals[signal_type], 0)
                total_score += score * weight
        
        # Convert back to signal
        if total_score > 0.2:
            return 'bullish'
        elif total_score < -0.2:
            return 'bearish'
        return 'neutral'