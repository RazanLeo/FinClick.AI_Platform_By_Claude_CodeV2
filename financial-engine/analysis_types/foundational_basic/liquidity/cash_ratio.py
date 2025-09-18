"""
Cash Ratio Analysis - نسبة النقدية
==================================

This module implements the Cash Ratio analysis.
يطبق هذا الوحدة تحليل نسبة النقدية.

The Cash Ratio is the most conservative liquidity ratio, measuring only cash and cash equivalents.
نسبة النقدية هي أكثر نسب السيولة تحفظاً، تقيس النقدية ومعادلات النقدية فقط.

Formula: Cash Ratio = (Cash + Cash Equivalents) / Current Liabilities
الصيغة: نسبة النقدية = (النقدية + معادلات النقدية) / الخصوم الجارية
"""

from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class CashRatioAnalysis(BaseFinancialAnalysis):
    """
    Cash Ratio Analysis
    تحليل نسبة النقدية

    Measures the most conservative liquidity using only cash and cash equivalents.
    يقيس السيولة الأكثر تحفظاً باستخدام النقدية ومعادلات النقدية فقط.
    """

    def __init__(self):
        super().__init__(
            name_ar="نسبة النقدية",
            name_en="Cash Ratio",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="تقيس قدرة الشركة على سداد التزاماتها الجارية باستخدام النقدية ومعادلاتها فقط",
            description_en="Measures company's ability to pay current liabilities using only cash and cash equivalents"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calculate Cash Ratio.
        حساب نسبة النقدية.

        Args:
            data: Dictionary containing financial data
                - cash: النقدية
                - cash_equivalents: معادلات النقدية (optional)
                - marketable_securities: الأوراق المالية القابلة للتداول (optional)
                - current_liabilities: الخصوم الجارية

        Returns:
            float: Cash Ratio value

        Raises:
            ValueError: If required data is missing
        """
        required_fields = ['current_liabilities']
        self.validate_data(data, required_fields)

        # Get cash components
        cash = data.get('cash', 0)
        cash_equivalents = data.get('cash_equivalents', 0)
        marketable_securities = data.get('marketable_securities', 0)
        current_liabilities = data['current_liabilities']

        # Total liquid cash (most conservative definition)
        total_cash = cash + cash_equivalents + marketable_securities

        # Handle negative values
        warnings_list = self.check_negative_values({
            'cash': cash,
            'cash_equivalents': cash_equivalents,
            'marketable_securities': marketable_securities,
            'current_liabilities': current_liabilities,
            'total_cash': total_cash
        })

        if warnings_list:
            for warning in warnings_list:
                print(f"Warning: {warning}")

        return self.handle_division_by_zero(total_cash, current_liabilities, float('inf'))

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        """
        Interpret Cash Ratio results.
        تفسير نتائج نسبة النقدية.

        Args:
            value: Calculated cash ratio
            benchmark_data: Industry benchmark data

        Returns:
            AnalysisResult: Complete analysis result
        """
        # Risk level thresholds (most conservative)
        risk_thresholds = {
            'very_high': 0.1,    # أقل من 0.1 خطر عالي جداً
            'high': 0.2,         # أقل من 0.2 خطر عالي
            'moderate': 0.4,     # أقل من 0.4 خطر متوسط
            'low': 0.6,          # أقل من 0.6 خطر منخفض
        }

        # Performance benchmarks
        performance_benchmarks = {
            'excellent': 0.5,    # ممتاز
            'good': 0.3,         # جيد
            'average': 0.2,      # متوسط
            'poor': 0.1,         # ضعيف
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
            return "الشركة لا تملك التزامات جارية، وبالتالي تحتفظ بكامل نقديتها"

        base_interpretation = f"نسبة النقدية هي {value:.3f} ({self.format_percentage(value)})"

        if value < 0.1:
            return f"{base_interpretation}. هذا مؤشر خطير جداً على نقص شديد في السيولة النقدية الفورية. الشركة تعتمد كلياً على تحويل الأصول الأخرى لتلبية التزاماتها، مما يعرضها لمخاطر السيولة الحادة."
        elif 0.1 <= value < 0.2:
            return f"{base_interpretation}. السيولة النقدية ضعيفة جداً. الشركة لديها احتياطي نقدي محدود جداً لمواجهة الأزمات أو الالتزامات العاجلة."
        elif 0.2 <= value < 0.4:
            return f"{base_interpretation}. السيولة النقدية مقبولة ولكن ليست مثالية. الشركة تحتاج لتحسين إدارة النقدية لزيادة المرونة المالية."
        elif 0.4 <= value < 0.8:
            return f"{base_interpretation}. السيولة النقدية جيدة. الشركة تتمتع بمخزون نقدي مناسب لمواجهة التزاماتها والطوارئ."
        else:
            return f"{base_interpretation}. السيولة النقدية مرتفعة جداً، مما قد يشير إلى تراكم نقدي مفرط وعدم استثمار الأموال بكفاءة في أنشطة مدرة للأرباح."

    def _generate_interpretation_en(self, value: float, risk_level: RiskLevel,
                                   performance_rating: PerformanceRating) -> str:
        """Generate English interpretation."""
        if value == float('inf'):
            return "The company has no current liabilities, maintaining all its cash"

        base_interpretation = f"The cash ratio is {value:.3f} ({self.format_percentage(value)})"

        if value < 0.1:
            return f"{base_interpretation}. This is a very critical indicator of severe immediate cash liquidity shortage. The company relies entirely on converting other assets to meet obligations, exposing it to acute liquidity risks."
        elif 0.1 <= value < 0.2:
            return f"{base_interpretation}. Cash liquidity is very weak. The company has very limited cash reserves to face crises or urgent obligations."
        elif 0.2 <= value < 0.4:
            return f"{base_interpretation}. Cash liquidity is acceptable but not ideal. The company needs to improve cash management to increase financial flexibility."
        elif 0.4 <= value < 0.8:
            return f"{base_interpretation}. Cash liquidity is good. The company maintains adequate cash reserves to meet obligations and emergencies."
        else:
            return f"{base_interpretation}. Cash liquidity is very high, which may indicate excessive cash accumulation and inefficient investment of funds in profit-generating activities."

    def _generate_recommendations_ar(self, value: float, risk_level: RiskLevel) -> list:
        """Generate Arabic recommendations."""
        recommendations = []

        if value < 0.2:
            recommendations.extend([
                "زيادة الاحتياطي النقدي بشكل عاجل",
                "تحسين إدارة التدفق النقدي الداخل",
                "تسريع تحصيل المبيعات النقدية",
                "تأجيل المدفوعات غير الضرورية",
                "الحصول على تسهيلات ائتمانية فورية",
                "بيع الأصول غير الأساسية للحصول على نقدية",
                "إعادة تقييم سياسات الاستثمار قصير الأجل"
            ])
        elif 0.2 <= value < 0.4:
            recommendations.extend([
                "تحسين التخطيط للتدفق النقدي",
                "إنشاء صندوق طوارئ",
                "تحسين دورة التحصيل",
                "مراقبة النقدية اليومية"
            ])
        elif value > 0.8:
            recommendations.extend([
                "استثمار الفائض النقدي في أدوات مالية آمنة ومربحة",
                "تقييم فرص النمو والتوسع",
                "تحسين العائد على النقدية المتاحة",
                "النظر في شراء معدات أو تقنيات جديدة",
                "تقييم إمكانية زيادة توزيعات الأرباح",
                "الاستثمار في البحث والتطوير"
            ])

        return recommendations

    def _generate_recommendations_en(self, value: float, risk_level: RiskLevel) -> list:
        """Generate English recommendations."""
        recommendations = []

        if value < 0.2:
            recommendations.extend([
                "Increase cash reserves urgently",
                "Improve cash inflow management",
                "Accelerate cash sales collection",
                "Defer non-essential payments",
                "Obtain immediate credit facilities",
                "Sell non-core assets for cash",
                "Re-evaluate short-term investment policies"
            ])
        elif 0.2 <= value < 0.4:
            recommendations.extend([
                "Improve cash flow planning",
                "Establish emergency fund",
                "Enhance collection cycle",
                "Monitor daily cash position"
            ])
        elif value > 0.8:
            recommendations.extend([
                "Invest excess cash in safe and profitable financial instruments",
                "Evaluate growth and expansion opportunities",
                "Improve return on available cash",
                "Consider purchasing new equipment or technology",
                "Evaluate potential for increased dividend payments",
                "Invest in research and development"
            ])

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Create analysis instance
    analysis = CashRatioAnalysis()

    # Test data
    test_data = {
        'cash': 25000,
        'cash_equivalents': 15000,
        'marketable_securities': 10000,
        'current_liabilities': 100000
    }

    # Create benchmark data
    benchmark = BenchmarkData(
        industry_average=0.25,
        sector_average=0.30,
        market_average=0.28
    )

    # Run analysis
    result = analysis.run_full_analysis(test_data, benchmark)

    # Print results
    print(f"Cash Ratio: {result.value:.3f}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Performance Rating: {result.performance_rating}")
    print(f"Arabic Interpretation: {result.interpretation_ar}")
    print(f"English Interpretation: {result.interpretation_en}")
    print(f"Benchmark Comparison: {result.benchmark_comparison}")