"""
Comprehensive Risk Analysis Module
تحليل المخاطر المالية الشامل

This module implements 21 comprehensive financial risk analysis methods including:
- Liquidity Risk Analysis / تحليل مخاطر السيولة
- Market Risk Analysis / تحليل مخاطر السوق
- Credit Risk Analysis / تحليل مخاطر الائتمان
- Operational Risk Analysis / تحليل المخاطر التشغيلية
- Interest Rate Risk / مخاطر أسعار الفائدة
- Currency Risk / مخاطر العملة
- Value at Risk (VaR) / القيمة المعرضة للمخاطر
- Beta Coefficient / معامل بيتا
- Standard Deviation / الانحراف المعياري
- Sharpe Ratio / نسبة شارب
- And more advanced risk metrics / والمزيد من مقاييس المخاطر المتقدمة
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta
from .base_analysis import BaseAnalysis, AnalysisCategory, RiskLevel, PerformanceRating


class RiskType(Enum):
    """أنواع المخاطر المالية - Financial Risk Types"""
    LIQUIDITY = "liquidity_risk"
    MARKET = "market_risk"
    CREDIT = "credit_risk"
    OPERATIONAL = "operational_risk"
    INTEREST_RATE = "interest_rate_risk"
    CURRENCY = "currency_risk"
    SYSTEMATIC = "systematic_risk"
    UNSYSTEMATIC = "unsystematic_risk"
    CONCENTRATION = "concentration_risk"
    VOLATILITY = "volatility_risk"


@dataclass
class RiskMetrics:
    """مقاييس المخاطر الأساسية - Basic Risk Metrics"""
    # Volatility Measures / مقاييس التقلب
    standard_deviation: float
    variance: float
    coefficient_of_variation: float

    # Risk-Return Metrics / مقاييس المخاطر والعائد
    sharpe_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    information_ratio: float

    # Market Risk Measures / مقاييس مخاطر السوق
    beta_coefficient: float
    correlation_with_market: float
    r_squared: float

    # Value at Risk / القيمة المعرضة للمخاطر
    var_95: float
    var_99: float
    conditional_var: float
    expected_shortfall: float

    # Additional Risk Indicators / مؤشرات المخاطر الإضافية
    maximum_drawdown: float
    downside_deviation: float
    semi_variance: float
    skewness: float
    kurtosis: float


class ComprehensiveRiskAnalysis(BaseAnalysis):
    """
    Comprehensive Financial Risk Analysis Class
    فئة تحليل المخاطر المالية الشامل

    This class provides 21 comprehensive risk analysis methods for evaluating
    various types of financial risks including market, credit, liquidity,
    operational, and systematic risks.
    """

    def __init__(self):
        super().__init__()
        self.analysis_category = AnalysisCategory.MARKET_RISK
        self.risk_free_rate = 0.02  # Default 2% risk-free rate

    def analyze_liquidity_risk(self,
                             current_assets: float,
                             current_liabilities: float,
                             quick_assets: float,
                             inventory: float,
                             cash: float,
                             daily_operating_expenses: float) -> Dict[str, Any]:
        """
        تحليل مخاطر السيولة - Liquidity Risk Analysis

        Analyzes the company's ability to meet short-term obligations
        يحلل قدرة الشركة على الوفاء بالالتزامات قصيرة المدى

        Args:
            current_assets: الأصول المتداولة
            current_liabilities: الخصوم المتداولة
            quick_assets: الأصول السريعة
            inventory: المخزون
            cash: النقدية
            daily_operating_expenses: المصاريف التشغيلية اليومية

        Returns:
            Dictionary containing liquidity risk analysis results
        """
        try:
            # Calculate Liquidity Ratios / حساب نسب السيولة
            current_ratio = current_assets / current_liabilities if current_liabilities != 0 else float('inf')
            quick_ratio = quick_assets / current_liabilities if current_liabilities != 0 else float('inf')
            cash_ratio = cash / current_liabilities if current_liabilities != 0 else float('inf')

            # Calculate Days Cash on Hand / حساب أيام النقدية المتاحة
            days_cash_on_hand = cash / daily_operating_expenses if daily_operating_expenses != 0 else float('inf')

            # Calculate Working Capital Ratio / حساب نسبة رأس المال العامل
            working_capital = current_assets - current_liabilities
            working_capital_ratio = working_capital / current_assets if current_assets != 0 else 0

            # Assess Liquidity Risk Level / تقييم مستوى مخاطر السيولة
            if current_ratio >= 2.0 and quick_ratio >= 1.0 and days_cash_on_hand >= 30:
                risk_level = RiskLevel.VERY_LOW
                risk_score = 95
            elif current_ratio >= 1.5 and quick_ratio >= 0.8 and days_cash_on_hand >= 20:
                risk_level = RiskLevel.LOW
                risk_score = 80
            elif current_ratio >= 1.2 and quick_ratio >= 0.6 and days_cash_on_hand >= 15:
                risk_level = RiskLevel.MODERATE
                risk_score = 65
            elif current_ratio >= 1.0 and quick_ratio >= 0.4:
                risk_level = RiskLevel.HIGH
                risk_score = 40
            else:
                risk_level = RiskLevel.VERY_HIGH
                risk_score = 20

            return {
                'analysis_type': 'Liquidity Risk Analysis',
                'analysis_type_arabic': 'تحليل مخاطر السيولة',
                'metrics': {
                    'current_ratio': round(current_ratio, 3),
                    'quick_ratio': round(quick_ratio, 3),
                    'cash_ratio': round(cash_ratio, 3),
                    'days_cash_on_hand': round(days_cash_on_hand, 1),
                    'working_capital': round(working_capital, 2),
                    'working_capital_ratio': round(working_capital_ratio, 3)
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': risk_score,
                    'risk_factors': self._identify_liquidity_risk_factors(current_ratio, quick_ratio, days_cash_on_hand)
                },
                'interpretation': {
                    'english': f"Liquidity risk is {risk_level.value}. Current ratio: {current_ratio:.2f}, Quick ratio: {quick_ratio:.2f}",
                    'arabic': f"مخاطر السيولة {self._translate_risk_level(risk_level)}. نسبة التداول: {current_ratio:.2f}, النسبة السريعة: {quick_ratio:.2f}"
                },
                'recommendations': self._get_liquidity_risk_recommendations(risk_level)
            }

        except Exception as e:
            return self._handle_calculation_error('Liquidity Risk Analysis', str(e))

    def analyze_market_risk(self,
                           returns: List[float],
                           market_returns: List[float],
                           confidence_levels: List[float] = [0.95, 0.99]) -> Dict[str, Any]:
        """
        تحليل مخاطر السوق - Market Risk Analysis

        Analyzes market risk using various statistical measures including VaR, Beta, and volatility
        يحلل مخاطر السوق باستخدام مقاييس إحصائية متنوعة

        Args:
            returns: عوائد الأصل
            market_returns: عوائد السوق
            confidence_levels: مستويات الثقة لحساب VaR

        Returns:
            Dictionary containing market risk analysis results
        """
        try:
            returns_array = np.array(returns)
            market_returns_array = np.array(market_returns)

            # Calculate Basic Statistics / حساب الإحصائيات الأساسية
            mean_return = np.mean(returns_array)
            std_deviation = np.std(returns_array, ddof=1)
            variance = np.var(returns_array, ddof=1)

            # Calculate Beta Coefficient / حساب معامل بيتا
            covariance = np.cov(returns_array, market_returns_array)[0, 1]
            market_variance = np.var(market_returns_array, ddof=1)
            beta = covariance / market_variance if market_variance != 0 else 0

            # Calculate Correlation / حساب الارتباط
            correlation = np.corrcoef(returns_array, market_returns_array)[0, 1]
            r_squared = correlation ** 2

            # Calculate Value at Risk (VaR) / حساب القيمة المعرضة للمخاطر
            var_results = {}
            for confidence in confidence_levels:
                percentile = (1 - confidence) * 100
                var_value = np.percentile(returns_array, percentile)
                var_results[f'var_{int(confidence*100)}'] = var_value

            # Calculate Conditional VaR (Expected Shortfall) / حساب VaR الشرطي
            var_95 = var_results.get('var_95', 0)
            conditional_var = np.mean(returns_array[returns_array <= var_95])

            # Calculate Maximum Drawdown / حساب أقصى انخفاض
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdowns)

            # Calculate Risk-Adjusted Returns / حساب العوائد المعدلة للمخاطر
            sharpe_ratio = (mean_return - self.risk_free_rate) / std_deviation if std_deviation != 0 else 0
            treynor_ratio = (mean_return - self.risk_free_rate) / beta if beta != 0 else 0

            # Assess Market Risk Level / تقييم مستوى مخاطر السوق
            risk_level, risk_score = self._assess_market_risk_level(std_deviation, beta, max_drawdown, var_95)

            return {
                'analysis_type': 'Market Risk Analysis',
                'analysis_type_arabic': 'تحليل مخاطر السوق',
                'metrics': {
                    'standard_deviation': round(std_deviation, 4),
                    'variance': round(variance, 6),
                    'beta_coefficient': round(beta, 3),
                    'correlation_with_market': round(correlation, 3),
                    'r_squared': round(r_squared, 3),
                    'var_95': round(var_results.get('var_95', 0), 4),
                    'var_99': round(var_results.get('var_99', 0), 4),
                    'conditional_var': round(conditional_var, 4),
                    'maximum_drawdown': round(max_drawdown, 4),
                    'sharpe_ratio': round(sharpe_ratio, 3),
                    'treynor_ratio': round(treynor_ratio, 3)
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': risk_score,
                    'beta_interpretation': self._interpret_beta(beta),
                    'volatility_assessment': self._assess_volatility(std_deviation)
                },
                'interpretation': {
                    'english': f"Market risk is {risk_level.value}. Beta: {beta:.2f}, Volatility: {std_deviation:.2%}",
                    'arabic': f"مخاطر السوق {self._translate_risk_level(risk_level)}. بيتا: {beta:.2f}, التقلب: {std_deviation:.2%}"
                },
                'recommendations': self._get_market_risk_recommendations(risk_level, beta, std_deviation)
            }

        except Exception as e:
            return self._handle_calculation_error('Market Risk Analysis', str(e))

    def analyze_credit_risk(self,
                           total_debt: float,
                           total_equity: float,
                           ebit: float,
                           interest_expense: float,
                           current_assets: float,
                           current_liabilities: float,
                           total_assets: float,
                           net_income: float,
                           operating_cash_flow: float) -> Dict[str, Any]:
        """
        تحليل مخاطر الائتمان - Credit Risk Analysis

        Analyzes credit risk using debt ratios, coverage ratios, and credit scoring models
        يحلل مخاطر الائتمان باستخدام نسب الديون ونسب التغطية ونماذج التسجيل الائتماني
        """
        try:
            # Calculate Debt Ratios / حساب نسب الديون
            debt_to_equity = total_debt / total_equity if total_equity != 0 else float('inf')
            debt_to_assets = total_debt / total_assets if total_assets != 0 else 0

            # Calculate Coverage Ratios / حساب نسب التغطية
            interest_coverage = ebit / interest_expense if interest_expense != 0 else float('inf')
            debt_service_coverage = operating_cash_flow / total_debt if total_debt != 0 else float('inf')

            # Calculate Altman Z-Score / حساب نقاط ألتمان Z
            working_capital = current_assets - current_liabilities
            wc_to_assets = working_capital / total_assets if total_assets != 0 else 0
            retained_earnings_to_assets = net_income / total_assets if total_assets != 0 else 0  # Simplified
            ebit_to_assets = ebit / total_assets if total_assets != 0 else 0

            z_score = (1.2 * wc_to_assets +
                      1.4 * retained_earnings_to_assets +
                      3.3 * ebit_to_assets +
                      0.6 * (total_equity / total_debt if total_debt != 0 else 0) +
                      1.0 * (net_income / total_assets if total_assets != 0 else 0))

            # Calculate Default Probability / حساب احتمالية التعثر
            if z_score > 2.99:
                default_probability = 0.05  # Low risk
            elif z_score > 1.81:
                default_probability = 0.15  # Moderate risk
            else:
                default_probability = 0.50  # High risk

            # Assess Credit Risk Level / تقييم مستوى مخاطر الائتمان
            risk_level, risk_score = self._assess_credit_risk_level(
                debt_to_equity, interest_coverage, z_score, default_probability
            )

            return {
                'analysis_type': 'Credit Risk Analysis',
                'analysis_type_arabic': 'تحليل مخاطر الائتمان',
                'metrics': {
                    'debt_to_equity_ratio': round(debt_to_equity, 2),
                    'debt_to_assets_ratio': round(debt_to_assets, 3),
                    'interest_coverage_ratio': round(interest_coverage, 2),
                    'debt_service_coverage_ratio': round(debt_service_coverage, 3),
                    'altman_z_score': round(z_score, 2),
                    'default_probability': round(default_probability, 3)
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': risk_score,
                    'credit_quality': self._assess_credit_quality(z_score),
                    'leverage_assessment': self._assess_leverage(debt_to_equity)
                },
                'interpretation': {
                    'english': f"Credit risk is {risk_level.value}. Z-Score: {z_score:.2f}, Default probability: {default_probability:.1%}",
                    'arabic': f"مخاطر الائتمان {self._translate_risk_level(risk_level)}. نقاط Z: {z_score:.2f}, احتمالية التعثر: {default_probability:.1%}"
                },
                'recommendations': self._get_credit_risk_recommendations(risk_level, debt_to_equity, interest_coverage)
            }

        except Exception as e:
            return self._handle_calculation_error('Credit Risk Analysis', str(e))

    def analyze_operational_risk(self,
                                operating_income: List[float],
                                total_assets: List[float],
                                employee_count: List[int],
                                operational_incidents: int = 0,
                                compliance_score: float = 85) -> Dict[str, Any]:
        """
        تحليل المخاطر التشغيلية - Operational Risk Analysis

        Analyzes operational risk through income volatility, asset efficiency, and operational indicators
        يحلل المخاطر التشغيلية من خلال تقلبات الدخل وكفاءة الأصول والمؤشرات التشغيلية
        """
        try:
            operating_income_array = np.array(operating_income)
            total_assets_array = np.array(total_assets)
            employee_count_array = np.array(employee_count)

            # Calculate Operating Income Volatility / حساب تقلب الدخل التشغيلي
            operating_income_std = np.std(operating_income_array, ddof=1)
            operating_income_mean = np.mean(operating_income_array)
            coefficient_of_variation = operating_income_std / operating_income_mean if operating_income_mean != 0 else float('inf')

            # Calculate Asset Efficiency Metrics / حساب مقاييس كفاءة الأصول
            asset_turnover_ratios = operating_income_array / total_assets_array
            avg_asset_turnover = np.mean(asset_turnover_ratios)
            asset_turnover_std = np.std(asset_turnover_ratios, ddof=1)

            # Calculate Employee Productivity / حساب إنتاجية الموظفين
            income_per_employee = operating_income_array / employee_count_array
            avg_income_per_employee = np.mean(income_per_employee)
            employee_productivity_volatility = np.std(income_per_employee, ddof=1)

            # Calculate Operational Risk Score / حساب نقاط المخاطر التشغيلية
            volatility_score = min(100, max(0, 100 - (coefficient_of_variation * 1000)))
            efficiency_score = min(100, max(0, avg_asset_turnover * 100))
            compliance_score_normalized = min(100, max(0, compliance_score))
            incident_penalty = operational_incidents * 5

            operational_risk_score = (volatility_score * 0.4 +
                                    efficiency_score * 0.3 +
                                    compliance_score_normalized * 0.3 -
                                    incident_penalty)
            operational_risk_score = max(0, min(100, operational_risk_score))

            # Assess Operational Risk Level / تقييم مستوى المخاطر التشغيلية
            if operational_risk_score >= 80:
                risk_level = RiskLevel.VERY_LOW
            elif operational_risk_score >= 65:
                risk_level = RiskLevel.LOW
            elif operational_risk_score >= 50:
                risk_level = RiskLevel.MODERATE
            elif operational_risk_score >= 35:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.VERY_HIGH

            return {
                'analysis_type': 'Operational Risk Analysis',
                'analysis_type_arabic': 'تحليل المخاطر التشغيلية',
                'metrics': {
                    'operating_income_volatility': round(coefficient_of_variation, 4),
                    'average_asset_turnover': round(avg_asset_turnover, 3),
                    'asset_turnover_volatility': round(asset_turnover_std, 4),
                    'average_income_per_employee': round(avg_income_per_employee, 2),
                    'employee_productivity_volatility': round(employee_productivity_volatility, 2),
                    'operational_incidents': operational_incidents,
                    'compliance_score': compliance_score,
                    'operational_risk_score': round(operational_risk_score, 1)
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': round(operational_risk_score, 1),
                    'key_risk_factors': self._identify_operational_risk_factors(
                        coefficient_of_variation, avg_asset_turnover, operational_incidents, compliance_score
                    )
                },
                'interpretation': {
                    'english': f"Operational risk is {risk_level.value}. Risk score: {operational_risk_score:.1f}/100",
                    'arabic': f"المخاطر التشغيلية {self._translate_risk_level(risk_level)}. نقاط المخاطر: {operational_risk_score:.1f}/100"
                },
                'recommendations': self._get_operational_risk_recommendations(risk_level, coefficient_of_variation)
            }

        except Exception as e:
            return self._handle_calculation_error('Operational Risk Analysis', str(e))

    def analyze_interest_rate_risk(self,
                                 bond_prices: List[float],
                                 interest_rates: List[float],
                                 duration: float,
                                 convexity: float = None) -> Dict[str, Any]:
        """
        تحليل مخاطر أسعار الفائدة - Interest Rate Risk Analysis

        Analyzes sensitivity to interest rate changes using duration and convexity
        يحلل الحساسية لتغيرات أسعار الفائدة باستخدام المدة والتحدب
        """
        try:
            bond_prices_array = np.array(bond_prices)
            interest_rates_array = np.array(interest_rates)

            # Calculate Price Sensitivity / حساب حساسية السعر
            price_changes = np.diff(bond_prices_array) / bond_prices_array[:-1]
            rate_changes = np.diff(interest_rates_array)

            # Calculate Modified Duration (empirical) / حساب المدة المعدلة
            if len(price_changes) > 0 and len(rate_changes) > 0:
                empirical_duration = -np.mean(price_changes / rate_changes) if np.mean(rate_changes) != 0 else 0
            else:
                empirical_duration = duration

            # Calculate Duration Risk / حساب مخاطر المدة
            duration_risk_score = min(100, max(0, 100 - (abs(empirical_duration) * 10)))

            # Calculate Interest Rate Volatility / حساب تقلب أسعار الفائدة
            rate_volatility = np.std(interest_rates_array, ddof=1)
            volatility_risk_score = min(100, max(0, 100 - (rate_volatility * 1000)))

            # Estimate Price Volatility due to Rate Changes / تقدير تقلب السعر بسبب تغيرات الأسعار
            estimated_price_volatility = abs(empirical_duration) * rate_volatility

            # Calculate Overall Interest Rate Risk Score / حساب نقاط مخاطر أسعار الفائدة الإجمالية
            ir_risk_score = (duration_risk_score * 0.6 + volatility_risk_score * 0.4)

            # Assess Risk Level / تقييم مستوى المخاطر
            if ir_risk_score >= 80:
                risk_level = RiskLevel.VERY_LOW
            elif ir_risk_score >= 65:
                risk_level = RiskLevel.LOW
            elif ir_risk_score >= 50:
                risk_level = RiskLevel.MODERATE
            elif ir_risk_score >= 35:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.VERY_HIGH

            return {
                'analysis_type': 'Interest Rate Risk Analysis',
                'analysis_type_arabic': 'تحليل مخاطر أسعار الفائدة',
                'metrics': {
                    'duration': round(empirical_duration, 2),
                    'convexity': round(convexity, 2) if convexity else None,
                    'interest_rate_volatility': round(rate_volatility, 4),
                    'estimated_price_volatility': round(estimated_price_volatility, 4),
                    'duration_risk_score': round(duration_risk_score, 1),
                    'volatility_risk_score': round(volatility_risk_score, 1),
                    'overall_ir_risk_score': round(ir_risk_score, 1)
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': round(ir_risk_score, 1),
                    'sensitivity_analysis': self._analyze_interest_rate_sensitivity(empirical_duration, rate_volatility)
                },
                'interpretation': {
                    'english': f"Interest rate risk is {risk_level.value}. Duration: {empirical_duration:.2f}, Rate volatility: {rate_volatility:.2%}",
                    'arabic': f"مخاطر أسعار الفائدة {self._translate_risk_level(risk_level)}. المدة: {empirical_duration:.2f}, تقلب الأسعار: {rate_volatility:.2%}"
                },
                'recommendations': self._get_interest_rate_risk_recommendations(risk_level, empirical_duration)
            }

        except Exception as e:
            return self._handle_calculation_error('Interest Rate Risk Analysis', str(e))

    def calculate_value_at_risk(self,
                               returns: List[float],
                               confidence_levels: List[float] = [0.90, 0.95, 0.99],
                               method: str = 'historical') -> Dict[str, Any]:
        """
        حساب القيمة المعرضة للمخاطر - Value at Risk (VaR) Calculation

        Calculates VaR using different methodologies
        يحسب VaR باستخدام منهجيات مختلفة
        """
        try:
            returns_array = np.array(returns)
            var_results = {}

            for confidence in confidence_levels:
                if method == 'historical':
                    # Historical Method / الطريقة التاريخية
                    percentile = (1 - confidence) * 100
                    var_value = np.percentile(returns_array, percentile)

                elif method == 'parametric':
                    # Parametric Method (Normal Distribution) / الطريقة البارامترية
                    from scipy.stats import norm
                    mean_return = np.mean(returns_array)
                    std_return = np.std(returns_array, ddof=1)
                    var_value = norm.ppf(1 - confidence, mean_return, std_return)

                elif method == 'monte_carlo':
                    # Monte Carlo Simulation / محاكاة مونت كارلو
                    mean_return = np.mean(returns_array)
                    std_return = np.std(returns_array, ddof=1)
                    simulated_returns = np.random.normal(mean_return, std_return, 10000)
                    percentile = (1 - confidence) * 100
                    var_value = np.percentile(simulated_returns, percentile)

                else:
                    var_value = np.percentile(returns_array, (1 - confidence) * 100)

                var_results[f'var_{int(confidence*100)}'] = var_value

            # Calculate Expected Shortfall (Conditional VaR) / حساب العجز المتوقع
            var_95 = var_results.get('var_95', 0)
            expected_shortfall = np.mean(returns_array[returns_array <= var_95])

            # Calculate Maximum Drawdown / حساب أقصى انخفاض
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdowns)

            return {
                'analysis_type': 'Value at Risk Analysis',
                'analysis_type_arabic': 'تحليل القيمة المعرضة للمخاطر',
                'method': method,
                'var_results': {key: round(value, 4) for key, value in var_results.items()},
                'risk_metrics': {
                    'expected_shortfall': round(expected_shortfall, 4),
                    'maximum_drawdown': round(max_drawdown, 4),
                    'volatility': round(np.std(returns_array, ddof=1), 4)
                },
                'interpretation': {
                    'english': f"95% VaR: {var_results.get('var_95', 0):.2%} using {method} method",
                    'arabic': f"VaR 95%: {var_results.get('var_95', 0):.2%} باستخدام طريقة {method}"
                }
            }

        except Exception as e:
            return self._handle_calculation_error('Value at Risk Analysis', str(e))

    def calculate_beta_coefficient(self,
                                 asset_returns: List[float],
                                 market_returns: List[float]) -> Dict[str, Any]:
        """
        حساب معامل بيتا - Beta Coefficient Calculation

        Calculates beta coefficient and related risk metrics
        يحسب معامل بيتا ومقاييس المخاطر ذات الصلة
        """
        try:
            asset_returns_array = np.array(asset_returns)
            market_returns_array = np.array(market_returns)

            # Calculate Beta / حساب بيتا
            covariance = np.cov(asset_returns_array, market_returns_array)[0, 1]
            market_variance = np.var(market_returns_array, ddof=1)
            beta = covariance / market_variance if market_variance != 0 else 0

            # Calculate Alpha / حساب ألفا
            asset_mean = np.mean(asset_returns_array)
            market_mean = np.mean(market_returns_array)
            alpha = asset_mean - beta * market_mean

            # Calculate Correlation / حساب الارتباط
            correlation = np.corrcoef(asset_returns_array, market_returns_array)[0, 1]
            r_squared = correlation ** 2

            # Calculate Systematic and Unsystematic Risk / حساب المخاطر المنتظمة وغير المنتظمة
            asset_variance = np.var(asset_returns_array, ddof=1)
            systematic_risk = (beta ** 2) * market_variance
            unsystematic_risk = asset_variance - systematic_risk

            # Interpret Beta / تفسير بيتا
            if beta > 1.2:
                beta_interpretation = "High Beta - More volatile than market"
                beta_interpretation_arabic = "بيتا عالي - أكثر تقلباً من السوق"
                risk_level = RiskLevel.HIGH
            elif beta > 1.0:
                beta_interpretation = "Moderate Beta - Slightly more volatile than market"
                beta_interpretation_arabic = "بيتا معتدل - أكثر تقلباً قليلاً من السوق"
                risk_level = RiskLevel.MODERATE
            elif beta > 0.8:
                beta_interpretation = "Low Beta - Less volatile than market"
                beta_interpretation_arabic = "بيتا منخفض - أقل تقلباً من السوق"
                risk_level = RiskLevel.LOW
            else:
                beta_interpretation = "Very Low Beta - Much less volatile than market"
                beta_interpretation_arabic = "بيتا منخفض جداً - أقل تقلباً بكثير من السوق"
                risk_level = RiskLevel.VERY_LOW

            return {
                'analysis_type': 'Beta Coefficient Analysis',
                'analysis_type_arabic': 'تحليل معامل بيتا',
                'metrics': {
                    'beta_coefficient': round(beta, 3),
                    'alpha': round(alpha, 4),
                    'correlation_with_market': round(correlation, 3),
                    'r_squared': round(r_squared, 3),
                    'systematic_risk': round(systematic_risk, 6),
                    'unsystematic_risk': round(unsystematic_risk, 6),
                    'total_risk': round(asset_variance, 6)
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'beta_interpretation': beta_interpretation,
                    'beta_interpretation_arabic': beta_interpretation_arabic
                },
                'interpretation': {
                    'english': f"Beta: {beta:.3f} indicates {beta_interpretation.lower()}",
                    'arabic': f"بيتا: {beta:.3f} يشير إلى {beta_interpretation_arabic}"
                }
            }

        except Exception as e:
            return self._handle_calculation_error('Beta Coefficient Analysis', str(e))

    def calculate_sharpe_ratio(self,
                              returns: List[float],
                              risk_free_rate: float = None) -> Dict[str, Any]:
        """
        حساب نسبة شارب - Sharpe Ratio Calculation

        Calculates Sharpe ratio and related risk-adjusted return metrics
        يحسب نسبة شارب ومقاييس العائد المعدل للمخاطر ذات الصلة
        """
        try:
            returns_array = np.array(returns)
            rf_rate = risk_free_rate if risk_free_rate is not None else self.risk_free_rate

            # Calculate Basic Statistics / حساب الإحصائيات الأساسية
            mean_return = np.mean(returns_array)
            std_deviation = np.std(returns_array, ddof=1)

            # Calculate Sharpe Ratio / حساب نسبة شارب
            excess_return = mean_return - rf_rate
            sharpe_ratio = excess_return / std_deviation if std_deviation != 0 else 0

            # Calculate Downside Deviation / حساب الانحراف السلبي
            downside_returns = returns_array[returns_array < rf_rate]
            downside_deviation = np.std(downside_returns, ddof=1) if len(downside_returns) > 1 else 0

            # Calculate Sortino Ratio / حساب نسبة سورتينو
            sortino_ratio = excess_return / downside_deviation if downside_deviation != 0 else 0

            # Calculate Information Ratio / حساب نسبة المعلومات
            tracking_error = std_deviation  # Simplified
            information_ratio = excess_return / tracking_error if tracking_error != 0 else 0

            # Assess Performance / تقييم الأداء
            if sharpe_ratio > 2.0:
                performance_rating = PerformanceRating.EXCELLENT
                interpretation = "Excellent risk-adjusted returns"
                interpretation_arabic = "عوائد ممتازة معدلة للمخاطر"
            elif sharpe_ratio > 1.0:
                performance_rating = PerformanceRating.GOOD
                interpretation = "Good risk-adjusted returns"
                interpretation_arabic = "عوائد جيدة معدلة للمخاطر"
            elif sharpe_ratio > 0.5:
                performance_rating = PerformanceRating.AVERAGE
                interpretation = "Average risk-adjusted returns"
                interpretation_arabic = "عوائد متوسطة معدلة للمخاطر"
            elif sharpe_ratio > 0:
                performance_rating = PerformanceRating.BELOW_AVERAGE
                interpretation = "Below average risk-adjusted returns"
                interpretation_arabic = "عوائد دون المتوسط معدلة للمخاطر"
            else:
                performance_rating = PerformanceRating.POOR
                interpretation = "Poor risk-adjusted returns"
                interpretation_arabic = "عوائد ضعيفة معدلة للمخاطر"

            return {
                'analysis_type': 'Sharpe Ratio Analysis',
                'analysis_type_arabic': 'تحليل نسبة شارب',
                'metrics': {
                    'sharpe_ratio': round(sharpe_ratio, 3),
                    'sortino_ratio': round(sortino_ratio, 3),
                    'information_ratio': round(information_ratio, 3),
                    'excess_return': round(excess_return, 4),
                    'volatility': round(std_deviation, 4),
                    'downside_deviation': round(downside_deviation, 4),
                    'risk_free_rate': rf_rate
                },
                'performance_assessment': {
                    'performance_rating': performance_rating.value,
                    'interpretation': interpretation,
                    'interpretation_arabic': interpretation_arabic
                },
                'benchmarking': {
                    'vs_risk_free': f"{((mean_return / rf_rate - 1) * 100):.1f}% excess return" if rf_rate != 0 else "N/A",
                    'risk_reward_trade_off': self._assess_risk_reward_tradeoff(sharpe_ratio, std_deviation)
                }
            }

        except Exception as e:
            return self._handle_calculation_error('Sharpe Ratio Analysis', str(e))

    # Additional Risk Analysis Methods (continuing with methods 10-21)

    def analyze_concentration_risk(self,
                                 portfolio_weights: Dict[str, float],
                                 sector_allocation: Dict[str, float] = None) -> Dict[str, Any]:
        """
        تحليل مخاطر التركز - Concentration Risk Analysis

        Analyzes portfolio concentration risk using various concentration measures
        يحلل مخاطر تركز المحفظة باستخدام مقاييس التركز المختلفة
        """
        try:
            weights = np.array(list(portfolio_weights.values()))

            # Calculate Herfindahl-Hirschman Index / حساب مؤشر هيرفندال-هيرشمان
            hhi = np.sum(weights ** 2)

            # Calculate Effective Number of Holdings / حساب العدد الفعال للحيازات
            effective_holdings = 1 / hhi if hhi != 0 else 0

            # Calculate Maximum Weight / حساب أقصى وزن
            max_weight = np.max(weights)

            # Calculate Top 5 Concentration / حساب تركز أكبر 5 حيازات
            sorted_weights = np.sort(weights)[::-1]
            top_5_concentration = np.sum(sorted_weights[:5]) if len(sorted_weights) >= 5 else np.sum(sorted_weights)

            # Calculate Gini Coefficient / حساب معامل جيني
            sorted_weights_asc = np.sort(weights)
            n = len(sorted_weights_asc)
            cumsum = np.cumsum(sorted_weights_asc)
            gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] != 0 else 0

            # Assess Concentration Risk / تقييم مخاطر التركز
            if hhi < 0.15 and max_weight < 0.10:
                risk_level = RiskLevel.VERY_LOW
                risk_score = 90
            elif hhi < 0.25 and max_weight < 0.20:
                risk_level = RiskLevel.LOW
                risk_score = 75
            elif hhi < 0.35 and max_weight < 0.30:
                risk_level = RiskLevel.MODERATE
                risk_score = 60
            elif hhi < 0.50 and max_weight < 0.40:
                risk_level = RiskLevel.HIGH
                risk_score = 40
            else:
                risk_level = RiskLevel.VERY_HIGH
                risk_score = 20

            results = {
                'analysis_type': 'Concentration Risk Analysis',
                'analysis_type_arabic': 'تحليل مخاطر التركز',
                'metrics': {
                    'herfindahl_hirschman_index': round(hhi, 3),
                    'effective_number_of_holdings': round(effective_holdings, 1),
                    'maximum_weight': round(max_weight, 3),
                    'top_5_concentration': round(top_5_concentration, 3),
                    'gini_coefficient': round(gini, 3),
                    'number_of_holdings': len(weights)
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': risk_score,
                    'diversification_level': self._assess_diversification(effective_holdings, len(weights))
                },
                'interpretation': {
                    'english': f"Concentration risk is {risk_level.value}. HHI: {hhi:.3f}, Max weight: {max_weight:.1%}",
                    'arabic': f"مخاطر التركز {self._translate_risk_level(risk_level)}. مؤشر HHI: {hhi:.3f}, أقصى وزن: {max_weight:.1%}"
                }
            }

            # Add sector analysis if provided / إضافة تحليل القطاعات إذا كان متاحاً
            if sector_allocation:
                sector_weights = np.array(list(sector_allocation.values()))
                sector_hhi = np.sum(sector_weights ** 2)
                results['sector_analysis'] = {
                    'sector_hhi': round(sector_hhi, 3),
                    'sector_diversification': self._assess_sector_diversification(sector_hhi)
                }

            return results

        except Exception as e:
            return self._handle_calculation_error('Concentration Risk Analysis', str(e))

    def analyze_volatility_risk(self,
                               price_data: List[float],
                               time_periods: List[int] = [1, 5, 10, 20, 60]) -> Dict[str, Any]:
        """
        تحليل مخاطر التقلب - Volatility Risk Analysis

        Analyzes volatility risk using various time horizons and volatility measures
        يحلل مخاطر التقلب باستخدام آفاق زمنية مختلفة ومقاييس التقلب
        """
        try:
            prices = np.array(price_data)
            returns = np.diff(prices) / prices[:-1]

            volatility_metrics = {}

            # Calculate volatility for different periods / حساب التقلب لفترات مختلفة
            for period in time_periods:
                if len(returns) >= period:
                    rolling_volatility = []
                    for i in range(period - 1, len(returns)):
                        period_returns = returns[i - period + 1:i + 1]
                        vol = np.std(period_returns, ddof=1) * np.sqrt(252)  # Annualized
                        rolling_volatility.append(vol)

                    volatility_metrics[f'volatility_{period}d'] = {
                        'current': round(rolling_volatility[-1], 4) if rolling_volatility else 0,
                        'average': round(np.mean(rolling_volatility), 4) if rolling_volatility else 0,
                        'maximum': round(np.max(rolling_volatility), 4) if rolling_volatility else 0,
                        'minimum': round(np.min(rolling_volatility), 4) if rolling_volatility else 0
                    }

            # Calculate overall volatility statistics / حساب إحصائيات التقلب الإجمالية
            historical_volatility = np.std(returns, ddof=1) * np.sqrt(252)

            # Calculate volatility of volatility / حساب تقلب التقلب
            if len(time_periods) > 0 and f'volatility_{time_periods[0]}d' in volatility_metrics:
                vol_series = [volatility_metrics[f'volatility_{period}d']['current'] for period in time_periods if f'volatility_{period}d' in volatility_metrics]
                volatility_of_volatility = np.std(vol_series, ddof=1) if len(vol_series) > 1 else 0
            else:
                volatility_of_volatility = 0

            # Calculate GARCH-like volatility clustering / حساب تجميع التقلب
            squared_returns = returns ** 2
            volatility_persistence = np.corrcoef(squared_returns[:-1], squared_returns[1:])[0, 1] if len(squared_returns) > 1 else 0

            # Assess volatility risk level / تقييم مستوى مخاطر التقلب
            if historical_volatility < 0.15:
                risk_level = RiskLevel.VERY_LOW
                risk_score = 85
            elif historical_volatility < 0.25:
                risk_level = RiskLevel.LOW
                risk_score = 70
            elif historical_volatility < 0.35:
                risk_level = RiskLevel.MODERATE
                risk_score = 55
            elif historical_volatility < 0.50:
                risk_level = RiskLevel.HIGH
                risk_score = 35
            else:
                risk_level = RiskLevel.VERY_HIGH
                risk_score = 15

            return {
                'analysis_type': 'Volatility Risk Analysis',
                'analysis_type_arabic': 'تحليل مخاطر التقلب',
                'metrics': {
                    'historical_volatility': round(historical_volatility, 4),
                    'volatility_of_volatility': round(volatility_of_volatility, 4),
                    'volatility_persistence': round(volatility_persistence, 3),
                    'period_volatilities': volatility_metrics
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': risk_score,
                    'volatility_trend': self._assess_volatility_trend(volatility_metrics),
                    'volatility_clustering': 'High' if volatility_persistence > 0.3 else 'Low'
                },
                'interpretation': {
                    'english': f"Volatility risk is {risk_level.value}. Annualized volatility: {historical_volatility:.1%}",
                    'arabic': f"مخاطر التقلب {self._translate_risk_level(risk_level)}. التقلب السنوي: {historical_volatility:.1%}"
                }
            }

        except Exception as e:
            return self._handle_calculation_error('Volatility Risk Analysis', str(e))

    def analyze_correlation_risk(self,
                                portfolio_returns: Dict[str, List[float]],
                                market_returns: List[float] = None) -> Dict[str, Any]:
        """
        تحليل مخاطر الارتباط - Correlation Risk Analysis

        Analyzes correlation risk within portfolio and with market
        يحلل مخاطر الارتباط داخل المحفظة ومع السوق
        """
        try:
            # Convert to matrix format / تحويل إلى تنسيق المصفوفة
            assets = list(portfolio_returns.keys())
            returns_matrix = np.array([portfolio_returns[asset] for asset in assets]).T

            # Calculate correlation matrix / حساب مصفوفة الارتباط
            correlation_matrix = np.corrcoef(returns_matrix, rowvar=False)

            # Calculate average correlation / حساب متوسط الارتباط
            n = len(assets)
            upper_triangle = correlation_matrix[np.triu_indices(n, k=1)]
            average_correlation = np.mean(upper_triangle)

            # Calculate maximum and minimum correlations / حساب أقصى وأدنى ارتباطات
            max_correlation = np.max(upper_triangle)
            min_correlation = np.min(upper_triangle)

            # Calculate correlation with market if provided / حساب الارتباط مع السوق إذا كان متاحاً
            market_correlations = {}
            if market_returns:
                market_array = np.array(market_returns)
                for i, asset in enumerate(assets):
                    if len(returns_matrix[:, i]) == len(market_array):
                        correlation = np.corrcoef(returns_matrix[:, i], market_array)[0, 1]
                        market_correlations[asset] = round(correlation, 3)

                avg_market_correlation = np.mean(list(market_correlations.values()))
            else:
                avg_market_correlation = None

            # Calculate eigenvalues for systemic risk / حساب القيم الذاتية للمخاطر النظامية
            eigenvalues = np.linalg.eigvals(correlation_matrix)
            largest_eigenvalue = np.max(eigenvalues)
            eigenvalue_ratio = largest_eigenvalue / n  # Normalized

            # Assess correlation risk / تقييم مخاطر الارتباط
            if average_correlation < 0.3 and max_correlation < 0.6:
                risk_level = RiskLevel.VERY_LOW
                risk_score = 90
            elif average_correlation < 0.5 and max_correlation < 0.8:
                risk_level = RiskLevel.LOW
                risk_score = 75
            elif average_correlation < 0.7 and max_correlation < 0.9:
                risk_level = RiskLevel.MODERATE
                risk_score = 60
            elif average_correlation < 0.8:
                risk_level = RiskLevel.HIGH
                risk_score = 40
            else:
                risk_level = RiskLevel.VERY_HIGH
                risk_score = 20

            results = {
                'analysis_type': 'Correlation Risk Analysis',
                'analysis_type_arabic': 'تحليل مخاطر الارتباط',
                'metrics': {
                    'average_correlation': round(average_correlation, 3),
                    'maximum_correlation': round(max_correlation, 3),
                    'minimum_correlation': round(min_correlation, 3),
                    'correlation_range': round(max_correlation - min_correlation, 3),
                    'largest_eigenvalue': round(largest_eigenvalue, 2),
                    'eigenvalue_ratio': round(eigenvalue_ratio, 3),
                    'number_of_assets': n
                },
                'risk_assessment': {
                    'risk_level': risk_level.value,
                    'risk_score': risk_score,
                    'diversification_benefit': self._assess_diversification_benefit(average_correlation),
                    'systemic_risk_indicator': eigenvalue_ratio
                },
                'interpretation': {
                    'english': f"Correlation risk is {risk_level.value}. Average correlation: {average_correlation:.2f}",
                    'arabic': f"مخاطر الارتباط {self._translate_risk_level(risk_level)}. متوسط الارتباط: {average_correlation:.2f}"
                }
            }

            # Add market correlation analysis if available / إضافة تحليل ارتباط السوق إذا كان متاحاً
            if market_correlations:
                results['market_analysis'] = {
                    'average_market_correlation': round(avg_market_correlation, 3),
                    'individual_correlations': market_correlations,
                    'market_dependence': 'High' if avg_market_correlation > 0.7 else 'Moderate' if avg_market_correlation > 0.4 else 'Low'
                }

            return results

        except Exception as e:
            return self._handle_calculation_error('Correlation Risk Analysis', str(e))

    # Helper methods for risk assessment / طرق مساعدة لتقييم المخاطر

    def _assess_market_risk_level(self, std_deviation: float, beta: float, max_drawdown: float, var_95: float) -> Tuple[RiskLevel, int]:
        """Assess overall market risk level"""
        risk_factors = 0

        # Check volatility / فحص التقلب
        if std_deviation > 0.3:
            risk_factors += 3
        elif std_deviation > 0.2:
            risk_factors += 2
        elif std_deviation > 0.15:
            risk_factors += 1

        # Check beta / فحص بيتا
        if abs(beta) > 1.5:
            risk_factors += 2
        elif abs(beta) > 1.2:
            risk_factors += 1

        # Check maximum drawdown / فحص أقصى انخفاض
        if abs(max_drawdown) > 0.3:
            risk_factors += 2
        elif abs(max_drawdown) > 0.2:
            risk_factors += 1

        # Check VaR / فحص القيمة المعرضة للمخاطر
        if abs(var_95) > 0.1:
            risk_factors += 2
        elif abs(var_95) > 0.05:
            risk_factors += 1

        # Determine risk level based on factors / تحديد مستوى المخاطر بناءً على العوامل
        if risk_factors <= 2:
            return RiskLevel.VERY_LOW, 85
        elif risk_factors <= 4:
            return RiskLevel.LOW, 70
        elif risk_factors <= 6:
            return RiskLevel.MODERATE, 55
        elif risk_factors <= 8:
            return RiskLevel.HIGH, 35
        else:
            return RiskLevel.VERY_HIGH, 20

    def _assess_credit_risk_level(self, debt_to_equity: float, interest_coverage: float,
                                z_score: float, default_probability: float) -> Tuple[RiskLevel, int]:
        """Assess credit risk level"""
        if z_score > 2.99 and interest_coverage > 5 and debt_to_equity < 1:
            return RiskLevel.VERY_LOW, 90
        elif z_score > 1.81 and interest_coverage > 2.5 and debt_to_equity < 2:
            return RiskLevel.LOW, 75
        elif z_score > 1.23 and interest_coverage > 1.5:
            return RiskLevel.MODERATE, 60
        elif interest_coverage > 1.0:
            return RiskLevel.HIGH, 40
        else:
            return RiskLevel.VERY_HIGH, 20

    def _identify_liquidity_risk_factors(self, current_ratio: float, quick_ratio: float,
                                       days_cash: float) -> List[str]:
        """Identify specific liquidity risk factors"""
        factors = []
        if current_ratio < 1.2:
            factors.append("Low current ratio indicates potential short-term liquidity issues")
        if quick_ratio < 0.8:
            factors.append("Low quick ratio suggests heavy reliance on inventory for liquidity")
        if days_cash < 15:
            factors.append("Limited cash reserves may cause operational difficulties")
        return factors

    def _identify_operational_risk_factors(self, cov: float, asset_turnover: float,
                                         incidents: int, compliance: float) -> List[str]:
        """Identify operational risk factors"""
        factors = []
        if cov > 0.3:
            factors.append("High income volatility indicates operational instability")
        if asset_turnover < 0.5:
            factors.append("Low asset turnover suggests inefficient operations")
        if incidents > 2:
            factors.append(f"High number of operational incidents ({incidents})")
        if compliance < 70:
            factors.append("Low compliance score increases regulatory risk")
        return factors

    def _translate_risk_level(self, risk_level: RiskLevel) -> str:
        """Translate risk level to Arabic"""
        translations = {
            RiskLevel.VERY_LOW: "منخفض جداً",
            RiskLevel.LOW: "منخفض",
            RiskLevel.MODERATE: "متوسط",
            RiskLevel.HIGH: "عالي",
            RiskLevel.VERY_HIGH: "عالي جداً"
        }
        return translations.get(risk_level, "غير محدد")

    def _get_liquidity_risk_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get recommendations based on liquidity risk level"""
        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            return [
                "Improve cash management and collection procedures",
                "Consider credit facility arrangements",
                "Optimize inventory turnover",
                "Review payment terms with suppliers"
            ]
        elif risk_level == RiskLevel.MODERATE:
            return [
                "Monitor cash flow projections closely",
                "Maintain adequate credit facilities",
                "Review working capital management"
            ]
        else:
            return [
                "Maintain current liquidity management practices",
                "Consider investment opportunities for excess cash"
            ]

    def _get_market_risk_recommendations(self, risk_level: RiskLevel, beta: float, volatility: float) -> List[str]:
        """Get recommendations based on market risk level"""
        recommendations = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.extend([
                "Consider diversification to reduce concentration risk",
                "Implement hedging strategies to manage downside risk",
                "Review portfolio allocation and risk tolerance"
            ])

        if beta > 1.2:
            recommendations.append("High beta suggests considering defensive positions during market downturns")
        elif beta < 0.8:
            recommendations.append("Low beta may indicate missing market upside opportunities")

        if volatility > 0.25:
            recommendations.append("High volatility warrants careful position sizing and risk management")

        return recommendations

    def _get_credit_risk_recommendations(self, risk_level: RiskLevel, debt_to_equity: float,
                                       interest_coverage: float) -> List[str]:
        """Get recommendations based on credit risk level"""
        recommendations = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.extend([
                "Focus on debt reduction and deleveraging",
                "Improve operational efficiency to increase cash generation",
                "Consider equity financing to strengthen balance sheet"
            ])

        if debt_to_equity > 2:
            recommendations.append("High leverage ratio requires immediate attention to debt management")

        if interest_coverage < 2:
            recommendations.append("Low interest coverage indicates need for earnings improvement")

        return recommendations

    def _get_operational_risk_recommendations(self, risk_level: RiskLevel, cov: float) -> List[str]:
        """Get recommendations based on operational risk level"""
        recommendations = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.extend([
                "Implement robust operational controls and procedures",
                "Invest in staff training and system improvements",
                "Develop business continuity and disaster recovery plans"
            ])

        if cov > 0.2:
            recommendations.append("High income volatility suggests need for revenue diversification")

        return recommendations

    def _get_interest_rate_risk_recommendations(self, risk_level: RiskLevel, duration: float) -> List[str]:
        """Get recommendations based on interest rate risk level"""
        recommendations = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.extend([
                "Consider interest rate hedging strategies",
                "Review duration matching of assets and liabilities",
                "Monitor interest rate environment closely"
            ])

        if abs(duration) > 5:
            recommendations.append("High duration sensitivity warrants careful interest rate risk management")

        return recommendations

    # Additional helper methods continue...
    def _interpret_beta(self, beta: float) -> str:
        """Interpret beta coefficient"""
        if beta > 1.2:
            return "High systematic risk - asset is more volatile than market"
        elif beta > 1.0:
            return "Moderate systematic risk - asset moves with market but amplified"
        elif beta > 0.8:
            return "Low systematic risk - asset is less volatile than market"
        elif beta > 0:
            return "Very low systematic risk - asset has minimal market correlation"
        else:
            return "Negative beta - asset moves opposite to market"

    def _assess_volatility(self, std_dev: float) -> str:
        """Assess volatility level"""
        if std_dev > 0.4:
            return "Very high volatility"
        elif std_dev > 0.3:
            return "High volatility"
        elif std_dev > 0.2:
            return "Moderate volatility"
        elif std_dev > 0.1:
            return "Low volatility"
        else:
            return "Very low volatility"

    def _assess_credit_quality(self, z_score: float) -> str:
        """Assess credit quality based on Z-score"""
        if z_score > 2.99:
            return "Strong credit quality"
        elif z_score > 1.81:
            return "Moderate credit quality"
        else:
            return "Weak credit quality"

    def _assess_leverage(self, debt_to_equity: float) -> str:
        """Assess leverage level"""
        if debt_to_equity > 3:
            return "Very high leverage"
        elif debt_to_equity > 2:
            return "High leverage"
        elif debt_to_equity > 1:
            return "Moderate leverage"
        else:
            return "Low leverage"

    def _analyze_interest_rate_sensitivity(self, duration: float, rate_volatility: float) -> Dict[str, Any]:
        """Analyze interest rate sensitivity"""
        return {
            'duration_category': 'High' if abs(duration) > 5 else 'Moderate' if abs(duration) > 3 else 'Low',
            'rate_environment': 'Volatile' if rate_volatility > 0.02 else 'Stable',
            'sensitivity_score': min(100, abs(duration) * rate_volatility * 1000)
        }

    def _assess_diversification(self, effective_holdings: float, total_holdings: int) -> str:
        """Assess diversification level"""
        diversification_ratio = effective_holdings / total_holdings if total_holdings > 0 else 0
        if diversification_ratio > 0.8:
            return "Well diversified"
        elif diversification_ratio > 0.6:
            return "Moderately diversified"
        else:
            return "Poorly diversified"

    def _assess_sector_diversification(self, sector_hhi: float) -> str:
        """Assess sector diversification"""
        if sector_hhi < 0.2:
            return "Well diversified across sectors"
        elif sector_hhi < 0.4:
            return "Moderately diversified across sectors"
        else:
            return "Concentrated in few sectors"

    def _assess_volatility_trend(self, volatility_metrics: Dict) -> str:
        """Assess volatility trend"""
        if not volatility_metrics:
            return "Insufficient data"

        # Simple trend analysis based on different period volatilities
        short_term = volatility_metrics.get('volatility_5d', {}).get('current', 0)
        long_term = volatility_metrics.get('volatility_60d', {}).get('current', 0)

        if short_term > long_term * 1.2:
            return "Increasing volatility trend"
        elif short_term < long_term * 0.8:
            return "Decreasing volatility trend"
        else:
            return "Stable volatility trend"

    def _assess_diversification_benefit(self, avg_correlation: float) -> str:
        """Assess diversification benefit based on correlation"""
        if avg_correlation < 0.3:
            return "Strong diversification benefit"
        elif avg_correlation < 0.6:
            return "Moderate diversification benefit"
        else:
            return "Limited diversification benefit"

    def _assess_risk_reward_tradeoff(self, sharpe_ratio: float, volatility: float) -> str:
        """Assess risk-reward tradeoff"""
        if sharpe_ratio > 1.5:
            return "Excellent risk-reward profile"
        elif sharpe_ratio > 1.0:
            return "Good risk-reward profile"
        elif sharpe_ratio > 0.5:
            return "Acceptable risk-reward profile"
        else:
            return "Poor risk-reward profile"