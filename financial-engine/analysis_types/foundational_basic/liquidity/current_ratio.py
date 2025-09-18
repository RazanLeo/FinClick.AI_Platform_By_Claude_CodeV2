"""
Current Ratio Analysis - نسبة السيولة الجارية
==============================================

This module implements the Current Ratio analysis, one of the most fundamental liquidity ratios.
يطبق هذا الوحدة تحليل نسبة السيولة الجارية، واحدة من أهم نسب السيولة الأساسية.

The Current Ratio measures a company's ability to pay short-term obligations with current assets.
تقيس نسبة السيولة الجارية قدرة الشركة على سداد الالتزامات قصيرة الأجل بالأصول الجارية.

Formula: Current Ratio = Current Assets / Current Liabilities
الصيغة: نسبة السيولة الجارية = الأصول الجارية / الخصوم الجارية
"""

from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class CurrentRatioAnalysis(BaseFinancialAnalysis):
    """
    Current Ratio Analysis
    تحليل نسبة السيولة الجارية

    Measures the company's ability to cover short-term liabilities with current assets.
    يقيس قدرة الشركة على تغطية الالتزامات قصيرة الأجل بالأصول الجارية.
    """

    def __init__(self):
        super().__init__(
            name_ar="نسبة السيولة الجارية",
            name_en="Current Ratio",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="تقيس قدرة الشركة على سداد التزاماتها قصيرة الأجل باستخدام أصولها الجارية",
            description_en="Measures company's ability to pay short-term obligations using current assets"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calculate Current Ratio.
        حساب نسبة السيولة الجارية.

        Args:
            data: Dictionary containing financial data
                - current_assets: الأصول الجارية
                - current_liabilities: الخصوم الجارية

        Returns:
            float: Current Ratio value

        Raises:
            ValueError: If required data is missing
        """
        required_fields = ['current_assets', 'current_liabilities']
        self.validate_data(data, required_fields)

        current_assets = data['current_assets']
        current_liabilities = data['current_liabilities']

        # Handle negative values
        warnings_list = self.check_negative_values({
            'current_assets': current_assets,
            'current_liabilities': current_liabilities
        })

        if warnings_list:
            for warning in warnings_list:
                print(f"Warning: {warning}")

        return self.handle_division_by_zero(current_assets, current_liabilities, float('inf'))

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        """
        Interpret Current Ratio results.
        تفسير نتائج نسبة السيولة الجارية.

        Args:
            value: Calculated current ratio
            benchmark_data: Industry benchmark data

        Returns:
            AnalysisResult: Complete analysis result
        """
        # Risk level thresholds
        risk_thresholds = {
            'very_high': 0.5,    # أقل من 0.5 خطر عالي جداً
            'high': 1.0,         # أقل من 1.0 خطر عالي
            'moderate': 1.5,     # أقل من 1.5 خطر متوسط
            'low': 2.0,          # أقل من 2.0 خطر منخفض
        }

        # Performance benchmarks
        performance_benchmarks = {
            'excellent': 2.5,    # ممتاز
            'good': 2.0,         # جيد
            'average': 1.5,      # متوسط
            'poor': 1.0,         # ضعيف
        }

        # Determine risk level and performance rating
        risk_level = self.determine_risk_level(value, risk_thresholds)
        performance_rating = self.determine_performance_rating(value, performance_benchmarks)

        # Generate interpretations in Arabic and English
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
            return "الشركة لا تملك التزامات جارية، مما يشير إلى سيولة مطلقة"

        base_interpretation = f"نسبة السيولة الجارية هي {value:.2f}"

        if value < 1.0:
            return f"{base_interpretation}. هذا يعني أن الأصول الجارية لا تكفي لتغطية الالتزامات الجارية، مما قد يشير إلى مشاكل في السيولة وصعوبات في سداد الالتزامات قصيرة الأجل."
        elif 1.0 <= value < 1.5:
            return f"{base_interpretation}. الشركة قادرة على تغطية التزاماتها الجارية ولكن هامش الأمان محدود. يُنصح بمراقبة التدفق النقدي عن كثب."
        elif 1.5 <= value < 2.5:
            return f"{base_interpretation}. الشركة تتمتع بوضع سيولة جيد وقادرة على تغطية التزاماتها الجارية بسهولة مع وجود هامش أمان مناسب."
        else:
            return f"{base_interpretation}. الشركة تتمتع بسيولة عالية جداً، ولكن قد يشير هذا إلى عدم استغلال الأصول الجارية بكفاءة في أنشطة مدرة للربح."

    def _generate_interpretation_en(self, value: float, risk_level: RiskLevel,
                                   performance_rating: PerformanceRating) -> str:
        """Generate English interpretation."""
        if value == float('inf'):
            return "The company has no current liabilities, indicating absolute liquidity"

        base_interpretation = f"The current ratio is {value:.2f}"

        if value < 1.0:
            return f"{base_interpretation}. This means current assets are insufficient to cover current liabilities, which may indicate liquidity problems and difficulties in meeting short-term obligations."
        elif 1.0 <= value < 1.5:
            return f"{base_interpretation}. The company can cover its current liabilities but the safety margin is limited. Close monitoring of cash flow is recommended."
        elif 1.5 <= value < 2.5:
            return f"{base_interpretation}. The company enjoys good liquidity position and can easily cover its current liabilities with an appropriate safety margin."
        else:
            return f"{base_interpretation}. The company has very high liquidity, but this may indicate inefficient utilization of current assets in profit-generating activities."

    def _generate_recommendations_ar(self, value: float, risk_level: RiskLevel) -> list:
        """Generate Arabic recommendations."""
        recommendations = []

        if value < 1.0:
            recommendations.extend([
                "تحسين إدارة النقد والتدفق النقدي التشغيلي",
                "تسريع تحصيل الذمم المدينة",
                "إعادة تقييم مستويات المخزون وتحسين دورانه",
                "التفاوض على شروط سداد أطول مع الموردين",
                "النظر في الحصول على تمويل قصير الأجل إضافي"
            ])
        elif 1.0 <= value < 1.5:
            recommendations.extend([
                "مراقبة التدفق النقدي بانتظام",
                "تحسين إدارة دورة التشغيل",
                "وضع خطط طوارئ للسيولة"
            ])
        elif value > 3.0:
            recommendations.extend([
                "استكشاف فرص استثمارية للأصول النقدية الزائدة",
                "تحسين كفاءة استخدام رأس المال العامل",
                "النظر في توسيع العمليات التجارية",
                "تقييم إمكانية زيادة توزيعات الأرباح"
            ])

        return recommendations

    def _generate_recommendations_en(self, value: float, risk_level: RiskLevel) -> list:
        """Generate English recommendations."""
        recommendations = []

        if value < 1.0:
            recommendations.extend([
                "Improve cash management and operating cash flow",
                "Accelerate accounts receivable collection",
                "Re-evaluate inventory levels and improve turnover",
                "Negotiate longer payment terms with suppliers",
                "Consider obtaining additional short-term financing"
            ])
        elif 1.0 <= value < 1.5:
            recommendations.extend([
                "Monitor cash flow regularly",
                "Improve working capital cycle management",
                "Develop contingency liquidity plans"
            ])
        elif value > 3.0:
            recommendations.extend([
                "Explore investment opportunities for excess cash",
                "Improve working capital efficiency",
                "Consider business expansion opportunities",
                "Evaluate potential for increased dividend payments"
            ])

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Create analysis instance
    analysis = CurrentRatioAnalysis()

    # Test data
    test_data = {
        'current_assets': 150000,
        'current_liabilities': 100000
    }

    # Create benchmark data
    benchmark = BenchmarkData(
        industry_average=1.8,
        sector_average=1.7,
        market_average=1.9
    )

    # Run analysis
    result = analysis.run_full_analysis(test_data, benchmark)

    # Print results
    print(f"Current Ratio: {result.value:.2f}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Performance Rating: {result.performance_rating}")
    print(f"Arabic Interpretation: {result.interpretation_ar}")
    print(f"English Interpretation: {result.interpretation_en}")
    print(f"Benchmark Comparison: {result.benchmark_comparison}")