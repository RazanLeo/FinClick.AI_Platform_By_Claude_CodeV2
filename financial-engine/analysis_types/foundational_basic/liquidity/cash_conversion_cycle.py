"""
Cash Conversion Cycle Analysis - دورة تحويل النقدية
================================================

This module implements the Cash Conversion Cycle analysis.
يطبق هذا الوحدة تحليل دورة تحويل النقدية.

The Cash Conversion Cycle measures how long it takes to convert investments into cash flows.
تقيس دورة تحويل النقدية المدة اللازمة لتحويل الاستثمارات إلى تدفقات نقدية.

Formula: CCC = DIO + DSO - DPO
الصيغة: دورة تحويل النقدية = أيام بقاء المخزون + أيام التحصيل - أيام الدفع
Where:
- DIO = Days Inventory Outstanding
- DSO = Days Sales Outstanding
- DPO = Days Payable Outstanding
"""

from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class CashConversionCycleAnalysis(BaseFinancialAnalysis):
    """
    Cash Conversion Cycle Analysis
    تحليل دورة تحويل النقدية

    Measures the efficiency of working capital management.
    يقيس كفاءة إدارة رأس المال العامل.
    """

    def __init__(self):
        super().__init__(
            name_ar="دورة تحويل النقدية",
            name_en="Cash Conversion Cycle",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="تقيس كفاءة الشركة في تحويل استثماراتها في المخزون والذمم المدينة إلى نقدية",
            description_en="Measures company's efficiency in converting inventory and receivables investments into cash"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calculate Cash Conversion Cycle.
        حساب دورة تحويل النقدية.

        Args:
            data: Dictionary containing financial data
                - inventory: المخزون (average or ending)
                - accounts_receivable: الذمم المدينة (average or ending)
                - accounts_payable: الذمم الدائنة (average or ending)
                - cost_of_goods_sold: تكلفة البضاعة المباعة
                - revenue: الإيرادات
                - purchases: المشتريات (optional, defaults to COGS)

        Returns:
            float: Cash Conversion Cycle in days

        Raises:
            ValueError: If required data is missing
        """
        required_fields = ['inventory', 'accounts_receivable', 'accounts_payable',
                          'cost_of_goods_sold', 'revenue']
        self.validate_data(data, required_fields)

        inventory = data['inventory']
        accounts_receivable = data['accounts_receivable']
        accounts_payable = data['accounts_payable']
        cost_of_goods_sold = data['cost_of_goods_sold']
        revenue = data['revenue']
        purchases = data.get('purchases', cost_of_goods_sold)  # Default to COGS if not provided

        # Calculate components
        # Days Inventory Outstanding (DIO)
        dio = self.handle_division_by_zero(inventory * 365, cost_of_goods_sold, 0)

        # Days Sales Outstanding (DSO)
        dso = self.handle_division_by_zero(accounts_receivable * 365, revenue, 0)

        # Days Payable Outstanding (DPO)
        dpo = self.handle_division_by_zero(accounts_payable * 365, purchases, 0)

        # Cash Conversion Cycle
        ccc = dio + dso - dpo

        # Handle negative values
        warnings_list = self.check_negative_values({
            'inventory': inventory,
            'accounts_receivable': accounts_receivable,
            'accounts_payable': accounts_payable,
            'cost_of_goods_sold': cost_of_goods_sold,
            'revenue': revenue
        })

        if warnings_list:
            for warning in warnings_list:
                print(f"Warning: {warning}")

        return ccc

    def calculate_components(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate individual components of CCC.
        حساب المكونات الفردية لدورة تحويل النقدية.

        Returns:
            Dict containing DIO, DSO, DPO values
        """
        inventory = data['inventory']
        accounts_receivable = data['accounts_receivable']
        accounts_payable = data['accounts_payable']
        cost_of_goods_sold = data['cost_of_goods_sold']
        revenue = data['revenue']
        purchases = data.get('purchases', cost_of_goods_sold)

        dio = self.handle_division_by_zero(inventory * 365, cost_of_goods_sold, 0)
        dso = self.handle_division_by_zero(accounts_receivable * 365, revenue, 0)
        dpo = self.handle_division_by_zero(accounts_payable * 365, purchases, 0)

        return {
            'DIO': dio,
            'DSO': dso,
            'DPO': dpo
        }

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        """
        Interpret Cash Conversion Cycle results.
        تفسير نتائج دورة تحويل النقدية.

        Args:
            value: Calculated cash conversion cycle in days
            benchmark_data: Industry benchmark data

        Returns:
            AnalysisResult: Complete analysis result
        """
        # Risk level thresholds (shorter cycles are better)
        risk_thresholds = {
            'very_high': 120,    # أكثر من 120 يوم خطر عالي جداً
            'high': 90,          # أكثر من 90 يوم خطر عالي
            'moderate': 60,      # أكثر من 60 يوم خطر متوسط
            'low': 30,           # أكثر من 30 يوم خطر منخفض
        }

        # Performance benchmarks (shorter is better)
        performance_benchmarks = {
            'excellent': 0,      # سالب أو صفر ممتاز
            'good': 30,          # أقل من 30 يوم جيد
            'average': 60,       # أقل من 60 يوم متوسط
            'poor': 90,          # أقل من 90 يوم ضعيف
        }

        # Determine risk level and performance rating (reverse logic for CCC)
        if value <= 0:
            risk_level = RiskLevel.VERY_LOW
            performance_rating = PerformanceRating.EXCELLENT
        elif value <= 30:
            risk_level = RiskLevel.LOW
            performance_rating = PerformanceRating.GOOD
        elif value <= 60:
            risk_level = RiskLevel.MODERATE
            performance_rating = PerformanceRating.AVERAGE
        elif value <= 90:
            risk_level = RiskLevel.HIGH
            performance_rating = PerformanceRating.POOR
        else:
            risk_level = RiskLevel.VERY_HIGH
            performance_rating = PerformanceRating.CRITICAL

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
        base_interpretation = f"دورة تحويل النقدية هي {value:.1f} يوم"

        if value < 0:
            return f"{base_interpretation}. هذا ممتاز! الشركة تحصل على الدفع من عملائها قبل أن تدفع لمورديها، مما يعني أن المورين يمولون عمليات الشركة فعلياً، وهذا يحسن التدفق النقدي بشكل كبير."
        elif 0 <= value <= 30:
            return f"{base_interpretation}. هذا أداء جيد جداً. الشركة تدير رأس مالها العامل بكفاءة عالية وتحول استثماراتها إلى نقدية بسرعة."
        elif 30 < value <= 60:
            return f"{base_interpretation}. هذا أداء متوسط. الشركة تحتاج حوالي شهرين لتحويل استثماراتها إلى نقدية، وهو مقبول لكن يمكن تحسينه."
        elif 60 < value <= 90:
            return f"{base_interpretation}. الدورة طويلة نسبياً. الشركة تحتاج إلى ثلاثة أشهر لتحويل استثماراتها إلى نقدية، مما قد يضغط على السيولة."
        else:
            return f"{base_interpretation}. الدورة طويلة جداً ومقلقة. الشركة تحتاج لأكثر من ثلاثة أشهر لتحويل استثماراتها إلى نقدية، مما يعرضها لمخاطر السيولة ويقلل من كفاءة رأس المال."

    def _generate_interpretation_en(self, value: float, risk_level: RiskLevel,
                                   performance_rating: PerformanceRating) -> str:
        """Generate English interpretation."""
        base_interpretation = f"The cash conversion cycle is {value:.1f} days"

        if value < 0:
            return f"{base_interpretation}. This is excellent! The company receives payment from customers before paying suppliers, meaning suppliers effectively finance the company's operations, significantly improving cash flow."
        elif 0 <= value <= 30:
            return f"{base_interpretation}. This is very good performance. The company manages working capital very efficiently and converts investments to cash quickly."
        elif 30 < value <= 60:
            return f"{base_interpretation}. This is average performance. The company needs about two months to convert investments to cash, which is acceptable but can be improved."
        elif 60 < value <= 90:
            return f"{base_interpretation}. The cycle is relatively long. The company needs three months to convert investments to cash, which may pressure liquidity."
        else:
            return f"{base_interpretation}. The cycle is very long and concerning. The company needs more than three months to convert investments to cash, exposing it to liquidity risks and reducing capital efficiency."

    def _generate_recommendations_ar(self, value: float, risk_level: RiskLevel) -> list:
        """Generate Arabic recommendations."""
        recommendations = []

        if value > 90:
            recommendations.extend([
                "تقليل مستويات المخزون وتحسين دورانه",
                "تسريع تحصيل الذمم المدينة",
                "تحسين شروط الائتمان مع العملاء",
                "التفاوض على شروط دفع أطول مع الموردين",
                "تحسين إدارة سلسلة التوريد",
                "استخدام تقنيات إدارة المخزون الحديثة (JIT)",
                "مراجعة سياسات الائتمان والتحصيل"
            ])
        elif 60 < value <= 90:
            recommendations.extend([
                "تحسين إدارة المخزون",
                "تقليل فترة التحصيل من العملاء",
                "تحسين شروط الدفع مع الموردين",
                "مراقبة دورة رأس المال العامل بانتظام"
            ])
        elif 30 < value <= 60:
            recommendations.extend([
                "الحفاظ على مستوى الأداء الحالي",
                "البحث عن فرص تحسين إضافية",
                "مراقبة مكونات الدورة بانتظام"
            ])
        else:  # value <= 30
            recommendations.extend([
                "الحفاظ على الأداء الممتاز الحالي",
                "مشاركة أفضل الممارسات مع الصناعة",
                "استكشاف فرص النمو باستخدام التدفق النقدي القوي"
            ])

        return recommendations

    def _generate_recommendations_en(self, value: float, risk_level: RiskLevel) -> list:
        """Generate English recommendations."""
        recommendations = []

        if value > 90:
            recommendations.extend([
                "Reduce inventory levels and improve turnover",
                "Accelerate accounts receivable collection",
                "Improve credit terms with customers",
                "Negotiate longer payment terms with suppliers",
                "Improve supply chain management",
                "Use modern inventory management techniques (JIT)",
                "Review credit and collection policies"
            ])
        elif 60 < value <= 90:
            recommendations.extend([
                "Improve inventory management",
                "Reduce customer collection period",
                "Improve payment terms with suppliers",
                "Monitor working capital cycle regularly"
            ])
        elif 30 < value <= 60:
            recommendations.extend([
                "Maintain current performance level",
                "Seek additional improvement opportunities",
                "Monitor cycle components regularly"
            ])
        else:  # value <= 30
            recommendations.extend([
                "Maintain excellent current performance",
                "Share best practices with industry",
                "Explore growth opportunities using strong cash flow"
            ])

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Create analysis instance
    analysis = CashConversionCycleAnalysis()

    # Test data
    test_data = {
        'inventory': 80000,
        'accounts_receivable': 60000,
        'accounts_payable': 40000,
        'cost_of_goods_sold': 400000,
        'revenue': 600000,
        'purchases': 420000
    }

    # Create benchmark data
    benchmark = BenchmarkData(
        industry_average=55.0,
        sector_average=60.0,
        market_average=58.0
    )

    # Run analysis
    result = analysis.run_full_analysis(test_data, benchmark)

    # Calculate components for detailed analysis
    components = analysis.calculate_components(test_data)

    # Print results
    print(f"Cash Conversion Cycle: {result.value:.1f} days")
    print(f"Components: DIO={components['DIO']:.1f}, DSO={components['DSO']:.1f}, DPO={components['DPO']:.1f}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Performance Rating: {result.performance_rating}")
    print(f"Arabic Interpretation: {result.interpretation_ar}")
    print(f"English Interpretation: {result.interpretation_en}")
    print(f"Benchmark Comparison: {result.benchmark_comparison}")