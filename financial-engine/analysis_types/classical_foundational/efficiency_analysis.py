"""
Efficiency Analysis Module
تحليلات الكفاءة المالية

This module implements comprehensive efficiency analysis including:
- Asset Turnover Analysis
- Inventory Management Efficiency
- Receivables Management Efficiency
- Working Capital Efficiency
- Operational Efficiency Metrics
- Resource Utilization Analysis
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from ..core.data_models import FinancialStatements, AnalysisResult


@dataclass
class EfficiencyMetrics:
    """Efficiency analysis metrics"""
    # Asset Turnover Metrics
    total_asset_turnover: float
    fixed_asset_turnover: float
    current_asset_turnover: float
    working_capital_turnover: float

    # Inventory Efficiency
    inventory_turnover: float
    days_in_inventory: float
    inventory_to_sales_ratio: float

    # Receivables Efficiency
    receivables_turnover: float
    days_sales_outstanding: float
    receivables_to_sales_ratio: float

    # Payables Efficiency
    payables_turnover: float
    days_payable_outstanding: float

    # Operational Efficiency
    revenue_per_employee: Optional[float]
    asset_per_employee: Optional[float]
    operating_cycle: float
    cash_conversion_cycle: float

    # Capital Efficiency
    capital_employed_turnover: float
    invested_capital_turnover: float

    # Cost Efficiency
    cost_to_revenue_ratio: float
    operating_expense_ratio: float
    administrative_expense_ratio: Optional[float]


class EfficiencyAnalyzer:
    """Comprehensive efficiency analysis engine"""

    def __init__(self):
        self.analysis_type = "efficiency_analysis"
        self.category = "classical_foundational"

    def analyze(self, financial_statements: FinancialStatements,
                comparison_data: Optional[Dict] = None) -> AnalysisResult:
        """
        Perform comprehensive efficiency analysis
        تنفيذ تحليل شامل للكفاءة المالية
        """
        try:
            # Calculate efficiency metrics
            metrics = self._calculate_efficiency_metrics(financial_statements)

            # Generate insights and recommendations
            insights = self._generate_insights(metrics, financial_statements)

            # Calculate industry benchmarks comparison
            benchmark_comparison = self._compare_with_benchmarks(
                metrics, financial_statements.sector, comparison_data
            )

            # Efficiency assessment
            efficiency_assessment = self._assess_efficiency(metrics)

            # Trend analysis if historical data available
            trend_analysis = self._analyze_trends(financial_statements)

            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                metrics=metrics.__dict__,
                insights=insights,
                recommendations=self._generate_recommendations(metrics, efficiency_assessment),
                risk_level=efficiency_assessment["overall_efficiency"],
                benchmark_comparison=benchmark_comparison,
                trend_analysis=trend_analysis,
                charts_data=self._prepare_charts_data(metrics, financial_statements),
                timestamp=datetime.now()
            )

        except Exception as e:
            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                error=f"Efficiency analysis failed: {str(e)}",
                timestamp=datetime.now()
            )

    def _calculate_efficiency_metrics(self, fs: FinancialStatements) -> EfficiencyMetrics:
        """Calculate all efficiency metrics"""
        balance_sheet = fs.balance_sheet
        income_statement = fs.income_statement

        # Financial statement items
        revenue = income_statement.get('revenue', 1)  # Avoid division by zero
        cost_of_goods_sold = income_statement.get('cost_of_goods_sold', 0)
        operating_expenses = income_statement.get('operating_expenses', 0)
        administrative_expenses = income_statement.get('administrative_expenses', 0)

        total_assets = balance_sheet.get('total_assets', 1)
        fixed_assets = balance_sheet.get('fixed_assets', 0)
        current_assets = balance_sheet.get('current_assets', 0)
        inventory = balance_sheet.get('inventory', 0)
        accounts_receivable = balance_sheet.get('accounts_receivable', 0)
        accounts_payable = balance_sheet.get('accounts_payable', 0)
        current_liabilities = balance_sheet.get('current_liabilities', 0)
        total_equity = balance_sheet.get('total_equity', 0)
        total_debt = balance_sheet.get('total_debt', 0)

        # Calculate working capital
        working_capital = current_assets - current_liabilities

        # Asset Turnover Metrics
        total_asset_turnover = revenue / total_assets if total_assets > 0 else 0
        fixed_asset_turnover = revenue / fixed_assets if fixed_assets > 0 else 0
        current_asset_turnover = revenue / current_assets if current_assets > 0 else 0
        working_capital_turnover = revenue / working_capital if working_capital > 0 else 0

        # Inventory Efficiency
        inventory_turnover = cost_of_goods_sold / inventory if inventory > 0 else 0
        days_in_inventory = 365 / inventory_turnover if inventory_turnover > 0 else 0
        inventory_to_sales_ratio = inventory / revenue if revenue > 0 else 0

        # Receivables Efficiency
        receivables_turnover = revenue / accounts_receivable if accounts_receivable > 0 else 0
        days_sales_outstanding = 365 / receivables_turnover if receivables_turnover > 0 else 0
        receivables_to_sales_ratio = accounts_receivable / revenue if revenue > 0 else 0

        # Payables Efficiency
        payables_turnover = cost_of_goods_sold / accounts_payable if accounts_payable > 0 else 0
        days_payable_outstanding = 365 / payables_turnover if payables_turnover > 0 else 0

        # Operational Efficiency
        employee_count = fs.employee_count
        revenue_per_employee = revenue / employee_count if employee_count else None
        asset_per_employee = total_assets / employee_count if employee_count else None

        operating_cycle = days_in_inventory + days_sales_outstanding
        cash_conversion_cycle = operating_cycle - days_payable_outstanding

        # Capital Efficiency
        capital_employed = total_assets - current_liabilities
        capital_employed_turnover = revenue / capital_employed if capital_employed > 0 else 0
        invested_capital = total_equity + total_debt
        invested_capital_turnover = revenue / invested_capital if invested_capital > 0 else 0

        # Cost Efficiency
        total_costs = cost_of_goods_sold + operating_expenses
        cost_to_revenue_ratio = total_costs / revenue if revenue > 0 else 0
        operating_expense_ratio = operating_expenses / revenue if revenue > 0 else 0
        administrative_expense_ratio = administrative_expenses / revenue if revenue > 0 and administrative_expenses > 0 else None

        return EfficiencyMetrics(
            total_asset_turnover=total_asset_turnover,
            fixed_asset_turnover=fixed_asset_turnover,
            current_asset_turnover=current_asset_turnover,
            working_capital_turnover=working_capital_turnover,
            inventory_turnover=inventory_turnover,
            days_in_inventory=days_in_inventory,
            inventory_to_sales_ratio=inventory_to_sales_ratio,
            receivables_turnover=receivables_turnover,
            days_sales_outstanding=days_sales_outstanding,
            receivables_to_sales_ratio=receivables_to_sales_ratio,
            payables_turnover=payables_turnover,
            days_payable_outstanding=days_payable_outstanding,
            revenue_per_employee=revenue_per_employee,
            asset_per_employee=asset_per_employee,
            operating_cycle=operating_cycle,
            cash_conversion_cycle=cash_conversion_cycle,
            capital_employed_turnover=capital_employed_turnover,
            invested_capital_turnover=invested_capital_turnover,
            cost_to_revenue_ratio=cost_to_revenue_ratio,
            operating_expense_ratio=operating_expense_ratio,
            administrative_expense_ratio=administrative_expense_ratio
        )

    def _generate_insights(self, metrics: EfficiencyMetrics, fs: FinancialStatements) -> List[Dict[str, Any]]:
        """Generate insights based on efficiency metrics"""
        insights = []

        # Asset Turnover Analysis
        if metrics.total_asset_turnover < 0.5:
            insights.append({
                "type": "warning",
                "title_ar": "كفاءة استخدام الأصول منخفضة",
                "title_en": "Low Asset Utilization Efficiency",
                "description_ar": f"معدل دوران الأصول {metrics.total_asset_turnover:.2f} منخفض، يشير إلى عدم كفاءة استخدام الأصول",
                "description_en": f"Asset turnover of {metrics.total_asset_turnover:.2f} is low, indicating inefficient asset utilization",
                "impact": "medium",
                "metric": "total_asset_turnover",
                "value": metrics.total_asset_turnover
            })
        elif metrics.total_asset_turnover > 2.0:
            insights.append({
                "type": "positive",
                "title_ar": "كفاءة ممتازة في استخدام الأصول",
                "title_en": "Excellent Asset Utilization",
                "description_ar": f"معدل دوران الأصول {metrics.total_asset_turnover:.2f} ممتاز، يشير إلى استخدام فعال للأصول",
                "description_en": f"Asset turnover of {metrics.total_asset_turnover:.2f} is excellent, indicating effective asset utilization",
                "impact": "positive",
                "metric": "total_asset_turnover",
                "value": metrics.total_asset_turnover
            })

        # Inventory Efficiency Analysis
        if metrics.inventory_turnover < 4:
            insights.append({
                "type": "warning",
                "title_ar": "بطء في دوران المخزون",
                "title_en": "Slow Inventory Turnover",
                "description_ar": f"معدل دوران المخزون {metrics.inventory_turnover:.1f} مرات منخفض، قد يشير إلى مخزون راكد",
                "description_en": f"Inventory turnover of {metrics.inventory_turnover:.1f} times is low, may indicate stagnant inventory",
                "impact": "medium",
                "metric": "inventory_turnover",
                "value": metrics.inventory_turnover
            })
        elif metrics.inventory_turnover > 12:
            insights.append({
                "type": "warning",
                "title_ar": "دوران مخزون سريع جداً",
                "title_en": "Very Fast Inventory Turnover",
                "description_ar": f"معدل دوران المخزون {metrics.inventory_turnover:.1f} مرات سريع جداً، قد يشير إلى نقص في المخزون",
                "description_en": f"Inventory turnover of {metrics.inventory_turnover:.1f} times is very fast, may indicate stock shortages",
                "impact": "medium",
                "metric": "inventory_turnover",
                "value": metrics.inventory_turnover
            })

        # Receivables Efficiency Analysis
        if metrics.days_sales_outstanding > 60:
            insights.append({
                "type": "alert",
                "title_ar": "بطء في تحصيل الذمم",
                "title_en": "Slow Receivables Collection",
                "description_ar": f"أيام المبيعات المستحقة {metrics.days_sales_outstanding:.0f} يوم طويلة، تحتاج تحسين سياسات التحصيل",
                "description_en": f"Days sales outstanding of {metrics.days_sales_outstanding:.0f} days is long, needs improved collection policies",
                "impact": "high",
                "metric": "days_sales_outstanding",
                "value": metrics.days_sales_outstanding
            })
        elif metrics.days_sales_outstanding < 30:
            insights.append({
                "type": "positive",
                "title_ar": "تحصيل ممتاز للذمم",
                "title_en": "Excellent Receivables Collection",
                "description_ar": f"أيام المبيعات المستحقة {metrics.days_sales_outstanding:.0f} يوم قصيرة، تشير إلى تحصيل فعال",
                "description_en": f"Days sales outstanding of {metrics.days_sales_outstanding:.0f} days is short, indicates effective collection",
                "impact": "positive",
                "metric": "days_sales_outstanding",
                "value": metrics.days_sales_outstanding
            })

        # Cash Conversion Cycle Analysis
        if metrics.cash_conversion_cycle > 90:
            insights.append({
                "type": "warning",
                "title_ar": "دورة تحويل نقدية طويلة",
                "title_en": "Long Cash Conversion Cycle",
                "description_ar": f"دورة التحويل النقدية {metrics.cash_conversion_cycle:.0f} يوم طويلة، تؤثر على السيولة",
                "description_en": f"Cash conversion cycle of {metrics.cash_conversion_cycle:.0f} days is long, affects liquidity",
                "impact": "medium",
                "metric": "cash_conversion_cycle",
                "value": metrics.cash_conversion_cycle
            })
        elif metrics.cash_conversion_cycle < 0:
            insights.append({
                "type": "positive",
                "title_ar": "دورة تحويل نقدية سالبة ممتازة",
                "title_en": "Excellent Negative Cash Conversion Cycle",
                "description_ar": f"دورة التحويل النقدية السالبة {metrics.cash_conversion_cycle:.0f} يوم تشير إلى إدارة ممتازة",
                "description_en": f"Negative cash conversion cycle of {metrics.cash_conversion_cycle:.0f} days indicates excellent management",
                "impact": "positive",
                "metric": "cash_conversion_cycle",
                "value": metrics.cash_conversion_cycle
            })

        # Employee Productivity Analysis
        if metrics.revenue_per_employee is not None:
            if metrics.revenue_per_employee < 100000:  # Assuming currency in local units
                insights.append({
                    "type": "warning",
                    "title_ar": "إنتاجية منخفضة للموظفين",
                    "title_en": "Low Employee Productivity",
                    "description_ar": f"الإيراد لكل موظف {metrics.revenue_per_employee:,.0f} منخفض",
                    "description_en": f"Revenue per employee of {metrics.revenue_per_employee:,.0f} is low",
                    "impact": "medium",
                    "metric": "revenue_per_employee",
                    "value": metrics.revenue_per_employee
                })
            elif metrics.revenue_per_employee > 500000:
                insights.append({
                    "type": "positive",
                    "title_ar": "إنتاجية ممتازة للموظفين",
                    "title_en": "Excellent Employee Productivity",
                    "description_ar": f"الإيراد لكل موظف {metrics.revenue_per_employee:,.0f} ممتاز",
                    "description_en": f"Revenue per employee of {metrics.revenue_per_employee:,.0f} is excellent",
                    "impact": "positive",
                    "metric": "revenue_per_employee",
                    "value": metrics.revenue_per_employee
                })

        # Cost Efficiency Analysis
        if metrics.cost_to_revenue_ratio > 0.8:
            insights.append({
                "type": "alert",
                "title_ar": "نسبة تكاليف مرتفعة",
                "title_en": "High Cost Ratio",
                "description_ar": f"نسبة التكاليف إلى الإيرادات {metrics.cost_to_revenue_ratio:.1%} مرتفعة",
                "description_en": f"Cost to revenue ratio of {metrics.cost_to_revenue_ratio:.1%} is high",
                "impact": "high",
                "metric": "cost_to_revenue_ratio",
                "value": metrics.cost_to_revenue_ratio
            })

        return insights

    def _compare_with_benchmarks(self, metrics: EfficiencyMetrics, sector: str,
                                comparison_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Compare efficiency metrics with industry benchmarks"""
        # Industry benchmark ranges
        benchmarks = {
            "manufacturing": {
                "total_asset_turnover": {"min": 0.8, "max": 1.5, "optimal": 1.2},
                "inventory_turnover": {"min": 6, "max": 12, "optimal": 8},
                "days_sales_outstanding": {"min": 30, "max": 60, "optimal": 45},
                "cash_conversion_cycle": {"min": 30, "max": 90, "optimal": 60}
            },
            "retail": {
                "total_asset_turnover": {"min": 1.5, "max": 3.0, "optimal": 2.2},
                "inventory_turnover": {"min": 8, "max": 15, "optimal": 12},
                "days_sales_outstanding": {"min": 15, "max": 45, "optimal": 30},
                "cash_conversion_cycle": {"min": 15, "max": 60, "optimal": 35}
            },
            "services": {
                "total_asset_turnover": {"min": 1.0, "max": 2.5, "optimal": 1.8},
                "inventory_turnover": {"min": 10, "max": 25, "optimal": 15},
                "days_sales_outstanding": {"min": 25, "max": 55, "optimal": 40},
                "cash_conversion_cycle": {"min": 20, "max": 70, "optimal": 45}
            },
            "default": {
                "total_asset_turnover": {"min": 0.8, "max": 2.0, "optimal": 1.4},
                "inventory_turnover": {"min": 6, "max": 15, "optimal": 10},
                "days_sales_outstanding": {"min": 25, "max": 60, "optimal": 42},
                "cash_conversion_cycle": {"min": 25, "max": 80, "optimal": 50}
            }
        }

        sector_benchmarks = benchmarks.get(sector.lower(), benchmarks["default"])
        comparison = {}

        for metric in ["total_asset_turnover", "inventory_turnover", "days_sales_outstanding", "cash_conversion_cycle"]:
            metric_value = getattr(metrics, metric)
            benchmark = sector_benchmarks[metric]

            # For days and cycle metrics, lower is better
            if metric in ["days_sales_outstanding", "cash_conversion_cycle"]:
                performance = self._calculate_performance_score_reverse(
                    metric_value, benchmark["min"], benchmark["max"], benchmark["optimal"]
                )
            else:
                performance = self._calculate_performance_score(
                    metric_value, benchmark["min"], benchmark["max"], benchmark["optimal"]
                )

            comparison[metric] = {
                "value": metric_value,
                "benchmark_min": benchmark["min"],
                "benchmark_max": benchmark["max"],
                "benchmark_optimal": benchmark["optimal"],
                "performance": performance
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

    def _assess_efficiency(self, metrics: EfficiencyMetrics) -> Dict[str, Any]:
        """Assess overall efficiency performance"""
        efficiency_factors = []
        scores = []

        # Asset Turnover Efficiency
        if metrics.total_asset_turnover > 1.5:
            efficiency_factors.append("excellent_asset_utilization")
            scores.append(9)
        elif metrics.total_asset_turnover > 1.0:
            efficiency_factors.append("good_asset_utilization")
            scores.append(7)
        elif metrics.total_asset_turnover > 0.5:
            efficiency_factors.append("acceptable_asset_utilization")
            scores.append(5)
        else:
            efficiency_factors.append("poor_asset_utilization")
            scores.append(3)

        # Inventory Efficiency
        if 6 <= metrics.inventory_turnover <= 12:
            efficiency_factors.append("optimal_inventory_management")
            scores.append(8)
        elif metrics.inventory_turnover > 4:
            efficiency_factors.append("acceptable_inventory_management")
            scores.append(6)
        else:
            efficiency_factors.append("poor_inventory_management")
            scores.append(3)

        # Receivables Efficiency
        if metrics.days_sales_outstanding < 45:
            efficiency_factors.append("excellent_receivables_management")
            scores.append(8)
        elif metrics.days_sales_outstanding < 60:
            efficiency_factors.append("good_receivables_management")
            scores.append(6)
        else:
            efficiency_factors.append("poor_receivables_management")
            scores.append(3)

        # Cash Conversion Cycle Efficiency
        if metrics.cash_conversion_cycle < 45:
            efficiency_factors.append("excellent_working_capital_management")
            scores.append(9)
        elif metrics.cash_conversion_cycle < 75:
            efficiency_factors.append("good_working_capital_management")
            scores.append(6)
        else:
            efficiency_factors.append("poor_working_capital_management")
            scores.append(3)

        # Calculate overall efficiency
        avg_score = np.mean(scores) if scores else 5
        if avg_score >= 8:
            overall_efficiency = "excellent"
        elif avg_score >= 6:
            overall_efficiency = "good"
        elif avg_score >= 4:
            overall_efficiency = "acceptable"
        else:
            overall_efficiency = "poor"

        return {
            "overall_efficiency": overall_efficiency,
            "efficiency_factors": efficiency_factors,
            "efficiency_score": avg_score
        }

    def _analyze_trends(self, fs: FinancialStatements) -> Dict[str, Any]:
        """Analyze efficiency trends"""
        if not fs.historical_data or len(fs.historical_data) < 2:
            return {"trend_available": False}

        trends = {}

        # Calculate historical metrics
        historical_metrics = []
        for historical_fs in fs.historical_data:
            metrics = self._calculate_efficiency_metrics(historical_fs)
            historical_metrics.append(metrics)

        # Asset turnover trends
        asset_turnovers = [m.total_asset_turnover for m in historical_metrics]
        trends["asset_turnover_trend"] = self._calculate_trend(asset_turnovers)

        # Inventory efficiency trends
        inventory_turnovers = [m.inventory_turnover for m in historical_metrics]
        trends["inventory_efficiency_trend"] = self._calculate_trend(inventory_turnovers)

        # Receivables efficiency trends
        dso_values = [m.days_sales_outstanding for m in historical_metrics]
        trends["receivables_efficiency_trend"] = self._calculate_trend_reverse(dso_values)

        # Cash conversion cycle trends
        ccc_values = [m.cash_conversion_cycle for m in historical_metrics]
        trends["cash_cycle_trend"] = self._calculate_trend_reverse(ccc_values)

        return {
            "trend_available": True,
            "trends": trends,
            "periods_analyzed": len(historical_metrics)
        }

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength (higher is better)"""
        if len(values) < 2:
            return {"direction": "stable", "strength": 0}

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if abs(slope) < 0.05:
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

    def _calculate_trend_reverse(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength (lower is better)"""
        if len(values) < 2:
            return {"direction": "stable", "strength": 0}

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if abs(slope) < 0.5:
            direction = "stable"
            strength = 0
        elif slope < 0:  # Decreasing is good for these metrics
            direction = "improving"
            strength = min(abs(slope), 10)
        else:
            direction = "declining"
            strength = min(abs(slope), 10)

        return {
            "direction": direction,
            "strength": strength,
            "slope": slope,
            "latest_value": values[-1],
            "previous_value": values[-2] if len(values) >= 2 else None
        }

    def _generate_recommendations(self, metrics: EfficiencyMetrics, efficiency: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []

        # Asset Turnover Improvement
        if metrics.total_asset_turnover < 1.0:
            recommendations.append({
                "priority": "high",
                "category": "asset_optimization",
                "title_ar": "تحسين كفاءة استخدام الأصول",
                "title_en": "Improve Asset Utilization Efficiency",
                "description_ar": "زيادة معدل دوران الأصول لتحسين الكفاءة التشغيلية",
                "description_en": "Increase asset turnover to improve operational efficiency",
                "actions_ar": [
                    "مراجعة الأصول غير المنتجة",
                    "تحسين استغلال الطاقة الإنتاجية",
                    "بيع الأصول الزائدة",
                    "تحسين إدارة المخزون"
                ],
                "actions_en": [
                    "Review non-productive assets",
                    "Improve capacity utilization",
                    "Sell excess assets",
                    "Improve inventory management"
                ],
                "expected_impact": "high",
                "timeframe": "medium_term"
            })

        # Inventory Management Improvement
        if metrics.inventory_turnover < 6:
            recommendations.append({
                "priority": "medium",
                "category": "inventory_optimization",
                "title_ar": "تحسين إدارة المخزون",
                "title_en": "Improve Inventory Management",
                "description_ar": "تسريع دوران المخزون وتقليل الأموال المقيدة",
                "description_en": "Accelerate inventory turnover and reduce tied-up capital",
                "actions_ar": [
                    "تطبيق نظام إدارة المخزون JIT",
                    "تحسين توقعات الطلب",
                    "تقليل مستويات الأمان في المخزون",
                    "تحسين سلسلة التوريد"
                ],
                "actions_en": [
                    "Implement JIT inventory system",
                    "Improve demand forecasting",
                    "Reduce safety stock levels",
                    "Optimize supply chain"
                ],
                "expected_impact": "medium",
                "timeframe": "short_term"
            })

        # Receivables Management Improvement
        if metrics.days_sales_outstanding > 60:
            recommendations.append({
                "priority": "high",
                "category": "receivables_optimization",
                "title_ar": "تحسين إدارة الذمم المدينة",
                "title_en": "Improve Receivables Management",
                "description_ar": "تسريع تحصيل الذمم وتحسين التدفق النقدي",
                "description_en": "Accelerate receivables collection and improve cash flow",
                "actions_ar": [
                    "مراجعة شروط الائتمان",
                    "تحسين عمليات التحصيل",
                    "تطبيق نظام متابعة آلي",
                    "تقديم حوافز للدفع المبكر"
                ],
                "actions_en": [
                    "Review credit terms",
                    "Improve collection processes",
                    "Implement automated follow-up system",
                    "Offer early payment incentives"
                ],
                "expected_impact": "high",
                "timeframe": "short_term"
            })

        # Working Capital Optimization
        if metrics.cash_conversion_cycle > 90:
            recommendations.append({
                "priority": "medium",
                "category": "working_capital_optimization",
                "title_ar": "تحسين إدارة رأس المال العامل",
                "title_en": "Optimize Working Capital Management",
                "description_ar": "تقليل دورة التحويل النقدية لتحسين السيولة",
                "description_en": "Reduce cash conversion cycle to improve liquidity",
                "actions_ar": [
                    "تسريع تحصيل المستحقات",
                    "تحسين دوران المخزون",
                    "تمديد فترات سداد الموردين",
                    "تحسين التنبؤات المالية"
                ],
                "actions_en": [
                    "Accelerate receivables collection",
                    "Improve inventory turnover",
                    "Extend supplier payment terms",
                    "Improve financial forecasting"
                ],
                "expected_impact": "medium",
                "timeframe": "medium_term"
            })

        # Cost Efficiency Improvement
        if metrics.cost_to_revenue_ratio > 0.75:
            recommendations.append({
                "priority": "high",
                "category": "cost_optimization",
                "title_ar": "تحسين كفاءة التكاليف",
                "title_en": "Improve Cost Efficiency",
                "description_ar": "خفض نسبة التكاليف إلى الإيرادات",
                "description_en": "Reduce cost-to-revenue ratio",
                "actions_ar": [
                    "مراجعة هيكل التكاليف",
                    "أتمتة العمليات",
                    "تحسين الكفاءة التشغيلية",
                    "إعادة التفاوض مع الموردين"
                ],
                "actions_en": [
                    "Review cost structure",
                    "Automate processes",
                    "Improve operational efficiency",
                    "Renegotiate with suppliers"
                ],
                "expected_impact": "high",
                "timeframe": "medium_term"
            })

        return recommendations

    def _prepare_charts_data(self, metrics: EfficiencyMetrics, fs: FinancialStatements) -> Dict[str, Any]:
        """Prepare data for charts and visualizations"""
        return {
            "turnover_ratios": {
                "type": "bar_chart",
                "title_ar": "نسب الدوران",
                "title_en": "Turnover Ratios",
                "data": {
                    "labels_ar": ["دوران الأصول", "دوران الأصول الثابتة", "دوران الأصول المتداولة", "دوران المخزون"],
                    "labels_en": ["Asset Turnover", "Fixed Asset Turnover", "Current Asset Turnover", "Inventory Turnover"],
                    "values": [
                        metrics.total_asset_turnover,
                        metrics.fixed_asset_turnover,
                        metrics.current_asset_turnover,
                        metrics.inventory_turnover
                    ]
                }
            },
            "efficiency_cycle": {
                "type": "waterfall_chart",
                "title_ar": "دورة الكفاءة التشغيلية",
                "title_en": "Operating Efficiency Cycle",
                "data": {
                    "components": [
                        {"name_ar": "أيام المخزون", "name_en": "Days in Inventory", "value": metrics.days_in_inventory},
                        {"name_ar": "أيام المبيعات المستحقة", "name_en": "Days Sales Outstanding", "value": metrics.days_sales_outstanding},
                        {"name_ar": "أيام الدفع المستحقة", "name_en": "Days Payable Outstanding", "value": -metrics.days_payable_outstanding},
                    ],
                    "operating_cycle": metrics.operating_cycle,
                    "cash_conversion_cycle": metrics.cash_conversion_cycle
                }
            },
            "productivity_metrics": {
                "type": "gauge_chart",
                "title_ar": "مقاييس الإنتاجية",
                "title_en": "Productivity Metrics",
                "data": {
                    "revenue_per_employee": metrics.revenue_per_employee,
                    "asset_per_employee": metrics.asset_per_employee,
                    "benchmarks": {
                        "revenue_per_employee": 250000,  # Industry benchmark
                        "asset_per_employee": 200000
                    }
                }
            }
        }