"""
Technical Analysis Agent
وكيل التحليل الفني

This agent specializes in technical analysis of financial markets including
chart patterns, technical indicators, and algorithmic trading signals.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class TechnicalIndicator(Enum):
    """Technical indicators supported"""
    SMA = "simple_moving_average"
    EMA = "exponential_moving_average"
    RSI = "relative_strength_index"
    MACD = "moving_average_convergence_divergence"
    BOLLINGER_BANDS = "bollinger_bands"
    STOCHASTIC = "stochastic_oscillator"
    ATR = "average_true_range"
    VOLUME_PROFILE = "volume_profile"
    FIBONACCI = "fibonacci_retracement"
    ICHIMOKU = "ichimoku_cloud"


class ChartPattern(Enum):
    """Chart patterns for recognition"""
    HEAD_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE = "triangle"
    FLAG = "flag"
    PENNANT = "pennant"
    WEDGE = "wedge"
    RECTANGLE = "rectangle"
    CUP_HANDLE = "cup_and_handle"


class TrendDirection(Enum):
    """Trend directions"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    UNCERTAIN = "uncertain"


class SignalStrength(Enum):
    """Signal strength levels"""
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NEUTRAL = "neutral"


@dataclass
class TechnicalSignal:
    """Technical analysis signal"""
    signal_id: str
    indicator: TechnicalIndicator
    signal_type: str  # buy, sell, hold
    strength: SignalStrength
    confidence: float
    price_level: float
    timestamp: datetime
    description_ar: str
    description_en: str
    targets: List[float]
    stop_loss: float


class TechnicalAnalysisAgent(FinancialAgent):
    """
    Specialized agent for technical market analysis
    وكيل متخصص في التحليل الفني للأسواق
    """

    def __init__(self, agent_id: str = "technical_analysis_agent",
                 agent_name_ar: str = "وكيل التحليل الفني",
                 agent_name_en: str = "Technical Analysis Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'TECHNICAL_ANALYSIS', 'technical_analysis')
        )

        # Technical analysis tools
        self.indicators = self._initialize_technical_indicators()
        self.pattern_library = self._initialize_pattern_library()
        self.signal_algorithms = self._initialize_signal_algorithms()

    def _initialize_capabilities(self) -> None:
        """Initialize technical analysis capabilities"""
        self.capabilities = {
            "technical_indicators": {
                "trend_indicators": True,
                "momentum_indicators": True,
                "volatility_indicators": True,
                "volume_indicators": True,
                "oscillators": True
            },
            "pattern_recognition": {
                "chart_patterns": True,
                "candlestick_patterns": True,
                "harmonic_patterns": True,
                "wave_analysis": True
            },
            "trading_signals": {
                "entry_signals": True,
                "exit_signals": True,
                "stop_loss_levels": True,
                "profit_targets": True,
                "risk_management": True
            },
            "timeframes": {
                "intraday": True,
                "daily": True,
                "weekly": True,
                "monthly": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_technical_indicators(self) -> Dict[str, Any]:
        """Initialize technical indicators configurations"""
        return {
            "sma": {
                "name_ar": "المتوسط المتحرك البسيط",
                "name_en": "Simple Moving Average",
                "default_periods": [20, 50, 200],
                "signals": ["golden_cross", "death_cross", "price_above_below"]
            },
            "ema": {
                "name_ar": "المتوسط المتحرك الأسي",
                "name_en": "Exponential Moving Average",
                "default_periods": [12, 26, 50],
                "signals": ["trend_direction", "support_resistance"]
            },
            "rsi": {
                "name_ar": "مؤشر القوة النسبية",
                "name_en": "Relative Strength Index",
                "default_period": 14,
                "overbought_level": 70,
                "oversold_level": 30,
                "signals": ["overbought", "oversold", "divergence"]
            },
            "macd": {
                "name_ar": "تقارب وتباعد المتوسطات المتحركة",
                "name_en": "MACD",
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "signals": ["signal_line_cross", "zero_line_cross", "divergence"]
            },
            "bollinger_bands": {
                "name_ar": "نطاقات بولينجر",
                "name_en": "Bollinger Bands",
                "period": 20,
                "std_dev": 2,
                "signals": ["band_squeeze", "band_expansion", "price_touch"]
            },
            "stochastic": {
                "name_ar": "مذبذب ستوكاستك",
                "name_en": "Stochastic Oscillator",
                "k_period": 14,
                "d_period": 3,
                "overbought": 80,
                "oversold": 20,
                "signals": ["k_d_cross", "overbought_oversold"]
            }
        }

    def _initialize_pattern_library(self) -> Dict[str, Any]:
        """Initialize chart pattern library"""
        return {
            "reversal_patterns": {
                "head_and_shoulders": {
                    "name_ar": "الرأس والكتفين",
                    "reliability": 0.85,
                    "target_calculation": "neckline_distance",
                    "confirmation": "volume_increase"
                },
                "double_top": {
                    "name_ar": "القمة المزدوجة",
                    "reliability": 0.78,
                    "target_calculation": "pattern_height",
                    "confirmation": "break_support"
                },
                "double_bottom": {
                    "name_ar": "القاع المزدوج",
                    "reliability": 0.80,
                    "target_calculation": "pattern_height",
                    "confirmation": "break_resistance"
                }
            },
            "continuation_patterns": {
                "triangle": {
                    "name_ar": "المثلث",
                    "types": ["ascending", "descending", "symmetrical"],
                    "reliability": 0.72,
                    "target_calculation": "base_distance"
                },
                "flag": {
                    "name_ar": "العلم",
                    "reliability": 0.75,
                    "target_calculation": "flagpole_length"
                },
                "pennant": {
                    "name_ar": "الراية",
                    "reliability": 0.73,
                    "target_calculation": "flagpole_length"
                }
            }
        }

    def _initialize_signal_algorithms(self) -> Dict[str, Any]:
        """Initialize signal generation algorithms"""
        return {
            "trend_following": {
                "moving_average_cross": {
                    "parameters": {"fast": 20, "slow": 50},
                    "signal_strength": "moderate",
                    "success_rate": 0.68
                },
                "breakout_strategy": {
                    "parameters": {"lookback": 20, "volume_multiplier": 1.5},
                    "signal_strength": "strong",
                    "success_rate": 0.72
                }
            },
            "mean_reversion": {
                "rsi_oversold": {
                    "parameters": {"rsi_level": 30, "confirmation_period": 2},
                    "signal_strength": "moderate",
                    "success_rate": 0.65
                },
                "bollinger_bounce": {
                    "parameters": {"touch_threshold": 0.95},
                    "signal_strength": "moderate",
                    "success_rate": 0.63
                }
            },
            "momentum": {
                "macd_divergence": {
                    "parameters": {"lookback": 20, "min_divergence": 5},
                    "signal_strength": "strong",
                    "success_rate": 0.75
                }
            }
        }

    async def analyze_technical_indicators(self, price_data: List[Dict[str, Any]],
                                         indicators: List[TechnicalIndicator]) -> Dict[str, Any]:
        """
        Analyze technical indicators for given price data
        تحليل المؤشرات الفنية للبيانات السعرية
        """
        try:
            if not price_data or len(price_data) < 20:
                return {"error": "Insufficient price data for technical analysis"}

            analysis_result = {
                "analysis_date": datetime.now().isoformat(),
                "data_points": len(price_data),
                "indicator_results": {},
                "signals": [],
                "overall_trend": "",
                "support_resistance": {},
                "recommendation": {}
            }

            # Convert to pandas DataFrame for easier calculation
            df = pd.DataFrame(price_data)
            if 'close' not in df.columns:
                return {"error": "Price data must include 'close' prices"}

            # Calculate each requested indicator
            for indicator in indicators:
                if indicator == TechnicalIndicator.SMA:
                    result = await self._calculate_sma(df)
                elif indicator == TechnicalIndicator.EMA:
                    result = await self._calculate_ema(df)
                elif indicator == TechnicalIndicator.RSI:
                    result = await self._calculate_rsi(df)
                elif indicator == TechnicalIndicator.MACD:
                    result = await self._calculate_macd(df)
                elif indicator == TechnicalIndicator.BOLLINGER_BANDS:
                    result = await self._calculate_bollinger_bands(df)
                elif indicator == TechnicalIndicator.STOCHASTIC:
                    result = await self._calculate_stochastic(df)
                else:
                    result = {"indicator": indicator.value, "status": "not_implemented"}

                analysis_result["indicator_results"][indicator.value] = result

            # Generate signals
            analysis_result["signals"] = await self._generate_technical_signals(
                df, analysis_result["indicator_results"]
            )

            # Determine overall trend
            analysis_result["overall_trend"] = await self._determine_overall_trend(
                analysis_result["indicator_results"]
            )

            # Identify support and resistance levels
            analysis_result["support_resistance"] = await self._identify_support_resistance(df)

            # Generate recommendation
            analysis_result["recommendation"] = await self._generate_recommendation(
                analysis_result["signals"], analysis_result["overall_trend"]
            )

            return analysis_result

        except Exception as e:
            return {"error": f"Technical analysis failed: {str(e)}"}

    async def _calculate_sma(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Simple Moving Average"""
        sma_config = self.indicators["sma"]
        periods = sma_config["default_periods"]

        result = {
            "indicator": "SMA",
            "name_ar": sma_config["name_ar"],
            "periods": periods,
            "values": {},
            "signals": []
        }

        current_price = df['close'].iloc[-1]

        for period in periods:
            if len(df) >= period:
                sma_values = df['close'].rolling(window=period).mean()
                current_sma = sma_values.iloc[-1]
                result["values"][f"sma_{period}"] = current_sma

                # Generate signals
                if current_price > current_sma:
                    signal_strength = "bullish"
                elif current_price < current_sma:
                    signal_strength = "bearish"
                else:
                    signal_strength = "neutral"

                result["signals"].append({
                    "period": period,
                    "signal": signal_strength,
                    "description": f"السعر {'أعلى' if signal_strength == 'bullish' else 'أدنى' if signal_strength == 'bearish' else 'مساوي'} من المتوسط المتحرك {period}"
                })

        # Check for golden cross / death cross
        if len(result["values"]) >= 2:
            short_sma = result["values"].get("sma_50", 0)
            long_sma = result["values"].get("sma_200", 0)

            if short_sma > long_sma:
                result["signals"].append({
                    "type": "golden_cross",
                    "signal": "bullish",
                    "description": "إشارة صعودية - التقاطع الذهبي"
                })
            elif short_sma < long_sma:
                result["signals"].append({
                    "type": "death_cross",
                    "signal": "bearish",
                    "description": "إشارة هبوطية - تقاطع الموت"
                })

        return result

    async def _calculate_ema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Exponential Moving Average"""
        ema_config = self.indicators["ema"]
        periods = ema_config["default_periods"]

        result = {
            "indicator": "EMA",
            "name_ar": ema_config["name_ar"],
            "periods": periods,
            "values": {},
            "signals": []
        }

        current_price = df['close'].iloc[-1]

        for period in periods:
            if len(df) >= period:
                ema_values = df['close'].ewm(span=period).mean()
                current_ema = ema_values.iloc[-1]
                result["values"][f"ema_{period}"] = current_ema

                # Generate trend signal
                if current_price > current_ema:
                    signal = "bullish"
                    description = f"السعر أعلى من المتوسط الأسي {period} - اتجاه صعودي"
                else:
                    signal = "bearish"
                    description = f"السعر أدنى من المتوسط الأسي {period} - اتجاه هبوطي"

                result["signals"].append({
                    "period": period,
                    "signal": signal,
                    "description": description
                })

        return result

    async def _calculate_rsi(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Relative Strength Index"""
        rsi_config = self.indicators["rsi"]
        period = rsi_config["default_period"]
        overbought = rsi_config["overbought_level"]
        oversold = rsi_config["oversold_level"]

        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_rsi = rsi.iloc[-1] if not rsi.empty else 50

        result = {
            "indicator": "RSI",
            "name_ar": rsi_config["name_ar"],
            "period": period,
            "current_value": current_rsi,
            "overbought_level": overbought,
            "oversold_level": oversold,
            "signals": []
        }

        # Generate signals
        if current_rsi > overbought:
            result["signals"].append({
                "type": "overbought",
                "signal": "bearish",
                "strength": "moderate",
                "description": f"مؤشر القوة النسبية في منطقة الشراء المفرط ({current_rsi:.1f})"
            })
        elif current_rsi < oversold:
            result["signals"].append({
                "type": "oversold",
                "signal": "bullish",
                "strength": "moderate",
                "description": f"مؤشر القوة النسبية في منطقة البيع المفرط ({current_rsi:.1f})"
            })
        else:
            result["signals"].append({
                "type": "neutral",
                "signal": "neutral",
                "strength": "weak",
                "description": f"مؤشر القوة النسبية في المنطقة المحايدة ({current_rsi:.1f})"
            })

        return result

    async def _calculate_macd(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate MACD"""
        macd_config = self.indicators["macd"]
        fast_period = macd_config["fast_period"]
        slow_period = macd_config["slow_period"]
        signal_period = macd_config["signal_period"]

        # Calculate MACD
        ema_fast = df['close'].ewm(span=fast_period).mean()
        ema_slow = df['close'].ewm(span=slow_period).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line

        current_macd = macd_line.iloc[-1] if not macd_line.empty else 0
        current_signal = signal_line.iloc[-1] if not signal_line.empty else 0
        current_histogram = histogram.iloc[-1] if not histogram.empty else 0

        result = {
            "indicator": "MACD",
            "name_ar": macd_config["name_ar"],
            "macd_line": current_macd,
            "signal_line": current_signal,
            "histogram": current_histogram,
            "signals": []
        }

        # Generate signals
        if current_macd > current_signal:
            result["signals"].append({
                "type": "signal_line_cross",
                "signal": "bullish",
                "description": "خط الماكد أعلى من خط الإشارة - إشارة شراء"
            })
        else:
            result["signals"].append({
                "type": "signal_line_cross",
                "signal": "bearish",
                "description": "خط الماكد أدنى من خط الإشارة - إشارة بيع"
            })

        # Zero line cross
        if current_macd > 0:
            result["signals"].append({
                "type": "zero_line",
                "signal": "bullish",
                "description": "الماكد أعلى من الخط الصفري - زخم صعودي"
            })
        else:
            result["signals"].append({
                "type": "zero_line",
                "signal": "bearish",
                "description": "الماكد أدنى من الخط الصفري - زخم هبوطي"
            })

        return result

    async def _calculate_bollinger_bands(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Bollinger Bands"""
        bb_config = self.indicators["bollinger_bands"]
        period = bb_config["period"]
        std_dev = bb_config["std_dev"]

        # Calculate Bollinger Bands
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        current_price = df['close'].iloc[-1]
        current_upper = upper_band.iloc[-1] if not upper_band.empty else current_price * 1.05
        current_lower = lower_band.iloc[-1] if not lower_band.empty else current_price * 0.95
        current_sma = sma.iloc[-1] if not sma.empty else current_price

        result = {
            "indicator": "Bollinger Bands",
            "name_ar": bb_config["name_ar"],
            "upper_band": current_upper,
            "middle_band": current_sma,
            "lower_band": current_lower,
            "current_price": current_price,
            "signals": []
        }

        # Generate signals
        band_width = (current_upper - current_lower) / current_sma
        price_position = (current_price - current_lower) / (current_upper - current_lower)

        if current_price >= current_upper * 0.98:
            result["signals"].append({
                "type": "upper_band_touch",
                "signal": "bearish",
                "description": "السعر يلامس النطاق العلوي - إشارة بيع محتملة"
            })
        elif current_price <= current_lower * 1.02:
            result["signals"].append({
                "type": "lower_band_touch",
                "signal": "bullish",
                "description": "السعر يلامس النطاق السفلي - إشارة شراء محتملة"
            })

        if band_width < 0.1:
            result["signals"].append({
                "type": "squeeze",
                "signal": "neutral",
                "description": "ضغط النطاقات - توقع حركة قوية قادمة"
            })

        return result

    async def _calculate_stochastic(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Stochastic Oscillator"""
        stoch_config = self.indicators["stochastic"]
        k_period = stoch_config["k_period"]
        d_period = stoch_config["d_period"]

        # Calculate Stochastic
        if 'high' not in df.columns or 'low' not in df.columns:
            # Use close price as approximation if high/low not available
            df['high'] = df['close']
            df['low'] = df['close']

        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        k_percent = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low)
        d_percent = k_percent.rolling(window=d_period).mean()

        current_k = k_percent.iloc[-1] if not k_percent.empty else 50
        current_d = d_percent.iloc[-1] if not d_percent.empty else 50

        result = {
            "indicator": "Stochastic",
            "name_ar": stoch_config["name_ar"],
            "k_percent": current_k,
            "d_percent": current_d,
            "overbought": stoch_config["overbought"],
            "oversold": stoch_config["oversold"],
            "signals": []
        }

        # Generate signals
        if current_k > stoch_config["overbought"] and current_d > stoch_config["overbought"]:
            result["signals"].append({
                "type": "overbought",
                "signal": "bearish",
                "description": f"مذبذب ستوكاستك في منطقة الشراء المفرط (%K: {current_k:.1f}, %D: {current_d:.1f})"
            })
        elif current_k < stoch_config["oversold"] and current_d < stoch_config["oversold"]:
            result["signals"].append({
                "type": "oversold",
                "signal": "bullish",
                "description": f"مذبذب ستوكاستك في منطقة البيع المفرط (%K: {current_k:.1f}, %D: {current_d:.1f})"
            })

        # K and D cross
        if current_k > current_d:
            result["signals"].append({
                "type": "k_d_cross",
                "signal": "bullish",
                "description": "%K يعبر أعلى %D - إشارة صعودية"
            })
        else:
            result["signals"].append({
                "type": "k_d_cross",
                "signal": "bearish",
                "description": "%K يعبر أدنى %D - إشارة هبوطية"
            })

        return result

    async def _generate_technical_signals(self, df: pd.DataFrame,
                                        indicator_results: Dict[str, Any]) -> List[TechnicalSignal]:
        """Generate comprehensive technical signals"""
        signals = []
        current_price = df['close'].iloc[-1]

        # Collect all individual signals
        for indicator, result in indicator_results.items():
            if "signals" in result:
                for signal_data in result["signals"]:
                    signal = TechnicalSignal(
                        signal_id=f"{indicator}_{len(signals)}_{datetime.now().strftime('%H%M%S')}",
                        indicator=TechnicalIndicator(indicator),
                        signal_type=signal_data.get("signal", "neutral"),
                        strength=SignalStrength(signal_data.get("strength", "moderate")),
                        confidence=self._calculate_signal_confidence(signal_data),
                        price_level=current_price,
                        timestamp=datetime.now(),
                        description_ar=signal_data.get("description", ""),
                        description_en=signal_data.get("description_en", ""),
                        targets=await self._calculate_targets(current_price, signal_data.get("signal", "neutral")),
                        stop_loss=await self._calculate_stop_loss(current_price, signal_data.get("signal", "neutral"))
                    )
                    signals.append(signal)

        return signals

    def _calculate_signal_confidence(self, signal_data: Dict[str, Any]) -> float:
        """Calculate confidence level for a signal"""
        strength = signal_data.get("strength", "moderate")
        signal_type = signal_data.get("signal", "neutral")

        base_confidence = {
            "very_strong": 0.85,
            "strong": 0.75,
            "moderate": 0.65,
            "weak": 0.45,
            "neutral": 0.30
        }.get(strength, 0.50)

        # Adjust based on signal clarity
        if signal_type in ["bullish", "bearish"]:
            base_confidence += 0.05
        elif signal_type == "neutral":
            base_confidence -= 0.10

        return min(max(base_confidence, 0.1), 0.95)

    async def _calculate_targets(self, current_price: float, signal_type: str) -> List[float]:
        """Calculate price targets based on signal"""
        if signal_type == "bullish":
            return [
                current_price * 1.02,  # Target 1: +2%
                current_price * 1.05,  # Target 2: +5%
                current_price * 1.08   # Target 3: +8%
            ]
        elif signal_type == "bearish":
            return [
                current_price * 0.98,  # Target 1: -2%
                current_price * 0.95,  # Target 2: -5%
                current_price * 0.92   # Target 3: -8%
            ]
        else:
            return [current_price]  # No targets for neutral signals

    async def _calculate_stop_loss(self, current_price: float, signal_type: str) -> float:
        """Calculate stop loss level"""
        if signal_type == "bullish":
            return current_price * 0.97  # 3% stop loss for long positions
        elif signal_type == "bearish":
            return current_price * 1.03  # 3% stop loss for short positions
        else:
            return current_price  # No stop loss for neutral signals

    async def _determine_overall_trend(self, indicator_results: Dict[str, Any]) -> str:
        """Determine overall trend based on multiple indicators"""
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0

        for indicator, result in indicator_results.items():
            if "signals" in result:
                for signal in result["signals"]:
                    total_signals += 1
                    if signal.get("signal") == "bullish":
                        bullish_signals += 1
                    elif signal.get("signal") == "bearish":
                        bearish_signals += 1

        if total_signals == 0:
            return "غير محدد"

        bullish_ratio = bullish_signals / total_signals
        bearish_ratio = bearish_signals / total_signals

        if bullish_ratio > 0.6:
            return "صعودي قوي"
        elif bullish_ratio > 0.4:
            return "صعودي معتدل"
        elif bearish_ratio > 0.6:
            return "هبوطي قوي"
        elif bearish_ratio > 0.4:
            return "هبوطي معتدل"
        else:
            return "جانبي/غير واضح"

    async def _identify_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify support and resistance levels"""
        prices = df['close'].values

        # Simple support/resistance calculation
        recent_high = max(prices[-20:]) if len(prices) >= 20 else max(prices)
        recent_low = min(prices[-20:]) if len(prices) >= 20 else min(prices)
        current_price = prices[-1]

        # Calculate pivot points
        range_size = recent_high - recent_low

        resistance_levels = [
            recent_high,
            current_price + (range_size * 0.382),  # Fibonacci 38.2%
            current_price + (range_size * 0.618)   # Fibonacci 61.8%
        ]

        support_levels = [
            recent_low,
            current_price - (range_size * 0.382),
            current_price - (range_size * 0.618)
        ]

        return {
            "resistance_levels": sorted(resistance_levels, reverse=True),
            "support_levels": sorted(support_levels, reverse=True),
            "current_price": current_price,
            "pivot_point": (recent_high + recent_low + current_price) / 3
        }

    async def _generate_recommendation(self, signals: List[TechnicalSignal],
                                     overall_trend: str) -> Dict[str, Any]:
        """Generate trading recommendation based on analysis"""
        # Count signal types
        buy_signals = len([s for s in signals if s.signal_type == "bullish"])
        sell_signals = len([s for s in signals if s.signal_type == "bearish"])
        neutral_signals = len([s for s in signals if s.signal_type == "neutral"])

        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals) if signals else 0.5

        # Generate recommendation
        if buy_signals > sell_signals and buy_signals > neutral_signals:
            recommendation_type = "شراء"
            action = "BUY"
        elif sell_signals > buy_signals and sell_signals > neutral_signals:
            recommendation_type = "بيع"
            action = "SELL"
        else:
            recommendation_type = "انتظار"
            action = "HOLD"

        return {
            "action": action,
            "recommendation_ar": recommendation_type,
            "confidence": avg_confidence,
            "overall_trend": overall_trend,
            "signal_summary": {
                "bullish_signals": buy_signals,
                "bearish_signals": sell_signals,
                "neutral_signals": neutral_signals
            },
            "reasoning": f"بناءً على {len(signals)} إشارة فنية، الاتجاه العام {overall_trend}"
        }

    async def detect_chart_patterns(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect chart patterns in price data
        اكتشاف الأنماط الفنية في البيانات السعرية
        """
        try:
            if len(price_data) < 50:
                return {"error": "Insufficient data for pattern detection"}

            df = pd.DataFrame(price_data)
            patterns_detected = []

            # Simple pattern detection algorithms
            patterns_detected.extend(await self._detect_head_shoulders(df))
            patterns_detected.extend(await self._detect_double_top_bottom(df))
            patterns_detected.extend(await self._detect_triangles(df))

            return {
                "analysis_date": datetime.now().isoformat(),
                "patterns_detected": patterns_detected,
                "pattern_count": len(patterns_detected),
                "reliability_score": self._calculate_pattern_reliability(patterns_detected)
            }

        except Exception as e:
            return {"error": f"Pattern detection failed: {str(e)}"}

    async def _detect_head_shoulders(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect head and shoulders pattern"""
        patterns = []
        # Simplified head and shoulders detection
        # In real implementation, would use more sophisticated algorithms

        if len(df) < 30:
            return patterns

        # Look for three peaks pattern
        prices = df['close'].values
        for i in range(10, len(prices) - 10):
            left_shoulder = prices[i-10:i-5]
            head = prices[i-2:i+3]
            right_shoulder = prices[i+5:i+10]

            if (max(left_shoulder) < max(head) and
                max(right_shoulder) < max(head) and
                abs(max(left_shoulder) - max(right_shoulder)) / max(head) < 0.05):

                patterns.append({
                    "pattern_type": "head_and_shoulders",
                    "pattern_name_ar": "الرأس والكتفين",
                    "reliability": 0.75,
                    "signal": "bearish",
                    "completion_level": max(head),
                    "target": min(prices[i-10:i+10]) - (max(head) - min(prices[i-10:i+10])),
                    "description": "نموذج الرأس والكتفين الهبوطي مكتمل"
                })

        return patterns

    async def _detect_double_top_bottom(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect double top/bottom patterns"""
        patterns = []
        prices = df['close'].values

        if len(prices) < 20:
            return patterns

        # Simple double top detection
        for i in range(10, len(prices) - 10):
            if i < len(prices) - 20:
                peak1 = max(prices[i-5:i+5])
                valley = min(prices[i+5:i+15])
                peak2 = max(prices[i+15:i+25]) if i+25 < len(prices) else 0

                if (abs(peak1 - peak2) / peak1 < 0.03 and  # Peaks are similar
                    valley < peak1 * 0.95):  # Valley is significantly lower

                    patterns.append({
                        "pattern_type": "double_top",
                        "pattern_name_ar": "القمة المزدوجة",
                        "reliability": 0.68,
                        "signal": "bearish",
                        "target": valley - (peak1 - valley),
                        "description": "نموذج القمة المزدوجة الهبوطي"
                    })

        return patterns

    async def _detect_triangles(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect triangle patterns"""
        patterns = []
        # Simplified triangle detection
        # Real implementation would use more sophisticated algorithms

        if len(df) < 30:
            return patterns

        prices = df['close'].values

        # Look for converging highs and lows
        recent_highs = []
        recent_lows = []

        for i in range(5, len(prices) - 5):
            if (prices[i] > prices[i-1] and prices[i] > prices[i+1] and
                prices[i] > prices[i-2] and prices[i] > prices[i+2]):
                recent_highs.append((i, prices[i]))

            if (prices[i] < prices[i-1] and prices[i] < prices[i+1] and
                prices[i] < prices[i-2] and prices[i] < prices[i+2]):
                recent_lows.append((i, prices[i]))

        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            # Check for converging trendlines
            high_slope = (recent_highs[-1][1] - recent_highs[0][1]) / (recent_highs[-1][0] - recent_highs[0][0])
            low_slope = (recent_lows[-1][1] - recent_lows[0][1]) / (recent_lows[-1][0] - recent_lows[0][0])

            if abs(high_slope - low_slope) > 0.01:  # Converging lines
                if high_slope < 0 and low_slope > 0:
                    triangle_type = "symmetrical"
                elif high_slope < 0 and abs(low_slope) < 0.005:
                    triangle_type = "descending"
                elif abs(high_slope) < 0.005 and low_slope > 0:
                    triangle_type = "ascending"
                else:
                    triangle_type = "symmetrical"

                patterns.append({
                    "pattern_type": "triangle",
                    "triangle_type": triangle_type,
                    "pattern_name_ar": f"المثلث {triangle_type}",
                    "reliability": 0.65,
                    "signal": "continuation",
                    "description": f"نموذج المثلث {triangle_type} - توقع استمرار الاتجاه"
                })

        return patterns

    def _calculate_pattern_reliability(self, patterns: List[Dict[str, Any]]) -> float:
        """Calculate overall reliability of detected patterns"""
        if not patterns:
            return 0.0

        total_reliability = sum(pattern.get("reliability", 0.5) for pattern in patterns)
        return total_reliability / len(patterns)

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process technical analysis tasks"""
        try:
            task_type = task.task_data.get("type", "technical_analysis")

            if task_type == "technical_analysis":
                price_data = task.task_data.get("price_data", [])
                indicators = [TechnicalIndicator(ind) for ind in task.task_data.get("indicators", [])]
                return await self.analyze_technical_indicators(price_data, indicators)

            elif task_type == "pattern_detection":
                price_data = task.task_data.get("price_data", [])
                return await self.detect_chart_patterns(price_data)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}