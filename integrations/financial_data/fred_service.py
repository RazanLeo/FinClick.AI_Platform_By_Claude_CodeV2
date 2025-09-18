"""
Federal Reserve Economic Data (FRED) API Service
Handles economic indicators and macroeconomic data for FinClick.AI platform
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
import xml.etree.ElementTree as ET

# Configure logging
logger = logging.getLogger(__name__)

class FileType(Enum):
    JSON = "json"
    XML = "xml"

class Units(Enum):
    LIN = "lin"  # Levels (default)
    CHG = "chg"  # Change
    CH1 = "ch1"  # Change from Year Ago
    PCH = "pch"  # Percent Change
    PC1 = "pc1"  # Percent Change from Year Ago
    PCA = "pca"  # Compounded Annual Rate of Change
    CCH = "cch"  # Continuously Compounded Rate of Change
    CCA = "cca"  # Continuously Compounded Annual Rate of Change
    LOG = "log"  # Natural Log

class Frequency(Enum):
    DAILY = "d"
    WEEKLY = "w"
    BIWEEKLY = "bw"
    MONTHLY = "m"
    QUARTERLY = "q"
    SEMIANNUAL = "sa"
    ANNUAL = "a"

class AggregationMethod(Enum):
    AVERAGE = "avg"
    SUM = "sum"
    END_OF_PERIOD = "eop"

@dataclass
class FREDSeries:
    id: str
    title: str
    units: str
    frequency: str
    seasonal_adjustment: str
    last_updated: datetime
    popularity: int
    notes: Optional[str] = None

@dataclass
class FREDObservation:
    date: datetime
    value: Optional[float]
    series_id: str

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
                        logger.warning(f"FRED API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class FREDService:
    """Comprehensive FRED API service for economic data - FinClick.AI"""

    def __init__(self, api_key: str, rate_limit_delay: float = 0.1):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # Cache for data
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour cache for most economic data

        # Common economic indicators
        self.economic_indicators = {
            # GDP and Growth
            'gdp': 'GDP',  # Gross Domestic Product
            'gdp_real': 'GDPC1',  # Real GDP
            'gdp_per_capita': 'A939RX0Q048SBEA',  # Real GDP per Capita
            'gdp_growth': 'A191RL1Q225SBEA',  # Real GDP Growth Rate

            # Employment
            'unemployment': 'UNRATE',  # Unemployment Rate
            'employment': 'PAYEMS',  # All Employees: Total Nonfarm Payrolls
            'labor_force': 'CIVPART',  # Labor Force Participation Rate
            'initial_claims': 'ICSA',  # Initial Jobless Claims

            # Inflation
            'cpi': 'CPIAUCSL',  # Consumer Price Index
            'core_cpi': 'CPILFESL',  # Core CPI (less food and energy)
            'pce': 'PCE',  # Personal Consumption Expenditures
            'core_pce': 'PCEPILFE',  # Core PCE Price Index

            # Interest Rates
            'fed_funds': 'FEDFUNDS',  # Federal Funds Rate
            'treasury_10y': 'DGS10',  # 10-Year Treasury Rate
            'treasury_2y': 'DGS2',  # 2-Year Treasury Rate
            'treasury_3m': 'DGS3MO',  # 3-Month Treasury Rate

            # Money Supply
            'm1': 'M1SL',  # M1 Money Stock
            'm2': 'M2SL',  # M2 Money Stock

            # Housing
            'housing_starts': 'HOUST',  # Housing Starts
            'home_sales': 'EXHOSLUSM495S',  # Existing Home Sales
            'home_prices': 'CSUSHPISA',  # Case-Shiller Home Price Index

            # Consumer
            'retail_sales': 'RSAFS',  # Retail Sales
            'consumer_sentiment': 'UMCSENT',  # Consumer Sentiment
            'personal_income': 'PI',  # Personal Income
            'personal_spending': 'PCE',  # Personal Consumption Expenditures

            # Manufacturing
            'industrial_production': 'INDPRO',  # Industrial Production Index
            'capacity_utilization': 'TCU',  # Capacity Utilization
            'ism_manufacturing': 'NAPM',  # ISM Manufacturing PMI

            # International
            'trade_balance': 'BOPGSTB',  # Trade Balance
            'exports': 'EXPGS',  # Exports of Goods and Services
            'imports': 'IMPGS',  # Imports of Goods and Services

            # Financial Markets
            'sp500': 'SP500',  # S&P 500
            'vix': 'VIXCLS',  # VIX Volatility Index
            'dollar_index': 'DTWEXBGS',  # US Dollar Index
        }

        logger.info("FRED service initialized")

    async def _rate_limit_check(self):
        """Ensure we don't exceed FRED rate limits"""
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

    async def _make_request(self, endpoint: str, params: Dict = None, cache_ttl: int = None) -> Dict:
        """Make request to FRED API"""
        await self._rate_limit_check()

        if params is None:
            params = {}

        params['api_key'] = self.api_key
        params['file_type'] = 'json'

        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_cached_data(cache_key, cache_ttl)
        if cached_data:
            return cached_data

        url = f"{self.base_url}/{endpoint}"

        headers = {
            'User-Agent': 'FinClick.AI/1.0'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check for API errors
                    if 'error_code' in data:
                        raise Exception(f"FRED API error {data['error_code']}: {data.get('error_message', 'Unknown error')}")

                    self._cache_data(cache_key, data)
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"FRED API error {response.status}: {error_text}")
                    raise Exception(f"FRED API error {response.status}: {error_text}")

    @retry_on_error()
    async def get_series(self, series_id: str) -> FREDSeries:
        """Get information about a specific series"""
        try:
            params = {
                'series_id': series_id
            }

            response = await self._make_request('series', params, cache_ttl=86400)  # 24 hour cache

            series_data = response.get('seriess', [])
            if not series_data:
                raise Exception(f"No series found for ID: {series_id}")

            series = series_data[0]

            fred_series = FREDSeries(
                id=series.get('id', series_id),
                title=series.get('title', ''),
                units=series.get('units', ''),
                frequency=series.get('frequency', ''),
                seasonal_adjustment=series.get('seasonal_adjustment', ''),
                last_updated=datetime.strptime(series.get('last_updated', '1970-01-01'), '%Y-%m-%d'),
                popularity=int(series.get('popularity', 0)),
                notes=series.get('notes')
            )

            logger.info(f"Retrieved series info for {series_id}")
            return fred_series

        except Exception as e:
            logger.error(f"Failed to get series info for {series_id}: {str(e)}")
            raise

    @retry_on_error()
    async def get_observations(
        self,
        series_id: str,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = None,
        units: Units = Units.LIN,
        frequency: Frequency = None,
        aggregation_method: AggregationMethod = AggregationMethod.AVERAGE
    ) -> List[FREDObservation]:
        """Get observations for a series"""
        try:
            params = {
                'series_id': series_id,
                'units': units.value,
                'aggregation_method': aggregation_method.value
            }

            if start_date:
                params['observation_start'] = start_date.strftime('%Y-%m-%d')

            if end_date:
                params['observation_end'] = end_date.strftime('%Y-%m-%d')

            if limit:
                params['limit'] = limit

            if frequency:
                params['frequency'] = frequency.value

            response = await self._make_request('series/observations', params)

            observations_data = response.get('observations', [])
            observations = []

            for obs in observations_data:
                try:
                    date = datetime.strptime(obs['date'], '%Y-%m-%d')
                    value = float(obs['value']) if obs['value'] != '.' else None

                    observations.append(FREDObservation(
                        date=date,
                        value=value,
                        series_id=series_id
                    ))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse observation: {obs}, error: {str(e)}")

            logger.info(f"Retrieved {len(observations)} observations for {series_id}")
            return observations

        except Exception as e:
            logger.error(f"Failed to get observations for {series_id}: {str(e)}")
            raise

    @retry_on_error()
    async def search_series(
        self,
        search_text: str,
        limit: int = 25,
        sort_order: str = 'search_rank'
    ) -> List[FREDSeries]:
        """Search for series"""
        try:
            params = {
                'search_text': search_text,
                'limit': limit,
                'order_by': sort_order
            }

            response = await self._make_request('series/search', params, cache_ttl=3600)

            series_data = response.get('seriess', [])
            series_list = []

            for series in series_data:
                try:
                    fred_series = FREDSeries(
                        id=series.get('id', ''),
                        title=series.get('title', ''),
                        units=series.get('units', ''),
                        frequency=series.get('frequency', ''),
                        seasonal_adjustment=series.get('seasonal_adjustment', ''),
                        last_updated=datetime.strptime(series.get('last_updated', '1970-01-01'), '%Y-%m-%d'),
                        popularity=int(series.get('popularity', 0)),
                        notes=series.get('notes')
                    )
                    series_list.append(fred_series)
                except Exception as e:
                    logger.warning(f"Failed to parse series: {series}, error: {str(e)}")

            logger.info(f"Found {len(series_list)} series for search: {search_text}")
            return series_list

        except Exception as e:
            logger.error(f"Failed to search series for: {search_text}: {str(e)}")
            raise

    @retry_on_error()
    async def get_categories(self, category_id: int = 0) -> List[Dict]:
        """Get categories"""
        try:
            params = {
                'category_id': category_id
            }

            response = await self._make_request('category', params, cache_ttl=86400)

            categories = response.get('categories', [])

            logger.info(f"Retrieved {len(categories)} categories for category_id: {category_id}")
            return categories

        except Exception as e:
            logger.error(f"Failed to get categories for category_id {category_id}: {str(e)}")
            raise

    @retry_on_error()
    async def get_category_series(self, category_id: int, limit: int = 25) -> List[FREDSeries]:
        """Get series in a category"""
        try:
            params = {
                'category_id': category_id,
                'limit': limit
            }

            response = await self._make_request('category/series', params, cache_ttl=3600)

            series_data = response.get('seriess', [])
            series_list = []

            for series in series_data:
                try:
                    fred_series = FREDSeries(
                        id=series.get('id', ''),
                        title=series.get('title', ''),
                        units=series.get('units', ''),
                        frequency=series.get('frequency', ''),
                        seasonal_adjustment=series.get('seasonal_adjustment', ''),
                        last_updated=datetime.strptime(series.get('last_updated', '1970-01-01'), '%Y-%m-%d'),
                        popularity=int(series.get('popularity', 0)),
                        notes=series.get('notes')
                    )
                    series_list.append(fred_series)
                except Exception as e:
                    logger.warning(f"Failed to parse series: {series}, error: {str(e)}")

            logger.info(f"Retrieved {len(series_list)} series for category_id: {category_id}")
            return series_list

        except Exception as e:
            logger.error(f"Failed to get category series for category_id {category_id}: {str(e)}")
            raise

    async def get_economic_indicator(self, indicator_name: str, **kwargs) -> List[FREDObservation]:
        """Get data for a common economic indicator"""
        if indicator_name not in self.economic_indicators:
            raise ValueError(f"Unknown indicator: {indicator_name}. Available indicators: {list(self.economic_indicators.keys())}")

        series_id = self.economic_indicators[indicator_name]
        return await self.get_observations(series_id, **kwargs)

    async def get_multiple_indicators(
        self,
        indicators: List[str],
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, List[FREDObservation]]:
        """Get data for multiple economic indicators"""
        results = {}

        for indicator in indicators:
            try:
                if indicator in self.economic_indicators:
                    series_id = self.economic_indicators[indicator]
                    observations = await self.get_observations(
                        series_id,
                        start_date=start_date,
                        end_date=end_date
                    )
                    results[indicator] = observations
                else:
                    logger.warning(f"Unknown indicator: {indicator}")
                    results[indicator] = []

                # Add delay between requests
                await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Failed to get data for indicator {indicator}: {str(e)}")
                results[indicator] = []

        return results

    async def get_yield_curve(self, date: datetime = None) -> Dict[str, float]:
        """Get yield curve data"""
        try:
            treasury_rates = {
                '1m': 'DGS1MO',
                '3m': 'DGS3MO',
                '6m': 'DGS6MO',
                '1y': 'DGS1',
                '2y': 'DGS2',
                '3y': 'DGS3',
                '5y': 'DGS5',
                '7y': 'DGS7',
                '10y': 'DGS10',
                '20y': 'DGS20',
                '30y': 'DGS30'
            }

            yield_curve = {}

            for maturity, series_id in treasury_rates.items():
                try:
                    observations = await self.get_observations(
                        series_id,
                        start_date=date or datetime.now() - timedelta(days=7),
                        end_date=date or datetime.now(),
                        limit=1
                    )

                    if observations and observations[-1].value is not None:
                        yield_curve[maturity] = observations[-1].value

                    await asyncio.sleep(self.rate_limit_delay)

                except Exception as e:
                    logger.warning(f"Failed to get yield for {maturity}: {str(e)}")

            logger.info(f"Retrieved yield curve with {len(yield_curve)} maturities")
            return yield_curve

        except Exception as e:
            logger.error(f"Failed to get yield curve: {str(e)}")
            raise

    async def get_economic_calendar(self, days_ahead: int = 30) -> Dict[str, List[FREDObservation]]:
        """Get upcoming economic data releases"""
        try:
            end_date = datetime.now() + timedelta(days=days_ahead)

            # Key economic indicators with regular release schedules
            key_indicators = [
                'unemployment',
                'cpi',
                'gdp_growth',
                'retail_sales',
                'industrial_production'
            ]

            calendar_data = {}

            for indicator in key_indicators:
                try:
                    observations = await self.get_economic_indicator(
                        indicator,
                        start_date=datetime.now() - timedelta(days=90),
                        end_date=end_date
                    )

                    # Filter for recent data
                    recent_observations = [
                        obs for obs in observations
                        if obs.date >= datetime.now() - timedelta(days=30)
                    ]

                    calendar_data[indicator] = recent_observations

                    await asyncio.sleep(self.rate_limit_delay)

                except Exception as e:
                    logger.warning(f"Failed to get calendar data for {indicator}: {str(e)}")

            logger.info(f"Retrieved economic calendar data for {len(calendar_data)} indicators")
            return calendar_data

        except Exception as e:
            logger.error(f"Failed to get economic calendar: {str(e)}")
            raise

    def calculate_economic_trends(self, observations: List[FREDObservation], periods: List[int] = [30, 90, 365]) -> Dict:
        """Calculate trends and changes in economic data"""
        if not observations or len(observations) < 2:
            return {}

        # Sort by date
        sorted_obs = sorted(observations, key=lambda x: x.date)
        valid_obs = [obs for obs in sorted_obs if obs.value is not None]

        if len(valid_obs) < 2:
            return {}

        trends = {}
        current_value = valid_obs[-1].value
        current_date = valid_obs[-1].date

        # Calculate trends for different periods
        for period_days in periods:
            cutoff_date = current_date - timedelta(days=period_days)
            period_obs = [obs for obs in valid_obs if obs.date >= cutoff_date]

            if len(period_obs) >= 2:
                period_start_value = period_obs[0].value
                change = current_value - period_start_value
                change_percent = (change / period_start_value) * 100 if period_start_value != 0 else 0

                trends[f'{period_days}d_change'] = change
                trends[f'{period_days}d_change_percent'] = change_percent
                trends[f'{period_days}d_direction'] = 'up' if change > 0 else 'down' if change < 0 else 'flat'

        # Calculate volatility
        if len(valid_obs) > 1:
            values = [obs.value for obs in valid_obs[-30:]]  # Last 30 observations
            if len(values) > 1:
                mean_value = sum(values) / len(values)
                variance = sum([(v - mean_value) ** 2 for v in values]) / len(values)
                trends['volatility'] = variance ** 0.5

        # Calculate moving averages
        if len(valid_obs) >= 10:
            last_10_values = [obs.value for obs in valid_obs[-10:]]
            trends['10_period_avg'] = sum(last_10_values) / len(last_10_values)

        if len(valid_obs) >= 20:
            last_20_values = [obs.value for obs in valid_obs[-20:]]
            trends['20_period_avg'] = sum(last_20_values) / len(last_20_values)

        trends['current_value'] = current_value
        trends['current_date'] = current_date.isoformat()

        return trends

    def get_available_indicators(self) -> Dict[str, str]:
        """Get list of available economic indicators"""
        return self.economic_indicators.copy()

# Utility functions
async def create_fred_service(api_key: str, rate_limit_delay: float = 0.1) -> FREDService:
    """Factory function to create FREDService instance"""
    return FREDService(api_key, rate_limit_delay)

def get_recession_indicators() -> List[str]:
    """Get list of key recession indicators"""
    return [
        'gdp_growth',
        'unemployment',
        'fed_funds',
        'treasury_10y',
        'treasury_3m',
        'industrial_production',
        'retail_sales',
        'consumer_sentiment'
    ]

def get_inflation_indicators() -> List[str]:
    """Get list of key inflation indicators"""
    return [
        'cpi',
        'core_cpi',
        'pce',
        'core_pce',
        'treasury_10y',
        'fed_funds'
    ]

def calculate_yield_spread(yield_curve: Dict[str, float]) -> Dict[str, float]:
    """Calculate yield spreads from yield curve data"""
    spreads = {}

    try:
        # Common spreads
        if '10y' in yield_curve and '2y' in yield_curve:
            spreads['10y_2y_spread'] = yield_curve['10y'] - yield_curve['2y']

        if '10y' in yield_curve and '3m' in yield_curve:
            spreads['10y_3m_spread'] = yield_curve['10y'] - yield_curve['3m']

        if '30y' in yield_curve and '10y' in yield_curve:
            spreads['30y_10y_spread'] = yield_curve['30y'] - yield_curve['10y']

        if '5y' in yield_curve and '2y' in yield_curve:
            spreads['5y_2y_spread'] = yield_curve['5y'] - yield_curve['2y']

    except (KeyError, TypeError) as e:
        logger.warning(f"Error calculating yield spreads: {str(e)}")

    return spreads