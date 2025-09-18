"""
Quick Ratio Analysis - نسبة السيولة السريعة (اختبار الحمض)
=========================================================

This module implements the Quick Ratio (Acid Test) analysis.
يطبق هذا الوحدة تحليل نسبة السيولة السريعة (اختبار الحمض).

The Quick Ratio measures immediate liquidity by excluding inventory from current assets.
تقيس نسبة السيولة السريعة السيولة الفورية باستثناء المخزون من الأصول الجارية.

Formula: Quick Ratio = (Current Assets - Inventory) / Current Liabilities
الصيغة: نسبة السيولة السريعة = (الأصول الجارية - المخزون) / الخصوم الجارية
"""

from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class QuickRatioAnalysis(BaseFinancialAnalysis):
    """
    Quick Ratio (Acid Test) Analysis
    تحليل نسبة السيولة السريعة (اختبار الحمض)

    Measures immediate liquidity excluding inventory.
    يقيس السيولة الفورية باستثناء المخزون.
    """

    def __init__(self):
        super().__init__(
            name_ar="نسبة السيولة السريعة (اختبار الحمض)",
            name_en="Quick Ratio (Acid Test)",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="تقيس السيولة الفورية للشركة باستثناء المخزون من الأصول الجارية",
            description_en="Measures company's immediate liquidity excluding inventory from current assets"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calculate Quick Ratio.
        حساب نسبة السيولة السريعة.

        Args:
            data: Dictionary containing financial data
                - current_assets: الأصول الجارية
                - inventory: المخزون
                - current_liabilities: الخصوم الجارية

        Returns:
            float: Quick Ratio value

        Raises:
            ValueError: If required data is missing
        """
        required_fields = ['current_assets', 'current_liabilities']
        self.validate_data(data, required_fields)

        current_assets = data['current_assets']
        current_liabilities = data['current_liabilities']
        inventory = data.get('inventory', 0)  # Default to 0 if not provided

        # Calculate quick assets (current assets minus inventory)
        quick_assets = current_assets - inventory

        # Handle negative values
        warnings_list = self.check_negative_values({
            'current_assets': current_assets,
            'current_liabilities': current_liabilities,
            'inventory': inventory,
            'quick_assets': quick_assets
        })

        if warnings_list:
            for warning in warnings_list:
                print(f"Warning: {warning}")

        return self.handle_division_by_zero(quick_assets, current_liabilities, float('inf'))

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        """
        Interpret Quick Ratio results.
        تفسير نتائج نسبة السيولة السريعة.

        Args:
            value: Calculated quick ratio
            benchmark_data: Industry benchmark data

        Returns:
            AnalysisResult: Complete analysis result
        """
        # Risk level thresholds (stricter than current ratio)
        risk_thresholds = {
            'very_high': 0.3,    # أقل من 0.3 خطر عالي جداً
            'high': 0.7,         # أقل من 0.7 خطر عالي
            'moderate': 1.0,     # أقل من 1.0 خطر متوسط
            'low': 1.5,          # أقل من 1.5 خطر منخفض
        }

        # Performance benchmarks
        performance_benchmarks = {
            'excellent': 1.5,    # ممتاز
            'good': 1.2,         # جيد
            'average': 1.0,      # متوسط
            'poor': 0.7,         # ضعيف
        }

        # Determine risk level and performance rating
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
            return "الشركة لا تملك التزامات جارية، مما يشير إلى سيولة مطلقة فورية"

        base_interpretation = f"نسبة السيولة السريعة هي {value:.2f}"

        if value < 0.5:
            return f"{base_interpretation}. هذا مؤشر خطير يدل على ضعف شديد في السيولة الفورية. الشركة قد تواجه صعوبات كبيرة في الوفاء بالتزاماتها الجارية دون الاعتماد على بيع المخزون."
        elif 0.5 <= value < 0.8:
            return f"{base_interpretation}. السيولة الفورية ضعيفة. الشركة تعتمد بشكل كبير على المخزون لتغطية التزاماتها، مما قد يشكل مخاطر في حالة بطء دوران المخزون."
        elif 0.8 <= value < 1.2:
            return f"{base_interpretation}. السيولة الفورية مقبولة. الشركة قادرة على تغطية معظم التزاماتها الجارية بالأصول السائلة، لكن هناك مجال للتحسين."
        elif 1.2 <= value < 2.0:
            return f"{base_interpretation}. السيولة الفورية جيدة جداً. الشركة تتمتع بقدرة قوية على الوفاء بالتزاماتها الجارية دون الحاجة لبيع المخزون."
        else:
            return f"{base_interpretation}. السيولة الفورية مرتفعة جداً، مما قد يشير إلى عدم استثمار الأصول النقدية بكفاءة أو تكديس نقدي مفرط."

    def _generate_interpretation_en(self, value: float, risk_level: RiskLevel,
                                   performance_rating: PerformanceRating) -> str:
        """Generate English interpretation."""
        if value == float('inf'):
            return "The company has no current liabilities, indicating absolute immediate liquidity"

        base_interpretation = f"The quick ratio is {value:.2f}"

        if value < 0.5:
            return f"{base_interpretation}. This is a critical indicator of severe immediate liquidity weakness. The company may face significant difficulties meeting current obligations without relying on inventory sales."
        elif 0.5 <= value < 0.8:
            return f"{base_interpretation}. Immediate liquidity is weak. The company heavily relies on inventory to cover obligations, which may pose risks if inventory turnover is slow."
        elif 0.8 <= value < 1.2:
            return f"{base_interpretation}. Immediate liquidity is acceptable. The company can cover most current liabilities with liquid assets, but there's room for improvement."
        elif 1.2 <= value < 2.0:
            return f"{base_interpretation}. Immediate liquidity is very good. The company has strong capability to meet current obligations without needing to sell inventory."
        else:
            return f"{base_interpretation}. Immediate liquidity is very high, which may indicate inefficient investment of cash assets or excessive cash hoarding."

    def _generate_recommendations_ar(self, value: float, risk_level: RiskLevel) -> list:
        """Generate Arabic recommendations."""
        recommendations = []

        if value < 0.7:
            recommendations.extend([
                "زيادة الأصول النقدية والاستثمارات قصيرة الأجل",
                "تسريع تحصيل الذمم المدينة بشكل عاجل",
                "تحسين إدارة التدفق النقدي الداخل",
                "إعادة النظر في سياسات الائتمان الممنوح للعملاء",
                "تأجيل المدفوعات غير الضرورية",
                "الحصول على خط ائتمان طارئ من البنك"
            ])
        elif 0.7 <= value < 1.0:
            recommendations.extend([
                "تحسين سياسات التحصيل",
                "مراقبة التدفق النقدي اليومي",
                "تقليل فترة التحصيل من العملاء",
                "تحسين إدارة النقدية"
            ])
        elif value > 2.0:
            recommendations.extend([
                "استثمار الفائض النقدي في أصول منتجة",
                "تقييم فرص التوسع أو الاستحواذ",
                "تحسين العائد على الأصول النقدية",
                "النظر في توزيعات أرباح إضافية للمساهمين",
                "استثمار في البحث والتطوير"
            ])

        return recommendations

    def _generate_recommendations_en(self, value: float, risk_level: RiskLevel) -> list:
        """Generate English recommendations."""
        recommendations = []

        if value < 0.7:
            recommendations.extend([
                "Increase cash and short-term investments urgently",
                "Accelerate accounts receivable collection",
                "Improve cash inflow management",
                "Review credit policies extended to customers",
                "Defer non-essential payments",
                "Obtain emergency credit line from bank"
            ])
        elif 0.7 <= value < 1.0:
            recommendations.extend([
                "Improve collection policies",
                "Monitor daily cash flow",
                "Reduce customer collection period",
                "Enhance cash management"
            ])
        elif value > 2.0:
            recommendations.extend([
                "Invest excess cash in productive assets",
                "Evaluate expansion or acquisition opportunities",
                "Improve return on cash assets",
                "Consider additional dividend payments to shareholders",
                "Invest in research and development"
            ])

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Create analysis instance
    analysis = QuickRatioAnalysis()

    # Test data
    test_data = {
        'current_assets': 150000,
        'inventory': 50000,
        'current_liabilities': 100000
    }

    # Create benchmark data
    benchmark = BenchmarkData(
        industry_average=1.1,
        sector_average=1.0,
        market_average=1.2
    )

    # Run analysis
    result = analysis.run_full_analysis(test_data, benchmark)

    # Print results
    print(f"Quick Ratio: {result.value:.2f}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Performance Rating: {result.performance_rating}")
    print(f"Arabic Interpretation: {result.interpretation_ar}")
    print(f"English Interpretation: {result.interpretation_en}")
    print(f"Benchmark Comparison: {result.benchmark_comparison}")