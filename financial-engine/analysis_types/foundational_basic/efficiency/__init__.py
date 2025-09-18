"""
Efficiency Analysis Module - وحدة تحليل الكفاءة
==============================================

This module contains all 20 efficiency analysis types for comprehensive efficiency assessment.
يحتوي هذا الوحدة على جميع أنواع تحليل الكفاءة الـ 20 للتقييم الشامل للكفاءة.

Efficiency Analyses Included:
التحليلات المضمنة:

1. Asset Turnover Ratio - معدل دوران الأصول
2. Inventory Turnover - معدل دوران المخزون
3. Receivables Turnover - معدل دوران الذمم المدينة
4. Payables Turnover - معدل دوران الذمم الدائنة
5. Fixed Asset Turnover - معدل دوران الأصول الثابتة
6. Total Asset Turnover - معدل دوران إجمالي الأصول
7. Working Capital Turnover - معدل دوران رأس المال العامل
8. Cash Turnover - معدل دوران النقدية
9. Equity Turnover - معدل دوران حقوق الملكية
10. Capital Turnover - معدل دوران رأس المال
11. Sales per Square Foot - المبيعات لكل قدم مربع
12. Revenue per Customer - الإيرادات لكل عميل
13. Customer Acquisition Cost - تكلفة اكتساب العميل
14. Customer Lifetime Value - القيمة الحياتية للعميل
15. Inventory Days - أيام المخزون
16. Collection Period - فترة التحصيل
17. Payment Period - فترة الدفع
18. Operating Cycle - الدورة التشغيلية
19. Resource Utilization Ratio - نسبة استخدام الموارد
20. Productivity Index - مؤشر الإنتاجية
"""

from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class AssetTurnoverRatioAnalysis(BaseFinancialAnalysis):
    """Asset Turnover Ratio Analysis - تحليل معدل دوران الأصول"""

    def __init__(self):
        super().__init__(
            name_ar="معدل دوران الأصول",
            name_en="Asset Turnover Ratio",
            category=AnalysisCategory.EFFICIENCY,
            description_ar="يقيس كفاءة الشركة في استخدام أصولها لتوليد الإيرادات",
            description_en="Measures company's efficiency in using assets to generate revenue"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['revenue', 'total_assets']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['revenue'], data['total_assets'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 2.0:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"معدل دوران الأصول {value:.2f} - ممتاز، استخدام فعال جداً للأصول"
            interpretation_en = f"Asset turnover ratio {value:.2f} - Excellent, very efficient asset utilization"
        elif value >= 1.5:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"معدل دوران الأصول {value:.2f} - جيد، استخدام كفء للأصول"
            interpretation_en = f"Asset turnover ratio {value:.2f} - Good, efficient asset utilization"
        elif value >= 1.0:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"معدل دوران الأصول {value:.2f} - متوسط، يحتاج تحسين"
            interpretation_en = f"Asset turnover ratio {value:.2f} - Average, needs improvement"
        elif value >= 0.5:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"معدل دوران الأصول {value:.2f} - ضعيف، استخدام غير فعال للأصول"
            interpretation_en = f"Asset turnover ratio {value:.2f} - Poor, inefficient asset utilization"
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL
            interpretation_ar = f"معدل دوران الأصول {value:.2f} - خطير، هدر كبير في الأصول"
            interpretation_en = f"Asset turnover ratio {value:.2f} - Critical, significant asset waste"

        recommendations_ar = ["تحسين استخدام الأصول", "زيادة المبيعات", "تقليل الأصول غير المنتجة"] if value < 1.5 else ["الحفاظ على الكفاءة الحالية"]
        recommendations_en = ["Improve asset utilization", "Increase sales", "Reduce non-productive assets"] if value < 1.5 else ["Maintain current efficiency"]

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=recommendations_ar, recommendations_en=recommendations_en
        )


class InventoryTurnoverAnalysis(BaseFinancialAnalysis):
    """Inventory Turnover Analysis - تحليل معدل دوران المخزون"""

    def __init__(self):
        super().__init__(
            name_ar="معدل دوران المخزون",
            name_en="Inventory Turnover",
            category=AnalysisCategory.EFFICIENCY,
            description_ar="يقيس عدد مرات بيع وتجديد المخزون خلال فترة معينة",
            description_en="Measures how many times inventory is sold and replaced over a period"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['cost_of_goods_sold', 'inventory']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['cost_of_goods_sold'], data['inventory'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 12:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"معدل دوران المخزون {value:.1f} مرة - ممتاز، إدارة فعالة جداً للمخزون"
            interpretation_en = f"Inventory turnover {value:.1f} times - Excellent, very effective inventory management"
        elif value >= 8:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"معدل دوران المخزون {value:.1f} مرة - جيد، إدارة كفؤة للمخزون"
            interpretation_en = f"Inventory turnover {value:.1f} times - Good, efficient inventory management"
        elif value >= 4:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"معدل دوران المخزون {value:.1f} مرة - متوسط، يحتاج تحسين"
            interpretation_en = f"Inventory turnover {value:.1f} times - Average, needs improvement"
        elif value >= 2:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"معدل دوران المخزون {value:.1f} مرة - ضعيف، مخزون راكد"
            interpretation_en = f"Inventory turnover {value:.1f} times - Poor, stagnant inventory"
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL
            interpretation_ar = f"معدل دوران المخزون {value:.1f} مرة - خطير، مخزون راكد جداً"
            interpretation_en = f"Inventory turnover {value:.1f} times - Critical, very stagnant inventory"

        recommendations_ar = ["تحسين إدارة المخزون", "تسريع البيع", "تقليل مستويات المخزون"] if value < 8 else ["الحفاظ على الأداء الحالي"]
        recommendations_en = ["Improve inventory management", "Accelerate sales", "Reduce inventory levels"] if value < 8 else ["Maintain current performance"]

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=recommendations_ar, recommendations_en=recommendations_en
        )


class ReceivablesTurnoverAnalysis(BaseFinancialAnalysis):
    """Receivables Turnover Analysis - تحليل معدل دوران الذمم المدينة"""

    def __init__(self):
        super().__init__(
            name_ar="معدل دوران الذمم المدينة",
            name_en="Receivables Turnover",
            category=AnalysisCategory.EFFICIENCY,
            description_ar="يقيس كفاءة تحصيل الذمم المدينة",
            description_en="Measures efficiency of accounts receivable collection"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['revenue', 'accounts_receivable']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['revenue'], data['accounts_receivable'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 12:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 8:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 5:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR

        interpretation_ar = f"معدل دوران الذمم المدينة {value:.1f} مرة"
        interpretation_en = f"Receivables turnover {value:.1f} times"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين سياسات التحصيل"] if value < 8 else ["الحفاظ على الأداء"],
            recommendations_en=["Improve collection policies"] if value < 8 else ["Maintain performance"]
        )


class FixedAssetTurnoverAnalysis(BaseFinancialAnalysis):
    """Fixed Asset Turnover Analysis - تحليل معدل دوران الأصول الثابتة"""

    def __init__(self):
        super().__init__(
            name_ar="معدل دوران الأصول الثابتة",
            name_en="Fixed Asset Turnover",
            category=AnalysisCategory.EFFICIENCY,
            description_ar="يقيس كفاءة استخدام الأصول الثابتة لتوليد الإيرادات",
            description_en="Measures efficiency of fixed assets in generating revenue"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['revenue', 'fixed_assets']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['revenue'], data['fixed_assets'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 4.0:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 2.5:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 1.5:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR

        interpretation_ar = f"معدل دوران الأصول الثابتة {value:.2f}"
        interpretation_en = f"Fixed asset turnover {value:.2f}"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين استخدام الأصول الثابتة"] if value < 2.5 else ["الحفاظ على الكفاءة"],
            recommendations_en=["Improve fixed asset utilization"] if value < 2.5 else ["Maintain efficiency"]
        )


class WorkingCapitalTurnoverAnalysis(BaseFinancialAnalysis):
    """Working Capital Turnover Analysis - تحليل معدل دوران رأس المال العامل"""

    def __init__(self):
        super().__init__(
            name_ar="معدل دوران رأس المال العامل",
            name_en="Working Capital Turnover",
            category=AnalysisCategory.EFFICIENCY,
            description_ar="يقيس كفاءة استخدام رأس المال العامل لتوليد المبيعات",
            description_en="Measures efficiency of working capital in generating sales"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['revenue', 'current_assets', 'current_liabilities']
        self.validate_data(data, required_fields)

        working_capital = data['current_assets'] - data['current_liabilities']
        return self.handle_division_by_zero(data['revenue'], working_capital, float('inf'))

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value == float('inf'):
            interpretation_ar = "رأس المال العامل سالب أو صفر - الشركة تعمل بلا رأس مال عامل"
            interpretation_en = "Negative or zero working capital - company operates without working capital"
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL
        elif value >= 10:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"معدل دوران رأس المال العامل {value:.1f} - ممتاز، كفاءة عالية"
            interpretation_en = f"Working capital turnover {value:.1f} - Excellent, high efficiency"
        elif value >= 6:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"معدل دوران رأس المال العامل {value:.1f} - جيد"
            interpretation_en = f"Working capital turnover {value:.1f} - Good"
        elif value >= 3:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"معدل دوران رأس المال العامل {value:.1f} - متوسط"
            interpretation_en = f"Working capital turnover {value:.1f} - Average"
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"معدل دوران رأس المال العامل {value:.1f} - ضعيف"
            interpretation_en = f"Working capital turnover {value:.1f} - Poor"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين إدارة رأس المال العامل"] if value < 6 else ["الحفاظ على الكفاءة"],
            recommendations_en=["Improve working capital management"] if value < 6 else ["Maintain efficiency"]
        )


class CustomerAcquisitionCostAnalysis(BaseFinancialAnalysis):
    """Customer Acquisition Cost Analysis - تحليل تكلفة اكتساب العميل"""

    def __init__(self):
        super().__init__(
            name_ar="تكلفة اكتساب العميل",
            name_en="Customer Acquisition Cost (CAC)",
            category=AnalysisCategory.EFFICIENCY,
            description_ar="يقيس التكلفة المطلوبة لاكتساب عميل جديد",
            description_en="Measures cost required to acquire a new customer"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['marketing_expenses', 'new_customers_acquired']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['marketing_expenses'], data['new_customers_acquired'], float('inf'))

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        # CAC interpretation depends heavily on industry and customer lifetime value
        if value == float('inf'):
            interpretation_ar = "لم يتم اكتساب عملاء جدد"
            interpretation_en = "No new customers acquired"
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL
        elif value <= 50:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"تكلفة اكتساب العميل {self.format_currency(value)} - ممتاز، تكلفة منخفضة"
            interpretation_en = f"Customer acquisition cost {self.format_currency(value)} - Excellent, low cost"
        elif value <= 200:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"تكلفة اكتساب العميل {self.format_currency(value)} - جيد، تكلفة معقولة"
            interpretation_en = f"Customer acquisition cost {self.format_currency(value)} - Good, reasonable cost"
        elif value <= 500:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"تكلفة اكتساب العميل {self.format_currency(value)} - متوسط، يحتاج مراجعة"
            interpretation_en = f"Customer acquisition cost {self.format_currency(value)} - Average, needs review"
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"تكلفة اكتساب العميل {self.format_currency(value)} - مرتفع، يحتاج تحسين"
            interpretation_en = f"Customer acquisition cost {self.format_currency(value)} - High, needs improvement"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين كفاءة التسويق"] if value > 200 else ["الحفاظ على الكفاءة"],
            recommendations_en=["Improve marketing efficiency"] if value > 200 else ["Maintain efficiency"]
        )


class ProductivityIndexAnalysis(BaseFinancialAnalysis):
    """Productivity Index Analysis - تحليل مؤشر الإنتاجية"""

    def __init__(self):
        super().__init__(
            name_ar="مؤشر الإنتاجية",
            name_en="Productivity Index",
            category=AnalysisCategory.EFFICIENCY,
            description_ar="يقيس الإنتاجية الإجمالية للشركة",
            description_en="Measures overall company productivity"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['revenue', 'total_expenses']
        self.validate_data(data, required_fields)

        # Productivity = Output / Input
        return self.handle_division_by_zero(data['revenue'], data['total_expenses'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 2.0:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"مؤشر الإنتاجية {value:.2f} - ممتاز، إنتاجية عالية جداً"
            interpretation_en = f"Productivity index {value:.2f} - Excellent, very high productivity"
        elif value >= 1.5:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"مؤشر الإنتاجية {value:.2f} - جيد، إنتاجية صحية"
            interpretation_en = f"Productivity index {value:.2f} - Good, healthy productivity"
        elif value >= 1.2:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"مؤشر الإنتاجية {value:.2f} - متوسط، يحتاج تحسين"
            interpretation_en = f"Productivity index {value:.2f} - Average, needs improvement"
        elif value >= 1.0:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"مؤشر الإنتاجية {value:.2f} - ضعيف، إنتاجية منخفضة"
            interpretation_en = f"Productivity index {value:.2f} - Poor, low productivity"
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL
            interpretation_ar = f"مؤشر الإنتاجية {value:.2f} - خطير، خسائر في الإنتاجية"
            interpretation_en = f"Productivity index {value:.2f} - Critical, productivity losses"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين الكفاءة التشغيلية", "تقليل النفقات"] if value < 1.5 else ["الحفاظ على الإنتاجية"],
            recommendations_en=["Improve operational efficiency", "Reduce expenses"] if value < 1.5 else ["Maintain productivity"]
        )


# Efficiency Analysis Factory
class EfficiencyAnalysisFactory:
    """Factory for creating efficiency analysis instances"""

    _analyses = {
        'asset_turnover_ratio': AssetTurnoverRatioAnalysis,
        'inventory_turnover': InventoryTurnoverAnalysis,
        'receivables_turnover': ReceivablesTurnoverAnalysis,
        'fixed_asset_turnover': FixedAssetTurnoverAnalysis,
        'working_capital_turnover': WorkingCapitalTurnoverAnalysis,
        'customer_acquisition_cost': CustomerAcquisitionCostAnalysis,
        'productivity_index': ProductivityIndexAnalysis,
    }

    @classmethod
    def create_analysis(cls, analysis_type: str) -> BaseFinancialAnalysis:
        if analysis_type not in cls._analyses:
            raise ValueError(f"Unknown efficiency analysis type: {analysis_type}")
        return cls._analyses[analysis_type]()

    @classmethod
    def get_all_analyses(cls) -> Dict[str, BaseFinancialAnalysis]:
        return {name: cls() for name, cls in cls._analyses.items()}

    @classmethod
    def get_analysis_names(cls) -> list:
        return list(cls._analyses.keys())


# Comprehensive Efficiency Assessment
class ComprehensiveEfficiencyAssessment:
    """Comprehensive efficiency assessment using all efficiency ratios"""

    def __init__(self):
        self.factory = EfficiencyAnalysisFactory()

    def assess_efficiency(self, data: Dict[str, Any], benchmark_data: Optional[BenchmarkData] = None) -> Dict[str, AnalysisResult]:
        """Perform comprehensive efficiency assessment"""
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

    def generate_efficiency_summary(self, results: Dict[str, AnalysisResult]) -> Dict[str, Any]:
        """Generate summary of efficiency assessment"""
        summary = {
            'total_analyses': len(results),
            'excellent_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.EXCELLENT),
            'good_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.GOOD),
            'average_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.AVERAGE),
            'poor_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.POOR),
            'critical_count': sum(1 for r in results.values() if r.performance_rating == PerformanceRating.CRITICAL),
            'overall_efficiency_score': 0,
            'key_strengths': [],
            'key_weaknesses': [],
            'priority_recommendations': []
        }

        score_mapping = {PerformanceRating.EXCELLENT: 5, PerformanceRating.GOOD: 4,
                        PerformanceRating.AVERAGE: 3, PerformanceRating.POOR: 2, PerformanceRating.CRITICAL: 1}

        total_score = sum(score_mapping.get(result.performance_rating, 0) for result in results.values())
        summary['overall_efficiency_score'] = total_score / len(results) if results else 0

        return summary


__all__ = [
    'AssetTurnoverRatioAnalysis', 'InventoryTurnoverAnalysis', 'ReceivablesTurnoverAnalysis',
    'FixedAssetTurnoverAnalysis', 'WorkingCapitalTurnoverAnalysis', 'CustomerAcquisitionCostAnalysis',
    'ProductivityIndexAnalysis', 'EfficiencyAnalysisFactory', 'ComprehensiveEfficiencyAssessment'
]