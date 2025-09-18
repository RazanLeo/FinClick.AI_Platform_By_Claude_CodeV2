"""
تحاليل السيولة - Liquidity Analysis
10 تحاليل أساسية للسيولة المالية
"""

import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
import math

class LiquidityAnalysis:
    """فئة تحاليل السيولة المالية"""

    def __init__(self):
        self.analysis_name = "تحاليل السيولة"
        self.analysis_name_en = "Liquidity Analysis"
        self.category = "السيولة"
        self.category_en = "Liquidity"

    def current_ratio(self, current_assets: float, current_liabilities: float) -> Dict[str, Any]:
        """
        1. نسبة التداول
        Current Ratio = Current Assets / Current Liabilities
        """
        try:
            if current_liabilities == 0:
                return {
                    'value': None,
                    'formula': 'الأصول المتداولة ÷ الخصوم المتداولة',
                    'formula_en': 'Current Assets ÷ Current Liabilities',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الخصوم المتداولة تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - current liabilities equal zero',
                    'risk_level': 'منخفض',
                    'recommendation_ar': 'مراجعة البيانات المالية',
                    'recommendation_en': 'Review financial data'
                }

            ratio = current_assets / current_liabilities

            # تفسير النتائج
            if ratio >= 2.0:
                interpretation_ar = 'سيولة ممتازة - الشركة قادرة على تغطية التزاماتها بسهولة'
                interpretation_en = 'Excellent liquidity - company can easily cover its obligations'
                risk_level = 'منخفض'
                recommendation_ar = 'الحفاظ على مستوى السيولة الحالي'
                recommendation_en = 'Maintain current liquidity level'
            elif ratio >= 1.5:
                interpretation_ar = 'سيولة جيدة - وضع مالي مستقر'
                interpretation_en = 'Good liquidity - stable financial position'
                risk_level = 'منخفض'
                recommendation_ar = 'مراقبة مستويات السيولة بانتظام'
                recommendation_en = 'Monitor liquidity levels regularly'
            elif ratio >= 1.0:
                interpretation_ar = 'سيولة مقبولة - تحتاج لتحسين'
                interpretation_en = 'Acceptable liquidity - needs improvement'
                risk_level = 'متوسط'
                recommendation_ar = 'تحسين إدارة رأس المال العامل'
                recommendation_en = 'Improve working capital management'
            else:
                interpretation_ar = 'سيولة ضعيفة - مخاطر عالية'
                interpretation_en = 'Poor liquidity - high risk'
                risk_level = 'عالي'
                recommendation_ar = 'اتخاذ إجراءات عاجلة لتحسين السيولة'
                recommendation_en = 'Take urgent action to improve liquidity'

            return {
                'value': round(ratio, 4),
                'percentage': f"{ratio:.2%}",
                'formula': 'الأصول المتداولة ÷ الخصوم المتداولة',
                'formula_en': 'Current Assets ÷ Current Liabilities',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'recommendation_ar': recommendation_ar,
                'recommendation_en': recommendation_en,
                'benchmark': {
                    'excellent': '≥ 2.0',
                    'good': '1.5 - 1.99',
                    'acceptable': '1.0 - 1.49',
                    'poor': '< 1.0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة التداول: {str(e)}',
                'error_en': f'Error calculating current ratio: {str(e)}'
            }

    def quick_ratio(self, current_assets: float, inventory: float,
                   prepaid_expenses: float, current_liabilities: float) -> Dict[str, Any]:
        """
        2. نسبة السيولة السريعة (الاختبار الحمضي)
        Quick Ratio = (Current Assets - Inventory - Prepaid Expenses) / Current Liabilities
        """
        try:
            if current_liabilities == 0:
                return {
                    'value': None,
                    'formula': '(الأصول المتداولة - المخزون - المصروفات المدفوعة مقدماً) ÷ الخصوم المتداولة',
                    'formula_en': '(Current Assets - Inventory - Prepaid Expenses) ÷ Current Liabilities',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الخصوم المتداولة تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - current liabilities equal zero'
                }

            quick_assets = current_assets - inventory - prepaid_expenses
            ratio = quick_assets / current_liabilities

            # تفسير النتائج
            if ratio >= 1.5:
                interpretation_ar = 'سيولة سريعة ممتازة - قدرة عالية على تسديد الالتزامات الفورية'
                interpretation_en = 'Excellent quick liquidity - high ability to meet immediate obligations'
                risk_level = 'منخفض'
            elif ratio >= 1.0:
                interpretation_ar = 'سيولة سريعة جيدة - وضع مالي مستقر'
                interpretation_en = 'Good quick liquidity - stable financial position'
                risk_level = 'منخفض'
            elif ratio >= 0.8:
                interpretation_ar = 'سيولة سريعة مقبولة - تحتاج لمراقبة'
                interpretation_en = 'Acceptable quick liquidity - needs monitoring'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'سيولة سريعة ضعيفة - صعوبة في تسديد الالتزامات الفورية'
                interpretation_en = 'Poor quick liquidity - difficulty meeting immediate obligations'
                risk_level = 'عالي'

            return {
                'value': round(ratio, 4),
                'percentage': f"{ratio:.2%}",
                'quick_assets': round(quick_assets, 2),
                'formula': '(الأصول المتداولة - المخزون - المصروفات المدفوعة مقدماً) ÷ الخصوم المتداولة',
                'formula_en': '(Current Assets - Inventory - Prepaid Expenses) ÷ Current Liabilities',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 1.5',
                    'good': '1.0 - 1.49',
                    'acceptable': '0.8 - 0.99',
                    'poor': '< 0.8'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة السيولة السريعة: {str(e)}',
                'error_en': f'Error calculating quick ratio: {str(e)}'
            }

    def cash_ratio(self, cash_and_equivalents: float,
                   short_term_investments: float, current_liabilities: float) -> Dict[str, Any]:
        """
        3. نسبة السيولة النقدية
        Cash Ratio = (Cash + Cash Equivalents + Short-term Investments) / Current Liabilities
        """
        try:
            if current_liabilities == 0:
                return {
                    'value': None,
                    'formula': '(النقد + شبه النقد + الاستثمارات قصيرة الأجل) ÷ الخصوم المتداولة',
                    'formula_en': '(Cash + Cash Equivalents + Short-term Investments) ÷ Current Liabilities',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الخصوم المتداولة تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - current liabilities equal zero'
                }

            liquid_cash = cash_and_equivalents + short_term_investments
            ratio = liquid_cash / current_liabilities

            # تفسير النتائج
            if ratio >= 0.5:
                interpretation_ar = 'سيولة نقدية ممتازة - احتياطي نقدي قوي'
                interpretation_en = 'Excellent cash liquidity - strong cash reserves'
                risk_level = 'منخفض'
            elif ratio >= 0.3:
                interpretation_ar = 'سيولة نقدية جيدة - وضع نقدي مستقر'
                interpretation_en = 'Good cash liquidity - stable cash position'
                risk_level = 'منخفض'
            elif ratio >= 0.15:
                interpretation_ar = 'سيولة نقدية مقبولة - تحتاج لتحسين'
                interpretation_en = 'Acceptable cash liquidity - needs improvement'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'سيولة نقدية ضعيفة - نقص في الاحتياطي النقدي'
                interpretation_en = 'Poor cash liquidity - insufficient cash reserves'
                risk_level = 'عالي'

            return {
                'value': round(ratio, 4),
                'percentage': f"{ratio:.2%}",
                'liquid_cash': round(liquid_cash, 2),
                'formula': '(النقد + شبه النقد + الاستثمارات قصيرة الأجل) ÷ الخصوم المتداولة',
                'formula_en': '(Cash + Cash Equivalents + Short-term Investments) ÷ Current Liabilities',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 0.5',
                    'good': '0.3 - 0.49',
                    'acceptable': '0.15 - 0.29',
                    'poor': '< 0.15'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة السيولة النقدية: {str(e)}',
                'error_en': f'Error calculating cash ratio: {str(e)}'
            }

    def working_capital(self, current_assets: float, current_liabilities: float) -> Dict[str, Any]:
        """
        4. رأس المال العامل
        Working Capital = Current Assets - Current Liabilities
        """
        try:
            wc = current_assets - current_liabilities

            # تفسير النتائج
            if wc > 0:
                if wc >= current_assets * 0.3:
                    interpretation_ar = 'رأس مال عامل إيجابي قوي - وضع مالي ممتاز'
                    interpretation_en = 'Strong positive working capital - excellent financial position'
                    risk_level = 'منخفض'
                else:
                    interpretation_ar = 'رأس مال عامل إيجابي - وضع مالي جيد'
                    interpretation_en = 'Positive working capital - good financial position'
                    risk_level = 'منخفض'
            elif wc == 0:
                interpretation_ar = 'رأس مال عامل متوازن - يحتاج لمراقبة دقيقة'
                interpretation_en = 'Balanced working capital - needs careful monitoring'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'رأس مال عامل سالب - مخاطر سيولة عالية'
                interpretation_en = 'Negative working capital - high liquidity risk'
                risk_level = 'عالي'

            # حساب نسبة رأس المال العامل إلى إجمالي الأصول المتداولة
            wc_ratio = (wc / current_assets) * 100 if current_assets > 0 else 0

            return {
                'value': round(wc, 2),
                'ratio_to_current_assets': round(wc_ratio, 2),
                'formula': 'الأصول المتداولة - الخصوم المتداولة',
                'formula_en': 'Current Assets - Current Liabilities',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '> 30% من الأصول المتداولة',
                    'good': '10-30% من الأصول المتداولة',
                    'acceptable': '0-10% من الأصول المتداولة',
                    'poor': 'أقل من 0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب رأس المال العامل: {str(e)}',
                'error_en': f'Error calculating working capital: {str(e)}'
            }

    def operating_cash_flow_ratio(self, operating_cash_flow: float,
                                 current_liabilities: float) -> Dict[str, Any]:
        """
        5. نسبة التدفق النقدي التشغيلي
        Operating Cash Flow Ratio = Operating Cash Flow / Current Liabilities
        """
        try:
            if current_liabilities == 0:
                return {
                    'value': None,
                    'formula': 'التدفق النقدي التشغيلي ÷ الخصوم المتداولة',
                    'formula_en': 'Operating Cash Flow ÷ Current Liabilities',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الخصوم المتداولة تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - current liabilities equal zero'
                }

            ratio = operating_cash_flow / current_liabilities

            # تفسير النتائج
            if ratio >= 0.4:
                interpretation_ar = 'تدفق نقدي تشغيلي ممتاز - قدرة عالية على تغطية الالتزامات'
                interpretation_en = 'Excellent operating cash flow - high ability to cover obligations'
                risk_level = 'منخفض'
            elif ratio >= 0.25:
                interpretation_ar = 'تدفق نقدي تشغيلي جيد - وضع مالي مستقر'
                interpretation_en = 'Good operating cash flow - stable financial position'
                risk_level = 'منخفض'
            elif ratio >= 0.1:
                interpretation_ar = 'تدفق نقدي تشغيلي مقبول - يحتاج لتحسين'
                interpretation_en = 'Acceptable operating cash flow - needs improvement'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'تدفق نقدي تشغيلي ضعيف - مخاطر سيولة'
                interpretation_en = 'Poor operating cash flow - liquidity risks'
                risk_level = 'عالي'

            return {
                'value': round(ratio, 4),
                'percentage': f"{ratio:.2%}",
                'formula': 'التدفق النقدي التشغيلي ÷ الخصوم المتداولة',
                'formula_en': 'Operating Cash Flow ÷ Current Liabilities',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 0.4',
                    'good': '0.25 - 0.39',
                    'acceptable': '0.1 - 0.24',
                    'poor': '< 0.1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة التدفق النقدي التشغيلي: {str(e)}',
                'error_en': f'Error calculating operating cash flow ratio: {str(e)}'
            }

    def days_inventory_outstanding(self, inventory: float, cost_of_goods_sold: float) -> Dict[str, Any]:
        """
        6. أيام بقاء المخزون
        Days Inventory Outstanding = (Inventory / Cost of Goods Sold) × 365
        """
        try:
            if cost_of_goods_sold == 0:
                return {
                    'value': None,
                    'formula': '(المخزون ÷ تكلفة البضاعة المباعة) × 365',
                    'formula_en': '(Inventory ÷ Cost of Goods Sold) × 365',
                    'interpretation_ar': 'لا يمكن حساب الأيام - تكلفة البضاعة تساوي صفر',
                    'interpretation_en': 'Cannot calculate days - cost of goods sold equals zero'
                }

            days = (inventory / cost_of_goods_sold) * 365

            # تفسير النتائج (يختلف حسب الصناعة)
            if days <= 30:
                interpretation_ar = 'دوران مخزون سريع جداً - إدارة ممتازة للمخزون'
                interpretation_en = 'Very fast inventory turnover - excellent inventory management'
                risk_level = 'منخفض'
            elif days <= 60:
                interpretation_ar = 'دوران مخزون جيد - إدارة فعالة للمخزون'
                interpretation_en = 'Good inventory turnover - effective inventory management'
                risk_level = 'منخفض'
            elif days <= 90:
                interpretation_ar = 'دوران مخزون مقبول - يمكن تحسينه'
                interpretation_en = 'Acceptable inventory turnover - can be improved'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'دوران مخزون بطيء - مخاطر تراكم المخزون'
                interpretation_en = 'Slow inventory turnover - risk of inventory accumulation'
                risk_level = 'عالي'

            # حساب معدل الدوران
            turnover_rate = 365 / days if days > 0 else 0

            return {
                'value': round(days, 2),
                'turnover_rate': round(turnover_rate, 2),
                'formula': '(المخزون ÷ تكلفة البضاعة المباعة) × 365',
                'formula_en': '(Inventory ÷ Cost of Goods Sold) × 365',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 30 يوم',
                    'good': '31-60 يوم',
                    'acceptable': '61-90 يوم',
                    'poor': '> 90 يوم'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب أيام بقاء المخزون: {str(e)}',
                'error_en': f'Error calculating days inventory outstanding: {str(e)}'
            }

    def days_payable_outstanding(self, accounts_payable: float,
                               cost_of_goods_sold: float) -> Dict[str, Any]:
        """
        7. أيام سداد الموردين
        Days Payable Outstanding = (Accounts Payable / Cost of Goods Sold) × 365
        """
        try:
            if cost_of_goods_sold == 0:
                return {
                    'value': None,
                    'formula': '(حسابات الدائنين ÷ تكلفة البضاعة المباعة) × 365',
                    'formula_en': '(Accounts Payable ÷ Cost of Goods Sold) × 365',
                    'interpretation_ar': 'لا يمكن حساب الأيام - تكلفة البضاعة تساوي صفر',
                    'interpretation_en': 'Cannot calculate days - cost of goods sold equals zero'
                }

            days = (accounts_payable / cost_of_goods_sold) * 365

            # تفسير النتائج
            if days >= 60:
                interpretation_ar = 'فترة سداد طويلة - استفادة جيدة من ائتمان الموردين'
                interpretation_en = 'Long payment period - good utilization of supplier credit'
                risk_level = 'منخفض'
            elif days >= 45:
                interpretation_ar = 'فترة سداد مقبولة - إدارة جيدة للسيولة'
                interpretation_en = 'Acceptable payment period - good liquidity management'
                risk_level = 'منخفض'
            elif days >= 30:
                interpretation_ar = 'فترة سداد قصيرة - يمكن تحسين إدارة السيولة'
                interpretation_en = 'Short payment period - can improve liquidity management'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'فترة سداد قصيرة جداً - ضغط على السيولة'
                interpretation_en = 'Very short payment period - pressure on liquidity'
                risk_level = 'عالي'

            return {
                'value': round(days, 2),
                'formula': '(حسابات الدائنين ÷ تكلفة البضاعة المباعة) × 365',
                'formula_en': '(Accounts Payable ÷ Cost of Goods Sold) × 365',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 60 يوم',
                    'good': '45-59 يوم',
                    'acceptable': '30-44 يوم',
                    'poor': '< 30 يوم'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب أيام سداد الموردين: {str(e)}',
                'error_en': f'Error calculating days payable outstanding: {str(e)}'
            }

    def working_capital_ratio(self, working_capital: float, total_assets: float) -> Dict[str, Any]:
        """
        8. نسبة رأس المال العامل
        Working Capital Ratio = Working Capital / Total Assets
        """
        try:
            if total_assets == 0:
                return {
                    'value': None,
                    'formula': 'رأس المال العامل ÷ إجمالي الأصول',
                    'formula_en': 'Working Capital ÷ Total Assets',
                    'interpretation_ar': 'لا يمكن حساب النسبة - إجمالي الأصول تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - total assets equal zero'
                }

            ratio = working_capital / total_assets

            # تفسير النتائج
            if ratio >= 0.3:
                interpretation_ar = 'نسبة رأس مال عامل ممتازة - وضع مالي قوي'
                interpretation_en = 'Excellent working capital ratio - strong financial position'
                risk_level = 'منخفض'
            elif ratio >= 0.15:
                interpretation_ar = 'نسبة رأس مال عامل جيدة - وضع مالي مستقر'
                interpretation_en = 'Good working capital ratio - stable financial position'
                risk_level = 'منخفض'
            elif ratio >= 0.05:
                interpretation_ar = 'نسبة رأس مال عامل مقبولة - تحتاج لتحسين'
                interpretation_en = 'Acceptable working capital ratio - needs improvement'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'نسبة رأس مال عامل ضعيفة - مخاطر سيولة'
                interpretation_en = 'Poor working capital ratio - liquidity risks'
                risk_level = 'عالي'

            return {
                'value': round(ratio, 4),
                'percentage': f"{ratio:.2%}",
                'formula': 'رأس المال العامل ÷ إجمالي الأصول',
                'formula_en': 'Working Capital ÷ Total Assets',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 30%',
                    'good': '15-29%',
                    'acceptable': '5-14%',
                    'poor': '< 5%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة رأس المال العامل: {str(e)}',
                'error_en': f'Error calculating working capital ratio: {str(e)}'
            }

    def cash_to_current_liabilities(self, cash_and_equivalents: float,
                                   current_liabilities: float) -> Dict[str, Any]:
        """
        9. نسبة النقد إلى الخصوم المتداولة
        Cash to Current Liabilities = Cash and Cash Equivalents / Current Liabilities
        """
        try:
            if current_liabilities == 0:
                return {
                    'value': None,
                    'formula': 'النقد وشبه النقد ÷ الخصوم المتداولة',
                    'formula_en': 'Cash and Cash Equivalents ÷ Current Liabilities',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الخصوم المتداولة تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - current liabilities equal zero'
                }

            ratio = cash_and_equivalents / current_liabilities

            # تفسير النتائج
            if ratio >= 0.3:
                interpretation_ar = 'نسبة نقد ممتازة - احتياطي نقدي قوي'
                interpretation_en = 'Excellent cash ratio - strong cash reserves'
                risk_level = 'منخفض'
            elif ratio >= 0.2:
                interpretation_ar = 'نسبة نقد جيدة - وضع نقدي مستقر'
                interpretation_en = 'Good cash ratio - stable cash position'
                risk_level = 'منخفض'
            elif ratio >= 0.1:
                interpretation_ar = 'نسبة نقد مقبولة - تحتاج لمراقبة'
                interpretation_en = 'Acceptable cash ratio - needs monitoring'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'نسبة نقد ضعيفة - نقص في السيولة النقدية'
                interpretation_en = 'Poor cash ratio - insufficient cash liquidity'
                risk_level = 'عالي'

            return {
                'value': round(ratio, 4),
                'percentage': f"{ratio:.2%}",
                'formula': 'النقد وشبه النقد ÷ الخصوم المتداولة',
                'formula_en': 'Cash and Cash Equivalents ÷ Current Liabilities',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 30%',
                    'good': '20-29%',
                    'acceptable': '10-19%',
                    'poor': '< 10%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة النقد إلى الخصوم المتداولة: {str(e)}',
                'error_en': f'Error calculating cash to current liabilities: {str(e)}'
            }

    def liquidity_index(self, cash: float, short_term_investments: float,
                       accounts_receivable: float, inventory: float,
                       current_liabilities: float) -> Dict[str, Any]:
        """
        10. مؤشر السيولة المرجح
        Liquidity Index = (Cash×1 + Short-term Investments×0.95 + A/R×0.85 + Inventory×0.5) / Current Liabilities
        """
        try:
            if current_liabilities == 0:
                return {
                    'value': None,
                    'formula': '(النقد×1 + الاستثمارات قصيرة الأجل×0.95 + الذمم×0.85 + المخزون×0.5) ÷ الخصوم المتداولة',
                    'formula_en': '(Cash×1 + Short-term Investments×0.95 + A/R×0.85 + Inventory×0.5) ÷ Current Liabilities',
                    'interpretation_ar': 'لا يمكن حساب المؤشر - الخصوم المتداولة تساوي صفر',
                    'interpretation_en': 'Cannot calculate index - current liabilities equal zero'
                }

            # أوزان السيولة للأصول المختلفة
            weighted_assets = (cash * 1.0 +
                             short_term_investments * 0.95 +
                             accounts_receivable * 0.85 +
                             inventory * 0.5)

            index = weighted_assets / current_liabilities

            # تفسير النتائج
            if index >= 1.2:
                interpretation_ar = 'مؤشر سيولة ممتاز - وضع مالي قوي جداً'
                interpretation_en = 'Excellent liquidity index - very strong financial position'
                risk_level = 'منخفض'
            elif index >= 1.0:
                interpretation_ar = 'مؤشر سيولة جيد - وضع مالي مستقر'
                interpretation_en = 'Good liquidity index - stable financial position'
                risk_level = 'منخفض'
            elif index >= 0.8:
                interpretation_ar = 'مؤشر سيولة مقبول - يحتاج لمراقبة'
                interpretation_en = 'Acceptable liquidity index - needs monitoring'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'مؤشر سيولة ضعيف - مخاطر سيولة عالية'
                interpretation_en = 'Poor liquidity index - high liquidity risks'
                risk_level = 'عالي'

            # تفاصيل المكونات
            components = {
                'cash_weight': round(cash * 1.0, 2),
                'investments_weight': round(short_term_investments * 0.95, 2),
                'receivables_weight': round(accounts_receivable * 0.85, 2),
                'inventory_weight': round(inventory * 0.5, 2),
                'total_weighted': round(weighted_assets, 2)
            }

            return {
                'value': round(index, 4),
                'weighted_assets': round(weighted_assets, 2),
                'components': components,
                'formula': '(النقد×1 + الاستثمارات قصيرة الأجل×0.95 + الذمم×0.85 + المخزون×0.5) ÷ الخصوم المتداولة',
                'formula_en': '(Cash×1 + Short-term Investments×0.95 + A/R×0.85 + Inventory×0.5) ÷ Current Liabilities',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 1.2',
                    'good': '1.0 - 1.19',
                    'acceptable': '0.8 - 0.99',
                    'poor': '< 0.8'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب مؤشر السيولة: {str(e)}',
                'error_en': f'Error calculating liquidity index: {str(e)}'
            }

    def comprehensive_liquidity_analysis(self, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """تحليل شامل للسيولة"""
        try:
            results = {}

            # 1. نسبة التداول
            if all(k in financial_data for k in ['current_assets', 'current_liabilities']):
                results['current_ratio'] = self.current_ratio(
                    financial_data['current_assets'],
                    financial_data['current_liabilities']
                )

            # 2. نسبة السيولة السريعة
            if all(k in financial_data for k in ['current_assets', 'inventory', 'prepaid_expenses', 'current_liabilities']):
                results['quick_ratio'] = self.quick_ratio(
                    financial_data['current_assets'],
                    financial_data['inventory'],
                    financial_data['prepaid_expenses'],
                    financial_data['current_liabilities']
                )

            # 3. نسبة السيولة النقدية
            if all(k in financial_data for k in ['cash_and_equivalents', 'short_term_investments', 'current_liabilities']):
                results['cash_ratio'] = self.cash_ratio(
                    financial_data['cash_and_equivalents'],
                    financial_data['short_term_investments'],
                    financial_data['current_liabilities']
                )

            # 4. رأس المال العامل
            if all(k in financial_data for k in ['current_assets', 'current_liabilities']):
                results['working_capital'] = self.working_capital(
                    financial_data['current_assets'],
                    financial_data['current_liabilities']
                )

            # 5. نسبة التدفق النقدي التشغيلي
            if all(k in financial_data for k in ['operating_cash_flow', 'current_liabilities']):
                results['operating_cash_flow_ratio'] = self.operating_cash_flow_ratio(
                    financial_data['operating_cash_flow'],
                    financial_data['current_liabilities']
                )

            # 6. أيام بقاء المخزون
            if all(k in financial_data for k in ['inventory', 'cost_of_goods_sold']):
                results['days_inventory_outstanding'] = self.days_inventory_outstanding(
                    financial_data['inventory'],
                    financial_data['cost_of_goods_sold']
                )

            # 7. أيام سداد الموردين
            if all(k in financial_data for k in ['accounts_payable', 'cost_of_goods_sold']):
                results['days_payable_outstanding'] = self.days_payable_outstanding(
                    financial_data['accounts_payable'],
                    financial_data['cost_of_goods_sold']
                )

            # 8. نسبة رأس المال العامل
            if all(k in financial_data for k in ['current_assets', 'current_liabilities', 'total_assets']):
                wc = financial_data['current_assets'] - financial_data['current_liabilities']
                results['working_capital_ratio'] = self.working_capital_ratio(
                    wc,
                    financial_data['total_assets']
                )

            # 9. نسبة النقد إلى الخصوم المتداولة
            if all(k in financial_data for k in ['cash_and_equivalents', 'current_liabilities']):
                results['cash_to_current_liabilities'] = self.cash_to_current_liabilities(
                    financial_data['cash_and_equivalents'],
                    financial_data['current_liabilities']
                )

            # 10. مؤشر السيولة
            if all(k in financial_data for k in ['cash_and_equivalents', 'short_term_investments',
                                               'accounts_receivable', 'inventory', 'current_liabilities']):
                results['liquidity_index'] = self.liquidity_index(
                    financial_data['cash_and_equivalents'],
                    financial_data['short_term_investments'],
                    financial_data['accounts_receivable'],
                    financial_data['inventory'],
                    financial_data['current_liabilities']
                )

            # تقييم عام للسيولة
            overall_assessment = self._assess_overall_liquidity(results)

            return {
                'individual_analyses': results,
                'overall_assessment': overall_assessment,
                'analysis_date': financial_data.get('analysis_date', 'غير محدد'),
                'company_name': financial_data.get('company_name', 'غير محدد')
            }

        except Exception as e:
            return {
                'error': f'خطأ في التحليل الشامل للسيولة: {str(e)}',
                'error_en': f'Error in comprehensive liquidity analysis: {str(e)}'
            }

    def _assess_overall_liquidity(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم الوضع العام للسيولة"""
        try:
            scores = []
            risk_levels = []

            # جمع النقاط ومستويات المخاطر
            for analysis_name, analysis_result in results.items():
                if isinstance(analysis_result, dict) and 'risk_level' in analysis_result:
                    risk_levels.append(analysis_result['risk_level'])

                    # تحويل مستوى المخاطر إلى نقاط
                    if analysis_result['risk_level'] == 'منخفض':
                        scores.append(4)
                    elif analysis_result['risk_level'] == 'متوسط':
                        scores.append(2)
                    else:  # عالي
                        scores.append(1)

            if not scores:
                return {
                    'overall_score': 0,
                    'overall_rating': 'غير محدد',
                    'overall_rating_en': 'Not determined',
                    'recommendation_ar': 'يحتاج لبيانات أكثر للتقييم',
                    'recommendation_en': 'Needs more data for assessment'
                }

            # حساب النقاط الإجمالية
            average_score = sum(scores) / len(scores)

            # تحديد التقييم العام
            if average_score >= 3.5:
                overall_rating = 'ممتاز'
                overall_rating_en = 'Excellent'
                recommendation_ar = 'وضع السيولة ممتاز - الحفاظ على الأداء الحالي'
                recommendation_en = 'Excellent liquidity position - maintain current performance'
            elif average_score >= 2.5:
                overall_rating = 'جيد'
                overall_rating_en = 'Good'
                recommendation_ar = 'وضع السيولة جيد - مراقبة مستمرة مطلوبة'
                recommendation_en = 'Good liquidity position - continuous monitoring required'
            elif average_score >= 1.5:
                overall_rating = 'مقبول'
                overall_rating_en = 'Acceptable'
                recommendation_ar = 'وضع السيولة يحتاج للتحسين - اتخاذ إجراءات تحسينية'
                recommendation_en = 'Liquidity position needs improvement - take corrective actions'
            else:
                overall_rating = 'ضعيف'
                overall_rating_en = 'Poor'
                recommendation_ar = 'وضع السيولة ضعيف - إجراءات عاجلة مطلوبة'
                recommendation_en = 'Poor liquidity position - urgent actions required'

            return {
                'overall_score': round(average_score, 2),
                'overall_rating': overall_rating,
                'overall_rating_en': overall_rating_en,
                'total_analyses': len(scores),
                'risk_distribution': {
                    'منخفض': risk_levels.count('منخفض'),
                    'متوسط': risk_levels.count('متوسط'),
                    'عالي': risk_levels.count('عالي')
                },
                'recommendation_ar': recommendation_ar,
                'recommendation_en': recommendation_en
            }

        except Exception as e:
            return {
                'error': f'خطأ في تقييم الوضع العام للسيولة: {str(e)}',
                'error_en': f'Error in overall liquidity assessment: {str(e)}'
            }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مثيل من فئة تحليل السيولة
    liquidity_analyzer = LiquidityAnalysis()

    # بيانات مالية تجريبية
    sample_data = {
        'current_assets': 500000,
        'current_liabilities': 300000,
        'inventory': 150000,
        'prepaid_expenses': 20000,
        'cash_and_equivalents': 100000,
        'short_term_investments': 50000,
        'accounts_receivable': 180000,
        'accounts_payable': 120000,
        'cost_of_goods_sold': 800000,
        'operating_cash_flow': 120000,
        'total_assets': 1200000,
        'company_name': 'شركة المثال التجارية',
        'analysis_date': '2024-12-31'
    }

    # تشغيل التحليل الشامل
    comprehensive_results = liquidity_analyzer.comprehensive_liquidity_analysis(sample_data)

    print("=== تحليل السيولة الشامل ===")
    print(f"اسم الشركة: {comprehensive_results.get('company_name', 'غير محدد')}")
    print(f"تاريخ التحليل: {comprehensive_results.get('analysis_date', 'غير محدد')}")
    print("\n=== النتائج التفصيلية ===")

    for analysis_name, result in comprehensive_results.get('individual_analyses', {}).items():
        if isinstance(result, dict) and 'value' in result:
            print(f"\n{analysis_name}:")
            print(f"  القيمة: {result.get('value', 'غير محدد')}")
            print(f"  التفسير: {result.get('interpretation_ar', 'غير محدد')}")
            print(f"  مستوى المخاطر: {result.get('risk_level', 'غير محدد')}")

    print(f"\n=== التقييم العام ===")
    overall = comprehensive_results.get('overall_assessment', {})
    print(f"التقييم العام: {overall.get('overall_rating', 'غير محدد')}")
    print(f"النقاط: {overall.get('overall_score', 0)}")
    print(f"التوصية: {overall.get('recommendation_ar', 'غير محدد')}")