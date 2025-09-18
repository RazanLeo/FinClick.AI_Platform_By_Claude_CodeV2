"""
IEX Cloud API Service
Handles market data and company financials for FinClick.AI platform
"""

import aiohttp
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

class Range(Enum):
    MAX = "max"
    FIVE_YEARS = "5y"
    TWO_YEARS = "2y"
    ONE_YEAR = "1y"
    YTD = "ytd"
    SIX_MONTHS = "6m"
    THREE_MONTHS = "3m"
    ONE_MONTH = "1m"
    ONE_WEEK = "1w"
    FIVE_DAYS = "5d"
    ONE_DAY = "1d"

class ChartRange(Enum):
    INTRADAY = "1d"
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    YTD = "ytd"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    MAX = "max"

class Period(Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarter"

@dataclass
class IEXQuote:
    symbol: str
    latest_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    avg_total_volume: Optional[int] = None
    timestamp: Optional[datetime] = None

@dataclass
class IEXHistoricalData:
    symbol: str
    data: List[Dict]
    range: str

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
                        logger.warning(f"IEX Cloud API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class IEXCloudService:
    """Comprehensive IEX Cloud API service for FinClick.AI"""

    def __init__(self, api_token: str, is_sandbox: bool = False, rate_limit_delay: float = 0.1):
        self.api_token = api_token
        self.is_sandbox = is_sandbox

        if is_sandbox:
            self.base_url = "https://sandbox.iexapis.com"
        else:
            self.base_url = "https://cloud.iexapis.com"

        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # Cache for data
        self._cache = {}
        self._cache_ttl = 60  # 1 minute cache for most data

        logger.info(f"IEX Cloud service initialized ({'sandbox' if is_sandbox else 'production'} mode)")

    async def _rate_limit_check(self):
        """Ensure we don't exceed IEX Cloud rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key for request"""
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return f"{endpoint}?{param_str}"

    def _is_cache_valid(self, cache_key: str, ttl: int = None) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False

        cached_time = self._cache[cache_key]['timestamp']
        cache_ttl = ttl or self._cache_ttl
        return (time.time() - cached_time) < cache_ttl

    def _get_cached_data(self, cache_key: str, ttl: int = None) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key, ttl):
            return self._cache[cache_key]['data']
        return None

    def _cache_data(self, cache_key: str, data: Any):
        """Cache data with timestamp"""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }

    async def _make_request(self, endpoint: str, params: Dict = None, cache_ttl: int = None) -> Union[Dict, List]:
        """Make request to IEX Cloud API"""
        await self._rate_limit_check()

        if params is None:
            params = {}

        params['token'] = self.api_token

        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_cached_data(cache_key, cache_ttl)
        if cached_data:
            return cached_data

        url = f"{self.base_url}{endpoint}"

        headers = {
            'User-Agent': 'FinClick.AI/1.0'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        data = await response.json()
                    else:
                        data = await response.text()

                    self._cache_data(cache_key, data)
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"IEX Cloud API error {response.status}: {error_text}")
                    raise Exception(f"IEX Cloud API error {response.status}: {error_text}")

    @retry_on_error()
    async def get_quote(self, symbol: str) -> IEXQuote:
        """Get current quote for a symbol"""
        try:
            response = await self._make_request(f'/stable/stock/{symbol}/quote')

            quote = IEXQuote(
                symbol=response.get('symbol', symbol),
                latest_price=response.get('latestPrice', 0),
                change=response.get('change', 0),
                change_percent=response.get('changePercent', 0) * 100,
                volume=response.get('latestVolume', 0),
                market_cap=response.get('marketCap'),
                pe_ratio=response.get('peRatio'),
                week_52_high=response.get('week52High'),
                week_52_low=response.get('week52Low'),
                avg_total_volume=response.get('avgTotalVolume'),
                timestamp=datetime.now()
            )

            logger.info(f"Retrieved quote for {symbol}: ${quote.latest_price}")
            return quote

        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_multiple_quotes(self, symbols: List[str]) -> List[IEXQuote]:
        """Get quotes for multiple symbols"""
        try:
            # IEX Cloud allows batch requests
            symbol_string = ','.join(symbols)
            params = {
                'types': 'quote',
                'symbols': symbol_string
            }

            response = await self._make_request('/stable/stock/market/batch', params)

            quotes = []
            for symbol in symbols:
                if symbol in response and 'quote' in response[symbol]:
                    quote_data = response[symbol]['quote']
                    quotes.append(IEXQuote(
                        symbol=quote_data.get('symbol', symbol),
                        latest_price=quote_data.get('latestPrice', 0),
                        change=quote_data.get('change', 0),
                        change_percent=quote_data.get('changePercent', 0) * 100,
                        volume=quote_data.get('latestVolume', 0),
                        market_cap=quote_data.get('marketCap'),
                        pe_ratio=quote_data.get('peRatio'),
                        week_52_high=quote_data.get('week52High'),
                        week_52_low=quote_data.get('week52Low'),
                        avg_total_volume=quote_data.get('avgTotalVolume'),
                        timestamp=datetime.now()
                    ))

            logger.info(f"Retrieved quotes for {len(quotes)} symbols")
            return quotes

        except Exception as e:
            logger.error(f"Failed to get multiple quotes: {str(e)}")
            raise

    @retry_on_error()
    async def get_historical_data(
        self,
        symbol: str,
        range_param: ChartRange = ChartRange.ONE_YEAR,
        include_today: bool = True
    ) -> IEXHistoricalData:
        """Get historical price data for a symbol"""
        try:
            params = {
                'includeToday': str(include_today).lower()
            }

            response = await self._make_request(
                f'/stable/stock/{symbol}/chart/{range_param.value}',
                params,
                cache_ttl=300  # 5 minute cache for historical data
            )

            historical_data = []
            for item in response:
                historical_data.append({
                    'date': datetime.strptime(item['date'], '%Y-%m-%d'),
                    'open': item.get('open', 0),
                    'high': item.get('high', 0),
                    'low': item.get('low', 0),
                    'close': item.get('close', 0),
                    'volume': item.get('volume', 0),
                    'unadjusted_volume': item.get('unadjustedVolume', 0),
                    'change': item.get('change', 0),
                    'change_percent': item.get('changePercent', 0) * 100,
                    'vwap': item.get('vwap', 0)
                })

            logger.info(f"Retrieved {len(historical_data)} historical data points for {symbol}")
            return IEXHistoricalData(
                symbol=symbol,
                data=historical_data,
                range=range_param.value
            )

        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_company_info(self, symbol: str) -> Dict:
        """Get company information"""
        try:
            response = await self._make_request(
                f'/stable/stock/{symbol}/company',
                cache_ttl=3600  # 1 hour cache for company info
            )

            logger.info(f"Retrieved company info for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_key_stats(self, symbol: str) -> Dict:
        """Get key statistics for a symbol"""
        try:
            response = await self._make_request(
                f'/stable/stock/{symbol}/stats',
                cache_ttl=300  # 5 minute cache
            )

            logger.info(f"Retrieved key stats for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get key stats for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_financials(self, symbol: str, period: Period = Period.QUARTERLY) -> Dict:
        """Get financial statements"""
        try:
            params = {
                'period': period.value
            }

            response = await self._make_request(
                f'/stable/stock/{symbol}/financials',
                params,
                cache_ttl=3600  # 1 hour cache
            )

            logger.info(f"Retrieved financials for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get financials for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_balance_sheet(self, symbol: str, period: Period = Period.QUARTERLY) -> Dict:
        """Get balance sheet data"""
        try:
            params = {
                'period': period.value
            }

            response = await self._make_request(
                f'/stable/stock/{symbol}/balance-sheet',
                params,
                cache_ttl=3600  # 1 hour cache
            )

            logger.info(f"Retrieved balance sheet for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get balance sheet for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_cash_flow(self, symbol: str, period: Period = Period.QUARTERLY) -> Dict:
        """Get cash flow statement"""
        try:
            params = {
                'period': period.value
            }

            response = await self._make_request(
                f'/stable/stock/{symbol}/cash-flow',
                params,
                cache_ttl=3600  # 1 hour cache
            )

            logger.info(f"Retrieved cash flow for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get cash flow for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_earnings(self, symbol: str, last: int = 4) -> Dict:
        """Get earnings data"""
        try:
            params = {
                'last': last
            }

            response = await self._make_request(
                f'/stable/stock/{symbol}/earnings',
                params,
                cache_ttl=3600  # 1 hour cache
            )

            logger.info(f"Retrieved earnings for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get earnings for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_dividends(self, symbol: str, range_param: Range = Range.ONE_YEAR) -> Dict:
        """Get dividend data"""
        try:
            response = await self._make_request(
                f'/stable/stock/{symbol}/dividends/{range_param.value}',
                cache_ttl=3600  # 1 hour cache
            )

            logger.info(f"Retrieved dividends for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get dividends for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_splits(self, symbol: str, range_param: Range = Range.FIVE_YEARS) -> Dict:
        """Get stock split data"""
        try:
            response = await self._make_request(
                f'/stable/stock/{symbol}/splits/{range_param.value}',
                cache_ttl=3600  # 1 hour cache
            )

            logger.info(f"Retrieved splits for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get splits for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_news(self, symbol: str, last: int = 10) -> List[Dict]:
        """Get news for a symbol"""
        try:
            params = {
                'last': last
            }

            response = await self._make_request(
                f'/stable/stock/{symbol}/news',
                params,
                cache_ttl=300  # 5 minute cache
            )

            logger.info(f"Retrieved {len(response)} news articles for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get news for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_market_news(self, last: int = 10) -> List[Dict]:
        """Get general market news"""
        try:
            params = {
                'last': last
            }

            response = await self._make_request(
                '/stable/stock/market/news',
                params,
                cache_ttl=300  # 5 minute cache
            )

            logger.info(f"Retrieved {len(response)} market news articles")
            return response

        except Exception as e:
            logger.error(f"Failed to get market news: {str(e)}")
            raise

    @retry_on_error()
    async def get_sector_performance(self) -> List[Dict]:
        """Get sector performance data"""
        try:
            response = await self._make_request(
                '/stable/stock/market/sector-performance',
                cache_ttl=300  # 5 minute cache
            )

            logger.info("Retrieved sector performance data")
            return response

        except Exception as e:
            logger.error(f"Failed to get sector performance: {str(e)}")
            raise

    @retry_on_error()
    async def get_market_movers(self) -> Dict:
        """Get market movers (gainers, losers, most active)"""
        try:
            params = {
                'types': 'gainers,losers,mostactive'
            }

            response = await self._make_request(
                '/stable/stock/market/list/gainers',
                cache_ttl=300  # 5 minute cache
            )

            gainers = response

            response = await self._make_request(
                '/stable/stock/market/list/losers',
                cache_ttl=300
            )

            losers = response

            response = await self._make_request(
                '/stable/stock/market/list/mostactive',
                cache_ttl=300
            )

            most_active = response

            logger.info("Retrieved market movers data")
            return {
                'gainers': gainers,
                'losers': losers,
                'most_active': most_active
            }

        except Exception as e:
            logger.error(f"Failed to get market movers: {str(e)}")
            raise

    @retry_on_error()
    async def search_symbols(self, fragment: str) -> List[Dict]:
        """Search for symbols"""
        try:
            params = {
                'fragment': fragment
            }

            response = await self._make_request(
                '/stable/search',
                params,
                cache_ttl=3600  # 1 hour cache
            )

            logger.info(f"Found {len(response)} symbols for fragment: {fragment}")
            return response

        except Exception as e:
            logger.error(f"Failed to search symbols for fragment {fragment}: {str(e)}")
            raise

    @retry_on_error()
    async def get_crypto_quote(self, symbol: str) -> Dict:
        """Get cryptocurrency quote"""
        try:
            response = await self._make_request(
                f'/stable/crypto/{symbol}/quote',
                cache_ttl=60  # 1 minute cache
            )

            logger.info(f"Retrieved crypto quote for {symbol}")
            return response

        except Exception as e:
            logger.error(f"Failed to get crypto quote for {symbol}: {str(e)}")
            raise

    @retry_on_error()
    async def get_forex_rate(self, symbols: str) -> Dict:
        """Get forex exchange rates"""
        try:
            response = await self._make_request(
                f'/stable/fx/rate/{symbols}',
                cache_ttl=60  # 1 minute cache
            )

            logger.info(f"Retrieved forex rate for {symbols}")
            return response

        except Exception as e:
            logger.error(f"Failed to get forex rate for {symbols}: {str(e)}")
            raise

    async def get_comprehensive_data(self, symbol: str) -> Dict:
        """Get comprehensive data for a symbol"""
        try:
            results = {}

            # Get basic quote
            quote = await self.get_quote(symbol)
            results['quote'] = quote

            # Get company info
            company_info = await self.get_company_info(symbol)
            results['company'] = company_info

            # Get key stats
            key_stats = await self.get_key_stats(symbol)
            results['stats'] = key_stats

            # Get historical data
            historical = await self.get_historical_data(symbol, ChartRange.ONE_YEAR)
            results['historical'] = historical

            # Get financials
            financials = await self.get_financials(symbol)
            results['financials'] = financials

            # Get earnings
            earnings = await self.get_earnings(symbol)
            results['earnings'] = earnings

            # Get news
            news = await self.get_news(symbol, 5)
            results['news'] = news

            logger.info(f"Retrieved comprehensive data for {symbol}")
            return results

        except Exception as e:
            logger.error(f"Failed to get comprehensive data for {symbol}: {str(e)}")
            raise

    async def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        try:
            response = await self._make_request('/stable/account/usage')

            logger.info("Retrieved usage stats")
            return response

        except Exception as e:
            logger.error(f"Failed to get usage stats: {str(e)}")
            raise

# Utility functions
async def create_iex_cloud_service(
    api_token: str,
    is_sandbox: bool = False,
    rate_limit_delay: float = 0.1
) -> IEXCloudService:
    """Factory function to create IEXCloudService instance"""
    return IEXCloudService(api_token, is_sandbox, rate_limit_delay)

def calculate_financial_ratios(stats: Dict, financials: Dict = None) -> Dict:
    """Calculate additional financial ratios from IEX data"""
    ratios = {}

    try:
        # Basic ratios from stats
        if 'marketcap' in stats and 'revenue' in stats and stats['revenue']:
            ratios['price_to_sales'] = stats['marketcap'] / stats['revenue']

        if 'marketcap' in stats and 'totalCash' in stats and stats['totalCash']:
            ratios['market_cap_to_cash'] = stats['marketcap'] / stats['totalCash']

        if 'debt' in stats and 'totalCash' in stats and stats['totalCash']:
            ratios['debt_to_cash'] = stats['debt'] / stats['totalCash']

        if 'EBITDA' in stats and 'debt' in stats and stats['EBITDA']:
            ratios['debt_to_ebitda'] = stats['debt'] / stats['EBITDA']

        # Advanced ratios if financials available
        if financials and 'financials' in financials:
            recent_financial = financials['financials'][0] if financials['financials'] else {}

            if 'totalRevenue' in recent_financial and 'totalRevenue' in recent_financial and recent_financial['totalRevenue']:
                net_income = recent_financial.get('netIncome', 0)
                ratios['net_margin'] = (net_income / recent_financial['totalRevenue']) * 100

            if 'totalAssets' in recent_financial and recent_financial['totalAssets']:
                net_income = recent_financial.get('netIncome', 0)
                ratios['roa'] = (net_income / recent_financial['totalAssets']) * 100

    except (KeyError, TypeError, ZeroDivisionError) as e:
        logger.warning(f"Error calculating financial ratios: {str(e)}")

    return ratios

def analyze_price_trends(historical_data: List[Dict], periods: List[int] = [5, 10, 20, 50]) -> Dict:
    """Analyze price trends from historical data"""
    if not historical_data or len(historical_data) < max(periods):
        return {}

    # Sort by date
    sorted_data = sorted(historical_data, key=lambda x: x['date'])
    closes = [item['close'] for item in sorted_data]

    trends = {}

    for period in periods:
        if len(closes) >= period:
            recent_price = closes[-1]
            period_ago_price = closes[-period]

            change = recent_price - period_ago_price
            change_percent = (change / period_ago_price) * 100

            trends[f'{period}_day_trend'] = {
                'change': change,
                'change_percent': change_percent,
                'direction': 'up' if change > 0 else 'down' if change < 0 else 'flat'
            }

    # Calculate volatility
    if len(closes) > 1:
        returns = [(closes[i] / closes[i-1] - 1) for i in range(1, len(closes))]
        volatility = (sum([(r - sum(returns)/len(returns))**2 for r in returns]) / len(returns))**0.5
        trends['volatility'] = volatility

    return trends