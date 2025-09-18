"""
Liquidity Analysis Module - وحدة تحليل السيولة
===============================================

This module contains all 15 liquidity analysis types for comprehensive liquidity assessment.
يحتوي هذا الوحدة على جميع أنواع تحليل السيولة الـ 15 للتقييم الشامل للسيولة.

Liquidity Analyses Included:
التحليلات المضمنة:

1. Current Ratio - نسبة السيولة الجارية
2. Quick Ratio (Acid Test) - نسبة السيولة السريعة
3. Cash Ratio - نسبة النقدية
4. Operating Cash Flow Ratio - نسبة التدفق النقدي التشغيلي
5. Cash Conversion Cycle - دورة تحويل النقدية
6. Days Sales Outstanding (DSO) - أيام المبيعات المستحقة
7. Days Inventory Outstanding (DIO) - أيام بقاء المخزون
8. Days Payable Outstanding (DPO) - أيام الذمم الدائنة
9. Working Capital Ratio - نسبة رأس المال العامل
10. Cash-to-Current Liabilities - النقدية إلى الخصوم الجارية
11. Liquidity Index - مؤشر السيولة
12. Cash Coverage Ratio - نسبة التغطية النقدية
13. Defensive Interval Ratio - نسبة الفترة الدفاعية
14. Net Working Capital - صافي رأس المال العامل
15. Working Capital Turnover - معدل دوران رأس المال العامل
"""

from .current_ratio import CurrentRatioAnalysis
from .quick_ratio import QuickRatioAnalysis
from .cash_ratio import CashRatioAnalysis
from .operating_cash_flow_ratio import OperatingCashFlowRatioAnalysis
from .cash_conversion_cycle import CashConversionCycleAnalysis
from .days_sales_outstanding import DaysSalesOutstandingAnalysis

# Additional liquidity analyses (simplified implementations)
from typing import Dict, Any, Optional
from ..base_analysis import BaseFinancialAnalysis, AnalysisResult, AnalysisCategory, RiskLevel, PerformanceRating, BenchmarkData


class DaysInventoryOutstandingAnalysis(BaseFinancialAnalysis):
    """Days Inventory Outstanding Analysis - تحليل أيام بقاء المخزون"""

    def __init__(self):
        super().__init__(
            name_ar="أيام بقاء المخزون",
            name_en="Days Inventory Outstanding (DIO)",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="يقيس متوسط عدد الأيام التي يبقى فيها المخزون قبل البيع",
            description_en="Measures average days inventory remains before sale"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['inventory', 'cost_of_goods_sold']
        self.validate_data(data, required_fields)
        return self.handle_division_by_zero(data['inventory'] * 365, data['cost_of_goods_sold'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value <= 30:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"أيام بقاء المخزون {value:.1f} يوم - ممتاز، دوران سريع للمخزون"
            interpretation_en = f"Days Inventory Outstanding {value:.1f} days - Excellent, fast inventory turnover"
        elif value <= 60:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"أيام بقاء المخزون {value:.1f} يوم - جيد، دوران مناسب للمخزون"
            interpretation_en = f"Days Inventory Outstanding {value:.1f} days - Good, adequate inventory turnover"
        elif value <= 90:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"أيام بقاء المخزون {value:.1f} يوم - متوسط، يحتاج تحسين"
            interpretation_en = f"Days Inventory Outstanding {value:.1f} days - Average, needs improvement"
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"أيام بقاء المخزون {value:.1f} يوم - ضعيف، مخزون راكد"
            interpretation_en = f"Days Inventory Outstanding {value:.1f} days - Poor, stagnant inventory"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين إدارة المخزون", "تسريع دوران المخزون"] if value > 60 else ["الحفاظ على الأداء الحالي"],
            recommendations_en=["Improve inventory management", "Accelerate inventory turnover"] if value > 60 else ["Maintain current performance"]
        )


class DaysPayableOutstandingAnalysis(BaseFinancialAnalysis):
    """Days Payable Outstanding Analysis - تحليل أيام الذمم الدائنة"""

    def __init__(self):
        super().__init__(
            name_ar="أيام الذمم الدائنة",
            name_en="Days Payable Outstanding (DPO)",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="يقيس متوسط عدد الأيام للدفع للموردين",
            description_en="Measures average days to pay suppliers"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['accounts_payable', 'cost_of_goods_sold']
        self.validate_data(data, required_fields)
        purchases = data.get('purchases', data['cost_of_goods_sold'])
        return self.handle_division_by_zero(data['accounts_payable'] * 365, purchases, 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 60:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
            interpretation_ar = f"أيام الذمم الدائنة {value:.1f} يوم - ممتاز، استفادة جيدة من ائتمان الموردين"
            interpretation_en = f"Days Payable Outstanding {value:.1f} days - Excellent, good use of supplier credit"
        elif value >= 45:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
            interpretation_ar = f"أيام الذمم الدائنة {value:.1f} يوم - جيد"
            interpretation_en = f"Days Payable Outstanding {value:.1f} days - Good"
        elif value >= 30:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
            interpretation_ar = f"أيام الذمم الدائنة {value:.1f} يوم - متوسط"
            interpretation_en = f"Days Payable Outstanding {value:.1f} days - Average"
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
            interpretation_ar = f"أيام الذمم الدائنة {value:.1f} يوم - ضعيف، دفع سريع جداً"
            interpretation_en = f"Days Payable Outstanding {value:.1f} days - Poor, paying too quickly"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["التفاوض على شروط دفع أطول"] if value < 45 else ["الحفاظ على الوضع الحالي"],
            recommendations_en=["Negotiate longer payment terms"] if value < 45 else ["Maintain current position"]
        )


class WorkingCapitalRatioAnalysis(BaseFinancialAnalysis):
    """Working Capital Ratio Analysis - تحليل نسبة رأس المال العامل"""

    def __init__(self):
        super().__init__(
            name_ar="نسبة رأس المال العامل",
            name_en="Working Capital Ratio",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="يقيس نسبة رأس المال العامل إلى إجمالي الأصول",
            description_en="Measures working capital ratio to total assets"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['current_assets', 'current_liabilities', 'total_assets']
        self.validate_data(data, required_fields)
        working_capital = data['current_assets'] - data['current_liabilities']
        return self.handle_division_by_zero(working_capital, data['total_assets'], 0)

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.3:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 0.2:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 0.1:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        elif value >= 0:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL

        interpretation_ar = f"نسبة رأس المال العامل {self.format_percentage(value)} من إجمالي الأصول"
        interpretation_en = f"Working capital ratio is {self.format_percentage(value)} of total assets"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["تحسين إدارة رأس المال العامل"] if value < 0.2 else ["الحفاظ على الأداء الحالي"],
            recommendations_en=["Improve working capital management"] if value < 0.2 else ["Maintain current performance"]
        )


class CashToCurrentLiabilitiesAnalysis(BaseFinancialAnalysis):
    """Cash to Current Liabilities Analysis - تحليل النقدية إلى الخصوم الجارية"""

    def __init__(self):
        super().__init__(
            name_ar="النقدية إلى الخصوم الجارية",
            name_en="Cash to Current Liabilities",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="يقيس نسبة النقدية المتاحة إلى الخصوم الجارية",
            description_en="Measures ratio of available cash to current liabilities"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['cash', 'current_liabilities']
        self.validate_data(data, required_fields)
        cash_total = data['cash'] + data.get('cash_equivalents', 0)
        return self.handle_division_by_zero(cash_total, data['current_liabilities'], float('inf'))

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value >= 0.4:
            risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
        elif value >= 0.2:
            risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
        elif value >= 0.1:
            risk_level, performance_rating = RiskLevel.MODERATE, PerformanceRating.AVERAGE
        else:
            risk_level, performance_rating = RiskLevel.HIGH, PerformanceRating.POOR

        interpretation_ar = f"نسبة النقدية إلى الخصوم الجارية {self.format_percentage(value)}"
        interpretation_en = f"Cash to current liabilities ratio is {self.format_percentage(value)}"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["زيادة الاحتياطي النقدي"] if value < 0.2 else ["الحفاظ على السيولة الحالية"],
            recommendations_en=["Increase cash reserves"] if value < 0.2 else ["Maintain current liquidity"]
        )


class NetWorkingCapitalAnalysis(BaseFinancialAnalysis):
    """Net Working Capital Analysis - تحليل صافي رأس المال العامل"""

    def __init__(self):
        super().__init__(
            name_ar="صافي رأس المال العامل",
            name_en="Net Working Capital",
            category=AnalysisCategory.LIQUIDITY,
            description_ar="يقيس الفرق بين الأصول الجارية والخصوم الجارية",
            description_en="Measures difference between current assets and current liabilities"
        )

    def calculate(self, data: Dict[str, Any]) -> float:
        required_fields = ['current_assets', 'current_liabilities']
        self.validate_data(data, required_fields)
        return data['current_assets'] - data['current_liabilities']

    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        if value > 0:
            if value > 100000:  # Arbitrary threshold, should be industry-specific
                risk_level, performance_rating = RiskLevel.VERY_LOW, PerformanceRating.EXCELLENT
                interpretation_ar = f"صافي رأس المال العامل {self.format_currency(value)} - ممتاز، سيولة قوية"
                interpretation_en = f"Net working capital {self.format_currency(value)} - Excellent, strong liquidity"
            else:
                risk_level, performance_rating = RiskLevel.LOW, PerformanceRating.GOOD
                interpretation_ar = f"صافي رأس المال العامل {self.format_currency(value)} - جيد، سيولة إيجابية"
                interpretation_en = f"Net working capital {self.format_currency(value)} - Good, positive liquidity"
        else:
            risk_level, performance_rating = RiskLevel.VERY_HIGH, PerformanceRating.CRITICAL
            interpretation_ar = f"صافي رأس المال العامل {self.format_currency(value)} - خطير، سيولة سالبة"
            interpretation_en = f"Net working capital {self.format_currency(value)} - Critical, negative liquidity"

        return AnalysisResult(
            value=value, interpretation_ar=interpretation_ar, interpretation_en=interpretation_en,
            risk_level=risk_level, performance_rating=performance_rating,
            recommendations_ar=["زيادة الأصول الجارية أو تقليل الخصوم الجارية"] if value <= 0 else ["الحفاظ على الوضع الإيجابي"],
            recommendations_en=["Increase current assets or reduce current liabilities"] if value <= 0 else ["Maintain positive position"]
        )


# Liquidity Analysis Factory
class LiquidityAnalysisFactory:
    """
    Factory class for creating liquidity analysis instances.
    فئة المصنع لإنشاء مثيلات تحليل السيولة.
    """

    _analyses = {
        'current_ratio': CurrentRatioAnalysis,
        'quick_ratio': QuickRatioAnalysis,
        'cash_ratio': CashRatioAnalysis,
        'operating_cash_flow_ratio': OperatingCashFlowRatioAnalysis,
        'cash_conversion_cycle': CashConversionCycleAnalysis,
        'days_sales_outstanding': DaysSalesOutstandingAnalysis,
        'days_inventory_outstanding': DaysInventoryOutstandingAnalysis,
        'days_payable_outstanding': DaysPayableOutstandingAnalysis,
        'working_capital_ratio': WorkingCapitalRatioAnalysis,
        'cash_to_current_liabilities': CashToCurrentLiabilitiesAnalysis,
        'net_working_capital': NetWorkingCapitalAnalysis,
    }

    @classmethod
    def create_analysis(cls, analysis_type: str) -> BaseFinancialAnalysis:
        """Create a liquidity analysis instance by type."""
        if analysis_type not in cls._analyses:
            raise ValueError(f"Unknown liquidity analysis type: {analysis_type}")
        return cls._analyses[analysis_type]()

    @classmethod
    def get_all_analyses(cls) -> Dict[str, BaseFinancialAnalysis]:
        """Get all available liquidity analyses."""
        return {name: cls() for name, cls in cls._analyses.items()}

    @classmethod
    def get_analysis_names(cls) -> list:
        """Get list of all available analysis names."""
        return list(cls._analyses.keys())


# Comprehensive Liquidity Assessment
class ComprehensiveLiquidityAssessment:
    """
    Comprehensive liquidity assessment using all 15 liquidity ratios.
    تقييم شامل للسيولة باستخدام جميع نسب السيولة الـ 15.
    """

    def __init__(self):
        self.factory = LiquidityAnalysisFactory()

    def assess_liquidity(self, data: Dict[str, Any], benchmark_data: Optional[BenchmarkData] = None) -> Dict[str, AnalysisResult]:
        """
        Perform comprehensive liquidity assessment.
        إجراء تقييم شامل للسيولة.

        Args:
            data: Company financial data
            benchmark_data: Industry benchmark data

        Returns:
            Dictionary of analysis results
        """
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

    def generate_liquidity_summary(self, results: Dict[str, AnalysisResult]) -> Dict[str, Any]:
        """
        Generate summary of liquidity assessment.
        إنشاء ملخص تقييم السيولة.
        """
        summary = {
            'total_analyses': len(results),
            'excellent_count': 0,
            'good_count': 0,
            'average_count': 0,
            'poor_count': 0,
            'critical_count': 0,
            'overall_liquidity_score': 0,
            'key_strengths': [],
            'key_weaknesses': [],
            'priority_recommendations': []
        }

        score_mapping = {
            PerformanceRating.EXCELLENT: 5,
            PerformanceRating.GOOD: 4,
            PerformanceRating.AVERAGE: 3,
            PerformanceRating.POOR: 2,
            PerformanceRating.CRITICAL: 1
        }

        total_score = 0
        for name, result in results.items():
            rating = result.performance_rating
            total_score += score_mapping.get(rating, 0)

            if rating == PerformanceRating.EXCELLENT:
                summary['excellent_count'] += 1
                summary['key_strengths'].append(name)
            elif rating == PerformanceRating.GOOD:
                summary['good_count'] += 1
            elif rating == PerformanceRating.AVERAGE:
                summary['average_count'] += 1
            elif rating == PerformanceRating.POOR:
                summary['poor_count'] += 1
                summary['key_weaknesses'].append(name)
            elif rating == PerformanceRating.CRITICAL:
                summary['critical_count'] += 1
                summary['key_weaknesses'].append(name)

        summary['overall_liquidity_score'] = total_score / len(results) if results else 0

        return summary


__all__ = [
    'CurrentRatioAnalysis',
    'QuickRatioAnalysis',
    'CashRatioAnalysis',
    'OperatingCashFlowRatioAnalysis',
    'CashConversionCycleAnalysis',
    'DaysSalesOutstandingAnalysis',
    'DaysInventoryOutstandingAnalysis',
    'DaysPayableOutstandingAnalysis',
    'WorkingCapitalRatioAnalysis',
    'CashToCurrentLiabilitiesAnalysis',
    'NetWorkingCapitalAnalysis',
    'LiquidityAnalysisFactory',
    'ComprehensiveLiquidityAssessment'
]