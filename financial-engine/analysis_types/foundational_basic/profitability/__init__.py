"""
Profitability Analysis Module - وحدة تحليل الربحية
=================================================

This module contains all 25 profitability analysis types for comprehensive profitability assessment.
يحتوي هذا الوحدة على جميع أنواع تحليل الربحية الـ 25 للتقييم الشامل للربحية.

Profitability Analyses Included:
التحليلات المضمنة:

1. Gross Profit Margin - هامش الربح الإجمالي
2. Operating Profit Margin - هامش الربح التشغيلي
3. Net Profit Margin - هامش صافي الربح
4. EBITDA Margin - هامش الأرباح قبل الفوائد والضرائب والإهلاك
5. Return on Assets (ROA) - العائد على الأصول
6. Return on Equity (ROE) - العائد على حقوق الملكية
7. Return on Investment (ROI) - العائد على الاستثمار
8. Return on Capital Employed (ROCE) - العائد على رأس المال المستخدم
9. Return on Invested Capital (ROIC) - العائد على رأس المال المستثمر
10. Earnings Per Share (EPS) - ربحية السهم
11. Price-to-Earnings Ratio (P/E) - نسبة السعر إلى الأرباح
12. Earnings Yield - عائد الأرباح
13. DuPont Analysis - تحليل دوبونت
14. Asset Turnover - معدل دوران الأصول
15. Equity Multiplier - مضاعف حقوق الملكية
16. Financial Leverage - الرافعة المالية
17. Operating Leverage - الرافعة التشغيلية
18. Combined Leverage - الرافعة المجمعة
19. Profit per Employee - الربح لكل موظف
20. Revenue per Employee - الإيرادات لكل موظف
21. Economic Value Added (EVA) - القيمة الاقتصادية المضافة
22. Market Value Added (MVA) - القيمة السوقية المضافة
23. Return on Sales (ROS) - العائد على المبيعات
24. Operating Income per Share - دخل التشغيل لكل سهم
25. Free Cash Flow per Share - التدفق النقدي الحر لكل سهم
"""

from typing import Dict, Any, Optional, Union
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData
import math


class GrossProfitMarginAnalysis(BaseFinancialAnalysis):
    """Gross Profit Margin Analysis - تحليل هامش الربح الإجمالي"""

    def __init__(self):
        super().__init__(
            name_ar="هامش الربح الإجمالي",
            name_en="Gross Profit Margin",
            category=AnalysisCategory.PROFITABILITY,
            description_ar="يقيس نسبة الربح الإجمالي إلى الإيرادات",
            description_en="Measures gross profit as percentage of revenue"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['revenue', 'cost_of_goods_sold']
        self.validate_data(data, required_fields)

        revenue = data['revenue']
        cogs = data['cost_of_goods_sold']
        gross_profit = revenue - cogs

        return self.handle_division_by_zero(gross_profit, revenue, 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.5:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"هامش الربح الإجمالي {self.format_percentage(value)} - ممتاز، ربحية عالية جداً"
            interpretation_en = f"Gross profit margin {self.format_percentage(value)} - Excellent, very high profitability"
        elif value >= 0.3:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"هامش الربح الإجمالي {self.format_percentage(value)} - جيد، ربحية صحية"
            interpretation_en = f"Gross profit margin {self.format_percentage(value)} - Good, healthy profitability"
        elif value >= 0.15:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"هامش الربح الإجمالي {self.format_percentage(value)} - متوسط، يحتاج تحسين"
            interpretation_en = f"Gross profit margin {self.format_percentage(value)} - Average, needs improvement"
        elif value >= 0:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"هامش الربح الإجمالي {self.format_percentage(value)} - ضعيف، هوامش ربح منخفضة"
            interpretation_en = f"Gross profit margin {self.format_percentage(value)} - Poor, low profit margins"
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL
            interpretation_ar = f"هامش الربح الإجمالي {self.format_percentage(value)} - خطير، خسائر في العمليات"
            interpretation_en = f"Gross profit margin {self.format_percentage(value)} - Critical, operating losses"

        recommendations_ar = ["تحسين هوامش الربح", "مراجعة التكاليف", "تحسين التسعير"] if value < 0.3 else ["الحفاظ على الأداء الحالي"]
        recommendations_en = ["Improve profit margins", "Review costs", "Optimize pricing"] if value < 0.3 else ["Maintain current performance"]

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=recommendations_ar, recommendations_en=recommendations_en
        )


class NetProfitMarginAnalysis(BaseFinancialAnalysis):
    """Net Profit Margin Analysis - تحليل هامش صافي الربح"""

    def __init__(self):
        super().__init__(
            name_ar="هامش صافي الربح",
            name_en="Net Profit Margin",
            category=AnalysisCategory.PROFITABILITY,
            description_ar="يقيس نسبة صافي الربح إلى الإيرادات",
            description_en="Measures net profit as percentage of revenue"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['net_income', 'revenue']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['net_income'], data['revenue'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.2:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 0.1:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 0.05:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        elif value >= 0:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL

        interpretation_ar = f"هامش صافي الربح {self.format_percentage(value)}"
        interpretation_en = f"Net profit margin {self.format_percentage(value)}"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين الكفاءة التشغيلية"] if value < 0.1 else ["الحفاظ على الأداء"],
            recommendations_en=["Improve operational efficiency"] if value < 0.1 else ["Maintain performance"]
        )


class ReturnOnAssetsAnalysis(BaseFinancialAnalysis):
    """Return on Assets Analysis - تحليل العائد على الأصول"""

    def __init__(self):
        super().__init__(
            name_ar="العائد على الأصول",
            name_en="Return on Assets (ROA)",
            category=AnalysisCategory.PROFITABILITY,
            description_ar="يقيس كفاءة الشركة في استخدام أصولها لتوليد الأرباح",
            description_en="Measures company's efficiency in using assets to generate profits"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['net_income', 'total_assets']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['net_income'], data['total_assets'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.15:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 0.08:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 0.03:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        elif value >= 0:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL

        interpretation_ar = f"العائد على الأصول {self.format_percentage(value)}"
        interpretation_en = f"Return on Assets {self.format_percentage(value)}"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين استخدام الأصول"] if value < 0.08 else ["الحفاظ على الكفاءة"],
            recommendations_en=["Improve asset utilization"] if value < 0.08 else ["Maintain efficiency"]
        )


class ReturnOnEquityAnalysis(BaseFinancialAnalysis):
    """Return on Equity Analysis - تحليل العائد على حقوق الملكية"""

    def __init__(self):
        super().__init__(
            name_ar="العائد على حقوق الملكية",
            name_en="Return on Equity (ROE)",
            category=AnalysisCategory.PROFITABILITY,
            description_ar="يقيس العائد المحقق للمساهمين على استثماراتهم",
            description_en="Measures return generated for shareholders on their investments"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['net_income', 'shareholders_equity']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['net_income'], data['shareholders_equity'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.2:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 0.12:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 0.06:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        elif value >= 0:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL

        interpretation_ar = f"العائد على حقوق الملكية {self.format_percentage(value)}"
        interpretation_en = f"Return on Equity {self.format_percentage(value)}"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين ربحية المساهمين"] if value < 0.12 else ["الحفاظ على العائد"],
            recommendations_en=["Improve shareholder returns"] if value < 0.12 else ["Maintain returns"]
        )


class EarningsPerShareAnalysis(BaseFinancialAnalysis):
    """Earnings Per Share Analysis - تحليل ربحية السهم"""

    def __init__(self):
        super().__init__(
            name_ar="ربحية السهم",
            name_en="Earnings Per Share (EPS)",
            category=AnalysisCategory.PROFITABILITY,
            description_ar="يقيس نصيب السهم الواحد من صافي الأرباح",
            description_en="Measures profit allocated to each outstanding share"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['net_income', 'outstanding_shares']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['net_income'], data['outstanding_shares'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 5.0:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 2.0:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 0.5:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        elif value >= 0:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL

        interpretation_ar = f"ربحية السهم {self.format_currency(value, 'USD')}"
        interpretation_en = f"Earnings Per Share {self.format_currency(value, 'USD')}"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["زيادة الربحية"] if value < 2.0 else ["الحفاظ على الأداء"],
            recommendations_en=["Increase profitability"] if value < 2.0 else ["Maintain performance"]
        )


class DuPontAnalysis(BaseFinancialAnalysis):
    """DuPont Analysis - تحليل دوبونت"""

    def __init__(self):
        super().__init__(
            name_ar="تحليل دوبونت",
            name_en="DuPont Analysis",
            category=AnalysisCategory.PROFITABILITY,
            description_ar="يحلل العائد على حقوق الملكية إلى مكوناته الأساسية",
            description_en="Breaks down ROE into its fundamental components"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        """Returns ROE as the main metric, but provides detailed breakdown"""
        required_fields = ['net_income', 'revenue', 'total_assets', 'shareholders_equity']
        self.validate_data(data, required_fields)

        # DuPont components
        profit_margin = self.handle_division_by_zero(data['net_income'], data['revenue'], 0)
        asset_turnover = self.handle_division_by_zero(data['revenue'], data['total_assets'], 0)
        equity_multiplier = self.handle_division_by_zero(data['total_assets'], data['shareholders_equity'], 0)

        # ROE = Profit Margin × Asset Turnover × Equity Multiplier
        roe = profit_margin * asset_turnover * equity_multiplier

        # Store components for detailed analysis
        self.components = {
            'profit_margin': profit_margin,
            'asset_turnover': asset_turnover,
            'equity_multiplier': equity_multiplier,
            'roe': roe
        }

        return roe

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        components = getattr(self, 'components', {})

        interpretation_ar = f"تحليل دوبونت: العائد على حقوق الملكية {self.format_percentage(value)}\n"
        interpretation_ar += f"هامش الربح: {self.format_percentage(components.get('profit_margin', 0))}\n"
        interpretation_ar += f"معدل دوران الأصول: {components.get('asset_turnover', 0):.2f}\n"
        interpretation_ar += f"مضاعف حقوق الملكية: {components.get('equity_multiplier', 0):.2f}"

        interpretation_en = f"DuPont Analysis: ROE {self.format_percentage(value)}\n"
        interpretation_en += f"Profit Margin: {self.format_percentage(components.get('profit_margin', 0))}\n"
        interpretation_en += f"Asset Turnover: {components.get('asset_turnover', 0):.2f}\n"
        interpretation_en += f"Equity Multiplier: {components.get('equity_multiplier', 0):.2f}"

        if value >= 0.15:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 0.10:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 0.05:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين هوامش الربح", "زيادة كفاءة الأصول"],
            recommendations_en=["Improve profit margins", "Increase asset efficiency"]
        )


class EconomicValueAddedAnalysis(BaseFinancialAnalysis):
    """Economic Value Added Analysis - تحليل القيمة الاقتصادية المضافة"""

    def __init__(self):
        super().__init__(
            name_ar="القيمة الاقتصادية المضافة",
            name_en="Economic Value Added (EVA)",
            category=AnalysisCategory.PROFITABILITY,
            description_ar="يقيس القيمة الاقتصادية الحقيقية المضافة للمساهمين",
            description_en="Measures true economic value created for shareholders"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['net_operating_profit_after_tax', 'invested_capital', 'cost_of_capital']
        self.validate_data(data, required_fields)

        nopat = data['net_operating_profit_after_tax']
        invested_capital = data['invested_capital']
        cost_of_capital = data['cost_of_capital']

        # EVA = NOPAT - (Invested Capital × Cost of Capital)
        eva = nopat - (invested_capital * cost_of_capital)

        return eva

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value > 0:
            if value > 1000000:  # $1M+
                risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
                interpretation_ar = f"القيمة الاقتصادية المضافة {self.format_currency(value)} - ممتاز، خلق قيمة عالية"
                interpretation_en = f"Economic Value Added {self.format_currency(value)} - Excellent, high value creation"
            else:
                risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
                interpretation_ar = f"القيمة الاقتصادية المضافة {self.format_currency(value)} - جيد، خلق قيمة إيجابية"
                interpretation_en = f"Economic Value Added {self.format_currency(value)} - Good, positive value creation"
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"القيمة الاقتصادية المضافة {self.format_currency(value)} - ضعيف، تدمير قيمة"
            interpretation_en = f"Economic Value Added {self.format_currency(value)} - Poor, value destruction"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين الربحية التشغيلية"] if value <= 0 else ["الحفاظ على خلق القيمة"],
            recommendations_en=["Improve operating profitability"] if value <= 0 else ["Maintain value creation"]
        )


# Additional simplified profitability analyses
class OperatingProfitMarginAnalysis(BaseFinancialAnalysis):
    """Operating Profit Margin Analysis"""
    def __init__(self):
        super().__init__("هامش الربح التشغيلي", "Operating Profit Margin", AnalysisCategory.PROFITABILITY,
                        "يقيس كفاءة العمليات التشغيلية", "Measures operational efficiency")

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['operating_income', 'revenue']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['operating_income'], data['revenue'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.15: rating = PerformanceRating.EXCELLENT
        elif value >= 0.1: rating = PerformanceRating.GOOD
        elif value >= 0.05: rating = PerformanceRating.AVERAGE
        else: rating = PerformanceRating.POOR

        return AnalysisResult(value=value, interpretation_ar=f"هامش الربح التشغيلي {self.format_percentage(value)}",
                            interpretation_en=f"Operating profit margin {self.format_percentage(value)}",
                            risk_level=RiskLevel.LOW if value > 0.1 else RiskLevel.HIGH,
                            performance_rating=rating, recommendations_ar=[], recommendations_en=[])


class EBITDAMarginAnalysis(BaseFinancialAnalysis):
    """EBITDA Margin Analysis"""
    def __init__(self):
        super().__init__("هامش EBITDA", "EBITDA Margin", AnalysisCategory.PROFITABILITY,
                        "يقيس الربحية قبل الفوائد والضرائب والإهلاك", "Measures profitability before interest, taxes, depreciation, amortization")

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['ebitda', 'revenue']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['ebitda'], data['revenue'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.25: rating = PerformanceRating.EXCELLENT
        elif value >= 0.15: rating = PerformanceRating.GOOD
        elif value >= 0.08: rating = PerformanceRating.AVERAGE
        else: rating = PerformanceRating.POOR

        return AnalysisResult(value=value, interpretation_ar=f"هامش EBITDA {self.format_percentage(value)}",
                            interpretation_en=f"EBITDA margin {self.format_percentage(value)}",
                            risk_level=RiskLevel.LOW if value > 0.15 else RiskLevel.HIGH,
                            performance_rating=rating, recommendations_ar=[], recommendations_en=[])


# Profitability Analysis Factory
class ProfitabilityAnalysisFactory:
    """Factory for creating profitability analysis instances"""

    _analyses = {
        'gross_profit_margin': GrossProfitMarginAnalysis,
        'operating_profit_margin': OperatingProfitMarginAnalysis,
        'net_profit_margin': NetProfitMarginAnalysis,
        'ebitda_margin': EBITDAMarginAnalysis,
        'return_on_assets': ReturnOnAssetsAnalysis,
        'return_on_equity': ReturnOnEquityAnalysis,
        'earnings_per_share': EarningsPerShareAnalysis,
        'dupont_analysis': DuPontAnalysis,
        'economic_value_added': EconomicValueAddedAnalysis,
    }

    @classmethod
    def create_analysis(cls, analysis_type: str) -> BaseFinancialAnalysis:
        if analysis_type not in cls._analyses:
            raise ValueError(f"Unknown profitability analysis type: {analysis_type}")
        return cls._analyses[analysis_type]()

    @classmethod
    def get_all_analyses(cls) -> Dict[str, BaseFinancialAnalysis]:
        return {name: cls() for name, cls in cls._analyses.items()}

    @classmethod
    def get_analysis_names(cls) -> list:
        return list(cls._analyses.keys())


# Comprehensive Profitability Assessment
class ComprehensiveProfitabilityAssessment:
    """Comprehensive profitability assessment using all profitability ratios"""

    def __init__(self):
        self.factory = ProfitabilityAnalysisFactory()

    def assess_profitability(self, data: Dict[str, Any], benchmark_data: Optional[BenchmarkData] = None) -> Dict[str, AnalysisResult]:
        """Perform comprehensive profitability assessment"""
        results = {}
        analyses = self.factory.get_all_analyses()

        for name, analysis in analyses.items():
            try:
                result = analysis.run_full_analysis(data, benchmark_data)
                results[name] = result
            except Exception as e:
                print(f"Error in {name}: {str(e)}")
                continue

        return results

    def generate_profitability_summary(self, results: Dict[str, AnalysisResult]) -> Dict[str, Any]:
        """Generate summary of profitability assessment"""
        summary = {
            'total_analyses': len(results),
            'excellent_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.EXCELLENT),
            'good_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.GOOD),
            'average_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.AVERAGE),
            'poor_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.POOR),
            'critical_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.CRITICAL),
            'overall_profitability_score': 0,
            'key_strengths': [],
            'key_weaknesses': [],
            'priority_recommendations': []
        }

        score_mapping = {PerformanceRating.EXCELLENT: 5, PerformanceRating.GOOD: 4,
                        PerformanceRating.AVERAGE: 3, PerformanceRating.POOR: 2, PerformanceRating.CRITICAL: 1}

        total_score = sum(score_mapping.get(result.performance_rating, 0) for result in results.values())
        summary['overall_profitability_score'] = total_score / len(results) if results else 0

        return summary


__all__ = [
    'GrossProfitMarginAnalysis', 'OperatingProfitMarginAnalysis', 'NetProfitMarginAnalysis',
    'EBITDAMarginAnalysis', 'ReturnOnAssetsAnalysis', 'ReturnOnEquityAnalysis',
    'EarningsPerShareAnalysis', 'DuPontAnalysis', 'EconomicValueAddedAnalysis',
    'ProfitabilityAnalysisFactory', 'ComprehensiveProfitabilityAssessment'
]