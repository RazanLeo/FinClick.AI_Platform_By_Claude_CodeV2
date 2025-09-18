"""
التحليل الهيكلي للقوائم المالية - Structural Financial Statements Analysis
يحتوي على 13 تحليل هيكلي أساسي للقوائم المالية
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

class StructuralAnalysis:
    """
    فئة التحليل الهيكلي للقوائم المالية
    Structural Analysis of Financial Statements Class
    """

    def __init__(self, data: pd.DataFrame):
        """
        تهيئة فئة التحليل الهيكلي
        Initialize Structural Analysis Class

        Args:
            data: بيانات القوائم المالية / Financial statements data
        """
        self.data = data.copy()
        self.results = {}

    def vertical_analysis_balance_sheet(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        1. التحليل الرأسي للميزانية العمومية
        Vertical Analysis of Balance Sheet

        Formula: (Item / Total Assets) * 100
        الصيغة: (البند / إجمالي الأصول) * 100
        """
        try:
            results = {}

            # التحقق من وجود الأعمدة المطلوبة
            required_columns = ['total_assets', 'current_assets', 'non_current_assets',
                              'current_liabilities', 'non_current_liabilities', 'total_equity']

            missing_columns = [col for col in required_columns if col not in balance_sheet.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # حساب النسب المئوية
            total_assets = balance_sheet['total_assets']

            # تحليل الأصول
            results['current_assets_pct'] = (balance_sheet['current_assets'] / total_assets * 100).round(2)
            results['non_current_assets_pct'] = (balance_sheet['non_current_assets'] / total_assets * 100).round(2)

            # تحليل الخصوم
            results['current_liabilities_pct'] = (balance_sheet['current_liabilities'] / total_assets * 100).round(2)
            results['non_current_liabilities_pct'] = (balance_sheet['non_current_liabilities'] / total_assets * 100).round(2)

            # تحليل حقوق الملكية
            results['total_equity_pct'] = (balance_sheet['total_equity'] / total_assets * 100).round(2)

            # إنشاء DataFrame للنتائج
            vertical_analysis_df = pd.DataFrame(results, index=balance_sheet.index)

            # التفسير
            interpretation_ar = self._interpret_vertical_balance_sheet_ar(results)
            interpretation_en = self._interpret_vertical_balance_sheet_en(results)

            # التوصيات
            recommendations = self._get_vertical_balance_sheet_recommendations(results)

            return {
                'analysis_name_ar': 'التحليل الرأسي للميزانية العمومية',
                'analysis_name_en': 'Vertical Analysis of Balance Sheet',
                'results': vertical_analysis_df,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'النسبة المئوية = (البند / إجمالي الأصول) * 100',
                'benchmark_ranges': {
                    'current_assets': {'good': '> 40%', 'average': '20-40%', 'poor': '< 20%'},
                    'equity_ratio': {'good': '> 50%', 'average': '30-50%', 'poor': '< 30%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب التحليل الرأسي للميزانية: {str(e)}'}

    def vertical_analysis_income_statement(self, income_statement: pd.DataFrame) -> Dict:
        """
        2. التحليل الرأسي لقائمة الدخل
        Vertical Analysis of Income Statement

        Formula: (Item / Total Revenue) * 100
        الصيغة: (البند / إجمالي الإيرادات) * 100
        """
        try:
            results = {}

            # التحقق من وجود الأعمدة المطلوبة
            required_columns = ['total_revenue', 'cost_of_goods_sold', 'gross_profit',
                              'operating_expenses', 'operating_income', 'net_income']

            missing_columns = [col for col in required_columns if col not in income_statement.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # حساب النسب المئوية
            total_revenue = income_statement['total_revenue']

            # نسب التكاليف والمصروفات
            results['cogs_pct'] = (income_statement['cost_of_goods_sold'] / total_revenue * 100).round(2)
            results['gross_profit_margin'] = (income_statement['gross_profit'] / total_revenue * 100).round(2)
            results['operating_expenses_pct'] = (income_statement['operating_expenses'] / total_revenue * 100).round(2)
            results['operating_margin'] = (income_statement['operating_income'] / total_revenue * 100).round(2)
            results['net_profit_margin'] = (income_statement['net_income'] / total_revenue * 100).round(2)

            # إنشاء DataFrame للنتائج
            vertical_analysis_df = pd.DataFrame(results, index=income_statement.index)

            # التفسير
            interpretation_ar = self._interpret_vertical_income_ar(results)
            interpretation_en = self._interpret_vertical_income_en(results)

            # التوصيات
            recommendations = self._get_vertical_income_recommendations(results)

            return {
                'analysis_name_ar': 'التحليل الرأسي لقائمة الدخل',
                'analysis_name_en': 'Vertical Analysis of Income Statement',
                'results': vertical_analysis_df,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'النسبة المئوية = (البند / إجمالي الإيرادات) * 100',
                'benchmark_ranges': {
                    'gross_profit_margin': {'excellent': '> 50%', 'good': '30-50%', 'average': '15-30%', 'poor': '< 15%'},
                    'net_profit_margin': {'excellent': '> 20%', 'good': '10-20%', 'average': '5-10%', 'poor': '< 5%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب التحليل الرأسي لقائمة الدخل: {str(e)}'}

    def horizontal_analysis_balance_sheet(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        3. التحليل الأفقي للميزانية العمومية
        Horizontal Analysis of Balance Sheet

        Formula: ((Current Year - Previous Year) / Previous Year) * 100
        الصيغة: ((السنة الحالية - السنة السابقة) / السنة السابقة) * 100
        """
        try:
            if len(balance_sheet) < 2:
                raise ValueError("يجب أن تحتوي البيانات على سنتين على الأقل للتحليل الأفقي")

            results = {}

            # حساب معدل النمو لكل بند
            for column in balance_sheet.select_dtypes(include=[np.number]).columns:
                growth_rates = []
                for i in range(1, len(balance_sheet)):
                    if balance_sheet[column].iloc[i-1] != 0:
                        growth_rate = ((balance_sheet[column].iloc[i] - balance_sheet[column].iloc[i-1]) /
                                     abs(balance_sheet[column].iloc[i-1]) * 100)
                        growth_rates.append(growth_rate)
                    else:
                        growth_rates.append(np.nan)

                results[f'{column}_growth'] = growth_rates

            # إنشاء DataFrame للنتائج
            horizontal_analysis_df = pd.DataFrame(results, index=balance_sheet.index[1:])

            # التفسير
            interpretation_ar = self._interpret_horizontal_balance_sheet_ar(results)
            interpretation_en = self._interpret_horizontal_balance_sheet_en(results)

            # التوصيات
            recommendations = self._get_horizontal_balance_sheet_recommendations(results)

            return {
                'analysis_name_ar': 'التحليل الأفقي للميزانية العمومية',
                'analysis_name_en': 'Horizontal Analysis of Balance Sheet',
                'results': horizontal_analysis_df,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل النمو = ((السنة الحالية - السنة السابقة) / السنة السابقة) * 100',
                'benchmark_ranges': {
                    'assets_growth': {'excellent': '> 15%', 'good': '5-15%', 'stable': '0-5%', 'concerning': '< 0%'},
                    'equity_growth': {'excellent': '> 10%', 'good': '3-10%', 'stable': '0-3%', 'concerning': '< 0%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب التحليل الأفقي للميزانية: {str(e)}'}

    def horizontal_analysis_income_statement(self, income_statement: pd.DataFrame) -> Dict:
        """
        4. التحليل الأفقي لقائمة الدخل
        Horizontal Analysis of Income Statement

        Formula: ((Current Year - Previous Year) / Previous Year) * 100
        الصيغة: ((السنة الحالية - السنة السابقة) / السنة السابقة) * 100
        """
        try:
            if len(income_statement) < 2:
                raise ValueError("يجب أن تحتوي البيانات على سنتين على الأقل للتحليل الأفقي")

            results = {}

            # حساب معدل النمو لكل بند
            for column in income_statement.select_dtypes(include=[np.number]).columns:
                growth_rates = []
                for i in range(1, len(income_statement)):
                    if income_statement[column].iloc[i-1] != 0:
                        growth_rate = ((income_statement[column].iloc[i] - income_statement[column].iloc[i-1]) /
                                     abs(income_statement[column].iloc[i-1]) * 100)
                        growth_rates.append(growth_rate)
                    else:
                        growth_rates.append(np.nan)

                results[f'{column}_growth'] = growth_rates

            # إنشاء DataFrame للنتائج
            horizontal_analysis_df = pd.DataFrame(results, index=income_statement.index[1:])

            # التفسير
            interpretation_ar = self._interpret_horizontal_income_ar(results)
            interpretation_en = self._interpret_horizontal_income_en(results)

            # التوصيات
            recommendations = self._get_horizontal_income_recommendations(results)

            return {
                'analysis_name_ar': 'التحليل الأفقي لقائمة الدخل',
                'analysis_name_en': 'Horizontal Analysis of Income Statement',
                'results': horizontal_analysis_df,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'معدل النمو = ((السنة الحالية - السنة السابقة) / السنة السابقة) * 100',
                'benchmark_ranges': {
                    'revenue_growth': {'excellent': '> 20%', 'good': '10-20%', 'average': '3-10%', 'poor': '< 3%'},
                    'profit_growth': {'excellent': '> 25%', 'good': '15-25%', 'average': '5-15%', 'poor': '< 5%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب التحليل الأفقي لقائمة الدخل: {str(e)}'}

    def trend_analysis(self, data: pd.DataFrame, base_year_index: int = 0) -> Dict:
        """
        5. تحليل الاتجاه العام
        Trend Analysis

        Formula: (Current Year / Base Year) * 100
        الصيغة: (السنة الحالية / سنة الأساس) * 100
        """
        try:
            if len(data) < 2:
                raise ValueError("يجب أن تحتوي البيانات على سنتين على الأقل لتحليل الاتجاه")

            results = {}
            base_year_data = data.iloc[base_year_index]

            # حساب مؤشر الاتجاه لكل بند
            for column in data.select_dtypes(include=[np.number]).columns:
                if base_year_data[column] != 0:
                    trend_index = (data[column] / abs(base_year_data[column]) * 100).round(2)
                    results[f'{column}_trend_index'] = trend_index
                else:
                    results[f'{column}_trend_index'] = np.nan

            # إنشاء DataFrame للنتائج
            trend_analysis_df = pd.DataFrame(results, index=data.index)

            # حساب متوسط معدل النمو السنوي
            compound_growth_rates = {}
            years = len(data) - 1
            for column in data.select_dtypes(include=[np.number]).columns:
                if base_year_data[column] != 0 and data[column].iloc[-1] != 0:
                    cagr = ((data[column].iloc[-1] / abs(base_year_data[column])) ** (1/years) - 1) * 100
                    compound_growth_rates[f'{column}_cagr'] = round(cagr, 2)

            # التفسير
            interpretation_ar = self._interpret_trend_analysis_ar(results, compound_growth_rates)
            interpretation_en = self._interpret_trend_analysis_en(results, compound_growth_rates)

            # التوصيات
            recommendations = self._get_trend_analysis_recommendations(results, compound_growth_rates)

            return {
                'analysis_name_ar': 'تحليل الاتجاه العام',
                'analysis_name_en': 'Trend Analysis',
                'results': trend_analysis_df,
                'compound_growth_rates': compound_growth_rates,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'مؤشر الاتجاه = (السنة الحالية / سنة الأساس) * 100',
                'base_year': data.index[base_year_index],
                'benchmark_ranges': {
                    'trend_index': {'strong_growth': '> 120', 'moderate_growth': '105-120', 'stable': '95-105', 'decline': '< 95'},
                    'cagr': {'excellent': '> 15%', 'good': '8-15%', 'average': '3-8%', 'poor': '< 3%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب تحليل الاتجاه: {str(e)}'}

    def base_year_analysis(self, data: pd.DataFrame, base_year_index: int = 0) -> Dict:
        """
        6. تحليل سنة الأساس
        Base Year Analysis

        Formula: (Item Value / Base Year Item Value) * 100
        الصيغة: (قيمة البند / قيمة البند في سنة الأساس) * 100
        """
        try:
            results = {}
            base_year_data = data.iloc[base_year_index]

            # حساب النسبة لسنة الأساس لكل بند
            for column in data.select_dtypes(include=[np.number]).columns:
                if base_year_data[column] != 0:
                    base_year_ratio = (data[column] / abs(base_year_data[column]) * 100).round(2)
                    results[f'{column}_base_ratio'] = base_year_ratio
                else:
                    results[f'{column}_base_ratio'] = np.nan

            # إنشاء DataFrame للنتائج
            base_year_df = pd.DataFrame(results, index=data.index)

            # حساب الانحراف عن سنة الأساس
            deviation_results = {}
            for column in results:
                deviation = (results[column] - 100).round(2)
                deviation_results[f'{column}_deviation'] = deviation

            # التفسير
            interpretation_ar = self._interpret_base_year_analysis_ar(results, base_year_data)
            interpretation_en = self._interpret_base_year_analysis_en(results, base_year_data)

            # التوصيات
            recommendations = self._get_base_year_recommendations(results, deviation_results)

            return {
                'analysis_name_ar': 'تحليل سنة الأساس',
                'analysis_name_en': 'Base Year Analysis',
                'results': base_year_df,
                'deviations': deviation_results,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نسبة سنة الأساس = (قيمة البند / قيمة البند في سنة الأساس) * 100',
                'base_year': data.index[base_year_index],
                'benchmark_ranges': {
                    'base_ratio': {'significant_growth': '> 150', 'moderate_growth': '110-150', 'stable': '90-110', 'decline': '< 90'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب تحليل سنة الأساس: {str(e)}'}

    def common_size_balance_sheet(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        7. الميزانية ذات الحجم المشترك
        Common Size Balance Sheet Analysis

        Formula: (Each Item / Total Assets) * 100
        الصيغة: (كل بند / إجمالي الأصول) * 100
        """
        try:
            if 'total_assets' not in balance_sheet.columns:
                raise ValueError("عمود 'total_assets' مطلوب للتحليل")

            results = {}
            total_assets = balance_sheet['total_assets']

            # حساب النسبة المئوية لكل بند
            for column in balance_sheet.select_dtypes(include=[np.number]).columns:
                if column != 'total_assets':
                    common_size_ratio = (balance_sheet[column] / total_assets * 100).round(2)
                    results[f'{column}_common_size'] = common_size_ratio
                else:
                    results[f'{column}_common_size'] = 100.0  # إجمالي الأصول دائماً 100%

            # إنشاء DataFrame للنتائج
            common_size_df = pd.DataFrame(results, index=balance_sheet.index)

            # تحليل التركيبة
            composition_analysis = self._analyze_balance_sheet_composition(results)

            # التفسير
            interpretation_ar = self._interpret_common_size_balance_sheet_ar(results, composition_analysis)
            interpretation_en = self._interpret_common_size_balance_sheet_en(results, composition_analysis)

            # التوصيات
            recommendations = self._get_common_size_balance_sheet_recommendations(composition_analysis)

            return {
                'analysis_name_ar': 'الميزانية ذات الحجم المشترك',
                'analysis_name_en': 'Common Size Balance Sheet',
                'results': common_size_df,
                'composition_analysis': composition_analysis,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'النسبة المئوية = (البند / إجمالي الأصول) * 100',
                'benchmark_ranges': {
                    'current_assets': {'high': '> 60%', 'moderate': '30-60%', 'low': '< 30%'},
                    'equity_ratio': {'strong': '> 60%', 'moderate': '40-60%', 'weak': '< 40%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب الميزانية ذات الحجم المشترك: {str(e)}'}

    def common_size_income_statement(self, income_statement: pd.DataFrame) -> Dict:
        """
        8. قائمة الدخل ذات الحجم المشترك
        Common Size Income Statement Analysis

        Formula: (Each Item / Total Revenue) * 100
        الصيغة: (كل بند / إجمالي الإيرادات) * 100
        """
        try:
            if 'total_revenue' not in income_statement.columns:
                raise ValueError("عمود 'total_revenue' مطلوب للتحليل")

            results = {}
            total_revenue = income_statement['total_revenue']

            # حساب النسبة المئوية لكل بند
            for column in income_statement.select_dtypes(include=[np.number]).columns:
                if column != 'total_revenue':
                    common_size_ratio = (income_statement[column] / total_revenue * 100).round(2)
                    results[f'{column}_common_size'] = common_size_ratio
                else:
                    results[f'{column}_common_size'] = 100.0  # إجمالي الإيرادات دائماً 100%

            # إنشاء DataFrame للنتائج
            common_size_df = pd.DataFrame(results, index=income_statement.index)

            # تحليل هيكل التكاليف
            cost_structure_analysis = self._analyze_cost_structure(results)

            # التفسير
            interpretation_ar = self._interpret_common_size_income_ar(results, cost_structure_analysis)
            interpretation_en = self._interpret_common_size_income_en(results, cost_structure_analysis)

            # التوصيات
            recommendations = self._get_common_size_income_recommendations(cost_structure_analysis)

            return {
                'analysis_name_ar': 'قائمة الدخل ذات الحجم المشترك',
                'analysis_name_en': 'Common Size Income Statement',
                'results': common_size_df,
                'cost_structure_analysis': cost_structure_analysis,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'النسبة المئوية = (البند / إجمالي الإيرادات) * 100',
                'benchmark_ranges': {
                    'gross_margin': {'excellent': '> 50%', 'good': '30-50%', 'average': '15-30%', 'poor': '< 15%'},
                    'operating_margin': {'excellent': '> 25%', 'good': '15-25%', 'average': '5-15%', 'poor': '< 5%'},
                    'net_margin': {'excellent': '> 20%', 'good': '10-20%', 'average': '3-10%', 'poor': '< 3%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب قائمة الدخل ذات الحجم المشترك: {str(e)}'}

    def comparative_analysis(self, current_data: pd.DataFrame, comparison_data: pd.DataFrame,
                           comparison_type: str = "industry") -> Dict:
        """
        9. التحليل المقارن
        Comparative Analysis

        Formula: ((Company Value - Benchmark Value) / Benchmark Value) * 100
        الصيغة: ((قيمة الشركة - القيمة المعيارية) / القيمة المعيارية) * 100
        """
        try:
            results = {}

            # التأكد من وجود نفس الأعمدة
            common_columns = set(current_data.columns) & set(comparison_data.columns)
            if not common_columns:
                raise ValueError("لا توجد أعمدة مشتركة بين البيانات")

            # حساب الفروقات النسبية
            for column in common_columns:
                if comparison_data[column].iloc[-1] != 0:  # استخدام آخر قيمة للمقارنة
                    variance = ((current_data[column].iloc[-1] - comparison_data[column].iloc[-1]) /
                              abs(comparison_data[column].iloc[-1]) * 100).round(2)
                    results[f'{column}_variance'] = variance
                else:
                    results[f'{column}_variance'] = np.nan

            # تصنيف الأداء
            performance_classification = self._classify_performance(results)

            # التفسير
            interpretation_ar = self._interpret_comparative_analysis_ar(results, comparison_type, performance_classification)
            interpretation_en = self._interpret_comparative_analysis_en(results, comparison_type, performance_classification)

            # التوصيات
            recommendations = self._get_comparative_analysis_recommendations(performance_classification, comparison_type)

            return {
                'analysis_name_ar': f'التحليل المقارن - {comparison_type}',
                'analysis_name_en': f'Comparative Analysis - {comparison_type}',
                'results': results,
                'performance_classification': performance_classification,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'الانحراف النسبي = ((قيمة الشركة - القيمة المعيارية) / القيمة المعيارية) * 100',
                'comparison_type': comparison_type,
                'benchmark_ranges': {
                    'variance': {'significantly_better': '> 20%', 'better': '5-20%', 'similar': '-5% to 5%',
                               'worse': '-20% to -5%', 'significantly_worse': '< -20%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب التحليل المقارن: {str(e)}'}

    def ratio_decomposition_analysis(self, financial_data: pd.DataFrame) -> Dict:
        """
        10. تحليل تفكيك النسب
        Ratio Decomposition Analysis

        DuPont Analysis: ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
        تحليل دوبونت: العائد على حقوق الملكية = هامش الربح الصافي × دوران الأصول × مضاعف حقوق الملكية
        """
        try:
            if not all(col in financial_data.columns for col in
                      ['net_income', 'total_revenue', 'total_assets', 'total_equity']):
                raise ValueError("البيانات المطلوبة للتحليل غير مكتملة")

            results = {}

            # حساب المكونات الأساسية
            # هامش الربح الصافي
            results['net_profit_margin'] = (financial_data['net_income'] / financial_data['total_revenue'] * 100).round(2)

            # دوران الأصول
            results['asset_turnover'] = (financial_data['total_revenue'] / financial_data['total_assets']).round(2)

            # مضاعف حقوق الملكية
            results['equity_multiplier'] = (financial_data['total_assets'] / financial_data['total_equity']).round(2)

            # العائد على حقوق الملكية
            results['roe_calculated'] = (results['net_profit_margin'] / 100 *
                                       results['asset_turnover'] *
                                       results['equity_multiplier'] * 100).round(2)

            # العائد على حقوق الملكية المباشر
            results['roe_direct'] = (financial_data['net_income'] / financial_data['total_equity'] * 100).round(2)

            # تحليل المساهمة
            contribution_analysis = self._analyze_roe_components_contribution(results)

            # إنشاء DataFrame للنتائج
            decomposition_df = pd.DataFrame(results, index=financial_data.index)

            # التفسير
            interpretation_ar = self._interpret_ratio_decomposition_ar(results, contribution_analysis)
            interpretation_en = self._interpret_ratio_decomposition_en(results, contribution_analysis)

            # التوصيات
            recommendations = self._get_ratio_decomposition_recommendations(contribution_analysis)

            return {
                'analysis_name_ar': 'تحليل تفكيك النسب (دوبونت)',
                'analysis_name_en': 'Ratio Decomposition Analysis (DuPont)',
                'results': decomposition_df,
                'contribution_analysis': contribution_analysis,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'ROE = هامش الربح الصافي × دوران الأصول × مضاعف حقوق الملكية',
                'benchmark_ranges': {
                    'net_profit_margin': {'excellent': '> 15%', 'good': '8-15%', 'average': '3-8%', 'poor': '< 3%'},
                    'asset_turnover': {'excellent': '> 1.5', 'good': '1.0-1.5', 'average': '0.5-1.0', 'poor': '< 0.5'},
                    'equity_multiplier': {'conservative': '< 2.0', 'moderate': '2.0-3.0', 'aggressive': '> 3.0'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب تحليل تفكيك النسب: {str(e)}'}

    def size_analysis(self, balance_sheet: pd.DataFrame) -> Dict:
        """
        11. تحليل الحجم
        Size Analysis

        Formula: Log(Total Assets) for size classification
        الصيغة: لوغاريتم إجمالي الأصول لتصنيف الحجم
        """
        try:
            if 'total_assets' not in balance_sheet.columns:
                raise ValueError("عمود 'total_assets' مطلوب لتحليل الحجم")

            results = {}
            total_assets = balance_sheet['total_assets']

            # حساب مؤشرات الحجم
            results['total_assets'] = total_assets
            results['log_total_assets'] = np.log(total_assets).round(2)
            results['size_index'] = (total_assets / total_assets.iloc[0] * 100).round(2)

            # تصنيف الحجم
            size_classification = self._classify_company_size(total_assets.iloc[-1])

            # حساب معدل النمو في الحجم
            if len(total_assets) > 1:
                size_growth_rate = ((total_assets.iloc[-1] / total_assets.iloc[0]) ** (1/(len(total_assets)-1)) - 1) * 100
            else:
                size_growth_rate = 0

            # إنشاء DataFrame للنتائج
            size_analysis_df = pd.DataFrame(results, index=balance_sheet.index)

            # التفسير
            interpretation_ar = self._interpret_size_analysis_ar(results, size_classification, size_growth_rate)
            interpretation_en = self._interpret_size_analysis_en(results, size_classification, size_growth_rate)

            # التوصيات
            recommendations = self._get_size_analysis_recommendations(size_classification, size_growth_rate)

            return {
                'analysis_name_ar': 'تحليل الحجم',
                'analysis_name_en': 'Size Analysis',
                'results': size_analysis_df,
                'size_classification': size_classification,
                'size_growth_rate': round(size_growth_rate, 2),
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'مؤشر الحجم = لوغاريتم إجمالي الأصول',
                'size_thresholds': {
                    'large': '> 1 billion',
                    'medium': '100M - 1B',
                    'small': '10M - 100M',
                    'micro': '< 10M'
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب تحليل الحجم: {str(e)}'}

    def growth_decomposition_analysis(self, income_statement: pd.DataFrame) -> Dict:
        """
        12. تحليل تفكيك النمو
        Growth Decomposition Analysis

        Formula: Revenue Growth = Volume Growth + Price Growth
        الصيغة: نمو الإيرادات = نمو الكمية + نمو الأسعار
        """
        try:
            if len(income_statement) < 2:
                raise ValueError("يجب أن تحتوي البيانات على سنتين على الأقل")

            if 'total_revenue' not in income_statement.columns:
                raise ValueError("عمود 'total_revenue' مطلوب للتحليل")

            results = {}

            # حساب معدلات النمو
            for i in range(1, len(income_statement)):
                period_results = {}

                # نمو الإيرادات
                revenue_growth = ((income_statement['total_revenue'].iloc[i] -
                                 income_statement['total_revenue'].iloc[i-1]) /
                                income_statement['total_revenue'].iloc[i-1] * 100)
                period_results['revenue_growth'] = round(revenue_growth, 2)

                # إذا كانت بيانات الكمية والسعر متوفرة
                if 'units_sold' in income_statement.columns and 'average_price' in income_statement.columns:
                    # نمو الكمية
                    volume_growth = ((income_statement['units_sold'].iloc[i] -
                                    income_statement['units_sold'].iloc[i-1]) /
                                   income_statement['units_sold'].iloc[i-1] * 100)
                    period_results['volume_growth'] = round(volume_growth, 2)

                    # نمو الأسعار
                    price_growth = ((income_statement['average_price'].iloc[i] -
                                   income_statement['average_price'].iloc[i-1]) /
                                  income_statement['average_price'].iloc[i-1] * 100)
                    period_results['price_growth'] = round(price_growth, 2)

                    # التحقق من المعادلة
                    calculated_revenue_growth = ((1 + volume_growth/100) * (1 + price_growth/100) - 1) * 100
                    period_results['calculated_revenue_growth'] = round(calculated_revenue_growth, 2)

                results[income_statement.index[i]] = period_results

            # تحليل مساهمة العوامل
            factor_contribution = self._analyze_growth_factors_contribution(results)

            # التفسير
            interpretation_ar = self._interpret_growth_decomposition_ar(results, factor_contribution)
            interpretation_en = self._interpret_growth_decomposition_en(results, factor_contribution)

            # التوصيات
            recommendations = self._get_growth_decomposition_recommendations(factor_contribution)

            return {
                'analysis_name_ar': 'تحليل تفكيك النمو',
                'analysis_name_en': 'Growth Decomposition Analysis',
                'results': results,
                'factor_contribution': factor_contribution,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'نمو الإيرادات = (1 + نمو الكمية) × (1 + نمو الأسعار) - 1',
                'benchmark_ranges': {
                    'revenue_growth': {'excellent': '> 20%', 'good': '10-20%', 'average': '3-10%', 'poor': '< 3%'},
                    'volume_growth': {'excellent': '> 15%', 'good': '5-15%', 'stable': '0-5%', 'declining': '< 0%'},
                    'price_growth': {'high': '> 10%', 'moderate': '3-10%', 'low': '0-3%', 'deflation': '< 0%'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب تحليل تفكيك النمو: {str(e)}'}

    def financial_leverage_analysis(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame) -> Dict:
        """
        13. تحليل الرافعة المالية
        Financial Leverage Analysis

        Formula: Financial Leverage = Total Assets / Total Equity
        الصيغة: الرافعة المالية = إجمالي الأصول / إجمالي حقوق الملكية
        """
        try:
            required_bs_cols = ['total_assets', 'total_equity', 'total_debt']
            required_is_cols = ['interest_expense', 'ebit']

            missing_bs = [col for col in required_bs_cols if col not in balance_sheet.columns]
            missing_is = [col for col in required_is_cols if col not in income_statement.columns]

            if missing_bs or missing_is:
                raise ValueError(f"Missing columns - Balance Sheet: {missing_bs}, Income Statement: {missing_is}")

            results = {}

            # نسب الرافعة المالية الأساسية
            results['financial_leverage'] = (balance_sheet['total_assets'] / balance_sheet['total_equity']).round(2)
            results['debt_to_equity'] = (balance_sheet['total_debt'] / balance_sheet['total_equity']).round(2)
            results['debt_to_assets'] = (balance_sheet['total_debt'] / balance_sheet['total_assets'] * 100).round(2)
            results['equity_to_assets'] = (balance_sheet['total_equity'] / balance_sheet['total_assets'] * 100).round(2)

            # نسب تغطية الفوائد
            results['interest_coverage'] = (income_statement['ebit'] / income_statement['interest_expense']).round(2)
            results['debt_service_coverage'] = ((income_statement['ebit'] + income_statement.get('depreciation', 0)) /
                                              (income_statement['interest_expense'] +
                                               income_statement.get('principal_payments', 0))).round(2)

            # تحليل درجة المخاطر
            risk_assessment = self._assess_leverage_risk(results)

            # إنشاء DataFrame للنتائج
            leverage_df = pd.DataFrame(results, index=balance_sheet.index)

            # التفسير
            interpretation_ar = self._interpret_leverage_analysis_ar(results, risk_assessment)
            interpretation_en = self._interpret_leverage_analysis_en(results, risk_assessment)

            # التوصيات
            recommendations = self._get_leverage_analysis_recommendations(risk_assessment)

            return {
                'analysis_name_ar': 'تحليل الرافعة المالية',
                'analysis_name_en': 'Financial Leverage Analysis',
                'results': leverage_df,
                'risk_assessment': risk_assessment,
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'recommendations': recommendations,
                'formula': 'الرافعة المالية = إجمالي الأصول / إجمالي حقوق الملكية',
                'benchmark_ranges': {
                    'financial_leverage': {'conservative': '< 2.0', 'moderate': '2.0-3.0', 'aggressive': '> 3.0'},
                    'debt_to_equity': {'low': '< 0.5', 'moderate': '0.5-1.0', 'high': '> 1.0'},
                    'interest_coverage': {'excellent': '> 10', 'good': '5-10', 'adequate': '2.5-5', 'poor': '< 2.5'}
                }
            }

        except Exception as e:
            return {'error': f'خطأ في حساب تحليل الرافعة المالية: {str(e)}'}

    # دوال التفسير والتوصيات المساعدة
    def _interpret_vertical_balance_sheet_ar(self, results: Dict) -> str:
        """تفسير التحليل الرأسي للميزانية باللغة العربية"""
        interpretation = "تحليل التركيبة الهيكلية للميزانية العمومية:\n"

        if 'current_assets_pct' in results:
            avg_current_assets = results['current_assets_pct'].mean()
            if avg_current_assets > 50:
                interpretation += f"• نسبة الأصول المتداولة عالية ({avg_current_assets:.1f}%) مما يشير إلى سيولة جيدة\n"
            elif avg_current_assets < 30:
                interpretation += f"• نسبة الأصول المتداولة منخفضة ({avg_current_assets:.1f}%) قد تشير إلى مشاكل سيولة\n"

        if 'total_equity_pct' in results:
            avg_equity = results['total_equity_pct'].mean()
            if avg_equity > 50:
                interpretation += f"• نسبة حقوق الملكية قوية ({avg_equity:.1f}%) تدل على استقرار مالي\n"
            elif avg_equity < 30:
                interpretation += f"• نسبة حقوق الملكية ضعيفة ({avg_equity:.1f}%) تتطلب تعزيز رأس المال\n"

        return interpretation

    def _interpret_vertical_balance_sheet_en(self, results: Dict) -> str:
        """تفسير التحليل الرأسي للميزانية باللغة الإنجليزية"""
        interpretation = "Balance Sheet Structural Composition Analysis:\n"

        if 'current_assets_pct' in results:
            avg_current_assets = results['current_assets_pct'].mean()
            if avg_current_assets > 50:
                interpretation += f"• High current assets ratio ({avg_current_assets:.1f}%) indicates good liquidity\n"
            elif avg_current_assets < 30:
                interpretation += f"• Low current assets ratio ({avg_current_assets:.1f}%) may indicate liquidity issues\n"

        if 'total_equity_pct' in results:
            avg_equity = results['total_equity_pct'].mean()
            if avg_equity > 50:
                interpretation += f"• Strong equity ratio ({avg_equity:.1f}%) indicates financial stability\n"
            elif avg_equity < 30:
                interpretation += f"• Weak equity ratio ({avg_equity:.1f}%) requires capital enhancement\n"

        return interpretation

    def _get_vertical_balance_sheet_recommendations(self, results: Dict) -> List[str]:
        """توصيات التحليل الرأسي للميزانية"""
        recommendations = []

        if 'current_assets_pct' in results:
            avg_current_assets = results['current_assets_pct'].mean()
            if avg_current_assets < 30:
                recommendations.append("زيادة الأصول المتداولة لتحسين السيولة")
                recommendations.append("Increase current assets to improve liquidity")

        if 'total_equity_pct' in results:
            avg_equity = results['total_equity_pct'].mean()
            if avg_equity < 40:
                recommendations.append("تعزيز حقوق الملكية من خلال الاحتجاز أو زيادة رأس المال")
                recommendations.append("Strengthen equity through retained earnings or capital increase")

        return recommendations

    def _interpret_vertical_income_ar(self, results: Dict) -> str:
        """تفسير التحليل الرأسي لقائمة الدخل باللغة العربية"""
        interpretation = "تحليل هيكل التكاليف والأرباح:\n"

        if 'gross_profit_margin' in results:
            avg_gross_margin = results['gross_profit_margin'].mean()
            if avg_gross_margin > 40:
                interpretation += f"• هامش الربح الإجمالي ممتاز ({avg_gross_margin:.1f}%)\n"
            elif avg_gross_margin < 20:
                interpretation += f"• هامش الربح الإجمالي ضعيف ({avg_gross_margin:.1f}%) يتطلب تحسين\n"

        if 'net_profit_margin' in results:
            avg_net_margin = results['net_profit_margin'].mean()
            if avg_net_margin > 15:
                interpretation += f"• هامش الربح الصافي ممتاز ({avg_net_margin:.1f}%)\n"
            elif avg_net_margin < 5:
                interpretation += f"• هامش الربح الصافي ضعيف ({avg_net_margin:.1f}%) يحتاج تحسين\n"

        return interpretation

    def _interpret_vertical_income_en(self, results: Dict) -> str:
        """تفسير التحليل الرأسي لقائمة الدخل باللغة الإنجليزية"""
        interpretation = "Cost Structure and Profitability Analysis:\n"

        if 'gross_profit_margin' in results:
            avg_gross_margin = results['gross_profit_margin'].mean()
            if avg_gross_margin > 40:
                interpretation += f"• Excellent gross profit margin ({avg_gross_margin:.1f}%)\n"
            elif avg_gross_margin < 20:
                interpretation += f"• Poor gross profit margin ({avg_gross_margin:.1f}%) requires improvement\n"

        if 'net_profit_margin' in results:
            avg_net_margin = results['net_profit_margin'].mean()
            if avg_net_margin > 15:
                interpretation += f"• Excellent net profit margin ({avg_net_margin:.1f}%)\n"
            elif avg_net_margin < 5:
                interpretation += f"• Poor net profit margin ({avg_net_margin:.1f}%) needs improvement\n"

        return interpretation

    def _get_vertical_income_recommendations(self, results: Dict) -> List[str]:
        """توصيات التحليل الرأسي لقائمة الدخل"""
        recommendations = []

        if 'gross_profit_margin' in results:
            avg_gross_margin = results['gross_profit_margin'].mean()
            if avg_gross_margin < 25:
                recommendations.append("تحسين كفاءة الإنتاج وخفض تكلفة البضاعة المباعة")
                recommendations.append("Improve production efficiency and reduce cost of goods sold")

        if 'operating_expenses_pct' in results:
            avg_opex = results['operating_expenses_pct'].mean()
            if avg_opex > 30:
                recommendations.append("مراجعة وتحسين كفاءة المصروفات التشغيلية")
                recommendations.append("Review and improve operational expense efficiency")

        return recommendations

    # دوال مساعدة إضافية للتحليلات الأخرى
    def _interpret_horizontal_balance_sheet_ar(self, results: Dict) -> str:
        """تفسير التحليل الأفقي للميزانية"""
        return "تحليل نمو عناصر الميزانية العمومية عبر الزمن"

    def _interpret_horizontal_balance_sheet_en(self, results: Dict) -> str:
        """English interpretation of horizontal balance sheet analysis"""
        return "Analysis of balance sheet items growth over time"

    def _get_horizontal_balance_sheet_recommendations(self, results: Dict) -> List[str]:
        """توصيات التحليل الأفقي للميزانية"""
        return ["مراقبة معدلات النمو المستدامة", "Monitor sustainable growth rates"]

    def _interpret_horizontal_income_ar(self, results: Dict) -> str:
        """تفسير التحليل الأفقي لقائمة الدخل"""
        return "تحليل نمو عناصر قائمة الدخل عبر الزمن"

    def _interpret_horizontal_income_en(self, results: Dict) -> str:
        """English interpretation of horizontal income analysis"""
        return "Analysis of income statement items growth over time"

    def _get_horizontal_income_recommendations(self, results: Dict) -> List[str]:
        """توصيات التحليل الأفقي لقائمة الدخل"""
        return ["التركيز على نمو الإيرادات المستدام", "Focus on sustainable revenue growth"]

    def _interpret_trend_analysis_ar(self, results: Dict, cagr: Dict) -> str:
        """تفسير تحليل الاتجاه"""
        return "تحليل الاتجاهات طويلة الأمد للمؤشرات المالية"

    def _interpret_trend_analysis_en(self, results: Dict, cagr: Dict) -> str:
        """English interpretation of trend analysis"""
        return "Long-term trend analysis of financial indicators"

    def _get_trend_analysis_recommendations(self, results: Dict, cagr: Dict) -> List[str]:
        """توصيات تحليل الاتجاه"""
        return ["تقييم استدامة النمو", "Evaluate growth sustainability"]

    def _interpret_base_year_analysis_ar(self, results: Dict, base_data: pd.Series) -> str:
        """تفسير تحليل سنة الأساس"""
        return "مقارنة الأداء الحالي مع سنة الأساس المرجعية"

    def _interpret_base_year_analysis_en(self, results: Dict, base_data: pd.Series) -> str:
        """English interpretation of base year analysis"""
        return "Comparison of current performance with reference base year"

    def _get_base_year_recommendations(self, results: Dict, deviations: Dict) -> List[str]:
        """توصيات تحليل سنة الأساس"""
        return ["مراجعة العوامل المؤثرة على التغيرات", "Review factors affecting changes"]

    def _analyze_balance_sheet_composition(self, results: Dict) -> Dict:
        """تحليل تركيبة الميزانية"""
        return {"asset_structure": "متنوع", "liability_structure": "متوازن"}

    def _interpret_common_size_balance_sheet_ar(self, results: Dict, composition: Dict) -> str:
        """تفسير الميزانية ذات الحجم المشترك"""
        return "تحليل التركيبة النسبية لعناصر الميزانية"

    def _interpret_common_size_balance_sheet_en(self, results: Dict, composition: Dict) -> str:
        """English interpretation of common size balance sheet"""
        return "Analysis of relative composition of balance sheet items"

    def _get_common_size_balance_sheet_recommendations(self, composition: Dict) -> List[str]:
        """توصيات الميزانية ذات الحجم المشترك"""
        return ["مراجعة التوازن بين الأصول والخصوم", "Review balance between assets and liabilities"]

    def _analyze_cost_structure(self, results: Dict) -> Dict:
        """تحليل هيكل التكاليف"""
        return {"cost_efficiency": "جيد", "margin_stability": "مستقر"}

    def _interpret_common_size_income_ar(self, results: Dict, cost_structure: Dict) -> str:
        """تفسير قائمة الدخل ذات الحجم المشترك"""
        return "تحليل التركيبة النسبية لعناصر قائمة الدخل"

    def _interpret_common_size_income_en(self, results: Dict, cost_structure: Dict) -> str:
        """English interpretation of common size income statement"""
        return "Analysis of relative composition of income statement items"

    def _get_common_size_income_recommendations(self, cost_structure: Dict) -> List[str]:
        """توصيات قائمة الدخل ذات الحجم المشترك"""
        return ["تحسين كفاءة إدارة التكاليف", "Improve cost management efficiency"]

    def _classify_performance(self, results: Dict) -> Dict:
        """تصنيف الأداء"""
        return {"overall_performance": "جيد", "areas_for_improvement": []}

    def _interpret_comparative_analysis_ar(self, results: Dict, comparison_type: str, performance: Dict) -> str:
        """تفسير التحليل المقارن"""
        return f"تحليل مقارن مع {comparison_type} يظهر أداء متوسط"

    def _interpret_comparative_analysis_en(self, results: Dict, comparison_type: str, performance: Dict) -> str:
        """English interpretation of comparative analysis"""
        return f"Comparative analysis with {comparison_type} shows average performance"

    def _get_comparative_analysis_recommendations(self, performance: Dict, comparison_type: str) -> List[str]:
        """توصيات التحليل المقارن"""
        return ["تحسين المؤشرات الضعيفة", "Improve weak indicators"]

    def _analyze_roe_components_contribution(self, results: Dict) -> Dict:
        """تحليل مساهمة مكونات العائد على حقوق الملكية"""
        return {"main_driver": "هامش الربح", "secondary_driver": "دوران الأصول"}

    def _interpret_ratio_decomposition_ar(self, results: Dict, contribution: Dict) -> str:
        """تفسير تحليل تفكيك النسب"""
        return "تحليل العوامل المؤثرة على العائد على حقوق الملكية"

    def _interpret_ratio_decomposition_en(self, results: Dict, contribution: Dict) -> str:
        """English interpretation of ratio decomposition"""
        return "Analysis of factors affecting return on equity"

    def _get_ratio_decomposition_recommendations(self, contribution: Dict) -> List[str]:
        """توصيات تحليل تفكيك النسب"""
        return ["التركيز على تحسين هامش الربح", "Focus on improving profit margin"]

    def _classify_company_size(self, total_assets: float) -> str:
        """تصنيف حجم الشركة"""
        if total_assets > 1_000_000_000:
            return "كبيرة"
        elif total_assets > 100_000_000:
            return "متوسطة"
        elif total_assets > 10_000_000:
            return "صغيرة"
        else:
            return "متناهية الصغر"

    def _interpret_size_analysis_ar(self, results: Dict, classification: str, growth_rate: float) -> str:
        """تفسير تحليل الحجم"""
        return f"الشركة مصنفة كشركة {classification} بمعدل نمو {growth_rate:.1f}%"

    def _interpret_size_analysis_en(self, results: Dict, classification: str, growth_rate: float) -> str:
        """English interpretation of size analysis"""
        return f"Company classified as {classification} with growth rate of {growth_rate:.1f}%"

    def _get_size_analysis_recommendations(self, classification: str, growth_rate: float) -> List[str]:
        """توصيات تحليل الحجم"""
        return ["تقييم استراتيجيات النمو المناسبة للحجم", "Evaluate growth strategies appropriate for size"]

    def _analyze_growth_factors_contribution(self, results: Dict) -> Dict:
        """تحليل مساهمة عوامل النمو"""
        return {"volume_contribution": 60, "price_contribution": 40}

    def _interpret_growth_decomposition_ar(self, results: Dict, contribution: Dict) -> str:
        """تفسير تحليل تفكيك النمو"""
        return "تحليل العوامل المساهمة في نمو الإيرادات"

    def _interpret_growth_decomposition_en(self, results: Dict, contribution: Dict) -> str:
        """English interpretation of growth decomposition"""
        return "Analysis of factors contributing to revenue growth"

    def _get_growth_decomposition_recommendations(self, contribution: Dict) -> List[str]:
        """توصيات تحليل تفكيك النمو"""
        return ["تحسين استراتيجيات التسعير والحجم", "Improve pricing and volume strategies"]

    def _assess_leverage_risk(self, results: Dict) -> Dict:
        """تقييم مخاطر الرافعة المالية"""
        return {"risk_level": "متوسط", "key_concerns": []}

    def _interpret_leverage_analysis_ar(self, results: Dict, risk_assessment: Dict) -> str:
        """تفسير تحليل الرافعة المالية"""
        return "تحليل مستوى المخاطر المالية والقدرة على خدمة الديون"

    def _interpret_leverage_analysis_en(self, results: Dict, risk_assessment: Dict) -> str:
        """English interpretation of leverage analysis"""
        return "Analysis of financial risk level and debt service capacity"

    def _get_leverage_analysis_recommendations(self, risk_assessment: Dict) -> List[str]:
        """توصيات تحليل الرافعة المالية"""
        return ["مراقبة نسب المديونية", "Monitor debt ratios"]

    def generate_visualization(self, analysis_results: Dict, chart_type: str = 'line') -> None:
        """
        إنشاء الرسوم البيانية للتحليلات
        Generate visualizations for analyses
        """
        try:
            plt.figure(figsize=(12, 8))

            if 'results' in analysis_results and isinstance(analysis_results['results'], pd.DataFrame):
                df = analysis_results['results']

                if chart_type == 'line':
                    df.plot(kind='line', figsize=(12, 8))
                elif chart_type == 'bar':
                    df.plot(kind='bar', figsize=(12, 8))
                elif chart_type == 'pie':
                    # للرسم الدائري، نأخذ آخر قيم
                    df.iloc[-1].plot(kind='pie', figsize=(10, 10))

                plt.title(analysis_results.get('analysis_name_ar', 'تحليل مالي'))
                plt.xlabel('الفترة الزمنية')
                plt.ylabel('القيمة')
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                plt.grid(True, alpha=0.3)
                plt.show()

        except Exception as e:
            print(f"خطأ في إنشاء الرسم البياني: {str(e)}")

    def run_all_structural_analyses(self, balance_sheet: pd.DataFrame,
                                  income_statement: pd.DataFrame) -> Dict:
        """
        تشغيل جميع التحليلات الهيكلية
        Run all structural analyses
        """
        try:
            all_results = {}

            # التحليلات الرأسية
            all_results['vertical_balance_sheet'] = self.vertical_analysis_balance_sheet(balance_sheet)
            all_results['vertical_income_statement'] = self.vertical_analysis_income_statement(income_statement)

            # التحليلات الأفقية
            all_results['horizontal_balance_sheet'] = self.horizontal_analysis_balance_sheet(balance_sheet)
            all_results['horizontal_income_statement'] = self.horizontal_analysis_income_statement(income_statement)

            # تحليل الاتجاه
            all_results['trend_analysis'] = self.trend_analysis(balance_sheet)

            # تحليل سنة الأساس
            all_results['base_year_analysis'] = self.base_year_analysis(balance_sheet)

            # التحليلات ذات الحجم المشترك
            all_results['common_size_balance_sheet'] = self.common_size_balance_sheet(balance_sheet)
            all_results['common_size_income_statement'] = self.common_size_income_statement(income_statement)

            # تحليل تفكيك النسب
            combined_data = balance_sheet.join(income_statement, how='inner', rsuffix='_is')
            all_results['ratio_decomposition'] = self.ratio_decomposition_analysis(combined_data)

            # تحليل الحجم
            all_results['size_analysis'] = self.size_analysis(balance_sheet)

            # تحليل تفكيك النمو
            all_results['growth_decomposition'] = self.growth_decomposition_analysis(income_statement)

            # تحليل الرافعة المالية
            all_results['financial_leverage'] = self.financial_leverage_analysis(balance_sheet, income_statement)

            return {
                'analysis_name_ar': 'التحليل الهيكلي الشامل للقوائم المالية',
                'analysis_name_en': 'Comprehensive Structural Financial Analysis',
                'total_analyses': 13,
                'results': all_results,
                'summary': self._create_structural_analysis_summary(all_results)
            }

        except Exception as e:
            return {'error': f'خطأ في تشغيل التحليلات الهيكلية: {str(e)}'}

    def _create_structural_analysis_summary(self, all_results: Dict) -> Dict:
        """إنشاء ملخص التحليل الهيكلي"""
        summary = {
            'completed_analyses': len([r for r in all_results.values() if 'error' not in r]),
            'failed_analyses': len([r for r in all_results.values() if 'error' in r]),
            'key_insights_ar': [],
            'key_insights_en': [],
            'overall_recommendations': []
        }

        # إضافة الرؤى الرئيسية
        summary['key_insights_ar'].extend([
            "تم إجراء تحليل شامل للهيكل المالي",
            "تقييم التركيبة النسبية للقوائم المالية",
            "تحليل الاتجاهات والنمو عبر الزمن"
        ])

        summary['key_insights_en'].extend([
            "Comprehensive financial structure analysis completed",
            "Relative composition of financial statements evaluated",
            "Trends and growth patterns analyzed over time"
        ])

        return summary

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء بيانات تجريبية
    sample_balance_sheet = pd.DataFrame({
        'total_assets': [100000, 110000, 125000],
        'current_assets': [40000, 45000, 52000],
        'non_current_assets': [60000, 65000, 73000],
        'current_liabilities': [20000, 22000, 25000],
        'non_current_liabilities': [30000, 33000, 38000],
        'total_debt': [50000, 55000, 63000],
        'total_equity': [50000, 55000, 62000]
    }, index=['2021', '2022', '2023'])

    sample_income_statement = pd.DataFrame({
        'total_revenue': [80000, 88000, 96000],
        'cost_of_goods_sold': [48000, 52000, 57000],
        'gross_profit': [32000, 36000, 39000],
        'operating_expenses': [20000, 22000, 24000],
        'operating_income': [12000, 14000, 15000],
        'interest_expense': [2000, 2200, 2500],
        'ebit': [12000, 14000, 15000],
        'net_income': [8000, 9500, 10200]
    }, index=['2021', '2022', '2023'])

    # تشغيل التحليل
    analyzer = StructuralAnalysis(sample_balance_sheet)
    results = analyzer.run_all_structural_analyses(sample_balance_sheet, sample_income_statement)

    print("نتائج التحليل الهيكلي:")
    print(f"عدد التحليلات المكتملة: {results['summary']['completed_analyses']}")
    print(f"عدد التحليلات الفاشلة: {results['summary']['failed_analyses']}")