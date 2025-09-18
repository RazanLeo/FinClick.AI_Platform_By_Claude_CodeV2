"""
Alpha Vantage API Service
Handles financial data and technical indicators for FinClick.AI platform
"""

import aiohttp
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

class Function(Enum):
    # Time Series
    TIME_SERIES_INTRADAY = "TIME_SERIES_INTRADAY"
    TIME_SERIES_DAILY = "TIME_SERIES_DAILY"
    TIME_SERIES_DAILY_ADJUSTED = "TIME_SERIES_DAILY_ADJUSTED"
    TIME_SERIES_WEEKLY = "TIME_SERIES_WEEKLY"
    TIME_SERIES_WEEKLY_ADJUSTED = "TIME_SERIES_WEEKLY_ADJUSTED"
    TIME_SERIES_MONTHLY = "TIME_SERIES_MONTHLY"
    TIME_SERIES_MONTHLY_ADJUSTED = "TIME_SERIES_MONTHLY_ADJUSTED"

    # Technical Indicators
    SMA = "SMA"  # Simple Moving Average
    EMA = "EMA"  # Exponential Moving Average
    WMA = "WMA"  # Weighted Moving Average
    DEMA = "DEMA"  # Double Exponential Moving Average
    TEMA = "TEMA"  # Triple Exponential Moving Average
    TRIMA = "TRIMA"  # Triangular Moving Average
    KAMA = "KAMA"  # Kaufman Adaptive Moving Average
    MAMA = "MAMA"  # MESA Adaptive Moving Average
    T3 = "T3"  # Triple Exponential Moving Average (T3)

    # Momentum Indicators
    RSI = "RSI"  # Relative Strength Index
    MACD = "MACD"  # Moving Average Convergence Divergence
    STOCH = "STOCH"  # Stochastic
    STOCHF = "STOCHF"  # Stochastic Fast
    STOCHRSI = "STOCHRSI"  # Stochastic Relative Strength Index
    WILLR = "WILLR"  # Williams' %R
    ADX = "ADX"  # Average Directional Index
    ADXR = "ADXR"  # Average Directional Index Rating
    APO = "APO"  # Absolute Price Oscillator
    PPO = "PPO"  # Percentage Price Oscillator
    MOM = "MOM"  # Momentum
    BOP = "BOP"  # Balance of Power
    CCI = "CCI"  # Commodity Channel Index
    CMO = "CMO"  # Chande Momentum Oscillator
    ROC = "ROC"  # Rate of Change
    ROCR = "ROCR"  # Rate of Change Ratio
    AROON = "AROON"  # Aroon
    AROONOSC = "AROONOSC"  # Aroon Oscillator
    MFI = "MFI"  # Money Flow Index
    TRIX = "TRIX"  # 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
    ULTOSC = "ULTOSC"  # Ultimate Oscillator
    DX = "DX"  # Directional Movement Index
    MINUS_DI = "MINUS_DI"  # Minus Directional Indicator
    PLUS_DI = "PLUS_DI"  # Plus Directional Indicator
    MINUS_DM = "MINUS_DM"  # Minus Directional Movement
    PLUS_DM = "PLUS_DM"  # Plus Directional Movement

    # Volume Indicators
    CHAIKIN_AD = "AD"  # Chaikin A/D Line
    CHAIKIN_ADOSC = "ADOSC"  # Chaikin A/D Oscillator
    OBV = "OBV"  # On Balance Volume

    # Volatility Indicators
    ATR = "ATR"  # Average True Range
    NATR = "NATR"  # Normalized Average True Range
    TRANGE = "TRANGE"  # True Range

    # Price Transform
    AVGPRICE = "AVGPRICE"  # Average Price
    MEDPRICE = "MEDPRICE"  # Median Price
    TYPPRICE = "TYPPRICE"  # Typical Price
    WCLPRICE = "WCLPRICE"  # Weighted Close Price

    # Cycle Indicators
    HT_DCPERIOD = "HT_DCPERIOD"  # Hilbert Transform - Dominant Cycle Period
    HT_DCPHASE = "HT_DCPHASE"  # Hilbert Transform - Dominant Cycle Phase
    HT_PHASOR = "HT_PHASOR"  # Hilbert Transform - Phasor Components
    HT_SINE = "HT_SINE"  # Hilbert Transform - SineWave
    HT_TRENDMODE = "HT_TRENDMODE"  # Hilbert Transform - Trend vs Cycle Mode

    # Pattern Recognition
    CDL2CROWS = "CDL2CROWS"  # Two Crows
    CDL3BLACKCROWS = "CDL3BLACKCROWS"  # Three Black Crows
    CDL3INSIDE = "CDL3INSIDE"  # Three Inside Up/Down
    CDL3LINESTRIKE = "CDL3LINESTRIKE"  # Three-Line Strike
    CDL3OUTSIDE = "CDL3OUTSIDE"  # Three Outside Up/Down
    CDL3STARSINSOUTH = "CDL3STARSINSOUTH"  # Three Stars In The South
    CDL3WHITESOLDIERS = "CDL3WHITESOLDIERS"  # Three Advancing White Soldiers

    # Fundamental Data
    OVERVIEW = "OVERVIEW"  # Company Overview
    INCOME_STATEMENT = "INCOME_STATEMENT"  # Income Statement
    BALANCE_SHEET = "BALANCE_SHEET"  # Balance Sheet
    CASH_FLOW = "CASH_FLOW"  # Cash Flow
    EARNINGS = "EARNINGS"  # Earnings

    # Economic Indicators
    REAL_GDP = "REAL_GDP"
    REAL_GDP_PER_CAPITA = "REAL_GDP_PER_CAPITA"
    TREASURY_YIELD = "TREASURY_YIELD"
    FEDERAL_FUNDS_RATE = "FEDERAL_FUNDS_RATE"
    CPI = "CPI"  # Consumer Price Index
    INFLATION = "INFLATION"
    RETAIL_SALES = "RETAIL_SALES"
    DURABLES = "DURABLES"
    UNEMPLOYMENT = "UNEMPLOYMENT"
    NONFARM_PAYROLL = "NONFARM_PAYROLL"

class Interval(Enum):
    ONE_MIN = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    SIXTY_MIN = "60min"

class OutputSize(Enum):
    COMPACT = "compact"  # Latest 100 data points
    FULL = "full"  # Full-length time series

class DataType(Enum):
    JSON = "json"
    CSV = "csv"

@dataclass
class AlphaVantageData:
    symbol: str
    function: str
    data: Dict
    metadata: Dict
    timestamp: datetime

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry API calls on specific errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except aiohttp.ClientError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Alpha Vantage API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class AlphaVantageService:
    """Comprehensive Alpha Vantage API service for FinClick.AI"""

    def __init__(self, api_key: str, rate_limit_delay: float = 12.0):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

        # Alpha Vantage has strict rate limits: 5 calls per minute for free tier
        self.rate_limit_delay = rate_limit_delay  # 12 seconds between calls for free tier
        self.last_request_time = 0

        # Cache for data
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache

        logger.info("Alpha Vantage service initialized")

    async def _rate_limit_check(self):
        """Ensure we don't exceed Alpha Vantage rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _get_cache_key(self, params: Dict) -> str:
        """Generate cache key for request"""
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return param_str

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False

        cached_time = self._cache[cache_key]['timestamp']
        return (time.time() - cached_time) < self._cache_ttl

    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]['data']
        return None

    def _cache_data(self, cache_key: str, data: Any):
        """Cache data with timestamp"""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }

    async def _make_request(self, params: Dict) -> Dict:
        """Make request to Alpha Vantage API"""
        await self._rate_limit_check()

        params['apikey'] = self.api_key

        # Check cache first
        cache_key = self._get_cache_key(params)
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        headers = {
            'User-Agent': 'FinClick.AI/1.0'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check for API error messages
                    if "Error Message" in data:
                        raise Exception(f"Alpha Vantage API error: {data['Error Message']}")

                    if "Note" in data:
                        logger.warning(f"Alpha Vantage API note: {data['Note']}")
                        raise Exception(f"Alpha Vantage rate limit exceeded: {data['Note']}")

                    self._cache_data(cache_key, data)
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Alpha Vantage API error {response.status}: {error_text}")
                    raise Exception(f"Alpha Vantage API error {response.status}: {error_text}")

    @retry_on_error()
    async def get_time_series_data(
        self,
        symbol: str,
        function: Function,
        interval: Interval = None,
        output_size: OutputSize = OutputSize.COMPACT,
        datatype: DataType = DataType.JSON
    ) -> AlphaVantageData:
        """Get time series data for a symbol"""
        try:
            params = {
                'function': function.value,
                'symbol': symbol,
                'outputsize': output_size.value,
                'datatype': datatype.value
            }

            if interval and function == Function.TIME_SERIES_INTRADAY:
                params['interval'] = interval.value

            response = await self._make_request(params)

            # Extract metadata and time series data
            metadata = {}
            time_series_data = {}

            for key, value in response.items():
                if "Meta Data" in key:
                    metadata = value
                elif "Time Series" in key or "Daily" in key or "Weekly" in key or "Monthly" in key:
                    time_series_data = value

            logger.info(f"Retrieved {function.value} data for {symbol}")
            return AlphaVantageData(
                symbol=symbol,
                function=function.value,
                data=time_series_data,
                metadata=metadata,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Failed to get time series data for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_technical_indicator(
        self,
        symbol: str,
        function: Function,
        interval: Interval,
        time_period: int = 14,
        series_type: str = "close",
        **kwargs
    ) -> AlphaVantageData:
        """Get technical indicator data"""
        try:
            params = {
                'function': function.value,
                'symbol': symbol,
                'interval': interval.value,
                'time_period': time_period,
                'series_type': series_type
            }

            # Add additional parameters based on indicator
            params.update(kwargs)

            response = await self._make_request(params)

            # Extract metadata and technical analysis data
            metadata = {}
            technical_data = {}

            for key, value in response.items():
                if "Meta Data" in key:
                    metadata = value
                elif "Technical Analysis" in key:
                    technical_data = value

            logger.info(f"Retrieved {function.value} for {symbol}")
            return AlphaVantageData(
                symbol=symbol,
                function=function.value,
                data=technical_data,
                metadata=metadata,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Failed to get technical indicator {function.value} for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_company_overview(self, symbol: str) -> Dict:
        """Get company overview and fundamental data"""
        try:
            params = {
                'function': Function.OVERVIEW.value,
                'symbol': symbol
            }

            response = await self._make_request(params)

            # Clean up the data
            cleaned_data = {}
            for key, value in response.items():
                if value and value != "None" and value != "-":
                    try:
                        # Try to convert numeric values
                        if '.' in str(value) and str(value).replace('.', '').replace('-', '').isdigit():
                            cleaned_data[key] = float(value)
                        elif str(value).isdigit():
                            cleaned_data[key] = int(value)
                        else:
                            cleaned_data[key] = value
                    except:
                        cleaned_data[key] = value

            logger.info(f"Retrieved company overview for {symbol}")
            return cleaned_data

        except Exception as e:
            logger.error(f"Failed to get company overview for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_earnings_data(self, symbol: str) -> Dict:
        """Get earnings data for a symbol"""
        try:
            params = {
                'function': Function.EARNINGS.value,
                'symbol': symbol
            }

            response = await self._make_request(params)

            logger.info(f"Retrieved earnings data for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get earnings data for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_economic_indicator(
        self,
        function: Function,
        interval: str = "annual",
        maturity: str = None
    ) -> Dict:
        """Get economic indicator data"""
        try:
            params = {
                'function': function.value,
                'interval': interval
            }

            if maturity:
                params['maturity'] = maturity

            response = await self._make_request(params)

            logger.info(f"Retrieved economic indicator {function.value}")
            return response

        except Exception as e:
            logger.error(f"Failed to get economic indicator {function.value}: {str(e)}")
            raise

    @retry_on_error()
    async def get_currency_exchange_rate(self, from_currency: str, to_currency: str) -> Dict:
        """Get currency exchange rate"""
        try:
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': from_currency,
                'to_currency': to_currency
            }

            response = await self._make_request(params)

            logger.info(f"Retrieved exchange rate for {from_currency}/{to_currency}")
            return response

        except Exception as e:
            logger.error(f"Failed to get exchange rate for {from_currency}/{to_currency}: {str(e)}")
            raise

    @retry_on_error()
    async def get_crypto_rating(self, symbol: str) -> Dict:
        """Get cryptocurrency rating"""
        try:
            params = {
                'function': 'CRYPTO_RATING',
                'symbol': symbol
            }

            response = await self._make_request(params)

            logger.info(f"Retrieved crypto rating for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get crypto rating for {symbol}: {str(e)}")
            raise

    async def get_multiple_indicators(
        self,
        symbol: str,
        indicators: List[Dict],
        interval: Interval
    ) -> Dict[str, AlphaVantageData]:
        """Get multiple technical indicators for a symbol"""
        results = {}

        for indicator_config in indicators:
            try:
                function = indicator_config['function']
                time_period = indicator_config.get('time_period', 14)
                series_type = indicator_config.get('series_type', 'close')
                kwargs = indicator_config.get('kwargs', {})

                result = await self.get_technical_indicator(
                    symbol=symbol,
                    function=function,
                    interval=interval,
                    time_period=time_period,
                    series_type=series_type,
                    **kwargs
                )

                results[function.value] = result

                # Add delay between requests
                await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Failed to get indicator {indicator_config['function'].value}: {str(e)}")
                results[indicator_config['function'].value] = None

        return results

    async def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """Get comprehensive analysis including price data and technical indicators"""
        try:
            results = {}

            # Get daily price data
            daily_data = await self.get_time_series_data(
                symbol=symbol,
                function=Function.TIME_SERIES_DAILY_ADJUSTED,
                output_size=OutputSize.COMPACT
            )
            results['daily_data'] = daily_data

            # Get company overview
            overview = await self.get_company_overview(symbol)
            results['overview'] = overview

            # Common technical indicators
            indicators = [
                {'function': Function.RSI, 'time_period': 14},
                {'function': Function.MACD, 'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},
                {'function': Function.SMA, 'time_period': 20},
                {'function': Function.EMA, 'time_period': 20},
                {'function': Function.ATR, 'time_period': 14},
                {'function': Function.ADX, 'time_period': 14}
            ]

            technical_results = await self.get_multiple_indicators(
                symbol=symbol,
                indicators=indicators,
                interval=Interval.SIXTY_MIN
            )
            results['technical_indicators'] = technical_results

            logger.info(f"Retrieved comprehensive analysis for {symbol}")
            return results

        except Exception as e:
            logger.error(f"Failed to get comprehensive analysis for {symbol}: {str(e)}")
            raise

    def parse_time_series_data(self, data: AlphaVantageData) -> List[Dict]:
        """Parse time series data into list of dictionaries"""
        parsed_data = []

        for date_str, values in data.data.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                parsed_entry = {
                    'date': date_obj,
                    'open': float(values.get('1. open', 0)),
                    'high': float(values.get('2. high', 0)),
                    'low': float(values.get('3. low', 0)),
                    'close': float(values.get('4. close', 0)),
                    'volume': int(values.get('5. volume', 0))
                }

                # Handle adjusted close if available
                if '5. adjusted close' in values:
                    parsed_entry['adjusted_close'] = float(values['5. adjusted close'])

                parsed_data.append(parsed_entry)

            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse data point {date_str}: {str(e)}")

        # Sort by date
        parsed_data.sort(key=lambda x: x['date'])
        return parsed_data

    def calculate_custom_indicators(self, price_data: List[Dict]) -> Dict:
        """Calculate custom indicators from price data"""
        if len(price_data) < 20:
            return {}

        # Sort by date
        sorted_data = sorted(price_data, key=lambda x: x['date'])
        closes = [item['close'] for item in sorted_data]
        highs = [item['high'] for item in sorted_data]
        lows = [item['low'] for item in sorted_data]
        volumes = [item['volume'] for item in sorted_data]

        # Calculate volatility (standard deviation of returns)
        if len(closes) > 1:
            returns = [(closes[i] / closes[i-1] - 1) for i in range(1, len(closes))]
            volatility = (sum([(r - sum(returns)/len(returns))**2 for r in returns]) / len(returns))**0.5
        else:
            volatility = 0

        # Calculate support and resistance levels
        recent_highs = highs[-20:] if len(highs) >= 20 else highs
        recent_lows = lows[-20:] if len(lows) >= 20 else lows

        resistance = max(recent_highs) if recent_highs else 0
        support = min(recent_lows) if recent_lows else 0

        # Calculate average volume
        avg_volume = sum(volumes[-20:]) / min(20, len(volumes)) if volumes else 0

        return {
            'volatility': volatility,
            'resistance': resistance,
            'support': support,
            'avg_volume': avg_volume,
            'current_price': closes[-1] if closes else 0,
            'price_change_percent': ((closes[-1] / closes[-2] - 1) * 100) if len(closes) > 1 else 0
        }

# Utility functions
async def create_alpha_vantage_service(api_key: str, rate_limit_delay: float = 12.0) -> AlphaVantageService:
    """Factory function to create AlphaVantageService instance"""
    return AlphaVantageService(api_key, rate_limit_delay)

def get_recommended_indicators() -> List[Dict]:
    """Get list of recommended technical indicators for analysis"""
    return [
        {'function': Function.RSI, 'time_period': 14, 'description': 'Relative Strength Index'},
        {'function': Function.MACD, 'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9, 'description': 'MACD'},
        {'function': Function.SMA, 'time_period': 20, 'description': '20-day Simple Moving Average'},
        {'function': Function.EMA, 'time_period': 20, 'description': '20-day Exponential Moving Average'},
        {'function': Function.ATR, 'time_period': 14, 'description': 'Average True Range'},
        {'function': Function.ADX, 'time_period': 14, 'description': 'Average Directional Index'},
        {'function': Function.STOCH, 'fastk_period': 14, 'slowk_period': 3, 'slowd_period': 3, 'description': 'Stochastic'},
        {'function': Function.CCI, 'time_period': 14, 'description': 'Commodity Channel Index'},
        {'function': Function.MFI, 'time_period': 14, 'description': 'Money Flow Index'},
        {'function': Function.OBV, 'description': 'On Balance Volume'}
    ]