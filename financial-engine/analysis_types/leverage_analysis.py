"""
تحاليل الرافعة المالية - Financial Leverage Analysis
15 تحليل أساسي للرافعة المالية وهيكل رأس المال
"""

import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
import math

class LeverageAnalysis:
    """فئة تحاليل الرافعة المالية"""

    def __init__(self):
        self.analysis_name = "تحاليل الرافعة المالية"
        self.analysis_name_en = "Financial Leverage Analysis"
        self.category = "الرافعة المالية"
        self.category_en = "Financial Leverage"

    def debt_to_equity_ratio(self, total_debt: float, shareholders_equity: float) -> Dict[str, Any]:
        """
        1. نسبة الدين إلى حقوق الملكية
        Debt to Equity Ratio = Total Debt / Shareholders' Equity
        """
        try:
            if shareholders_equity == 0:
                return {
                    'value': None,
                    'formula': 'إجمالي الدين ÷ حقوق الملكية',
                    'formula_en': 'Total Debt ÷ Shareholders\' Equity',
                    'interpretation_ar': 'لا يمكن حساب النسبة - حقوق الملكية تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - shareholders\' equity equals zero'
                }

            ratio = total_debt / shareholders_equity

            # تفسير النتائج
            if ratio <= 0.3:
                interpretation_ar = 'رافعة مالية منخفضة - محافظة جداً ومستقرة'
                interpretation_en = 'Low financial leverage - very conservative and stable'
                leverage_level = 'منخفضة'
                risk_level = 'منخفض'
                financial_stability = 'عالية جداً'
                growth_potential = 'محدود'
            elif ratio <= 0.6:
                interpretation_ar = 'رافعة مالية معتدلة - توازن جيد بين المخاطر والعوائد'
                interpretation_en = 'Moderate financial leverage - good balance between risk and returns'
                leverage_level = 'معتدلة'
                risk_level = 'منخفض'
                financial_stability = 'عالية'
                growth_potential = 'جيد'
            elif ratio <= 1.0:
                interpretation_ar = 'رافعة مالية مقبولة - مخاطر معتدلة'
                interpretation_en = 'Acceptable financial leverage - moderate risks'
                leverage_level = 'مقبولة'
                risk_level = 'متوسط'
                financial_stability = 'متوسطة'
                growth_potential = 'جيد'
            elif ratio <= 2.0:
                interpretation_ar = 'رافعة مالية عالية - مخاطر مرتفعة'
                interpretation_en = 'High financial leverage - elevated risks'
                leverage_level = 'عالية'
                risk_level = 'عالي'
                financial_stability = 'منخفضة'
                growth_potential = 'عالي'
            else:
                interpretation_ar = 'رافعة مالية عالية جداً - مخاطر مالية خطيرة'
                interpretation_en = 'Very high financial leverage - serious financial risks'
                leverage_level = 'عالية جداً'
                risk_level = 'عالي جداً'
                financial_stability = 'منخفضة جداً'
                growth_potential = 'عالي جداً'

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2%}",
                'total_debt': round(total_debt, 2),
                'shareholders_equity': round(shareholders_equity, 2),
                'formula': 'إجمالي الدين ÷ حقوق الملكية',
                'formula_en': 'Total Debt ÷ Shareholders\' Equity',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'leverage_level': leverage_level,
                'risk_level': risk_level,
                'financial_stability': financial_stability,
                'growth_potential': growth_potential,
                'benchmark': {
                    'conservative': '≤ 0.3',
                    'moderate': '0.31-0.6',
                    'acceptable': '0.61-1.0',
                    'high': '1.01-2.0',
                    'very_high': '> 2.0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة الدين إلى حقوق الملكية: {str(e)}',
                'error_en': f'Error calculating debt to equity ratio: {str(e)}'
            }

    def debt_ratio(self, total_debt: float, total_assets: float) -> Dict[str, Any]:
        """
        2. نسبة الدين
        Debt Ratio = Total Debt / Total Assets
        """
        try:
            if total_assets == 0:
                return {
                    'value': None,
                    'formula': 'إجمالي الدين ÷ إجمالي الأصول',
                    'formula_en': 'Total Debt ÷ Total Assets',
                    'interpretation_ar': 'لا يمكن حساب النسبة - إجمالي الأصول تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - total assets equal zero'
                }

            ratio = total_debt / total_assets

            # تفسير النتائج
            if ratio <= 0.2:
                interpretation_ar = 'نسبة دين منخفضة جداً - تمويل محافظ'
                interpretation_en = 'Very low debt ratio - conservative financing'
                debt_level = 'منخفضة جداً'
                financial_risk = 'منخفض جداً'
                solvency = 'ممتازة'
            elif ratio <= 0.4:
                interpretation_ar = 'نسبة دين منخفضة - تمويل مستقر'
                interpretation_en = 'Low debt ratio - stable financing'
                debt_level = 'منخفضة'
                financial_risk = 'منخفض'
                solvency = 'ممتازة'
            elif ratio <= 0.6:
                interpretation_ar = 'نسبة دين معتدلة - توازن جيد في التمويل'
                interpretation_en = 'Moderate debt ratio - good financing balance'
                debt_level = 'معتدلة'
                financial_risk = 'متوسط'
                solvency = 'جيدة'
            elif ratio <= 0.8:
                interpretation_ar = 'نسبة دين عالية - زيادة في المخاطر المالية'
                interpretation_en = 'High debt ratio - increased financial risks'
                debt_level = 'عالية'
                financial_risk = 'عالي'
                solvency = 'مقبولة'
            else:
                interpretation_ar = 'نسبة دين عالية جداً - مخاطر مالية خطيرة'
                interpretation_en = 'Very high debt ratio - serious financial risks'
                debt_level = 'عالية جداً'
                financial_risk = 'عالي جداً'
                solvency = 'ضعيفة'

            # حساب نسبة حقوق الملكية
            equity_ratio = 1 - ratio

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2%}",
                'equity_ratio': round(equity_ratio, 2),
                'equity_percentage': f"{equity_ratio:.2%}",
                'total_debt': round(total_debt, 2),
                'total_assets': round(total_assets, 2),
                'formula': 'إجمالي الدين ÷ إجمالي الأصول',
                'formula_en': 'Total Debt ÷ Total Assets',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'debt_level': debt_level,
                'financial_risk': financial_risk,
                'solvency': solvency,
                'benchmark': {
                    'very_low': '≤ 20%',
                    'low': '21-40%',
                    'moderate': '41-60%',
                    'high': '61-80%',
                    'very_high': '> 80%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة الدين: {str(e)}',
                'error_en': f'Error calculating debt ratio: {str(e)}'
            }

    def equity_multiplier(self, total_assets: float, shareholders_equity: float) -> Dict[str, Any]:
        """
        3. مضاعف حقوق الملكية
        Equity Multiplier = Total Assets / Shareholders' Equity
        """
        try:
            if shareholders_equity == 0:
                return {
                    'value': None,
                    'formula': 'إجمالي الأصول ÷ حقوق الملكية',
                    'formula_en': 'Total Assets ÷ Shareholders\' Equity',
                    'interpretation_ar': 'لا يمكن حساب المضاعف - حقوق الملكية تساوي صفر',
                    'interpretation_en': 'Cannot calculate multiplier - shareholders\' equity equals zero'
                }

            multiplier = total_assets / shareholders_equity

            # تفسير النتائج
            if multiplier <= 1.5:
                interpretation_ar = 'مضاعف منخفض - تمويل محافظ بحقوق الملكية'
                interpretation_en = 'Low multiplier - conservative equity financing'
                leverage_level = 'منخفضة'
                financial_risk = 'منخفض'
                capital_structure = 'محافظ'
            elif multiplier <= 2.5:
                interpretation_ar = 'مضاعف معتدل - توازن جيد في هيكل رأس المال'
                interpretation_en = 'Moderate multiplier - good capital structure balance'
                leverage_level = 'معتدلة'
                financial_risk = 'متوسط'
                capital_structure = 'متوازن'
            elif multiplier <= 4.0:
                interpretation_ar = 'مضاعف عالي - اعتماد كبير على الديون'
                interpretation_en = 'High multiplier - heavy reliance on debt'
                leverage_level = 'عالية'
                financial_risk = 'عالي'
                capital_structure = 'مُدَان'
            else:
                interpretation_ar = 'مضاعف عالي جداً - مخاطر مالية خطيرة'
                interpretation_en = 'Very high multiplier - serious financial risks'
                leverage_level = 'عالية جداً'
                financial_risk = 'عالي جداً'
                capital_structure = 'خطير'

            # حساب نسبة الرافعة المالية
            financial_leverage = multiplier - 1

            return {
                'value': round(multiplier, 2),
                'financial_leverage': round(financial_leverage, 2),
                'total_assets': round(total_assets, 2),
                'shareholders_equity': round(shareholders_equity, 2),
                'formula': 'إجمالي الأصول ÷ حقوق الملكية',
                'formula_en': 'Total Assets ÷ Shareholders\' Equity',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'leverage_level': leverage_level,
                'financial_risk': financial_risk,
                'capital_structure': capital_structure,
                'benchmark': {
                    'conservative': '≤ 1.5',
                    'moderate': '1.51-2.5',
                    'high': '2.51-4.0',
                    'very_high': '> 4.0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب مضاعف حقوق الملكية: {str(e)}',
                'error_en': f'Error calculating equity multiplier: {str(e)}'
            }

    def times_interest_earned(self, ebit: float, interest_expense: float) -> Dict[str, Any]:
        """
        4. مضاعف تغطية الفوائد
        Times Interest Earned = EBIT / Interest Expense
        """
        try:
            if interest_expense == 0:
                return {
                    'value': None,
                    'formula': 'الأرباح قبل الفوائد والضرائب ÷ مصروفات الفوائد',
                    'formula_en': 'EBIT ÷ Interest Expense',
                    'interpretation_ar': 'لا يمكن حساب المضاعف - مصروفات الفوائد تساوي صفر',
                    'interpretation_en': 'Cannot calculate multiplier - interest expense equals zero'
                }

            times_earned = ebit / interest_expense

            # تفسير النتائج
            if times_earned >= 8:
                interpretation_ar = 'تغطية ممتازة للفوائد - قدرة عالية على خدمة الدين'
                interpretation_en = 'Excellent interest coverage - high debt service capability'
                coverage_quality = 'ممتازة'
                financial_safety = 'عالية جداً'
                default_risk = 'منخفض جداً'
            elif times_earned >= 5:
                interpretation_ar = 'تغطية جيدة للفوائد - قدرة مستقرة على خدمة الدين'
                interpretation_en = 'Good interest coverage - stable debt service capability'
                coverage_quality = 'جيدة'
                financial_safety = 'عالية'
                default_risk = 'منخفض'
            elif times_earned >= 2.5:
                interpretation_ar = 'تغطية مقبولة للفوائد - قدرة معتدلة على خدمة الدين'
                interpretation_en = 'Acceptable interest coverage - moderate debt service capability'
                coverage_quality = 'مقبولة'
                financial_safety = 'متوسطة'
                default_risk = 'متوسط'
            elif times_earned >= 1.5:
                interpretation_ar = 'تغطية ضعيفة للفوائد - مخاطر في خدمة الدين'
                interpretation_en = 'Poor interest coverage - debt service risks'
                coverage_quality = 'ضعيفة'
                financial_safety = 'منخفضة'
                default_risk = 'عالي'
            else:
                interpretation_ar = 'تغطية ضعيفة جداً للفوائد - مخاطر تعثر عالية'
                interpretation_en = 'Very poor interest coverage - high default risks'
                coverage_quality = 'ضعيفة جداً'
                financial_safety = 'منخفضة جداً'
                default_risk = 'عالي جداً'

            # حساب هامش الأمان
            safety_margin = times_earned - 1

            return {
                'value': round(times_earned, 2),
                'safety_margin': round(safety_margin, 2),
                'ebit': round(ebit, 2),
                'interest_expense': round(interest_expense, 2),
                'formula': 'الأرباح قبل الفوائد والضرائب ÷ مصروفات الفوائد',
                'formula_en': 'EBIT ÷ Interest Expense',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'coverage_quality': coverage_quality,
                'financial_safety': financial_safety,
                'default_risk': default_risk,
                'benchmark': {
                    'excellent': '≥ 8',
                    'good': '5-7.99',
                    'acceptable': '2.5-4.99',
                    'poor': '1.5-2.49',
                    'very_poor': '< 1.5'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب مضاعف تغطية الفوائد: {str(e)}',
                'error_en': f'Error calculating times interest earned: {str(e)}'
            }

    def debt_service_coverage_ratio(self, ebitda: float, debt_service: float) -> Dict[str, Any]:
        """
        5. نسبة تغطية خدمة الدين
        Debt Service Coverage Ratio = EBITDA / Debt Service
        """
        try:
            if debt_service == 0:
                return {
                    'value': None,
                    'formula': 'الأرباح قبل الفوائد والضرائب والإهلاك ÷ خدمة الدين',
                    'formula_en': 'EBITDA ÷ Debt Service',
                    'interpretation_ar': 'لا يمكن حساب النسبة - خدمة الدين تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - debt service equals zero'
                }

            dscr = ebitda / debt_service

            # تفسير النتائج
            if dscr >= 2.0:
                interpretation_ar = 'تغطية ممتازة لخدمة الدين - قدرة عالية على الوفاء بالالتزامات'
                interpretation_en = 'Excellent debt service coverage - high ability to meet obligations'
                coverage_quality = 'ممتازة'
                creditworthiness = 'عالية جداً'
                refinancing_ability = 'ممتازة'
                default_risk = 'منخفض جداً'
            elif dscr >= 1.5:
                interpretation_ar = 'تغطية جيدة لخدمة الدين - قدرة مستقرة على الوفاء'
                interpretation_en = 'Good debt service coverage - stable ability to meet obligations'
                coverage_quality = 'جيدة'
                creditworthiness = 'عالية'
                refinancing_ability = 'جيدة'
                default_risk = 'منخفض'
            elif dscr >= 1.2:
                interpretation_ar = 'تغطية مقبولة لخدمة الدين - قدرة معتدلة على الوفاء'
                interpretation_en = 'Acceptable debt service coverage - moderate ability to meet obligations'
                coverage_quality = 'مقبولة'
                creditworthiness = 'متوسطة'
                refinancing_ability = 'مقبولة'
                default_risk = 'متوسط'
            elif dscr >= 1.0:
                interpretation_ar = 'تغطية ضعيفة لخدمة الدين - قدرة محدودة على الوفاء'
                interpretation_en = 'Poor debt service coverage - limited ability to meet obligations'
                coverage_quality = 'ضعيفة'
                creditworthiness = 'منخفضة'
                refinancing_ability = 'ضعيفة'
                default_risk = 'عالي'
            else:
                interpretation_ar = 'تغطية غير كافية لخدمة الدين - عجز عن الوفاء بالالتزامات'
                interpretation_en = 'Insufficient debt service coverage - unable to meet obligations'
                coverage_quality = 'غير كافية'
                creditworthiness = 'منخفضة جداً'
                refinancing_ability = 'ضعيفة جداً'
                default_risk = 'عالي جداً'

            return {
                'value': round(dscr, 2),
                'ebitda': round(ebitda, 2),
                'debt_service': round(debt_service, 2),
                'formula': 'الأرباح قبل الفوائد والضرائب والإهلاك ÷ خدمة الدين',
                'formula_en': 'EBITDA ÷ Debt Service',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'coverage_quality': coverage_quality,
                'creditworthiness': creditworthiness,
                'refinancing_ability': refinancing_ability,
                'default_risk': default_risk,
                'benchmark': {
                    'excellent': '≥ 2.0',
                    'good': '1.5-1.99',
                    'acceptable': '1.2-1.49',
                    'poor': '1.0-1.19',
                    'insufficient': '< 1.0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة تغطية خدمة الدين: {str(e)}',
                'error_en': f'Error calculating debt service coverage ratio: {str(e)}'
            }

    def long_term_debt_to_equity(self, long_term_debt: float, shareholders_equity: float) -> Dict[str, Any]:
        """
        6. نسبة الدين طويل الأجل إلى حقوق الملكية
        Long-term Debt to Equity = Long-term Debt / Shareholders' Equity
        """
        try:
            if shareholders_equity == 0:
                return {
                    'value': None,
                    'formula': 'الدين طويل الأجل ÷ حقوق الملكية',
                    'formula_en': 'Long-term Debt ÷ Shareholders\' Equity',
                    'interpretation_ar': 'لا يمكن حساب النسبة - حقوق الملكية تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - shareholders\' equity equals zero'
                }

            ratio = long_term_debt / shareholders_equity

            # تفسير النتائج
            if ratio <= 0.2:
                interpretation_ar = 'نسبة دين طويل أجل منخفضة - هيكل رأس مال محافظ'
                interpretation_en = 'Low long-term debt ratio - conservative capital structure'
                debt_structure = 'محافظ'
                financial_flexibility = 'عالية جداً'
                long_term_risk = 'منخفض'
            elif ratio <= 0.5:
                interpretation_ar = 'نسبة دين طويل أجل معتدلة - هيكل رأس مال متوازن'
                interpretation_en = 'Moderate long-term debt ratio - balanced capital structure'
                debt_structure = 'متوازن'
                financial_flexibility = 'جيدة'
                long_term_risk = 'منخفض'
            elif ratio <= 1.0:
                interpretation_ar = 'نسبة دين طويل أجل مقبولة - زيادة طفيفة في المخاطر'
                interpretation_en = 'Acceptable long-term debt ratio - slight increase in risks'
                debt_structure = 'مقبول'
                financial_flexibility = 'متوسطة'
                long_term_risk = 'متوسط'
            elif ratio <= 2.0:
                interpretation_ar = 'نسبة دين طويل أجل عالية - مخاطر مالية مرتفعة'
                interpretation_en = 'High long-term debt ratio - elevated financial risks'
                debt_structure = 'مُدَان'
                financial_flexibility = 'منخفضة'
                long_term_risk = 'عالي'
            else:
                interpretation_ar = 'نسبة دين طويل أجل عالية جداً - مخاطر مالية خطيرة'
                interpretation_en = 'Very high long-term debt ratio - serious financial risks'
                debt_structure = 'خطير'
                financial_flexibility = 'منخفضة جداً'
                long_term_risk = 'عالي جداً'

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2%}",
                'long_term_debt': round(long_term_debt, 2),
                'shareholders_equity': round(shareholders_equity, 2),
                'formula': 'الدين طويل الأجل ÷ حقوق الملكية',
                'formula_en': 'Long-term Debt ÷ Shareholders\' Equity',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'debt_structure': debt_structure,
                'financial_flexibility': financial_flexibility,
                'long_term_risk': long_term_risk,
                'benchmark': {
                    'conservative': '≤ 0.2',
                    'balanced': '0.21-0.5',
                    'acceptable': '0.51-1.0',
                    'high': '1.01-2.0',
                    'very_high': '> 2.0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة الدين طويل الأجل إلى حقوق الملكية: {str(e)}',
                'error_en': f'Error calculating long-term debt to equity: {str(e)}'
            }

    def capitalization_ratio(self, long_term_debt: float, total_capitalization: float) -> Dict[str, Any]:
        """
        7. نسبة الرسملة
        Capitalization Ratio = Long-term Debt / (Long-term Debt + Shareholders' Equity)
        """
        try:
            if total_capitalization == 0:
                return {
                    'value': None,
                    'formula': 'الدين طويل الأجل ÷ (الدين طويل الأجل + حقوق الملكية)',
                    'formula_en': 'Long-term Debt ÷ (Long-term Debt + Shareholders\' Equity)',
                    'interpretation_ar': 'لا يمكن حساب النسبة - إجمالي الرسملة تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - total capitalization equals zero'
                }

            ratio = long_term_debt / total_capitalization

            # تفسير النتائج
            if ratio <= 0.2:
                interpretation_ar = 'نسبة رسملة منخفضة - اعتماد أساسي على حقوق الملكية'
                interpretation_en = 'Low capitalization ratio - primary reliance on equity'
                capital_structure = 'محافظ جداً'
                debt_dependency = 'منخفض'
                financial_risk = 'منخفض'
            elif ratio <= 0.4:
                interpretation_ar = 'نسبة رسملة معتدلة - توازن جيد في هيكل رأس المال'
                interpretation_en = 'Moderate capitalization ratio - good capital structure balance'
                capital_structure = 'متوازن'
                debt_dependency = 'معتدل'
                financial_risk = 'منخفض'
            elif ratio <= 0.6:
                interpretation_ar = 'نسبة رسملة مقبولة - اعتماد متزايد على الديون'
                interpretation_en = 'Acceptable capitalization ratio - increasing debt reliance'
                capital_structure = 'مقبول'
                debt_dependency = 'متوسط'
                financial_risk = 'متوسط'
            elif ratio <= 0.8:
                interpretation_ar = 'نسبة رسملة عالية - اعتماد كبير على الديون'
                interpretation_en = 'High capitalization ratio - heavy debt reliance'
                capital_structure = 'مُدَان'
                debt_dependency = 'عالي'
                financial_risk = 'عالي'
            else:
                interpretation_ar = 'نسبة رسملة عالية جداً - اعتماد مفرط على الديون'
                interpretation_en = 'Very high capitalization ratio - excessive debt reliance'
                capital_structure = 'خطير'
                debt_dependency = 'عالي جداً'
                financial_risk = 'عالي جداً'

            # حساب نسبة حقوق الملكية في الرسملة
            equity_ratio = 1 - ratio

            return {
                'value': round(ratio, 2),
                'percentage': f"{ratio:.2%}",
                'equity_ratio': round(equity_ratio, 2),
                'equity_percentage': f"{equity_ratio:.2%}",
                'long_term_debt': round(long_term_debt, 2),
                'total_capitalization': round(total_capitalization, 2),
                'formula': 'الدين طويل الأجل ÷ (الدين طويل الأجل + حقوق الملكية)',
                'formula_en': 'Long-term Debt ÷ (Long-term Debt + Shareholders\' Equity)',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'capital_structure': capital_structure,
                'debt_dependency': debt_dependency,
                'financial_risk': financial_risk,
                'benchmark': {
                    'very_conservative': '≤ 20%',
                    'moderate': '21-40%',
                    'acceptable': '41-60%',
                    'high': '61-80%',
                    'very_high': '> 80%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة الرسملة: {str(e)}',
                'error_en': f'Error calculating capitalization ratio: {str(e)}'
            }

    def financial_leverage_multiplier(self, percentage_change_roe: float, percentage_change_roi: float) -> Dict[str, Any]:
        """
        8. مضاعف الرافعة المالية
        Financial Leverage Multiplier = % Change in ROE / % Change in ROI
        """
        try:
            if percentage_change_roi == 0:
                return {
                    'value': None,
                    'formula': 'النسبة المئوية للتغيير في العائد على حقوق الملكية ÷ النسبة المئوية للتغيير في العائد على الاستثمار',
                    'formula_en': '% Change in ROE ÷ % Change in ROI',
                    'interpretation_ar': 'لا يمكن حساب المضاعف - التغيير في العائد على الاستثمار يساوي صفر',
                    'interpretation_en': 'Cannot calculate multiplier - change in ROI equals zero'
                }

            multiplier = percentage_change_roe / percentage_change_roi

            # تفسير النتائج
            if multiplier >= 3:
                interpretation_ar = 'رافعة مالية عالية جداً - تأثير قوي للديون على العوائد'
                interpretation_en = 'Very high financial leverage - strong debt impact on returns'
                leverage_effect = 'عالي جداً'
                risk_amplification = 'عالي جداً'
                volatility = 'عالية جداً'
            elif multiplier >= 2:
                interpretation_ar = 'رافعة مالية عالية - تأثير كبير للديون على العوائد'
                interpretation_en = 'High financial leverage - significant debt impact on returns'
                leverage_effect = 'عالي'
                risk_amplification = 'عالي'
                volatility = 'عالية'
            elif multiplier >= 1.5:
                interpretation_ar = 'رافعة مالية معتدلة - تأثير متوسط للديون على العوائد'
                interpretation_en = 'Moderate financial leverage - moderate debt impact on returns'
                leverage_effect = 'معتدل'
                risk_amplification = 'متوسط'
                volatility = 'متوسطة'
            elif multiplier >= 1:
                interpretation_ar = 'رافعة مالية منخفضة - تأثير محدود للديون على العوائد'
                interpretation_en = 'Low financial leverage - limited debt impact on returns'
                leverage_effect = 'منخفض'
                risk_amplification = 'منخفض'
                volatility = 'منخفضة'
            else:
                interpretation_ar = 'رافعة مالية سالبة أو عكسية - تأثير عكسي للديون'
                interpretation_en = 'Negative or inverse financial leverage - inverse debt impact'
                leverage_effect = 'عكسي'
                risk_amplification = 'غير متوقع'
                volatility = 'غير متوقعة'

            return {
                'value': round(multiplier, 2),
                'percentage_change_roe': round(percentage_change_roe, 2),
                'percentage_change_roi': round(percentage_change_roi, 2),
                'formula': 'النسبة المئوية للتغيير في العائد على حقوق الملكية ÷ النسبة المئوية للتغيير في العائد على الاستثمار',
                'formula_en': '% Change in ROE ÷ % Change in ROI',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'leverage_effect': leverage_effect,
                'risk_amplification': risk_amplification,
                'volatility': volatility,
                'benchmark': {
                    'very_high': '≥ 3',
                    'high': '2-2.99',
                    'moderate': '1.5-1.99',
                    'low': '1-1.49',
                    'inverse': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب مضاعف الرافعة المالية: {str(e)}',
                'error_en': f'Error calculating financial leverage multiplier: {str(e)}'
            }

    def cash_coverage_ratio(self, ebitda: float, interest_expense: float) -> Dict[str, Any]:
        """
        9. نسبة التغطية النقدية
        Cash Coverage Ratio = EBITDA / Interest Expense
        """
        try:
            if interest_expense == 0:
                return {
                    'value': None,
                    'formula': 'الأرباح قبل الفوائد والضرائب والإهلاك ÷ مصروفات الفوائد',
                    'formula_en': 'EBITDA ÷ Interest Expense',
                    'interpretation_ar': 'لا يمكن حساب النسبة - مصروفات الفوائد تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - interest expense equals zero'
                }

            ratio = ebitda / interest_expense

            # تفسير النتائج
            if ratio >= 10:
                interpretation_ar = 'تغطية نقدية ممتازة - قدرة عالية جداً على خدمة الدين'
                interpretation_en = 'Excellent cash coverage - very high debt service capability'
                coverage_quality = 'ممتازة'
                cash_flow_adequacy = 'عالية جداً'
                interest_payment_security = 'مضمونة'
                default_risk = 'منخفض جداً'
            elif ratio >= 6:
                interpretation_ar = 'تغطية نقدية جيدة - قدرة مستقرة على خدمة الدين'
                interpretation_en = 'Good cash coverage - stable debt service capability'
                coverage_quality = 'جيدة'
                cash_flow_adequacy = 'جيدة'
                interest_payment_security = 'آمنة'
                default_risk = 'منخفض'
            elif ratio >= 3:
                interpretation_ar = 'تغطية نقدية مقبولة - قدرة معتدلة على خدمة الدين'
                interpretation_en = 'Acceptable cash coverage - moderate debt service capability'
                coverage_quality = 'مقبولة'
                cash_flow_adequacy = 'معتدلة'
                interest_payment_security = 'مقبولة'
                default_risk = 'متوسط'
            elif ratio >= 2:
                interpretation_ar = 'تغطية نقدية ضعيفة - قدرة محدودة على خدمة الدين'
                interpretation_en = 'Poor cash coverage - limited debt service capability'
                coverage_quality = 'ضعيفة'
                cash_flow_adequacy = 'ضعيفة'
                interest_payment_security = 'مخاطر'
                default_risk = 'عالي'
            else:
                interpretation_ar = 'تغطية نقدية ضعيفة جداً - مخاطر عالية في خدمة الدين'
                interpretation_en = 'Very poor cash coverage - high debt service risks'
                coverage_quality = 'ضعيفة جداً'
                cash_flow_adequacy = 'ضعيفة جداً'
                interest_payment_security = 'خطيرة'
                default_risk = 'عالي جداً'

            return {
                'value': round(ratio, 2),
                'ebitda': round(ebitda, 2),
                'interest_expense': round(interest_expense, 2),
                'formula': 'الأرباح قبل الفوائد والضرائب والإهلاك ÷ مصروفات الفوائد',
                'formula_en': 'EBITDA ÷ Interest Expense',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'coverage_quality': coverage_quality,
                'cash_flow_adequacy': cash_flow_adequacy,
                'interest_payment_security': interest_payment_security,
                'default_risk': default_risk,
                'benchmark': {
                    'excellent': '≥ 10',
                    'good': '6-9.99',
                    'acceptable': '3-5.99',
                    'poor': '2-2.99',
                    'very_poor': '< 2'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة التغطية النقدية: {str(e)}',
                'error_en': f'Error calculating cash coverage ratio: {str(e)}'
            }

    def degree_of_financial_leverage(self, ebit: float, interest_expense: float, preferred_dividends: float, tax_rate: float) -> Dict[str, Any]:
        """
        10. درجة الرافعة المالية
        DFL = EBIT / [EBIT - Interest - (Preferred Dividends / (1 - Tax Rate))]
        """
        try:
            # حساب الأرباح المتاحة للمساهمين العاديين
            preferred_div_gross = preferred_dividends / (1 - tax_rate) if tax_rate < 1 else preferred_dividends
            earnings_available = ebit - interest_expense - preferred_div_gross

            if earnings_available == 0:
                return {
                    'value': None,
                    'formula': 'الأرباح قبل الفوائد والضرائب ÷ [الأرباح قبل الفوائد والضرائب - الفوائد - (توزيعات الأسهم الممتازة ÷ (1 - معدل الضريبة))]',
                    'formula_en': 'EBIT ÷ [EBIT - Interest - (Preferred Dividends ÷ (1 - Tax Rate))]',
                    'interpretation_ar': 'لا يمكن حساب درجة الرافعة - الأرباح المتاحة تساوي صفر',
                    'interpretation_en': 'Cannot calculate DFL - available earnings equal zero'
                }

            dfl = ebit / earnings_available

            # تفسير النتائج
            if dfl >= 3:
                interpretation_ar = 'درجة رافعة مالية عالية جداً - حساسية شديدة للتغييرات'
                interpretation_en = 'Very high degree of financial leverage - extreme sensitivity to changes'
                leverage_level = 'عالية جداً'
                earnings_volatility = 'عالية جداً'
                financial_risk = 'عالي جداً'
            elif dfl >= 2:
                interpretation_ar = 'درجة رافعة مالية عالية - حساسية كبيرة للتغييرات'
                interpretation_en = 'High degree of financial leverage - high sensitivity to changes'
                leverage_level = 'عالية'
                earnings_volatility = 'عالية'
                financial_risk = 'عالي'
            elif dfl >= 1.5:
                interpretation_ar = 'درجة رافعة مالية معتدلة - حساسية متوسطة للتغييرات'
                interpretation_en = 'Moderate degree of financial leverage - moderate sensitivity to changes'
                leverage_level = 'معتدلة'
                earnings_volatility = 'متوسطة'
                financial_risk = 'متوسط'
            elif dfl >= 1:
                interpretation_ar = 'درجة رافعة مالية منخفضة - حساسية محدودة للتغييرات'
                interpretation_en = 'Low degree of financial leverage - limited sensitivity to changes'
                leverage_level = 'منخفضة'
                earnings_volatility = 'منخفضة'
                financial_risk = 'منخفض'
            else:
                interpretation_ar = 'درجة رافعة مالية سالبة - تأثير عكسي للديون'
                interpretation_en = 'Negative degree of financial leverage - inverse debt impact'
                leverage_level = 'سالبة'
                earnings_volatility = 'غير متوقعة'
                financial_risk = 'غير محدد'

            return {
                'value': round(dfl, 2),
                'ebit': round(ebit, 2),
                'interest_expense': round(interest_expense, 2),
                'preferred_dividends': round(preferred_dividends, 2),
                'tax_rate': round(tax_rate * 100, 2),
                'earnings_available': round(earnings_available, 2),
                'formula': 'الأرباح قبل الفوائد والضرائب ÷ [الأرباح قبل الفوائد والضرائب - الفوائد - (توزيعات الأسهم الممتازة ÷ (1 - معدل الضريبة))]',
                'formula_en': 'EBIT ÷ [EBIT - Interest - (Preferred Dividends ÷ (1 - Tax Rate))]',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'leverage_level': leverage_level,
                'earnings_volatility': earnings_volatility,
                'financial_risk': financial_risk,
                'benchmark': {
                    'very_high': '≥ 3',
                    'high': '2-2.99',
                    'moderate': '1.5-1.99',
                    'low': '1-1.49',
                    'negative': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب درجة الرافعة المالية: {str(e)}',
                'error_en': f'Error calculating degree of financial leverage: {str(e)}'
            }

    def comprehensive_leverage_analysis(self, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """تحليل شامل للرافعة المالية"""
        try:
            results = {}

            # 1. نسبة الدين إلى حقوق الملكية
            if all(k in financial_data for k in ['total_debt', 'shareholders_equity']):
                results['debt_to_equity_ratio'] = self.debt_to_equity_ratio(
                    financial_data['total_debt'],
                    financial_data['shareholders_equity']
                )

            # 2. نسبة الدين
            if all(k in financial_data for k in ['total_debt', 'total_assets']):
                results['debt_ratio'] = self.debt_ratio(
                    financial_data['total_debt'],
                    financial_data['total_assets']
                )

            # 3. مضاعف حقوق الملكية
            if all(k in financial_data for k in ['total_assets', 'shareholders_equity']):
                results['equity_multiplier'] = self.equity_multiplier(
                    financial_data['total_assets'],
                    financial_data['shareholders_equity']
                )

            # 4. مضاعف تغطية الفوائد
            if all(k in financial_data for k in ['ebit', 'interest_expense']):
                results['times_interest_earned'] = self.times_interest_earned(
                    financial_data['ebit'],
                    financial_data['interest_expense']
                )

            # 5. نسبة تغطية خدمة الدين
            if all(k in financial_data for k in ['ebitda', 'debt_service']):
                results['debt_service_coverage_ratio'] = self.debt_service_coverage_ratio(
                    financial_data['ebitda'],
                    financial_data['debt_service']
                )

            # 6. نسبة الدين طويل الأجل إلى حقوق الملكية
            if all(k in financial_data for k in ['long_term_debt', 'shareholders_equity']):
                results['long_term_debt_to_equity'] = self.long_term_debt_to_equity(
                    financial_data['long_term_debt'],
                    financial_data['shareholders_equity']
                )

            # 7. نسبة الرسملة
            if all(k in financial_data for k in ['long_term_debt', 'total_capitalization']):
                results['capitalization_ratio'] = self.capitalization_ratio(
                    financial_data['long_term_debt'],
                    financial_data['total_capitalization']
                )

            # 8. مضاعف الرافعة المالية
            if all(k in financial_data for k in ['percentage_change_roe', 'percentage_change_roi']):
                results['financial_leverage_multiplier'] = self.financial_leverage_multiplier(
                    financial_data['percentage_change_roe'],
                    financial_data['percentage_change_roi']
                )

            # 9. نسبة التغطية النقدية
            if all(k in financial_data for k in ['ebitda', 'interest_expense']):
                results['cash_coverage_ratio'] = self.cash_coverage_ratio(
                    financial_data['ebitda'],
                    financial_data['interest_expense']
                )

            # 10. درجة الرافعة المالية
            if all(k in financial_data for k in ['ebit', 'interest_expense', 'preferred_dividends', 'tax_rate']):
                results['degree_of_financial_leverage'] = self.degree_of_financial_leverage(
                    financial_data['ebit'],
                    financial_data['interest_expense'],
                    financial_data['preferred_dividends'],
                    financial_data['tax_rate']
                )

            # تقييم عام للرافعة المالية
            overall_assessment = self._assess_overall_leverage(results)

            return {
                'individual_analyses': results,
                'overall_assessment': overall_assessment,
                'analysis_date': financial_data.get('analysis_date', 'غير محدد'),
                'company_name': financial_data.get('company_name', 'غير محدد')
            }

        except Exception as e:
            return {
                'error': f'خطأ في التحليل الشامل للرافعة المالية: {str(e)}',
                'error_en': f'Error in comprehensive leverage analysis: {str(e)}'
            }

    def _assess_overall_leverage(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم الوضع العام للرافعة المالية"""
        try:
            scores = []
            risk_levels = []

            # جمع النقاط ومستويات المخاطر
            for analysis_name, analysis_result in results.items():
                if isinstance(analysis_result, dict) and 'financial_risk' in analysis_result:
                    risk_levels.append(analysis_result['financial_risk'])

                    # تحويل مستوى المخاطر إلى نقاط (عكسي - أقل مخاطر = نقاط أعلى)
                    if analysis_result['financial_risk'] == 'منخفض جداً':
                        scores.append(5)
                    elif analysis_result['financial_risk'] == 'منخفض':
                        scores.append(4)
                    elif analysis_result['financial_risk'] == 'متوسط':
                        scores.append(3)
                    elif analysis_result['financial_risk'] == 'عالي':
                        scores.append(2)
                    else:  # عالي جداً
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
                recommendation_ar = 'هيكل رأس مال ممتاز - مخاطر مالية منخفضة جداً'
                recommendation_en = 'Excellent capital structure - very low financial risks'
            elif average_score >= 3.5:
                overall_rating = 'جيد'
                overall_rating_en = 'Good'
                recommendation_ar = 'هيكل رأس مال جيد - مخاطر مالية منخفضة'
                recommendation_en = 'Good capital structure - low financial risks'
            elif average_score >= 2.5:
                overall_rating = 'مقبول'
                overall_rating_en = 'Acceptable'
                recommendation_ar = 'هيكل رأس مال مقبول - مراقبة مستويات الرافعة'
                recommendation_en = 'Acceptable capital structure - monitor leverage levels'
            elif average_score >= 1.5:
                overall_rating = 'مخاطر عالية'
                overall_rating_en = 'High Risk'
                recommendation_ar = 'مخاطر مالية عالية - إعادة هيكلة رأس المال'
                recommendation_en = 'High financial risks - capital structure restructuring'
            else:
                overall_rating = 'مخاطر عالية جداً'
                overall_rating_en = 'Very High Risk'
                recommendation_ar = 'مخاطر مالية عالية جداً - إجراءات طارئة مطلوبة'
                recommendation_en = 'Very high financial risks - emergency actions required'

            return {
                'overall_score': round(average_score, 2),
                'overall_rating': overall_rating,
                'overall_rating_en': overall_rating_en,
                'total_analyses': len(scores),
                'risk_distribution': {
                    'منخفض جداً': risk_levels.count('منخفض جداً'),
                    'منخفض': risk_levels.count('منخفض'),
                    'متوسط': risk_levels.count('متوسط'),
                    'عالي': risk_levels.count('عالي'),
                    'عالي جداً': risk_levels.count('عالي جداً')
                },
                'recommendation_ar': recommendation_ar,
                'recommendation_en': recommendation_en
            }

        except Exception as e:
            return {
                'error': f'خطأ في تقييم الوضع العام للرافعة المالية: {str(e)}',
                'error_en': f'Error in overall leverage assessment: {str(e)}'
            }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مثيل من فئة تحليل الرافعة المالية
    leverage_analyzer = LeverageAnalysis()

    # بيانات مالية تجريبية
    sample_data = {
        'total_debt': 400000,
        'shareholders_equity': 600000,
        'total_assets': 1000000,
        'long_term_debt': 300000,
        'total_capitalization': 900000,
        'ebit': 150000,
        'ebitda': 200000,
        'interest_expense': 20000,
        'debt_service': 60000,
        'preferred_dividends': 5000,
        'tax_rate': 0.25,
        'percentage_change_roe': 15,
        'percentage_change_roi': 10,
        'company_name': 'شركة المثال التجارية',
        'analysis_date': '2024-12-31'
    }

    # تشغيل التحليل الشامل
    comprehensive_results = leverage_analyzer.comprehensive_leverage_analysis(sample_data)

    print("=== تحليل الرافعة المالية الشامل ===")
    print(f"اسم الشركة: {comprehensive_results.get('company_name', 'غير محدد')}")
    print(f"تاريخ التحليل: {comprehensive_results.get('analysis_date', 'غير محدد')}")
    print("\n=== النتائج التفصيلية ===")

    for analysis_name, result in comprehensive_results.get('individual_analyses', {}).items():
        if isinstance(result, dict) and 'value' in result:
            print(f"\n{analysis_name}:")
            if 'percentage' in result:
                print(f"  القيمة: {result.get('percentage', 'غير محدد')}")
            else:
                print(f"  القيمة: {result.get('value', 'غير محدد')}")
            print(f"  التفسير: {result.get('interpretation_ar', 'غير محدد')}")
            print(f"  مستوى المخاطر: {result.get('financial_risk', result.get('risk_level', 'غير محدد'))}")

    print(f"\n=== التقييم العام ===")
    overall = comprehensive_results.get('overall_assessment', {})
    print(f"التقييم العام: {overall.get('overall_rating', 'غير محدد')}")
    print(f"النقاط: {overall.get('overall_score', 0)}")
    print(f"التوصية: {overall.get('recommendation_ar', 'غير محدد')}")