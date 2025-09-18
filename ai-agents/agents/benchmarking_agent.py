"""
Benchmarking Agent
وكيل المقارنات المعيارية

This agent specializes in financial benchmarking analysis, comparing financial
performance against industry standards, peer groups, and market indices.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class BenchmarkType(Enum):
    """Types of benchmarking analysis"""
    PEER_COMPARISON = "peer_comparison"
    INDUSTRY_AVERAGE = "industry_average"
    MARKET_INDEX = "market_index"
    HISTORICAL_PERFORMANCE = "historical_performance"
    BEST_IN_CLASS = "best_in_class"
    REGULATORY_MINIMUMS = "regulatory_minimums"


class BenchmarkMetric(Enum):
    """Financial metrics for benchmarking"""
    ROE = "return_on_equity"
    ROA = "return_on_assets"
    ROI = "return_on_investment"
    CAPITAL_RATIO = "capital_adequacy_ratio"
    LIQUIDITY_RATIO = "liquidity_ratio"
    EFFICIENCY_RATIO = "efficiency_ratio"
    NIM = "net_interest_margin"
    COST_INCOME_RATIO = "cost_income_ratio"
    LOAN_LOSS_RATIO = "loan_loss_ratio"
    ASSET_QUALITY = "asset_quality"


class PerformanceRating(Enum):
    """Performance rating categories"""
    EXCELLENT = "excellent"
    ABOVE_AVERAGE = "above_average"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"


@dataclass
class BenchmarkResult:
    """Represents a benchmark comparison result"""
    metric: BenchmarkMetric
    company_value: float
    benchmark_value: float
    percentile_rank: float
    performance_rating: PerformanceRating
    variance_percentage: float
    industry_context: str
    recommendations: List[str]


@dataclass
class PeerGroup:
    """Represents a peer group for comparison"""
    group_id: str
    group_name: str
    companies: List[str]
    industry_sector: str
    region: str
    asset_size_range: Tuple[float, float]
    business_model: str


class BenchmarkingAgent(FinancialAgent):
    """
    Specialized agent for financial benchmarking analysis
    وكيل متخصص في تحليل المقارنات المعيارية المالية
    """

    def __init__(self, agent_id: str = "benchmarking_agent",
                 agent_name_ar: str = "وكيل المقارنات المعيارية",
                 agent_name_en: str = "Benchmarking Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'BENCHMARKING', 'benchmarking')
        )

        # Benchmarking data and standards
        self.peer_groups = self._initialize_peer_groups()
        self.industry_benchmarks = self._initialize_industry_benchmarks()
        self.performance_thresholds = self._initialize_performance_thresholds()
        self.benchmark_data_sources = self._initialize_data_sources()

    def _initialize_capabilities(self) -> None:
        """Initialize benchmarking capabilities"""
        self.capabilities = {
            "benchmarking_types": {
                "peer_analysis": True,
                "industry_comparison": True,
                "market_benchmarking": True,
                "historical_analysis": True,
                "best_practice_identification": True
            },
            "metrics_analysis": {
                "profitability_ratios": True,
                "efficiency_metrics": True,
                "risk_indicators": True,
                "capital_metrics": True,
                "liquidity_measures": True
            },
            "statistical_analysis": {
                "percentile_ranking": True,
                "trend_analysis": True,
                "correlation_analysis": True,
                "outlier_detection": True,
                "significance_testing": True
            },
            "reporting": {
                "comparative_reports": True,
                "visual_dashboards": True,
                "performance_scorecards": True,
                "gap_analysis": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_peer_groups(self) -> Dict[str, PeerGroup]:
        """Initialize peer groups for different sectors"""
        return {
            "gcc_large_banks": PeerGroup(
                group_id="gcc_large_banks",
                group_name="البنوك الكبرى في دول مجلس التعاون الخليجي",
                companies=[
                    "الراجحي", "الأهلي السعودي", "سامبا", "الرياض",
                    "الإمارات دبي الوطني", "بنك أبوظبي الأول", "بنك الكويت الوطني"
                ],
                industry_sector="banking",
                region="gcc",
                asset_size_range=(100_000_000_000, 1_000_000_000_000),
                business_model="universal_banking"
            ),
            "saudi_banks": PeerGroup(
                group_id="saudi_banks",
                group_name="البنوك السعودية",
                companies=[
                    "الراجحي", "الأهلي السعودي", "سامبا", "الرياض",
                    "البلاد", "الجزيرة", "الإنماء", "ساب"
                ],
                industry_sector="banking",
                region="saudi_arabia",
                asset_size_range=(50_000_000_000, 800_000_000_000),
                business_model="retail_corporate_banking"
            ),
            "islamic_banks": PeerGroup(
                group_id="islamic_banks",
                group_name="البنوك الإسلامية",
                companies=[
                    "الراجحي", "الجزيرة", "الإنماء", "البلاد",
                    "بنك دبي الإسلامي", "بيت التمويل الكويتي"
                ],
                industry_sector="islamic_banking",
                region="mena",
                asset_size_range=(20_000_000_000, 600_000_000_000),
                business_model="sharia_compliant"
            ),
            "insurance_companies": PeerGroup(
                group_id="gcc_insurance",
                group_name="شركات التأمين الخليجية",
                companies=[
                    "التعاونية", "ملاذ", "الأهلية", "سلامة",
                    "الإمارات للتأمين", "قطر للتأمين"
                ],
                industry_sector="insurance",
                region="gcc",
                asset_size_range=(1_000_000_000, 50_000_000_000),
                business_model="general_insurance"
            )
        }

    def _initialize_industry_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize industry benchmark standards"""
        return {
            "banking": {
                "gcc": {
                    "return_on_equity": {"excellent": 0.15, "good": 0.12, "average": 0.10, "poor": 0.08},
                    "return_on_assets": {"excellent": 0.02, "good": 0.015, "average": 0.012, "poor": 0.01},
                    "capital_adequacy_ratio": {"excellent": 0.18, "good": 0.15, "average": 0.13, "minimum": 0.125},
                    "cost_income_ratio": {"excellent": 0.35, "good": 0.40, "average": 0.45, "poor": 0.55},
                    "net_interest_margin": {"excellent": 0.035, "good": 0.030, "average": 0.025, "poor": 0.020},
                    "loan_loss_provision": {"excellent": 0.005, "good": 0.010, "average": 0.015, "poor": 0.025}
                },
                "saudi_arabia": {
                    "return_on_equity": {"excellent": 0.16, "good": 0.13, "average": 0.11, "poor": 0.09},
                    "return_on_assets": {"excellent": 0.022, "good": 0.018, "average": 0.015, "poor": 0.012},
                    "capital_adequacy_ratio": {"excellent": 0.20, "good": 0.17, "average": 0.15, "minimum": 0.125},
                    "efficiency_ratio": {"excellent": 0.30, "good": 0.35, "average": 0.40, "poor": 0.50},
                    "liquidity_coverage_ratio": {"excellent": 1.5, "good": 1.3, "average": 1.1, "minimum": 1.0}
                }
            },
            "islamic_banking": {
                "global": {
                    "return_on_equity": {"excellent": 0.14, "good": 0.11, "average": 0.09, "poor": 0.07},
                    "return_on_assets": {"excellent": 0.018, "good": 0.014, "average": 0.011, "poor": 0.008},
                    "financing_to_deposit_ratio": {"excellent": 0.85, "good": 0.80, "average": 0.75, "poor": 0.70},
                    "sharia_compliance_ratio": {"minimum": 1.0}
                }
            },
            "insurance": {
                "gcc": {
                    "return_on_equity": {"excellent": 0.20, "good": 0.15, "average": 0.12, "poor": 0.08},
                    "combined_ratio": {"excellent": 0.85, "good": 0.90, "average": 0.95, "poor": 1.05},
                    "expense_ratio": {"excellent": 0.25, "good": 0.30, "average": 0.35, "poor": 0.45},
                    "claims_ratio": {"excellent": 0.60, "good": 0.70, "average": 0.80, "poor": 0.90}
                }
            }
        }

    def _initialize_performance_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize performance rating thresholds"""
        return {
            "percentile_thresholds": {
                "excellent": 90.0,    # Top 10%
                "above_average": 75.0, # Top 25%
                "average": 50.0,       # Median
                "below_average": 25.0, # Bottom 75%
                "poor": 0.0           # Bottom 25%
            },
            "variance_thresholds": {
                "significant_outperformance": 0.20,  # 20% above benchmark
                "moderate_outperformance": 0.10,     # 10% above benchmark
                "neutral": 0.05,                     # Within 5% of benchmark
                "moderate_underperformance": -0.10,  # 10% below benchmark
                "significant_underperformance": -0.20 # 20% below benchmark
            }
        }

    def _initialize_data_sources(self) -> Dict[str, Any]:
        """Initialize benchmark data sources"""
        return {
            "regulatory_sources": [
                "SAMA (Saudi Arabian Monetary Authority)",
                "CMA (Capital Market Authority)",
                "Central Banks of GCC countries"
            ],
            "commercial_sources": [
                "Bloomberg Terminal",
                "Refinitiv Eikon",
                "S&P Market Intelligence",
                "Moody's Analytics"
            ],
            "industry_sources": [
                "Banking associations",
                "Industry reports",
                "Credit rating agencies",
                "Financial data providers"
            ],
            "update_frequency": {
                "quarterly_financials": "quarterly",
                "annual_reports": "annual",
                "regulatory_ratios": "monthly",
                "market_data": "daily"
            }
        }

    async def perform_peer_analysis(self, company_data: Dict[str, Any],
                                  peer_group_id: str,
                                  metrics: List[BenchmarkMetric]) -> Dict[str, Any]:
        """
        Perform comprehensive peer analysis
        تنفيذ تحليل شامل للمقارنة مع الشركات المماثلة
        """
        try:
            peer_group = self.peer_groups.get(peer_group_id)
            if not peer_group:
                return {"error": f"Peer group {peer_group_id} not found"}

            analysis_results = {
                "company_name": company_data.get("company_name", "غير محدد"),
                "peer_group": peer_group.group_name,
                "analysis_date": datetime.now().isoformat(),
                "benchmark_results": [],
                "overall_ranking": {},
                "summary_insights": {},
                "recommendations": []
            }

            # Generate mock peer data (in real implementation, this would come from data sources)
            peer_data = await self._generate_peer_data(peer_group, metrics)

            # Analyze each metric
            for metric in metrics:
                company_value = company_data.get(metric.value, 0)
                benchmark_result = await self._analyze_metric_vs_peers(
                    metric, company_value, peer_data[metric.value]
                )
                analysis_results["benchmark_results"].append(benchmark_result)

            # Calculate overall performance ranking
            analysis_results["overall_ranking"] = await self._calculate_overall_ranking(
                analysis_results["benchmark_results"]
            )

            # Generate insights and recommendations
            analysis_results["summary_insights"] = await self._generate_peer_insights(
                analysis_results["benchmark_results"], peer_group
            )

            analysis_results["recommendations"] = await self._generate_peer_recommendations(
                analysis_results["benchmark_results"]
            )

            return analysis_results

        except Exception as e:
            return {"error": f"Peer analysis failed: {str(e)}"}

    async def _generate_peer_data(self, peer_group: PeerGroup,
                                metrics: List[BenchmarkMetric]) -> Dict[str, List[float]]:
        """Generate representative peer data for benchmarking"""
        peer_data = {}

        # Industry-specific base values and variations
        base_values = {
            BenchmarkMetric.ROE: 0.12,
            BenchmarkMetric.ROA: 0.015,
            BenchmarkMetric.CAPITAL_RATIO: 0.16,
            BenchmarkMetric.COST_INCOME_RATIO: 0.42,
            BenchmarkMetric.NIM: 0.028,
            BenchmarkMetric.LOAN_LOSS_RATIO: 0.012
        }

        for metric in metrics:
            base_value = base_values.get(metric, 0.1)
            # Generate realistic peer values with normal distribution
            peer_values = []
            for _ in range(len(peer_group.companies)):
                # Add realistic variation (±20% from base)
                variation = np.random.normal(0, base_value * 0.15)
                peer_value = max(0, base_value + variation)
                peer_values.append(peer_value)

            peer_data[metric.value] = peer_values

        return peer_data

    async def _analyze_metric_vs_peers(self, metric: BenchmarkMetric,
                                     company_value: float,
                                     peer_values: List[float]) -> BenchmarkResult:
        """Analyze a single metric against peer values"""

        # Calculate statistics
        peer_mean = statistics.mean(peer_values)
        peer_median = statistics.median(peer_values)
        peer_std = statistics.stdev(peer_values) if len(peer_values) > 1 else 0

        # Calculate percentile rank
        sorted_values = sorted(peer_values + [company_value])
        company_rank = sorted_values.index(company_value)
        percentile_rank = (company_rank / len(sorted_values)) * 100

        # Determine performance rating
        if percentile_rank >= 90:
            rating = PerformanceRating.EXCELLENT
        elif percentile_rank >= 75:
            rating = PerformanceRating.ABOVE_AVERAGE
        elif percentile_rank >= 25:
            rating = PerformanceRating.AVERAGE
        elif percentile_rank >= 10:
            rating = PerformanceRating.BELOW_AVERAGE
        else:
            rating = PerformanceRating.POOR

        # Calculate variance percentage
        variance_pct = ((company_value - peer_median) / peer_median) * 100 if peer_median != 0 else 0

        # Generate metric-specific context
        industry_context = await self._get_metric_context(metric, company_value, peer_mean)

        # Generate recommendations
        recommendations = await self._get_metric_recommendations(metric, rating, variance_pct)

        return BenchmarkResult(
            metric=metric,
            company_value=company_value,
            benchmark_value=peer_median,
            percentile_rank=percentile_rank,
            performance_rating=rating,
            variance_percentage=variance_pct,
            industry_context=industry_context,
            recommendations=recommendations
        )

    async def _get_metric_context(self, metric: BenchmarkMetric,
                                company_value: float, peer_average: float) -> str:
        """Get contextual information for a specific metric"""
        contexts = {
            BenchmarkMetric.ROE: {
                "ar": f"العائد على حقوق الملكية للشركة {company_value:.1%} مقابل متوسط القطاع {peer_average:.1%}",
                "en": f"Company ROE of {company_value:.1%} vs industry average of {peer_average:.1%}"
            },
            BenchmarkMetric.ROA: {
                "ar": f"العائد على الأصول {company_value:.1%} مقابل متوسط المنافسين {peer_average:.1%}",
                "en": f"Return on Assets of {company_value:.1%} vs peer average of {peer_average:.1%}"
            },
            BenchmarkMetric.CAPITAL_RATIO: {
                "ar": f"نسبة كفاية رأس المال {company_value:.1%} مقابل متوسط القطاع {peer_average:.1%}",
                "en": f"Capital adequacy ratio of {company_value:.1%} vs sector average of {peer_average:.1%}"
            },
            BenchmarkMetric.COST_INCOME_RATIO: {
                "ar": f"نسبة التكلفة إلى الدخل {company_value:.1%} مقابل متوسط الأقران {peer_average:.1%}",
                "en": f"Cost-to-income ratio of {company_value:.1%} vs peer average of {peer_average:.1%}"
            }
        }

        return contexts.get(metric, {}).get("ar", "تحليل مقارن للمؤشر المالي")

    async def _get_metric_recommendations(self, metric: BenchmarkMetric,
                                        rating: PerformanceRating,
                                        variance_pct: float) -> List[str]:
        """Generate recommendations based on metric performance"""
        recommendations = []

        if rating in [PerformanceRating.POOR, PerformanceRating.BELOW_AVERAGE]:
            if metric == BenchmarkMetric.ROE:
                recommendations.extend([
                    "تحسين كفاءة استخدام رأس المال",
                    "زيادة الربحية من خلال تنويع مصادر الدخل",
                    "مراجعة استراتيجية التسعير"
                ])
            elif metric == BenchmarkMetric.COST_INCOME_RATIO:
                recommendations.extend([
                    "تحسين الكفاءة التشغيلية",
                    "أتمتة العمليات لتقليل التكاليف",
                    "مراجعة هيكل التكاليف"
                ])
            elif metric == BenchmarkMetric.CAPITAL_RATIO:
                recommendations.extend([
                    "تعزيز قاعدة رأس المال",
                    "تحسين إدارة المخاطر",
                    "مراجعة محفظة الأصول"
                ])

        elif rating == PerformanceRating.EXCELLENT:
            recommendations.extend([
                "الحفاظ على الأداء المتميز",
                "مشاركة أفضل الممارسات مع القطاع",
                "الاستثمار في النمو المستدام"
            ])

        return recommendations

    async def _calculate_overall_ranking(self, benchmark_results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Calculate overall performance ranking across all metrics"""
        if not benchmark_results:
            return {}

        # Calculate weighted average percentile
        total_percentile = sum(result.percentile_rank for result in benchmark_results)
        average_percentile = total_percentile / len(benchmark_results)

        # Count performance ratings
        rating_counts = {}
        for result in benchmark_results:
            rating = result.performance_rating.value
            rating_counts[rating] = rating_counts.get(rating, 0) + 1

        # Determine overall rating
        if average_percentile >= 85:
            overall_rating = "متفوق"
        elif average_percentile >= 70:
            overall_rating = "جيد جداً"
        elif average_percentile >= 50:
            overall_rating = "متوسط"
        elif average_percentile >= 30:
            overall_rating = "دون المتوسط"
        else:
            overall_rating = "ضعيف"

        return {
            "overall_percentile": average_percentile,
            "overall_rating": overall_rating,
            "rating_distribution": rating_counts,
            "strengths": [r.metric.value for r in benchmark_results if r.performance_rating in
                         [PerformanceRating.EXCELLENT, PerformanceRating.ABOVE_AVERAGE]],
            "improvement_areas": [r.metric.value for r in benchmark_results if r.performance_rating in
                                [PerformanceRating.POOR, PerformanceRating.BELOW_AVERAGE]]
        }

    async def _generate_peer_insights(self, benchmark_results: List[BenchmarkResult],
                                    peer_group: PeerGroup) -> Dict[str, Any]:
        """Generate insights from peer analysis"""
        insights = {
            "key_insights": [],
            "competitive_position": "",
            "market_trends": [],
            "risk_assessment": ""
        }

        # Analyze competitive position
        excellent_count = sum(1 for r in benchmark_results
                            if r.performance_rating == PerformanceRating.EXCELLENT)
        poor_count = sum(1 for r in benchmark_results
                        if r.performance_rating == PerformanceRating.POOR)

        if excellent_count >= len(benchmark_results) * 0.6:
            insights["competitive_position"] = "موقع تنافسي قوي في معظم المؤشرات"
        elif poor_count >= len(benchmark_results) * 0.4:
            insights["competitive_position"] = "يحتاج تحسين كبير في عدة مؤشرات رئيسية"
        else:
            insights["competitive_position"] = "أداء متوازن مع فرص للتحسين"

        # Generate key insights
        insights["key_insights"] = [
            f"تحليل مقارن مع {len(peer_group.companies)} شركة في قطاع {peer_group.industry_sector}",
            f"الأداء العام في المرتبة المئوية {sum(r.percentile_rank for r in benchmark_results) / len(benchmark_results):.0f}",
            f"نقاط القوة: {len([r for r in benchmark_results if r.performance_rating == PerformanceRating.EXCELLENT])} مؤشرات متفوقة",
            f"مجالات التحسين: {len([r for r in benchmark_results if r.performance_rating == PerformanceRating.POOR])} مؤشرات تحتاج تطوير"
        ]

        return insights

    async def _generate_peer_recommendations(self, benchmark_results: List[BenchmarkResult]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations based on peer analysis"""
        recommendations = []

        # High priority recommendations for poor performing metrics
        poor_metrics = [r for r in benchmark_results if r.performance_rating == PerformanceRating.POOR]
        if poor_metrics:
            recommendations.append({
                "priority": "high",
                "category": "immediate_improvements",
                "title": "تحسينات فورية مطلوبة",
                "description": "معالجة المؤشرات ذات الأداء الضعيف",
                "actions": [rec for metric in poor_metrics for rec in metric.recommendations]
            })

        # Medium priority for average metrics
        average_metrics = [r for r in benchmark_results if r.performance_rating == PerformanceRating.AVERAGE]
        if average_metrics:
            recommendations.append({
                "priority": "medium",
                "category": "performance_enhancement",
                "title": "تعزيز الأداء",
                "description": "رفع مستوى المؤشرات المتوسطة",
                "actions": [rec for metric in average_metrics for rec in metric.recommendations]
            })

        # Maintain excellence for top performers
        excellent_metrics = [r for r in benchmark_results if r.performance_rating == PerformanceRating.EXCELLENT]
        if excellent_metrics:
            recommendations.append({
                "priority": "low",
                "category": "maintain_excellence",
                "title": "المحافظة على التفوق",
                "description": "استمرار الأداء المتميز",
                "actions": ["الحفاظ على أفضل الممارسات", "مشاركة الخبرات", "الاستثمار في التطوير المستمر"]
            })

        return recommendations

    async def generate_industry_benchmark_report(self, company_data: Dict[str, Any],
                                               industry: str, region: str = "gcc") -> Dict[str, Any]:
        """
        Generate comprehensive industry benchmark report
        إنشاء تقرير شامل للمقارنات المعيارية القطاعية
        """
        try:
            benchmarks = self.industry_benchmarks.get(industry, {}).get(region, {})
            if not benchmarks:
                return {"error": f"No benchmarks available for {industry} in {region}"}

            report = {
                "report_title": f"تقرير المقارنة المعيارية - {industry}",
                "industry": industry,
                "region": region,
                "report_date": datetime.now().isoformat(),
                "company_performance": {},
                "industry_standards": benchmarks,
                "gap_analysis": {},
                "recommendations": [],
                "action_plan": {}
            }

            # Analyze each benchmark metric
            for metric, thresholds in benchmarks.items():
                company_value = company_data.get(metric, 0)

                # Determine performance level
                if company_value >= thresholds.get("excellent", float('inf')):
                    level = "excellent"
                elif company_value >= thresholds.get("good", float('inf')):
                    level = "good"
                elif company_value >= thresholds.get("average", float('inf')):
                    level = "average"
                else:
                    level = "below_average"

                report["company_performance"][metric] = {
                    "value": company_value,
                    "performance_level": level,
                    "benchmark_excellent": thresholds.get("excellent"),
                    "benchmark_good": thresholds.get("good"),
                    "benchmark_average": thresholds.get("average"),
                    "gap_to_excellent": thresholds.get("excellent", 0) - company_value
                }

            # Generate gap analysis
            report["gap_analysis"] = await self._generate_gap_analysis(report["company_performance"])

            # Generate recommendations
            report["recommendations"] = await self._generate_industry_recommendations(
                report["company_performance"], industry
            )

            return report

        except Exception as e:
            return {"error": f"Industry benchmark report generation failed: {str(e)}"}

    async def _generate_gap_analysis(self, company_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Generate gap analysis against industry standards"""
        gap_analysis = {
            "critical_gaps": [],
            "moderate_gaps": [],
            "strengths": [],
            "overall_assessment": ""
        }

        for metric, performance in company_performance.items():
            gap = performance.get("gap_to_excellent", 0)
            level = performance.get("performance_level", "")

            if level == "below_average" and gap > 0:
                gap_analysis["critical_gaps"].append({
                    "metric": metric,
                    "gap": gap,
                    "current_level": level
                })
            elif level in ["average", "good"] and gap > 0:
                gap_analysis["moderate_gaps"].append({
                    "metric": metric,
                    "gap": gap,
                    "current_level": level
                })
            elif level == "excellent":
                gap_analysis["strengths"].append({
                    "metric": metric,
                    "performance_level": level
                })

        # Overall assessment
        if len(gap_analysis["critical_gaps"]) > 3:
            gap_analysis["overall_assessment"] = "يتطلب تحسين كبير في عدة مجالات أساسية"
        elif len(gap_analysis["moderate_gaps"]) > 2:
            gap_analysis["overall_assessment"] = "أداء جيد مع فرص للتحسين"
        else:
            gap_analysis["overall_assessment"] = "أداء قوي مع تفوق في معظم المجالات"

        return gap_analysis

    async def _generate_industry_recommendations(self, company_performance: Dict[str, Any],
                                               industry: str) -> List[Dict[str, Any]]:
        """Generate industry-specific recommendations"""
        recommendations = []

        # Industry-specific improvement strategies
        if industry == "banking":
            recommendations.extend([
                {
                    "category": "profitability",
                    "title": "تحسين الربحية",
                    "actions": [
                        "تنويع مصادر الدخل غير التمويلية",
                        "تحسين هوامش الفوائد",
                        "زيادة كفاءة إدارة الأصول"
                    ]
                },
                {
                    "category": "efficiency",
                    "title": "تعزيز الكفاءة التشغيلية",
                    "actions": [
                        "أتمتة العمليات المصرفية",
                        "تطوير الخدمات الرقمية",
                        "تحسين إدارة التكاليف"
                    ]
                }
            ])

        return recommendations

    async def track_performance_trends(self, historical_data: List[Dict[str, Any]],
                                     metrics: List[BenchmarkMetric]) -> Dict[str, Any]:
        """
        Track performance trends over time
        تتبع اتجاهات الأداء عبر الزمن
        """
        try:
            trends_analysis = {
                "trend_summary": {},
                "metric_trends": {},
                "forecast": {},
                "trend_alerts": []
            }

            for metric in metrics:
                metric_values = []
                dates = []

                for data_point in historical_data:
                    if metric.value in data_point:
                        metric_values.append(data_point[metric.value])
                        dates.append(data_point.get("date", datetime.now()))

                if len(metric_values) >= 2:
                    trend_analysis = await self._analyze_metric_trend(metric, metric_values, dates)
                    trends_analysis["metric_trends"][metric.value] = trend_analysis

            # Generate overall trend summary
            trends_analysis["trend_summary"] = await self._generate_trend_summary(
                trends_analysis["metric_trends"]
            )

            return trends_analysis

        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}

    async def _analyze_metric_trend(self, metric: BenchmarkMetric,
                                  values: List[float], dates: List[datetime]) -> Dict[str, Any]:
        """Analyze trend for a specific metric"""

        # Calculate trend direction and strength
        if len(values) < 2:
            return {"error": "Insufficient data for trend analysis"}

        # Simple trend calculation
        recent_avg = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
        earlier_avg = statistics.mean(values[:3]) if len(values) >= 3 else values[0]

        trend_direction = "improving" if recent_avg > earlier_avg else "declining"
        trend_strength = abs((recent_avg - earlier_avg) / earlier_avg) if earlier_avg != 0 else 0

        return {
            "metric": metric.value,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "current_value": values[-1],
            "period_change": recent_avg - earlier_avg,
            "volatility": statistics.stdev(values) if len(values) > 1 else 0
        }

    async def _generate_trend_summary(self, metric_trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall trend summary"""
        improving_metrics = [m for m, t in metric_trends.items()
                           if t.get("trend_direction") == "improving"]
        declining_metrics = [m for m, t in metric_trends.items()
                           if t.get("trend_direction") == "declining"]

        return {
            "improving_metrics_count": len(improving_metrics),
            "declining_metrics_count": len(declining_metrics),
            "overall_trend": "positive" if len(improving_metrics) > len(declining_metrics) else "negative",
            "key_improvements": improving_metrics[:3],
            "areas_of_concern": declining_metrics[:3]
        }

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process benchmarking-related tasks"""
        try:
            task_type = task.task_data.get("type", "peer_analysis")

            if task_type == "peer_analysis":
                company_data = task.task_data.get("company_data", {})
                peer_group_id = task.task_data.get("peer_group_id", "")
                metrics = [BenchmarkMetric(m) for m in task.task_data.get("metrics", [])]
                return await self.perform_peer_analysis(company_data, peer_group_id, metrics)

            elif task_type == "industry_benchmark":
                company_data = task.task_data.get("company_data", {})
                industry = task.task_data.get("industry", "banking")
                region = task.task_data.get("region", "gcc")
                return await self.generate_industry_benchmark_report(company_data, industry, region)

            elif task_type == "trend_analysis":
                historical_data = task.task_data.get("historical_data", [])
                metrics = [BenchmarkMetric(m) for m in task.task_data.get("metrics", [])]
                return await self.track_performance_trends(historical_data, metrics)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}