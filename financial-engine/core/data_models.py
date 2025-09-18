"""
Data Models for Financial Analysis Engine
Defines the core data structures used throughout the analysis engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class AnalysisCategory(Enum):
    """Analysis categories as specified in the prompt"""
    CLASSICAL_FOUNDATIONAL = "classical_foundational"
    APPLIED_INTERMEDIATE = "applied_intermediate"
    ADVANCED_SOPHISTICATED = "advanced_sophisticated"


class AnalysisSubcategory(Enum):
    """Analysis subcategories"""
    # Classical Foundational
    STRUCTURAL_ANALYSIS = "structural_analysis"
    FINANCIAL_RATIOS = "financial_ratios"
    FLOW_MOVEMENT_ANALYSIS = "flow_movement_analysis"

    # Applied Intermediate
    ADVANCED_COMPARISON = "advanced_comparison"
    VALUATION_INVESTMENT = "valuation_investment"
    PERFORMANCE_EFFICIENCY = "performance_efficiency"

    # Advanced Sophisticated
    MODELING_SIMULATION = "modeling_simulation"
    STATISTICAL_QUANTITATIVE = "statistical_quantitative"
    PREDICTION_CREDIT_CLASSIFICATION = "prediction_credit_classification"
    QUANTITATIVE_RISK = "quantitative_risk"
    PORTFOLIO_INVESTMENT = "portfolio_investment"
    MERGER_ACQUISITION = "merger_acquisition"
    QUANTITATIVE_DETECTION_PREDICTION = "quantitative_detection_prediction"
    TIME_SERIES_STATISTICAL = "time_series_statistical"


class ComparisonLevel(Enum):
    """Geographic comparison levels as specified"""
    LOCAL_SAUDI = "local_saudi"
    GCC = "gcc"
    ARAB_COUNTRIES = "arab_countries"
    ASIA = "asia"
    AFRICA = "africa"
    EUROPE = "europe"
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    AUSTRALIA = "australia"
    GLOBAL = "global"


class AnalysisStatus(Enum):
    """Analysis request status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Language(Enum):
    """Supported languages"""
    ARABIC = "ar"
    ENGLISH = "en"


@dataclass
class CompanyInfo:
    """Company information structure"""
    name: str
    sector: str
    activity: str
    legal_entity: str
    analysis_years: int = 1
    comparison_level: ComparisonLevel = ComparisonLevel.LOCAL_SAUDI
    language: Language = Language.ARABIC

    # Additional metadata
    country: Optional[str] = None
    exchange: Optional[str] = None
    ticker: Optional[str] = None
    employees: Optional[int] = None
    founded_year: Optional[int] = None


@dataclass
class FinancialStatements:
    """Complete financial statements structure"""

    # Income Statement
    revenue: float = 0.0
    cost_of_goods_sold: float = 0.0
    gross_profit: float = 0.0
    operating_expenses: float = 0.0
    operating_income: float = 0.0
    interest_expense: float = 0.0
    interest_income: float = 0.0
    other_income: float = 0.0
    ebit: float = 0.0
    ebitda: float = 0.0
    depreciation: float = 0.0
    amortization: float = 0.0
    pretax_income: float = 0.0
    tax_expense: float = 0.0
    net_income: float = 0.0

    # Balance Sheet - Assets
    current_assets: float = 0.0
    cash_and_equivalents: float = 0.0
    accounts_receivable: float = 0.0
    inventory: float = 0.0
    prepaid_expenses: float = 0.0
    other_current_assets: float = 0.0

    non_current_assets: float = 0.0
    property_plant_equipment: float = 0.0
    accumulated_depreciation: float = 0.0
    intangible_assets: float = 0.0
    goodwill: float = 0.0
    investments: float = 0.0
    other_non_current_assets: float = 0.0

    total_assets: float = 0.0

    # Balance Sheet - Liabilities
    current_liabilities: float = 0.0
    accounts_payable: float = 0.0
    short_term_debt: float = 0.0
    accrued_expenses: float = 0.0
    other_current_liabilities: float = 0.0

    non_current_liabilities: float = 0.0
    long_term_debt: float = 0.0
    other_non_current_liabilities: float = 0.0

    total_liabilities: float = 0.0

    # Equity
    shareholders_equity: float = 0.0
    common_stock: float = 0.0
    retained_earnings: float = 0.0
    other_equity: float = 0.0

    # Cash Flow Statement
    operating_cash_flow: float = 0.0
    investing_cash_flow: float = 0.0
    financing_cash_flow: float = 0.0
    net_cash_flow: float = 0.0
    beginning_cash: float = 0.0
    ending_cash: float = 0.0

    # Additional metrics
    shares_outstanding: float = 0.0
    market_cap: float = 0.0
    stock_price: float = 0.0

    # Year and period information
    year: int = datetime.now().year
    period: str = "annual"  # annual, quarterly, monthly

    def __post_init__(self):
        """Calculate derived values after initialization"""
        if self.revenue and self.cost_of_goods_sold:
            self.gross_profit = self.revenue - self.cost_of_goods_sold

        if self.gross_profit and self.operating_expenses:
            self.operating_income = self.gross_profit - self.operating_expenses

        if self.operating_income:
            self.ebit = self.operating_income + self.interest_expense

        if self.ebit and self.depreciation and self.amortization:
            self.ebitda = self.ebit + self.depreciation + self.amortization


@dataclass
class BenchmarkData:
    """Industry benchmark and competitor data"""
    industry_averages: Dict[str, float] = field(default_factory=dict)
    peer_companies: List[Dict[str, Any]] = field(default_factory=list)
    market_data: Dict[str, float] = field(default_factory=dict)
    economic_indicators: Dict[str, float] = field(default_factory=dict)
    comparison_level: ComparisonLevel = ComparisonLevel.LOCAL_SAUDI


@dataclass
class AnalysisResult:
    """Individual analysis result structure"""
    analysis_name: str
    analysis_code: str
    category: AnalysisCategory
    subcategory: AnalysisSubcategory

    # Core result data
    value: Union[float, int, str, Dict, List]
    unit: str  # percentage, ratio, currency, days, times, etc.

    # Analysis context
    formula: str
    description_ar: str
    description_en: str
    interpretation_ar: str
    interpretation_en: str

    # Comparative analysis
    industry_average: Optional[float] = None
    peer_comparison: Optional[Dict[str, float]] = None
    historical_trend: Optional[List[float]] = None

    # Evaluation
    score: float = 0.0  # 0-10 scale
    rating: str = "N/A"  # Excellent, Good, Average, Poor, Critical
    rating_color: str = "#808080"  # Color code for rating

    # Risk and recommendations
    risk_level: str = "Medium"  # Low, Medium, High, Critical
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Metadata
    calculation_date: datetime = field(default_factory=datetime.now)
    confidence_level: float = 1.0  # 0-1 scale


@dataclass
class AnalysisRequest:
    """Analysis request structure"""
    request_id: str
    user_id: str
    company_info: CompanyInfo
    financial_statements: List[FinancialStatements]
    budget_statements: Optional[List[FinancialStatements]] = None

    # Analysis preferences
    selected_analyses: Optional[List[str]] = None  # If None, run all 180
    include_predictions: bool = True
    include_visualizations: bool = True

    # Output preferences
    language: Language = Language.ARABIC
    export_formats: List[str] = field(default_factory=lambda: ["pdf", "excel"])
    include_executive_summary: bool = True

    # Technical settings
    benchmark_data: Optional[BenchmarkData] = None
    custom_comparisons: Optional[List[str]] = None

    # Request metadata
    created_at: datetime = field(default_factory=datetime.now)
    status: AnalysisStatus = AnalysisStatus.PENDING


@dataclass
class ComprehensiveAnalysisReport:
    """Complete analysis report structure"""
    request_id: str
    company_info: CompanyInfo
    analysis_results: List[AnalysisResult]

    # Executive summary
    executive_summary_ar: str = ""
    executive_summary_en: str = ""

    # Overall scores and ratings
    overall_financial_health_score: float = 0.0
    liquidity_score: float = 0.0
    profitability_score: float = 0.0
    efficiency_score: float = 0.0
    leverage_score: float = 0.0
    market_score: float = 0.0

    # SWOT Analysis
    overall_strengths: List[str] = field(default_factory=list)
    overall_weaknesses: List[str] = field(default_factory=list)
    overall_opportunities: List[str] = field(default_factory=list)
    overall_threats: List[str] = field(default_factory=list)

    # Strategic recommendations
    immediate_actions: List[str] = field(default_factory=list)
    strategic_recommendations: List[str] = field(default_factory=list)
    risk_mitigation: List[str] = field(default_factory=list)

    # Report metadata
    generated_at: datetime = field(default_factory=datetime.now)
    generation_time: float = 0.0  # seconds
    language: Language = Language.ARABIC

    # File paths for generated reports
    pdf_report_path: Optional[str] = None
    excel_report_path: Optional[str] = None
    word_report_path: Optional[str] = None
    powerpoint_report_path: Optional[str] = None


# Analysis type definitions as per the prompt requirements
ANALYSIS_TYPES = {
    # Classical Foundational Analysis (106 analyses)
    "structural_analysis": [
        "vertical_analysis", "horizontal_analysis", "mixed_analysis",
        "trend_analysis", "basic_comparative_analysis", "value_added_analysis",
        "common_base_analysis", "simple_time_series_analysis", "relative_changes_analysis",
        "growth_rates_analysis", "basic_variance_analysis", "simple_variance_analysis",
        "index_numbers_analysis"
    ],

    "financial_ratios": {
        "liquidity_ratios": [
            "current_ratio", "quick_ratio", "cash_ratio", "operating_cash_flow_ratio",
            "working_capital_ratio", "defensive_interval_ratio", "cash_coverage_ratio",
            "absolute_liquidity_ratio", "free_cash_flow_ratio", "basic_liquidity_index"
        ],
        "activity_efficiency_ratios": [
            "inventory_turnover", "inventory_period", "receivables_turnover",
            "collection_period", "payables_turnover", "payment_period",
            "cash_conversion_cycle", "operating_cycle", "fixed_assets_turnover",
            "total_assets_turnover", "working_capital_turnover", "net_assets_turnover",
            "invested_capital_turnover", "equity_turnover", "total_productivity_ratio"
        ],
        "profitability_ratios": [
            "gross_profit_margin", "operating_profit_margin", "net_profit_margin",
            "ebitda_margin", "return_on_assets", "return_on_equity",
            "return_on_invested_capital", "return_on_capital_employed", "return_on_sales",
            "operating_cash_flow_margin", "earnings_per_share", "eps_growth",
            "book_value_per_share", "breakeven_point", "margin_of_safety",
            "contribution_margin", "return_on_net_assets", "sustainable_growth_rate",
            "profitability_index", "payback_period"
        ],
        "leverage_debt_ratios": [
            "debt_to_total_assets", "debt_to_equity", "debt_to_ebitda",
            "interest_coverage_ratio", "debt_service_coverage_ratio", "degree_of_operating_leverage",
            "degree_of_financial_leverage", "degree_of_combined_leverage", "equity_to_assets_ratio",
            "long_term_debt_ratio", "short_term_debt_ratio", "equity_multiplier",
            "self_financing_ratio", "financial_independence_ratio", "net_debt_ratio"
        ],
        "market_ratios": [
            "price_to_earnings", "price_to_book", "price_to_sales",
            "enterprise_value_to_ebitda", "enterprise_value_to_sales", "dividend_yield",
            "payout_ratio", "peg_ratio", "earnings_yield", "tobin_q_ratio",
            "price_to_cash_flow", "retention_ratio", "market_to_book_ratio",
            "dividend_coverage_ratio", "dividend_growth_rate"
        ]
    },

    "flow_movement_analysis": [
        "basic_cash_flow_analysis", "working_capital_analysis", "free_cash_flow_analysis",
        "earnings_quality_analysis", "accruals_index", "fixed_cost_structure_analysis",
        "variable_cost_structure_analysis", "dupont_three_factor", "dupont_five_factor",
        "economic_value_added", "market_value_added", "cash_cycle_analysis",
        "breakeven_analysis", "margin_of_safety_analysis", "operating_leverage_analysis",
        "contribution_margin_analysis", "fcff_analysis", "fcfe_analysis"
    ]
}

# Total: 180 analysis types as specified in the prompt