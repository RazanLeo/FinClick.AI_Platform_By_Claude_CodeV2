"""
Yahoo Finance API Service
Handles stock data and market information for FinClick.AI platform
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
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

class Interval(Enum):
    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"

class Range(Enum):
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YTD = "ytd"
    MAX = "max"

@dataclass
class StockData:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    timestamp: Optional[datetime] = None

@dataclass
class HistoricalData:
    symbol: str
    data: List[Dict]
    period: str
    interval: str

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
                        logger.warning(f"Yahoo Finance API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class YahooFinanceService:
    """Comprehensive Yahoo Finance API service for FinClick.AI"""

    def __init__(self, rate_limit_delay: float = 0.5):
        self.base_url = "https://query1.finance.yahoo.com"
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # Cache for frequently accessed data
        self._cache = {}
        self._cache_ttl = 60  # 1 minute cache

        logger.info("Yahoo Finance service initialized")

    async def _rate_limit_check(self):
        """Ensure we don't exceed Yahoo Finance rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key for request"""
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return f"{endpoint}?{param_str}"

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

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make request to Yahoo Finance API"""
        await self._rate_limit_check()

        if params is None:
            params = {}

        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        url = f"{self.base_url}{endpoint}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self._cache_data(cache_key, data)
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Yahoo Finance API error {response.status}: {error_text}")
                    raise Exception(f"Yahoo Finance API error {response.status}: {error_text}")

    @retry_on_error()
    async def get_quote(self, symbol: str) -> StockData:
        """Get current quote for a symbol"""
        try:
            params = {
                'symbols': symbol,
                'modules': 'price,summaryDetail,defaultKeyStatistics'
            }

            response = await self._make_request('/v10/finance/quoteSummary/' + symbol, params)

            quote_summary = response.get('quoteSummary', {})
            result = quote_summary.get('result', [])

            if not result:
                raise Exception(f"No data found for symbol {symbol}")

            data = result[0]
            price_data = data.get('price', {})
            summary_detail = data.get('summaryDetail', {})
            key_stats = data.get('defaultKeyStatistics', {})

            current_price = price_data.get('regularMarketPrice', {}).get('raw', 0)
            change = price_data.get('regularMarketChange', {}).get('raw', 0)
            change_percent = price_data.get('regularMarketChangePercent', {}).get('raw', 0) * 100
            volume = price_data.get('regularMarketVolume', {}).get('raw', 0)
            market_cap = summary_detail.get('marketCap', {}).get('raw')
            pe_ratio = summary_detail.get('trailingPE', {}).get('raw')
            eps = key_stats.get('trailingEps', {}).get('raw')

            logger.info(f"Retrieved quote for {symbol}: ${current_price}")
            return StockData(
                symbol=symbol,
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=volume,
                market_cap=market_cap,
                pe_ratio=pe_ratio,
                eps=eps,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_historical_data(
        self,
        symbol: str,
        period: Range = Range.ONE_YEAR,
        interval: Interval = Interval.ONE_DAY,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> HistoricalData:
        """Get historical data for a symbol"""
        try:
            params = {
                'interval': interval.value,
                'includePrePost': 'true',
                'events': 'div,splits'
            }

            if start_date and end_date:
                params['period1'] = int(start_date.timestamp())
                params['period2'] = int(end_date.timestamp())
            else:
                params['range'] = period.value

            response = await self._make_request(f'/v8/finance/chart/{symbol}', params)

            chart = response.get('chart', {})
            result = chart.get('result', [])

            if not result:
                raise Exception(f"No historical data found for symbol {symbol}")

            data = result[0]
            timestamps = data.get('timestamp', [])
            indicators = data.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]

            opens = quote.get('open', [])
            highs = quote.get('high', [])
            lows = quote.get('low', [])
            closes = quote.get('close', [])
            volumes = quote.get('volume', [])

            historical_data = []
            for i, timestamp in enumerate(timestamps):
                if i < len(opens) and opens[i] is not None:
                    historical_data.append({
                        'date': datetime.fromtimestamp(timestamp),
                        'open': opens[i],
                        'high': highs[i],
                        'low': lows[i],
                        'close': closes[i],
                        'volume': volumes[i] if i < len(volumes) else 0
                    })

            logger.info(f"Retrieved {len(historical_data)} historical data points for {symbol}")
            return HistoricalData(
                symbol=symbol,
                data=historical_data,
                period=period.value if not start_date else f"{start_date.date()}_to_{end_date.date()}",
                interval=interval.value
            )

        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_multiple_quotes(self, symbols: List[str]) -> List[StockData]:
        """Get quotes for multiple symbols"""
        try:
            # Yahoo Finance allows up to 100 symbols per request
            chunk_size = 100
            all_quotes = []

            for i in range(0, len(symbols), chunk_size):
                chunk = symbols[i:i + chunk_size]
                symbol_string = ','.join(chunk)

                params = {
                    'symbols': symbol_string,
                    'modules': 'price,summaryDetail'
                }

                response = await self._make_request('/v10/finance/quoteSummary/' + symbol_string, params)

                quote_summary = response.get('quoteSummary', {})
                results = quote_summary.get('result', [])

                for result in results:
                    try:
                        price_data = result.get('price', {})
                        summary_detail = result.get('summaryDetail', {})

                        symbol = price_data.get('symbol', '')
                        current_price = price_data.get('regularMarketPrice', {}).get('raw', 0)
                        change = price_data.get('regularMarketChange', {}).get('raw', 0)
                        change_percent = price_data.get('regularMarketChangePercent', {}).get('raw', 0) * 100
                        volume = price_data.get('regularMarketVolume', {}).get('raw', 0)
                        market_cap = summary_detail.get('marketCap', {}).get('raw')

                        all_quotes.append(StockData(
                            symbol=symbol,
                            price=current_price,
                            change=change,
                            change_percent=change_percent,
                            volume=volume,
                            market_cap=market_cap,
                            timestamp=datetime.now()
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse quote data: {str(e)}")

                # Add delay between chunks
                if i + chunk_size < len(symbols):
                    await asyncio.sleep(self.rate_limit_delay)

            logger.info(f"Retrieved quotes for {len(all_quotes)} symbols")
            return all_quotes

        except Exception as e:
            logger.error(f"Failed to get multiple quotes: {str(e)}")
            raise

    @retry_on_error()
    async def search_symbols(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for symbols based on query"""
        try:
            params = {
                'q': query,
                'quotesCount': limit,
                'newsCount': 0,
                'enableFuzzyQuery': 'false'
            }

            response = await self._make_request('/v1/finance/search', params)

            quotes = response.get('quotes', [])
            results = []

            for quote in quotes[:limit]:
                results.append({
                    'symbol': quote.get('symbol', ''),
                    'shortname': quote.get('shortname', ''),
                    'longname': quote.get('longname', ''),
                    'exchange': quote.get('exchange', ''),
                    'type': quote.get('typeDisp', '')
                })

            logger.info(f"Found {len(results)} symbols for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Failed to search symbols for query {query}: {str(e)}")
            raise

    @retry_on_error()
    async def get_market_summary(self) -> List[Dict]:
        """Get market summary data"""
        try:
            response = await self._make_request('/v6/finance/quote/marketSummary')

            market_summary = response.get('marketSummaryResponse', {})
            results = market_summary.get('result', [])

            summary_data = []
            for result in results:
                summary_data.append({
                    'symbol': result.get('symbol', ''),
                    'fullExchangeName': result.get('fullExchangeName', ''),
                    'regularMarketPrice': result.get('regularMarketPrice', {}).get('raw', 0),
                    'regularMarketChange': result.get('regularMarketChange', {}).get('raw', 0),
                    'regularMarketChangePercent': result.get('regularMarketChangePercent', {}).get('raw', 0) * 100,
                    'regularMarketTime': datetime.fromtimestamp(result.get('regularMarketTime', 0))
                })

            logger.info(f"Retrieved market summary with {len(summary_data)} indices")
            return summary_data

        except Exception as e:
            logger.error(f"Failed to get market summary: {str(e)}")
            raise

    @retry_on_error()
    async def get_trending_symbols(self, region: str = 'US') -> List[Dict]:
        """Get trending symbols for a region"""
        try:
            params = {'region': region}
            response = await self._make_request('/v1/finance/trending/' + region, params)

            finance = response.get('finance', {})
            result = finance.get('result', [])

            if not result:
                return []

            quotes = result[0].get('quotes', [])
            trending_symbols = []

            for quote in quotes:
                trending_symbols.append({
                    'symbol': quote.get('symbol', ''),
                    'shortName': quote.get('shortName', ''),
                    'longName': quote.get('longName', ''),
                    'regularMarketPrice': quote.get('regularMarketPrice', 0),
                    'regularMarketChange': quote.get('regularMarketChange', 0),
                    'regularMarketChangePercent': quote.get('regularMarketChangePercent', 0) * 100
                })

            logger.info(f"Retrieved {len(trending_symbols)} trending symbols for {region}")
            return trending_symbols

        except Exception as e:
            logger.error(f"Failed to get trending symbols for {region}: {str(e)}")
            raise

    @retry_on_error()
    async def get_company_info(self, symbol: str) -> Dict:
        """Get detailed company information"""
        try:
            params = {
                'modules': 'assetProfile,summaryProfile,financialData,defaultKeyStatistics,calendarEvents'
            }

            response = await self._make_request(f'/v10/finance/quoteSummary/{symbol}', params)

            quote_summary = response.get('quoteSummary', {})
            result = quote_summary.get('result', [])

            if not result:
                raise Exception(f"No company info found for symbol {symbol}")

            data = result[0]
            asset_profile = data.get('assetProfile', {})
            summary_profile = data.get('summaryProfile', {})
            financial_data = data.get('financialData', {})
            key_stats = data.get('defaultKeyStatistics', {})

            company_info = {
                'symbol': symbol,
                'longName': summary_profile.get('longName', ''),
                'industry': asset_profile.get('industry', ''),
                'sector': asset_profile.get('sector', ''),
                'website': asset_profile.get('website', ''),
                'description': asset_profile.get('longBusinessSummary', ''),
                'employees': asset_profile.get('fullTimeEmployees'),
                'country': asset_profile.get('country', ''),
                'city': asset_profile.get('city', ''),
                'marketCap': key_stats.get('marketCap', {}).get('raw'),
                'enterpriseValue': key_stats.get('enterpriseValue', {}).get('raw'),
                'trailingPE': key_stats.get('trailingPE', {}).get('raw'),
                'forwardPE': key_stats.get('forwardPE', {}).get('raw'),
                'pegRatio': key_stats.get('pegRatio', {}).get('raw'),
                'priceToBook': key_stats.get('priceToBook', {}).get('raw'),
                'totalRevenue': financial_data.get('totalRevenue', {}).get('raw'),
                'revenueGrowth': financial_data.get('revenueGrowth', {}).get('raw'),
                'grossMargins': financial_data.get('grossMargins', {}).get('raw'),
                'operatingMargins': financial_data.get('operatingMargins', {}).get('raw'),
                'profitMargins': financial_data.get('profitMargins', {}).get('raw'),
                'returnOnAssets': financial_data.get('returnOnAssets', {}).get('raw'),
                'returnOnEquity': financial_data.get('returnOnEquity', {}).get('raw'),
                'totalCash': financial_data.get('totalCash', {}).get('raw'),
                'totalDebt': financial_data.get('totalDebt', {}).get('raw'),
                'debtToEquity': financial_data.get('debtToEquity', {}).get('raw'),
                'currentRatio': financial_data.get('currentRatio', {}).get('raw'),
                'quickRatio': financial_data.get('quickRatio', {}).get('raw')
            }

            logger.info(f"Retrieved company info for {symbol}")
            return company_info

        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {str(e)}")
            raise

    async def get_options_data(self, symbol: str, expiration_date: str = None) -> Dict:
        """Get options data for a symbol"""
        try:
            params = {}
            if expiration_date:
                # Convert date to timestamp
                exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
                params['date'] = int(exp_date.timestamp())

            response = await self._make_request(f'/v7/finance/options/{symbol}', params)

            options_chain = response.get('optionChain', {})
            result = options_chain.get('result', [])

            if not result:
                raise Exception(f"No options data found for symbol {symbol}")

            data = result[0]
            options = data.get('options', [])

            if not options:
                return {'calls': [], 'puts': [], 'expirationDates': data.get('expirationDates', [])}

            option_data = options[0]
            calls = option_data.get('calls', [])
            puts = option_data.get('puts', [])

            logger.info(f"Retrieved options data for {symbol}")
            return {
                'calls': calls,
                'puts': puts,
                'expirationDates': data.get('expirationDates', []),
                'underlyingSymbol': symbol,
                'quote': data.get('quote', {})
            }

        except Exception as e:
            logger.error(f"Failed to get options data for {symbol}: {str(e)}")
            raise

# Utility functions
async def create_yahoo_finance_service(rate_limit_delay: float = 0.5) -> YahooFinanceService:
    """Factory function to create YahooFinanceService instance"""
    return YahooFinanceService(rate_limit_delay)

def calculate_technical_indicators(historical_data: List[Dict]) -> Dict:
    """Calculate basic technical indicators from historical data"""
    if len(historical_data) < 20:
        return {}

    # Convert to DataFrame for easier calculation
    df = pd.DataFrame(historical_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Simple Moving Averages
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean() if len(df) >= 50 else None

    # Exponential Moving Averages
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

    # Return latest values
    latest = df.iloc[-1]
    return {
        'sma_10': latest.get('sma_10'),
        'sma_20': latest.get('sma_20'),
        'sma_50': latest.get('sma_50'),
        'ema_12': latest.get('ema_12'),
        'ema_26': latest.get('ema_26'),
        'macd': latest.get('macd'),
        'macd_signal': latest.get('macd_signal'),
        'macd_histogram': latest.get('macd_histogram'),
        'rsi': latest.get('rsi'),
        'bb_upper': latest.get('bb_upper'),
        'bb_middle': latest.get('bb_middle'),
        'bb_lower': latest.get('bb_lower'),
        'price_vs_sma_20': (latest['close'] / latest.get('sma_20') - 1) * 100 if latest.get('sma_20') else None
    }