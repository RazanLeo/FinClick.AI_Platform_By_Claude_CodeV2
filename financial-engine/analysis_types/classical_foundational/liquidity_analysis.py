"""
Liquidity Analysis Module
التحليلات الخاصة بالسيولة المالية

This module implements comprehensive liquidity analysis including:
- Current Ratio Analysis
- Quick Ratio Analysis
- Cash Ratio Analysis
- Operating Cash Flow Ratio
- Working Capital Analysis
- Cash Conversion Cycle
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from ..core.data_models import FinancialStatements, AnalysisResult


@dataclass
class LiquidityMetrics:
    """Liquidity analysis metrics"""
    current_ratio: float
    quick_ratio: float
    cash_ratio: float
    operating_cash_flow_ratio: float
    working_capital: float
    working_capital_ratio: float
    cash_conversion_cycle: float
    days_sales_outstanding: float
    days_inventory_outstanding: float
    days_payable_outstanding: float
    net_working_capital_turnover: float
    current_asset_turnover: float


class LiquidityAnalyzer:
    """Comprehensive liquidity analysis engine"""

    def __init__(self):
        self.analysis_type = "liquidity_analysis"
        self.category = "classical_foundational"

    def analyze(self, financial_statements: FinancialStatements,
                comparison_data: Optional[Dict] = None) -> AnalysisResult:
        """
        Perform comprehensive liquidity analysis
        تنفيذ تحليل شامل للسيولة المالية
        """
        try:
            # Calculate liquidity metrics
            metrics = self._calculate_liquidity_metrics(financial_statements)

            # Generate insights and recommendations
            insights = self._generate_insights(metrics, financial_statements)

            # Calculate industry benchmarks comparison
            benchmark_comparison = self._compare_with_benchmarks(
                metrics, financial_statements.sector, comparison_data
            )

            # Risk assessment
            risk_assessment = self._assess_liquidity_risks(metrics)

            # Trend analysis if historical data available
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
                timestamp=datetime.now()
            )

        except Exception as e:
            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                error=f"Liquidity analysis failed: {str(e)}",
                timestamp=datetime.now()
            )

    def _calculate_liquidity_metrics(self, fs: FinancialStatements) -> LiquidityMetrics:
        """Calculate all liquidity metrics"""
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        # Current Assets and Liabilities
        current_assets = balance_sheet.get('current_assets', 0)
        current_liabilities = balance_sheet.get('current_liabilities', 0)
        cash_and_equivalents = balance_sheet.get('cash_and_cash_equivalents', 0)
        short_term_investments = balance_sheet.get('short_term_investments', 0)
        accounts_receivable = balance_sheet.get('accounts_receivable', 0)
        inventory = balance_sheet.get('inventory', 0)
        accounts_payable = balance_sheet.get('accounts_payable', 0)

        # Income Statement items
        revenue = income_statement.get('revenue', 1)  # Avoid division by zero
        cost_of_goods_sold = income_statement.get('cost_of_goods_sold', 0)

        # Cash Flow items
        operating_cash_flow = cash_flow.get('operating_cash_flow', 0)

        # Calculate ratios
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0

        quick_assets = current_assets - inventory
        quick_ratio = quick_assets / current_liabilities if current_liabilities > 0 else 0

        liquid_assets = cash_and_equivalents + short_term_investments
        cash_ratio = liquid_assets / current_liabilities if current_liabilities > 0 else 0

        operating_cash_flow_ratio = operating_cash_flow / current_liabilities if current_liabilities > 0 else 0

        working_capital = current_assets - current_liabilities
        working_capital_ratio = working_capital / current_assets if current_assets > 0 else 0

        # Cash Conversion Cycle components
        days_sales_outstanding = (accounts_receivable / revenue) * 365 if revenue > 0 else 0
        days_inventory_outstanding = (inventory / cost_of_goods_sold) * 365 if cost_of_goods_sold > 0 else 0
        days_payable_outstanding = (accounts_payable / cost_of_goods_sold) * 365 if cost_of_goods_sold > 0 else 0

        cash_conversion_cycle = days_sales_outstanding + days_inventory_outstanding - days_payable_outstanding

        # Turnover ratios
        net_working_capital_turnover = revenue / working_capital if working_capital > 0 else 0
        current_asset_turnover = revenue / current_assets if current_assets > 0 else 0

        return LiquidityMetrics(
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            cash_ratio=cash_ratio,
            operating_cash_flow_ratio=operating_cash_flow_ratio,
            working_capital=working_capital,
            working_capital_ratio=working_capital_ratio,
            cash_conversion_cycle=cash_conversion_cycle,
            days_sales_outstanding=days_sales_outstanding,
            days_inventory_outstanding=days_inventory_outstanding,
            days_payable_outstanding=days_payable_outstanding,
            net_working_capital_turnover=net_working_capital_turnover,
            current_asset_turnover=current_asset_turnover
        )

    def _generate_insights(self, metrics: LiquidityMetrics, fs: FinancialStatements) -> List[Dict[str, Any]]:
        """Generate insights based on liquidity metrics"""
        insights = []

        # Current Ratio Analysis
        if metrics.current_ratio > 2.5:
            insights.append({
                "type": "warning",
                "title_ar": "نسبة تداول مرتفعة",
                "title_en": "High Current Ratio",
                "description_ar": f"نسبة التداول {metrics.current_ratio:.2f} مرتفعة، قد تشير إلى عدم كفاءة استخدام الأصول",
                "description_en": f"Current ratio of {metrics.current_ratio:.2f} is high, may indicate inefficient asset utilization",
                "impact": "medium",
                "metric": "current_ratio",
                "value": metrics.current_ratio
            })
        elif metrics.current_ratio < 1.0:
            insights.append({
                "type": "alert",
                "title_ar": "نسبة تداول منخفضة",
                "title_en": "Low Current Ratio",
                "description_ar": f"نسبة التداول {metrics.current_ratio:.2f} أقل من 1، قد تشير إلى مشاكل سيولة",
                "description_en": f"Current ratio of {metrics.current_ratio:.2f} below 1, may indicate liquidity problems",
                "impact": "high",
                "metric": "current_ratio",
                "value": metrics.current_ratio
            })
        else:
            insights.append({
                "type": "positive",
                "title_ar": "نسبة تداول صحية",
                "title_en": "Healthy Current Ratio",
                "description_ar": f"نسبة التداول {metrics.current_ratio:.2f} ضمن المدى الصحي",
                "description_en": f"Current ratio of {metrics.current_ratio:.2f} is within healthy range",
                "impact": "low",
                "metric": "current_ratio",
                "value": metrics.current_ratio
            })

        # Quick Ratio Analysis
        if metrics.quick_ratio < 0.8:
            insights.append({
                "type": "alert",
                "title_ar": "نسبة سيولة سريعة منخفضة",
                "title_en": "Low Quick Ratio",
                "description_ar": f"نسبة السيولة السريعة {metrics.quick_ratio:.2f} منخفضة، قد تواجه صعوبة في سداد الالتزامات قصيرة الأجل",
                "description_en": f"Quick ratio of {metrics.quick_ratio:.2f} is low, may face difficulty meeting short-term obligations",
                "impact": "high",
                "metric": "quick_ratio",
                "value": metrics.quick_ratio
            })

        # Cash Conversion Cycle Analysis
        if metrics.cash_conversion_cycle > 90:
            insights.append({
                "type": "warning",
                "title_ar": "دورة تحويل نقدية طويلة",
                "title_en": "Long Cash Conversion Cycle",
                "description_ar": f"دورة التحويل النقدية {metrics.cash_conversion_cycle:.0f} يوم طويلة، تحتاج إلى تحسين إدارة رأس المال العامل",
                "description_en": f"Cash conversion cycle of {metrics.cash_conversion_cycle:.0f} days is long, needs working capital management improvement",
                "impact": "medium",
                "metric": "cash_conversion_cycle",
                "value": metrics.cash_conversion_cycle
            })
        elif metrics.cash_conversion_cycle < 0:
            insights.append({
                "type": "positive",
                "title_ar": "دورة تحويل نقدية سالبة ممتازة",
                "title_en": "Excellent Negative Cash Conversion Cycle",
                "description_ar": f"دورة التحويل النقدية السالبة {metrics.cash_conversion_cycle:.0f} يوم تشير إلى إدارة ممتازة لرأس المال العامل",
                "description_en": f"Negative cash conversion cycle of {metrics.cash_conversion_cycle:.0f} days indicates excellent working capital management",
                "impact": "positive",
                "metric": "cash_conversion_cycle",
                "value": metrics.cash_conversion_cycle
            })

        # Working Capital Analysis
        if metrics.working_capital < 0:
            insights.append({
                "type": "alert",
                "title_ar": "رأس مال عامل سالب",
                "title_en": "Negative Working Capital",
                "description_ar": f"رأس المال العامل السالب {metrics.working_capital:,.0f} يشير إلى مخاطر سيولة عالية",
                "description_en": f"Negative working capital of {metrics.working_capital:,.0f} indicates high liquidity risk",
                "impact": "high",
                "metric": "working_capital",
                "value": metrics.working_capital
            })

        return insights

    def _compare_with_benchmarks(self, metrics: LiquidityMetrics, sector: str,
                                comparison_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Compare liquidity metrics with industry benchmarks"""
        # Industry benchmark ranges (can be expanded with real data)
        benchmarks = {
            "manufacturing": {
                "current_ratio": {"min": 1.2, "max": 2.0, "optimal": 1.5},
                "quick_ratio": {"min": 0.8, "max": 1.2, "optimal": 1.0},
                "cash_conversion_cycle": {"min": 30, "max": 90, "optimal": 60}
            },
            "retail": {
                "current_ratio": {"min": 1.0, "max": 1.8, "optimal": 1.3},
                "quick_ratio": {"min": 0.5, "max": 1.0, "optimal": 0.7},
                "cash_conversion_cycle": {"min": 15, "max": 45, "optimal": 30}
            },
            "services": {
                "current_ratio": {"min": 1.1, "max": 2.2, "optimal": 1.6},
                "quick_ratio": {"min": 0.9, "max": 1.3, "optimal": 1.1},
                "cash_conversion_cycle": {"min": 20, "max": 60, "optimal": 40}
            },
            "default": {
                "current_ratio": {"min": 1.2, "max": 2.0, "optimal": 1.5},
                "quick_ratio": {"min": 0.8, "max": 1.2, "optimal": 1.0},
                "cash_conversion_cycle": {"min": 30, "max": 90, "optimal": 60}
            }
        }

        sector_benchmarks = benchmarks.get(sector.lower(), benchmarks["default"])

        comparison = {}

        # Current Ratio Comparison
        cr_benchmark = sector_benchmarks["current_ratio"]
        comparison["current_ratio"] = {
            "value": metrics.current_ratio,
            "benchmark_min": cr_benchmark["min"],
            "benchmark_max": cr_benchmark["max"],
            "benchmark_optimal": cr_benchmark["optimal"],
            "performance": self._calculate_performance_score(
                metrics.current_ratio, cr_benchmark["min"], cr_benchmark["max"], cr_benchmark["optimal"]
            )
        }

        # Quick Ratio Comparison
        qr_benchmark = sector_benchmarks["quick_ratio"]
        comparison["quick_ratio"] = {
            "value": metrics.quick_ratio,
            "benchmark_min": qr_benchmark["min"],
            "benchmark_max": qr_benchmark["max"],
            "benchmark_optimal": qr_benchmark["optimal"],
            "performance": self._calculate_performance_score(
                metrics.quick_ratio, qr_benchmark["min"], qr_benchmark["max"], qr_benchmark["optimal"]
            )
        }

        # Cash Conversion Cycle Comparison (lower is better)
        ccc_benchmark = sector_benchmarks["cash_conversion_cycle"]
        comparison["cash_conversion_cycle"] = {
            "value": metrics.cash_conversion_cycle,
            "benchmark_min": ccc_benchmark["min"],
            "benchmark_max": ccc_benchmark["max"],
            "benchmark_optimal": ccc_benchmark["optimal"],
            "performance": self._calculate_performance_score_reverse(
                metrics.cash_conversion_cycle, ccc_benchmark["min"], ccc_benchmark["max"], ccc_benchmark["optimal"]
            )
        }

        return comparison

    def _calculate_performance_score(self, value: float, min_val: float, max_val: float, optimal: float) -> str:
        """Calculate performance score (higher values are better)"""
        if value >= optimal:
            return "excellent" if value <= max_val else "above_optimal"
        elif value >= min_val:
            return "good"
        else:
            return "poor"

    def _calculate_performance_score_reverse(self, value: float, min_val: float, max_val: float, optimal: float) -> str:
        """Calculate performance score (lower values are better)"""
        if value <= optimal:
            return "excellent" if value >= min_val else "above_optimal"
        elif value <= max_val:
            return "good"
        else:
            return "poor"

    def _assess_liquidity_risks(self, metrics: LiquidityMetrics) -> Dict[str, Any]:
        """Assess liquidity-related risks"""
        risks = []
        risk_scores = []

        # Current Ratio Risk
        if metrics.current_ratio < 1.0:
            risks.append({
                "type": "current_ratio_risk",
                "severity": "high",
                "description_ar": "نسبة التداول أقل من 1 تشير إلى مخاطر سيولة عالية",
                "description_en": "Current ratio below 1 indicates high liquidity risk"
            })
            risk_scores.append(8)
        elif metrics.current_ratio < 1.2:
            risks.append({
                "type": "current_ratio_risk",
                "severity": "medium",
                "description_ar": "نسبة التداول منخفضة قد تؤثر على السيولة",
                "description_en": "Low current ratio may affect liquidity"
            })
            risk_scores.append(5)

        # Quick Ratio Risk
        if metrics.quick_ratio < 0.5:
            risks.append({
                "type": "quick_ratio_risk",
                "severity": "high",
                "description_ar": "نسبة السيولة السريعة منخفضة جداً",
                "description_en": "Very low quick ratio"
            })
            risk_scores.append(7)

        # Cash Conversion Cycle Risk
        if metrics.cash_conversion_cycle > 120:
            risks.append({
                "type": "cash_cycle_risk",
                "severity": "medium",
                "description_ar": "دورة التحويل النقدية طويلة تؤثر على السيولة",
                "description_en": "Long cash conversion cycle affects liquidity"
            })
            risk_scores.append(6)

        # Working Capital Risk
        if metrics.working_capital < 0:
            risks.append({
                "type": "working_capital_risk",
                "severity": "high",
                "description_ar": "رأس المال العامل السالب يشير إلى مخاطر سيولة",
                "description_en": "Negative working capital indicates liquidity risk"
            })
            risk_scores.append(9)

        # Calculate overall risk level
        if not risk_scores:
            overall_risk = "low"
        else:
            avg_risk = np.mean(risk_scores)
            if avg_risk >= 7:
                overall_risk = "high"
            elif avg_risk >= 4:
                overall_risk = "medium"
            else:
                overall_risk = "low"

        return {
            "overall_risk": overall_risk,
            "risk_factors": risks,
            "risk_score": np.mean(risk_scores) if risk_scores else 2
        }

    def _analyze_trends(self, fs: FinancialStatements) -> Dict[str, Any]:
        """Analyze liquidity trends if historical data is available"""
        if not fs.historical_data or len(fs.historical_data) < 2:
            return {"trend_available": False}

        trends = {}

        # Calculate trends for key liquidity metrics
        historical_metrics = []
        for historical_fs in fs.historical_data:
            metrics = self._calculate_liquidity_metrics(historical_fs)
            historical_metrics.append(metrics)

        # Current ratio trend
        current_ratios = [m.current_ratio for m in historical_metrics]
        trends["current_ratio_trend"] = self._calculate_trend(current_ratios)

        # Quick ratio trend
        quick_ratios = [m.quick_ratio for m in historical_metrics]
        trends["quick_ratio_trend"] = self._calculate_trend(quick_ratios)

        # Working capital trend
        working_capitals = [m.working_capital for m in historical_metrics]
        trends["working_capital_trend"] = self._calculate_trend(working_capitals)

        return {
            "trend_available": True,
            "trends": trends,
            "periods_analyzed": len(historical_metrics)
        }

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength"""
        if len(values) < 2:
            return {"direction": "stable", "strength": 0}

        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        # Determine trend direction and strength
        if abs(slope) < 0.01:  # Threshold for considering stable
            direction = "stable"
            strength = 0
        elif slope > 0:
            direction = "improving"
            strength = min(abs(slope) * 10, 10)  # Scale to 0-10
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

    def _generate_recommendations(self, metrics: LiquidityMetrics, risk_assessment: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []

        # Current Ratio Recommendations
        if metrics.current_ratio < 1.2:
            recommendations.append({
                "priority": "high",
                "category": "liquidity_improvement",
                "title_ar": "تحسين نسبة التداول",
                "title_en": "Improve Current Ratio",
                "description_ar": "زيادة الأصول المتداولة أو تقليل الخصوم المتداولة لتحسين السيولة قصيرة الأجل",
                "description_en": "Increase current assets or reduce current liabilities to improve short-term liquidity",
                "actions_ar": [
                    "مراجعة سياسات الائتمان وتحصيل الذمم",
                    "تحسين إدارة المخزون",
                    "إعادة جدولة الديون قصيرة الأجل",
                    "زيادة النقدية من خلال التمويل طويل الأجل"
                ],
                "actions_en": [
                    "Review credit policies and receivables collection",
                    "Improve inventory management",
                    "Reschedule short-term debt",
                    "Increase cash through long-term financing"
                ],
                "expected_impact": "high",
                "timeframe": "short_term"
            })

        # Cash Conversion Cycle Recommendations
        if metrics.cash_conversion_cycle > 90:
            recommendations.append({
                "priority": "medium",
                "category": "working_capital_optimization",
                "title_ar": "تحسين دورة التحويل النقدية",
                "title_en": "Optimize Cash Conversion Cycle",
                "description_ar": "تقليل الوقت اللازم لتحويل الاستثمارات إلى نقدية",
                "description_en": "Reduce time required to convert investments to cash",
                "actions_ar": [
                    "تسريع تحصيل الذمم المدينة",
                    "تحسين دوران المخزون",
                    "تمديد فترات سداد الموردين",
                    "تطبيق نظام إدارة المخزون JIT"
                ],
                "actions_en": [
                    "Accelerate accounts receivable collection",
                    "Improve inventory turnover",
                    "Extend supplier payment terms",
                    "Implement JIT inventory management"
                ],
                "expected_impact": "medium",
                "timeframe": "medium_term"
            })

        # Working Capital Recommendations
        if metrics.working_capital < 0:
            recommendations.append({
                "priority": "critical",
                "category": "immediate_action",
                "title_ar": "معالجة رأس المال العامل السالب",
                "title_en": "Address Negative Working Capital",
                "description_ar": "اتخاذ إجراءات فورية لتحسين رأس المال العامل",
                "description_en": "Take immediate actions to improve working capital",
                "actions_ar": [
                    "الحصول على تمويل قصير الأجل",
                    "تسريع تحصيل المستحقات",
                    "تأجيل المدفوعات غير الحرجة",
                    "بيع الأصول غير الضرورية"
                ],
                "actions_en": [
                    "Obtain short-term financing",
                    "Accelerate receivables collection",
                    "Defer non-critical payments",
                    "Sell non-essential assets"
                ],
                "expected_impact": "critical",
                "timeframe": "immediate"
            })

        return recommendations

    def _prepare_charts_data(self, metrics: LiquidityMetrics, fs: FinancialStatements) -> Dict[str, Any]:
        """Prepare data for charts and visualizations"""
        return {
            "liquidity_ratios": {
                "type": "bar_chart",
                "title_ar": "نسب السيولة",
                "title_en": "Liquidity Ratios",
                "data": {
                    "labels_ar": ["نسبة التداول", "نسبة السيولة السريعة", "نسبة النقدية", "نسبة التدفق النقدي التشغيلي"],
                    "labels_en": ["Current Ratio", "Quick Ratio", "Cash Ratio", "Operating Cash Flow Ratio"],
                    "values": [
                        metrics.current_ratio,
                        metrics.quick_ratio,
                        metrics.cash_ratio,
                        metrics.operating_cash_flow_ratio
                    ],
                    "benchmarks": [1.5, 1.0, 0.2, 0.15]  # Industry average benchmarks
                }
            },
            "cash_conversion_cycle": {
                "type": "waterfall_chart",
                "title_ar": "دورة التحويل النقدية",
                "title_en": "Cash Conversion Cycle",
                "data": {
                    "components": [
                        {"name_ar": "أيام المبيعات المستحقة", "name_en": "Days Sales Outstanding", "value": metrics.days_sales_outstanding},
                        {"name_ar": "أيام المخزون المستحقة", "name_en": "Days Inventory Outstanding", "value": metrics.days_inventory_outstanding},
                        {"name_ar": "أيام الدفع المستحقة", "name_en": "Days Payable Outstanding", "value": -metrics.days_payable_outstanding},
                    ],
                    "total": metrics.cash_conversion_cycle
                }
            },
            "working_capital_composition": {
                "type": "pie_chart",
                "title_ar": "تركيب رأس المال العامل",
                "title_en": "Working Capital Composition",
                "data": {
                    "labels_ar": ["النقدية", "الذمم المدينة", "المخزون", "أصول متداولة أخرى"],
                    "labels_en": ["Cash", "Receivables", "Inventory", "Other Current Assets"],
                    "values": [
                        fs.balance_sheet.get('cash_and_cash_equivalents', 0),
                        fs.balance_sheet.get('accounts_receivable', 0),
                        fs.balance_sheet.get('inventory', 0),
                        fs.balance_sheet.get('current_assets', 0) - fs.balance_sheet.get('cash_and_cash_equivalents', 0) - fs.balance_sheet.get('accounts_receivable', 0) - fs.balance_sheet.get('inventory', 0)
                    ]
                }
            }
        }