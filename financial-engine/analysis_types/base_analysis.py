"""
Base Analysis Class for Financial Analysis Engine
قاعدة البيانات الأساسية لمحرك التحليل المالي

This module provides the foundational structure for all financial analysis types.
يوفر هذا الوحدة الهيكل الأساسي لجميع أنواع التحليل المالي.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import warnings
import math
import numpy as np
import pandas as pd
from datetime import datetime


class AnalysisCategory(Enum):
    """تصنيفات التحليل المالي - Financial Analysis Categories"""
    LIQUIDITY = "liquidity"
    PROFITABILITY = "profitability"
    EFFICIENCY = "efficiency"
    LEVERAGE = "leverage"
    MARKET_VALUATION = "market_valuation"
    GROWTH = "growth"
    CREDIT_RISK = "credit_risk"
    MARKET_RISK = "market_risk"
    OPERATIONAL_RISK = "operational_risk"
    VALUATION_ANALYSIS = "valuation_analysis"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    INDUSTRY_ANALYSIS = "industry_analysis"
    COMPARATIVE_ANALYSIS = "comparative_analysis"


class RiskLevel(Enum):
    """مستويات المخاطر - Risk Levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PerformanceRating(Enum):
    """تقييمات الأداء - Performance Ratings"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class AnalysisResult:
    """
    نتيجة التحليل المالي - Financial Analysis Result

    Contains the complete analysis output with all necessary components.
    يحتوي على مخرجات التحليل الكاملة مع جميع المكونات الضرورية.
    """
    value: float
    interpretation_ar: str
    interpretation_en: str
    risk_level: RiskLevel
    performance_rating: PerformanceRating
    industry_benchmark: Optional[float] = None
    benchmark_comparison: Optional[str] = None
    recommendations_ar: List[str] = None
    recommendations_en: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class BenchmarkData:
    """
    بيانات المعايير المرجعية - Benchmark Data

    Industry and sector benchmark information for comparison.
    معلومات المعايير المرجعية للصناعة والقطاع للمقارنة.
    """
    industry_average: Optional[float] = None
    sector_average: Optional[float] = None
    market_average: Optional[float] = None
    peer_group_average: Optional[float] = None
    historical_average: Optional[float] = None
    best_in_class: Optional[float] = None
    worst_in_class: Optional[float] = None


class BaseFinancialAnalysis(ABC):
    """
    الفئة الأساسية للتحليل المالي - Base Financial Analysis Class

    Abstract base class that defines the structure and common functionality
    for all financial analysis types.

    فئة أساسية مجردة تحدد الهيكل والوظائف المشتركة
    لجميع أنواع التحليل المالي.
    """

    def __init__(self,
                 name_ar: str,
                 name_en: str,
                 category: AnalysisCategory,
                 description_ar: str,
                 description_en: str):
        """
        Initialize the base analysis.
        تهيئة التحليل الأساسي.

        Args:
            name_ar: الاسم بالعربية - Arabic name
            name_en: الاسم بالإنجليزية - English name
            category: تصنيف التحليل - Analysis category
            description_ar: الوصف بالعربية - Arabic description
            description_en: الوصف بالإنجليزية - English description
        """
        self.name_ar = name_ar
        self.name_en = name_en
        self.category = category
        self.description_ar = description_ar
        self.description_en = description_en
        self.benchmark_data = BenchmarkData()

    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calculate the financial metric.
        حساب المؤشر المالي.

        Args:
            data: بيانات الشركة المالية - Company financial data

        Returns:
            float: قيمة المؤشر المحسوبة - Calculated metric value
        """
        pass

    @abstractmethod
    def interpret(self, value: float, benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        """
        Interpret the calculated result.
        تفسير النتيجة المحسوبة.

        Args:
            value: القيمة المحسوبة - Calculated value
            benchmark_data: بيانات المعايير المرجعية - Benchmark data

        Returns:
            AnalysisResult: نتيجة التحليل الكاملة - Complete analysis result
        """
        pass

    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate input data for required fields.
        التحقق من صحة البيانات المدخلة للحقول المطلوبة.

        Args:
            data: بيانات الإدخال - Input data
            required_fields: الحقول المطلوبة - Required fields

        Returns:
            bool: صحة البيانات - Data validity

        Raises:
            ValueError: في حالة عدم توفر الحقول المطلوبة - If required fields are missing
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        return True

    def handle_division_by_zero(self, numerator: float, denominator: float,
                               default_value: float = 0.0) -> float:
        """
        Handle division by zero safely.
        التعامل مع القسمة على صفر بأمان.

        Args:
            numerator: البسط - Numerator
            denominator: المقام - Denominator
            default_value: القيمة الافتراضية - Default value

        Returns:
            float: النتيجة أو القيمة الافتراضية - Result or default value
        """
        if denominator == 0 or math.isnan(denominator):
            warnings.warn(f"Division by zero in {self.name_en}. Using default value: {default_value}")
            return default_value
        return numerator / denominator

    def check_negative_values(self, values: Dict[str, float]) -> List[str]:
        """
        Check for negative values that might indicate data errors.
        فحص القيم السالبة التي قد تشير إلى أخطاء في البيانات.

        Args:
            values: القيم للفحص - Values to check

        Returns:
            List[str]: قائمة التحذيرات - List of warnings
        """
        warnings_list = []
        for key, value in values.items():
            if value < 0:
                warnings_list.append(f"Negative value detected for {key}: {value}")
        return warnings_list

    def format_percentage(self, value: float, decimal_places: int = 2) -> str:
        """
        Format value as percentage.
        تنسيق القيمة كنسبة مئوية.

        Args:
            value: القيمة - Value
            decimal_places: عدد المنازل العشرية - Decimal places

        Returns:
            str: القيمة منسقة كنسبة مئوية - Formatted percentage
        """
        return f"{value * 100:.{decimal_places}f}%"

    def format_currency(self, value: float, currency: str = "USD") -> str:
        """
        Format value as currency.
        تنسيق القيمة كعملة.

        Args:
            value: القيمة - Value
            currency: العملة - Currency

        Returns:
            str: القيمة منسقة كعملة - Formatted currency
        """
        return f"{currency} {value:,.2f}"

    def calculate_percentile_ranking(self, value: float, benchmark_values: List[float]) -> float:
        """
        Calculate percentile ranking against benchmark values.
        حساب الترتيب المئوي مقابل القيم المرجعية.

        Args:
            value: القيمة المحسوبة - Calculated value
            benchmark_values: القيم المرجعية - Benchmark values

        Returns:
            float: الترتيب المئوي - Percentile ranking
        """
        if not benchmark_values:
            return 50.0  # Default to median if no benchmarks

        sorted_values = sorted(benchmark_values)
        position = sum(1 for x in sorted_values if x <= value)
        return (position / len(sorted_values)) * 100

    def determine_risk_level(self, value: float, thresholds: Dict[str, float]) -> RiskLevel:
        """
        Determine risk level based on value and thresholds.
        تحديد مستوى المخاطر بناءً على القيمة والعتبات.

        Args:
            value: القيمة المحسوبة - Calculated value
            thresholds: عتبات المخاطر - Risk thresholds

        Returns:
            RiskLevel: مستوى المخاطر - Risk level
        """
        if value <= thresholds.get('very_high', float('inf')):
            return RiskLevel.VERY_HIGH
        elif value <= thresholds.get('high', float('inf')):
            return RiskLevel.HIGH
        elif value <= thresholds.get('moderate', float('inf')):
            return RiskLevel.MODERATE
        elif value <= thresholds.get('low', float('inf')):
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW

    def determine_performance_rating(self, value: float, benchmarks: Dict[str, float]) -> PerformanceRating:
        """
        Determine performance rating based on value and benchmarks.
        تحديد تقييم الأداء بناءً على القيمة والمعايير المرجعية.

        Args:
            value: القيمة المحسوبة - Calculated value
            benchmarks: المعايير المرجعية - Benchmarks

        Returns:
            PerformanceRating: تقييم الأداء - Performance rating
        """
        if value >= benchmarks.get('excellent', float('inf')):
            return PerformanceRating.EXCELLENT
        elif value >= benchmarks.get('good', float('inf')):
            return PerformanceRating.GOOD
        elif value >= benchmarks.get('average', float('inf')):
            return PerformanceRating.AVERAGE
        elif value >= benchmarks.get('poor', float('inf')):
            return PerformanceRating.POOR
        else:
            return PerformanceRating.CRITICAL

    def generate_benchmark_comparison(self, value: float, benchmark: float) -> str:
        """
        Generate benchmark comparison text.
        إنشاء نص مقارنة المعايير المرجعية.

        Args:
            value: القيمة المحسوبة - Calculated value
            benchmark: المعيار المرجعي - Benchmark value

        Returns:
            str: نص المقارنة - Comparison text
        """
        if benchmark is None:
            return "No benchmark available for comparison"

        percentage_diff = ((value - benchmark) / benchmark) * 100 if benchmark != 0 else 0

        if percentage_diff > 0:
            return f"Above industry average by {abs(percentage_diff):.1f}%"
        elif percentage_diff < 0:
            return f"Below industry average by {abs(percentage_diff):.1f}%"
        else:
            return "At industry average"

    def run_full_analysis(self, data: Dict[str, Any],
                         benchmark_data: Optional[BenchmarkData] = None) -> AnalysisResult:
        """
        Run complete analysis including calculation and interpretation.
        تشغيل التحليل الكامل بما في ذلك الحساب والتفسير.

        Args:
            data: بيانات الشركة المالية - Company financial data
            benchmark_data: بيانات المعايير المرجعية - Benchmark data

        Returns:
            AnalysisResult: نتيجة التحليل الكاملة - Complete analysis result
        """
        try:
            # Calculate the metric
            value = self.calculate(data)

            # Interpret the result
            result = self.interpret(value, benchmark_data)

            # Add metadata
            result.metadata = {
                'analysis_name_ar': self.name_ar,
                'analysis_name_en': self.name_en,
                'category': self.category.value,
                'calculation_date': datetime.now().isoformat(),
                'data_fields_used': list(data.keys())
            }

            return result

        except Exception as e:
            # Return error result
            return AnalysisResult(
                value=float('nan'),
                interpretation_ar=f"خطأ في التحليل: {str(e)}",
                interpretation_en=f"Analysis error: {str(e)}",
                risk_level=RiskLevel.VERY_HIGH,
                performance_rating=PerformanceRating.CRITICAL,
                warnings=[f"Calculation failed: {str(e)}"],
                metadata={'error': True, 'error_message': str(e)}
            )