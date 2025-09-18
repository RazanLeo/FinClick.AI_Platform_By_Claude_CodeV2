"""
Days Sales Outstanding Analysis - أيام المبيعات المستحقة
=====================================================

This module implements Days Sales Outstanding (DSO) analysis.
يطبق هذا الوحدة تحليل أيام المبيعات المستحقة.

DSO measures the average number of days to collect receivables.
يقيس متوسط عدد الأيام لتحصيل الذمم المدينة.

Formula: DSO = (Accounts Receivable / Revenue) × 365
الصيغة: أيام المبيعات المستحقة = (الذمم المدينة / الإيرادات) × 365
"""

from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class DaysSalesOutstandingAnalysis(BaseFinancialAnalysis):
    """Days Sales Outstanding Analysis - تحليل أيام المبيعات المستحقة"""

    def __init__(self):
        super().__init__(
            name_ar="أيام المبيعات المستحقة",
            name_en="Days Sales Outstanding (DSO)",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="يقيس متوسط عدد الأيام اللازمة لتحصيل الذمم المدينة",
            description_en="Measures average number of days to collect accounts receivable"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['accounts_receivable', 'revenue']
        self.validate_data(data, required_fields)
        
        accounts_receivable = data['accounts_receivable']
        revenue = data['revenue']
        
        return self.handle_division_by_zero(accounts_receivable * 365, revenue, 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        # Shorter DSO is better
        if value <= 30:
            risk_level = RiskLevel.VERY_LOW
            performance_rating = PerformanceRating.EXCELLENT
        elif value <= 45:
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

        interpretation_ar = f"أيام المبيعات المستحقة {value:.1f} يوم. "
        interpretation_en = f"Days Sales Outstanding is {value:.1f} days. "
        
        if value <= 30:
            interpretation_ar += "ممتاز - تحصيل سريع جداً"
            interpretation_en += "Excellent - very fast collection"
        elif value > 90:
            interpretation_ar += "ضعيف - تحصيل بطيء يؤثر على السيولة"
            interpretation_en += "Poor - slow collection affecting liquidity"
        else:
            interpretation_ar += "مقبول - يمكن تحسينه"
            interpretation_en += "Acceptable - can be improved"

        recommendations_ar = ["تحسين سياسات التحصيل", "مراجعة شروط الائتمان"] if value > 45 else ["الحفاظ على الأداء الحالي"]
        recommendations_en = ["Improve collection policies", "Review credit terms"] if value > 45 else ["Maintain current performance"]

        return AnalysisResult(
            value=value,
            interpretation_ar=interpretation_ar,
            interpretation_en=interpretation_en,
            risk_level=risk_level,
            performance_rating=performance_rating,
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en
        )


if __name__ == "__main__":
    analysis = DaysSalesOutstandingAnalysis()
    test_data = {'accounts_receivable': 50000, 'revenue': 600000}
    result = analysis.run_full_analysis(test_data)
    print(f"DSO: {result.value:.1f} days - {result.performance_rating}")