"""
Valuation Analysis Module
تحليل التقييم المالي

This module implements comprehensive valuation analysis including:
- Discounted Cash Flow (DCF) Analysis
- Comparable Company Analysis (Comps)
- Precedent Transaction Analysis
- Asset-Based Valuation
- Market Multiple Analysis
- Economic Value Added (EVA)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import math
from datetime import datetime, timedelta

from ..core.data_models import FinancialStatements, AnalysisResult


@dataclass
class ValuationMetrics:
    """Valuation analysis metrics"""
    # DCF Valuation
    enterprise_value: float
    equity_value: float
    intrinsic_value_per_share: float
    terminal_value: float
    dcf_multiple_years: int

    # Market Multiples
    price_to_earnings: Optional[float]
    price_to_book: Optional[float]
    price_to_sales: Optional[float]
    enterprise_value_to_ebitda: Optional[float]
    enterprise_value_to_sales: Optional[float]
    price_to_cash_flow: Optional[float]

    # Value Ratios
    market_to_book_ratio: Optional[float]
    price_to_tangible_book: Optional[float]
    dividend_yield: Optional[float]

    # Growth Metrics
    sustainable_growth_rate: float
    internal_growth_rate: float
    earnings_growth_rate: Optional[float]
    revenue_growth_rate: Optional[float]

    # Economic Value
    economic_value_added: float
    market_value_added: Optional[float]
    return_on_invested_capital: float
    weighted_average_cost_of_capital: float

    # Asset-Based Valuation
    book_value_per_share: float
    tangible_book_value_per_share: float
    liquidation_value_estimate: float


class ValuationAnalyzer:
    """Comprehensive valuation analysis engine"""

    def __init__(self):
        self.analysis_type = "valuation_analysis"
        self.category = "market_analysis"

    def analyze(self, financial_statements: FinancialStatements,
                comparison_data: Optional[Dict] = None) -> AnalysisResult:
        """
        Perform comprehensive valuation analysis
        تنفيذ تحليل شامل للتقييم المالي
        """
        try:
            # Calculate valuation metrics
            metrics = self._calculate_valuation_metrics(financial_statements)

            # Generate insights and valuation assessment
            insights = self._generate_insights(metrics, financial_statements)

            # Perform different valuation methods
            valuation_methods = self._perform_valuation_methods(financial_statements, metrics)

            # Market comparison
            market_comparison = self._compare_with_market(
                metrics, financial_statements.sector, comparison_data
            )

            # Sensitivity analysis
            sensitivity_analysis = self._perform_sensitivity_analysis(financial_statements)

            # Trend analysis
            trend_analysis = self._analyze_trends(financial_statements)

            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                metrics=metrics.__dict__,
                insights=insights,
                recommendations=self._generate_recommendations(metrics, valuation_methods),
                risk_level=self._assess_valuation_risk(metrics),
                benchmark_comparison=market_comparison,
                trend_analysis=trend_analysis,
                charts_data=self._prepare_charts_data(metrics, financial_statements),
                additional_data={
                    "valuation_methods": valuation_methods,
                    "sensitivity_analysis": sensitivity_analysis,
                    "investment_thesis": self._generate_investment_thesis(metrics, valuation_methods)
                },
                timestamp=datetime.now()
            )

        except Exception as e:
            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                error=f"Valuation analysis failed: {str(e)}",
                timestamp=datetime.now()
            )

    def _calculate_valuation_metrics(self, fs: FinancialStatements) -> ValuationMetrics:
        """Calculate all valuation metrics"""
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        # Financial statement items
        revenue = income_statement.get('revenue', 0)
        net_income = income_statement.get('net_income', 0)
        ebitda = income_statement.get('ebitda', 0)
        ebit = income_statement.get('ebit', 0)
        operating_cash_flow = cash_flow.get('operating_cash_flow', 0)
        free_cash_flow = cash_flow.get('free_cash_flow', 0)
        capital_expenditures = cash_flow.get('capital_expenditures', 0)

        total_assets = balance_sheet.get('total_assets', 0)
        total_debt = balance_sheet.get('total_debt', 0)
        cash_and_equivalents = balance_sheet.get('cash_and_cash_equivalents', 0)
        total_equity = balance_sheet.get('total_equity', 1)
        tangible_assets = total_assets - balance_sheet.get('intangible_assets', 0)

        # Share and market data
        shares_outstanding = fs.shares_outstanding or 1
        share_price = fs.share_price or 0
        market_cap = share_price * shares_outstanding if share_price else 0
        dividends_paid = cash_flow.get('dividends_paid', 0)

        # Calculate DCF components
        if free_cash_flow == 0 and operating_cash_flow > 0:
            free_cash_flow = operating_cash_flow - capital_expenditures

        # DCF Valuation (simplified 5-year model)
        dcf_years = 5
        discount_rate = self._calculate_wacc(fs)

        # Project future cash flows (simplified growth model)
        growth_rate = self._estimate_growth_rate(fs)
        terminal_growth_rate = 0.025  # 2.5% long-term growth

        future_fcfs = []
        current_fcf = free_cash_flow if free_cash_flow > 0 else net_income * 0.8  # Simplified

        for year in range(1, dcf_years + 1):
            future_fcf = current_fcf * ((1 + growth_rate) ** year)
            future_fcfs.append(future_fcf)

        # Terminal value
        terminal_fcf = future_fcfs[-1] * (1 + terminal_growth_rate)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate) if discount_rate > terminal_growth_rate else 0

        # Present value calculations
        pv_fcfs = sum([fcf / ((1 + discount_rate) ** (i + 1)) for i, fcf in enumerate(future_fcfs)])
        pv_terminal = terminal_value / ((1 + discount_rate) ** dcf_years)

        enterprise_value = pv_fcfs + pv_terminal
        equity_value = enterprise_value - total_debt + cash_and_equivalents
        intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0

        # Market multiples
        price_to_earnings = share_price / (net_income / shares_outstanding) if net_income > 0 and share_price > 0 else None
        price_to_book = share_price / (total_equity / shares_outstanding) if total_equity > 0 and share_price > 0 else None
        price_to_sales = share_price / (revenue / shares_outstanding) if revenue > 0 and share_price > 0 else None

        ev = market_cap + total_debt - cash_and_equivalents if market_cap > 0 else None
        enterprise_value_to_ebitda = ev / ebitda if ebitda > 0 and ev else None
        enterprise_value_to_sales = ev / revenue if revenue > 0 and ev else None
        price_to_cash_flow = share_price / (operating_cash_flow / shares_outstanding) if operating_cash_flow > 0 and share_price > 0 else None

        # Value ratios
        book_value_per_share = total_equity / shares_outstanding if shares_outstanding > 0 else 0
        tangible_book_value_per_share = (total_equity - balance_sheet.get('intangible_assets', 0)) / shares_outstanding if shares_outstanding > 0 else 0
        market_to_book_ratio = market_cap / total_equity if total_equity > 0 and market_cap > 0 else None
        price_to_tangible_book = share_price / tangible_book_value_per_share if tangible_book_value_per_share > 0 and share_price > 0 else None
        dividend_yield = (dividends_paid / shares_outstanding) / share_price if share_price > 0 and dividends_paid > 0 else None

        # Growth metrics
        roe = net_income / total_equity if total_equity > 0 else 0
        retention_ratio = (net_income - dividends_paid) / net_income if net_income > 0 else 0
        sustainable_growth_rate = roe * retention_ratio

        roa = net_income / total_assets if total_assets > 0 else 0
        internal_growth_rate = roa * retention_ratio

        earnings_growth_rate = self._calculate_growth_rate(fs, 'net_income')
        revenue_growth_rate = self._calculate_growth_rate(fs, 'revenue')

        # Economic value metrics
        invested_capital = total_equity + total_debt
        roic = ebit * (1 - 0.25) / invested_capital if invested_capital > 0 else 0  # Assuming 25% tax rate
        economic_value_added = (roic - discount_rate) * invested_capital
        market_value_added = market_cap - total_equity if market_cap > 0 else None

        # Asset-based valuation
        liquidation_value_estimate = self._estimate_liquidation_value(balance_sheet)

        return ValuationMetrics(
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            intrinsic_value_per_share=intrinsic_value_per_share,
            terminal_value=terminal_value,
            dcf_multiple_years=dcf_years,
            price_to_earnings=price_to_earnings,
            price_to_book=price_to_book,
            price_to_sales=price_to_sales,
            enterprise_value_to_ebitda=enterprise_value_to_ebitda,
            enterprise_value_to_sales=enterprise_value_to_sales,
            price_to_cash_flow=price_to_cash_flow,
            market_to_book_ratio=market_to_book_ratio,
            price_to_tangible_book=price_to_tangible_book,
            dividend_yield=dividend_yield,
            sustainable_growth_rate=sustainable_growth_rate,
            internal_growth_rate=internal_growth_rate,
            earnings_growth_rate=earnings_growth_rate,
            revenue_growth_rate=revenue_growth_rate,
            economic_value_added=economic_value_added,
            market_value_added=market_value_added,
            return_on_invested_capital=roic,
            weighted_average_cost_of_capital=discount_rate,
            book_value_per_share=book_value_per_share,
            tangible_book_value_per_share=tangible_book_value_per_share,
            liquidation_value_estimate=liquidation_value_estimate
        )

    def _calculate_wacc(self, fs: FinancialStatements) -> float:
        """Calculate Weighted Average Cost of Capital"""
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement

        total_debt = balance_sheet.get('total_debt', 0)
        total_equity = balance_sheet.get('total_equity', 1)
        total_capital = total_debt + total_equity

        # Cost of debt (simplified)
        interest_expense = income_statement.get('interest_expense', 0)
        cost_of_debt = interest_expense / total_debt if total_debt > 0 else 0.05
        tax_rate = 0.25  # Assumed corporate tax rate

        # Cost of equity (simplified CAPM)
        risk_free_rate = 0.03  # Assumed risk-free rate
        market_risk_premium = 0.06  # Assumed market risk premium
        beta = fs.beta if hasattr(fs, 'beta') else 1.0  # Default beta
        cost_of_equity = risk_free_rate + beta * market_risk_premium

        # WACC calculation
        weight_debt = total_debt / total_capital if total_capital > 0 else 0
        weight_equity = total_equity / total_capital if total_capital > 0 else 1

        wacc = (weight_debt * cost_of_debt * (1 - tax_rate)) + (weight_equity * cost_of_equity)

        return max(0.05, min(0.20, wacc))  # Bound between 5% and 20%

    def _estimate_growth_rate(self, fs: FinancialStatements) -> float:
        """Estimate sustainable growth rate for projections"""
        # Try multiple methods and take average
        growth_rates = []

        # Historical revenue growth
        revenue_growth = self._calculate_growth_rate(fs, 'revenue')
        if revenue_growth is not None and -0.5 <= revenue_growth <= 1.0:  # Reasonable bounds
            growth_rates.append(revenue_growth)

        # Historical earnings growth
        earnings_growth = self._calculate_growth_rate(fs, 'net_income')
        if earnings_growth is not None and -0.5 <= earnings_growth <= 1.0:
            growth_rates.append(earnings_growth)

        # Sustainable growth rate
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        net_income = income_statement.get('net_income', 0)
        total_equity = balance_sheet.get('total_equity', 1)
        dividends_paid = cash_flow.get('dividends_paid', 0)

        if net_income > 0 and total_equity > 0:
            roe = net_income / total_equity
            retention_ratio = (net_income - dividends_paid) / net_income if net_income > 0 else 0
            sustainable_growth = roe * retention_ratio
            if 0 <= sustainable_growth <= 0.5:  # Reasonable bounds
                growth_rates.append(sustainable_growth)

        # Industry average (simplified)
        sector = fs.sector.lower() if fs.sector else 'default'
        industry_growth = {
            'technology': 0.15,
            'healthcare': 0.12,
            'consumer': 0.08,
            'industrial': 0.06,
            'utilities': 0.04,
            'default': 0.06
        }
        growth_rates.append(industry_growth.get(sector, 0.06))

        # Return weighted average with more weight on recent performance
        if growth_rates:
            # Give more weight to historical data if available
            if len(growth_rates) > 1:
                weights = [0.4, 0.4, 0.2] if len(growth_rates) >= 3 else [0.6, 0.4]
                return np.average(growth_rates[:len(weights)], weights=weights)
            else:
                return growth_rates[0]

        return 0.05  # Default 5% growth

    def _calculate_growth_rate(self, fs: FinancialStatements, metric: str) -> Optional[float]:
        """Calculate historical growth rate for a metric"""
        if not fs.historical_data or len(fs.historical_data) < 2:
            return None

        values = []

        # Get current value
        current_value = fs.income_statement.get(metric, 0)
        values.append(current_value)

        # Get historical values
        for hist_fs in fs.historical_data[-3:]:  # Last 3 years max
            hist_value = hist_fs.income_statement.get(metric, 0)
            values.append(hist_value)

        if len(values) < 2:
            return None

        # Calculate compound annual growth rate (CAGR)
        values.reverse()  # Oldest to newest

        if values[0] <= 0 or values[-1] <= 0:
            return None

        years = len(values) - 1
        cagr = (values[-1] / values[0]) ** (1 / years) - 1

        return cagr if -0.5 <= cagr <= 1.0 else None  # Reasonable bounds

    def _estimate_liquidation_value(self, balance_sheet: Dict[str, float]) -> float:
        """Estimate liquidation value of assets"""
        # Simplified liquidation value estimation
        cash = balance_sheet.get('cash_and_cash_equivalents', 0)
        receivables = balance_sheet.get('accounts_receivable', 0)
        inventory = balance_sheet.get('inventory', 0)
        ppe = balance_sheet.get('property_plant_equipment', 0)
        other_assets = balance_sheet.get('other_assets', 0)

        # Apply liquidation discounts
        liquidation_value = (
            cash * 1.0 +  # Cash at full value
            receivables * 0.85 +  # 15% discount on receivables
            inventory * 0.50 +  # 50% discount on inventory
            ppe * 0.60 +  # 40% discount on fixed assets
            other_assets * 0.25  # 75% discount on other assets
        )

        return liquidation_value

    def _perform_valuation_methods(self, fs: FinancialStatements, metrics: ValuationMetrics) -> Dict[str, Any]:
        """Perform multiple valuation methods"""
        valuation_methods = {}

        # DCF Valuation
        valuation_methods["dcf"] = {
            "method_name_ar": "التدفق النقدي المخصوم",
            "method_name_en": "Discounted Cash Flow",
            "enterprise_value": metrics.enterprise_value,
            "equity_value": metrics.equity_value,
            "value_per_share": metrics.intrinsic_value_per_share,
            "confidence": "medium",
            "assumptions": {
                "growth_rate": self._estimate_growth_rate(fs),
                "terminal_growth": 0.025,
                "discount_rate": metrics.weighted_average_cost_of_capital
            }
        }

        # Comparable Company Analysis (using multiples)
        if metrics.price_to_earnings:
            # Industry P/E multiples (simplified)
            sector = fs.sector.lower() if fs.sector else 'default'
            industry_pe = {
                'technology': 25.0,
                'healthcare': 20.0,
                'consumer': 18.0,
                'industrial': 15.0,
                'utilities': 12.0,
                'default': 16.0
            }

            benchmark_pe = industry_pe.get(sector, 16.0)
            earnings_per_share = fs.income_statement.get('net_income', 0) / (fs.shares_outstanding or 1)
            comparable_value = earnings_per_share * benchmark_pe

            valuation_methods["comparable"] = {
                "method_name_ar": "مقارنة الشركات",
                "method_name_en": "Comparable Company Analysis",
                "value_per_share": comparable_value,
                "multiple_used": "P/E",
                "industry_multiple": benchmark_pe,
                "company_multiple": metrics.price_to_earnings,
                "confidence": "high" if abs(metrics.price_to_earnings - benchmark_pe) / benchmark_pe < 0.3 else "medium"
            }

        # Asset-Based Valuation
        valuation_methods["asset_based"] = {
            "method_name_ar": "القيمة المبنية على الأصول",
            "method_name_en": "Asset-Based Valuation",
            "book_value_per_share": metrics.book_value_per_share,
            "tangible_book_value_per_share": metrics.tangible_book_value_per_share,
            "liquidation_value_per_share": metrics.liquidation_value_estimate / (fs.shares_outstanding or 1),
            "confidence": "high"
        }

        # Economic Value Added approach
        if metrics.economic_value_added > 0:
            # Simplified EVA-based valuation
            eva_multiple = 10  # Simplified multiple
            eva_value_per_share = metrics.economic_value_added / (fs.shares_outstanding or 1) * eva_multiple

            valuation_methods["eva"] = {
                "method_name_ar": "القيمة الاقتصادية المضافة",
                "method_name_en": "Economic Value Added",
                "value_per_share": eva_value_per_share,
                "eva_amount": metrics.economic_value_added,
                "confidence": "medium"
            }

        return valuation_methods

    def _compare_with_market(self, metrics: ValuationMetrics, sector: str,
                           comparison_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Compare valuation with market benchmarks"""
        # Industry benchmark multiples
        benchmarks = {
            "technology": {
                "pe_ratio": {"min": 15, "max": 35, "median": 25},
                "pb_ratio": {"min": 2, "max": 8, "median": 4},
                "ev_ebitda": {"min": 10, "max": 25, "median": 18},
                "ps_ratio": {"min": 3, "max": 12, "median": 6}
            },
            "healthcare": {
                "pe_ratio": {"min": 12, "max": 28, "median": 20},
                "pb_ratio": {"min": 1.5, "max": 6, "median": 3},
                "ev_ebitda": {"min": 8, "max": 20, "median": 15},
                "ps_ratio": {"min": 2, "max": 8, "median": 4}
            },
            "consumer": {
                "pe_ratio": {"min": 10, "max": 25, "median": 18},
                "pb_ratio": {"min": 1, "max": 4, "median": 2.5},
                "ev_ebitda": {"min": 6, "max": 15, "median": 12},
                "ps_ratio": {"min": 0.5, "max": 3, "median": 1.5}
            },
            "default": {
                "pe_ratio": {"min": 8, "max": 22, "median": 16},
                "pb_ratio": {"min": 0.8, "max": 3.5, "median": 2},
                "ev_ebitda": {"min": 5, "max": 15, "median": 10},
                "ps_ratio": {"min": 0.5, "max": 4, "median": 2}
            }
        }

        sector_benchmarks = benchmarks.get(sector.lower(), benchmarks["default"])
        comparison = {}

        # Compare P/E ratio
        if metrics.price_to_earnings:
            pe_benchmark = sector_benchmarks["pe_ratio"]
            comparison["pe_ratio"] = {
                "value": metrics.price_to_earnings,
                "benchmark_min": pe_benchmark["min"],
                "benchmark_max": pe_benchmark["max"],
                "benchmark_median": pe_benchmark["median"],
                "relative_position": self._calculate_relative_position(
                    metrics.price_to_earnings, pe_benchmark["min"], pe_benchmark["max"], pe_benchmark["median"]
                )
            }

        # Compare P/B ratio
        if metrics.price_to_book:
            pb_benchmark = sector_benchmarks["pb_ratio"]
            comparison["pb_ratio"] = {
                "value": metrics.price_to_book,
                "benchmark_min": pb_benchmark["min"],
                "benchmark_max": pb_benchmark["max"],
                "benchmark_median": pb_benchmark["median"],
                "relative_position": self._calculate_relative_position(
                    metrics.price_to_book, pb_benchmark["min"], pb_benchmark["max"], pb_benchmark["median"]
                )
            }

        # Compare EV/EBITDA
        if metrics.enterprise_value_to_ebitda:
            evebitda_benchmark = sector_benchmarks["ev_ebitda"]
            comparison["ev_ebitda"] = {
                "value": metrics.enterprise_value_to_ebitda,
                "benchmark_min": evebitda_benchmark["min"],
                "benchmark_max": evebitda_benchmark["max"],
                "benchmark_median": evebitda_benchmark["median"],
                "relative_position": self._calculate_relative_position(
                    metrics.enterprise_value_to_ebitda, evebitda_benchmark["min"],
                    evebitda_benchmark["max"], evebitda_benchmark["median"]
                )
            }

        return comparison

    def _calculate_relative_position(self, value: float, min_val: float, max_val: float, median: float) -> str:
        """Calculate relative position within benchmark range"""
        if value < min_val:
            return "below_range"
        elif value > max_val:
            return "above_range"
        elif value < median:
            return "below_median"
        else:
            return "above_median"

    def _perform_sensitivity_analysis(self, fs: FinancialStatements) -> Dict[str, Any]:
        """Perform sensitivity analysis on key valuation drivers"""
        base_growth = self._estimate_growth_rate(fs)
        base_wacc = self._calculate_wacc(fs)

        sensitivity_scenarios = {}

        # Growth rate sensitivity
        growth_scenarios = [base_growth - 0.02, base_growth, base_growth + 0.02]
        wacc_scenarios = [base_wacc - 0.01, base_wacc, base_wacc + 0.01]

        valuation_matrix = []
        for growth in growth_scenarios:
            row = []
            for wacc in wacc_scenarios:
                # Simplified DCF calculation for sensitivity
                mock_fs = fs  # Use existing FS
                mock_metrics = self._calculate_simplified_dcf(mock_fs, growth, wacc)
                row.append(mock_metrics)
            valuation_matrix.append(row)

        sensitivity_scenarios["dcf_sensitivity"] = {
            "growth_rates": growth_scenarios,
            "discount_rates": wacc_scenarios,
            "valuation_matrix": valuation_matrix,
            "base_case": valuation_matrix[1][1]  # Middle scenario
        }

        return sensitivity_scenarios

    def _calculate_simplified_dcf(self, fs: FinancialStatements, growth_rate: float, wacc: float) -> float:
        """Simplified DCF calculation for sensitivity analysis"""
        cash_flow = fs.cash_flow_statement
        free_cash_flow = cash_flow.get('free_cash_flow', 0)

        if free_cash_flow <= 0:
            # Estimate FCF from net income
            net_income = fs.income_statement.get('net_income', 0)
            free_cash_flow = net_income * 0.8  # Simplified assumption

        # 5-year projection
        years = 5
        terminal_growth = 0.025

        future_fcfs = []
        for year in range(1, years + 1):
            future_fcf = free_cash_flow * ((1 + growth_rate) ** year)
            future_fcfs.append(future_fcf)

        # Terminal value
        terminal_fcf = future_fcfs[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth) if wacc > terminal_growth else 0

        # Present values
        pv_fcfs = sum([fcf / ((1 + wacc) ** (i + 1)) for i, fcf in enumerate(future_fcfs)])
        pv_terminal = terminal_value / ((1 + wacc) ** years)

        enterprise_value = pv_fcfs + pv_terminal

        # Convert to equity value
        total_debt = fs.balance_sheet.get('total_debt', 0)
        cash = fs.balance_sheet.get('cash_and_cash_equivalents', 0)
        equity_value = enterprise_value - total_debt + cash

        shares_outstanding = fs.shares_outstanding or 1
        value_per_share = equity_value / shares_outstanding

        return value_per_share

    def _generate_insights(self, metrics: ValuationMetrics, fs: FinancialStatements) -> List[Dict[str, Any]]:
        """Generate valuation insights"""
        insights = []

        # DCF vs Market Price comparison
        if fs.share_price and metrics.intrinsic_value_per_share > 0:
            price_difference = (metrics.intrinsic_value_per_share - fs.share_price) / fs.share_price

            if price_difference > 0.2:  # 20% undervalued
                insights.append({
                    "type": "positive",
                    "title_ar": "السهم مقوم بأقل من قيمته",
                    "title_en": "Stock Appears Undervalued",
                    "description_ar": f"القيمة الجوهرية {metrics.intrinsic_value_per_share:.2f} أعلى من سعر السوق {fs.share_price:.2f}",
                    "description_en": f"Intrinsic value of {metrics.intrinsic_value_per_share:.2f} exceeds market price of {fs.share_price:.2f}",
                    "impact": "positive",
                    "metric": "intrinsic_value_vs_market",
                    "value": price_difference
                })
            elif price_difference < -0.2:  # 20% overvalued
                insights.append({
                    "type": "warning",
                    "title_ar": "السهم مقوم بأكثر من قيمته",
                    "title_en": "Stock Appears Overvalued",
                    "description_ar": f"سعر السوق {fs.share_price:.2f} أعلى من القيمة الجوهرية {metrics.intrinsic_value_per_share:.2f}",
                    "description_en": f"Market price of {fs.share_price:.2f} exceeds intrinsic value of {metrics.intrinsic_value_per_share:.2f}",
                    "impact": "negative",
                    "metric": "intrinsic_value_vs_market",
                    "value": price_difference
                })

        # P/E Analysis
        if metrics.price_to_earnings:
            if metrics.price_to_earnings > 30:
                insights.append({
                    "type": "warning",
                    "title_ar": "نسبة سعر إلى ربحية مرتفعة",
                    "title_en": "High P/E Ratio",
                    "description_ar": f"نسبة P/E {metrics.price_to_earnings:.1f} مرتفعة قد تشير إلى مبالغة في التقييم",
                    "description_en": f"P/E ratio of {metrics.price_to_earnings:.1f} is high, may indicate overvaluation",
                    "impact": "medium",
                    "metric": "price_to_earnings",
                    "value": metrics.price_to_earnings
                })
            elif metrics.price_to_earnings < 10:
                insights.append({
                    "type": "positive",
                    "title_ar": "نسبة سعر إلى ربحية منخفضة",
                    "title_en": "Low P/E Ratio",
                    "description_ar": f"نسبة P/E {metrics.price_to_earnings:.1f} منخفضة قد تشير إلى فرصة استثمارية",
                    "description_en": f"P/E ratio of {metrics.price_to_earnings:.1f} is low, may indicate investment opportunity",
                    "impact": "positive",
                    "metric": "price_to_earnings",
                    "value": metrics.price_to_earnings
                })

        # Economic Value Added Analysis
        if metrics.economic_value_added > 0:
            insights.append({
                "type": "positive",
                "title_ar": "قيمة اقتصادية مضافة إيجابية",
                "title_en": "Positive Economic Value Added",
                "description_ar": f"القيمة الاقتصادية المضافة {metrics.economic_value_added:,.0f} تشير إلى خلق قيمة",
                "description_en": f"Economic Value Added of {metrics.economic_value_added:,.0f} indicates value creation",
                "impact": "positive",
                "metric": "economic_value_added",
                "value": metrics.economic_value_added
            })
        else:
            insights.append({
                "type": "warning",
                "title_ar": "قيمة اقتصادية مضافة سالبة",
                "title_en": "Negative Economic Value Added",
                "description_ar": f"القيمة الاقتصادية المضافة {metrics.economic_value_added:,.0f} تشير إلى تدمير قيمة",
                "description_en": f"Economic Value Added of {metrics.economic_value_added:,.0f} indicates value destruction",
                "impact": "negative",
                "metric": "economic_value_added",
                "value": metrics.economic_value_added
            })

        # Growth Analysis
        if metrics.sustainable_growth_rate > 0.15:
            insights.append({
                "type": "positive",
                "title_ar": "معدل نمو مستدام مرتفع",
                "title_en": "High Sustainable Growth Rate",
                "description_ar": f"معدل النمو المستدام {metrics.sustainable_growth_rate:.1%} يشير إلى إمكانات نمو قوية",
                "description_en": f"Sustainable growth rate of {metrics.sustainable_growth_rate:.1%} indicates strong growth potential",
                "impact": "positive",
                "metric": "sustainable_growth_rate",
                "value": metrics.sustainable_growth_rate
            })

        return insights

    def _assess_valuation_risk(self, metrics: ValuationMetrics) -> str:
        """Assess overall valuation risk level"""
        risk_factors = []

        # High multiples indicate higher risk
        if metrics.price_to_earnings and metrics.price_to_earnings > 25:
            risk_factors.append("high_pe_multiple")

        if metrics.price_to_book and metrics.price_to_book > 4:
            risk_factors.append("high_pb_multiple")

        # Negative EVA indicates value destruction risk
        if metrics.economic_value_added < 0:
            risk_factors.append("negative_eva")

        # Low growth indicates limited upside
        if metrics.sustainable_growth_rate < 0.05:
            risk_factors.append("low_growth_potential")

        # High WACC indicates higher required returns
        if metrics.weighted_average_cost_of_capital > 0.12:
            risk_factors.append("high_cost_of_capital")

        # Determine overall risk
        if len(risk_factors) >= 3:
            return "high"
        elif len(risk_factors) >= 1:
            return "medium"
        else:
            return "low"

    def _analyze_trends(self, fs: FinancialStatements) -> Dict[str, Any]:
        """Analyze valuation trends over time"""
        if not fs.historical_data or len(fs.historical_data) < 2:
            return {"trend_available": False}

        trends = {}

        # Calculate historical valuation metrics
        historical_metrics = []
        for historical_fs in fs.historical_data:
            try:
                metrics = self._calculate_valuation_metrics(historical_fs)
                historical_metrics.append(metrics)
            except:
                continue

        if len(historical_metrics) < 2:
            return {"trend_available": False}

        # P/E trend
        pe_values = [m.price_to_earnings for m in historical_metrics if m.price_to_earnings]
        if pe_values:
            trends["pe_trend"] = self._calculate_trend(pe_values)

        # P/B trend
        pb_values = [m.price_to_book for m in historical_metrics if m.price_to_book]
        if pb_values:
            trends["pb_trend"] = self._calculate_trend(pb_values)

        # Growth trend
        growth_values = [m.sustainable_growth_rate for m in historical_metrics]
        trends["growth_trend"] = self._calculate_trend(growth_values)

        # EVA trend
        eva_values = [m.economic_value_added for m in historical_metrics]
        trends["eva_trend"] = self._calculate_trend(eva_values)

        return {
            "trend_available": True,
            "trends": trends,
            "periods_analyzed": len(historical_metrics)
        }

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength"""
        if len(values) < 2:
            return {"direction": "stable", "strength": 0}

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if abs(slope) < 0.01:
            direction = "stable"
            strength = 0
        elif slope > 0:
            direction = "improving"
            strength = min(abs(slope) * 10, 10)
        else:
            direction = "declining"
            strength = min(abs(slope) * 10, 10)

        return {
            "direction": direction,
            "strength": strength,
            "slope": slope,
            "latest_value": values[-1],
            "previous_value": values[-2] if len(values) >= 2 else None
        }

    def _generate_investment_thesis(self, metrics: ValuationMetrics, valuation_methods: Dict) -> Dict[str, Any]:
        """Generate investment thesis based on valuation analysis"""
        thesis_points = []
        overall_recommendation = "hold"  # Default

        # DCF-based assessment
        if "dcf" in valuation_methods:
            dcf_value = valuation_methods["dcf"]["value_per_share"]
            if dcf_value > 0:
                thesis_points.append({
                    "point_ar": f"القيمة الجوهرية من تحليل DCF: {dcf_value:.2f}",
                    "point_en": f"DCF intrinsic value: {dcf_value:.2f}",
                    "weight": "high"
                })

        # Growth assessment
        if metrics.sustainable_growth_rate > 0.10:
            thesis_points.append({
                "point_ar": f"معدل نمو مستدام قوي: {metrics.sustainable_growth_rate:.1%}",
                "point_en": f"Strong sustainable growth rate: {metrics.sustainable_growth_rate:.1%}",
                "weight": "medium"
            })

        # Value creation assessment
        if metrics.economic_value_added > 0:
            thesis_points.append({
                "point_ar": "الشركة تخلق قيمة اقتصادية مضافة إيجابية",
                "point_en": "Company creates positive economic value added",
                "weight": "high"
            })

        # Generate recommendation
        positive_factors = len([p for p in thesis_points if "قوي" in p.get("point_ar", "") or "إيجابية" in p.get("point_ar", "")])

        if positive_factors >= 2:
            overall_recommendation = "buy"
        elif positive_factors == 0:
            overall_recommendation = "sell"

        return {
            "overall_recommendation": overall_recommendation,
            "confidence_level": "medium",
            "thesis_points": thesis_points,
            "key_risks": [
                "تقلبات السوق",
                "تغيرات في معدلات النمو",
                "تغيرات في تكلفة رأس المال"
            ],
            "key_opportunities": [
                "تحسن في الكفاءة التشغيلية",
                "نمو في الأسواق الجديدة",
                "تحسن في هوامش الربح"
            ]
        }

    def _generate_recommendations(self, metrics: ValuationMetrics, valuation_methods: Dict) -> List[Dict[str, Any]]:
        """Generate valuation-based recommendations"""
        recommendations = []

        # Undervaluation recommendations
        if "dcf" in valuation_methods and "comparable" in valuation_methods:
            dcf_value = valuation_methods["dcf"]["value_per_share"]
            if dcf_value > 0:  # Stock appears undervalued
                recommendations.append({
                    "priority": "medium",
                    "category": "investment_opportunity",
                    "title_ar": "فرصة استثمارية محتملة",
                    "title_en": "Potential Investment Opportunity",
                    "description_ar": "تحليل التقييم يشير إلى أن السهم مقوم بأقل من قيمته الجوهرية",
                    "description_en": "Valuation analysis suggests the stock is undervalued relative to intrinsic value",
                    "actions_ar": [
                        "مراجعة افتراضات التقييم",
                        "تحليل المخاطر المحتملة",
                        "مقارنة مع البدائل الاستثمارية",
                        "وضع استراتيجية دخول"
                    ],
                    "actions_en": [
                        "Review valuation assumptions",
                        "Analyze potential risks",
                        "Compare with investment alternatives",
                        "Develop entry strategy"
                    ],
                    "expected_impact": "medium",
                    "timeframe": "medium_term"
                })

        # Growth strategy recommendations
        if metrics.sustainable_growth_rate < 0.08:
            recommendations.append({
                "priority": "medium",
                "category": "growth_enhancement",
                "title_ar": "تحسين استراتيجية النمو",
                "title_en": "Enhance Growth Strategy",
                "description_ar": "معدل النمو المستدام منخفض يتطلب تحسين استراتيجيات النمو",
                "description_en": "Low sustainable growth rate requires improved growth strategies",
                "actions_ar": [
                    "زيادة الاستثمار في R&D",
                    "توسيع الأسواق الجغرافية",
                    "تطوير منتجات جديدة",
                    "تحسين الكفاءة التشغيلية"
                ],
                "actions_en": [
                    "Increase R&D investment",
                    "Expand geographic markets",
                    "Develop new products",
                    "Improve operational efficiency"
                ],
                "expected_impact": "high",
                "timeframe": "long_term"
            })

        # Value creation recommendations
        if metrics.economic_value_added < 0:
            recommendations.append({
                "priority": "high",
                "category": "value_creation",
                "title_ar": "تحسين خلق القيمة",
                "title_en": "Improve Value Creation",
                "description_ar": "القيمة الاقتصادية المضافة السالبة تتطلب تحسين العائد على رأس المال",
                "description_en": "Negative economic value added requires improved return on invested capital",
                "actions_ar": [
                    "تحسين الربحية التشغيلية",
                    "تحسين كفاءة استخدام رأس المال",
                    "خفض تكلفة رأس المال",
                    "إعادة هيكلة العمليات"
                ],
                "actions_en": [
                    "Improve operating profitability",
                    "Enhance capital efficiency",
                    "Reduce cost of capital",
                    "Restructure operations"
                ],
                "expected_impact": "high",
                "timeframe": "medium_term"
            })

        return recommendations

    def _prepare_charts_data(self, metrics: ValuationMetrics, fs: FinancialStatements) -> Dict[str, Any]:
        """Prepare charts data for visualization"""
        return {
            "valuation_summary": {
                "type": "gauge_chart",
                "title_ar": "ملخص التقييم",
                "title_en": "Valuation Summary",
                "data": {
                    "intrinsic_value": metrics.intrinsic_value_per_share,
                    "market_price": fs.share_price or 0,
                    "book_value": metrics.book_value_per_share,
                    "liquidation_value": metrics.liquidation_value_estimate / (fs.shares_outstanding or 1)
                }
            },
            "valuation_multiples": {
                "type": "bar_chart",
                "title_ar": "مضاعفات التقييم",
                "title_en": "Valuation Multiples",
                "data": {
                    "labels_ar": ["P/E", "P/B", "P/S", "EV/EBITDA"],
                    "labels_en": ["P/E", "P/B", "P/S", "EV/EBITDA"],
                    "company_values": [
                        metrics.price_to_earnings or 0,
                        metrics.price_to_book or 0,
                        metrics.price_to_sales or 0,
                        metrics.enterprise_value_to_ebitda or 0
                    ],
                    "industry_benchmarks": [16, 2, 2, 10]  # Simplified benchmarks
                }
            },
            "dcf_components": {
                "type": "waterfall_chart",
                "title_ar": "مكونات التدفق النقدي المخصوم",
                "title_en": "DCF Components",
                "data": {
                    "pv_cash_flows": metrics.enterprise_value - metrics.terminal_value,
                    "terminal_value": metrics.terminal_value,
                    "enterprise_value": metrics.enterprise_value,
                    "equity_value": metrics.equity_value,
                    "value_per_share": metrics.intrinsic_value_per_share
                }
            },
            "growth_drivers": {
                "type": "radar_chart",
                "title_ar": "محركات النمو",
                "title_en": "Growth Drivers",
                "data": {
                    "labels_ar": ["النمو المستدام", "النمو الداخلي", "نمو الإيرادات", "نمو الأرباح"],
                    "labels_en": ["Sustainable Growth", "Internal Growth", "Revenue Growth", "Earnings Growth"],
                    "values": [
                        metrics.sustainable_growth_rate * 100,
                        metrics.internal_growth_rate * 100,
                        (metrics.revenue_growth_rate or 0) * 100,
                        (metrics.earnings_growth_rate or 0) * 100
                    ]
                }
            }
        }