"""
Operating Cash Flow Ratio Analysis - نسبة التدفق النقدي التشغيلي
==============================================================

This module implements the Operating Cash Flow Ratio analysis.
يطبق هذا الوحدة تحليل نسبة التدفق النقدي التشغيلي.

The Operating Cash Flow Ratio measures ability to pay current liabilities with cash from operations.
تقيس نسبة التدفق النقدي التشغيلي القدرة على سداد الالتزامات الجارية بالنقد من العمليات.

Formula: Operating Cash Flow Ratio = Operating Cash Flow / Current Liabilities
الصيغة: نسبة التدفق النقدي التشغيلي = التدفق النقدي التشغيلي / الخصوم الجارية
"""

from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class OperatingCashFlowRatioAnalysis(BaseFinancialAnalysis):
    """
    Operating Cash Flow Ratio Analysis
    تحليل نسبة التدفق النقدي التشغيلي

    Measures liquidity based on cash generated from core business operations.
    يقيس السيولة بناءً على النقد المتولد من العمليات التجارية الأساسية.
    """

    def __init__(self):
        super().__init__(
            name_ar="نسبة التدفق النقدي التشغيلي",
            name_en="Operating Cash Flow Ratio",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="تقيس قدرة الشركة على تغطية التزاماتها الجارية من التدفق النقدي التشغيلي",
            description_en="Measures company's ability to cover current liabilities from operating cash flow"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calculate Operating Cash Flow Ratio.
        حساب نسبة التدفق النقدي التشغيلي.

        Args:
            data: Dictionary containing financial data
                - operating_cash_flow: التدفق النقدي التشغيلي
                - current_liabilities: الخصوم الجارية

        Returns:
            float: Operating Cash Flow Ratio value

        Raises:
            ValueError: If required data is missing
        """
        required_fields = ['operating_cash_flow', 'current_liabilities']
        self.validate_data(data, required_fields)

        operating_cash_flow = data['operating_cash_flow']
        current_liabilities = data['current_liabilities']

        # Handle negative values - negative OCF is particularly concerning
        warnings_list = []
        if operating_cash_flow < 0:
            warnings_list.append("Negative operating cash flow detected - company is consuming cash in operations")
        if current_liabilities < 0:
            warnings_list.append("Negative current liabilities detected - unusual accounting treatment")

        if warnings_list:
            for warning in warnings_list:
                print(f"Warning: {warning}")

        return self.handle_division_by_zero(operating_cash_flow, current_liabilities, float('inf'))

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        """
        Interpret Operating Cash Flow Ratio results.
        تفسير نتائج نسبة التدفق النقدي التشغيلي.

        Args:
            value: Calculated operating cash flow ratio
            benchmark_data: Industry benchmark data

        Returns:
            AnalysisResult: Complete analysis result
        """
        # Risk level thresholds
        risk_thresholds = {
            'very_high': 0.1,    # أقل من 0.1 خطر عالي جداً
            'high': 0.25,        # أقل من 0.25 خطر عالي
            'moderate': 0.4,     # أقل من 0.4 خطر متوسط
            'low': 0.6,          # أقل من 0.6 خطر منخفض
        }

        # Performance benchmarks
        performance_benchmarks = {
            'excellent': 0.8,    # ممتاز
            'good': 0.6,         # جيد
            'average': 0.4,      # متوسط
            'poor': 0.25,        # ضعيف
        }

        # Special handling for negative values
        if value < 0:
            risk_level = RiskLevel.VERY_HIGH
            performance_rating = PerformanceRating.CRITICAL
        else:
            risk_level = self.determine_risk_level(value, risk_thresholds)
            performance_rating = self.determine_performance_rating(value, performance_benchmarks)

        # Generate interpretations
        interpretation_ar = self._generate_interpretation_ar(value, risk_level, performance_rating)
        interpretation_en = self._generate_interpretation_en(value, risk_level, performance_rating)

        # Generate recommendations
        recommendations_ar = self._generate_recommendations_ar(value, risk_level)
        recommendations_en = self._generate_recommendations_en(value, risk_level)

        # Benchmark comparison
        benchmark_comparison = None
        industry_benchmark = None
        if benchmark_data and benchmark_data.industry_average:
            industry_benchmark = benchmark_data.industry_average
            benchmark_comparison = self.generate_benchmark_comparison(value, industry_benchmark)

        return AnalysisResult(
            value=value,
            interpretation_ar=interpretation_ar,
            interpretation_en=interpretation_en,
            risk_level=risk_level,
            performance_rating=performance_rating,
            industry_benchmark=industry_benchmark,
            benchmark_comparison=benchmark_comparison,
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en,
            warnings=None
        )

    def _generate_interpretation_ar(self, value: float, risk_level: RiskLevel,
                                  performance_rating: PerformanceRating) -> str:
        """Generate Arabic interpretation."""
        if value == float('inf'):
            return "الشركة لا تملك التزامات جارية وتحقق تدفق نقدي تشغيلي إيجابي"

        base_interpretation = f"نسبة التدفق النقدي التشغيلي هي {value:.3f} ({self.format_percentage(value)})"

        if value < 0:
            return f"{base_interpretation}. هذا مؤشر خطير جداً يعني أن الشركة تحقق تدفق نقدي تشغيلي سالب، أي أنها تستنزف النقدية في عملياتها الأساسية بدلاً من توليدها. هذا يشير إلى مشاكل جوهرية في النموذج التجاري والربحية."
        elif 0 <= value < 0.2:
            return f"{base_interpretation}. التدفق النقدي التشغيلي ضعيف جداً مقارنة بالالتزامات الجارية. الشركة تواجه صعوبات في توليد نقدية كافية من عملياتها لتغطية التزاماتها."
        elif 0.2 <= value < 0.5:
            return f"{base_interpretation}. التدفق النقدي التشغيلي مقبول ولكن يحتاج لتحسين. الشركة تولد نقدية من عملياتها لكن ليس بالمستوى المطلوب لتغطية جميع الالتزامات الجارية."
        elif 0.5 <= value < 1.0:
            return f"{base_interpretation}. التدفق النقدي التشغيلي جيد. الشركة قادرة على تغطية نسبة كبيرة من التزاماتها الجارية من عملياتها الأساسية."
        else:
            return f"{base_interpretation}. التدفق النقدي التشغيلي ممتاز. الشركة تولد نقدية كافية من عملياتها لتغطية جميع التزاماتها الجارية مع فائض إضافي."

    def _generate_interpretation_en(self, value: float, risk_level: RiskLevel,
                                   performance_rating: PerformanceRating) -> str:
        """Generate English interpretation."""
        if value == float('inf'):
            return "The company has no current liabilities and generates positive operating cash flow"

        base_interpretation = f"The operating cash flow ratio is {value:.3f} ({self.format_percentage(value)})"

        if value < 0:
            return f"{base_interpretation}. This is a very critical indicator meaning the company generates negative operating cash flow, consuming cash in its core operations instead of generating it. This indicates fundamental problems in the business model and profitability."
        elif 0 <= value < 0.2:
            return f"{base_interpretation}. Operating cash flow is very weak compared to current liabilities. The company faces difficulties generating sufficient cash from operations to cover its obligations."
        elif 0.2 <= value < 0.5:
            return f"{base_interpretation}. Operating cash flow is acceptable but needs improvement. The company generates cash from operations but not at the required level to cover all current liabilities."
        elif 0.5 <= value < 1.0:
            return f"{base_interpretation}. Operating cash flow is good. The company can cover a large portion of its current liabilities from core operations."
        else:
            return f"{base_interpretation}. Operating cash flow is excellent. The company generates sufficient cash from operations to cover all current liabilities with additional surplus."

    def _generate_recommendations_ar(self, value: float, risk_level: RiskLevel) -> list:
        """Generate Arabic recommendations."""
        recommendations = []

        if value < 0:
            recommendations.extend([
                "مراجعة النموذج التجاري والعمليات الأساسية بشكل عاجل",
                "تحليل أسباب استنزاف النقدية في العمليات",
                "تحسين هوامش الربح وتقليل التكاليف التشغيلية",
                "تسريع دورة التحصيل وتأجيل المدفوعات",
                "إعادة تقييم استراتيجية التسعير",
                "تحسين إدارة المخزون وتقليل رأس المال العامل"
            ])
        elif 0 <= value < 0.4:
            recommendations.extend([
                "تحسين كفاءة العمليات التشغيلية",
                "تقليل التكاليف المتغيرة والثابتة",
                "تحسين إدارة رأس المال العامل",
                "تسريع تحصيل الذمم المدينة",
                "مراجعة شروط الدفع مع الموردين"
            ])
        elif 0.4 <= value < 0.8:
            recommendations.extend([
                "الحفاظ على مستوى التدفق النقدي الحالي",
                "البحث عن فرص تحسين الكفاءة",
                "تحسين التخطيط للتدفق النقدي"
            ])
        else:
            recommendations.extend([
                "استثمار الفائض النقدي بحكمة",
                "تقييم فرص التوسع والنمو",
                "تحسين العائد على الاستثمار",
                "النظر في توزيعات أرباح أعلى"
            ])

        return recommendations

    def _generate_recommendations_en(self, value: float, risk_level: RiskLevel) -> list:
        """Generate English recommendations."""
        recommendations = []

        if value < 0:
            recommendations.extend([
                "Urgently review business model and core operations",
                "Analyze causes of cash consumption in operations",
                "Improve profit margins and reduce operating costs",
                "Accelerate collection cycle and delay payments",
                "Re-evaluate pricing strategy",
                "Improve inventory management and reduce working capital"
            ])
        elif 0 <= value < 0.4:
            recommendations.extend([
                "Improve operational efficiency",
                "Reduce variable and fixed costs",
                "Enhance working capital management",
                "Accelerate accounts receivable collection",
                "Review payment terms with suppliers"
            ])
        elif 0.4 <= value < 0.8:
            recommendations.extend([
                "Maintain current cash flow level",
                "Seek efficiency improvement opportunities",
                "Improve cash flow planning"
            ])
        else:
            recommendations.extend([
                "Invest excess cash wisely",
                "Evaluate expansion and growth opportunities",
                "Improve return on investment",
                "Consider higher dividend payments"
            ])

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Create analysis instance
    analysis = OperatingCashFlowRatioAnalysis()

    # Test data
    test_data = {
        'operating_cash_flow': 45000,
        'current_liabilities': 100000
    }

    # Create benchmark data
    benchmark = BenchmarkData(
        industry_average=0.5,
        sector_average=0.45,
        market_average=0.52
    )

    # Run analysis
    result = analysis.run_full_analysis(test_data, benchmark)

    # Print results
    print(f"Operating Cash Flow Ratio: {result.value:.3f}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Performance Rating: {result.performance_rating}")
    print(f"Arabic Interpretation: {result.interpretation_ar}")
    print(f"English Interpretation: {result.interpretation_en}")
    print(f"Benchmark Comparison: {result.benchmark_comparison}")