"""
نسب النشاط/الكفاءة - Activity/Efficiency Ratios
يحتوي على 15 نسبة لقياس كفاءة الشركة في استخدام أصولها وإدارة عملياتها
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

class ActivityEfficiencyRatios:
    """
    فئة نسب النشاط والكفاءة
    Activity and Efficiency Ratios Class
    """

    def __init__(self, data: pd.DataFrame):
        """
        تهيئة فئة نسب النشاط والكفاءة
        Initialize Activity and Efficiency Ratios Class

        Args:
            data: بيانات القوائم المالية / Financial statements data
        """
        self.data = data.copy()
        self.results = {}

    def total_asset_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        1. معدل دوران إجمالي الأصول
        Total Asset Turnover Ratio

        Formula: Net Sales / Average Total Assets
        الصيغة: صافي المبيعات / متوسط إجمالي الأصول
        """
        try:
            required_bs_columns = ['total_assets']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط إجمالي الأصول
            if len(balance_sheet) > 1:
                avg_total_assets = (balance_sheet['total_assets'] + balance_sheet['total_assets'].shift(1)) / 2
                avg_total_assets = avg_total_assets.dropna()
            else:
                avg_total_assets = balance_sheet['total_assets']

            # محاذاة المؤشرات
            common_index = avg_total_assets.index.intersection(income_statement.index)
            avg_total_assets = avg_total_assets.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # حساب معدل الدوران
            total_asset_turnover = (revenue / avg_total_assets).round(2)

            # تصنيف النسبة
            classification = self._classify_total_asset_turnover(total_asset_turnover)

            # التفسير
            interpretation_ar = self._interpret_total_asset_turnover_ar(total_asset_turnover, classification)
            interpretation_en = self._interpret_total_asset_turnover_en(total_asset_turnover, classification)

            # التوصيات
            recommendations = self._get_total_asset_turnover_recommendations(total_asset_turnover, classification)

            return {
                'analysis_name_ar': 'معدل دوران إجمالي الأصول',
                'analysis_name_en': 'Total Asset Turnover Ratio',
                'result': total_asset_turnover,
                'average_total_assets': avg_total_assets,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران إجمالي الأصول = صافي المبيعات ÷ متوسط إجمالي الأصول',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 2.0',
                    'good': '1.5 - 2.0',
                    'average': '1.0 - 1.5',
                    'weak': '0.5 - 1.0',
                    'poor': '< 0.5'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران إجمالي الأصول: {str(e)}'}

    def fixed_asset_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        2. معدل دوران الأصول الثابتة
        Fixed Asset Turnover Ratio

        Formula: Net Sales / Average Fixed Assets
        الصيغة: صافي المبيعات / متوسط الأصول الثابتة
        """
        try:
            required_bs_columns = ['property_plant_equipment']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط الأصول الثابتة
            if len(balance_sheet) > 1:
                avg_fixed_assets = (balance_sheet['property_plant_equipment'] +
                                  balance_sheet['property_plant_equipment'].shift(1)) / 2
                avg_fixed_assets = avg_fixed_assets.dropna()
            else:
                avg_fixed_assets = balance_sheet['property_plant_equipment']

            # محاذاة المؤشرات
            common_index = avg_fixed_assets.index.intersection(income_statement.index)
            avg_fixed_assets = avg_fixed_assets.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # تجنب القسمة على صفر
            fixed_asset_turnover = np.where(
                avg_fixed_assets != 0,
                (revenue / avg_fixed_assets).round(2),
                np.inf
            )

            # تصنيف النسبة
            classification = self._classify_fixed_asset_turnover(fixed_asset_turnover)

            # التفسير
            interpretation_ar = self._interpret_fixed_asset_turnover_ar(fixed_asset_turnover, classification)
            interpretation_en = self._interpret_fixed_asset_turnover_en(fixed_asset_turnover, classification)

            # التوصيات
            recommendations = self._get_fixed_asset_turnover_recommendations(fixed_asset_turnover, classification)

            return {
                'analysis_name_ar': 'معدل دوران الأصول الثابتة',
                'analysis_name_en': 'Fixed Asset Turnover Ratio',
                'result': fixed_asset_turnover,
                'average_fixed_assets': avg_fixed_assets,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران الأصول الثابتة = صافي المبيعات ÷ متوسط الأصول الثابتة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 4.0',
                    'good': '3.0 - 4.0',
                    'average': '2.0 - 3.0',
                    'weak': '1.0 - 2.0',
                    'poor': '< 1.0'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران الأصول الثابتة: {str(e)}'}

    def inventory_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        3. معدل دوران المخزون
        Inventory Turnover Ratio

        Formula: Cost of Goods Sold / Average Inventory
        الصيغة: تكلفة البضاعة المباعة / متوسط المخزون
        """
        try:
            required_bs_columns = ['inventory']
            required_is_columns = ['cost_of_goods_sold']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط المخزون
            if len(balance_sheet) > 1:
                avg_inventory = (balance_sheet['inventory'] + balance_sheet['inventory'].shift(1)) / 2
                avg_inventory = avg_inventory.dropna()
            else:
                avg_inventory = balance_sheet['inventory']

            # محاذاة المؤشرات
            common_index = avg_inventory.index.intersection(income_statement.index)
            avg_inventory = avg_inventory.loc[common_index]
            cogs = income_statement.loc[common_index, 'cost_of_goods_sold']

            # تجنب القسمة على صفر
            inventory_turnover = np.where(
                avg_inventory != 0,
                (cogs / avg_inventory).round(2),
                np.inf
            )

            # حساب أيام المخزون
            days_inventory_outstanding = np.where(
                inventory_turnover != 0,
                (365 / inventory_turnover).round(0),
                np.inf
            )

            # تصنيف النسبة
            classification = self._classify_inventory_turnover(inventory_turnover)

            # التفسير
            interpretation_ar = self._interpret_inventory_turnover_ar(
                inventory_turnover, days_inventory_outstanding, classification)
            interpretation_en = self._interpret_inventory_turnover_en(
                inventory_turnover, days_inventory_outstanding, classification)

            # التوصيات
            recommendations = self._get_inventory_turnover_recommendations(
                inventory_turnover, days_inventory_outstanding, classification)

            return {
                'analysis_name_ar': 'معدل دوران المخزون',
                'analysis_name_en': 'Inventory Turnover Ratio',
                'result': inventory_turnover,
                'days_inventory_outstanding': days_inventory_outstanding,
                'average_inventory': avg_inventory,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران المخزون = تكلفة البضاعة المباعة ÷ متوسط المخزون',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 12',
                    'good': '8 - 12',
                    'average': '6 - 8',
                    'weak': '4 - 6',
                    'poor': '< 4'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران المخزون: {str(e)}'}

    def accounts_receivable_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        4. معدل دوران المدينين
        Accounts Receivable Turnover Ratio

        Formula: Net Credit Sales / Average Accounts Receivable
        الصيغة: صافي المبيعات الآجلة / متوسط المدينين
        """
        try:
            required_bs_columns = ['accounts_receivable']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط المدينين
            if len(balance_sheet) > 1:
                avg_receivables = (balance_sheet['accounts_receivable'] +
                                 balance_sheet['accounts_receivable'].shift(1)) / 2
                avg_receivables = avg_receivables.dropna()
            else:
                avg_receivables = balance_sheet['accounts_receivable']

            # محاذاة المؤشرات
            common_index = avg_receivables.index.intersection(income_statement.index)
            avg_receivables = avg_receivables.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # تجنب القسمة على صفر
            receivables_turnover = np.where(
                avg_receivables != 0,
                (revenue / avg_receivables).round(2),
                np.inf
            )

            # حساب أيام التحصيل
            days_sales_outstanding = np.where(
                receivables_turnover != 0,
                (365 / receivables_turnover).round(0),
                np.inf
            )

            # تصنيف النسبة
            classification = self._classify_receivables_turnover(receivables_turnover)

            # التفسير
            interpretation_ar = self._interpret_receivables_turnover_ar(
                receivables_turnover, days_sales_outstanding, classification)
            interpretation_en = self._interpret_receivables_turnover_en(
                receivables_turnover, days_sales_outstanding, classification)

            # التوصيات
            recommendations = self._get_receivables_turnover_recommendations(
                receivables_turnover, days_sales_outstanding, classification)

            return {
                'analysis_name_ar': 'معدل دوران المدينين',
                'analysis_name_en': 'Accounts Receivable Turnover Ratio',
                'result': receivables_turnover,
                'days_sales_outstanding': days_sales_outstanding,
                'average_receivables': avg_receivables,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران المدينين = صافي المبيعات ÷ متوسط المدينين',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 12',
                    'good': '8 - 12',
                    'average': '6 - 8',
                    'weak': '4 - 6',
                    'poor': '< 4'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران المدينين: {str(e)}'}

    def accounts_payable_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        5. معدل دوران الدائنين
        Accounts Payable Turnover Ratio

        Formula: Cost of Goods Sold / Average Accounts Payable
        الصيغة: تكلفة البضاعة المباعة / متوسط الدائنين
        """
        try:
            required_bs_columns = ['accounts_payable']
            required_is_columns = ['cost_of_goods_sold']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط الدائنين
            if len(balance_sheet) > 1:
                avg_payables = (balance_sheet['accounts_payable'] +
                              balance_sheet['accounts_payable'].shift(1)) / 2
                avg_payables = avg_payables.dropna()
            else:
                avg_payables = balance_sheet['accounts_payable']

            # محاذاة المؤشرات
            common_index = avg_payables.index.intersection(income_statement.index)
            avg_payables = avg_payables.loc[common_index]
            cogs = income_statement.loc[common_index, 'cost_of_goods_sold']

            # تجنب القسمة على صفر
            payables_turnover = np.where(
                avg_payables != 0,
                (cogs / avg_payables).round(2),
                np.inf
            )

            # حساب أيام السداد
            days_payable_outstanding = np.where(
                payables_turnover != 0,
                (365 / payables_turnover).round(0),
                np.inf
            )

            # تصنيف النسبة
            classification = self._classify_payables_turnover(payables_turnover)

            # التفسير
            interpretation_ar = self._interpret_payables_turnover_ar(
                payables_turnover, days_payable_outstanding, classification)
            interpretation_en = self._interpret_payables_turnover_en(
                payables_turnover, days_payable_outstanding, classification)

            # التوصيات
            recommendations = self._get_payables_turnover_recommendations(
                payables_turnover, days_payable_outstanding, classification)

            return {
                'analysis_name_ar': 'معدل دوران الدائنين',
                'analysis_name_en': 'Accounts Payable Turnover Ratio',
                'result': payables_turnover,
                'days_payable_outstanding': days_payable_outstanding,
                'average_payables': avg_payables,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران الدائنين = تكلفة البضاعة المباعة ÷ متوسط الدائنين',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'conservative': '< 6',
                    'balanced': '6 - 10',
                    'aggressive': '> 10'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران الدائنين: {str(e)}'}

    def working_capital_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        6. معدل دوران رأس المال العامل
        Working Capital Turnover Ratio

        Formula: Net Sales / Average Working Capital
        الصيغة: صافي المبيعات / متوسط رأس المال العامل
        """
        try:
            required_bs_columns = ['current_assets', 'current_liabilities']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب رأس المال العامل
            working_capital = balance_sheet['current_assets'] - balance_sheet['current_liabilities']

            # حساب متوسط رأس المال العامل
            if len(balance_sheet) > 1:
                avg_working_capital = (working_capital + working_capital.shift(1)) / 2
                avg_working_capital = avg_working_capital.dropna()
            else:
                avg_working_capital = working_capital

            # محاذاة المؤشرات
            common_index = avg_working_capital.index.intersection(income_statement.index)
            avg_working_capital = avg_working_capital.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # تجنب القسمة على صفر أو رأس المال العامل السالب
            wc_turnover = np.where(
                avg_working_capital > 0,
                (revenue / avg_working_capital).round(2),
                np.where(avg_working_capital < 0, -np.inf, np.inf)
            )

            # تصنيف النسبة
            classification = self._classify_wc_turnover(wc_turnover, avg_working_capital)

            # التفسير
            interpretation_ar = self._interpret_wc_turnover_ar(wc_turnover, avg_working_capital, classification)
            interpretation_en = self._interpret_wc_turnover_en(wc_turnover, avg_working_capital, classification)

            # التوصيات
            recommendations = self._get_wc_turnover_recommendations(wc_turnover, avg_working_capital, classification)

            return {
                'analysis_name_ar': 'معدل دوران رأس المال العامل',
                'analysis_name_en': 'Working Capital Turnover Ratio',
                'result': wc_turnover,
                'average_working_capital': avg_working_capital,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران رأس المال العامل = صافي المبيعات ÷ متوسط رأس المال العامل',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 6',
                    'good': '4 - 6',
                    'average': '2 - 4',
                    'weak': '1 - 2',
                    'poor': '< 1'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران رأس المال العامل: {str(e)}'}

    def cash_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        7. معدل دوران النقد
        Cash Turnover Ratio

        Formula: Net Sales / Average Cash and Cash Equivalents
        الصيغة: صافي المبيعات / متوسط النقد ومعادلاته
        """
        try:
            required_bs_columns = ['cash_and_equivalents']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط النقد
            if len(balance_sheet) > 1:
                avg_cash = (balance_sheet['cash_and_equivalents'] +
                           balance_sheet['cash_and_equivalents'].shift(1)) / 2
                avg_cash = avg_cash.dropna()
            else:
                avg_cash = balance_sheet['cash_and_equivalents']

            # محاذاة المؤشرات
            common_index = avg_cash.index.intersection(income_statement.index)
            avg_cash = avg_cash.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # تجنب القسمة على صفر
            cash_turnover = np.where(
                avg_cash != 0,
                (revenue / avg_cash).round(2),
                np.inf
            )

            # تصنيف النسبة
            classification = self._classify_cash_turnover(cash_turnover)

            # التفسير
            interpretation_ar = self._interpret_cash_turnover_ar(cash_turnover, classification)
            interpretation_en = self._interpret_cash_turnover_en(cash_turnover, classification)

            # التوصيات
            recommendations = self._get_cash_turnover_recommendations(cash_turnover, classification)

            return {
                'analysis_name_ar': 'معدل دوران النقد',
                'analysis_name_en': 'Cash Turnover Ratio',
                'result': cash_turnover,
                'average_cash': avg_cash,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران النقد = صافي المبيعات ÷ متوسط النقد ومعادلاته',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 20',
                    'good': '15 - 20',
                    'average': '10 - 15',
                    'weak': '5 - 10',
                    'poor': '< 5'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران النقد: {str(e)}'}

    def equity_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        8. معدل دوران حقوق الملكية
        Equity Turnover Ratio

        Formula: Net Sales / Average Shareholders' Equity
        الصيغة: صافي المبيعات / متوسط حقوق الملكية
        """
        try:
            required_bs_columns = ['total_equity']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط حقوق الملكية
            if len(balance_sheet) > 1:
                avg_equity = (balance_sheet['total_equity'] + balance_sheet['total_equity'].shift(1)) / 2
                avg_equity = avg_equity.dropna()
            else:
                avg_equity = balance_sheet['total_equity']

            # محاذاة المؤشرات
            common_index = avg_equity.index.intersection(income_statement.index)
            avg_equity = avg_equity.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # تجنب القسمة على صفر
            equity_turnover = np.where(
                avg_equity != 0,
                (revenue / avg_equity).round(2),
                np.inf
            )

            # تصنيف النسبة
            classification = self._classify_equity_turnover(equity_turnover)

            # التفسير
            interpretation_ar = self._interpret_equity_turnover_ar(equity_turnover, classification)
            interpretation_en = self._interpret_equity_turnover_en(equity_turnover, classification)

            # التوصيات
            recommendations = self._get_equity_turnover_recommendations(equity_turnover, classification)

            return {
                'analysis_name_ar': 'معدل دوران حقوق الملكية',
                'analysis_name_en': 'Equity Turnover Ratio',
                'result': equity_turnover,
                'average_equity': avg_equity,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران حقوق الملكية = صافي المبيعات ÷ متوسط حقوق الملكية',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 3.0',
                    'good': '2.0 - 3.0',
                    'average': '1.5 - 2.0',
                    'weak': '1.0 - 1.5',
                    'poor': '< 1.0'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران حقوق الملكية: {str(e)}'}

    def capital_intensity_ratio(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        9. نسبة كثافة رأس المال
        Capital Intensity Ratio

        Formula: Total Assets / Net Sales
        الصيغة: إجمالي الأصول / صافي المبيعات
        """
        try:
            required_bs_columns = ['total_assets']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # محاذاة المؤشرات
            common_index = balance_sheet.index.intersection(income_statement.index)
            total_assets = balance_sheet.loc[common_index, 'total_assets']
            revenue = income_statement.loc[common_index, 'total_revenue']

            # حساب نسبة كثافة رأس المال
            capital_intensity = (total_assets / revenue).round(2)

            # تصنيف النسبة
            classification = self._classify_capital_intensity(capital_intensity)

            # التفسير
            interpretation_ar = self._interpret_capital_intensity_ar(capital_intensity, classification)
            interpretation_en = self._interpret_capital_intensity_en(capital_intensity, classification)

            # التوصيات
            recommendations = self._get_capital_intensity_recommendations(capital_intensity, classification)

            return {
                'analysis_name_ar': 'نسبة كثافة رأس المال',
                'analysis_name_en': 'Capital Intensity Ratio',
                'result': capital_intensity,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة كثافة رأس المال = إجمالي الأصول ÷ صافي المبيعات',
                'unit': 'نسبة / ratio',
                'benchmark_ranges': {
                    'low_intensity': '< 0.5',
                    'moderate_intensity': '0.5 - 1.0',
                    'high_intensity': '1.0 - 2.0',
                    'very_high_intensity': '> 2.0'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة كثافة رأس المال: {str(e)}'}

    def asset_utilization_ratio(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        10. نسبة استغلال الأصول
        Asset Utilization Ratio

        Formula: Operating Income / Average Total Assets
        الصيغة: الدخل التشغيلي / متوسط إجمالي الأصول
        """
        try:
            required_bs_columns = ['total_assets']
            required_is_columns = ['operating_income']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط إجمالي الأصول
            if len(balance_sheet) > 1:
                avg_total_assets = (balance_sheet['total_assets'] + balance_sheet['total_assets'].shift(1)) / 2
                avg_total_assets = avg_total_assets.dropna()
            else:
                avg_total_assets = balance_sheet['total_assets']

            # محاذاة المؤشرات
            common_index = avg_total_assets.index.intersection(income_statement.index)
            avg_total_assets = avg_total_assets.loc[common_index]
            operating_income = income_statement.loc[common_index, 'operating_income']

            # حساب نسبة استغلال الأصول
            asset_utilization = (operating_income / avg_total_assets * 100).round(2)

            # تصنيف النسبة
            classification = self._classify_asset_utilization(asset_utilization)

            # التفسير
            interpretation_ar = self._interpret_asset_utilization_ar(asset_utilization, classification)
            interpretation_en = self._interpret_asset_utilization_en(asset_utilization, classification)

            # التوصيات
            recommendations = self._get_asset_utilization_recommendations(asset_utilization, classification)

            return {
                'analysis_name_ar': 'نسبة استغلال الأصول',
                'analysis_name_en': 'Asset Utilization Ratio',
                'result': asset_utilization,
                'average_total_assets': avg_total_assets,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة استغلال الأصول = الدخل التشغيلي ÷ متوسط إجمالي الأصول × 100',
                'unit': '%',
                'benchmark_ranges': {
                    'excellent': '> 15%',
                    'good': '10% - 15%',
                    'average': '5% - 10%',
                    'weak': '2% - 5%',
                    'poor': '< 2%'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نسبة استغلال الأصول: {str(e)}'}

    def current_asset_turnover(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        11. معدل دوران الأصول المتداولة
        Current Asset Turnover Ratio

        Formula: Net Sales / Average Current Assets
        الصيغة: صافي المبيعات / متوسط الأصول المتداولة
        """
        try:
            required_bs_columns = ['current_assets']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب متوسط الأصول المتداولة
            if len(balance_sheet) > 1:
                avg_current_assets = (balance_sheet['current_assets'] +
                                    balance_sheet['current_assets'].shift(1)) / 2
                avg_current_assets = avg_current_assets.dropna()
            else:
                avg_current_assets = balance_sheet['current_assets']

            # محاذاة المؤشرات
            common_index = avg_current_assets.index.intersection(income_statement.index)
            avg_current_assets = avg_current_assets.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # حساب معدل دوران الأصول المتداولة
            current_asset_turnover = (revenue / avg_current_assets).round(2)

            # تصنيف النسبة
            classification = self._classify_current_asset_turnover(current_asset_turnover)

            # التفسير
            interpretation_ar = self._interpret_current_asset_turnover_ar(current_asset_turnover, classification)
            interpretation_en = self._interpret_current_asset_turnover_en(current_asset_turnover, classification)

            # التوصيات
            recommendations = self._get_current_asset_turnover_recommendations(current_asset_turnover, classification)

            return {
                'analysis_name_ar': 'معدل دوران الأصول المتداولة',
                'analysis_name_en': 'Current Asset Turnover Ratio',
                'result': current_asset_turnover,
                'average_current_assets': avg_current_assets,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل دوران الأصول المتداولة = صافي المبيعات ÷ متوسط الأصول المتداولة',
                'unit': 'مرة / times',
                'benchmark_ranges': {
                    'excellent': '> 4.0',
                    'good': '3.0 - 4.0',
                    'average': '2.0 - 3.0',
                    'weak': '1.0 - 2.0',
                    'poor': '< 1.0'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب معدل دوران الأصول المتداولة: {str(e)}'}

    def revenue_per_employee(self, income_statement: pd.DataFrame, employee_data: pd.DataFrame = None) -> Dict:
        """
        12. الإيرادات لكل موظف
        Revenue per Employee

        Formula: Total Revenue / Number of Employees
        الصيغة: إجمالي الإيرادات / عدد الموظفين
        """
        try:
            required_is_columns = ['total_revenue']
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_is:
                raise ValueError(f"Missing columns in income statement: {missing_is}")

            # التحقق من بيانات الموظفين
            if employee_data is None or 'number_of_employees' not in employee_data.columns:
                # استخدام قيم افتراضية أو تقديرية
                avg_employees = pd.Series([100, 110, 120], index=income_statement.index)
                estimated_data = True
            else:
                avg_employees = employee_data['number_of_employees']
                estimated_data = False

            # محاذاة المؤشرات
            common_index = avg_employees.index.intersection(income_statement.index)
            avg_employees = avg_employees.loc[common_index]
            revenue = income_statement.loc[common_index, 'total_revenue']

            # حساب الإيرادات لكل موظف
            revenue_per_employee = (revenue / avg_employees).round(0)

            # تصنيف النسبة
            classification = self._classify_revenue_per_employee(revenue_per_employee)

            # التفسير
            interpretation_ar = self._interpret_revenue_per_employee_ar(
                revenue_per_employee, classification, estimated_data)
            interpretation_en = self._interpret_revenue_per_employee_en(
                revenue_per_employee, classification, estimated_data)

            # التوصيات
            recommendations = self._get_revenue_per_employee_recommendations(
                revenue_per_employee, classification)

            return {
                'analysis_name_ar': 'الإيرادات لكل موظف',
                'analysis_name_en': 'Revenue per Employee',
                'result': revenue_per_employee,
                'number_of_employees': avg_employees,
                'estimated_data': estimated_data,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'الإيرادات لكل موظف = إجمالي الإيرادات ÷ عدد الموظفين',
                'unit': 'ريال/موظف / SAR per employee',
                'benchmark_ranges': {
                    'excellent': '> 1,000,000',
                    'good': '500,000 - 1,000,000',
                    'average': '250,000 - 500,000',
                    'weak': '100,000 - 250,000',
                    'poor': '< 100,000'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب الإيرادات لكل موظف: {str(e)}'}

    def asset_efficiency_score(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        13. نقاط كفاءة الأصول
        Asset Efficiency Score

        Formula: Composite score based on multiple turnover ratios
        الصيغة: نقاط مركبة بناءً على نسب الدوران المتعددة
        """
        try:
            # حساب النسب الأساسية
            total_asset_turnover_result = self.total_asset_turnover(balance_sheet, income_statement)
            inventory_turnover_result = self.inventory_turnover(balance_sheet, income_statement)
            receivables_turnover_result = self.accounts_receivable_turnover(balance_sheet, income_statement)

            # استخراج القيم
            scores = {}
            weights = {'total_asset_turnover': 0.4, 'inventory_turnover': 0.3, 'receivables_turnover': 0.3}

            if 'error' not in total_asset_turnover_result:
                scores['total_asset_turnover'] = self._normalize_turnover_score(
                    total_asset_turnover_result['result'], 'total_asset')

            if 'error' not in inventory_turnover_result:
                scores['inventory_turnover'] = self._normalize_turnover_score(
                    inventory_turnover_result['result'], 'inventory')

            if 'error' not in receivables_turnover_result:
                scores['receivables_turnover'] = self._normalize_turnover_score(
                    receivables_turnover_result['result'], 'receivables')

            # حساب النقاط المركبة
            weighted_scores = []
            for ratio, score in scores.items():
                if ratio in weights:
                    weighted_scores.append(score * weights[ratio])

            if weighted_scores:
                composite_score = pd.Series(weighted_scores).sum() if len(weighted_scores) > 1 else weighted_scores[0]
                composite_score = composite_score.round(1)
            else:
                composite_score = pd.Series([0] * len(balance_sheet.index), index=balance_sheet.index)

            # تصنيف النقاط
            classification = self._classify_efficiency_score(composite_score)

            # التفسير
            interpretation_ar = self._interpret_efficiency_score_ar(composite_score, scores, classification)
            interpretation_en = self._interpret_efficiency_score_en(composite_score, scores, classification)

            # التوصيات
            recommendations = self._get_efficiency_score_recommendations(composite_score, scores, classification)

            return {
                'analysis_name_ar': 'نقاط كفاءة الأصول',
                'analysis_name_en': 'Asset Efficiency Score',
                'result': composite_score,
                'component_scores': scores,
                'weights_used': weights,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نقاط الكفاءة = مجموع (نسب الدوران × الأوزان المعيارية)',
                'unit': 'نقاط / points',
                'benchmark_ranges': {
                    'excellent': '> 8.0',
                    'good': '6.0 - 8.0',
                    'average': '4.0 - 6.0',
                    'weak': '2.0 - 4.0',
                    'poor': '< 2.0'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب نقاط كفاءة الأصول: {str(e)}'}

    def days_working_capital(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        14. أيام رأس المال العامل
        Days Working Capital

        Formula: (Average Working Capital / Daily Sales)
        الصيغة: (متوسط رأس المال العامل / المبيعات اليومية)
        """
        try:
            required_bs_columns = ['current_assets', 'current_liabilities']
            required_is_columns = ['total_revenue']

            missing_bs = [col for col in required_bs_columns if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_columns if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - BS: {missing_bs}, IS: {missing_is}")

            # حساب رأس المال العامل
            working_capital = balance_sheet['current_assets'] - balance_sheet['current_liabilities']

            # حساب متوسط رأس المال العامل
            if len(balance_sheet) > 1:
                avg_working_capital = (working_capital + working_capital.shift(1)) / 2
                avg_working_capital = avg_working_capital.dropna()
            else:
                avg_working_capital = working_capital

            # حساب المبيعات اليومية
            daily_sales = income_statement['total_revenue'] / 365

            # محاذاة المؤشرات
            common_index = avg_working_capital.index.intersection(income_statement.index)
            avg_working_capital = avg_working_capital.loc[common_index]
            daily_sales = daily_sales.loc[common_index]

            # حساب أيام رأس المال العامل
            days_wc = (avg_working_capital / daily_sales).round(0)

            # تصنيف النتيجة
            classification = self._classify_days_working_capital(days_wc)

            # التفسير
            interpretation_ar = self._interpret_days_wc_ar(days_wc, avg_working_capital, classification)
            interpretation_en = self._interpret_days_wc_en(days_wc, avg_working_capital, classification)

            # التوصيات
            recommendations = self._get_days_wc_recommendations(days_wc, classification)

            return {
                'analysis_name_ar': 'أيام رأس المال العامل',
                'analysis_name_en': 'Days Working Capital',
                'result': days_wc,
                'average_working_capital': avg_working_capital,
                'daily_sales': daily_sales,
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'أيام رأس المال العامل = متوسط رأس المال العامل ÷ المبيعات اليومية',
                'unit': 'يوم / days',
                'benchmark_ranges': {
                    'excellent': '< 30 days',
                    'good': '30 - 60 days',
                    'average': '60 - 90 days',
                    'weak': '90 - 120 days',
                    'poor': '> 120 days'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب أيام رأس المال العامل: {str(e)}'}

    def operating_cycle(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        15. الدورة التشغيلية
        Operating Cycle

        Formula: Days Inventory Outstanding + Days Sales Outstanding
        الصيغة: أيام دوران المخزون + أيام تحصيل المبيعات
        """
        try:
            # حساب مكونات الدورة التشغيلية
            inventory_result = self.inventory_turnover(balance_sheet, income_statement)
            receivables_result = self.accounts_receivable_turnover(balance_sheet, income_statement)

            if 'error' in inventory_result or 'error' in receivables_result:
                raise ValueError("خطأ في حساب مكونات الدورة التشغيلية")

            # استخراج أيام دوران المخزون وتحصيل المبيعات
            dio = inventory_result['days_inventory_outstanding']
            dso = receivables_result['days_sales_outstanding']

            # حساب الدورة التشغيلية
            operating_cycle = dio + dso

            # تصنيف الدورة
            classification = self._classify_operating_cycle(operating_cycle)

            # التفسير
            interpretation_ar = self._interpret_operating_cycle_ar(operating_cycle, dio, dso, classification)
            interpretation_en = self._interpret_operating_cycle_en(operating_cycle, dio, dso, classification)

            # التوصيات
            recommendations = self._get_operating_cycle_recommendations(operating_cycle, dio, dso, classification)

            return {
                'analysis_name_ar': 'الدورة التشغيلية',
                'analysis_name_en': 'Operating Cycle',
                'result': operating_cycle,
                'components': {
                    'days_inventory_outstanding': dio,
                    'days_sales_outstanding': dso
                },
                'classification': classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'الدورة التشغيلية = أيام دوران المخزون + أيام تحصيل المبيعات',
                'unit': 'يوم / days',
                'benchmark_ranges': {
                    'excellent': '< 60 days',
                    'good': '60 - 90 days',
                    'average': '90 - 120 days',
                    'weak': '120 - 150 days',
                    'poor': '> 150 days'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب الدورة التشغيلية: {str(e)}'}

    # دوال التصنيف والتفسير (مختصرة لتوفير المساحة)
    def _classify_total_asset_turnover(self, ratio: pd.Series) -> pd.Series:
        """تصنيف معدل دوران إجمالي الأصول"""
        return ratio.apply(lambda x:
            'ممتاز' if x > 2.0 else
            'جيد' if x >= 1.5 else
            'متوسط' if x >= 1.0 else
            'ضعيف' if x >= 0.5 else
            'سيء'
        )

    def _interpret_total_asset_turnover_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        """تفسير معدل دوران إجمالي الأصول باللغة العربية"""
        avg_ratio = ratio.mean()
        latest_class = classification.iloc[-1]

        interpretation = f"معدل دوران إجمالي الأصول {avg_ratio:.2f} مرة، مما يعني أن الشركة تحقق "
        interpretation += f"{avg_ratio:.2f} ريال من المبيعات لكل ريال من الأصول.\n"

        if latest_class == 'ممتاز':
            interpretation += "كفاءة ممتازة في استخدام الأصول لتوليد الإيرادات."
        elif latest_class == 'جيد':
            interpretation += "كفاءة جيدة في استغلال الأصول."
        elif latest_class == 'متوسط':
            interpretation += "كفاءة متوسطة تحتاج لتحسين."
        else:
            interpretation += "كفاءة ضعيفة في استخدام الأصول تتطلب مراجعة شاملة."

        return interpretation

    def _interpret_total_asset_turnover_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        """English interpretation of total asset turnover"""
        avg_ratio = ratio.mean()
        return f"Total asset turnover of {avg_ratio:.2f}x indicates the company generates {avg_ratio:.2f} in sales for every unit of assets."

    def _get_total_asset_turnover_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        """توصيات معدل دوران إجمالي الأصول"""
        recommendations = []
        latest_class = classification.iloc[-1]

        if latest_class in ['ضعيف', 'سيء']:
            recommendations.extend([
                "تحسين استراتيجيات المبيعات والتسويق",
                "Improve sales and marketing strategies",
                "مراجعة كفاءة استخدام الأصول",
                "Review asset utilization efficiency",
                "التخلص من الأصول غير المنتجة",
                "Dispose of non-productive assets"
            ])
        elif latest_class == 'متوسط':
            recommendations.extend([
                "تحسين العمليات التشغيلية",
                "Improve operational processes",
                "زيادة الاستثمار في التكنولوجيا",
                "Increase investment in technology"
            ])

        return recommendations

    # دوال التصنيف والتفسير الأخرى (مختصرة)
    def _classify_fixed_asset_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 4.0 else 'جيد' if x >= 3.0 else 'متوسط' if x >= 2.0 else 'ضعيف' if x >= 1.0 else 'سيء')

    def _interpret_fixed_asset_turnover_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران الأصول الثابتة {ratio.mean():.2f} يشير إلى كفاءة استخدام المعدات والممتلكات."

    def _interpret_fixed_asset_turnover_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"Fixed asset turnover of {ratio.mean():.2f} indicates efficiency in utilizing property and equipment."

    def _get_fixed_asset_turnover_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين استخدام الأصول الثابتة", "Improve fixed asset utilization"]

    def _classify_inventory_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 12 else 'جيد' if x >= 8 else 'متوسط' if x >= 6 else 'ضعيف' if x >= 4 else 'سيء')

    def _interpret_inventory_turnover_ar(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران المخزون {ratio.mean():.1f} مرة سنوياً، أي كل {days.mean():.0f} يوم تقريباً."

    def _interpret_inventory_turnover_en(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> str:
        return f"Inventory turns {ratio.mean():.1f} times annually, approximately every {days.mean():.0f} days."

    def _get_inventory_turnover_recommendations(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> List[str]:
        recommendations = []
        if days.mean() > 90:
            recommendations.extend(["تحسين إدارة المخزون", "Improve inventory management"])
        return recommendations

    # باقي دوال التصنيف والتفسير للنسب الأخرى...
    def _classify_receivables_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 12 else 'جيد' if x >= 8 else 'متوسط' if x >= 6 else 'ضعيف' if x >= 4 else 'سيء')

    def _interpret_receivables_turnover_ar(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران المدينين {ratio.mean():.1f} مرة، متوسط فترة التحصيل {days.mean():.0f} يوم."

    def _interpret_receivables_turnover_en(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> str:
        return f"Receivables turnover {ratio.mean():.1f} times, average collection period {days.mean():.0f} days."

    def _get_receivables_turnover_recommendations(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين سياسات التحصيل", "Improve collection policies"]

    def _classify_payables_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'محافظ' if x < 6 else 'متوازن' if x <= 10 else 'عدواني')

    def _interpret_payables_turnover_ar(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران الدائنين {ratio.mean():.1f} مرة، متوسط فترة السداد {days.mean():.0f} يوم."

    def _interpret_payables_turnover_en(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> str:
        return f"Payables turnover {ratio.mean():.1f} times, average payment period {days.mean():.0f} days."

    def _get_payables_turnover_recommendations(self, ratio: pd.Series, days: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة الدائنين", "Improve payables management"]

    # دوال مساعدة إضافية
    def _normalize_turnover_score(self, ratio: pd.Series, ratio_type: str) -> pd.Series:
        """تطبيع نقاط نسب الدوران"""
        if ratio_type == 'total_asset':
            return ratio.apply(lambda x: min(10, max(0, x * 5)))
        elif ratio_type == 'inventory':
            return ratio.apply(lambda x: min(10, max(0, x * 0.8)))
        elif ratio_type == 'receivables':
            return ratio.apply(lambda x: min(10, max(0, x * 0.8)))
        else:
            return ratio.apply(lambda x: min(10, max(0, x)))

    # دوال التصنيف والتفسير المتبقية (مختصرة)
    def _classify_wc_turnover(self, ratio: pd.Series, wc: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 6 else 'جيد' if x >= 4 else 'متوسط' if x >= 2 else 'ضعيف' if x >= 1 else 'سيء')

    def _interpret_wc_turnover_ar(self, ratio: pd.Series, wc: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران رأس المال العامل {ratio.mean():.2f} مرة."

    def _interpret_wc_turnover_en(self, ratio: pd.Series, wc: pd.Series, classification: pd.Series) -> str:
        return f"Working capital turnover {ratio.mean():.2f} times."

    def _get_wc_turnover_recommendations(self, ratio: pd.Series, wc: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة رأس المال العامل", "Improve working capital management"]

    def _classify_cash_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 20 else 'جيد' if x >= 15 else 'متوسط' if x >= 10 else 'ضعيف' if x >= 5 else 'سيء')

    def _interpret_cash_turnover_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران النقد {ratio.mean():.1f} مرة يشير إلى كفاءة استخدام السيولة."

    def _interpret_cash_turnover_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"Cash turnover {ratio.mean():.1f} times indicates liquidity utilization efficiency."

    def _get_cash_turnover_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة النقد", "Improve cash management"]

    def _classify_equity_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 3.0 else 'جيد' if x >= 2.0 else 'متوسط' if x >= 1.5 else 'ضعيف' if x >= 1.0 else 'سيء')

    def _interpret_equity_turnover_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران حقوق الملكية {ratio.mean():.2f} مرة."

    def _interpret_equity_turnover_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"Equity turnover {ratio.mean():.2f} times."

    def _get_equity_turnover_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين استخدام حقوق الملكية", "Improve equity utilization"]

    def _classify_capital_intensity(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'كثافة منخفضة' if x < 0.5 else 'كثافة متوسطة' if x <= 1.0 else 'كثافة عالية' if x <= 2.0 else 'كثافة عالية جداً')

    def _interpret_capital_intensity_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"نسبة كثافة رأس المال {ratio.mean():.2f} تشير إلى مستوى الاستثمار المطلوب."

    def _interpret_capital_intensity_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"Capital intensity ratio {ratio.mean():.2f} indicates required investment level."

    def _get_capital_intensity_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["مراجعة استراتيجية الاستثمار", "Review investment strategy"]

    def _classify_asset_utilization(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 15 else 'جيد' if x >= 10 else 'متوسط' if x >= 5 else 'ضعيف' if x >= 2 else 'سيء')

    def _interpret_asset_utilization_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"نسبة استغلال الأصول {ratio.mean():.1f}% تشير إلى كفاءة توليد الأرباح."

    def _interpret_asset_utilization_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"Asset utilization {ratio.mean():.1f}% indicates profit generation efficiency."

    def _get_asset_utilization_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين استغلال الأصول", "Improve asset utilization"]

    def _classify_current_asset_turnover(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 4.0 else 'جيد' if x >= 3.0 else 'متوسط' if x >= 2.0 else 'ضعيف' if x >= 1.0 else 'سيء')

    def _interpret_current_asset_turnover_ar(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"معدل دوران الأصول المتداولة {ratio.mean():.2f} مرة."

    def _interpret_current_asset_turnover_en(self, ratio: pd.Series, classification: pd.Series) -> str:
        return f"Current asset turnover {ratio.mean():.2f} times."

    def _get_current_asset_turnover_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة الأصول المتداولة", "Improve current asset management"]

    def _classify_revenue_per_employee(self, ratio: pd.Series) -> pd.Series:
        return ratio.apply(lambda x: 'ممتاز' if x > 1000000 else 'جيد' if x >= 500000 else 'متوسط' if x >= 250000 else 'ضعيف' if x >= 100000 else 'سيء')

    def _interpret_revenue_per_employee_ar(self, ratio: pd.Series, classification: pd.Series, estimated: bool) -> str:
        note = " (بيانات تقديرية)" if estimated else ""
        return f"الإيرادات لكل موظف {ratio.mean():,.0f} ريال{note}."

    def _interpret_revenue_per_employee_en(self, ratio: pd.Series, classification: pd.Series, estimated: bool) -> str:
        note = " (estimated data)" if estimated else ""
        return f"Revenue per employee {ratio.mean():,.0f} SAR{note}."

    def _get_revenue_per_employee_recommendations(self, ratio: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إنتاجية الموظفين", "Improve employee productivity"]

    def _classify_efficiency_score(self, score: pd.Series) -> pd.Series:
        return score.apply(lambda x: 'ممتاز' if x > 8.0 else 'جيد' if x >= 6.0 else 'متوسط' if x >= 4.0 else 'ضعيف' if x >= 2.0 else 'سيء')

    def _interpret_efficiency_score_ar(self, score: pd.Series, components: Dict, classification: pd.Series) -> str:
        return f"نقاط كفاءة الأصول {score.mean():.1f} من 10 نقاط."

    def _interpret_efficiency_score_en(self, score: pd.Series, components: Dict, classification: pd.Series) -> str:
        return f"Asset efficiency score {score.mean():.1f} out of 10 points."

    def _get_efficiency_score_recommendations(self, score: pd.Series, components: Dict, classification: pd.Series) -> List[str]:
        return ["تحسين الكفاءة الإجمالية", "Improve overall efficiency"]

    def _classify_days_working_capital(self, days: pd.Series) -> pd.Series:
        return days.apply(lambda x: 'ممتاز' if x < 30 else 'جيد' if x <= 60 else 'متوسط' if x <= 90 else 'ضعيف' if x <= 120 else 'سيء')

    def _interpret_days_wc_ar(self, days: pd.Series, wc: pd.Series, classification: pd.Series) -> str:
        return f"أيام رأس المال العامل {days.mean():.0f} يوم."

    def _interpret_days_wc_en(self, days: pd.Series, wc: pd.Series, classification: pd.Series) -> str:
        return f"Days working capital {days.mean():.0f} days."

    def _get_days_wc_recommendations(self, days: pd.Series, classification: pd.Series) -> List[str]:
        return ["تحسين إدارة رأس المال العامل", "Improve working capital management"]

    def _classify_operating_cycle(self, cycle: pd.Series) -> pd.Series:
        return cycle.apply(lambda x: 'ممتاز' if x < 60 else 'جيد' if x <= 90 else 'متوسط' if x <= 120 else 'ضعيف' if x <= 150 else 'سيء')

    def _interpret_operating_cycle_ar(self, cycle: pd.Series, dio: pd.Series, dso: pd.Series, classification: pd.Series) -> str:
        return f"الدورة التشغيلية {cycle.mean():.0f} يوم ({dio.mean():.0f} مخزون + {dso.mean():.0f} مدينين)."

    def _interpret_operating_cycle_en(self, cycle: pd.Series, dio: pd.Series, dso: pd.Series, classification: pd.Series) -> str:
        return f"Operating cycle {cycle.mean():.0f} days ({dio.mean():.0f} inventory + {dso.mean():.0f} receivables)."

    def _get_operating_cycle_recommendations(self, cycle: pd.Series, dio: pd.Series, dso: pd.Series, classification: pd.Series) -> List[str]:
        return ["تقليل الدورة التشغيلية", "Reduce operating cycle"]

    def generate_activity_dashboard(self, balance_sheet: pd.DataFrame,
                                  income_statement: pd.DataFrame,
                                  employee_data: pd.DataFrame = None) -> Dict:
        """
        إنشاء لوحة تحكم شاملة لنسب النشاط والكفاءة
        Generate comprehensive activity and efficiency ratios dashboard
        """
        try:
            dashboard_results = {}

            # حساب جميع نسب النشاط والكفاءة
            dashboard_results['total_asset_turnover'] = self.total_asset_turnover(balance_sheet, income_statement)
            dashboard_results['fixed_asset_turnover'] = self.fixed_asset_turnover(balance_sheet, income_statement)
            dashboard_results['inventory_turnover'] = self.inventory_turnover(balance_sheet, income_statement)
            dashboard_results['receivables_turnover'] = self.accounts_receivable_turnover(balance_sheet, income_statement)
            dashboard_results['payables_turnover'] = self.accounts_payable_turnover(balance_sheet, income_statement)
            dashboard_results['working_capital_turnover'] = self.working_capital_turnover(balance_sheet, income_statement)
            dashboard_results['cash_turnover'] = self.cash_turnover(balance_sheet, income_statement)
            dashboard_results['equity_turnover'] = self.equity_turnover(balance_sheet, income_statement)
            dashboard_results['capital_intensity'] = self.capital_intensity_ratio(balance_sheet, income_statement)
            dashboard_results['asset_utilization'] = self.asset_utilization_ratio(balance_sheet, income_statement)
            dashboard_results['current_asset_turnover'] = self.current_asset_turnover(balance_sheet, income_statement)
            dashboard_results['revenue_per_employee'] = self.revenue_per_employee(income_statement, employee_data)
            dashboard_results['efficiency_score'] = self.asset_efficiency_score(balance_sheet, income_statement)
            dashboard_results['days_working_capital'] = self.days_working_capital(balance_sheet, income_statement)
            dashboard_results['operating_cycle'] = self.operating_cycle(balance_sheet, income_statement)

            # إنشاء ملخص شامل
            summary = self._create_activity_summary(dashboard_results)

            return {
                'analysis_name_ar': 'لوحة تحكم نسب النشاط والكفاءة الشاملة',
                'analysis_name_en': 'Comprehensive Activity & Efficiency Ratios Dashboard',
                'total_ratios': 15,
                'results': dashboard_results,
                'summary': summary,
                'overall_efficiency_score': self._calculate_overall_efficiency_score(dashboard_results)
            }

        except Exception as e:
            return {'error': f'خطأ في إنشاء لوحة تحكم النشاط والكفاءة: {str(e)}'}

    def _create_activity_summary(self, results: Dict) -> Dict:
        """إنشاء ملخص نسب النشاط والكفاءة"""
        successful_analyses = [k for k, v in results.items() if 'error' not in v]
        failed_analyses = [k for k, v in results.items() if 'error' in v]

        summary = {
            'successful_ratios': len(successful_analyses),
            'failed_ratios': len(failed_analyses),
            'efficiency_status': 'متوسط',
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

    def _calculate_overall_efficiency_score(self, results: Dict) -> float:
        """حساب النقاط الإجمالية للكفاءة"""
        total_score = 0
        count = 0

        score_mapping = {'ممتاز': 5, 'جيد': 4, 'متوسط': 3, 'ضعيف': 2, 'سيء': 1}

        for ratio_data in results.values():
            if 'error' not in ratio_data and 'classification' in ratio_data:
                latest_class = ratio_data['classification'].iloc[-1] if hasattr(ratio_data['classification'], 'iloc') else ratio_data['classification']
                total_score += score_mapping.get(latest_class, 0)
                count += 1

        return round(total_score / count if count > 0 else 0, 2)

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء بيانات تجريبية
    sample_balance_sheet = pd.DataFrame({
        'total_assets': [100000, 110000, 125000],
        'current_assets': [45000, 50000, 55000],
        'property_plant_equipment': [55000, 60000, 70000],
        'inventory': [13000, 12000, 13000],
        'accounts_receivable': [12000, 14000, 15000],
        'accounts_payable': [15000, 16000, 17000],
        'current_liabilities': [25000, 28000, 30000],
        'total_equity': [50000, 55000, 62000],
        'cash_and_equivalents': [15000, 18000, 20000]
    }, index=['2021', '2022', '2023'])

    sample_income_statement = pd.DataFrame({
        'total_revenue': [80000, 88000, 96000],
        'cost_of_goods_sold': [48000, 52000, 57000],
        'operating_income': [12000, 14000, 15000]
    }, index=['2021', '2022', '2023'])

    sample_employee_data = pd.DataFrame({
        'number_of_employees': [100, 110, 120]
    }, index=['2021', '2022', '2023'])

    # تشغيل التحليل
    analyzer = ActivityEfficiencyRatios(sample_balance_sheet)
    dashboard = analyzer.generate_activity_dashboard(
        sample_balance_sheet,
        sample_income_statement,
        sample_employee_data
    )

    print("نتائج تحليل نسب النشاط والكفاءة:")
    print(f"عدد النسب المحسوبة: {dashboard['summary']['successful_ratios']}")
    print(f"النقاط الإجمالية للكفاءة: {dashboard['overall_efficiency_score']}")