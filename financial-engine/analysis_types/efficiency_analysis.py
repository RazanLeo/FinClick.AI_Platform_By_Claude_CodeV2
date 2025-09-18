"""
تحاليل الكفاءة - Efficiency Analysis
20 تحليل أساسي لكفاءة الأداء المالي والتشغيلي
"""

import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
import math

class EfficiencyAnalysis:
    """فئة تحاليل الكفاءة المالية والتشغيلية"""

    def __init__(self):
        self.analysis_name = "تحاليل الكفاءة"
        self.analysis_name_en = "Efficiency Analysis"
        self.category = "الكفاءة"
        self.category_en = "Efficiency"

    def inventory_turnover(self, cost_of_goods_sold: float, average_inventory: float) -> Dict[str, Any]:
        """
        1. معدل دوران المخزون
        Inventory Turnover = Cost of Goods Sold / Average Inventory
        """
        try:
            if average_inventory == 0:
                return {
                    'value': None,
                    'formula': 'تكلفة البضاعة المباعة ÷ متوسط المخزون',
                    'formula_en': 'Cost of Goods Sold ÷ Average Inventory',
                    'interpretation_ar': 'لا يمكن حساب معدل الدوران - متوسط المخزون يساوي صفر',
                    'interpretation_en': 'Cannot calculate turnover - average inventory equals zero'
                }

            turnover = cost_of_goods_sold / average_inventory

            # حساب أيام المخزون
            days_in_inventory = 365 / turnover if turnover > 0 else float('inf')

            # تفسير النتائج
            if turnover >= 12:
                interpretation_ar = 'معدل دوران مخزون ممتاز - كفاءة عالية في إدارة المخزون'
                interpretation_en = 'Excellent inventory turnover - high efficiency in inventory management'
                efficiency = 'عالية جداً'
                risk_level = 'منخفض'
            elif turnover >= 8:
                interpretation_ar = 'معدل دوران مخزون جيد - إدارة فعالة للمخزون'
                interpretation_en = 'Good inventory turnover - effective inventory management'
                efficiency = 'جيدة'
                risk_level = 'منخفض'
            elif turnover >= 4:
                interpretation_ar = 'معدل دوران مخزون مقبول - يحتاج لتحسين'
                interpretation_en = 'Acceptable inventory turnover - needs improvement'
                efficiency = 'معتدلة'
                risk_level = 'متوسط'
            elif turnover >= 2:
                interpretation_ar = 'معدل دوران مخزون ضعيف - مخاطر تراكم المخزون'
                interpretation_en = 'Poor inventory turnover - risk of inventory accumulation'
                efficiency = 'ضعيفة'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'معدل دوران مخزون ضعيف جداً - مشاكل جدية في إدارة المخزون'
                interpretation_en = 'Very poor inventory turnover - serious inventory management problems'
                efficiency = 'ضعيفة جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(turnover, 2),
                'days_in_inventory': round(days_in_inventory, 1) if days_in_inventory != float('inf') else 'غير محدود',
                'cost_of_goods_sold': round(cost_of_goods_sold, 2),
                'average_inventory': round(average_inventory, 2),
                'formula': 'تكلفة البضاعة المباعة ÷ متوسط المخزون',
                'formula_en': 'Cost of Goods Sold ÷ Average Inventory',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 12',
                    'good': '8-11.99',
                    'acceptable': '4-7.99',
                    'poor': '2-3.99',
                    'very_poor': '< 2'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب معدل دوران المخزون: {str(e)}',
                'error_en': f'Error calculating inventory turnover: {str(e)}'
            }

    def accounts_receivable_turnover(self, net_credit_sales: float, average_accounts_receivable: float) -> Dict[str, Any]:
        """
        2. معدل دوران الذمم المدينة
        Accounts Receivable Turnover = Net Credit Sales / Average Accounts Receivable
        """
        try:
            if average_accounts_receivable == 0:
                return {
                    'value': None,
                    'formula': 'صافي المبيعات الآجلة ÷ متوسط الذمم المدينة',
                    'formula_en': 'Net Credit Sales ÷ Average Accounts Receivable',
                    'interpretation_ar': 'لا يمكن حساب معدل الدوران - متوسط الذمم المدينة يساوي صفر',
                    'interpretation_en': 'Cannot calculate turnover - average accounts receivable equals zero'
                }

            turnover = net_credit_sales / average_accounts_receivable

            # حساب أيام التحصيل
            collection_days = 365 / turnover if turnover > 0 else float('inf')

            # تفسير النتائج
            if turnover >= 12:
                interpretation_ar = 'معدل دوران ذمم ممتاز - تحصيل سريع وفعال'
                interpretation_en = 'Excellent receivables turnover - fast and effective collection'
                efficiency = 'عالية جداً'
                risk_level = 'منخفض'
            elif turnover >= 8:
                interpretation_ar = 'معدل دوران ذمم جيد - سياسة تحصيل فعالة'
                interpretation_en = 'Good receivables turnover - effective collection policy'
                efficiency = 'جيدة'
                risk_level = 'منخفض'
            elif turnover >= 6:
                interpretation_ar = 'معدل دوران ذمم مقبول - يحتاج لتحسين'
                interpretation_en = 'Acceptable receivables turnover - needs improvement'
                efficiency = 'معتدلة'
                risk_level = 'متوسط'
            elif turnover >= 4:
                interpretation_ar = 'معدل دوران ذمم ضعيف - مشاكل في التحصيل'
                interpretation_en = 'Poor receivables turnover - collection problems'
                efficiency = 'ضعيفة'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'معدل دوران ذمم ضعيف جداً - مخاطر ديون معدومة'
                interpretation_en = 'Very poor receivables turnover - bad debt risks'
                efficiency = 'ضعيفة جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(turnover, 2),
                'collection_days': round(collection_days, 1) if collection_days != float('inf') else 'غير محدود',
                'net_credit_sales': round(net_credit_sales, 2),
                'average_accounts_receivable': round(average_accounts_receivable, 2),
                'formula': 'صافي المبيعات الآجلة ÷ متوسط الذمم المدينة',
                'formula_en': 'Net Credit Sales ÷ Average Accounts Receivable',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 12',
                    'good': '8-11.99',
                    'acceptable': '6-7.99',
                    'poor': '4-5.99',
                    'very_poor': '< 4'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب معدل دوران الذمم المدينة: {str(e)}',
                'error_en': f'Error calculating accounts receivable turnover: {str(e)}'
            }

    def accounts_payable_turnover(self, cost_of_goods_sold: float, average_accounts_payable: float) -> Dict[str, Any]:
        """
        3. معدل دوران الذمم الدائنة
        Accounts Payable Turnover = Cost of Goods Sold / Average Accounts Payable
        """
        try:
            if average_accounts_payable == 0:
                return {
                    'value': None,
                    'formula': 'تكلفة البضاعة المباعة ÷ متوسط الذمم الدائنة',
                    'formula_en': 'Cost of Goods Sold ÷ Average Accounts Payable',
                    'interpretation_ar': 'لا يمكن حساب معدل الدوران - متوسط الذمم الدائنة يساوي صفر',
                    'interpretation_en': 'Cannot calculate turnover - average accounts payable equals zero'
                }

            turnover = cost_of_goods_sold / average_accounts_payable

            # حساب أيام الدفع
            payment_days = 365 / turnover if turnover > 0 else float('inf')

            # تفسير النتائج (أقل أفضل للاستفادة من ائتمان الموردين)
            if turnover <= 4:
                interpretation_ar = 'معدل دوران دائنة ممتاز - استفادة مثلى من ائتمان الموردين'
                interpretation_en = 'Excellent payables turnover - optimal utilization of supplier credit'
                efficiency = 'عالية جداً'
                liquidity_benefit = 'عالي'
                risk_level = 'منخفض'
            elif turnover <= 6:
                interpretation_ar = 'معدل دوران دائنة جيد - استفادة جيدة من ائتمان الموردين'
                interpretation_en = 'Good payables turnover - good utilization of supplier credit'
                efficiency = 'جيدة'
                liquidity_benefit = 'جيد'
                risk_level = 'منخفض'
            elif turnover <= 8:
                interpretation_ar = 'معدل دوران دائنة مقبول - يمكن تحسين الاستفادة من الائتمان'
                interpretation_en = 'Acceptable payables turnover - can improve credit utilization'
                efficiency = 'معتدلة'
                liquidity_benefit = 'معتدل'
                risk_level = 'متوسط'
            elif turnover <= 12:
                interpretation_ar = 'معدل دوران دائنة سريع - ضغط على السيولة'
                interpretation_en = 'Fast payables turnover - pressure on liquidity'
                efficiency = 'ضعيفة'
                liquidity_benefit = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'معدل دوران دائنة سريع جداً - ضغط شديد على السيولة'
                interpretation_en = 'Very fast payables turnover - severe pressure on liquidity'
                efficiency = 'ضعيفة جداً'
                liquidity_benefit = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(turnover, 2),
                'payment_days': round(payment_days, 1) if payment_days != float('inf') else 'غير محدود',
                'cost_of_goods_sold': round(cost_of_goods_sold, 2),
                'average_accounts_payable': round(average_accounts_payable, 2),
                'formula': 'تكلفة البضاعة المباعة ÷ متوسط الذمم الدائنة',
                'formula_en': 'Cost of Goods Sold ÷ Average Accounts Payable',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'liquidity_benefit': liquidity_benefit,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 4',
                    'good': '4.01-6',
                    'acceptable': '6.01-8',
                    'poor': '8.01-12',
                    'very_poor': '> 12'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب معدل دوران الذمم الدائنة: {str(e)}',
                'error_en': f'Error calculating accounts payable turnover: {str(e)}'
            }

    def total_asset_turnover(self, revenue: float, average_total_assets: float) -> Dict[str, Any]:
        """
        4. معدل دوران إجمالي الأصول
        Total Asset Turnover = Revenue / Average Total Assets
        """
        try:
            if average_total_assets == 0:
                return {
                    'value': None,
                    'formula': 'الإيرادات ÷ متوسط إجمالي الأصول',
                    'formula_en': 'Revenue ÷ Average Total Assets',
                    'interpretation_ar': 'لا يمكن حساب معدل الدوران - متوسط إجمالي الأصول يساوي صفر',
                    'interpretation_en': 'Cannot calculate turnover - average total assets equals zero'
                }

            turnover = revenue / average_total_assets

            # تفسير النتائج
            if turnover >= 2.5:
                interpretation_ar = 'معدل دوران أصول ممتاز - كفاءة عالية في استغلال الأصول'
                interpretation_en = 'Excellent asset turnover - high efficiency in asset utilization'
                efficiency = 'عالية جداً'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif turnover >= 1.5:
                interpretation_ar = 'معدل دوران أصول جيد - استغلال فعال للأصول'
                interpretation_en = 'Good asset turnover - effective asset utilization'
                efficiency = 'جيدة'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif turnover >= 1.0:
                interpretation_ar = 'معدل دوران أصول مقبول - يحتاج لتحسين الكفاءة'
                interpretation_en = 'Acceptable asset turnover - needs efficiency improvement'
                efficiency = 'معتدلة'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif turnover >= 0.5:
                interpretation_ar = 'معدل دوران أصول ضعيف - ضعف في استغلال الأصول'
                interpretation_en = 'Poor asset turnover - weak asset utilization'
                efficiency = 'ضعيفة'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'معدل دوران أصول ضعيف جداً - مشاكل جدية في الكفاءة'
                interpretation_en = 'Very poor asset turnover - serious efficiency problems'
                efficiency = 'ضعيفة جداً'
                performance = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(turnover, 2),
                'revenue': round(revenue, 2),
                'average_total_assets': round(average_total_assets, 2),
                'formula': 'الإيرادات ÷ متوسط إجمالي الأصول',
                'formula_en': 'Revenue ÷ Average Total Assets',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 2.5',
                    'good': '1.5-2.49',
                    'acceptable': '1.0-1.49',
                    'poor': '0.5-0.99',
                    'very_poor': '< 0.5'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب معدل دوران إجمالي الأصول: {str(e)}',
                'error_en': f'Error calculating total asset turnover: {str(e)}'
            }

    def fixed_asset_turnover(self, revenue: float, average_fixed_assets: float) -> Dict[str, Any]:
        """
        5. معدل دوران الأصول الثابتة
        Fixed Asset Turnover = Revenue / Average Fixed Assets
        """
        try:
            if average_fixed_assets == 0:
                return {
                    'value': None,
                    'formula': 'الإيرادات ÷ متوسط الأصول الثابتة',
                    'formula_en': 'Revenue ÷ Average Fixed Assets',
                    'interpretation_ar': 'لا يمكن حساب معدل الدوران - متوسط الأصول الثابتة يساوي صفر',
                    'interpretation_en': 'Cannot calculate turnover - average fixed assets equals zero'
                }

            turnover = revenue / average_fixed_assets

            # تفسير النتائج
            if turnover >= 5:
                interpretation_ar = 'معدل دوران أصول ثابتة ممتاز - استغلال عالي الكفاءة'
                interpretation_en = 'Excellent fixed asset turnover - highly efficient utilization'
                efficiency = 'عالية جداً'
                productivity = 'عالية جداً'
                risk_level = 'منخفض'
            elif turnover >= 3:
                interpretation_ar = 'معدل دوران أصول ثابتة جيد - استغلال فعال'
                interpretation_en = 'Good fixed asset turnover - effective utilization'
                efficiency = 'جيدة'
                productivity = 'جيدة'
                risk_level = 'منخفض'
            elif turnover >= 2:
                interpretation_ar = 'معدل دوران أصول ثابتة مقبول - يحتاج لتحسين'
                interpretation_en = 'Acceptable fixed asset turnover - needs improvement'
                efficiency = 'معتدلة'
                productivity = 'معتدلة'
                risk_level = 'متوسط'
            elif turnover >= 1:
                interpretation_ar = 'معدل دوران أصول ثابتة ضعيف - ضعف في الإنتاجية'
                interpretation_en = 'Poor fixed asset turnover - weak productivity'
                efficiency = 'ضعيفة'
                productivity = 'ضعيفة'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'معدل دوران أصول ثابتة ضعيف جداً - أصول خاملة'
                interpretation_en = 'Very poor fixed asset turnover - idle assets'
                efficiency = 'ضعيفة جداً'
                productivity = 'ضعيفة جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(turnover, 2),
                'revenue': round(revenue, 2),
                'average_fixed_assets': round(average_fixed_assets, 2),
                'formula': 'الإيرادات ÷ متوسط الأصول الثابتة',
                'formula_en': 'Revenue ÷ Average Fixed Assets',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'productivity': productivity,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 5',
                    'good': '3-4.99',
                    'acceptable': '2-2.99',
                    'poor': '1-1.99',
                    'very_poor': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب معدل دوران الأصول الثابتة: {str(e)}',
                'error_en': f'Error calculating fixed asset turnover: {str(e)}'
            }

    def working_capital_turnover(self, revenue: float, average_working_capital: float) -> Dict[str, Any]:
        """
        6. معدل دوران رأس المال العامل
        Working Capital Turnover = Revenue / Average Working Capital
        """
        try:
            if average_working_capital == 0:
                return {
                    'value': None,
                    'formula': 'الإيرادات ÷ متوسط رأس المال العامل',
                    'formula_en': 'Revenue ÷ Average Working Capital',
                    'interpretation_ar': 'لا يمكن حساب معدل الدوران - متوسط رأس المال العامل يساوي صفر',
                    'interpretation_en': 'Cannot calculate turnover - average working capital equals zero'
                }

            turnover = revenue / average_working_capital

            # تفسير النتائج
            if turnover >= 8:
                interpretation_ar = 'معدل دوران رأس مال عامل ممتاز - كفاءة عالية في إدارة السيولة'
                interpretation_en = 'Excellent working capital turnover - high efficiency in liquidity management'
                efficiency = 'عالية جداً'
                liquidity_management = 'ممتاز'
                risk_level = 'منخفض'
            elif turnover >= 5:
                interpretation_ar = 'معدل دوران رأس مال عامل جيد - إدارة فعالة للسيولة'
                interpretation_en = 'Good working capital turnover - effective liquidity management'
                efficiency = 'جيدة'
                liquidity_management = 'جيد'
                risk_level = 'منخفض'
            elif turnover >= 3:
                interpretation_ar = 'معدل دوران رأس مال عامل مقبول - يحتاج لتحسين'
                interpretation_en = 'Acceptable working capital turnover - needs improvement'
                efficiency = 'معتدلة'
                liquidity_management = 'مقبول'
                risk_level = 'متوسط'
            elif turnover >= 1:
                interpretation_ar = 'معدل دوران رأس مال عامل ضعيف - ضعف في إدارة السيولة'
                interpretation_en = 'Poor working capital turnover - weak liquidity management'
                efficiency = 'ضعيفة'
                liquidity_management = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'معدل دوران رأس مال عامل ضعيف جداً - مشاكل في إدارة السيولة'
                interpretation_en = 'Very poor working capital turnover - liquidity management problems'
                efficiency = 'ضعيفة جداً'
                liquidity_management = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(turnover, 2),
                'revenue': round(revenue, 2),
                'average_working_capital': round(average_working_capital, 2),
                'formula': 'الإيرادات ÷ متوسط رأس المال العامل',
                'formula_en': 'Revenue ÷ Average Working Capital',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'liquidity_management': liquidity_management,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 8',
                    'good': '5-7.99',
                    'acceptable': '3-4.99',
                    'poor': '1-2.99',
                    'very_poor': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب معدل دوران رأس المال العامل: {str(e)}',
                'error_en': f'Error calculating working capital turnover: {str(e)}'
            }

    def cash_conversion_cycle(self, days_inventory: float, days_receivables: float, days_payables: float) -> Dict[str, Any]:
        """
        7. دورة تحويل النقد
        Cash Conversion Cycle = Days Inventory Outstanding + Days Sales Outstanding - Days Payable Outstanding
        """
        try:
            ccc = days_inventory + days_receivables - days_payables

            # تفسير النتائج
            if ccc <= 30:
                interpretation_ar = 'دورة تحويل نقد ممتازة - كفاءة عالية في إدارة النقد'
                interpretation_en = 'Excellent cash conversion cycle - high efficiency in cash management'
                efficiency = 'عالية جداً'
                cash_management = 'ممتاز'
                risk_level = 'منخفض'
            elif ccc <= 60:
                interpretation_ar = 'دورة تحويل نقد جيدة - إدارة فعالة للنقد'
                interpretation_en = 'Good cash conversion cycle - effective cash management'
                efficiency = 'جيدة'
                cash_management = 'جيد'
                risk_level = 'منخفض'
            elif ccc <= 90:
                interpretation_ar = 'دورة تحويل نقد مقبولة - يحتاج لتحسين'
                interpretation_en = 'Acceptable cash conversion cycle - needs improvement'
                efficiency = 'معتدلة'
                cash_management = 'مقبول'
                risk_level = 'متوسط'
            elif ccc <= 120:
                interpretation_ar = 'دورة تحويل نقد طويلة - ضغط على السيولة'
                interpretation_en = 'Long cash conversion cycle - pressure on liquidity'
                efficiency = 'ضعيفة'
                cash_management = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'دورة تحويل نقد طويلة جداً - مخاطر سيولة عالية'
                interpretation_en = 'Very long cash conversion cycle - high liquidity risks'
                efficiency = 'ضعيفة جداً'
                cash_management = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            # تحليل المكونات
            component_analysis = {
                'inventory_component': {
                    'days': round(days_inventory, 1),
                    'percentage': round((days_inventory / (days_inventory + days_receivables)) * 100, 1) if (days_inventory + days_receivables) > 0 else 0,
                    'impact': 'إيجابي' if days_inventory > 0 else 'معدوم'
                },
                'receivables_component': {
                    'days': round(days_receivables, 1),
                    'percentage': round((days_receivables / (days_inventory + days_receivables)) * 100, 1) if (days_inventory + days_receivables) > 0 else 0,
                    'impact': 'إيجابي' if days_receivables > 0 else 'معدوم'
                },
                'payables_component': {
                    'days': round(days_payables, 1),
                    'impact': 'سلبي (مفيد)' if days_payables > 0 else 'معدوم'
                }
            }

            return {
                'value': round(ccc, 1),
                'days_inventory': round(days_inventory, 1),
                'days_receivables': round(days_receivables, 1),
                'days_payables': round(days_payables, 1),
                'component_analysis': component_analysis,
                'formula': 'أيام المخزون + أيام الذمم المدينة - أيام الذمم الدائنة',
                'formula_en': 'Days Inventory Outstanding + Days Sales Outstanding - Days Payable Outstanding',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'cash_management': cash_management,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 30 يوم',
                    'good': '31-60 يوم',
                    'acceptable': '61-90 يوم',
                    'poor': '91-120 يوم',
                    'very_poor': '> 120 يوم'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب دورة تحويل النقد: {str(e)}',
                'error_en': f'Error calculating cash conversion cycle: {str(e)}'
            }

    def receivables_to_sales_ratio(self, accounts_receivable: float, revenue: float) -> Dict[str, Any]:
        """
        8. نسبة الذمم المدينة إلى المبيعات
        Receivables to Sales Ratio = (Accounts Receivable / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(الذمم المدينة ÷ الإيرادات) × 100',
                    'formula_en': '(Accounts Receivable ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - revenue equals zero'
                }

            ratio = (accounts_receivable / revenue) * 100

            # تفسير النتائج
            if ratio <= 8:
                interpretation_ar = 'نسبة ذمم ممتازة - تحصيل فعال وسريع'
                interpretation_en = 'Excellent receivables ratio - effective and fast collection'
                collection_efficiency = 'عالية جداً'
                credit_policy = 'ممتاز'
                risk_level = 'منخفض'
            elif ratio <= 15:
                interpretation_ar = 'نسبة ذمم جيدة - سياسة ائتمان فعالة'
                interpretation_en = 'Good receivables ratio - effective credit policy'
                collection_efficiency = 'جيدة'
                credit_policy = 'جيد'
                risk_level = 'منخفض'
            elif ratio <= 25:
                interpretation_ar = 'نسبة ذمم مقبولة - يحتاج لتحسين التحصيل'
                interpretation_en = 'Acceptable receivables ratio - needs collection improvement'
                collection_efficiency = 'معتدلة'
                credit_policy = 'مقبول'
                risk_level = 'متوسط'
            elif ratio <= 35:
                interpretation_ar = 'نسبة ذمم مرتفعة - مشاكل في التحصيل'
                interpretation_en = 'High receivables ratio - collection problems'
                collection_efficiency = 'ضعيفة'
                credit_policy = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'نسبة ذمم مرتفعة جداً - مخاطر ديون معدومة'
                interpretation_en = 'Very high receivables ratio - bad debt risks'
                collection_efficiency = 'ضعيفة جداً'
                credit_policy = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2f}%",
                'accounts_receivable': round(accounts_receivable, 2),
                'revenue': round(revenue, 2),
                'formula': '(الذمم المدينة ÷ الإيرادات) × 100',
                'formula_en': '(Accounts Receivable ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'collection_efficiency': collection_efficiency,
                'credit_policy': credit_policy,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 8%',
                    'good': '8.01-15%',
                    'acceptable': '15.01-25%',
                    'poor': '25.01-35%',
                    'very_poor': '> 35%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة الذمم المدينة إلى المبيعات: {str(e)}',
                'error_en': f'Error calculating receivables to sales ratio: {str(e)}'
            }

    def inventory_to_sales_ratio(self, inventory: float, revenue: float) -> Dict[str, Any]:
        """
        9. نسبة المخزون إلى المبيعات
        Inventory to Sales Ratio = (Inventory / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(المخزون ÷ الإيرادات) × 100',
                    'formula_en': '(Inventory ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - revenue equals zero'
                }

            ratio = (inventory / revenue) * 100

            # تفسير النتائج
            if ratio <= 10:
                interpretation_ar = 'نسبة مخزون ممتازة - إدارة مخزون عالية الكفاءة'
                interpretation_en = 'Excellent inventory ratio - highly efficient inventory management'
                inventory_management = 'ممتاز'
                efficiency = 'عالية جداً'
                risk_level = 'منخفض'
            elif ratio <= 20:
                interpretation_ar = 'نسبة مخزون جيدة - إدارة مخزون فعالة'
                interpretation_en = 'Good inventory ratio - effective inventory management'
                inventory_management = 'جيد'
                efficiency = 'جيدة'
                risk_level = 'منخفض'
            elif ratio <= 30:
                interpretation_ar = 'نسبة مخزون مقبولة - يحتاج لتحسين الإدارة'
                interpretation_en = 'Acceptable inventory ratio - needs management improvement'
                inventory_management = 'مقبول'
                efficiency = 'معتدلة'
                risk_level = 'متوسط'
            elif ratio <= 40:
                interpretation_ar = 'نسبة مخزون مرتفعة - مخاطر تراكم المخزون'
                interpretation_en = 'High inventory ratio - inventory accumulation risks'
                inventory_management = 'ضعيف'
                efficiency = 'ضعيفة'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'نسبة مخزون مرتفعة جداً - مشاكل جدية في إدارة المخزون'
                interpretation_en = 'Very high inventory ratio - serious inventory management problems'
                inventory_management = 'ضعيف جداً'
                efficiency = 'ضعيفة جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2f}%",
                'inventory': round(inventory, 2),
                'revenue': round(revenue, 2),
                'formula': '(المخزون ÷ الإيرادات) × 100',
                'formula_en': '(Inventory ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'inventory_management': inventory_management,
                'efficiency': efficiency,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 10%',
                    'good': '10.01-20%',
                    'acceptable': '20.01-30%',
                    'poor': '30.01-40%',
                    'very_poor': '> 40%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة المخزون إلى المبيعات: {str(e)}',
                'error_en': f'Error calculating inventory to sales ratio: {str(e)}'
            }

    def operating_cycle(self, days_inventory: float, days_receivables: float) -> Dict[str, Any]:
        """
        10. الدورة التشغيلية
        Operating Cycle = Days Inventory Outstanding + Days Sales Outstanding
        """
        try:
            operating_cycle = days_inventory + days_receivables

            # تفسير النتائج
            if operating_cycle <= 60:
                interpretation_ar = 'دورة تشغيلية ممتازة - كفاءة عالية في العمليات'
                interpretation_en = 'Excellent operating cycle - high operational efficiency'
                efficiency = 'عالية جداً'
                operational_management = 'ممتاز'
                risk_level = 'منخفض'
            elif operating_cycle <= 90:
                interpretation_ar = 'دورة تشغيلية جيدة - إدارة فعالة للعمليات'
                interpretation_en = 'Good operating cycle - effective operational management'
                efficiency = 'جيدة'
                operational_management = 'جيد'
                risk_level = 'منخفض'
            elif operating_cycle <= 120:
                interpretation_ar = 'دورة تشغيلية مقبولة - يحتاج لتحسين'
                interpretation_en = 'Acceptable operating cycle - needs improvement'
                efficiency = 'معتدلة'
                operational_management = 'مقبول'
                risk_level = 'متوسط'
            elif operating_cycle <= 150:
                interpretation_ar = 'دورة تشغيلية طويلة - ضعف في كفاءة العمليات'
                interpretation_en = 'Long operating cycle - weak operational efficiency'
                efficiency = 'ضعيفة'
                operational_management = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'دورة تشغيلية طويلة جداً - مشاكل جدية في العمليات'
                interpretation_en = 'Very long operating cycle - serious operational problems'
                efficiency = 'ضعيفة جداً'
                operational_management = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            # تحليل المكونات
            inventory_contribution = (days_inventory / operating_cycle) * 100 if operating_cycle > 0 else 0
            receivables_contribution = (days_receivables / operating_cycle) * 100 if operating_cycle > 0 else 0

            return {
                'value': round(operating_cycle, 1),
                'days_inventory': round(days_inventory, 1),
                'days_receivables': round(days_receivables, 1),
                'inventory_contribution': round(inventory_contribution, 1),
                'receivables_contribution': round(receivables_contribution, 1),
                'formula': 'أيام المخزون + أيام الذمم المدينة',
                'formula_en': 'Days Inventory Outstanding + Days Sales Outstanding',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'operational_management': operational_management,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 60 يوم',
                    'good': '61-90 يوم',
                    'acceptable': '91-120 يوم',
                    'poor': '121-150 يوم',
                    'very_poor': '> 150 يوم'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب الدورة التشغيلية: {str(e)}',
                'error_en': f'Error calculating operating cycle: {str(e)}'
            }

    def employee_productivity(self, revenue: float, number_of_employees: float) -> Dict[str, Any]:
        """
        11. إنتاجية الموظف
        Employee Productivity = Revenue / Number of Employees
        """
        try:
            if number_of_employees == 0:
                return {
                    'value': None,
                    'formula': 'الإيرادات ÷ عدد الموظفين',
                    'formula_en': 'Revenue ÷ Number of Employees',
                    'interpretation_ar': 'لا يمكن حساب الإنتاجية - عدد الموظفين يساوي صفر',
                    'interpretation_en': 'Cannot calculate productivity - number of employees equals zero'
                }

            productivity = revenue / number_of_employees

            # تفسير النتائج (يختلف حسب الصناعة)
            if productivity >= 500000:
                interpretation_ar = 'إنتاجية موظف ممتازة - كفاءة عالية جداً'
                interpretation_en = 'Excellent employee productivity - very high efficiency'
                efficiency = 'عالية جداً'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif productivity >= 300000:
                interpretation_ar = 'إنتاجية موظف جيدة - كفاءة عالية'
                interpretation_en = 'Good employee productivity - high efficiency'
                efficiency = 'جيدة'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif productivity >= 200000:
                interpretation_ar = 'إنتاجية موظف مقبولة - كفاءة معتدلة'
                interpretation_en = 'Acceptable employee productivity - moderate efficiency'
                efficiency = 'معتدلة'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif productivity >= 100000:
                interpretation_ar = 'إنتاجية موظف ضعيفة - كفاءة منخفضة'
                interpretation_en = 'Poor employee productivity - low efficiency'
                efficiency = 'ضعيفة'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'إنتاجية موظف ضعيفة جداً - مشاكل في الكفاءة'
                interpretation_en = 'Very poor employee productivity - efficiency problems'
                efficiency = 'ضعيفة جداً'
                performance = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(productivity, 2),
                'revenue': round(revenue, 2),
                'number_of_employees': round(number_of_employees, 0),
                'formula': 'الإيرادات ÷ عدد الموظفين',
                'formula_en': 'Revenue ÷ Number of Employees',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 500,000',
                    'good': '300,000-499,999',
                    'acceptable': '200,000-299,999',
                    'poor': '100,000-199,999',
                    'very_poor': '< 100,000'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب إنتاجية الموظف: {str(e)}',
                'error_en': f'Error calculating employee productivity: {str(e)}'
            }

    def cost_efficiency_ratio(self, total_costs: float, revenue: float) -> Dict[str, Any]:
        """
        12. نسبة كفاءة التكلفة
        Cost Efficiency Ratio = (Total Costs / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(إجمالي التكاليف ÷ الإيرادات) × 100',
                    'formula_en': '(Total Costs ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - revenue equals zero'
                }

            ratio = (total_costs / revenue) * 100

            # تفسير النتائج (أقل أفضل)
            if ratio <= 60:
                interpretation_ar = 'كفاءة تكلفة ممتازة - تحكم ممتاز في التكاليف'
                interpretation_en = 'Excellent cost efficiency - excellent cost control'
                efficiency = 'عالية جداً'
                cost_control = 'ممتاز'
                profitability_potential = 'عالي'
                risk_level = 'منخفض'
            elif ratio <= 75:
                interpretation_ar = 'كفاءة تكلفة جيدة - تحكم جيد في التكاليف'
                interpretation_en = 'Good cost efficiency - good cost control'
                efficiency = 'جيدة'
                cost_control = 'جيد'
                profitability_potential = 'جيد'
                risk_level = 'منخفض'
            elif ratio <= 85:
                interpretation_ar = 'كفاءة تكلفة مقبولة - يحتاج لتحسين التحكم في التكاليف'
                interpretation_en = 'Acceptable cost efficiency - needs cost control improvement'
                efficiency = 'معتدلة'
                cost_control = 'مقبول'
                profitability_potential = 'معتدل'
                risk_level = 'متوسط'
            elif ratio <= 95:
                interpretation_ar = 'كفاءة تكلفة ضعيفة - ضعف في التحكم بالتكاليف'
                interpretation_en = 'Poor cost efficiency - weak cost control'
                efficiency = 'ضعيفة'
                cost_control = 'ضعيف'
                profitability_potential = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'كفاءة تكلفة ضعيفة جداً - مشاكل جدية في التحكم بالتكاليف'
                interpretation_en = 'Very poor cost efficiency - serious cost control problems'
                efficiency = 'ضعيفة جداً'
                cost_control = 'ضعيف جداً'
                profitability_potential = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            # حساب هامش التكلفة المتاح
            margin_available = 100 - ratio

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2f}%",
                'margin_available': round(margin_available, 2),
                'total_costs': round(total_costs, 2),
                'revenue': round(revenue, 2),
                'formula': '(إجمالي التكاليف ÷ الإيرادات) × 100',
                'formula_en': '(Total Costs ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'cost_control': cost_control,
                'profitability_potential': profitability_potential,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 60%',
                    'good': '60.01-75%',
                    'acceptable': '75.01-85%',
                    'poor': '85.01-95%',
                    'very_poor': '> 95%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة كفاءة التكلفة: {str(e)}',
                'error_en': f'Error calculating cost efficiency ratio: {str(e)}'
            }

    def sales_per_square_meter(self, revenue: float, floor_area: float) -> Dict[str, Any]:
        """
        13. المبيعات لكل متر مربع
        Sales per Square Meter = Revenue / Floor Area (m²)
        """
        try:
            if floor_area == 0:
                return {
                    'value': None,
                    'formula': 'الإيرادات ÷ المساحة (متر مربع)',
                    'formula_en': 'Revenue ÷ Floor Area (m²)',
                    'interpretation_ar': 'لا يمكن حساب المبيعات لكل متر - المساحة تساوي صفر',
                    'interpretation_en': 'Cannot calculate sales per square meter - floor area equals zero'
                }

            sales_per_sqm = revenue / floor_area

            # تفسير النتائج (يختلف حسب نوع المتجر/الصناعة)
            if sales_per_sqm >= 10000:
                interpretation_ar = 'مبيعات ممتازة لكل متر مربع - استغلال مثالي للمساحة'
                interpretation_en = 'Excellent sales per square meter - optimal space utilization'
                space_efficiency = 'عالية جداً'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif sales_per_sqm >= 7500:
                interpretation_ar = 'مبيعات جيدة لكل متر مربع - استغلال فعال للمساحة'
                interpretation_en = 'Good sales per square meter - effective space utilization'
                space_efficiency = 'جيدة'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif sales_per_sqm >= 5000:
                interpretation_ar = 'مبيعات مقبولة لكل متر مربع - يحتاج لتحسين'
                interpretation_en = 'Acceptable sales per square meter - needs improvement'
                space_efficiency = 'معتدلة'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif sales_per_sqm >= 2500:
                interpretation_ar = 'مبيعات ضعيفة لكل متر مربع - استغلال ضعيف للمساحة'
                interpretation_en = 'Poor sales per square meter - weak space utilization'
                space_efficiency = 'ضعيفة'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'مبيعات ضعيفة جداً لكل متر مربع - مشاكل في استغلال المساحة'
                interpretation_en = 'Very poor sales per square meter - space utilization problems'
                space_efficiency = 'ضعيفة جداً'
                performance = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(sales_per_sqm, 2),
                'revenue': round(revenue, 2),
                'floor_area': round(floor_area, 2),
                'formula': 'الإيرادات ÷ المساحة (متر مربع)',
                'formula_en': 'Revenue ÷ Floor Area (m²)',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'space_efficiency': space_efficiency,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 10,000',
                    'good': '7,500-9,999',
                    'acceptable': '5,000-7,499',
                    'poor': '2,500-4,999',
                    'very_poor': '< 2,500'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب المبيعات لكل متر مربع: {str(e)}',
                'error_en': f'Error calculating sales per square meter: {str(e)}'
            }

    def marketing_efficiency_ratio(self, marketing_expenses: float, revenue: float) -> Dict[str, Any]:
        """
        14. نسبة كفاءة التسويق
        Marketing Efficiency Ratio = (Marketing Expenses / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(مصروفات التسويق ÷ الإيرادات) × 100',
                    'formula_en': '(Marketing Expenses ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - revenue equals zero'
                }

            ratio = (marketing_expenses / revenue) * 100

            # تفسير النتائج
            if ratio <= 3:
                interpretation_ar = 'كفاءة تسويق ممتازة - عائد عالي على الاستثمار التسويقي'
                interpretation_en = 'Excellent marketing efficiency - high ROI on marketing investment'
                efficiency = 'عالية جداً'
                marketing_performance = 'ممتاز'
                roi_potential = 'عالي'
                risk_level = 'منخفض'
            elif ratio <= 6:
                interpretation_ar = 'كفاءة تسويق جيدة - عائد جيد على الاستثمار التسويقي'
                interpretation_en = 'Good marketing efficiency - good ROI on marketing investment'
                efficiency = 'جيدة'
                marketing_performance = 'جيد'
                roi_potential = 'جيد'
                risk_level = 'منخفض'
            elif ratio <= 10:
                interpretation_ar = 'كفاءة تسويق مقبولة - يحتاج لتحسين الفعالية'
                interpretation_en = 'Acceptable marketing efficiency - needs effectiveness improvement'
                efficiency = 'معتدلة'
                marketing_performance = 'مقبول'
                roi_potential = 'معتدل'
                risk_level = 'متوسط'
            elif ratio <= 15:
                interpretation_ar = 'كفاءة تسويق ضعيفة - عائد منخفض على الاستثمار'
                interpretation_en = 'Poor marketing efficiency - low ROI on investment'
                efficiency = 'ضعيفة'
                marketing_performance = 'ضعيف'
                roi_potential = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'كفاءة تسويق ضعيفة جداً - مشاكل في الاستراتيجية التسويقية'
                interpretation_en = 'Very poor marketing efficiency - marketing strategy problems'
                efficiency = 'ضعيفة جداً'
                marketing_performance = 'ضعيف جداً'
                roi_potential = 'ضعيف جداً'
                risk_level = 'عالي جداً'

            # حساب العائد على الاستثمار التسويقي
            marketing_roi = ((revenue - marketing_expenses) / marketing_expenses) * 100 if marketing_expenses > 0 else 0

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2f}%",
                'marketing_roi': round(marketing_roi, 2),
                'marketing_expenses': round(marketing_expenses, 2),
                'revenue': round(revenue, 2),
                'formula': '(مصروفات التسويق ÷ الإيرادات) × 100',
                'formula_en': '(Marketing Expenses ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'marketing_performance': marketing_performance,
                'roi_potential': roi_potential,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 3%',
                    'good': '3.01-6%',
                    'acceptable': '6.01-10%',
                    'poor': '10.01-15%',
                    'very_poor': '> 15%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة كفاءة التسويق: {str(e)}',
                'error_en': f'Error calculating marketing efficiency ratio: {str(e)}'
            }

    def operating_expense_ratio(self, operating_expenses: float, revenue: float) -> Dict[str, Any]:
        """
        15. نسبة المصروفات التشغيلية
        Operating Expense Ratio = (Operating Expenses / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(المصروفات التشغيلية ÷ الإيرادات) × 100',
                    'formula_en': '(Operating Expenses ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - revenue equals zero'
                }

            ratio = (operating_expenses / revenue) * 100

            # تفسير النتائج
            if ratio <= 20:
                interpretation_ar = 'نسبة مصروفات تشغيلية ممتازة - كفاءة عالية في العمليات'
                interpretation_en = 'Excellent operating expense ratio - high operational efficiency'
                efficiency = 'عالية جداً'
                cost_control = 'ممتاز'
                profitability_impact = 'إيجابي عالي'
                risk_level = 'منخفض'
            elif ratio <= 35:
                interpretation_ar = 'نسبة مصروفات تشغيلية جيدة - كفاءة جيدة في العمليات'
                interpretation_en = 'Good operating expense ratio - good operational efficiency'
                efficiency = 'جيدة'
                cost_control = 'جيد'
                profitability_impact = 'إيجابي'
                risk_level = 'منخفض'
            elif ratio <= 50:
                interpretation_ar = 'نسبة مصروفات تشغيلية مقبولة - يحتاج لتحسين الكفاءة'
                interpretation_en = 'Acceptable operating expense ratio - needs efficiency improvement'
                efficiency = 'معتدلة'
                cost_control = 'مقبول'
                profitability_impact = 'محايد'
                risk_level = 'متوسط'
            elif ratio <= 65:
                interpretation_ar = 'نسبة مصروفات تشغيلية مرتفعة - ضعف في كفاءة العمليات'
                interpretation_en = 'High operating expense ratio - weak operational efficiency'
                efficiency = 'ضعيفة'
                cost_control = 'ضعيف'
                profitability_impact = 'سلبي'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'نسبة مصروفات تشغيلية مرتفعة جداً - مشاكل جدية في الكفاءة'
                interpretation_en = 'Very high operating expense ratio - serious efficiency problems'
                efficiency = 'ضعيفة جداً'
                cost_control = 'ضعيف جداً'
                profitability_impact = 'سلبي عالي'
                risk_level = 'عالي جداً'

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2f}%",
                'operating_expenses': round(operating_expenses, 2),
                'revenue': round(revenue, 2),
                'formula': '(المصروفات التشغيلية ÷ الإيرادات) × 100',
                'formula_en': '(Operating Expenses ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'efficiency': efficiency,
                'cost_control': cost_control,
                'profitability_impact': profitability_impact,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≤ 20%',
                    'good': '20.01-35%',
                    'acceptable': '35.01-50%',
                    'poor': '50.01-65%',
                    'very_poor': '> 65%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة المصروفات التشغيلية: {str(e)}',
                'error_en': f'Error calculating operating expense ratio: {str(e)}'
            }

    def comprehensive_efficiency_analysis(self, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """تحليل شامل للكفاءة"""
        try:
            results = {}

            # 1. معدل دوران المخزون
            if all(k in financial_data for k in ['cost_of_goods_sold', 'average_inventory']):
                results['inventory_turnover'] = self.inventory_turnover(
                    financial_data['cost_of_goods_sold'],
                    financial_data['average_inventory']
                )

            # 2. معدل دوران الذمم المدينة
            if all(k in financial_data for k in ['net_credit_sales', 'average_accounts_receivable']):
                results['accounts_receivable_turnover'] = self.accounts_receivable_turnover(
                    financial_data['net_credit_sales'],
                    financial_data['average_accounts_receivable']
                )

            # 3. معدل دوران الذمم الدائنة
            if all(k in financial_data for k in ['cost_of_goods_sold', 'average_accounts_payable']):
                results['accounts_payable_turnover'] = self.accounts_payable_turnover(
                    financial_data['cost_of_goods_sold'],
                    financial_data['average_accounts_payable']
                )

            # 4. معدل دوران إجمالي الأصول
            if all(k in financial_data for k in ['revenue', 'average_total_assets']):
                results['total_asset_turnover'] = self.total_asset_turnover(
                    financial_data['revenue'],
                    financial_data['average_total_assets']
                )

            # 5. معدل دوران الأصول الثابتة
            if all(k in financial_data for k in ['revenue', 'average_fixed_assets']):
                results['fixed_asset_turnover'] = self.fixed_asset_turnover(
                    financial_data['revenue'],
                    financial_data['average_fixed_assets']
                )

            # 6. معدل دوران رأس المال العامل
            if all(k in financial_data for k in ['revenue', 'average_working_capital']):
                results['working_capital_turnover'] = self.working_capital_turnover(
                    financial_data['revenue'],
                    financial_data['average_working_capital']
                )

            # 7. دورة تحويل النقد
            if all(k in financial_data for k in ['days_inventory', 'days_receivables', 'days_payables']):
                results['cash_conversion_cycle'] = self.cash_conversion_cycle(
                    financial_data['days_inventory'],
                    financial_data['days_receivables'],
                    financial_data['days_payables']
                )

            # 8. نسبة الذمم المدينة إلى المبيعات
            if all(k in financial_data for k in ['accounts_receivable', 'revenue']):
                results['receivables_to_sales_ratio'] = self.receivables_to_sales_ratio(
                    financial_data['accounts_receivable'],
                    financial_data['revenue']
                )

            # 9. نسبة المخزون إلى المبيعات
            if all(k in financial_data for k in ['inventory', 'revenue']):
                results['inventory_to_sales_ratio'] = self.inventory_to_sales_ratio(
                    financial_data['inventory'],
                    financial_data['revenue']
                )

            # 10. الدورة التشغيلية
            if all(k in financial_data for k in ['days_inventory', 'days_receivables']):
                results['operating_cycle'] = self.operating_cycle(
                    financial_data['days_inventory'],
                    financial_data['days_receivables']
                )

            # 11. إنتاجية الموظف
            if all(k in financial_data for k in ['revenue', 'number_of_employees']):
                results['employee_productivity'] = self.employee_productivity(
                    financial_data['revenue'],
                    financial_data['number_of_employees']
                )

            # 12. نسبة كفاءة التكلفة
            if all(k in financial_data for k in ['total_costs', 'revenue']):
                results['cost_efficiency_ratio'] = self.cost_efficiency_ratio(
                    financial_data['total_costs'],
                    financial_data['revenue']
                )

            # 13. المبيعات لكل متر مربع
            if all(k in financial_data for k in ['revenue', 'floor_area']):
                results['sales_per_square_meter'] = self.sales_per_square_meter(
                    financial_data['revenue'],
                    financial_data['floor_area']
                )

            # 14. نسبة كفاءة التسويق
            if all(k in financial_data for k in ['marketing_expenses', 'revenue']):
                results['marketing_efficiency_ratio'] = self.marketing_efficiency_ratio(
                    financial_data['marketing_expenses'],
                    financial_data['revenue']
                )

            # 15. نسبة المصروفات التشغيلية
            if all(k in financial_data for k in ['operating_expenses', 'revenue']):
                results['operating_expense_ratio'] = self.operating_expense_ratio(
                    financial_data['operating_expenses'],
                    financial_data['revenue']
                )

            # تقييم عام للكفاءة
            overall_assessment = self._assess_overall_efficiency(results)

            return {
                'individual_analyses': results,
                'overall_assessment': overall_assessment,
                'analysis_date': financial_data.get('analysis_date', 'غير محدد'),
                'company_name': financial_data.get('company_name', 'غير محدد')
            }

        except Exception as e:
            return {
                'error': f'خطأ في التحليل الشامل للكفاءة: {str(e)}',
                'error_en': f'Error in comprehensive efficiency analysis: {str(e)}'
            }

    def _assess_overall_efficiency(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم الوضع العام للكفاءة"""
        try:
            scores = []
            efficiencies = []

            # جمع النقاط ومستويات الكفاءة
            for analysis_name, analysis_result in results.items():
                if isinstance(analysis_result, dict) and 'efficiency' in analysis_result:
                    efficiencies.append(analysis_result['efficiency'])

                    # تحويل الكفاءة إلى نقاط
                    if analysis_result['efficiency'] == 'عالية جداً':
                        scores.append(5)
                    elif analysis_result['efficiency'] == 'جيدة':
                        scores.append(4)
                    elif analysis_result['efficiency'] == 'معتدلة':
                        scores.append(3)
                    elif analysis_result['efficiency'] == 'ضعيفة':
                        scores.append(2)
                    else:  # ضعيفة جداً
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
            if average_score >= 4.5:
                overall_rating = 'ممتاز'
                overall_rating_en = 'Excellent'
                recommendation_ar = 'كفاءة ممتازة - الحفاظ على مستوى الأداء والتطوير المستمر'
                recommendation_en = 'Excellent efficiency - maintain performance level and continuous improvement'
            elif average_score >= 3.5:
                overall_rating = 'جيد'
                overall_rating_en = 'Good'
                recommendation_ar = 'كفاءة جيدة - البحث عن فرص تحسين إضافية'
                recommendation_en = 'Good efficiency - seek additional improvement opportunities'
            elif average_score >= 2.5:
                overall_rating = 'مقبول'
                overall_rating_en = 'Acceptable'
                recommendation_ar = 'كفاءة مقبولة - تطوير خطط تحسين الكفاءة'
                recommendation_en = 'Acceptable efficiency - develop efficiency improvement plans'
            elif average_score >= 1.5:
                overall_rating = 'ضعيف'
                overall_rating_en = 'Poor'
                recommendation_ar = 'كفاءة ضعيفة - إعادة هيكلة العمليات والاستراتيجيات'
                recommendation_en = 'Poor efficiency - restructure operations and strategies'
            else:
                overall_rating = 'ضعيف جداً'
                overall_rating_en = 'Very Poor'
                recommendation_ar = 'كفاءة ضعيفة جداً - إجراءات جذرية وعاجلة مطلوبة'
                recommendation_en = 'Very poor efficiency - radical and urgent actions required'

            return {
                'overall_score': round(average_score, 2),
                'overall_rating': overall_rating,
                'overall_rating_en': overall_rating_en,
                'total_analyses': len(scores),
                'efficiency_distribution': {
                    'عالية جداً': efficiencies.count('عالية جداً'),
                    'جيدة': efficiencies.count('جيدة'),
                    'معتدلة': efficiencies.count('معتدلة'),
                    'ضعيفة': efficiencies.count('ضعيفة'),
                    'ضعيفة جداً': efficiencies.count('ضعيفة جداً')
                },
                'recommendation_ar': recommendation_ar,
                'recommendation_en': recommendation_en
            }

        except Exception as e:
            return {
                'error': f'خطأ في تقييم الوضع العام للكفاءة: {str(e)}',
                'error_en': f'Error in overall efficiency assessment: {str(e)}'
            }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مثيل من فئة تحليل الكفاءة
    efficiency_analyzer = EfficiencyAnalysis()

    # بيانات مالية تجريبية
    sample_data = {
        'cost_of_goods_sold': 600000,
        'average_inventory': 100000,
        'net_credit_sales': 800000,
        'average_accounts_receivable': 120000,
        'average_accounts_payable': 80000,
        'revenue': 1000000,
        'average_total_assets': 800000,
        'average_fixed_assets': 500000,
        'average_working_capital': 150000,
        'days_inventory': 60,
        'days_receivables': 45,
        'days_payables': 30,
        'accounts_receivable': 120000,
        'inventory': 100000,
        'number_of_employees': 25,
        'total_costs': 750000,
        'floor_area': 200,
        'marketing_expenses': 50000,
        'operating_expenses': 200000,
        'company_name': 'شركة المثال التجارية',
        'analysis_date': '2024-12-31'
    }

    # تشغيل التحليل الشامل
    comprehensive_results = efficiency_analyzer.comprehensive_efficiency_analysis(sample_data)

    print("=== تحليل الكفاءة الشامل ===")
    print(f"اسم الشركة: {comprehensive_results.get('company_name', 'غير محدد')}")
    print(f"تاريخ التحليل: {comprehensive_results.get('analysis_date', 'غير محدد')}")
    print("\n=== النتائج التفصيلية ===")

    for analysis_name, result in comprehensive_results.get('individual_analyses', {}).items():
        if isinstance(result, dict) and 'value' in result:
            print(f"\n{analysis_name}:")
            print(f"  القيمة: {result.get('value', 'غير محدد')}")
            print(f"  التفسير: {result.get('interpretation_ar', 'غير محدد')}")
            print(f"  الكفاءة: {result.get('efficiency', 'غير محدد')}")

    print(f"\n=== التقييم العام ===")
    overall = comprehensive_results.get('overall_assessment', {})
    print(f"التقييم العام: {overall.get('overall_rating', 'غير محدد')}")
    print(f"النقاط: {overall.get('overall_score', 0)}")
    print(f"التوصية: {overall.get('recommendation_ar', 'غير محدد')}")