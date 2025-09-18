"""
Credit Risk Analysis Module
تحليل مخاطر الائتمان

This module implements comprehensive credit risk analysis including:
- Credit Scoring Models
- Default Probability Assessment
- Credit Rating Analysis
- Debt Capacity Analysis
- Payment Behavior Analysis
- Credit Quality Metrics
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
import math
from datetime import datetime

from ..core.data_models import FinancialStatements, AnalysisResult


@dataclass
class CreditRiskMetrics:
    """Credit risk analysis metrics"""
    # Credit Ratios
    debt_to_equity_ratio: float
    debt_to_assets_ratio: float
    debt_service_coverage_ratio: float
    interest_coverage_ratio: float
    current_ratio: float
    quick_ratio: float

    # Profitability & Cash Flow
    return_on_assets: float
    operating_margin: float
    operating_cash_flow_ratio: float
    free_cash_flow_margin: float

    # Credit Scoring Components
    altman_z_score: float
    piotroski_f_score: float
    beneish_m_score: float

    # Risk Indicators
    default_probability: float
    credit_rating_score: float
    payment_capacity_ratio: float
    working_capital_adequacy: float

    # Stability Metrics
    earnings_volatility: Optional[float]
    revenue_growth_stability: Optional[float]
    cash_flow_stability: Optional[float]


class CreditRiskAnalyzer:
    """Comprehensive credit risk analysis engine"""

    def __init__(self):
        self.analysis_type = "credit_risk_analysis"
        self.category = "risk_analysis"

    def analyze(self, financial_statements: FinancialStatements,
                comparison_data: Optional[Dict] = None) -> AnalysisResult:
        """
        Perform comprehensive credit risk analysis
        تنفيذ تحليل شامل لمخاطر الائتمان
        """
        try:
            # Calculate credit risk metrics
            metrics = self._calculate_credit_risk_metrics(financial_statements)

            # Generate insights and risk assessment
            insights = self._generate_insights(metrics, financial_statements)

            # Calculate credit rating
            credit_rating = self._calculate_credit_rating(metrics)

            # Risk assessment
            risk_assessment = self._assess_credit_risk(metrics)

            # Industry comparison
            benchmark_comparison = self._compare_with_benchmarks(
                metrics, financial_statements.sector, comparison_data
            )

            # Trend analysis
            trend_analysis = self._analyze_trends(financial_statements)

            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                metrics=metrics.__dict__,
                insights=insights,
                recommendations=self._generate_recommendations(metrics, risk_assessment),
                risk_level=risk_assessment["overall_risk"],
                benchmark_comparison=benchmark_comparison,
                trend_analysis=trend_analysis,
                charts_data=self._prepare_charts_data(metrics, financial_statements),
                additional_data={
                    "credit_rating": credit_rating,
                    "default_probability": metrics.default_probability,
                    "risk_factors": risk_assessment["risk_factors"]
                },
                timestamp=datetime.now()
            )

        except Exception as e:
            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                error=f"Credit risk analysis failed: {str(e)}",
                timestamp=datetime.now()
            )

    def _calculate_credit_risk_metrics(self, fs: FinancialStatements) -> CreditRiskMetrics:
        """Calculate all credit risk metrics"""
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        # Balance Sheet items
        total_assets = balance_sheet.get('total_assets', 1)
        total_debt = balance_sheet.get('total_debt', 0)
        total_equity = balance_sheet.get('total_equity', 1)
        current_assets = balance_sheet.get('current_assets', 0)
        current_liabilities = balance_sheet.get('current_liabilities', 1)
        cash_and_equivalents = balance_sheet.get('cash_and_cash_equivalents', 0)
        short_term_investments = balance_sheet.get('short_term_investments', 0)
        inventory = balance_sheet.get('inventory', 0)
        retained_earnings = balance_sheet.get('retained_earnings', 0)

        # Income Statement items
        revenue = income_statement.get('revenue', 1)
        ebit = income_statement.get('ebit', 0)
        ebitda = income_statement.get('ebitda', 0)
        net_income = income_statement.get('net_income', 0)
        operating_income = income_statement.get('operating_income', 0)
        interest_expense = income_statement.get('interest_expense', 1)
        gross_profit = income_statement.get('gross_profit', 0)

        # Cash Flow items
        operating_cash_flow = cash_flow.get('operating_cash_flow', 0)
        capital_expenditures = cash_flow.get('capital_expenditures', 0)
        debt_service = cash_flow.get('debt_service', interest_expense)  # Simplified

        # Calculate basic credit ratios
        debt_to_equity_ratio = total_debt / total_equity if total_equity > 0 else float('inf')
        debt_to_assets_ratio = total_debt / total_assets if total_assets > 0 else 0
        debt_service_coverage_ratio = operating_cash_flow / debt_service if debt_service > 0 else float('inf')
        interest_coverage_ratio = ebit / interest_expense if interest_expense > 0 else float('inf')
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
        quick_assets = current_assets - inventory
        quick_ratio = quick_assets / current_liabilities if current_liabilities > 0 else 0

        # Profitability and cash flow metrics
        return_on_assets = net_income / total_assets if total_assets > 0 else 0
        operating_margin = operating_income / revenue if revenue > 0 else 0
        operating_cash_flow_ratio = operating_cash_flow / current_liabilities if current_liabilities > 0 else 0
        free_cash_flow = operating_cash_flow - capital_expenditures
        free_cash_flow_margin = free_cash_flow / revenue if revenue > 0 else 0

        # Calculate credit scoring models
        altman_z_score = self._calculate_altman_z_score(fs)
        piotroski_f_score = self._calculate_piotroski_f_score(fs)
        beneish_m_score = self._calculate_beneish_m_score(fs)

        # Calculate risk indicators
        default_probability = self._calculate_default_probability(fs)
        credit_rating_score = self._calculate_credit_rating_score(fs)

        # Payment capacity and working capital adequacy
        payment_capacity_ratio = operating_cash_flow / total_debt if total_debt > 0 else float('inf')
        working_capital = current_assets - current_liabilities
        working_capital_adequacy = working_capital / revenue if revenue > 0 else 0

        # Stability metrics (if historical data available)
        earnings_volatility = self._calculate_earnings_volatility(fs)
        revenue_growth_stability = self._calculate_revenue_growth_stability(fs)
        cash_flow_stability = self._calculate_cash_flow_stability(fs)

        return CreditRiskMetrics(
            debt_to_equity_ratio=debt_to_equity_ratio,
            debt_to_assets_ratio=debt_to_assets_ratio,
            debt_service_coverage_ratio=debt_service_coverage_ratio,
            interest_coverage_ratio=interest_coverage_ratio,
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            return_on_assets=return_on_assets,
            operating_margin=operating_margin,
            operating_cash_flow_ratio=operating_cash_flow_ratio,
            free_cash_flow_margin=free_cash_flow_margin,
            altman_z_score=altman_z_score,
            piotroski_f_score=piotroski_f_score,
            beneish_m_score=beneish_m_score,
            default_probability=default_probability,
            credit_rating_score=credit_rating_score,
            payment_capacity_ratio=payment_capacity_ratio,
            working_capital_adequacy=working_capital_adequacy,
            earnings_volatility=earnings_volatility,
            revenue_growth_stability=revenue_growth_stability,
            cash_flow_stability=cash_flow_stability
        )

    def _calculate_altman_z_score(self, fs: FinancialStatements) -> float:
        """Calculate Altman Z-Score for bankruptcy prediction"""
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement

        total_assets = balance_sheet.get('total_assets', 1)
        current_assets = balance_sheet.get('current_assets', 0)
        current_liabilities = balance_sheet.get('current_liabilities', 0)
        retained_earnings = balance_sheet.get('retained_earnings', 0)
        ebit = income_statement.get('ebit', 0)
        revenue = income_statement.get('revenue', 0)
        market_value_equity = balance_sheet.get('total_equity', 0)  # Simplified
        total_liabilities = balance_sheet.get('total_liabilities', 0)

        # Altman Z-Score components
        working_capital = current_assets - current_liabilities
        x1 = working_capital / total_assets if total_assets > 0 else 0
        x2 = retained_earnings / total_assets if total_assets > 0 else 0
        x3 = ebit / total_assets if total_assets > 0 else 0
        x4 = market_value_equity / total_liabilities if total_liabilities > 0 else 0
        x5 = revenue / total_assets if total_assets > 0 else 0

        # Altman Z-Score formula
        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

        return z_score

    def _calculate_piotroski_f_score(self, fs: FinancialStatements) -> float:
        """Calculate Piotroski F-Score for financial strength"""
        score = 0
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        # Profitability criteria (4 points)
        if income_statement.get('net_income', 0) > 0:
            score += 1  # Positive net income

        if income_statement.get('return_on_assets', 0) > 0:
            score += 1  # Positive ROA

        if cash_flow.get('operating_cash_flow', 0) > 0:
            score += 1  # Positive operating cash flow

        ocf = cash_flow.get('operating_cash_flow', 0)
        ni = income_statement.get('net_income', 1)
        if ocf > ni and ni > 0:
            score += 1  # Cash flow from operations > net income (quality of earnings)

        # Leverage, liquidity and source of funds criteria (3 points)
        # Simplified implementation - would need historical data for proper calculation
        current_ratio = balance_sheet.get('current_assets', 0) / balance_sheet.get('current_liabilities', 1)
        if current_ratio > 1.0:
            score += 1  # Improvement in liquidity (simplified)

        debt_ratio = balance_sheet.get('total_debt', 0) / balance_sheet.get('total_assets', 1)
        if debt_ratio < 0.4:  # Conservative debt level
            score += 1

        shares_outstanding = fs.shares_outstanding or 1
        if shares_outstanding > 0:  # No share dilution (simplified)
            score += 1

        # Operating efficiency criteria (2 points)
        # Would need historical data for proper gross margin and asset turnover trend analysis
        gross_margin = income_statement.get('gross_profit', 0) / income_statement.get('revenue', 1)
        if gross_margin > 0.3:  # Reasonable gross margin
            score += 1

        asset_turnover = income_statement.get('revenue', 0) / balance_sheet.get('total_assets', 1)
        if asset_turnover > 0.5:  # Reasonable asset utilization
            score += 1

        return score

    def _calculate_beneish_m_score(self, fs: FinancialStatements) -> float:
        """Calculate Beneish M-Score for earnings manipulation detection"""
        # Simplified implementation - would need more detailed data for full calculation
        income_statement = fs.income_statement
        balance_sheet = fs.balance_sheet

        # Using simplified proxies for M-Score variables
        revenue = income_statement.get('revenue', 1)
        total_assets = balance_sheet.get('total_assets', 1)
        receivables = balance_sheet.get('accounts_receivable', 0)

        # Simplified M-Score approximation
        receivables_to_sales = receivables / revenue if revenue > 0 else 0
        asset_quality = (total_assets - receivables) / total_assets if total_assets > 0 else 0

        # Very simplified M-Score (normally requires more complex calculations)
        m_score = -2.0 + (receivables_to_sales * 0.5) + (asset_quality * 0.3)

        return m_score

    def _calculate_default_probability(self, fs: FinancialStatements) -> float:
        """Calculate probability of default using multiple factors"""
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        # Collect risk factors
        risk_factors = []

        # Leverage risk
        debt_to_equity = balance_sheet.get('total_debt', 0) / balance_sheet.get('total_equity', 1)
        if debt_to_equity > 2.0:
            risk_factors.append(0.25)
        elif debt_to_equity > 1.0:
            risk_factors.append(0.15)
        else:
            risk_factors.append(0.05)

        # Profitability risk
        net_margin = income_statement.get('net_income', 0) / income_statement.get('revenue', 1)
        if net_margin < 0:
            risk_factors.append(0.30)
        elif net_margin < 0.05:
            risk_factors.append(0.20)
        else:
            risk_factors.append(0.05)

        # Liquidity risk
        current_ratio = balance_sheet.get('current_assets', 0) / balance_sheet.get('current_liabilities', 1)
        if current_ratio < 1.0:
            risk_factors.append(0.25)
        elif current_ratio < 1.2:
            risk_factors.append(0.15)
        else:
            risk_factors.append(0.05)

        # Cash flow risk
        operating_cf = cash_flow.get('operating_cash_flow', 0)
        revenue = income_statement.get('revenue', 1)
        cf_margin = operating_cf / revenue if revenue > 0 else 0
        if cf_margin < 0:
            risk_factors.append(0.20)
        elif cf_margin < 0.10:
            risk_factors.append(0.10)
        else:
            risk_factors.append(0.03)

        # Interest coverage risk
        ebit = income_statement.get('ebit', 0)
        interest_expense = income_statement.get('interest_expense', 1)
        interest_coverage = ebit / interest_expense if interest_expense > 0 else float('inf')
        if interest_coverage < 1.5:
            risk_factors.append(0.25)
        elif interest_coverage < 2.5:
            risk_factors.append(0.15)
        else:
            risk_factors.append(0.05)

        # Calculate weighted probability
        base_probability = np.mean(risk_factors)

        # Adjust based on Altman Z-Score if available
        z_score = self._calculate_altman_z_score(fs)
        if z_score < 1.8:
            base_probability *= 1.5  # High distress zone
        elif z_score < 3.0:
            base_probability *= 1.2  # Gray zone
        else:
            base_probability *= 0.8  # Safe zone

        return min(1.0, max(0.001, base_probability))

    def _calculate_credit_rating_score(self, fs: FinancialStatements) -> float:
        """Calculate credit rating score (0-100)"""
        score = 100.0  # Start with perfect score

        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        # Leverage penalty
        debt_to_equity = balance_sheet.get('total_debt', 0) / balance_sheet.get('total_equity', 1)
        if debt_to_equity > 3.0:
            score -= 30
        elif debt_to_equity > 2.0:
            score -= 20
        elif debt_to_equity > 1.0:
            score -= 10

        # Profitability penalty
        roa = income_statement.get('net_income', 0) / balance_sheet.get('total_assets', 1)
        if roa < 0:
            score -= 25
        elif roa < 0.02:
            score -= 15
        elif roa < 0.05:
            score -= 5

        # Liquidity penalty
        current_ratio = balance_sheet.get('current_assets', 0) / balance_sheet.get('current_liabilities', 1)
        if current_ratio < 1.0:
            score -= 20
        elif current_ratio < 1.2:
            score -= 10

        # Interest coverage penalty
        ebit = income_statement.get('ebit', 0)
        interest_expense = income_statement.get('interest_expense', 1)
        interest_coverage = ebit / interest_expense if interest_expense > 0 else float('inf')
        if interest_coverage < 2.0:
            score -= 25
        elif interest_coverage < 3.0:
            score -= 15
        elif interest_coverage < 5.0:
            score -= 5

        # Cash flow penalty
        ocf_margin = cash_flow.get('operating_cash_flow', 0) / income_statement.get('revenue', 1)
        if ocf_margin < 0:
            score -= 20
        elif ocf_margin < 0.10:
            score -= 10

        return max(0, min(100, score))

    def _calculate_earnings_volatility(self, fs: FinancialStatements) -> Optional[float]:
        """Calculate earnings volatility over time"""
        if not fs.historical_data or len(fs.historical_data) < 3:
            return None

        earnings = []
        for hist_fs in fs.historical_data:
            earnings.append(hist_fs.income_statement.get('net_income', 0))

        if len(earnings) < 3:
            return None

        # Calculate coefficient of variation
        mean_earnings = np.mean(earnings)
        if mean_earnings == 0:
            return None

        std_earnings = np.std(earnings)
        return std_earnings / abs(mean_earnings)

    def _calculate_revenue_growth_stability(self, fs: FinancialStatements) -> Optional[float]:
        """Calculate revenue growth stability"""
        if not fs.historical_data or len(fs.historical_data) < 3:
            return None

        revenues = []
        for hist_fs in fs.historical_data:
            revenues.append(hist_fs.income_statement.get('revenue', 0))

        if len(revenues) < 3:
            return None

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                growth_rate = (revenues[i] - revenues[i-1]) / revenues[i-1]
                growth_rates.append(growth_rate)

        if len(growth_rates) < 2:
            return None

        # Return standard deviation of growth rates (lower is more stable)
        return np.std(growth_rates)

    def _calculate_cash_flow_stability(self, fs: FinancialStatements) -> Optional[float]:
        """Calculate cash flow stability"""
        if not fs.historical_data or len(fs.historical_data) < 3:
            return None

        cash_flows = []
        for hist_fs in fs.historical_data:
            cash_flows.append(hist_fs.cash_flow_statement.get('operating_cash_flow', 0))

        if len(cash_flows) < 3:
            return None

        # Calculate coefficient of variation
        mean_cf = np.mean(cash_flows)
        if mean_cf == 0:
            return None

        std_cf = np.std(cash_flows)
        return std_cf / abs(mean_cf)

    def _generate_insights(self, metrics: CreditRiskMetrics, fs: FinancialStatements) -> List[Dict[str, Any]]:
        """Generate credit risk insights"""
        insights = []

        # Altman Z-Score Analysis
        if metrics.altman_z_score < 1.8:
            insights.append({
                "type": "alert",
                "title_ar": "مخاطر إفلاس عالية",
                "title_en": "High Bankruptcy Risk",
                "description_ar": f"درجة ألتمان Z {metrics.altman_z_score:.2f} تشير إلى مخاطر إفلاس عالية",
                "description_en": f"Altman Z-Score of {metrics.altman_z_score:.2f} indicates high bankruptcy risk",
                "impact": "critical",
                "metric": "altman_z_score",
                "value": metrics.altman_z_score
            })
        elif metrics.altman_z_score < 3.0:
            insights.append({
                "type": "warning",
                "title_ar": "منطقة رمادية للمخاطر",
                "title_en": "Gray Zone Risk Area",
                "description_ar": f"درجة ألتمان Z {metrics.altman_z_score:.2f} في المنطقة الرمادية",
                "description_en": f"Altman Z-Score of {metrics.altman_z_score:.2f} is in the gray zone",
                "impact": "medium",
                "metric": "altman_z_score",
                "value": metrics.altman_z_score
            })

        # Debt Analysis
        if metrics.debt_to_equity_ratio > 2.0:
            insights.append({
                "type": "alert",
                "title_ar": "نسبة ديون مرتفعة",
                "title_en": "High Debt Ratio",
                "description_ar": f"نسبة الدين إلى حقوق الملكية {metrics.debt_to_equity_ratio:.2f} مرتفعة جداً",
                "description_en": f"Debt-to-equity ratio of {metrics.debt_to_equity_ratio:.2f} is very high",
                "impact": "high",
                "metric": "debt_to_equity_ratio",
                "value": metrics.debt_to_equity_ratio
            })

        # Interest Coverage Analysis
        if metrics.interest_coverage_ratio < 2.5:
            insights.append({
                "type": "alert",
                "title_ar": "ضعف في تغطية الفوائد",
                "title_en": "Weak Interest Coverage",
                "description_ar": f"نسبة تغطية الفوائد {metrics.interest_coverage_ratio:.1f} منخفضة",
                "description_en": f"Interest coverage ratio of {metrics.interest_coverage_ratio:.1f} is low",
                "impact": "high",
                "metric": "interest_coverage_ratio",
                "value": metrics.interest_coverage_ratio
            })

        # Default Probability Analysis
        if metrics.default_probability > 0.15:
            insights.append({
                "type": "alert",
                "title_ar": "احتمالية إفلاس عالية",
                "title_en": "High Default Probability",
                "description_ar": f"احتمالية الإفلاس {metrics.default_probability:.1%} عالية",
                "description_en": f"Default probability of {metrics.default_probability:.1%} is high",
                "impact": "critical",
                "metric": "default_probability",
                "value": metrics.default_probability
            })

        # Credit Rating Analysis
        if metrics.credit_rating_score < 50:
            insights.append({
                "type": "alert",
                "title_ar": "تصنيف ائتماني ضعيف",
                "title_en": "Poor Credit Rating",
                "description_ar": f"درجة التصنيف الائتماني {metrics.credit_rating_score:.0f} ضعيفة",
                "description_en": f"Credit rating score of {metrics.credit_rating_score:.0f} is poor",
                "impact": "high",
                "metric": "credit_rating_score",
                "value": metrics.credit_rating_score
            })

        return insights

    def _calculate_credit_rating(self, metrics: CreditRiskMetrics) -> Dict[str, Any]:
        """Calculate credit rating based on metrics"""
        score = metrics.credit_rating_score

        if score >= 90:
            rating = "AAA"
            grade = "investment_grade"
            description_ar = "ممتاز - مخاطر ائتمانية منخفضة جداً"
            description_en = "Excellent - Very low credit risk"
        elif score >= 80:
            rating = "AA"
            grade = "investment_grade"
            description_ar = "جيد جداً - مخاطر ائتمانية منخفضة"
            description_en = "Very Good - Low credit risk"
        elif score >= 70:
            rating = "A"
            grade = "investment_grade"
            description_ar = "جيد - مخاطر ائتمانية محدودة"
            description_en = "Good - Limited credit risk"
        elif score >= 60:
            rating = "BBB"
            grade = "investment_grade"
            description_ar = "مقبول - مخاطر ائتمانية متوسطة"
            description_en = "Acceptable - Moderate credit risk"
        elif score >= 50:
            rating = "BB"
            grade = "speculative_grade"
            description_ar = "مضاربي - مخاطر ائتمانية عالية"
            description_en = "Speculative - High credit risk"
        elif score >= 40:
            rating = "B"
            grade = "speculative_grade"
            description_ar = "مضاربي عالي - مخاطر ائتمانية عالية جداً"
            description_en = "Highly Speculative - Very high credit risk"
        else:
            rating = "C"
            grade = "default_risk"
            description_ar = "مخاطر إفلاس - مخاطر ائتمانية حرجة"
            description_en = "Default Risk - Critical credit risk"

        return {
            "rating": rating,
            "grade": grade,
            "score": score,
            "description_ar": description_ar,
            "description_en": description_en
        }

    def _assess_credit_risk(self, metrics: CreditRiskMetrics) -> Dict[str, Any]:
        """Assess overall credit risk"""
        risk_factors = []
        risk_scores = []

        # Leverage risk
        if metrics.debt_to_equity_ratio > 2.0:
            risk_factors.append("high_leverage")
            risk_scores.append(8)
        elif metrics.debt_to_equity_ratio > 1.0:
            risk_factors.append("moderate_leverage")
            risk_scores.append(5)

        # Profitability risk
        if metrics.return_on_assets < 0:
            risk_factors.append("negative_profitability")
            risk_scores.append(9)
        elif metrics.return_on_assets < 0.02:
            risk_factors.append("low_profitability")
            risk_scores.append(6)

        # Liquidity risk
        if metrics.current_ratio < 1.0:
            risk_factors.append("liquidity_stress")
            risk_scores.append(8)
        elif metrics.current_ratio < 1.2:
            risk_factors.append("liquidity_concern")
            risk_scores.append(5)

        # Interest coverage risk
        if metrics.interest_coverage_ratio < 2.0:
            risk_factors.append("weak_interest_coverage")
            risk_scores.append(8)
        elif metrics.interest_coverage_ratio < 3.0:
            risk_factors.append("moderate_interest_coverage")
            risk_scores.append(5)

        # Default probability risk
        if metrics.default_probability > 0.15:
            risk_factors.append("high_default_probability")
            risk_scores.append(9)
        elif metrics.default_probability > 0.08:
            risk_factors.append("moderate_default_probability")
            risk_scores.append(6)

        # Calculate overall risk
        if not risk_scores:
            overall_risk = "low"
        else:
            avg_risk = np.mean(risk_scores)
            if avg_risk >= 7:
                overall_risk = "high"
            elif avg_risk >= 5:
                overall_risk = "medium"
            else:
                overall_risk = "low"

        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "risk_score": np.mean(risk_scores) if risk_scores else 2
        }

    def _compare_with_benchmarks(self, metrics: CreditRiskMetrics, sector: str,
                                comparison_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Compare with industry benchmarks"""
        # Industry-specific benchmarks
        benchmarks = {
            "manufacturing": {
                "debt_to_equity": {"max_safe": 1.0, "max_acceptable": 1.5},
                "interest_coverage": {"min_safe": 5.0, "min_acceptable": 2.5},
                "current_ratio": {"min_safe": 1.5, "min_acceptable": 1.2},
                "default_probability": {"max_safe": 0.03, "max_acceptable": 0.08}
            },
            "retail": {
                "debt_to_equity": {"max_safe": 0.8, "max_acceptable": 1.2},
                "interest_coverage": {"min_safe": 4.0, "min_acceptable": 2.0},
                "current_ratio": {"min_safe": 1.3, "min_acceptable": 1.0},
                "default_probability": {"max_safe": 0.05, "max_acceptable": 0.12}
            },
            "default": {
                "debt_to_equity": {"max_safe": 1.0, "max_acceptable": 1.5},
                "interest_coverage": {"min_safe": 4.0, "min_acceptable": 2.5},
                "current_ratio": {"min_safe": 1.5, "min_acceptable": 1.2},
                "default_probability": {"max_safe": 0.04, "max_acceptable": 0.10}
            }
        }

        sector_benchmarks = benchmarks.get(sector.lower(), benchmarks["default"])
        comparison = {}

        # Compare each metric
        for metric, benchmark in sector_benchmarks.items():
            if hasattr(metrics, metric):
                value = getattr(metrics, metric)

                if "max_" in list(benchmark.keys())[0]:  # Lower is better
                    if value <= benchmark["max_safe"]:
                        performance = "excellent"
                    elif value <= benchmark["max_acceptable"]:
                        performance = "acceptable"
                    else:
                        performance = "poor"
                else:  # Higher is better
                    if value >= benchmark["min_safe"]:
                        performance = "excellent"
                    elif value >= benchmark["min_acceptable"]:
                        performance = "acceptable"
                    else:
                        performance = "poor"

                comparison[metric] = {
                    "value": value,
                    "benchmark": benchmark,
                    "performance": performance
                }

        return comparison

    def _analyze_trends(self, fs: FinancialStatements) -> Dict[str, Any]:
        """Analyze credit risk trends"""
        if not fs.historical_data or len(fs.historical_data) < 2:
            return {"trend_available": False}

        trends = {}

        # Calculate historical metrics
        historical_metrics = []
        for historical_fs in fs.historical_data:
            metrics = self._calculate_credit_risk_metrics(historical_fs)
            historical_metrics.append(metrics)

        # Debt trend
        debt_ratios = [m.debt_to_equity_ratio for m in historical_metrics if m.debt_to_equity_ratio != float('inf')]
        if debt_ratios:
            trends["debt_trend"] = self._calculate_trend_reverse(debt_ratios)

        # Profitability trend
        roa_values = [m.return_on_assets for m in historical_metrics]
        trends["profitability_trend"] = self._calculate_trend(roa_values)

        # Credit rating trend
        credit_scores = [m.credit_rating_score for m in historical_metrics]
        trends["credit_rating_trend"] = self._calculate_trend(credit_scores)

        return {
            "trend_available": True,
            "trends": trends,
            "periods_analyzed": len(historical_metrics)
        }

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend (higher is better)"""
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
            "previous_value": values[-2]
        }

    def _calculate_trend_reverse(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend (lower is better)"""
        if len(values) < 2:
            return {"direction": "stable", "strength": 0}

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if abs(slope) < 0.01:
            direction = "stable"
            strength = 0
        elif slope < 0:  # Decreasing is good
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
            "previous_value": values[-2]
        }

    def _generate_recommendations(self, metrics: CreditRiskMetrics, risk_assessment: Dict) -> List[Dict[str, Any]]:
        """Generate credit risk recommendations"""
        recommendations = []

        # High leverage recommendations
        if metrics.debt_to_equity_ratio > 1.5:
            recommendations.append({
                "priority": "critical",
                "category": "debt_reduction",
                "title_ar": "تقليل مستويات الديون",
                "title_en": "Reduce Debt Levels",
                "description_ar": "تقليل نسبة الديون لتحسين الملف الائتماني",
                "description_en": "Reduce debt ratios to improve credit profile",
                "actions_ar": [
                    "سداد الديون عالية التكلفة",
                    "إعادة هيكلة الديون",
                    "زيادة رأس المال",
                    "بيع أصول غير أساسية"
                ],
                "actions_en": [
                    "Pay down high-cost debt",
                    "Restructure debt obligations",
                    "Raise equity capital",
                    "Sell non-core assets"
                ],
                "expected_impact": "high",
                "timeframe": "medium_term"
            })

        # Low interest coverage recommendations
        if metrics.interest_coverage_ratio < 3.0:
            recommendations.append({
                "priority": "high",
                "category": "earnings_improvement",
                "title_ar": "تحسين القدرة على تغطية الفوائد",
                "title_en": "Improve Interest Coverage Ability",
                "description_ar": "زيادة الأرباح التشغيلية أو تقليل تكاليف الفوائد",
                "description_en": "Increase operating earnings or reduce interest costs",
                "actions_ar": [
                    "تحسين الربحية التشغيلية",
                    "إعادة تمويل الديون بتكلفة أقل",
                    "تحسين كفاءة العمليات",
                    "زيادة الإيرادات"
                ],
                "actions_en": [
                    "Improve operating profitability",
                    "Refinance debt at lower cost",
                    "Improve operational efficiency",
                    "Increase revenues"
                ],
                "expected_impact": "high",
                "timeframe": "short_term"
            })

        # Liquidity improvement recommendations
        if metrics.current_ratio < 1.2:
            recommendations.append({
                "priority": "high",
                "category": "liquidity_improvement",
                "title_ar": "تحسين السيولة قصيرة الأجل",
                "title_en": "Improve Short-term Liquidity",
                "description_ar": "تحسين إدارة رأس المال العامل والسيولة",
                "description_en": "Improve working capital management and liquidity",
                "actions_ar": [
                    "زيادة الأصول المتداولة",
                    "تحسين إدارة المخزون",
                    "تسريع تحصيل الذمم",
                    "الحصول على خطوط ائتمان"
                ],
                "actions_en": [
                    "Increase current assets",
                    "Improve inventory management",
                    "Accelerate receivables collection",
                    "Establish credit facilities"
                ],
                "expected_impact": "medium",
                "timeframe": "short_term"
            })

        return recommendations

    def _prepare_charts_data(self, metrics: CreditRiskMetrics, fs: FinancialStatements) -> Dict[str, Any]:
        """Prepare charts data for visualization"""
        return {
            "credit_risk_dashboard": {
                "type": "gauge_chart",
                "title_ar": "لوحة مخاطر الائتمان",
                "title_en": "Credit Risk Dashboard",
                "data": {
                    "altman_z_score": {
                        "value": metrics.altman_z_score,
                        "max": 6.0,
                        "zones": [{"min": 0, "max": 1.8, "color": "red", "label": "High Risk"},
                                 {"min": 1.8, "max": 3.0, "color": "yellow", "label": "Gray Zone"},
                                 {"min": 3.0, "max": 6.0, "color": "green", "label": "Safe Zone"}]
                    },
                    "credit_rating_score": {
                        "value": metrics.credit_rating_score,
                        "max": 100,
                        "zones": [{"min": 0, "max": 50, "color": "red", "label": "Poor"},
                                 {"min": 50, "max": 70, "color": "yellow", "label": "Fair"},
                                 {"min": 70, "max": 100, "color": "green", "label": "Good"}]
                    },
                    "default_probability": {
                        "value": metrics.default_probability * 100,
                        "max": 25,
                        "format": "percentage"
                    }
                }
            },
            "credit_ratios": {
                "type": "bar_chart",
                "title_ar": "النسب الائتمانية الرئيسية",
                "title_en": "Key Credit Ratios",
                "data": {
                    "labels_ar": ["نسبة الدين للملكية", "تغطية الفوائد", "نسبة التداول", "نسبة السيولة السريعة"],
                    "labels_en": ["Debt-to-Equity", "Interest Coverage", "Current Ratio", "Quick Ratio"],
                    "values": [
                        min(metrics.debt_to_equity_ratio, 5),  # Cap for visualization
                        min(metrics.interest_coverage_ratio, 10),
                        metrics.current_ratio,
                        metrics.quick_ratio
                    ],
                    "benchmarks": [1.0, 3.0, 1.5, 1.0]
                }
            },
            "risk_components": {
                "type": "radar_chart",
                "title_ar": "مكونات المخاطر",
                "title_en": "Risk Components",
                "data": {
                    "labels_ar": ["الرافعة المالية", "الربحية", "السيولة", "التدفق النقدي", "جودة الأرباح"],
                    "labels_en": ["Leverage", "Profitability", "Liquidity", "Cash Flow", "Earnings Quality"],
                    "values": [
                        max(0, 100 - metrics.debt_to_equity_ratio * 30),
                        max(0, metrics.return_on_assets * 100 * 10),
                        min(100, metrics.current_ratio * 50),
                        max(0, metrics.free_cash_flow_margin * 100 * 5),
                        metrics.piotroski_f_score * 10
                    ]
                }
            }
        }