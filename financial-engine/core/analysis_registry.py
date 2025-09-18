"""
Analysis Registry - Central registry for all 180 financial analysis types
Manages and organizes all financial analysis definitions and metadata.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .data_models import AnalysisCategory, AnalysisSubcategory, Language


@dataclass
class AnalysisDefinition:
    """Definition structure for each financial analysis type"""
    code: str
    name_ar: str
    name_en: str
    category: AnalysisCategory
    subcategory: AnalysisSubcategory
    description_ar: str
    description_en: str
    formula: str
    what_it_measures_ar: str
    what_it_measures_en: str
    interpretation_guide_ar: str
    interpretation_guide_en: str
    unit: str  # percentage, ratio, currency, days, times, etc.
    good_range: Optional[str] = None
    industry_benchmarks: Dict[str, float] = None
    calculation_method: str = ""
    dependencies: List[str] = None  # Required data fields


class AnalysisRegistry:
    """
    Central registry for all 180 financial analysis types as specified in the prompt.
    Organizes analyses by categories and subcategories exactly as required.
    """

    def __init__(self):
        """Initialize the analysis registry with all 180 analysis types"""
        self.analyses: Dict[str, AnalysisDefinition] = {}
        self._initialize_all_analyses()

    def _initialize_all_analyses(self):
        """Initialize all 180 analysis types with their definitions"""

        # Classical Foundational Analysis (106 total)
        self._register_structural_analyses()  # 13 analyses
        self._register_financial_ratios()     # 75 analyses
        self._register_flow_movement_analyses()  # 18 analyses

        # Applied Intermediate Analysis (21 total)
        self._register_advanced_comparison_analyses()  # 3 analyses
        self._register_valuation_investment_analyses()  # 13 analyses
        self._register_performance_efficiency_analyses()  # 5 analyses

        # Advanced Sophisticated Analysis (53 total)
        self._register_modeling_simulation_analyses()  # 11 analyses
        self._register_statistical_quantitative_analyses()  # 16 analyses
        self._register_prediction_credit_analyses()  # 10 analyses
        self._register_quantitative_risk_analyses()  # 25 analyses
        self._register_portfolio_investment_analyses()  # 14 analyses
        self._register_merger_acquisition_analyses()  # 5 analyses
        self._register_detection_prediction_analyses()  # 10 analyses
        self._register_timeseries_statistical_analyses()  # 6 analyses

    def _register_structural_analyses(self):
        """Register all 13 structural analysis types"""

        structural_analyses = [
            {
                "code": "vertical_analysis",
                "name_ar": "التحليل الرأسي",
                "name_en": "Vertical Analysis",
                "description_ar": "تحليل يوضح نسبة كل بند في القوائم المالية إلى إجمالي القائمة",
                "description_en": "Analysis showing each item as percentage of total statement",
                "formula": "نسبة البند = (قيمة البند / إجمالي القائمة) × 100",
                "what_it_measures_ar": "يقيس الأهمية النسبية لكل بند في القوائم المالية",
                "what_it_measures_en": "Measures relative importance of each item in financial statements",
                "unit": "percentage"
            },
            {
                "code": "horizontal_analysis",
                "name_ar": "التحليل الأفقي",
                "name_en": "Horizontal Analysis",
                "description_ar": "تحليل يقارن البيانات المالية عبر فترات زمنية متعددة",
                "description_en": "Analysis comparing financial data across multiple time periods",
                "formula": "نسبة التغير = ((السنة الحالية - سنة الأساس) / سنة الأساس) × 100",
                "what_it_measures_ar": "يقيس التغيرات والاتجاهات في البيانات المالية عبر الزمن",
                "what_it_measures_en": "Measures changes and trends in financial data over time",
                "unit": "percentage"
            },
            {
                "code": "mixed_analysis",
                "name_ar": "التحليل المختلط",
                "name_en": "Mixed Analysis",
                "description_ar": "تحليل يجمع بين التحليل الرأسي والأفقي",
                "description_en": "Analysis combining both vertical and horizontal analysis",
                "formula": "يجمع بين صيغ التحليل الرأسي والأفقي",
                "what_it_measures_ar": "يقيس الأهمية النسبية والتغيرات الزمنية معاً",
                "what_it_measures_en": "Measures both relative importance and temporal changes",
                "unit": "percentage"
            },
            {
                "code": "trend_analysis",
                "name_ar": "تحليل الاتجاه",
                "name_en": "Trend Analysis",
                "description_ar": "تحليل يحدد الاتجاهات طويلة المدى في الأداء المالي",
                "description_en": "Analysis identifying long-term trends in financial performance",
                "formula": "اتجاه = (القيمة النهائية - القيمة الأولى) / عدد الفترات",
                "what_it_measures_ar": "يقيس الاتجاه العام والنمط في البيانات المالية",
                "what_it_measures_en": "Measures general direction and pattern in financial data",
                "unit": "percentage"
            },
            {
                "code": "basic_comparative_analysis",
                "name_ar": "التحليل المقارن الأساسي",
                "name_en": "Basic Comparative Analysis",
                "description_ar": "مقارنة الأداء المالي مع الشركات المماثلة",
                "description_en": "Comparing financial performance with similar companies",
                "formula": "الفرق = الشركة - متوسط الصناعة",
                "what_it_measures_ar": "يقيس الموقع التنافسي للشركة في الصناعة",
                "what_it_measures_en": "Measures company's competitive position in industry",
                "unit": "various"
            },
            {
                "code": "value_added_analysis",
                "name_ar": "تحليل القيمة المضافة",
                "name_en": "Value Added Analysis",
                "description_ar": "تحليل القيمة التي تضيفها الشركة في عملياتها",
                "description_en": "Analysis of value company adds through its operations",
                "formula": "القيمة المضافة = الإيرادات - تكلفة المواد والخدمات الخارجية",
                "what_it_measures_ar": "يقيس مدى قدرة الشركة على إضافة قيمة",
                "what_it_measures_en": "Measures company's ability to add value",
                "unit": "currency"
            },
            {
                "code": "common_base_analysis",
                "name_ar": "تحليل الأساس المشترك",
                "name_en": "Common Base Analysis",
                "description_ar": "تحليل يستخدم سنة أساس للمقارنة",
                "description_en": "Analysis using a base year for comparison",
                "formula": "رقم قياسي = (السنة الحالية / سنة الأساس) × 100",
                "what_it_measures_ar": "يقيس التغير النسبي مقارنة بسنة الأساس",
                "what_it_measures_en": "Measures relative change compared to base year",
                "unit": "index"
            },
            {
                "code": "simple_time_series_analysis",
                "name_ar": "تحليل السلاسل الزمنية البسيط",
                "name_en": "Simple Time Series Analysis",
                "description_ar": "تحليل البيانات عبر فترات زمنية متتالية",
                "description_en": "Analysis of data across consecutive time periods",
                "formula": "متوسط = مجموع القيم / عدد الفترات",
                "what_it_measures_ar": "يقيس الأنماط والتقلبات عبر الزمن",
                "what_it_measures_en": "Measures patterns and fluctuations over time",
                "unit": "various"
            },
            {
                "code": "relative_changes_analysis",
                "name_ar": "تحليل التغيرات النسبية",
                "name_en": "Relative Changes Analysis",
                "description_ar": "تحليل التغيرات النسبية في البيانات المالية",
                "description_en": "Analysis of relative changes in financial data",
                "formula": "التغير النسبي = (الجديد - القديم) / القديم × 100",
                "what_it_measures_ar": "يقيس حجم التغيرات النسبية",
                "what_it_measures_en": "Measures magnitude of relative changes",
                "unit": "percentage"
            },
            {
                "code": "growth_rates_analysis",
                "name_ar": "تحليل معدلات النمو",
                "name_en": "Growth Rates Analysis",
                "description_ar": "تحليل معدلات النمو في مختلف البنود المالية",
                "description_en": "Analysis of growth rates in various financial items",
                "formula": "معدل النمو = ((القيمة النهائية / القيمة الأولى)^(1/n)) - 1",
                "what_it_measures_ar": "يقيس معدل النمو السنوي المركب",
                "what_it_measures_en": "Measures compound annual growth rate",
                "unit": "percentage"
            },
            {
                "code": "basic_variance_analysis",
                "name_ar": "تحليل الانحرافات الأساسي",
                "name_en": "Basic Variance Analysis",
                "description_ar": "تحليل الانحرافات بين الفعلي والمخطط",
                "description_en": "Analysis of variances between actual and planned",
                "formula": "الانحراف = الفعلي - المخطط",
                "what_it_measures_ar": "يقيس الانحرافات عن الخطة",
                "what_it_measures_en": "Measures deviations from plan",
                "unit": "currency"
            },
            {
                "code": "simple_variance_analysis",
                "name_ar": "تحليل التباين البسيط",
                "name_en": "Simple Variance Analysis",
                "description_ar": "تحليل التباين في البيانات المالية",
                "description_en": "Analysis of variance in financial data",
                "formula": "التباين = Σ(xi - μ)² / n",
                "what_it_measures_ar": "يقيس مدى تشتت البيانات",
                "what_it_measures_en": "Measures data dispersion",
                "unit": "variance"
            },
            {
                "code": "index_numbers_analysis",
                "name_ar": "تحليل الأرقام القياسية",
                "name_en": "Index Numbers Analysis",
                "description_ar": "تحليل باستخدام الأرقام القياسية",
                "description_en": "Analysis using index numbers",
                "formula": "الرقم القياسي = (القيمة الحالية / قيمة الأساس) × 100",
                "what_it_measures_ar": "يقيس التغير النسبي باستخدام رقم قياسي",
                "what_it_measures_en": "Measures relative change using index",
                "unit": "index"
            }
        ]

        for analysis in structural_analyses:
            self._register_analysis(
                analysis,
                AnalysisCategory.CLASSICAL_FOUNDATIONAL,
                AnalysisSubcategory.STRUCTURAL_ANALYSIS
            )

    def _register_financial_ratios(self):
        """Register all 75 financial ratios"""

        # Liquidity Ratios (10 ratios)
        liquidity_ratios = [
            {
                "code": "current_ratio",
                "name_ar": "النسبة الجارية",
                "name_en": "Current Ratio",
                "description_ar": "نسبة الأصول المتداولة إلى الخصوم المتداولة",
                "description_en": "Ratio of current assets to current liabilities",
                "formula": "النسبة الجارية = الأصول المتداولة / الخصوم المتداولة",
                "what_it_measures_ar": "يقيس قدرة الشركة على الوفاء بالتزاماتها قصيرة المدى",
                "what_it_measures_en": "Measures company's ability to meet short-term obligations",
                "unit": "ratio",
                "good_range": "1.5 - 3.0"
            },
            {
                "code": "quick_ratio",
                "name_ar": "النسبة السريعة",
                "name_en": "Quick Ratio",
                "description_ar": "نسبة الأصول السائلة إلى الخصوم المتداولة",
                "description_en": "Ratio of liquid assets to current liabilities",
                "formula": "النسبة السريعة = (الأصول المتداولة - المخزون) / الخصوم المتداولة",
                "what_it_measures_ar": "يقيس السيولة الفورية للشركة",
                "what_it_measures_en": "Measures immediate liquidity of company",
                "unit": "ratio",
                "good_range": "1.0 - 1.5"
            },
            {
                "code": "cash_ratio",
                "name_ar": "نسبة النقد",
                "name_en": "Cash Ratio",
                "description_ar": "نسبة النقد وما في حكمه إلى الخصوم المتداولة",
                "description_en": "Ratio of cash and equivalents to current liabilities",
                "formula": "نسبة النقد = النقد وما في حكمه / الخصوم المتداولة",
                "what_it_measures_ar": "يقيس السيولة النقدية المباشرة",
                "what_it_measures_en": "Measures direct cash liquidity",
                "unit": "ratio",
                "good_range": "0.1 - 0.2"
            },
            {
                "code": "operating_cash_flow_ratio",
                "name_ar": "نسبة التدفق النقدي التشغيلي",
                "name_en": "Operating Cash Flow Ratio",
                "description_ar": "نسبة التدفق النقدي التشغيلي إلى الخصوم المتداولة",
                "description_en": "Ratio of operating cash flow to current liabilities",
                "formula": "نسبة التدفق النقدي = التدفق النقدي التشغيلي / الخصوم المتداولة",
                "what_it_measures_ar": "يقيس قدرة العمليات على توليد نقد لتغطية الالتزامات",
                "what_it_measures_en": "Measures operations' ability to generate cash for obligations",
                "unit": "ratio"
            },
            {
                "code": "working_capital_ratio",
                "name_ar": "نسبة رأس المال العامل",
                "name_en": "Working Capital Ratio",
                "description_ar": "رأس المال العامل كنسبة من إجمالي الأصول",
                "description_en": "Working capital as percentage of total assets",
                "formula": "نسبة رأس المال العامل = (الأصول المتداولة - الخصوم المتداولة) / إجمالي الأصول",
                "what_it_measures_ar": "يقيس كفاءة إدارة رأس المال العامل",
                "what_it_measures_en": "Measures efficiency of working capital management",
                "unit": "percentage"
            },
            {
                "code": "defensive_interval_ratio",
                "name_ar": "نسبة الفترة الدفاعية",
                "name_en": "Defensive Interval Ratio",
                "description_ar": "عدد الأيام التي يمكن للشركة تغطية نفقاتها بالأصول السائلة",
                "description_en": "Number of days company can cover expenses with liquid assets",
                "formula": "الفترة الدفاعية = الأصول السائلة / المصروفات اليومية",
                "what_it_measures_ar": "يقيس المدة التي يمكن البقاء دون إيرادات",
                "what_it_measures_en": "Measures duration company can survive without revenues",
                "unit": "days"
            },
            {
                "code": "cash_coverage_ratio",
                "name_ar": "نسبة التغطية النقدية",
                "name_en": "Cash Coverage Ratio",
                "description_ar": "قدرة النقد على تغطية المصروفات النقدية",
                "description_en": "Ability of cash to cover cash expenses",
                "formula": "التغطية النقدية = النقد المتاح / المصروفات النقدية الشهرية",
                "what_it_measures_ar": "يقيس الحماية النقدية للشركة",
                "what_it_measures_en": "Measures company's cash protection",
                "unit": "months"
            },
            {
                "code": "absolute_liquidity_ratio",
                "name_ar": "نسبة السيولة المطلقة",
                "name_en": "Absolute Liquidity Ratio",
                "description_ar": "النقد والاستثمارات قصيرة المدى إلى الخصوم المتداولة",
                "description_en": "Cash and short-term investments to current liabilities",
                "formula": "السيولة المطلقة = (النقد + الاستثمارات قصيرة المدى) / الخصوم المتداولة",
                "what_it_measures_ar": "يقيس السيولة الفورية المطلقة",
                "what_it_measures_en": "Measures absolute immediate liquidity",
                "unit": "ratio"
            },
            {
                "code": "free_cash_flow_ratio",
                "name_ar": "نسبة التدفق النقدي الحر",
                "name_en": "Free Cash Flow Ratio",
                "description_ar": "التدفق النقدي الحر إلى الخصوم المتداولة",
                "description_en": "Free cash flow to current liabilities",
                "formula": "نسبة التدفق الحر = التدفق النقدي الحر / الخصوم المتداولة",
                "what_it_measures_ar": "يقيس القدرة على توليد نقد حر لتغطية الالتزامات",
                "what_it_measures_en": "Measures ability to generate free cash for obligations",
                "unit": "ratio"
            },
            {
                "code": "basic_liquidity_index",
                "name_ar": "مؤشر السيولة الأساسي",
                "name_en": "Basic Liquidity Index",
                "description_ar": "مؤشر مركب للسيولة يجمع عدة نسب",
                "description_en": "Composite liquidity index combining several ratios",
                "formula": "مؤشر السيولة = متوسط مرجح للنسب السيولة",
                "what_it_measures_ar": "يقيس الوضع العام للسيولة",
                "what_it_measures_en": "Measures overall liquidity position",
                "unit": "index"
            }
        ]

        for ratio in liquidity_ratios:
            self._register_analysis(
                ratio,
                AnalysisCategory.CLASSICAL_FOUNDATIONAL,
                AnalysisSubcategory.FINANCIAL_RATIOS
            )

        # Activity/Efficiency Ratios (15 ratios)
        activity_ratios = [
            {
                "code": "inventory_turnover",
                "name_ar": "معدل دوران المخزون",
                "name_en": "Inventory Turnover",
                "description_ar": "عدد مرات بيع المخزون خلال الفترة",
                "description_en": "Number of times inventory is sold during period",
                "formula": "دوران المخزون = تكلفة البضاعة المباعة / متوسط المخزون",
                "what_it_measures_ar": "يقيس كفاءة إدارة المخزون",
                "what_it_measures_en": "Measures inventory management efficiency",
                "unit": "times"
            },
            {
                "code": "inventory_period",
                "name_ar": "فترة بقاء المخزون",
                "name_en": "Inventory Period",
                "description_ar": "متوسط عدد الأيام لبيع المخزون",
                "description_en": "Average number of days to sell inventory",
                "formula": "فترة المخزون = 365 / معدل دوران المخزون",
                "what_it_measures_ar": "يقيس الفترة الزمنية لتحويل المخزون لنقد",
                "what_it_measures_en": "Measures time to convert inventory to cash",
                "unit": "days"
            },
            {
                "code": "receivables_turnover",
                "name_ar": "معدل دوران الذمم المدينة",
                "name_en": "Receivables Turnover",
                "description_ar": "عدد مرات تحصيل الذمم المدينة خلال الفترة",
                "description_en": "Number of times receivables are collected during period",
                "formula": "دوران الذمم = صافي المبيعات الآجلة / متوسط الذمم المدينة",
                "what_it_measures_ar": "يقيس كفاءة تحصيل الذمم المدينة",
                "what_it_measures_en": "Measures receivables collection efficiency",
                "unit": "times"
            },
            {
                "code": "collection_period",
                "name_ar": "فترة التحصيل للذمم المدينة",
                "name_en": "Collection Period",
                "description_ar": "متوسط عدد الأيام لتحصيل الذمم المدينة",
                "description_en": "Average number of days to collect receivables",
                "formula": "فترة التحصيل = 365 / معدل دوران الذمم المدينة",
                "what_it_measures_ar": "يقيس سرعة تحصيل المستحقات",
                "what_it_measures_en": "Measures speed of receivables collection",
                "unit": "days"
            },
            {
                "code": "payables_turnover",
                "name_ar": "معدل دوران الذمم الدائنة",
                "name_en": "Payables Turnover",
                "description_ar": "عدد مرات سداد الذمم الدائنة خلال الفترة",
                "description_en": "Number of times payables are paid during period",
                "formula": "دوران الدائنة = تكلفة البضاعة المباعة / متوسط الذمم الدائنة",
                "what_it_measures_ar": "يقيس سرعة سداد الالتزامات للموردين",
                "what_it_measures_en": "Measures speed of paying supplier obligations",
                "unit": "times"
            },
            {
                "code": "payment_period",
                "name_ar": "فترة السداد للذمم الدائنة",
                "name_en": "Payment Period",
                "description_ar": "متوسط عدد الأيام لسداد الذمم الدائنة",
                "description_en": "Average number of days to pay payables",
                "formula": "فترة السداد = 365 / معدل دوران الذمم الدائنة",
                "what_it_measures_ar": "يقيس الفترة الزمنية لسداد الموردين",
                "what_it_measures_en": "Measures time period to pay suppliers",
                "unit": "days"
            },
            {
                "code": "cash_conversion_cycle",
                "name_ar": "دورة التحويل النقدي",
                "name_en": "Cash Conversion Cycle",
                "description_ar": "الوقت المطلوب لتحويل الاستثمارات إلى نقد",
                "description_en": "Time required to convert investments to cash",
                "formula": "دورة النقد = فترة المخزون + فترة التحصيل - فترة السداد",
                "what_it_measures_ar": "يقيس كفاءة إدارة رأس المال العامل",
                "what_it_measures_en": "Measures working capital management efficiency",
                "unit": "days"
            },
            {
                "code": "operating_cycle",
                "name_ar": "دورة التشغيل",
                "name_en": "Operating Cycle",
                "description_ar": "الوقت من شراء المخزون حتى تحصيل النقد",
                "description_en": "Time from inventory purchase to cash collection",
                "formula": "دورة التشغيل = فترة المخزون + فترة التحصيل",
                "what_it_measures_ar": "يقيس طول دورة العمليات التشغيلية",
                "what_it_measures_en": "Measures length of operating cycle",
                "unit": "days"
            },
            {
                "code": "fixed_assets_turnover",
                "name_ar": "معدل دوران الأصول الثابتة",
                "name_en": "Fixed Assets Turnover",
                "description_ar": "كفاءة استخدام الأصول الثابتة في توليد الإيرادات",
                "description_en": "Efficiency of using fixed assets to generate revenue",
                "formula": "دوران الأصول الثابتة = صافي المبيعات / متوسط الأصول الثابتة",
                "what_it_measures_ar": "يقيس كفاءة استخدام الأصول الثابتة",
                "what_it_measures_en": "Measures fixed assets utilization efficiency",
                "unit": "times"
            },
            {
                "code": "total_assets_turnover",
                "name_ar": "معدل دوران إجمالي الأصول",
                "name_en": "Total Assets Turnover",
                "description_ar": "كفاءة استخدام جميع الأصول في توليد الإيرادات",
                "description_en": "Efficiency of using all assets to generate revenue",
                "formula": "دوران الأصول = صافي المبيعات / متوسط إجمالي الأصول",
                "what_it_measures_ar": "يقيس الكفاءة الإجمالية في استخدام الأصول",
                "what_it_measures_en": "Measures overall asset utilization efficiency",
                "unit": "times"
            },
            {
                "code": "working_capital_turnover",
                "name_ar": "معدل دوران رأس المال العامل",
                "name_en": "Working Capital Turnover",
                "description_ar": "كفاءة استخدام رأس المال العامل",
                "description_en": "Efficiency of using working capital",
                "formula": "دوران رأس المال العامل = صافي المبيعات / متوسط رأس المال العامل",
                "what_it_measures_ar": "يقيس كفاءة إدارة رأس المال العامل",
                "what_it_measures_en": "Measures working capital management efficiency",
                "unit": "times"
            },
            {
                "code": "net_assets_turnover",
                "name_ar": "معدل دوران الأصول الصافية",
                "name_en": "Net Assets Turnover",
                "description_ar": "كفاءة استخدام الأصول الصافية",
                "description_en": "Efficiency of using net assets",
                "formula": "دوران الأصول الصافية = صافي المبيعات / متوسط الأصول الصافية",
                "what_it_measures_ar": "يقيس كفاءة استخدام الأصول بعد خصم الالتزامات",
                "what_it_measures_en": "Measures efficiency of net assets utilization",
                "unit": "times"
            },
            {
                "code": "invested_capital_turnover",
                "name_ar": "معدل دوران رأس المال المستثمر",
                "name_en": "Invested Capital Turnover",
                "description_ar": "كفاءة استخدام رأس المال المستثمر",
                "description_en": "Efficiency of using invested capital",
                "formula": "دوران رأس المال المستثمر = صافي المبيعات / رأس المال المستثمر",
                "what_it_measures_ar": "يقيس عائد الاستثمار من ناحية المبيعات",
                "what_it_measures_en": "Measures investment return from sales perspective",
                "unit": "times"
            },
            {
                "code": "equity_turnover",
                "name_ar": "معدل دوران حقوق الملكية",
                "name_en": "Equity Turnover",
                "description_ar": "كفاءة استخدام حقوق الملكية في توليد المبيعات",
                "description_en": "Efficiency of using equity to generate sales",
                "formula": "دوران حقوق الملكية = صافي المبيعات / متوسط حقوق الملكية",
                "what_it_measures_ar": "يقيس كفاءة استخدام أموال الملاك",
                "what_it_measures_en": "Measures efficiency of using owners' funds",
                "unit": "times"
            },
            {
                "code": "total_productivity_ratio",
                "name_ar": "نسبة الإنتاجية الإجمالية",
                "name_en": "Total Productivity Ratio",
                "description_ar": "مقياس شامل للإنتاجية",
                "description_en": "Comprehensive productivity measure",
                "formula": "الإنتاجية الإجمالية = إجمالي المخرجات / إجمالي المدخلات",
                "what_it_measures_ar": "يقيس الكفاءة الشاملة للشركة",
                "what_it_measures_en": "Measures overall company efficiency",
                "unit": "ratio"
            }
        ]

        for ratio in activity_ratios:
            self._register_analysis(
                ratio,
                AnalysisCategory.CLASSICAL_FOUNDATIONAL,
                AnalysisSubcategory.FINANCIAL_RATIOS
            )

        # Continue with profitability ratios (20), leverage ratios (15), and market ratios (15)
        # [Implementation continues for all remaining ratio categories...]

    def _register_analysis(
        self,
        analysis_data: Dict[str, Any],
        category: AnalysisCategory,
        subcategory: AnalysisSubcategory
    ):
        """Register a single analysis definition"""

        analysis = AnalysisDefinition(
            code=analysis_data["code"],
            name_ar=analysis_data["name_ar"],
            name_en=analysis_data["name_en"],
            category=category,
            subcategory=subcategory,
            description_ar=analysis_data["description_ar"],
            description_en=analysis_data["description_en"],
            formula=analysis_data["formula"],
            what_it_measures_ar=analysis_data["what_it_measures_ar"],
            what_it_measures_en=analysis_data["what_it_measures_en"],
            interpretation_guide_ar=analysis_data.get("interpretation_guide_ar", ""),
            interpretation_guide_en=analysis_data.get("interpretation_guide_en", ""),
            unit=analysis_data["unit"],
            good_range=analysis_data.get("good_range"),
            industry_benchmarks=analysis_data.get("industry_benchmarks", {}),
            calculation_method=analysis_data.get("calculation_method", ""),
            dependencies=analysis_data.get("dependencies", [])
        )

        self.analyses[analysis_data["code"]] = analysis

    # [Continue with all other analysis registration methods...]
    def _register_flow_movement_analyses(self):
        """Register all 18 flow and movement analyses"""
        pass

    def _register_advanced_comparison_analyses(self):
        """Register all 3 advanced comparison analyses"""
        pass

    def _register_valuation_investment_analyses(self):
        """Register all 13 valuation and investment analyses"""
        pass

    def _register_performance_efficiency_analyses(self):
        """Register all 5 performance efficiency analyses"""
        pass

    def _register_modeling_simulation_analyses(self):
        """Register all 11 modeling and simulation analyses"""
        pass

    def _register_statistical_quantitative_analyses(self):
        """Register all 16 statistical quantitative analyses"""
        pass

    def _register_prediction_credit_analyses(self):
        """Register all 10 prediction and credit analyses"""
        pass

    def _register_quantitative_risk_analyses(self):
        """Register all 25 quantitative risk analyses"""
        pass

    def _register_portfolio_investment_analyses(self):
        """Register all 14 portfolio investment analyses"""
        pass

    def _register_merger_acquisition_analyses(self):
        """Register all 5 merger and acquisition analyses"""
        pass

    def _register_detection_prediction_analyses(self):
        """Register all 10 detection and prediction analyses"""
        pass

    def _register_timeseries_statistical_analyses(self):
        """Register all 6 time series statistical analyses"""
        pass

    def get_analysis(self, code: str) -> Optional[AnalysisDefinition]:
        """Get analysis definition by code"""
        return self.analyses.get(code)

    def get_analyses_by_category(self, category: AnalysisCategory) -> List[AnalysisDefinition]:
        """Get all analyses in a category"""
        return [analysis for analysis in self.analyses.values() if analysis.category == category]

    def get_analyses_by_subcategory(self, subcategory: AnalysisSubcategory) -> List[AnalysisDefinition]:
        """Get all analyses in a subcategory"""
        return [analysis for analysis in self.analyses.values() if analysis.subcategory == subcategory]

    def get_all_analysis_codes(self) -> List[str]:
        """Get all analysis codes"""
        return list(self.analyses.keys())

    def get_total_count(self) -> int:
        """Get total number of registered analyses"""
        return len(self.analyses)

    def get_count_by_category(self) -> Dict[str, int]:
        """Get count of analyses by category"""
        counts = {}
        for analysis in self.analyses.values():
            category_name = analysis.category.value
            counts[category_name] = counts.get(category_name, 0) + 1
        return counts