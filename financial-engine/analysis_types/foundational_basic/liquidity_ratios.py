"""
نسب السيولة - Liquidity Ratios
يحتوي على 10 نسب سيولة أساسية لتقييم قدرة الشركة على سداد التزاماتها قصيرة الأجل
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# إعداد الخطوط العربية
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Tahoma', 'DejaVu Sans']

class LiquidityRatios:
    """
    فئة نسب السيولة
    Liquidity Ratios Class
    """

    def __init__(self, data: pd.DataFrame):
        """
        تهيئة فئة نسب السيولة
        Initialize Liquidity Ratios Class

        Args:
            data: بيانات القوائم المالية / Financial statements data
        """
        self.data = data.copy()
        self.results = {}

    def current_ratio(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        1. نسبة التداول
        Current Ratio

        Formula: Current Assets / Current Liabilities
        الصيغة: الأصول المتداولة / الخصوم المتداولة
        """
        try:
            required_columns = ['current_assets', 'current_liabilities']
            missing_columns = [col for col in required_columns if col not in balance_sheet.columns]

            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # حساب نسبة التداول
            current_ratio = (balance_sheet['current_assets'] /
                           balance_sheet['current_liabilities']).round(2)

            # تصنيف النسبة
            classification = self._classify_current_ratio(current_ratio)

            # التفسير
            interpretation_ar = self._interpret_current_ratio_ar(current_ratio, classification)
            interpretation_en = self._interpret_current_ratio_en(current_ratio, classification)

            # التوصيات
            recommendations = self._get_current_ratio_recommendations(current_ratio, classification)

            return {
                'analysis_name_ar': 'نسبة التداول',
                'analysis_name_en': 'Current Ratio',
                'result': current_ratio,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة التداول = الأصول المتداولة ÷ الخصوم المتداولة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '2.0 - 3.0',
                    'good': '1.5 - 2.0',
                    'acceptable': '1.2 - 1.5',
                    'weak': '1.0 - 1.2',
                    'poor': '< 1.0'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة التداول: {str(e)}'}

    def quick_ratio(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        2. نسبة السيولة السريعة (الاختبار الحمضي)
        Quick Ratio (Acid Test)

        Formula: (Current Assets - Inventory) / Current Liabilities
        الصيغة: (الأصول المتداولة - المخزون) / الخصوم المتداولة
        """
        try:
            required_columns = ['current_assets', 'current_liabilities', 'inventory']
            missing_columns = [col for col in required_columns if col not in balance_sheet.columns]

            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # حساب نسبة السيولة السريعة
            quick_assets = balance_sheet['current_assets'] - balance_sheet['inventory']
            quick_ratio = (quick_assets / balance_sheet['current_liabilities']).round(2)

            # تصنيف النسبة
            classification = self._classify_quick_ratio(quick_ratio)

            # التفسير
            interpretation_ar = self._interpret_quick_ratio_ar(quick_ratio, classification)
            interpretation_en = self._interpret_quick_ratio_en(quick_ratio, classification)

            # التوصيات
            recommendations = self._get_quick_ratio_recommendations(quick_ratio, classification)

            return {
                'analysis_name_ar': 'نسبة السيولة السريعة (الاختبار الحمضي)',
                'analysis_name_en': 'Quick Ratio (Acid Test)',
                'result': quick_ratio,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة السيولة السريعة = (الأصول المتداولة - المخزون) ÷ الخصوم المتداولة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 1.5',
                    'good': '1.2 - 1.5',
                    'acceptable': '1.0 - 1.2',
                    'weak': '0.8 - 1.0',
                    'poor': '< 0.8'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة السيولة السريعة: {str(e)}'}

    def cash_ratio(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        3. نسبة النقدية
        Cash Ratio

        Formula: (Cash + Short-term Investments) / Current Liabilities
        الصيغة: (النقد + الاستثمارات قصيرة الأجل) / الخصوم المتداولة
        """
        try:
            required_columns = ['cash_and_equivalents', 'current_liabilities']
            optional_columns = ['short_term_investments']

            missing_required = [col for col in required_columns if col not in balance_sheet.columns]
            if missing_required:
                raise ValueError(f"Missing required columns: {missing_required}")

            # حساب الأصول النقدية
            cash_assets = balance_sheet['cash_and_equivalents']
            if 'short_term_investments' in balance_sheet.columns:
                cash_assets += balance_sheet['short_term_investments']

            # حساب نسبة النقدية
            cash_ratio = (cash_assets / balance_sheet['current_liabilities']).round(2)

            # تصنيف النسبة
            classification = self._classify_cash_ratio(cash_ratio)

            # التفسير
            interpretation_ar = self._interpret_cash_ratio_ar(cash_ratio, classification)
            interpretation_en = self._interpret_cash_ratio_en(cash_ratio, classification)

            # التوصيات
            recommendations = self._get_cash_ratio_recommendations(cash_ratio, classification)

            return {
                'analysis_name_ar': 'نسبة النقدية',
                'analysis_name_en': 'Cash Ratio',
                'result': cash_ratio,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة النقدية = (النقد + الاستثمارات قصيرة الأجل) ÷ الخصوم المتداولة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 0.5',
                    'good': '0.3 - 0.5',
                    'acceptable': '0.2 - 0.3',
                    'weak': '0.1 - 0.2',
                    'poor': '< 0.1'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة النقدية: {str(e)}'}

    def absolute_liquidity_ratio(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        4. نسبة السيولة المطلقة
        Absolute Liquidity Ratio

        Formula: Cash / Current Liabilities
        الصيغة: النقد / الخصوم المتداولة
        """
        try:
            required_columns = ['cash_and_equivalents', 'current_liabilities']
            missing_columns = [col for col in required_columns if col not in balance_sheet.columns]

            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # حساب نسبة السيولة المطلقة
            absolute_liquidity = (balance_sheet['cash_and_equivalents'] /
                                balance_sheet['current_liabilities']).round(2)

            # تصنيف النسبة
            classification = self._classify_absolute_liquidity(absolute_liquidity)

            # التفسير
            interpretation_ar = self._interpret_absolute_liquidity_ar(absolute_liquidity, classification)
            interpretation_en = self._interpret_absolute_liquidity_en(absolute_liquidity, classification)

            # التوصيات
            recommendations = self._get_absolute_liquidity_recommendations(absolute_liquidity, classification)

            return {
                'analysis_name_ar': 'نسبة السيولة المطلقة',
                'analysis_name_en': 'Absolute Liquidity Ratio',
                'result': absolute_liquidity,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة السيولة المطلقة = النقد ÷ الخصوم المتداولة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 0.3',
                    'good': '0.2 - 0.3',
                    'acceptable': '0.15 - 0.2',
                    'weak': '0.1 - 0.15',
                    'poor': '< 0.1'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة السيولة المطلقة: {str(e)}'}

    def operating_cash_flow_ratio(self, balance_sheet: pd.DataFrame,
                                 cash_flow_statement: pd.DataFrame) -> Dict:
        """
        5. نسبة التدفق النقدي التشغيلي
        Operating Cash Flow Ratio

        Formula: Operating Cash Flow / Current Liabilities
        الصيغة: التدفق النقدي التشغيلي / الخصوم المتداولة
        """
        try:
            if 'current_liabilities' not in balance_sheet.columns:
                raise ValueError("Missing 'current_liabilities' in balance sheet")
            if 'operating_cash_flow' not in cash_flow_statement.columns:
                raise ValueError("Missing 'operating_cash_flow' in cash flow statement")

            # حساب نسبة التدفق النقدي التشغيلي
            ocf_ratio = (cash_flow_statement['operating_cash_flow'] /
                        balance_sheet['current_liabilities']).round(2)

            # تصنيف النسبة
            classification = self._classify_ocf_ratio(ocf_ratio)

            # التفسير
            interpretation_ar = self._interpret_ocf_ratio_ar(ocf_ratio, classification)
            interpretation_en = self._interpret_ocf_ratio_en(ocf_ratio, classification)

            # التوصيات
            recommendations = self._get_ocf_ratio_recommendations(ocf_ratio, classification)

            return {
                'analysis_name_ar': 'نسبة التدفق النقدي التشغيلي',
                'analysis_name_en': 'Operating Cash Flow Ratio',
                'result': ocf_ratio,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة التدفق النقدي التشغيلي = التدفق النقدي التشغيلي ÷ الخصوم المتداولة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 0.4',
                    'good': '0.25 - 0.4',
                    'acceptable': '0.15 - 0.25',
                    'weak': '0.05 - 0.15',
                    'poor': '< 0.05'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة التدفق النقدي التشغيلي: {str(e)}'}

    def working_capital_ratio(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        6. نسبة رأس المال العامل
        Working Capital Ratio

        Formula: (Current Assets - Current Liabilities) / Total Assets
        الصيغة: (الأصول المتداولة - الخصوم المتداولة) / إجمالي الأصول
        """
        try:
            required_columns = ['current_assets', 'current_liabilities', 'total_assets']
            missing_columns = [col for col in required_columns if col not in balance_sheet.columns]

            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # حساب رأس المال العامل
            working_capital = balance_sheet['current_assets'] - balance_sheet['current_liabilities']

            # حساب نسبة رأس المال العامل
            wc_ratio = (working_capital / balance_sheet['total_assets'] * 100).round(2)

            # تصنيف النسبة
            classification = self._classify_working_capital_ratio(wc_ratio)

            # التفسير
            interpretation_ar = self._interpret_wc_ratio_ar(wc_ratio, working_capital, classification)
            interpretation_en = self._interpret_wc_ratio_en(wc_ratio, working_capital, classification)

            # التوصيات
            recommendations = self._get_wc_ratio_recommendations(wc_ratio, classification)

            return {
                'analysis_name_ar': 'نسبة رأس المال العامل',
                'analysis_name_en': 'Working Capital Ratio',
                'result': wc_ratio,
                'working_capital': working_capital,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة رأس المال العامل = (الأصول المتداولة - الخصوم المتداولة) ÷ إجمالي الأصول × 100',
                'unit': '%',
                'benchmark_ranges': {
                    'excellent': '> 30%',
                    'good': '20% - 30%',
                    'acceptable': '10% - 20%',
                    'weak': '0% - 10%',
                    'poor': '< 0%'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة رأس المال العامل: {str(e)}'}

    def net_working_capital_turnover(self, balance_sheet: pd.DataFrame,
                                   income_statement: pd.DataFrame) -> Dict:
        """
        7. معدل دوران رأس المال العامل الصافي
        Net Working Capital Turnover

        Formula: Sales / Net Working Capital
        الصيغة: المبيعات / رأس المال العامل الصافي
        """
        try:
            required_bs_columns = ['current_assets', 'current_liabilities']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب رأس المال العامل الصافي
            net_working_capital = (balance_sheet['current_assets'] -
                                 balance_sheet['current_liabilities'])

            # تجنب القسمة على صفر
            nwc_turnover = np.where(
                net_working_capital != 0,
                (income_statement['total_revenue'] / net_working_capital).round(2),
                np.inf
            )

            # تصنيف النسبة
            classification = self._classify_nwc_turnover(nwc_turnover)

            # التفسير
            interpretation_ar = self._interpret_nwc_turnover_ar(nwc_turnover, classification)
            interpretation_en = self._interpret_nwc_turnover_en(nwc_turnover, classification)

            # التوصيات
            recommendations = self._get_nwc_turnover_recommendations(nwc_turnover, classification)

            return {
                'analysis_name_ar': 'معدل دوران رأس المال العامل الصافي',
                'analysis_name_en': 'Net Working Capital Turnover',
                'result': nwc_turnover,
                'net_working_capital': net_working_capital,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران رأس المال العامل = المبيعات ÷ رأس المال العامل الصافي',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 6',
                    'good': '4 - 6',
                    'acceptable': '2 - 4',
                    'weak': '1 - 2',
                    'poor': '< 1'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران رأس المال العامل: {str(e)}'}

    def defensive_interval_ratio(self, balance_sheet: pd.DataFrame,
                                income_statement: pd.DataFrame) -> Dict:
        """
        8. نسبة الفترة الدفاعية
        Defensive Interval Ratio

        Formula: (Cash + Short-term Investments + Receivables) / Daily Operating Expenses
        الصيغة: (النقد + الاستثمارات قصيرة الأجل + المدينون) / المصروفات التشغيلية اليومية
        """
        try:
            required_bs_columns = ['cash_and_equivalents', 'accounts_receivable']
            required_is_columns = ['operating_expenses']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب الأصول السائلة
            liquid_assets = (balance_sheet['cash_and_equivalents'] +
                           balance_sheet['accounts_receivable'])

            if 'short_term_investments' in balance_sheet.columns:
                liquid_assets += balance_sheet['short_term_investments']

            # حساب المصروفات التشغيلية اليومية
            daily_operating_expenses = income_statement['operating_expenses'] / 365

            # حساب نسبة الفترة الدفاعية
            defensive_interval = (liquid_assets / daily_operating_expenses).round(0)

            # تصنيف النسبة
            classification = self._classify_defensive_interval(defensive_interval)

            # التفسير
            interpretation_ar = self._interpret_defensive_interval_ar(defensive_interval, classification)
            interpretation_en = self._interpret_defensive_interval_en(defensive_interval, classification)

            # التوصيات
            recommendations = self._get_defensive_interval_recommendations(defensive_interval, classification)

            return {
                'analysis_name_ar': 'نسبة الفترة الدفاعية',
                'analysis_name_en': 'Defensive Interval Ratio',
                'result': defensive_interval,
                'liquid_assets': liquid_assets,
                'daily_operating_expenses': daily_operating_expenses,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'الفترة الدفاعية = الأصول السائلة ÷ المصروفات التشغيلية اليومية',
                'unit': 'يوم / days',
                'benchmark_ranges': {
                    'excellent': '> 100 days',
                    'good': '60 - 100 days',
                    'acceptable': '30 - 60 days',
                    'weak': '15 - 30 days',
                    'poor': '< 15 days'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة الفترة الدفاعية: {str(e)}'}

    def cash_conversion_cycle(self, balance_sheet: pd.DataFrame,
                            income_statement: pd.DataFrame) -> Dict:
        """
        9. دورة تحويل النقد
        Cash Conversion Cycle

        Formula: DIO + DSO - DPO
        الصيغة: فترة دوران المخزون + فترة تحصيل المدينين - فترة سداد الدائنين
        """
        try:
            required_bs_columns = ['inventory', 'accounts_receivable', 'accounts_payable']
            required_is_columns = ['cost_of_goods_sold', 'total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب فترة دوران المخزون (DIO)
            dio = (balance_sheet['inventory'] / income_statement['cost_of_goods_sold'] * 365).round(0)

            # حساب فترة تحصيل المدينين (DSO)
            dso = (balance_sheet['accounts_receivable'] / income_statement['total_revenue'] * 365).round(0)

            # حساب فترة سداد الدائنين (DPO)
            dpo = (balance_sheet['accounts_payable'] / income_statement['cost_of_goods_sold'] * 365).round(0)

            # حساب دورة تحويل النقد
            cash_conversion_cycle = dio + dso - dpo

            # تصنيف الدورة
            classification = self._classify_cash_conversion_cycle(cash_conversion_cycle)

            # التفسير
            interpretation_ar = self._interpret_ccc_ar(cash_conversion_cycle, dio, dso, dpo, classification)
            interpretation_en = self._interpret_ccc_en(cash_conversion_cycle, dio, dso, dpo, classification)

            # التوصيات
            recommendations = self._get_ccc_recommendations(cash_conversion_cycle, dio, dso, dpo, classification)

            return {
                'analysis_name_ar': 'دورة تحويل النقد',
                'analysis_name_en': 'Cash Conversion Cycle',
                'result': cash_conversion_cycle,
                'components': {
                    'days_inventory_outstanding': dio,
                    'days_sales_outstanding': dso,
                    'days_payable_outstanding': dpo
                },
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'دورة تحويل النقد = فترة دوران المخزون + فترة تحصيل المدينين - فترة سداد الدائنين',
                'unit': 'يوم / days',
                'benchmark_ranges': {
                    'excellent': '< 30 days',
                    'good': '30 - 60 days',
                    'acceptable': '60 - 90 days',
                    'weak': '90 - 120 days',
                    'poor': '> 120 days'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب دورة تحويل النقد: {str(e)}'}

    def liquidity_index(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        10. مؤشر السيولة
        Liquidity Index

        Formula: Weighted average of current assets by liquidity
        الصيغة: المتوسط المرجح للأصول المتداولة حسب درجة السيولة
        """
        try:
            required_columns = ['cash_and_equivalents', 'current_assets', 'current_liabilities']
            optional_columns = ['short_term_investments', 'accounts_receivable', 'inventory']

            missing_required = [col for col in required_columns if col not in balance_sheet.columns]
            if missing_required:
                raise ValueError(f"Missing required columns: {missing_required}")

            # تحديد أوزان السيولة (كلما ارتفع الوزن، زادت السيولة)
            weights = {
                'cash_and_equivalents': 1.0,
                'short_term_investments': 0.9,
                'accounts_receivable': 0.8,
                'inventory': 0.6,
                'other_current_assets': 0.4
            }

            # حساب المؤشر
            weighted_sum = 0
            total_assets = 0

            for asset, weight in weights.items():
                if asset in balance_sheet.columns:
                    asset_value = balance_sheet[asset]
                    weighted_sum += asset_value * weight
                    total_assets += asset_value

            # إضافة الأصول الأخرى غير المصنفة
            classified_assets = sum([balance_sheet.get(asset, 0) for asset in weights.keys()
                                   if asset in balance_sheet.columns])
            other_assets = balance_sheet['current_assets'] - classified_assets

            if other_assets.sum() > 0:
                weighted_sum += other_assets * weights['other_current_assets']
                total_assets += other_assets

            # حساب مؤشر السيولة
            liquidity_index = (weighted_sum / balance_sheet['current_liabilities']).round(2)

            # تصنيف المؤشر
            classification = self._classify_liquidity_index(liquidity_index)

            # التفسير
            interpretation_ar = self._interpret_liquidity_index_ar(liquidity_index, classification)
            interpretation_en = self._interpret_liquidity_index_en(liquidity_index, classification)

            # التوصيات
            recommendations = self._get_liquidity_index_recommendations(liquidity_index, classification)

            return {
                'analysis_name_ar': 'مؤشر السيولة',
                'analysis_name_en': 'Liquidity Index',
                'result': liquidity_index,
                'weights_used': weights,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'مؤشر السيولة = مجموع (الأصول المتداولة × أوزان السيولة) ÷ الخصوم المتداولة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 1.8',
                    'good': '1.4 - 1.8',
                    'acceptable': '1.0 - 1.4',
                    'weak': '0.8 - 1.0',
                    'poor': '< 0.8'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب مؤشر السيولة: {str(e)}'}

    # دوال التصنيف والتفسير
    def _classify_current_ratio(self, ratio: pd.Series) -> pd.Series:
        """تصنيف نسبة التداول"""
        return ratio.apply(lambda x:
            'ممتاز' if x >= 2.0 else
            'جيد' if x >= 1.5 else
            'مقبول' if x >= 1.2 else
            'ضعيف' if x >= 1.0 else
            'سيء'
        )

    def _interpret_current_ratio_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        """تفسير نسبة التداول باللغة العربية"""
        avg_ratio = ratio.mean()
        latest_class = classification.iloc[-1]

        interpretation = f"نسبة التداول الحالية {avg_ratio:.2f} مرة، مما يعني أن الشركة تملك "
        interpretation += f"{avg_ratio:.2f} ريال من الأصول المتداولة لكل ريال من الخصوم المتداولة.\n"

        if latest_class == 'ممتاز':
            interpretation += "السيولة ممتازة والشركة قادرة على سداد التزاماتها قصيرة الأجل بسهولة."
        elif latest_class == 'جيد':
            interpretation += "السيولة جيدة والشركة تتمتع بوضع مالي صحي."
        elif latest_class == 'مقبول':
            interpretation += "السيولة مقبولة لكن تحتاج لمراقبة مستمرة."
        elif latest_class == 'ضعيف':
            interpretation += "السيولة ضعيفة وقد تواجه الشركة صعوبة في سداد التزاماتها."
        else:
            interpretation += "السيولة سيئة جداً والشركة معرضة لمخاطر عدم السداد."

        return interpretation

    def _interpret_current_ratio_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        """تفسير نسبة التداول باللغة الإنجليزية"""
        avg_ratio = ratio.mean()
        latest_class = classification.iloc[-1]

        interpretation = f"Current ratio is {avg_ratio:.2f}x, meaning the company has "
        interpretation += f"{avg_ratio:.2f} of current assets for every 1 unit of current liabilities.\n"

        if latest_class == 'ممتاز':
            interpretation += "Excellent liquidity - company can easily meet short-term obligations."
        elif latest_class == 'جيد':
            interpretation += "Good liquidity position with healthy financial standing."
        elif latest_class == 'مقبول':
            interpretation += "Acceptable liquidity but requires continuous monitoring."
        elif latest_class == 'ضعيف':
            interpretation += "Weak liquidity - company may face difficulty meeting obligations."
        else:
            interpretation += "Poor liquidity - company is at risk of default."

        return interpretation

    def _get_current_ratio_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        """توصيات نسبة التداول"""
        recommendations = []
        latest_class = classification.iloc[-1]

        if latest_class in ['ضعيف', 'سيء']:
            recommendations.extend([
                "زيادة الأصول المتداولة من خلال تحسين إدارة المخزون والمدينين",
                "Increase current assets through better inventory and receivables management",
                "إعادة جدولة الديون قصيرة الأجل لتحسين السيولة",
                "Reschedule short-term debts to improve liquidity"
            ])
        elif latest_class == 'مقبول':
            recommendations.extend([
                "مراقبة مستويات السيولة بانتظام",
                "Monitor liquidity levels regularly",
                "تنويع مصادر التمويل قصير الأجل",
                "Diversify short-term financing sources"
            ])

        return recommendations

    def _classify_quick_ratio(self, ratio: pd.Series) -> pd.Series:
        """تصنيف نسبة السيولة السريعة"""
        return ratio.apply(lambda x:
            'ممتاز' if x > 1.5 else
            'جيد' if x >= 1.2 else
            'مقبول' if x >= 1.0 else
            'ضعيف' if x >= 0.8 else
            'سيء'
        )

    def _interpret_quick_ratio_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        """تفسير نسبة السيولة السريعة"""
        avg_ratio = ratio.mean()
        return f"نسبة السيولة السريعة {avg_ratio:.2f} تشير إلى قدرة الشركة على سداد الالتزامات فوراً دون الاعتماد على بيع المخزون."

    def _interpret_quick_ratio_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        """English interpretation of quick ratio"""
        avg_ratio = ratio.mean()
        return f"Quick ratio of {avg_ratio:.2f} indicates company's ability to meet immediate obligations without relying on inventory sales."

    def _get_quick_ratio_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        """توصيات نسبة السيولة السريعة"""
        recommendations = []
        latest_class = classification.iloc[-1]

        if latest_class in ['ضعيف', 'سيء']:
            recommendations.extend([
                "تحسين إدارة المدينين لزيادة التحصيلات",
                "Improve receivables management to increase collections",
                "الاحتفاظ بمستوى مناسب من النقد",
                "Maintain adequate cash levels"
            ])

        return recommendations

    # باقي دوال التصنيف والتفسير للنسب الأخرى (مختصرة لتوفير المساحة)
    def _classify_cash_ratio(self, ratio: pd.Series) -> pd.Series:
        """تصنيف نسبة النقدية"""
        return ratio.apply(lambda x:
            'ممتاز' if x > 0.5 else
            'جيد' if x >= 0.3 else
            'مقبول' if x >= 0.2 else
            'ضعيف' if x >= 0.1 else
            'سيء'
        )

    def _interpret_cash_ratio_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        avg_ratio = ratio.mean()
        return f"نسبة النقدية {avg_ratio:.2f} تدل على قدرة الشركة الفورية على سداد الديون نقداً."

    def _interpret_cash_ratio_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        avg_ratio = ratio.mean()
        return f"Cash ratio of {avg_ratio:.2f} indicates company's immediate cash payment ability."

    def _get_cash_ratio_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة النقد", "Improve cash management"]

    def _classify_absolute_liquidity(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x:
            'ممتاز' if x > 0.3 else
            'جيد' if x >= 0.2 else
            'مقبول' if x >= 0.15 else
            'ضعيف' if x >= 0.1 else
            'سيء'
        )

    def _interpret_absolute_liquidity_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return "تشير إلى قدرة الشركة على السداد الفوري بالنقد المتاح فقط."

    def _interpret_absolute_liquidity_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return "Indicates company's ability for immediate payment with available cash only."

    def _get_absolute_liquidity_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة السيولة", "Improve liquidity management"]

    def _classify_ocf_ratio(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x:
            'ممتاز' if x > 0.4 else
            'جيد' if x >= 0.25 else
            'مقبول' if x >= 0.15 else
            'ضعيف' if x >= 0.05 else
            'سيء'
        )

    def _interpret_ocf_ratio_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return "يقيس قدرة الشركة على توليد نقد من العمليات التشغيلية لسداد الديون."

    def _interpret_ocf_ratio_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return "Measures company's ability to generate operating cash to service debts."

    def _get_ocf_ratio_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين التدفق النقدي التشغيلي", "Improve operating cash flow"]

    def _classify_working_capital_ratio(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x:
            'ممتاز' if x > 30 else
            'جيد' if x >= 20 else
            'مقبول' if x >= 10 else
            'ضعيف' if x >= 0 else
            'سيء'
        )

    def _interpret_wc_ratio_ar(self, ratio: pd.Series, wc: pd.Series, classification: pd.Series) -> str:
        return f"رأس المال العامل يمثل {ratio.mean():.1f}% من إجمالي الأصول."

    def _interpret_wc_ratio_en(self, ratio: pd.Series, wc: pd.Series, classification: pd.Series) -> str:
        return f"Working capital represents {ratio.mean():.1f}% of total assets."

    def _get_wc_ratio_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة رأس المال العامل", "Improve working capital management"]

    def _classify_nwc_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x:
            'ممتاز' if x > 6 else
            'جيد' if x >= 4 else
            'مقبول' if x >= 2 else
            'ضعيف' if x >= 1 else
            'سيء'
        )

    def _interpret_nwc_turnover_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return "يقيس كفاءة استخدام رأس المال العامل في توليد المبيعات."

    def _interpret_nwc_turnover_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return "Measures efficiency of working capital utilization in generating sales."

    def _get_nwc_turnover_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين كفاءة استخدام رأس المال العامل", "Improve working capital efficiency"]

    def _classify_defensive_interval(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x:
            'ممتاز' if x > 100 else
            'جيد' if x >= 60 else
            'مقبول' if x >= 30 else
            'ضعيف' if x >= 15 else
            'سيء'
        )

    def _interpret_defensive_interval_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        avg_days = ratio.mean()
        return f"الشركة قادرة على تغطية مصروفاتها التشغيلية لمدة {avg_days:.0f} يوم بالأصول السائلة."

    def _interpret_defensive_interval_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        avg_days = ratio.mean()
        return f"Company can cover operating expenses for {avg_days:.0f} days with liquid assets."

    def _get_defensive_interval_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["زيادة الأصول السائلة", "Increase liquid assets"]

    def _classify_cash_conversion_cycle(self, cycle: pd.Series) -> pd.Series:
        return cycle.apply(lambda x:
            'ممتاز' if x < 30 else
            'جيد' if x <= 60 else
            'مقبول' if x <= 90 else
            'ضعيف' if x <= 120 else
            'سيء'
        )

    def _interpret_ccc_ar(self, ccc: pd.Series, dio: pd.Series, dso: pd.Series,
                         dpo: pd.Series, classification: pd.Series) -> str:
        avg_ccc = ccc.mean()
        return f"دورة تحويل النقد {avg_ccc:.0f} يوم، تتكون من {dio.mean():.0f} يوم مخزون، {dso.mean():.0f} يوم مدينين، و{dpo.mean():.0f} يوم دائنين."

    def _interpret_ccc_en(self, ccc: pd.Series, dio: pd.Series, dso: pd.Series,
                         dpo: pd.Series, classification: pd.Series) -> str:
        avg_ccc = ccc.mean()
        return f"Cash conversion cycle is {avg_ccc:.0f} days, consisting of {dio.mean():.0f} days inventory, {dso.mean():.0f} days receivables, and {dpo.mean():.0f} days payables."

    def _get_ccc_recommendations(self, ccc: pd.Series, dio: pd.Series, dso: pd.Series,
                               dpo: pd.Series, classification: pd.Series) -> List[str]:
        recommendations = []
        if dio.mean() > 60:
            recommendations.extend(["تحسين إدارة المخزون", "Improve inventory management"])
        if dso.mean() > 45:
            recommendations.extend(["تحسين تحصيل المدينين", "Improve receivables collection"])
        if dpo.mean() < 30:
            recommendations.extend(["تحسين إدارة الدائنين", "Improve payables management"])
        return recommendations

    def _classify_liquidity_index(self, index: pd.Series) -> pd.Series:
        return index.apply(lambda x:
            'ممتاز' if x > 1.8 else
            'جيد' if x >= 1.4 else
            'مقبول' if x >= 1.0 else
            'ضعيف' if x >= 0.8 else
            'سيء'
        )

    def _interpret_liquidity_index_ar(self, index: pd.Series, classification: pd.Series) -> str:
        avg_index = index.mean()
        return f"مؤشر السيولة {avg_index:.2f} يعكس جودة الأصول المتداولة من ناحية السيولة."

    def _interpret_liquidity_index_en(self, index: pd.Series, classification: pd.Series) -> str:
        avg_index = index.mean()
        return f"Liquidity index of {avg_index:.2f} reflects quality of current assets in terms of liquidity."

    def _get_liquidity_index_recommendations(self, index: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين تركيبة الأصول المتداولة", "Improve current assets composition"]

    def generate_liquidity_dashboard(self, balance_sheet: pd.DataFrame,
                                   income_statement: pd.DataFrame,
                                   cash_flow_statement: pd.DataFrame) -> Dict:
        """
        إنشاء لوحة تحكم شاملة لنسب السيولة
        Generate comprehensive liquidity ratios dashboard
        """
        try:
            dashboard_results = {}

            # حساب جميع نسب السيولة
            dashboard_results['current_ratio'] = self.current_ratio(balance_sheet)
            dashboard_results['quick_ratio'] = self.quick_ratio(balance_sheet)
            dashboard_results['cash_ratio'] = self.cash_ratio(balance_sheet)
            dashboard_results['absolute_liquidity'] = self.absolute_liquidity_ratio(balance_sheet)
            dashboard_results['ocf_ratio'] = self.operating_cash_flow_ratio(balance_sheet, cash_flow_statement)
            dashboard_results['working_capital_ratio'] = self.working_capital_ratio(balance_sheet)
            dashboard_results['nwc_turnover'] = self.net_working_capital_turnover(balance_sheet, income_statement)
            dashboard_results['defensive_interval'] = self.defensive_interval_ratio(balance_sheet, income_statement)
            dashboard_results['cash_conversion_cycle'] = self.cash_conversion_cycle(balance_sheet, income_statement)
            dashboard_results['liquidity_index'] = self.liquidity_index(balance_sheet)

            # إنشاء ملخص شامل
            summary = self._create_liquidity_summary(dashboard_results)

            return {
                'analysis_name_ar': 'لوحة تحكم نسب السيولة الشاملة',
                'analysis_name_en': 'Comprehensive Liquidity Ratios Dashboard',
                'total_ratios': 10,
                'results': dashboard_results,
                'summary': summary,
                'overall_liquidity_score': self._calculate_overall_liquidity_score(dashboard_results)
            }

        except Exception as e:
            return {'error': f'خطأ في إنشاء لوحة تحكم السيولة: {str(e)}'}

    def _create_liquidity_summary(self, results: Dict) -> Dict:
        """إنشاء ملخص نسب السيولة"""
        successful_analyses = [k for k, v in results.items() if 'error' not in v]
        failed_analyses = [k for k, v in results.items() if 'error' in v]

        summary = {
            'successful_ratios': len(successful_analyses),
            'failed_ratios': len(failed_analyses),
            'liquidity_status': 'جيد',  # سيتم تحديده بناءً على النتائج
            'key_strengths': [],
            'key_weaknesses': [],
            'priority_recommendations': []
        }

        # تحليل نقاط القوة والضعف
        for ratio_name, ratio_data in results.items():
            if 'error' not in ratio_data and 'classification' in ratio_data:
                latest_class = ratio_data['classification'].iloc[-1] if hasattr(ratio_data['classification'], 'iloc') else ratio_data['classification']

                if latest_class in ['ممتاز', 'جيد']:
                    summary['key_strengths'].append(ratio_data['analysis_name_ar'])
                elif latest_class in ['ضعيف', 'سيء']:
                    summary['key_weaknesses'].append(ratio_data['analysis_name_ar'])

        return summary

    def _calculate_overall_liquidity_score(self, results: Dict) -> float:
        """حساب النقاط الإجمالية للسيولة"""
        total_score = 0
        count = 0

        score_mapping = {'ممتاز': 5, 'جيد': 4, 'مقبول': 3, 'ضعيف': 2, 'سيء': 1}

        for ratio_data in results.values():
            if 'error' not in ratio_data and 'classification' in ratio_data:
                latest_class = ratio_data['classification'].iloc[-1] if hasattr(ratio_data['classification'], 'iloc') else ratio_data['classification']
                total_score += score_mapping.get(latest_class, 0)
                count += 1

        return round(total_score / count if count > 0 else 0, 2)

    def generate_visualization(self, results: Dict, chart_type: str = 'dashboard') -> None:
        """
        إنشاء الرسوم البيانية لنسب السيولة
        Generate visualizations for liquidity ratios
        """
        try:
            if chart_type == 'dashboard':
                fig, axes = plt.subplots(2, 3, figsize=(18, 12))
                fig.suptitle('لوحة تحكم نسب السيولة / Liquidity Ratios Dashboard', fontsize=16)

                # استخراج النتائج للرسم
                ratio_names = []
                ratio_values = []

                for ratio_name, ratio_data in results['results'].items():
                    if 'error' not in ratio_data and 'result' in ratio_data:
                        ratio_names.append(ratio_data['analysis_name_ar'])
                        if hasattr(ratio_data['result'], 'iloc'):
                            ratio_values.append(ratio_data['result'].iloc[-1])
                        else:
                            ratio_values.append(ratio_data['result'])

                # رسم المخططات المختلفة
                axes[0, 0].bar(ratio_names[:3], ratio_values[:3])
                axes[0, 0].set_title('النسب الأساسية')
                axes[0, 0].tick_params(axis='x', rotation=45)

                axes[0, 1].plot(ratio_values[:5])
                axes[0, 1].set_title('اتجاه النسب')

                # المزيد من المخططات...
                plt.tight_layout()
                plt.show()

        except Exception as e:
            print(f"خطأ في إنشاء الرسم البياني: {str(e)}")

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء بيانات تجريبية
    sample_balance_sheet = pd.DataFrame({
        'current_assets': [45000, 50000, 55000],
        'cash_and_equivalents': [15000, 18000, 20000],
        'short_term_investments': [5000, 6000, 7000],
        'accounts_receivable': [12000, 14000, 15000],
        'inventory': [13000, 12000, 13000],
        'current_liabilities': [25000, 28000, 30000],
        'accounts_payable': [15000, 16000, 17000],
        'total_assets': [100000, 110000, 125000]
    }, index=['2021', '2022', '2023'])

    sample_income_statement = pd.DataFrame({
        'total_revenue': [80000, 88000, 96000],
        'cost_of_goods_sold': [48000, 52000, 57000],
        'operating_expenses': [20000, 22000, 24000]
    }, index=['2021', '2022', '2023'])

    sample_cash_flow = pd.DataFrame({
        'operating_cash_flow': [12000, 15000, 18000]
    }, index=['2021', '2022', '2023'])

    # تشغيل التحليل
    analyzer = LiquidityRatios(sample_balance_sheet)
    dashboard = analyzer.generate_liquidity_dashboard(
        sample_balance_sheet,
        sample_income_statement,
        sample_cash_flow
    )

    print("نتائج تحليل نسب السيولة:")
    print(f"عدد النسب المحسوبة: {dashboard['summary']['successful_ratios']}")
    print(f"النقاط الإجمالية للسيولة: {dashboard['overall_liquidity_score']}")