"""
Profitability Analysis Module
تحليلات الربحية المالية

This module implements comprehensive profitability analysis including:
- Margin Analysis (Gross, Operating, Net, EBITDA)
- Return Ratios (ROA, ROE, ROIC, ROI)
- Earnings Quality Analysis
- Profit Trend Analysis
- Cost Structure Analysis
- Revenue Analysis
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from ..core.data_models import FinancialStatements, AnalysisResult


@dataclass
class ProfitabilityMetrics:
    """Profitability analysis metrics"""
    # Margin Ratios
    gross_profit_margin: float
    operating_profit_margin: float
    net_profit_margin: float
    ebitda_margin: float
    ebit_margin: float

    # Return Ratios
    return_on_assets: float
    return_on_equity: float
    return_on_invested_capital: float
    return_on_sales: float

    # Earnings Analysis
    earnings_per_share: float
    diluted_eps: float
    price_earnings_ratio: Optional[float]
    earnings_quality_score: float

    # Cost Analysis
    cost_of_goods_sold_ratio: float
    operating_expense_ratio: float
    interest_coverage_ratio: float

    # Growth Metrics
    revenue_growth: Optional[float]
    profit_growth: Optional[float]
    eps_growth: Optional[float]


class ProfitabilityAnalyzer:
    """Comprehensive profitability analysis engine"""

    def __init__(self):
        self.analysis_type = "profitability_analysis"
        self.category = "classical_foundational"

    def analyze(self, financial_statements: FinancialStatements,
                comparison_data: Optional[Dict] = None) -> AnalysisResult:
        """
        Perform comprehensive profitability analysis
        تنفيذ تحليل شامل للربحية المالية
        """
        try:
            # Calculate profitability metrics
            metrics = self._calculate_profitability_metrics(financial_statements)

            # Generate insights and recommendations
            insights = self._generate_insights(metrics, financial_statements)

            # Calculate industry benchmarks comparison
            benchmark_comparison = self._compare_with_benchmarks(
                metrics, financial_statements.sector, comparison_data
            )

            # Performance assessment
            performance_assessment = self._assess_performance(metrics)

            # Trend analysis if historical data available
            trend_analysis = self._analyze_trends(financial_statements)

            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                metrics=metrics.__dict__,
                insights=insights,
                recommendations=self._generate_recommendations(metrics, performance_assessment),
                risk_level=performance_assessment["overall_performance"],
                benchmark_comparison=benchmark_comparison,
                trend_analysis=trend_analysis,
                charts_data=self._prepare_charts_data(metrics, financial_statements),
                timestamp=datetime.now()
            )

        except Exception as e:
            return AnalysisResult(
                analysis_type=self.analysis_type,
                category=self.category,
                error=f"Profitability analysis failed: {str(e)}",
                timestamp=datetime.now()
            )

    def _calculate_profitability_metrics(self, fs: FinancialStatements) -> ProfitabilityMetrics:
        """Calculate all profitability metrics"""
        income_statement = fs.income_statement
        balance_sheet = fs.balance_sheet

        # Income Statement items
        revenue = income_statement.get('revenue', 1)  # Avoid division by zero
        gross_profit = income_statement.get('gross_profit', 0)
        operating_income = income_statement.get('operating_income', 0)
        net_income = income_statement.get('net_income', 0)
        ebitda = income_statement.get('ebitda', 0)
        ebit = income_statement.get('ebit', operating_income)
        cost_of_goods_sold = income_statement.get('cost_of_goods_sold', 0)
        operating_expenses = income_statement.get('operating_expenses', 0)
        interest_expense = income_statement.get('interest_expense', 1)  # Avoid division by zero

        # Balance Sheet items
        total_assets = balance_sheet.get('total_assets', 1)
        total_equity = balance_sheet.get('total_equity', 1)
        invested_capital = balance_sheet.get('total_equity', 0) + balance_sheet.get('total_debt', 0)

        # Shares data
        shares_outstanding = fs.shares_outstanding or 1
        share_price = fs.share_price

        # Calculate margin ratios
        gross_profit_margin = (gross_profit / revenue) * 100 if revenue > 0 else 0
        operating_profit_margin = (operating_income / revenue) * 100 if revenue > 0 else 0
        net_profit_margin = (net_income / revenue) * 100 if revenue > 0 else 0
        ebitda_margin = (ebitda / revenue) * 100 if revenue > 0 else 0
        ebit_margin = (ebit / revenue) * 100 if revenue > 0 else 0

        # Calculate return ratios
        return_on_assets = (net_income / total_assets) * 100 if total_assets > 0 else 0
        return_on_equity = (net_income / total_equity) * 100 if total_equity > 0 else 0
        return_on_invested_capital = (ebit / invested_capital) * 100 if invested_capital > 0 else 0
        return_on_sales = net_profit_margin  # Same as net profit margin

        # Calculate earnings metrics
        earnings_per_share = net_income / shares_outstanding if shares_outstanding > 0 else 0
        diluted_eps = earnings_per_share  # Simplified, would need diluted shares data
        price_earnings_ratio = share_price / earnings_per_share if earnings_per_share > 0 and share_price else None

        # Calculate earnings quality score (simplified)
        earnings_quality_score = self._calculate_earnings_quality(fs)

        # Calculate cost ratios
        cost_of_goods_sold_ratio = (cost_of_goods_sold / revenue) * 100 if revenue > 0 else 0
        operating_expense_ratio = (operating_expenses / revenue) * 100 if revenue > 0 else 0
        interest_coverage_ratio = ebit / interest_expense if interest_expense > 0 else float('inf')

        # Calculate growth metrics (if historical data available)
        revenue_growth = self._calculate_growth_rate(fs, 'revenue')
        profit_growth = self._calculate_growth_rate(fs, 'net_income')
        eps_growth = self._calculate_eps_growth(fs)

        return ProfitabilityMetrics(
            gross_profit_margin=gross_profit_margin,
            operating_profit_margin=operating_profit_margin,
            net_profit_margin=net_profit_margin,
            ebitda_margin=ebitda_margin,
            ebit_margin=ebit_margin,
            return_on_assets=return_on_assets,
            return_on_equity=return_on_equity,
            return_on_invested_capital=return_on_invested_capital,
            return_on_sales=return_on_sales,
            earnings_per_share=earnings_per_share,
            diluted_eps=diluted_eps,
            price_earnings_ratio=price_earnings_ratio,
            earnings_quality_score=earnings_quality_score,
            cost_of_goods_sold_ratio=cost_of_goods_sold_ratio,
            operating_expense_ratio=operating_expense_ratio,
            interest_coverage_ratio=interest_coverage_ratio,
            revenue_growth=revenue_growth,
            profit_growth=profit_growth,
            eps_growth=eps_growth
        )

    def _calculate_earnings_quality(self, fs: FinancialStatements) -> float:
        """Calculate earnings quality score based on various factors"""
        score = 100.0  # Start with perfect score

        income_statement = fs.income_statement
        cash_flow = fs.cash_flow_statement

        net_income = income_statement.get('net_income', 0)
        operating_cash_flow = cash_flow.get('operating_cash_flow', 0)

        # Factor 1: Operating cash flow vs net income
        if net_income > 0:
            ocf_to_ni_ratio = operating_cash_flow / net_income
            if ocf_to_ni_ratio < 0.8:
                score -= 20  # Penalty for low cash conversion
            elif ocf_to_ni_ratio > 1.2:
                score += 10  # Bonus for strong cash conversion

        # Factor 2: Revenue quality (simplified)
        # Check for unusual revenue spikes or patterns
        if fs.historical_data and len(fs.historical_data) > 1:
            current_revenue = income_statement.get('revenue', 0)
            previous_revenue = fs.historical_data[-1].income_statement.get('revenue', 1)
            revenue_growth = (current_revenue - previous_revenue) / previous_revenue * 100

            if revenue_growth > 50:  # Unusual spike
                score -= 15
            elif revenue_growth < -30:  # Unusual drop
                score -= 10

        # Factor 3: Expense consistency
        # Check for unusual one-time items (simplified)
        total_expenses = income_statement.get('total_expenses', 0)
        revenue = income_statement.get('revenue', 1)
        expense_ratio = total_expenses / revenue * 100

        if expense_ratio > 95:  # Very high expense ratio
            score -= 15

        return max(0, min(100, score))

    def _calculate_growth_rate(self, fs: FinancialStatements, metric: str) -> Optional[float]:
        """Calculate growth rate for a specific metric"""
        if not fs.historical_data or len(fs.historical_data) == 0:
            return None

        current_value = fs.income_statement.get(metric, 0)
        previous_value = fs.historical_data[-1].income_statement.get(metric, 0)

        if previous_value == 0:
            return None

        return ((current_value - previous_value) / previous_value) * 100

    def _calculate_eps_growth(self, fs: FinancialStatements) -> Optional[float]:
        """Calculate EPS growth rate"""
        if not fs.historical_data or len(fs.historical_data) == 0:
            return None

        current_eps = fs.income_statement.get('net_income', 0) / (fs.shares_outstanding or 1)
        previous_eps = fs.historical_data[-1].income_statement.get('net_income', 0) / (fs.historical_data[-1].shares_outstanding or 1)

        if previous_eps == 0:
            return None

        return ((current_eps - previous_eps) / previous_eps) * 100

    def _generate_insights(self, metrics: ProfitabilityMetrics, fs: FinancialStatements) -> List[Dict[str, Any]]:
        """Generate insights based on profitability metrics"""
        insights = []

        # Net Profit Margin Analysis
        if metrics.net_profit_margin < 0:
            insights.append({
                "type": "alert",
                "title_ar": "خسائر صافية",
                "title_en": "Net Losses",
                "description_ar": f"هامش الربح الصافي سالب {metrics.net_profit_margin:.2f}% يشير إلى خسائر",
                "description_en": f"Negative net profit margin of {metrics.net_profit_margin:.2f}% indicates losses",
                "impact": "high",
                "metric": "net_profit_margin",
                "value": metrics.net_profit_margin
            })
        elif metrics.net_profit_margin < 5:
            insights.append({
                "type": "warning",
                "title_ar": "هامش ربح منخفض",
                "title_en": "Low Profit Margin",
                "description_ar": f"هامش الربح الصافي {metrics.net_profit_margin:.2f}% أقل من المتوسط",
                "description_en": f"Net profit margin of {metrics.net_profit_margin:.2f}% is below average",
                "impact": "medium",
                "metric": "net_profit_margin",
                "value": metrics.net_profit_margin
            })
        elif metrics.net_profit_margin > 15:
            insights.append({
                "type": "positive",
                "title_ar": "هامش ربح ممتاز",
                "title_en": "Excellent Profit Margin",
                "description_ar": f"هامش الربح الصافي {metrics.net_profit_margin:.2f}% ممتاز",
                "description_en": f"Net profit margin of {metrics.net_profit_margin:.2f}% is excellent",
                "impact": "positive",
                "metric": "net_profit_margin",
                "value": metrics.net_profit_margin
            })

        # ROE Analysis
        if metrics.return_on_equity < 5:
            insights.append({
                "type": "warning",
                "title_ar": "عائد منخفض على حقوق الملكية",
                "title_en": "Low Return on Equity",
                "description_ar": f"عائد حقوق الملكية {metrics.return_on_equity:.2f}% منخفض",
                "description_en": f"Return on equity of {metrics.return_on_equity:.2f}% is low",
                "impact": "medium",
                "metric": "return_on_equity",
                "value": metrics.return_on_equity
            })
        elif metrics.return_on_equity > 20:
            insights.append({
                "type": "positive",
                "title_ar": "عائد ممتاز على حقوق الملكية",
                "title_en": "Excellent Return on Equity",
                "description_ar": f"عائد حقوق الملكية {metrics.return_on_equity:.2f}% ممتاز",
                "description_en": f"Return on equity of {metrics.return_on_equity:.2f}% is excellent",
                "impact": "positive",
                "metric": "return_on_equity",
                "value": metrics.return_on_equity
            })

        # Growth Analysis
        if metrics.revenue_growth is not None:
            if metrics.revenue_growth < -10:
                insights.append({
                    "type": "alert",
                    "title_ar": "تراجع الإيرادات",
                    "title_en": "Revenue Decline",
                    "description_ar": f"انخفاض الإيرادات بنسبة {abs(metrics.revenue_growth):.1f}%",
                    "description_en": f"Revenue declined by {abs(metrics.revenue_growth):.1f}%",
                    "impact": "high",
                    "metric": "revenue_growth",
                    "value": metrics.revenue_growth
                })
            elif metrics.revenue_growth > 20:
                insights.append({
                    "type": "positive",
                    "title_ar": "نمو قوي في الإيرادات",
                    "title_en": "Strong Revenue Growth",
                    "description_ar": f"نمو الإيرادات بنسبة {metrics.revenue_growth:.1f}%",
                    "description_en": f"Revenue grew by {metrics.revenue_growth:.1f}%",
                    "impact": "positive",
                    "metric": "revenue_growth",
                    "value": metrics.revenue_growth
                })

        # Earnings Quality Analysis
        if metrics.earnings_quality_score < 60:
            insights.append({
                "type": "warning",
                "title_ar": "جودة أرباح منخفضة",
                "title_en": "Low Earnings Quality",
                "description_ar": f"جودة الأرباح {metrics.earnings_quality_score:.0f}% تحتاج تحسين",
                "description_en": f"Earnings quality of {metrics.earnings_quality_score:.0f}% needs improvement",
                "impact": "medium",
                "metric": "earnings_quality_score",
                "value": metrics.earnings_quality_score
            })

        # Interest Coverage Analysis
        if metrics.interest_coverage_ratio < 2.5:
            insights.append({
                "type": "alert",
                "title_ar": "قدرة منخفضة على تغطية الفوائد",
                "title_en": "Low Interest Coverage",
                "description_ar": f"نسبة تغطية الفوائد {metrics.interest_coverage_ratio:.1f} منخفضة",
                "description_en": f"Interest coverage ratio of {metrics.interest_coverage_ratio:.1f} is low",
                "impact": "high",
                "metric": "interest_coverage_ratio",
                "value": metrics.interest_coverage_ratio
            })

        return insights

    def _compare_with_benchmarks(self, metrics: ProfitabilityMetrics, sector: str,
                                comparison_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Compare profitability metrics with industry benchmarks"""
        # Industry benchmark ranges
        benchmarks = {
            "manufacturing": {
                "net_profit_margin": {"min": 3, "max": 8, "optimal": 6},
                "return_on_equity": {"min": 8, "max": 15, "optimal": 12},
                "return_on_assets": {"min": 3, "max": 8, "optimal": 5},
                "gross_profit_margin": {"min": 20, "max": 40, "optimal": 30}
            },
            "retail": {
                "net_profit_margin": {"min": 2, "max": 6, "optimal": 4},
                "return_on_equity": {"min": 10, "max": 20, "optimal": 15},
                "return_on_assets": {"min": 4, "max": 10, "optimal": 7},
                "gross_profit_margin": {"min": 25, "max": 50, "optimal": 35}
            },
            "technology": {
                "net_profit_margin": {"min": 8, "max": 25, "optimal": 15},
                "return_on_equity": {"min": 15, "max": 30, "optimal": 20},
                "return_on_assets": {"min": 8, "max": 20, "optimal": 12},
                "gross_profit_margin": {"min": 60, "max": 85, "optimal": 70}
            },
            "default": {
                "net_profit_margin": {"min": 4, "max": 10, "optimal": 7},
                "return_on_equity": {"min": 10, "max": 18, "optimal": 14},
                "return_on_assets": {"min": 4, "max": 8, "optimal": 6},
                "gross_profit_margin": {"min": 25, "max": 45, "optimal": 35}
            }
        }

        sector_benchmarks = benchmarks.get(sector.lower(), benchmarks["default"])
        comparison = {}

        for metric in ["net_profit_margin", "return_on_equity", "return_on_assets", "gross_profit_margin"]:
            metric_value = getattr(metrics, metric)
            benchmark = sector_benchmarks[metric]

            comparison[metric] = {
                "value": metric_value,
                "benchmark_min": benchmark["min"],
                "benchmark_max": benchmark["max"],
                "benchmark_optimal": benchmark["optimal"],
                "performance": self._calculate_performance_score(
                    metric_value, benchmark["min"], benchmark["max"], benchmark["optimal"]
                )
            }

        return comparison

    def _calculate_performance_score(self, value: float, min_val: float, max_val: float, optimal: float) -> str:
        """Calculate performance score"""
        if value >= optimal:
            return "excellent" if value <= max_val else "above_optimal"
        elif value >= min_val:
            return "good"
        else:
            return "poor"

    def _assess_performance(self, metrics: ProfitabilityMetrics) -> Dict[str, Any]:
        """Assess overall profitability performance"""
        performance_factors = []
        scores = []

        # Net Profit Margin Performance
        if metrics.net_profit_margin > 10:
            performance_factors.append("excellent_margins")
            scores.append(9)
        elif metrics.net_profit_margin > 5:
            performance_factors.append("good_margins")
            scores.append(7)
        elif metrics.net_profit_margin > 0:
            performance_factors.append("acceptable_margins")
            scores.append(5)
        else:
            performance_factors.append("negative_margins")
            scores.append(2)

        # ROE Performance
        if metrics.return_on_equity > 15:
            performance_factors.append("excellent_roe")
            scores.append(9)
        elif metrics.return_on_equity > 8:
            performance_factors.append("good_roe")
            scores.append(7)
        elif metrics.return_on_equity > 0:
            performance_factors.append("acceptable_roe")
            scores.append(5)
        else:
            performance_factors.append("negative_roe")
            scores.append(2)

        # Growth Performance
        if metrics.revenue_growth is not None:
            if metrics.revenue_growth > 15:
                performance_factors.append("strong_growth")
                scores.append(8)
            elif metrics.revenue_growth > 5:
                performance_factors.append("moderate_growth")
                scores.append(6)
            elif metrics.revenue_growth > 0:
                performance_factors.append("slow_growth")
                scores.append(4)
            else:
                performance_factors.append("declining_revenue")
                scores.append(2)

        # Calculate overall performance
        avg_score = np.mean(scores) if scores else 5
        if avg_score >= 8:
            overall_performance = "excellent"
        elif avg_score >= 6:
            overall_performance = "good"
        elif avg_score >= 4:
            overall_performance = "acceptable"
        else:
            overall_performance = "poor"

        return {
            "overall_performance": overall_performance,
            "performance_factors": performance_factors,
            "performance_score": avg_score
        }

    def _analyze_trends(self, fs: FinancialStatements) -> Dict[str, Any]:
        """Analyze profitability trends"""
        if not fs.historical_data or len(fs.historical_data) < 2:
            return {"trend_available": False}

        trends = {}

        # Calculate historical metrics
        historical_metrics = []
        for historical_fs in fs.historical_data:
            metrics = self._calculate_profitability_metrics(historical_fs)
            historical_metrics.append(metrics)

        # Margin trends
        net_margins = [m.net_profit_margin for m in historical_metrics]
        trends["net_margin_trend"] = self._calculate_trend(net_margins)

        gross_margins = [m.gross_profit_margin for m in historical_metrics]
        trends["gross_margin_trend"] = self._calculate_trend(gross_margins)

        # Return trends
        roe_values = [m.return_on_equity for m in historical_metrics]
        trends["roe_trend"] = self._calculate_trend(roe_values)

        roa_values = [m.return_on_assets for m in historical_metrics]
        trends["roa_trend"] = self._calculate_trend(roa_values)

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

        if abs(slope) < 0.1:
            direction = "stable"
            strength = 0
        elif slope > 0:
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

    def _generate_recommendations(self, metrics: ProfitabilityMetrics, performance: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []

        # Margin Improvement Recommendations
        if metrics.net_profit_margin < 5:
            recommendations.append({
                "priority": "high",
                "category": "margin_improvement",
                "title_ar": "تحسين هوامش الربح",
                "title_en": "Improve Profit Margins",
                "description_ar": "تحسين الربحية من خلال تحسين الهوامش وخفض التكاليف",
                "description_en": "Improve profitability through margin enhancement and cost reduction",
                "actions_ar": [
                    "مراجعة استراتيجية التسعير",
                    "تحسين كفاءة العمليات",
                    "خفض التكاليف غير الضرورية",
                    "تحسين مزيج المنتجات"
                ],
                "actions_en": [
                    "Review pricing strategy",
                    "Improve operational efficiency",
                    "Reduce unnecessary costs",
                    "Optimize product mix"
                ],
                "expected_impact": "high",
                "timeframe": "medium_term"
            })

        # ROE Improvement Recommendations
        if metrics.return_on_equity < 10:
            recommendations.append({
                "priority": "medium",
                "category": "roe_improvement",
                "title_ar": "تحسين عائد حقوق الملكية",
                "title_en": "Improve Return on Equity",
                "description_ar": "زيادة كفاءة استخدام رأس المال",
                "description_en": "Increase capital utilization efficiency",
                "actions_ar": [
                    "تحسين الربحية التشغيلية",
                    "تحسين معدل دوران الأصول",
                    "مراجعة هيكل رأس المال",
                    "توزيع الأرباح المحتجزة بكفاءة"
                ],
                "actions_en": [
                    "Improve operating profitability",
                    "Enhance asset turnover",
                    "Review capital structure",
                    "Efficiently deploy retained earnings"
                ],
                "expected_impact": "medium",
                "timeframe": "medium_term"
            })

        # Growth Recommendations
        if metrics.revenue_growth is not None and metrics.revenue_growth < 5:
            recommendations.append({
                "priority": "medium",
                "category": "growth_enhancement",
                "title_ar": "تسريع النمو",
                "title_en": "Accelerate Growth",
                "description_ar": "تطوير استراتيجيات النمو وزيادة الإيرادات",
                "description_en": "Develop growth strategies and increase revenue",
                "actions_ar": [
                    "تطوير منتجات جديدة",
                    "توسيع قاعدة العملاء",
                    "دخول أسواق جديدة",
                    "تحسين التسويق والمبيعات"
                ],
                "actions_en": [
                    "Develop new products",
                    "Expand customer base",
                    "Enter new markets",
                    "Improve marketing and sales"
                ],
                "expected_impact": "high",
                "timeframe": "long_term"
            })

        return recommendations

    def _prepare_charts_data(self, metrics: ProfitabilityMetrics, fs: FinancialStatements) -> Dict[str, Any]:
        """Prepare data for charts and visualizations"""
        return {
            "margin_analysis": {
                "type": "bar_chart",
                "title_ar": "تحليل الهوامش",
                "title_en": "Margin Analysis",
                "data": {
                    "labels_ar": ["هامش إجمالي", "هامش تشغيلي", "هامش EBITDA", "هامش صافي"],
                    "labels_en": ["Gross Margin", "Operating Margin", "EBITDA Margin", "Net Margin"],
                    "values": [
                        metrics.gross_profit_margin,
                        metrics.operating_profit_margin,
                        metrics.ebitda_margin,
                        metrics.net_profit_margin
                    ]
                }
            },
            "return_ratios": {
                "type": "radar_chart",
                "title_ar": "نسب العائد",
                "title_en": "Return Ratios",
                "data": {
                    "labels_ar": ["عائد الأصول", "عائد حقوق الملكية", "عائد رأس المال المستثمر"],
                    "labels_en": ["ROA", "ROE", "ROIC"],
                    "values": [
                        metrics.return_on_assets,
                        metrics.return_on_equity,
                        metrics.return_on_invested_capital
                    ],
                    "benchmarks": [6, 14, 10]  # Industry benchmarks
                }
            },
            "profitability_breakdown": {
                "type": "waterfall_chart",
                "title_ar": "تفكيك الربحية",
                "title_en": "Profitability Breakdown",
                "data": {
                    "revenue": fs.income_statement.get('revenue', 0),
                    "gross_profit": fs.income_statement.get('gross_profit', 0),
                    "operating_income": fs.income_statement.get('operating_income', 0),
                    "net_income": fs.income_statement.get('net_income', 0)
                }
            }
        }