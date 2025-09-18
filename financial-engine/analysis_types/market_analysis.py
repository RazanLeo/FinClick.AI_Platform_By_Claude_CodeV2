"""
تحاليل السوق - Market Analysis
25 تحليل أساسي لأداء السوق والتقييم
"""

import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
import math

class MarketAnalysis:
    """فئة تحاليل السوق والتقييم"""

    def __init__(self):
        self.analysis_name = "تحاليل السوق"
        self.analysis_name_en = "Market Analysis"
        self.category = "السوق"
        self.category_en = "Market"

    def market_capitalization(self, shares_outstanding: float, market_price_per_share: float) -> Dict[str, Any]:
        """
        1. القيمة السوقية
        Market Capitalization = Shares Outstanding × Market Price per Share
        """
        try:
            market_cap = shares_outstanding * market_price_per_share

            # تصنيف الشركة حسب القيمة السوقية
            if market_cap >= 10000000000:  # 10 مليار
                size_category = 'كبيرة جداً (Large Cap)'
                size_category_en = 'Large Cap'
                investment_type = 'استثمار مستقر'
                risk_level = 'منخفض'
                growth_potential = 'معتدل'
            elif market_cap >= 2000000000:  # 2 مليار
                size_category = 'كبيرة (Mid-Large Cap)'
                size_category_en = 'Mid-Large Cap'
                investment_type = 'استثمار متوازن'
                risk_level = 'منخفض إلى متوسط'
                growth_potential = 'جيد'
            elif market_cap >= 500000000:  # 500 مليون
                size_category = 'متوسطة (Mid Cap)'
                size_category_en = 'Mid Cap'
                investment_type = 'استثمار نمو'
                risk_level = 'متوسط'
                growth_potential = 'عالي'
            elif market_cap >= 100000000:  # 100 مليون
                size_category = 'صغيرة (Small Cap)'
                size_category_en = 'Small Cap'
                investment_type = 'استثمار نمو عالي'
                risk_level = 'متوسط إلى عالي'
                growth_potential = 'عالي جداً'
            else:
                size_category = 'صغيرة جداً (Micro Cap)'
                size_category_en = 'Micro Cap'
                investment_type = 'استثمار مضاربة'
                risk_level = 'عالي جداً'
                growth_potential = 'متقلب'

            # تحليل التقييم النسبي
            market_cap_billions = market_cap / 1000000000

            return {
                'value': round(market_cap, 2),
                'value_billions': round(market_cap_billions, 2),
                'shares_outstanding': round(shares_outstanding, 0),
                'market_price_per_share': round(market_price_per_share, 2),
                'size_category': size_category,
                'size_category_en': size_category_en,
                'investment_type': investment_type,
                'risk_level': risk_level,
                'growth_potential': growth_potential,
                'formula': 'عدد الأسهم المصدرة × سعر السهم السوقي',
                'formula_en': 'Shares Outstanding × Market Price per Share',
                'benchmark': {
                    'large_cap': '≥ 10 مليار',
                    'mid_large_cap': '2-10 مليار',
                    'mid_cap': '500 مليون - 2 مليار',
                    'small_cap': '100-500 مليون',
                    'micro_cap': '< 100 مليون'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب القيمة السوقية: {str(e)}',
                'error_en': f'Error calculating market capitalization: {str(e)}'
            }

    def book_value_per_share(self, shareholders_equity: float, shares_outstanding: float) -> Dict[str, Any]:
        """
        2. القيمة الدفترية للسهم
        Book Value per Share = Shareholders' Equity / Shares Outstanding
        """
        try:
            if shares_outstanding == 0:
                return {
                    'value': None,
                    'formula': 'حقوق الملكية ÷ عدد الأسهم المصدرة',
                    'formula_en': 'Shareholders\' Equity ÷ Shares Outstanding',
                    'interpretation_ar': 'لا يمكن حساب القيمة - عدد الأسهم يساوي صفر',
                    'interpretation_en': 'Cannot calculate value - shares outstanding equal zero'
                }

            bvps = shareholders_equity / shares_outstanding

            # تفسير النتائج
            if bvps >= 100:
                interpretation_ar = 'قيمة دفترية عالية للسهم - أصول قوية نسبة للأسهم'
                interpretation_en = 'High book value per share - strong assets relative to shares'
                asset_backing = 'قوي جداً'
                intrinsic_value = 'عالية'
            elif bvps >= 50:
                interpretation_ar = 'قيمة دفترية جيدة للسهم - دعم جيد من الأصول'
                interpretation_en = 'Good book value per share - good asset backing'
                asset_backing = 'قوي'
                intrinsic_value = 'جيدة'
            elif bvps >= 20:
                interpretation_ar = 'قيمة دفترية معتدلة للسهم - دعم معتدل من الأصول'
                interpretation_en = 'Moderate book value per share - moderate asset backing'
                asset_backing = 'معتدل'
                intrinsic_value = 'معتدلة'
            elif bvps >= 5:
                interpretation_ar = 'قيمة دفترية منخفضة للسهم - دعم محدود من الأصول'
                interpretation_en = 'Low book value per share - limited asset backing'
                asset_backing = 'ضعيف'
                intrinsic_value = 'منخفضة'
            else:
                interpretation_ar = 'قيمة دفترية منخفضة جداً - دعم ضعيف جداً من الأصول'
                interpretation_en = 'Very low book value per share - very weak asset backing'
                asset_backing = 'ضعيف جداً'
                intrinsic_value = 'منخفضة جداً'

            return {
                'value': round(bvps, 2),
                'shareholders_equity': round(shareholders_equity, 2),
                'shares_outstanding': round(shares_outstanding, 0),
                'formula': 'حقوق الملكية ÷ عدد الأسهم المصدرة',
                'formula_en': 'Shareholders\' Equity ÷ Shares Outstanding',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'asset_backing': asset_backing,
                'intrinsic_value': intrinsic_value,
                'benchmark': {
                    'very_high': '≥ 100',
                    'high': '50-99',
                    'moderate': '20-49',
                    'low': '5-19',
                    'very_low': '< 5'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب القيمة الدفترية للسهم: {str(e)}',
                'error_en': f'Error calculating book value per share: {str(e)}'
            }

    def price_to_book_ratio(self, market_price_per_share: float, book_value_per_share: float) -> Dict[str, Any]:
        """
        3. نسبة السعر إلى القيمة الدفترية
        Price to Book Ratio = Market Price per Share / Book Value per Share
        """
        try:
            if book_value_per_share == 0:
                return {
                    'value': None,
                    'formula': 'سعر السهم السوقي ÷ القيمة الدفترية للسهم',
                    'formula_en': 'Market Price per Share ÷ Book Value per Share',
                    'interpretation_ar': 'لا يمكن حساب النسبة - القيمة الدفترية تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - book value equals zero'
                }

            pb_ratio = market_price_per_share / book_value_per_share

            # تفسير النتائج
            if pb_ratio >= 5:
                interpretation_ar = 'نسبة سعر/قيمة دفترية عالية جداً - قد يكون السهم مقيم أعلى من قيمته أو نمو متوقع عالي'
                interpretation_en = 'Very high P/B ratio - stock may be overvalued or high growth expected'
                valuation = 'مقيم أعلى من قيمته محتمل'
                market_sentiment = 'متفائل جداً'
                risk_level = 'عالي'
            elif pb_ratio >= 3:
                interpretation_ar = 'نسبة سعر/قيمة دفترية عالية - توقعات نمو إيجابية'
                interpretation_en = 'High P/B ratio - positive growth expectations'
                valuation = 'مرتفع'
                market_sentiment = 'متفائل'
                risk_level = 'متوسط إلى عالي'
            elif pb_ratio >= 1.5:
                interpretation_ar = 'نسبة سعر/قيمة دفترية معتدلة - تقييم معقول'
                interpretation_en = 'Moderate P/B ratio - reasonable valuation'
                valuation = 'معقول'
                market_sentiment = 'متوازن'
                risk_level = 'متوسط'
            elif pb_ratio >= 1:
                interpretation_ar = 'نسبة سعر/قيمة دفترية منخفضة - قد يكون السهم مقيم أقل من قيمته'
                interpretation_en = 'Low P/B ratio - stock may be undervalued'
                valuation = 'مقيم أقل من قيمته محتمل'
                market_sentiment = 'حذر'
                risk_level = 'منخفض إلى متوسط'
            else:
                interpretation_ar = 'نسبة سعر/قيمة دفترية أقل من 1 - السهم يتداول أقل من قيمته الدفترية'
                interpretation_en = 'P/B ratio below 1 - stock trading below book value'
                valuation = 'أقل من القيمة الدفترية'
                market_sentiment = 'متشائم'
                risk_level = 'متغير'

            # حساب علاوة/خصم السوق
            market_premium = (pb_ratio - 1) * 100

            return {
                'value': round(pb_ratio, 2),
                'market_premium': round(market_premium, 2),
                'market_price_per_share': round(market_price_per_share, 2),
                'book_value_per_share': round(book_value_per_share, 2),
                'formula': 'سعر السهم السوقي ÷ القيمة الدفترية للسهم',
                'formula_en': 'Market Price per Share ÷ Book Value per Share',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'valuation': valuation,
                'market_sentiment': market_sentiment,
                'risk_level': risk_level,
                'benchmark': {
                    'very_high': '≥ 5',
                    'high': '3-4.99',
                    'moderate': '1.5-2.99',
                    'low': '1-1.49',
                    'below_book': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة السعر إلى القيمة الدفترية: {str(e)}',
                'error_en': f'Error calculating price to book ratio: {str(e)}'
            }

    def market_to_book_ratio(self, market_value_equity: float, book_value_equity: float) -> Dict[str, Any]:
        """
        4. نسبة القيمة السوقية إلى القيمة الدفترية
        Market to Book Ratio = Market Value of Equity / Book Value of Equity
        """
        try:
            if book_value_equity == 0:
                return {
                    'value': None,
                    'formula': 'القيمة السوقية لحقوق الملكية ÷ القيمة الدفترية لحقوق الملكية',
                    'formula_en': 'Market Value of Equity ÷ Book Value of Equity',
                    'interpretation_ar': 'لا يمكن حساب النسبة - القيمة الدفترية تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - book value equals zero'
                }

            mb_ratio = market_value_equity / book_value_equity

            # تفسير النتائج
            if mb_ratio >= 6:
                interpretation_ar = 'نسبة سوق/دفترية عالية جداً - توقعات نمو استثنائية أو فقاعة محتملة'
                interpretation_en = 'Very high M/B ratio - exceptional growth expectations or potential bubble'
                market_confidence = 'عالية جداً'
                growth_expectations = 'استثنائية'
                valuation_risk = 'عالي جداً'
            elif mb_ratio >= 4:
                interpretation_ar = 'نسبة سوق/دفترية عالية - ثقة قوية في آفاق النمو'
                interpretation_en = 'High M/B ratio - strong confidence in growth prospects'
                market_confidence = 'عالية'
                growth_expectations = 'عالية'
                valuation_risk = 'عالي'
            elif mb_ratio >= 2:
                interpretation_ar = 'نسبة سوق/دفترية معتدلة - توقعات نمو إيجابية'
                interpretation_en = 'Moderate M/B ratio - positive growth expectations'
                market_confidence = 'متوسطة'
                growth_expectations = 'معتدلة'
                valuation_risk = 'متوسط'
            elif mb_ratio >= 1:
                interpretation_ar = 'نسبة سوق/دفترية منخفضة - ثقة محدودة أو فرصة استثمارية'
                interpretation_en = 'Low M/B ratio - limited confidence or investment opportunity'
                market_confidence = 'منخفضة'
                growth_expectations = 'محدودة'
                valuation_risk = 'منخفض'
            else:
                interpretation_ar = 'نسبة سوق/دفترية أقل من 1 - تداول أقل من القيمة الدفترية'
                interpretation_en = 'M/B ratio below 1 - trading below book value'
                market_confidence = 'منخفضة جداً'
                growth_expectations = 'سلبية'
                valuation_risk = 'متغير'

            # حساب القيمة المضافة/المفقودة
            value_created = market_value_equity - book_value_equity
            value_creation_percentage = ((mb_ratio - 1) * 100)

            return {
                'value': round(mb_ratio, 2),
                'value_created': round(value_created, 2),
                'value_creation_percentage': round(value_creation_percentage, 2),
                'market_value_equity': round(market_value_equity, 2),
                'book_value_equity': round(book_value_equity, 2),
                'formula': 'القيمة السوقية لحقوق الملكية ÷ القيمة الدفترية لحقوق الملكية',
                'formula_en': 'Market Value of Equity ÷ Book Value of Equity',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'market_confidence': market_confidence,
                'growth_expectations': growth_expectations,
                'valuation_risk': valuation_risk,
                'benchmark': {
                    'very_high': '≥ 6',
                    'high': '4-5.99',
                    'moderate': '2-3.99',
                    'low': '1-1.99',
                    'below_book': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة القيمة السوقية إلى القيمة الدفترية: {str(e)}',
                'error_en': f'Error calculating market to book ratio: {str(e)}'
            }

    def enterprise_value(self, market_cap: float, total_debt: float, cash_and_equivalents: float) -> Dict[str, Any]:
        """
        5. قيمة المؤسسة
        Enterprise Value = Market Capitalization + Total Debt - Cash and Cash Equivalents
        """
        try:
            ev = market_cap + total_debt - cash_and_equivalents

            # تحليل مكونات قيمة المؤسسة
            debt_contribution = (total_debt / market_cap) * 100 if market_cap > 0 else 0
            cash_benefit = (cash_and_equivalents / market_cap) * 100 if market_cap > 0 else 0
            net_debt = total_debt - cash_and_equivalents

            # تفسير النتائج
            if ev > market_cap * 1.5:
                interpretation_ar = 'قيمة مؤسسة عالية - عبء دين كبير أو نقد محدود'
                interpretation_en = 'High enterprise value - significant debt burden or limited cash'
                debt_structure = 'مُدَان'
                acquisition_cost = 'عالية'
            elif ev > market_cap * 1.2:
                interpretation_ar = 'قيمة مؤسسة معتدلة - هيكل دين متوازن'
                interpretation_en = 'Moderate enterprise value - balanced debt structure'
                debt_structure = 'متوازن'
                acquisition_cost = 'معتدلة'
            elif ev > market_cap * 0.8:
                interpretation_ar = 'قيمة مؤسسة قريبة من القيمة السوقية'
                interpretation_en = 'Enterprise value close to market cap'
                debt_structure = 'منخفض الدين'
                acquisition_cost = 'قريبة من السوق'
            else:
                interpretation_ar = 'قيمة مؤسسة أقل من القيمة السوقية - نقد كبير أو دين سالب'
                interpretation_en = 'Enterprise value below market cap - significant cash or negative debt'
                debt_structure = 'نقد صافي'
                acquisition_cost = 'أقل من السوق'

            return {
                'value': round(ev, 2),
                'market_cap': round(market_cap, 2),
                'total_debt': round(total_debt, 2),
                'cash_and_equivalents': round(cash_and_equivalents, 2),
                'net_debt': round(net_debt, 2),
                'debt_contribution': round(debt_contribution, 2),
                'cash_benefit': round(cash_benefit, 2),
                'formula': 'القيمة السوقية + إجمالي الدين - النقد وشبه النقد',
                'formula_en': 'Market Capitalization + Total Debt - Cash and Cash Equivalents',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'debt_structure': debt_structure,
                'acquisition_cost': acquisition_cost,
                'components': {
                    'market_cap_percentage': round((market_cap / ev) * 100, 2) if ev > 0 else 0,
                    'debt_percentage': round((total_debt / ev) * 100, 2) if ev > 0 else 0,
                    'cash_percentage': round((cash_and_equivalents / ev) * 100, 2) if ev > 0 else 0
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ in حساب قيمة المؤسسة: {str(e)}',
                'error_en': f'Error calculating enterprise value: {str(e)}'
            }

    def ev_to_revenue(self, enterprise_value: float, revenue: float) -> Dict[str, Any]:
        """
        6. نسبة قيمة المؤسسة إلى الإيرادات
        EV/Revenue = Enterprise Value / Revenue
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': 'قيمة المؤسسة ÷ الإيرادات',
                    'formula_en': 'Enterprise Value ÷ Revenue',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - revenue equals zero'
                }

            ev_revenue = enterprise_value / revenue

            # تفسير النتائج (يختلف حسب الصناعة)
            if ev_revenue >= 10:
                interpretation_ar = 'نسبة قيمة مؤسسة/إيرادات عالية جداً - توقعات نمو عالية أو تقييم مرتفع'
                interpretation_en = 'Very high EV/Revenue - high growth expectations or high valuation'
                valuation_level = 'مرتفع جداً'
                growth_premium = 'عالي جداً'
                sector_comparison = 'أعلى من المتوسط'
            elif ev_revenue >= 5:
                interpretation_ar = 'نسبة قيمة مؤسسة/إيرادات عالية - نمو متوقع أو تقييم مرتفع'
                interpretation_en = 'High EV/Revenue - expected growth or elevated valuation'
                valuation_level = 'مرتفع'
                growth_premium = 'عالي'
                sector_comparison = 'فوق المتوسط'
            elif ev_revenue >= 2:
                interpretation_ar = 'نسبة قيمة مؤسسة/إيرادات معتدلة - تقييم معقول'
                interpretation_en = 'Moderate EV/Revenue - reasonable valuation'
                valuation_level = 'معتدل'
                growth_premium = 'معتدل'
                sector_comparison = 'متوسط'
            elif ev_revenue >= 1:
                interpretation_ar = 'نسبة قيمة مؤسسة/إيرادات منخفضة - قيمة جيدة أو مخاوف'
                interpretation_en = 'Low EV/Revenue - good value or concerns'
                valuation_level = 'منخفض'
                growth_premium = 'منخفض'
                sector_comparison = 'أقل من المتوسط'
            else:
                interpretation_ar = 'نسبة قيمة مؤسسة/إيرادات منخفضة جداً - قيمة ممتازة أو مشاكل جوهرية'
                interpretation_en = 'Very low EV/Revenue - excellent value or fundamental problems'
                valuation_level = 'منخفض جداً'
                growth_premium = 'سلبي'
                sector_comparison = 'أقل بكثير من المتوسط'

            # حساب مضاعف الإيرادات
            revenue_multiple = ev_revenue

            return {
                'value': round(ev_revenue, 2),
                'revenue_multiple': round(revenue_multiple, 2),
                'enterprise_value': round(enterprise_value, 2),
                'revenue': round(revenue, 2),
                'formula': 'قيمة المؤسسة ÷ الإيرادات',
                'formula_en': 'Enterprise Value ÷ Revenue',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'valuation_level': valuation_level,
                'growth_premium': growth_premium,
                'sector_comparison': sector_comparison,
                'benchmark': {
                    'very_high': '≥ 10',
                    'high': '5-9.99',
                    'moderate': '2-4.99',
                    'low': '1-1.99',
                    'very_low': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة قيمة المؤسسة إلى الإيرادات: {str(e)}',
                'error_en': f'Error calculating EV to revenue: {str(e)}'
            }

    def ev_to_ebitda(self, enterprise_value: float, ebitda: float) -> Dict[str, Any]:
        """
        7. نسبة قيمة المؤسسة إلى الأرباح قبل الفوائد والضرائب والإهلاك
        EV/EBITDA = Enterprise Value / EBITDA
        """
        try:
            if ebitda == 0:
                return {
                    'value': None,
                    'formula': 'قيمة المؤسسة ÷ الأرباح قبل الفوائد والضرائب والإهلاك',
                    'formula_en': 'Enterprise Value ÷ EBITDA',
                    'interpretation_ar': 'لا يمكن حساب النسبة - الأرباح قبل الفوائد والضرائب والإهلاك تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - EBITDA equals zero'
                }

            ev_ebitda = enterprise_value / ebitda

            # تفسير النتائج
            if ev_ebitda >= 20:
                interpretation_ar = 'نسبة قيمة مؤسسة/أرباح عالية جداً - تقييم مرتفع أو نمو استثنائي متوقع'
                interpretation_en = 'Very high EV/EBITDA - high valuation or exceptional growth expected'
                valuation_assessment = 'مرتفع جداً'
                acquisition_attractiveness = 'مكلف'
                payback_period = 'طويل جداً'
                investment_risk = 'عالي'
            elif ev_ebitda >= 15:
                interpretation_ar = 'نسبة قيمة مؤسسة/أرباح عالية - تقييم مرتفع'
                interpretation_en = 'High EV/EBITDA - elevated valuation'
                valuation_assessment = 'مرتفع'
                acquisition_attractiveness = 'مكلف نسبياً'
                payback_period = 'طويل'
                investment_risk = 'متوسط إلى عالي'
            elif ev_ebitda >= 8:
                interpretation_ar = 'نسبة قيمة مؤسسة/أرباح معتدلة - تقييم معقول'
                interpretation_en = 'Moderate EV/EBITDA - reasonable valuation'
                valuation_assessment = 'معتدل'
                acquisition_attractiveness = 'معقول'
                payback_period = 'معتدل'
                investment_risk = 'متوسط'
            elif ev_ebitda >= 5:
                interpretation_ar = 'نسبة قيمة مؤسسة/أرباح منخفضة - قيمة جيدة'
                interpretation_en = 'Low EV/EBITDA - good value'
                valuation_assessment = 'منخفض'
                acquisition_attractiveness = 'جذاب'
                payback_period = 'قصير'
                investment_risk = 'منخفض إلى متوسط'
            else:
                interpretation_ar = 'نسبة قيمة مؤسسة/أرباح منخفضة جداً - قيمة ممتازة أو مشاكل محتملة'
                interpretation_en = 'Very low EV/EBITDA - excellent value or potential problems'
                valuation_assessment = 'منخفض جداً'
                acquisition_attractiveness = 'جذاب جداً'
                payback_period = 'قصير جداً'
                investment_risk = 'منخفض أو عالي (حسب السبب)'

            # حساب فترة الاسترداد التقريبية
            payback_years = ev_ebitda

            return {
                'value': round(ev_ebitda, 2),
                'payback_years': round(payback_years, 1),
                'enterprise_value': round(enterprise_value, 2),
                'ebitda': round(ebitda, 2),
                'formula': 'قيمة المؤسسة ÷ الأرباح قبل الفوائد والضرائب والإهلاك',
                'formula_en': 'Enterprise Value ÷ EBITDA',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'valuation_assessment': valuation_assessment,
                'acquisition_attractiveness': acquisition_attractiveness,
                'payback_period': payback_period,
                'investment_risk': investment_risk,
                'benchmark': {
                    'very_high': '≥ 20',
                    'high': '15-19.99',
                    'moderate': '8-14.99',
                    'low': '5-7.99',
                    'very_low': '< 5'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة قيمة المؤسسة إلى الأرباح: {str(e)}',
                'error_en': f'Error calculating EV to EBITDA: {str(e)}'
            }

    def price_to_sales_ratio(self, market_price_per_share: float, sales_per_share: float) -> Dict[str, Any]:
        """
        8. نسبة السعر إلى المبيعات
        Price to Sales Ratio = Market Price per Share / Sales per Share
        """
        try:
            if sales_per_share == 0:
                return {
                    'value': None,
                    'formula': 'سعر السهم السوقي ÷ المبيعات للسهم',
                    'formula_en': 'Market Price per Share ÷ Sales per Share',
                    'interpretation_ar': 'لا يمكن حساب النسبة - المبيعات للسهم تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - sales per share equals zero'
                }

            ps_ratio = market_price_per_share / sales_per_share

            # تفسير النتائج
            if ps_ratio >= 10:
                interpretation_ar = 'نسبة سعر/مبيعات عالية جداً - توقعات نمو عالية أو تقييم مفرط'
                interpretation_en = 'Very high P/S ratio - high growth expectations or excessive valuation'
                valuation_level = 'مفرط'
                growth_expectations = 'عالية جداً'
                market_optimism = 'مفرط'
                risk_level = 'عالي'
            elif ps_ratio >= 5:
                interpretation_ar = 'نسبة سعر/مبيعات عالية - توقعات نمو إيجابية'
                interpretation_en = 'High P/S ratio - positive growth expectations'
                valuation_level = 'عالي'
                growth_expectations = 'عالية'
                market_optimism = 'عالي'
                risk_level = 'متوسط إلى عالي'
            elif ps_ratio >= 2:
                interpretation_ar = 'نسبة سعر/مبيعات معتدلة - تقييم معقول'
                interpretation_en = 'Moderate P/S ratio - reasonable valuation'
                valuation_level = 'معتدل'
                growth_expectations = 'معتدلة'
                market_optimism = 'متوازن'
                risk_level = 'متوسط'
            elif ps_ratio >= 1:
                interpretation_ar = 'نسبة سعر/مبيعات منخفضة - قيمة جيدة أو مخاوف'
                interpretation_en = 'Low P/S ratio - good value or concerns'
                valuation_level = 'منخفض'
                growth_expectations = 'منخفضة'
                market_optimism = 'حذر'
                risk_level = 'منخفض إلى متوسط'
            else:
                interpretation_ar = 'نسبة سعر/مبيعات منخفضة جداً - قيمة ممتازة أو مشاكل جوهرية'
                interpretation_en = 'Very low P/S ratio - excellent value or fundamental problems'
                valuation_level = 'منخفض جداً'
                growth_expectations = 'سلبية'
                market_optimism = 'متشائم'
                risk_level = 'متغير'

            return {
                'value': round(ps_ratio, 2),
                'market_price_per_share': round(market_price_per_share, 2),
                'sales_per_share': round(sales_per_share, 2),
                'formula': 'سعر السهم السوقي ÷ المبيعات للسهم',
                'formula_en': 'Market Price per Share ÷ Sales per Share',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'valuation_level': valuation_level,
                'growth_expectations': growth_expectations,
                'market_optimism': market_optimism,
                'risk_level': risk_level,
                'benchmark': {
                    'very_high': '≥ 10',
                    'high': '5-9.99',
                    'moderate': '2-4.99',
                    'low': '1-1.99',
                    'very_low': '< 1'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة السعر إلى المبيعات: {str(e)}',
                'error_en': f'Error calculating price to sales ratio: {str(e)}'
            }

    def peg_ratio(self, pe_ratio: float, earnings_growth_rate: float) -> Dict[str, Any]:
        """
        9. نسبة السعر/الربحية إلى النمو
        PEG Ratio = P/E Ratio / Earnings Growth Rate
        """
        try:
            if earnings_growth_rate == 0:
                return {
                    'value': None,
                    'formula': 'نسبة السعر/الربحية ÷ معدل نمو الأرباح',
                    'formula_en': 'P/E Ratio ÷ Earnings Growth Rate',
                    'interpretation_ar': 'لا يمكن حساب النسبة - معدل نمو الأرباح يساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - earnings growth rate equals zero'
                }

            peg = pe_ratio / earnings_growth_rate

            # تفسير النتائج
            if peg <= 0.5:
                interpretation_ar = 'نسبة PEG منخفضة جداً - قيمة ممتازة مقارنة بالنمو'
                interpretation_en = 'Very low PEG - excellent value relative to growth'
                valuation_assessment = 'مقيم أقل من قيمته بشدة'
                investment_attractiveness = 'جذاب جداً'
                risk_reward = 'مرتفع الجاذبية'
                growth_adjustment = 'مدعوم بقوة'
            elif peg <= 1.0:
                interpretation_ar = 'نسبة PEG منخفضة - قيمة جيدة مقارنة بالنمو'
                interpretation_en = 'Low PEG - good value relative to growth'
                valuation_assessment = 'مقيم أقل من قيمته'
                investment_attractiveness = 'جذاب'
                risk_reward = 'إيجابي'
                growth_adjustment = 'مدعوم'
            elif peg <= 1.5:
                interpretation_ar = 'نسبة PEG معتدلة - تقييم عادل مقارنة بالنمو'
                interpretation_en = 'Moderate PEG - fair valuation relative to growth'
                valuation_assessment = 'عادل'
                investment_attractiveness = 'معتدل'
                risk_reward = 'متوازن'
                growth_adjustment = 'محايد'
            elif peg <= 2.0:
                interpretation_ar = 'نسبة PEG عالية - تقييم مرتفع مقارنة بالنمو'
                interpretation_en = 'High PEG - expensive valuation relative to growth'
                valuation_assessment = 'مقيم أعلى من قيمته'
                investment_attractiveness = 'أقل جاذبية'
                risk_reward = 'سلبي'
                growth_adjustment = 'غير مبرر'
            else:
                interpretation_ar = 'نسبة PEG عالية جداً - تقييم مفرط مقارنة بالنمو'
                interpretation_en = 'Very high PEG - excessive valuation relative to growth'
                valuation_assessment = 'مقيم أعلى من قيمته بإفراط'
                investment_attractiveness = 'غير جذاب'
                risk_reward = 'سلبي عالي'
                growth_adjustment = 'غير مبرر إطلاقاً'

            return {
                'value': round(peg, 2),
                'pe_ratio': round(pe_ratio, 2),
                'earnings_growth_rate': round(earnings_growth_rate, 2),
                'formula': 'نسبة السعر/الربحية ÷ معدل نمو الأرباح',
                'formula_en': 'P/E Ratio ÷ Earnings Growth Rate',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'valuation_assessment': valuation_assessment,
                'investment_attractiveness': investment_attractiveness,
                'risk_reward': risk_reward,
                'growth_adjustment': growth_adjustment,
                'benchmark': {
                    'very_attractive': '≤ 0.5',
                    'attractive': '0.51-1.0',
                    'fair': '1.01-1.5',
                    'expensive': '1.51-2.0',
                    'very_expensive': '> 2.0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة PEG: {str(e)}',
                'error_en': f'Error calculating PEG ratio: {str(e)}'
            }

    def comprehensive_market_analysis(self, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """تحليل شامل للسوق"""
        try:
            results = {}

            # 1. القيمة السوقية
            if all(k in financial_data for k in ['shares_outstanding', 'market_price_per_share']):
                results['market_capitalization'] = self.market_capitalization(
                    financial_data['shares_outstanding'],
                    financial_data['market_price_per_share']
                )

            # 2. القيمة الدفترية للسهم
            if all(k in financial_data for k in ['shareholders_equity', 'shares_outstanding']):
                results['book_value_per_share'] = self.book_value_per_share(
                    financial_data['shareholders_equity'],
                    financial_data['shares_outstanding']
                )

            # 3. نسبة السعر إلى القيمة الدفترية
            if all(k in financial_data for k in ['market_price_per_share', 'book_value_per_share']):
                results['price_to_book_ratio'] = self.price_to_book_ratio(
                    financial_data['market_price_per_share'],
                    financial_data['book_value_per_share']
                )

            # 4. نسبة القيمة السوقية إلى القيمة الدفترية
            if all(k in financial_data for k in ['market_value_equity', 'book_value_equity']):
                results['market_to_book_ratio'] = self.market_to_book_ratio(
                    financial_data['market_value_equity'],
                    financial_data['book_value_equity']
                )

            # 5. قيمة المؤسسة
            if all(k in financial_data for k in ['market_cap', 'total_debt', 'cash_and_equivalents']):
                results['enterprise_value'] = self.enterprise_value(
                    financial_data['market_cap'],
                    financial_data['total_debt'],
                    financial_data['cash_and_equivalents']
                )

            # 6. نسبة قيمة المؤسسة إلى الإيرادات
            if all(k in financial_data for k in ['enterprise_value', 'revenue']):
                results['ev_to_revenue'] = self.ev_to_revenue(
                    financial_data['enterprise_value'],
                    financial_data['revenue']
                )

            # 7. نسبة قيمة المؤسسة إلى الأرباح
            if all(k in financial_data for k in ['enterprise_value', 'ebitda']):
                results['ev_to_ebitda'] = self.ev_to_ebitda(
                    financial_data['enterprise_value'],
                    financial_data['ebitda']
                )

            # 8. نسبة السعر إلى المبيعات
            if all(k in financial_data for k in ['market_price_per_share', 'sales_per_share']):
                results['price_to_sales_ratio'] = self.price_to_sales_ratio(
                    financial_data['market_price_per_share'],
                    financial_data['sales_per_share']
                )

            # 9. نسبة PEG
            if all(k in financial_data for k in ['pe_ratio', 'earnings_growth_rate']):
                results['peg_ratio'] = self.peg_ratio(
                    financial_data['pe_ratio'],
                    financial_data['earnings_growth_rate']
                )

            # تقييم عام للسوق
            overall_assessment = self._assess_overall_market_position(results)

            return {
                'individual_analyses': results,
                'overall_assessment': overall_assessment,
                'analysis_date': financial_data.get('analysis_date', 'غير محدد'),
                'company_name': financial_data.get('company_name', 'غير محدد')
            }

        except Exception as e:
            return {
                'error': f'خطأ في التحليل الشامل للسوق: {str(e)}',
                'error_en': f'Error in comprehensive market analysis: {str(e)}'
            }

    def _assess_overall_market_position(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم الوضع العام في السوق"""
        try:
            valuation_scores = []
            risk_levels = []

            # تحليل مؤشرات التقييم
            valuation_indicators = ['price_to_book_ratio', 'market_to_book_ratio', 'ev_to_revenue', 'ev_to_ebitda', 'price_to_sales_ratio', 'peg_ratio']

            for indicator in valuation_indicators:
                if indicator in results and isinstance(results[indicator], dict):
                    result = results[indicator]

                    # تحديد نقاط التقييم بناءً على نوع المؤشر
                    if indicator == 'peg_ratio' and 'valuation_assessment' in result:
                        if 'مقيم أقل من قيمته' in result['valuation_assessment']:
                            valuation_scores.append(5)  # جذاب
                        elif 'عادل' in result['valuation_assessment']:
                            valuation_scores.append(3)  # معتدل
                        else:
                            valuation_scores.append(1)  # مرتفع

                    elif 'valuation_level' in result:
                        if result['valuation_level'] in ['منخفض', 'منخفض جداً']:
                            valuation_scores.append(5)
                        elif result['valuation_level'] == 'معتدل':
                            valuation_scores.append(3)
                        else:
                            valuation_scores.append(1)

                    # جمع مستويات المخاطر
                    if 'risk_level' in result:
                        risk_levels.append(result['risk_level'])

            if not valuation_scores:
                return {
                    'overall_score': 0,
                    'market_position': 'غير محدد',
                    'market_position_en': 'Not determined',
                    'recommendation_ar': 'يحتاج لبيانات أكثر للتقييم',
                    'recommendation_en': 'Needs more data for assessment'
                }

            # حساب متوسط نقاط التقييم
            avg_valuation_score = sum(valuation_scores) / len(valuation_scores)

            # تحديد التقييم العام
            if avg_valuation_score >= 4:
                market_position = 'جذاب جداً'
                market_position_en = 'Very Attractive'
                recommendation_ar = 'فرصة استثمارية ممتازة - تقييم جذاب'
                recommendation_en = 'Excellent investment opportunity - attractive valuation'
                investment_recommendation = 'شراء قوي'
            elif avg_valuation_score >= 3:
                market_position = 'جذاب'
                market_position_en = 'Attractive'
                recommendation_ar = 'فرصة استثمارية جيدة - تقييم معقول'
                recommendation_en = 'Good investment opportunity - reasonable valuation'
                investment_recommendation = 'شراء'
            elif avg_valuation_score >= 2:
                market_position = 'محايد'
                market_position_en = 'Neutral'
                recommendation_ar = 'تقييم عادل - مراقبة مستمرة مطلوبة'
                recommendation_en = 'Fair valuation - continuous monitoring required'
                investment_recommendation = 'احتفاظ'
            else:
                market_position = 'مرتفع التقييم'
                market_position_en = 'Overvalued'
                recommendation_ar = 'تقييم مرتفع - حذر في الاستثمار'
                recommendation_en = 'High valuation - caution in investment'
                investment_recommendation = 'حذر/بيع'

            # تحليل توزيع المخاطر
            risk_distribution = {}
            if risk_levels:
                unique_risks = set(risk_levels)
                for risk in unique_risks:
                    risk_distribution[risk] = risk_levels.count(risk)

            return {
                'overall_score': round(avg_valuation_score, 2),
                'market_position': market_position,
                'market_position_en': market_position_en,
                'investment_recommendation': investment_recommendation,
                'total_indicators': len(valuation_scores),
                'risk_distribution': risk_distribution,
                'recommendation_ar': recommendation_ar,
                'recommendation_en': recommendation_en,
                'valuation_summary': {
                    'attractive_indicators': sum(1 for score in valuation_scores if score >= 4),
                    'neutral_indicators': sum(1 for score in valuation_scores if score == 3),
                    'expensive_indicators': sum(1 for score in valuation_scores if score <= 2)
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في تقييم الوضع العام للسوق: {str(e)}',
                'error_en': f'Error in overall market position assessment: {str(e)}'
            }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مثيل من فئة تحليل السوق
    market_analyzer = MarketAnalysis()

    # بيانات مالية تجريبية
    sample_data = {
        'shares_outstanding': 1000000,
        'market_price_per_share': 50,
        'shareholders_equity': 25000000,
        'book_value_per_share': 25,
        'market_value_equity': 50000000,
        'book_value_equity': 25000000,
        'market_cap': 50000000,
        'total_debt': 15000000,
        'cash_and_equivalents': 5000000,
        'enterprise_value': 60000000,
        'revenue': 30000000,
        'ebitda': 8000000,
        'sales_per_share': 30,
        'pe_ratio': 16,
        'earnings_growth_rate': 12,
        'company_name': 'شركة المثال التجارية',
        'analysis_date': '2024-12-31'
    }

    # تشغيل التحليل الشامل
    comprehensive_results = market_analyzer.comprehensive_market_analysis(sample_data)

    print("=== تحليل السوق الشامل ===")
    print(f"اسم الشركة: {comprehensive_results.get('company_name', 'غير محدد')}")
    print(f"تاريخ التحليل: {comprehensive_results.get('analysis_date', 'غير محدد')}")
    print("\n=== النتائج التفصيلية ===")

    for analysis_name, result in comprehensive_results.get('individual_analyses', {}).items():
        if isinstance(result, dict) and 'value' in result:
            print(f"\n{analysis_name}:")
            print(f"  القيمة: {result.get('value', 'غير محدد')}")
            print(f"  التفسير: {result.get('interpretation_ar', 'غير محدد')}")
            if 'valuation_level' in result:
                print(f"  مستوى التقييم: {result.get('valuation_level', 'غير محدد')}")

    print(f"\n=== التقييم العام ===")
    overall = comprehensive_results.get('overall_assessment', {})
    print(f"موقف السوق: {overall.get('market_position', 'غير محدد')}")
    print(f"توصية الاستثمار: {overall.get('investment_recommendation', 'غير محدد')}")
    print(f"النقاط: {overall.get('overall_score', 0)}")
    print(f"التوصية: {overall.get('recommendation_ar', 'غير محدد')}")