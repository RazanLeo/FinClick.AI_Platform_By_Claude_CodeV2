"""
Financial Data APIs Integration Package
Provides unified access to all financial data services for FinClick.AI platform
"""

from .yahoo_finance_service import (
    YahooFinanceService,
    StockData,
    HistoricalData,
    Interval as YahooInterval,
    Range as YahooRange,
    create_yahoo_finance_service,
    calculate_technical_indicators
)

from .alpha_vantage_service import (
    AlphaVantageService,
    AlphaVantageData,
    Function,
    Interval as AVInterval,
    OutputSize,
    DataType,
    create_alpha_vantage_service,
    get_recommended_indicators
)

from .iex_cloud_service import (
    IEXCloudService,
    IEXQuote,
    IEXHistoricalData,
    Range as IEXRange,
    ChartRange,
    Period,
    create_iex_cloud_service,
    calculate_financial_ratios,
    analyze_price_trends
)

from .fred_service import (
    FREDService,
    FREDSeries,
    FREDObservation,
    FileType,
    Units,
    Frequency,
    AggregationMethod,
    create_fred_service,
    get_recession_indicators,
    get_inflation_indicators,
    calculate_yield_spread
)

__all__ = [
    # Yahoo Finance
    'YahooFinanceService',
    'StockData',
    'HistoricalData',
    'YahooInterval',
    'YahooRange',
    'create_yahoo_finance_service',
    'calculate_technical_indicators',

    # Alpha Vantage
    'AlphaVantageService',
    'AlphaVantageData',
    'Function',
    'AVInterval',
    'OutputSize',
    'DataType',
    'create_alpha_vantage_service',
    'get_recommended_indicators',

    # IEX Cloud
    'IEXCloudService',
    'IEXQuote',
    'IEXHistoricalData',
    'IEXRange',
    'ChartRange',
    'Period',
    'create_iex_cloud_service',
    'calculate_financial_ratios',
    'analyze_price_trends',

    # FRED
    'FREDService',
    'FREDSeries',
    'FREDObservation',
    'FileType',
    'Units',
    'Frequency',
    'AggregationMethod',
    'create_fred_service',
    'get_recession_indicators',
    'get_inflation_indicators',
    'calculate_yield_spread'
]