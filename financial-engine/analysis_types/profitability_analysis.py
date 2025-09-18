"""
تحاليل الربحية - Profitability Analysis
15 تحليل أساسي للربحية المالية
"""

import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
import math

class ProfitabilityAnalysis:
    """فئة تحاليل الربحية المالية"""

    def __init__(self):
        self.analysis_name = "تحاليل الربحية"
        self.analysis_name_en = "Profitability Analysis"
        self.category = "الربحية"
        self.category_en = "Profitability"

    def gross_profit_margin(self, gross_profit: float, revenue: float) -> Dict[str, Any]:
        """
        1. هامش الربح الإجمالي
        Gross Profit Margin = (Gross Profit / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(الربح الإجمالي ÷ الإيرادات) × 100',
                    'formula_en': '(Gross Profit ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب الهامش - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate margin - revenue equals zero'
                }

            margin = (gross_profit / revenue) * 100

            # تفسير النتائج
            if margin >= 50:
                interpretation_ar = 'هامش ربح إجمالي ممتاز - قدرة عالية على تحقيق الأرباح'
                interpretation_en = 'Excellent gross profit margin - high profitability capability'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif margin >= 30:
                interpretation_ar = 'هامش ربح إجمالي جيد - أداء مالي مستقر'
                interpretation_en = 'Good gross profit margin - stable financial performance'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif margin >= 15:
                interpretation_ar = 'هامش ربح إجمالي مقبول - يحتاج للتحسين'
                interpretation_en = 'Acceptable gross profit margin - needs improvement'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif margin >= 0:
                interpretation_ar = 'هامش ربح إجمالي ضعيف - مخاطر ربحية'
                interpretation_en = 'Poor gross profit margin - profitability risks'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'خسارة إجمالية - وضع مالي خطير'
                interpretation_en = 'Gross loss - critical financial situation'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(margin, 2),
                'percentage': f"{margin:.2f}%",
                'gross_profit': round(gross_profit, 2),
                'revenue': round(revenue, 2),
                'formula': '(الربح الإجمالي ÷ الإيرادات) × 100',
                'formula_en': '(Gross Profit ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 50%',
                    'good': '30-49%',
                    'acceptable': '15-29%',
                    'poor': '0-14%',
                    'critical': '< 0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب هامش الربح الإجمالي: {str(e)}',
                'error_en': f'Error calculating gross profit margin: {str(e)}'
            }

    def operating_profit_margin(self, operating_profit: float, revenue: float) -> Dict[str, Any]:
        """
        2. هامش الربح التشغيلي
        Operating Profit Margin = (Operating Profit / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(الربح التشغيلي ÷ الإيرادات) × 100',
                    'formula_en': '(Operating Profit ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب الهامش - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate margin - revenue equals zero'
                }

            margin = (operating_profit / revenue) * 100

            # تفسير النتائج
            if margin >= 25:
                interpretation_ar = 'هامش ربح تشغيلي ممتاز - كفاءة تشغيلية عالية'
                interpretation_en = 'Excellent operating profit margin - high operational efficiency'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif margin >= 15:
                interpretation_ar = 'هامش ربح تشغيلي جيد - إدارة تشغيلية فعالة'
                interpretation_en = 'Good operating profit margin - effective operational management'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif margin >= 8:
                interpretation_ar = 'هامش ربح تشغيلي مقبول - يحتاج لتحسين الكفاءة'
                interpretation_en = 'Acceptable operating profit margin - needs efficiency improvement'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif margin >= 0:
                interpretation_ar = 'هامش ربح تشغيلي ضعيف - مشاكل في الكفاءة التشغيلية'
                interpretation_en = 'Poor operating profit margin - operational efficiency problems'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'خسارة تشغيلية - مشاكل جوهرية في العمليات'
                interpretation_en = 'Operating loss - fundamental operational problems'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(margin, 2),
                'percentage': f"{margin:.2f}%",
                'operating_profit': round(operating_profit, 2),
                'revenue': round(revenue, 2),
                'formula': '(الربح التشغيلي ÷ الإيرادات) × 100',
                'formula_en': '(Operating Profit ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 25%',
                    'good': '15-24%',
                    'acceptable': '8-14%',
                    'poor': '0-7%',
                    'critical': '< 0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب هامش الربح التشغيلي: {str(e)}',
                'error_en': f'Error calculating operating profit margin: {str(e)}'
            }

    def net_profit_margin(self, net_profit: float, revenue: float) -> Dict[str, Any]:
        """
        3. هامش الربح الصافي
        Net Profit Margin = (Net Profit / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(الربح الصافي ÷ الإيرادات) × 100',
                    'formula_en': '(Net Profit ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب الهامش - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate margin - revenue equals zero'
                }

            margin = (net_profit / revenue) * 100

            # تفسير النتائج
            if margin >= 20:
                interpretation_ar = 'هامش ربح صافي ممتاز - ربحية عالية جداً'
                interpretation_en = 'Excellent net profit margin - very high profitability'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif margin >= 10:
                interpretation_ar = 'هامش ربح صافي جيد - ربحية مستقرة'
                interpretation_en = 'Good net profit margin - stable profitability'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif margin >= 5:
                interpretation_ar = 'هامش ربح صافي مقبول - يحتاج للتحسين'
                interpretation_en = 'Acceptable net profit margin - needs improvement'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif margin >= 0:
                interpretation_ar = 'هامش ربح صافي ضعيف - ربحية منخفضة'
                interpretation_en = 'Poor net profit margin - low profitability'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'خسارة صافية - وضع مالي خطير'
                interpretation_en = 'Net loss - critical financial situation'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(margin, 2),
                'percentage': f"{margin:.2f}%",
                'net_profit': round(net_profit, 2),
                'revenue': round(revenue, 2),
                'formula': '(الربح الصافي ÷ الإيرادات) × 100',
                'formula_en': '(Net Profit ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 20%',
                    'good': '10-19%',
                    'acceptable': '5-9%',
                    'poor': '0-4%',
                    'critical': '< 0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب هامش الربح الصافي: {str(e)}',
                'error_en': f'Error calculating net profit margin: {str(e)}'
            }

    def return_on_assets(self, net_profit: float, total_assets: float) -> Dict[str, Any]:
        """
        4. العائد على الأصول
        Return on Assets (ROA) = (Net Profit / Total Assets) × 100
        """
        try:
            if total_assets == 0:
                return {
                    'value': None,
                    'formula': '(الربح الصافي ÷ إجمالي الأصول) × 100',
                    'formula_en': '(Net Profit ÷ Total Assets) × 100',
                    'interpretation_ar': 'لا يمكن حساب العائد - إجمالي الأصول تساوي صفر',
                    'interpretation_en': 'Cannot calculate return - total assets equal zero'
                }

            roa = (net_profit / total_assets) * 100

            # تفسير النتائج
            if roa >= 15:
                interpretation_ar = 'عائد ممتاز على الأصول - استخدام عالي الكفاءة للأصول'
                interpretation_en = 'Excellent return on assets - highly efficient asset utilization'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif roa >= 8:
                interpretation_ar = 'عائد جيد على الأصول - إدارة فعالة للأصول'
                interpretation_en = 'Good return on assets - effective asset management'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif roa >= 3:
                interpretation_ar = 'عائد مقبول على الأصول - يحتاج لتحسين الكفاءة'
                interpretation_en = 'Acceptable return on assets - needs efficiency improvement'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif roa >= 0:
                interpretation_ar = 'عائد ضعيف على الأصول - ضعف في استخدام الأصول'
                interpretation_en = 'Poor return on assets - weak asset utilization'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'عائد سالب على الأصول - تدهور في قيمة الأصول'
                interpretation_en = 'Negative return on assets - deterioration in asset value'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(roa, 2),
                'percentage': f"{roa:.2f}%",
                'net_profit': round(net_profit, 2),
                'total_assets': round(total_assets, 2),
                'formula': '(الربح الصافي ÷ إجمالي الأصول) × 100',
                'formula_en': '(Net Profit ÷ Total Assets) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 15%',
                    'good': '8-14%',
                    'acceptable': '3-7%',
                    'poor': '0-2%',
                    'critical': '< 0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب العائد على الأصول: {str(e)}',
                'error_en': f'Error calculating return on assets: {str(e)}'
            }

    def return_on_equity(self, net_profit: float, shareholders_equity: float) -> Dict[str, Any]:
        """
        5. العائد على حقوق الملكية
        Return on Equity (ROE) = (Net Profit / Shareholders' Equity) × 100
        """
        try:
            if shareholders_equity == 0:
                return {
                    'value': None,
                    'formula': '(الربح الصافي ÷ حقوق الملكية) × 100',
                    'formula_en': '(Net Profit ÷ Shareholders\' Equity) × 100',
                    'interpretation_ar': 'لا يمكن حساب العائد - حقوق الملكية تساوي صفر',
                    'interpretation_en': 'Cannot calculate return - shareholders\' equity equals zero'
                }

            roe = (net_profit / shareholders_equity) * 100

            # تفسير النتائج
            if roe >= 20:
                interpretation_ar = 'عائد ممتاز على حقوق الملكية - قيمة عالية للمساهمين'
                interpretation_en = 'Excellent return on equity - high value for shareholders'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif roe >= 12:
                interpretation_ar = 'عائد جيد على حقوق الملكية - عائد مرضي للمساهمين'
                interpretation_en = 'Good return on equity - satisfactory return for shareholders'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif roe >= 6:
                interpretation_ar = 'عائد مقبول على حقوق الملكية - يحتاج للتحسين'
                interpretation_en = 'Acceptable return on equity - needs improvement'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif roe >= 0:
                interpretation_ar = 'عائد ضعيف على حقوق الملكية - عائد منخفض للمساهمين'
                interpretation_en = 'Poor return on equity - low return for shareholders'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'عائد سالب على حقوق الملكية - خسائر للمساهمين'
                interpretation_en = 'Negative return on equity - losses for shareholders'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(roe, 2),
                'percentage': f"{roe:.2f}%",
                'net_profit': round(net_profit, 2),
                'shareholders_equity': round(shareholders_equity, 2),
                'formula': '(الربح الصافي ÷ حقوق الملكية) × 100',
                'formula_en': '(Net Profit ÷ Shareholders\' Equity) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 20%',
                    'good': '12-19%',
                    'acceptable': '6-11%',
                    'poor': '0-5%',
                    'critical': '< 0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب العائد على حقوق الملكية: {str(e)}',
                'error_en': f'Error calculating return on equity: {str(e)}'
            }

    def return_on_investment(self, net_profit: float, total_investment: float) -> Dict[str, Any]:
        """
        6. العائد على الاستثمار
        Return on Investment (ROI) = (Net Profit / Total Investment) × 100
        """
        try:
            if total_investment == 0:
                return {
                    'value': None,
                    'formula': '(الربح الصافي ÷ إجمالي الاستثمار) × 100',
                    'formula_en': '(Net Profit ÷ Total Investment) × 100',
                    'interpretation_ar': 'لا يمكن حساب العائد - إجمالي الاستثمار يساوي صفر',
                    'interpretation_en': 'Cannot calculate return - total investment equals zero'
                }

            roi = (net_profit / total_investment) * 100

            # تفسير النتائج
            if roi >= 25:
                interpretation_ar = 'عائد ممتاز على الاستثمار - استثمار عالي المردود'
                interpretation_en = 'Excellent return on investment - highly profitable investment'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif roi >= 15:
                interpretation_ar = 'عائد جيد على الاستثمار - استثمار مربح'
                interpretation_en = 'Good return on investment - profitable investment'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif roi >= 8:
                interpretation_ar = 'عائد مقبول على الاستثمار - يحتاج لتحسين'
                interpretation_en = 'Acceptable return on investment - needs improvement'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif roi >= 0:
                interpretation_ar = 'عائد ضعيف على الاستثمار - ربحية منخفضة'
                interpretation_en = 'Poor return on investment - low profitability'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'عائد سالب على الاستثمار - خسارة في الاستثمار'
                interpretation_en = 'Negative return on investment - investment loss'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(roi, 2),
                'percentage': f"{roi:.2f}%",
                'net_profit': round(net_profit, 2),
                'total_investment': round(total_investment, 2),
                'formula': '(الربح الصافي ÷ إجمالي الاستثمار) × 100',
                'formula_en': '(Net Profit ÷ Total Investment) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 25%',
                    'good': '15-24%',
                    'acceptable': '8-14%',
                    'poor': '0-7%',
                    'critical': '< 0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب العائد على الاستثمار: {str(e)}',
                'error_en': f'Error calculating return on investment: {str(e)}'
            }

    def earnings_per_share(self, net_profit: float, number_of_shares: float) -> Dict[str, Any]:
        """
        7. ربحية السهم
        Earnings Per Share (EPS) = Net Profit / Number of Outstanding Shares
        """
        try:
            if number_of_shares == 0:
                return {
                    'value': None,
                    'formula': 'الربح الصافي ÷ عدد الأسهم المصدرة',
                    'formula_en': 'Net Profit ÷ Number of Outstanding Shares',
                    'interpretation_ar': 'لا يمكن حساب ربحية السهم - عدد الأسهم يساوي صفر',
                    'interpretation_en': 'Cannot calculate EPS - number of shares equals zero'
                }

            eps = net_profit / number_of_shares

            # تفسير النتائج (يعتمد على سعر السهم والصناعة)
            if eps >= 10:
                interpretation_ar = 'ربحية سهم ممتازة - عائد عالي للمساهمين'
                interpretation_en = 'Excellent earnings per share - high return for shareholders'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif eps >= 5:
                interpretation_ar = 'ربحية سهم جيدة - عائد مرضي للمساهمين'
                interpretation_en = 'Good earnings per share - satisfactory return for shareholders'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif eps >= 1:
                interpretation_ar = 'ربحية سهم مقبولة - يحتاج للتحسين'
                interpretation_en = 'Acceptable earnings per share - needs improvement'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif eps >= 0:
                interpretation_ar = 'ربحية سهم ضعيفة - عائد منخفض للمساهمين'
                interpretation_en = 'Poor earnings per share - low return for shareholders'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'خسارة للسهم - خسائر للمساهمين'
                interpretation_en = 'Loss per share - losses for shareholders'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(eps, 2),
                'net_profit': round(net_profit, 2),
                'number_of_shares': round(number_of_shares, 0),
                'formula': 'الربح الصافي ÷ عدد الأسهم المصدرة',
                'formula_en': 'Net Profit ÷ Number of Outstanding Shares',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 10',
                    'good': '5-9.99',
                    'acceptable': '1-4.99',
                    'poor': '0-0.99',
                    'critical': '< 0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب ربحية السهم: {str(e)}',
                'error_en': f'Error calculating earnings per share: {str(e)}'
            }

    def price_to_earnings_ratio(self, market_price_per_share: float, earnings_per_share: float) -> Dict[str, Any]:
        """
        8. نسبة السعر إلى الربحية
        Price to Earnings Ratio (P/E) = Market Price per Share / Earnings per Share
        """
        try:
            if earnings_per_share == 0:
                return {
                    'value': None,
                    'formula': 'سعر السهم السوقي ÷ ربحية السهم',
                    'formula_en': 'Market Price per Share ÷ Earnings per Share',
                    'interpretation_ar': 'لا يمكن حساب النسبة - ربحية السهم تساوي صفر',
                    'interpretation_en': 'Cannot calculate ratio - earnings per share equals zero'
                }

            pe_ratio = market_price_per_share / earnings_per_share

            # تفسير النتائج
            if pe_ratio >= 30:
                interpretation_ar = 'نسبة سعر/ربحية عالية - توقعات نمو عالية أو سهم مُقَيَّم أعلى من قيمته'
                interpretation_en = 'High P/E ratio - high growth expectations or overvalued stock'
                performance = 'مرتفع'
                risk_level = 'متوسط'
            elif pe_ratio >= 20:
                interpretation_ar = 'نسبة سعر/ربحية مرتفعة - توقعات نمو جيدة'
                interpretation_en = 'Elevated P/E ratio - good growth expectations'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif pe_ratio >= 10:
                interpretation_ar = 'نسبة سعر/ربحية معتدلة - تقييم معقول للسهم'
                interpretation_en = 'Moderate P/E ratio - reasonable stock valuation'
                performance = 'معتدل'
                risk_level = 'منخفض'
            elif pe_ratio >= 5:
                interpretation_ar = 'نسبة سعر/ربحية منخفضة - سهم مُقَيَّم أقل من قيمته أو مخاطر عالية'
                interpretation_en = 'Low P/E ratio - undervalued stock or high risks'
                performance = 'منخفض'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'نسبة سعر/ربحية منخفضة جداً - مخاطر عالية أو مشاكل في الشركة'
                interpretation_en = 'Very low P/E ratio - high risks or company problems'
                performance = 'منخفض جداً'
                risk_level = 'عالي'

            return {
                'value': round(pe_ratio, 2),
                'market_price_per_share': round(market_price_per_share, 2),
                'earnings_per_share': round(earnings_per_share, 2),
                'formula': 'سعر السهم السوقي ÷ ربحية السهم',
                'formula_en': 'Market Price per Share ÷ Earnings per Share',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'high': '≥ 30',
                    'elevated': '20-29',
                    'moderate': '10-19',
                    'low': '5-9',
                    'very_low': '< 5'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة السعر إلى الربحية: {str(e)}',
                'error_en': f'Error calculating price to earnings ratio: {str(e)}'
            }

    def dividend_yield(self, annual_dividends_per_share: float, market_price_per_share: float) -> Dict[str, Any]:
        """
        9. عائد التوزيعات
        Dividend Yield = (Annual Dividends per Share / Market Price per Share) × 100
        """
        try:
            if market_price_per_share == 0:
                return {
                    'value': None,
                    'formula': '(التوزيعات السنوية للسهم ÷ سعر السهم السوقي) × 100',
                    'formula_en': '(Annual Dividends per Share ÷ Market Price per Share) × 100',
                    'interpretation_ar': 'لا يمكن حساب عائد التوزيعات - سعر السهم يساوي صفر',
                    'interpretation_en': 'Cannot calculate dividend yield - market price equals zero'
                }

            dividend_yield = (annual_dividends_per_share / market_price_per_share) * 100

            # تفسير النتائج
            if dividend_yield >= 8:
                interpretation_ar = 'عائد توزيعات عالي جداً - دخل ممتاز أو مخاطر عالية'
                interpretation_en = 'Very high dividend yield - excellent income or high risks'
                performance = 'عالي جداً'
                risk_level = 'متوسط'
            elif dividend_yield >= 5:
                interpretation_ar = 'عائد توزيعات عالي - دخل جيد للمستثمرين'
                interpretation_en = 'High dividend yield - good income for investors'
                performance = 'عالي'
                risk_level = 'منخفض'
            elif dividend_yield >= 2:
                interpretation_ar = 'عائد توزيعات معتدل - دخل معقول'
                interpretation_en = 'Moderate dividend yield - reasonable income'
                performance = 'معتدل'
                risk_level = 'منخفض'
            elif dividend_yield > 0:
                interpretation_ar = 'عائد توزيعات منخفض - دخل محدود'
                interpretation_en = 'Low dividend yield - limited income'
                performance = 'منخفض'
                risk_level = 'منخفض'
            else:
                interpretation_ar = 'لا توجد توزيعات - لا دخل من التوزيعات'
                interpretation_en = 'No dividends - no income from dividends'
                performance = 'معدوم'
                risk_level = 'منخفض'

            return {
                'value': round(dividend_yield, 2),
                'percentage': f"{dividend_yield:.2f}%",
                'annual_dividends_per_share': round(annual_dividends_per_share, 2),
                'market_price_per_share': round(market_price_per_share, 2),
                'formula': '(التوزيعات السنوية للسهم ÷ سعر السهم السوقي) × 100',
                'formula_en': '(Annual Dividends per Share ÷ Market Price per Share) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'very_high': '≥ 8%',
                    'high': '5-7.99%',
                    'moderate': '2-4.99%',
                    'low': '0.01-1.99%',
                    'none': '0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب عائد التوزيعات: {str(e)}',
                'error_en': f'Error calculating dividend yield: {str(e)}'
            }

    def dividend_payout_ratio(self, dividends_paid: float, net_profit: float) -> Dict[str, Any]:
        """
        10. نسبة توزيع الأرباح
        Dividend Payout Ratio = (Dividends Paid / Net Profit) × 100
        """
        try:
            if net_profit == 0:
                return {
                    'value': None,
                    'formula': '(الأرباح الموزعة ÷ الربح الصافي) × 100',
                    'formula_en': '(Dividends Paid ÷ Net Profit) × 100',
                    'interpretation_ar': 'لا يمكن حساب نسبة التوزيع - الربح الصافي يساوي صفر',
                    'interpretation_en': 'Cannot calculate payout ratio - net profit equals zero'
                }

            payout_ratio = (dividends_paid / net_profit) * 100

            # تفسير النتائج
            if payout_ratio >= 80:
                interpretation_ar = 'نسبة توزيع عالية جداً - توزيع معظم الأرباح'
                interpretation_en = 'Very high payout ratio - distributing most profits'
                performance = 'عالي جداً'
                risk_level = 'متوسط'
            elif payout_ratio >= 60:
                interpretation_ar = 'نسبة توزيع عالية - توزيع جيد للأرباح'
                interpretation_en = 'High payout ratio - good profit distribution'
                performance = 'عالي'
                risk_level = 'منخفض'
            elif payout_ratio >= 30:
                interpretation_ar = 'نسبة توزيع معتدلة - توازن بين التوزيع والاحتفاظ'
                interpretation_en = 'Moderate payout ratio - balance between distribution and retention'
                performance = 'معتدل'
                risk_level = 'منخفض'
            elif payout_ratio > 0:
                interpretation_ar = 'نسبة توزيع منخفضة - احتفاظ بمعظم الأرباح للنمو'
                interpretation_en = 'Low payout ratio - retaining most profits for growth'
                performance = 'منخفض'
                risk_level = 'منخفض'
            else:
                interpretation_ar = 'لا توجد توزيعات - احتفاظ بجميع الأرباح'
                interpretation_en = 'No dividends - retaining all profits'
                performance = 'معدوم'
                risk_level = 'منخفض'

            # حساب نسبة الاحتفاظ
            retention_ratio = 100 - payout_ratio if payout_ratio >= 0 else 100

            return {
                'value': round(payout_ratio, 2),
                'percentage': f"{payout_ratio:.2f}%",
                'retention_ratio': round(retention_ratio, 2),
                'dividends_paid': round(dividends_paid, 2),
                'net_profit': round(net_profit, 2),
                'formula': '(الأرباح الموزعة ÷ الربح الصافي) × 100',
                'formula_en': '(Dividends Paid ÷ Net Profit) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'very_high': '≥ 80%',
                    'high': '60-79%',
                    'moderate': '30-59%',
                    'low': '1-29%',
                    'none': '0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب نسبة توزيع الأرباح: {str(e)}',
                'error_en': f'Error calculating dividend payout ratio: {str(e)}'
            }

    def ebitda_margin(self, ebitda: float, revenue: float) -> Dict[str, Any]:
        """
        11. هامش الأرباح قبل الفوائد والضرائب والإهلاك والاستهلاك
        EBITDA Margin = (EBITDA / Revenue) × 100
        """
        try:
            if revenue == 0:
                return {
                    'value': None,
                    'formula': '(الأرباح قبل الفوائد والضرائب والإهلاك ÷ الإيرادات) × 100',
                    'formula_en': '(EBITDA ÷ Revenue) × 100',
                    'interpretation_ar': 'لا يمكن حساب الهامش - الإيرادات تساوي صفر',
                    'interpretation_en': 'Cannot calculate margin - revenue equals zero'
                }

            margin = (ebitda / revenue) * 100

            # تفسير النتائج
            if margin >= 30:
                interpretation_ar = 'هامش EBITDA ممتاز - ربحية تشغيلية عالية جداً'
                interpretation_en = 'Excellent EBITDA margin - very high operational profitability'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif margin >= 20:
                interpretation_ar = 'هامش EBITDA جيد - ربحية تشغيلية قوية'
                interpretation_en = 'Good EBITDA margin - strong operational profitability'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif margin >= 10:
                interpretation_ar = 'هامش EBITDA مقبول - ربحية تشغيلية معتدلة'
                interpretation_en = 'Acceptable EBITDA margin - moderate operational profitability'
                performance = 'مقبول'
                risk_level = 'متوسط'
            elif margin >= 0:
                interpretation_ar = 'هامش EBITDA ضعيف - ربحية تشغيلية منخفضة'
                interpretation_en = 'Poor EBITDA margin - low operational profitability'
                performance = 'ضعيف'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'هامش EBITDA سالب - خسائر تشغيلية'
                interpretation_en = 'Negative EBITDA margin - operational losses'
                performance = 'خطير'
                risk_level = 'عالي جداً'

            return {
                'value': round(margin, 2),
                'percentage': f"{margin:.2f}%",
                'ebitda': round(ebitda, 2),
                'revenue': round(revenue, 2),
                'formula': '(الأرباح قبل الفوائد والضرائب والإهلاك ÷ الإيرادات) × 100',
                'formula_en': '(EBITDA ÷ Revenue) × 100',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'excellent': '≥ 30%',
                    'good': '20-29%',
                    'acceptable': '10-19%',
                    'poor': '0-9%',
                    'critical': '< 0%'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب هامش EBITDA: {str(e)}',
                'error_en': f'Error calculating EBITDA margin: {str(e)}'
            }

    def operating_leverage(self, percentage_change_ebit: float, percentage_change_sales: float) -> Dict[str, Any]:
        """
        12. الرافعة التشغيلية
        Operating Leverage = % Change in EBIT / % Change in Sales
        """
        try:
            if percentage_change_sales == 0:
                return {
                    'value': None,
                    'formula': 'النسبة المئوية للتغيير في الأرباح التشغيلية ÷ النسبة المئوية للتغيير في المبيعات',
                    'formula_en': '% Change in EBIT ÷ % Change in Sales',
                    'interpretation_ar': 'لا يمكن حساب الرافعة - التغيير في المبيعات يساوي صفر',
                    'interpretation_en': 'Cannot calculate leverage - change in sales equals zero'
                }

            leverage = percentage_change_ebit / percentage_change_sales

            # تفسير النتائج
            if leverage >= 3:
                interpretation_ar = 'رافعة تشغيلية عالية جداً - حساسية عالية للمبيعات'
                interpretation_en = 'Very high operating leverage - high sensitivity to sales'
                performance = 'عالي جداً'
                risk_level = 'عالي'
            elif leverage >= 2:
                interpretation_ar = 'رافعة تشغيلية عالية - حساسية جيدة للمبيعات'
                interpretation_en = 'High operating leverage - good sensitivity to sales'
                performance = 'عالي'
                risk_level = 'متوسط'
            elif leverage >= 1:
                interpretation_ar = 'رافعة تشغيلية معتدلة - استجابة متناسبة للمبيعات'
                interpretation_en = 'Moderate operating leverage - proportional response to sales'
                performance = 'معتدل'
                risk_level = 'منخفض'
            elif leverage > 0:
                interpretation_ar = 'رافعة تشغيلية منخفضة - استجابة ضعيفة للمبيعات'
                interpretation_en = 'Low operating leverage - weak response to sales'
                performance = 'منخفض'
                risk_level = 'منخفض'
            else:
                interpretation_ar = 'رافعة تشغيلية سالبة - استجابة عكسية'
                interpretation_en = 'Negative operating leverage - inverse response'
                performance = 'سالب'
                risk_level = 'عالي'

            return {
                'value': round(leverage, 2),
                'percentage_change_ebit': round(percentage_change_ebit, 2),
                'percentage_change_sales': round(percentage_change_sales, 2),
                'formula': 'النسبة المئوية للتغيير في الأرباح التشغيلية ÷ النسبة المئوية للتغيير في المبيعات',
                'formula_en': '% Change in EBIT ÷ % Change in Sales',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'benchmark': {
                    'very_high': '≥ 3',
                    'high': '2-2.99',
                    'moderate': '1-1.99',
                    'low': '0.01-0.99',
                    'negative': '≤ 0'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في حساب الرافعة التشغيلية: {str(e)}',
                'error_en': f'Error calculating operating leverage: {str(e)}'
            }

    def asset_turnover(self, revenue: float, average_total_assets: float) -> Dict[str, Any]:
        """
        13. معدل دوران الأصول
        Asset Turnover = Revenue / Average Total Assets
        """
        try:
            if average_total_assets == 0:
                return {
                    'value': None,
                    'formula': 'الإيرادات ÷ متوسط إجمالي الأصول',
                    'formula_en': 'Revenue ÷ Average Total Assets',
                    'interpretation_ar': 'لا يمكن حساب معدل الدوران - متوسط الأصول يساوي صفر',
                    'interpretation_en': 'Cannot calculate turnover - average assets equal zero'
                }

            turnover = revenue / average_total_assets

            # تفسير النتائج
            if turnover >= 2.5:
                interpretation_ar = 'معدل دوران أصول ممتاز - كفاءة عالية في استخدام الأصول'
                interpretation_en = 'Excellent asset turnover - high efficiency in asset utilization'
                performance = 'ممتاز'
                efficiency = 'عالية جداً'
                risk_level = 'منخفض'
            elif turnover >= 1.5:
                interpretation_ar = 'معدل دوران أصول جيد - كفاءة جيدة في استخدام الأصول'
                interpretation_en = 'Good asset turnover - good efficiency in asset utilization'
                performance = 'جيد'
                efficiency = 'جيدة'
                risk_level = 'منخفض'
            elif turnover >= 1.0:
                interpretation_ar = 'معدل دوران أصول مقبول - كفاءة معتدلة في استخدام الأصول'
                interpretation_en = 'Acceptable asset turnover - moderate efficiency in asset utilization'
                performance = 'مقبول'
                efficiency = 'معتدلة'
                risk_level = 'متوسط'
            elif turnover >= 0.5:
                interpretation_ar = 'معدل دوران أصول ضعيف - كفاءة منخفضة في استخدام الأصول'
                interpretation_en = 'Poor asset turnover - low efficiency in asset utilization'
                performance = 'ضعيف'
                efficiency = 'منخفضة'
                risk_level = 'عالي'
            else:
                interpretation_ar = 'معدل دوران أصول ضعيف جداً - كفاءة ضعيفة جداً في استخدام الأصول'
                interpretation_en = 'Very poor asset turnover - very low efficiency in asset utilization'
                performance = 'ضعيف جداً'
                efficiency = 'ضعيفة جداً'
                risk_level = 'عالي جداً'

            return {
                'value': round(turnover, 2),
                'revenue': round(revenue, 2),
                'average_total_assets': round(average_total_assets, 2),
                'formula': 'الإيرادات ÷ متوسط إجمالي الأصول',
                'formula_en': 'Revenue ÷ Average Total Assets',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'efficiency': efficiency,
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
                'error': f'خطأ في حساب معدل دوران الأصول: {str(e)}',
                'error_en': f'Error calculating asset turnover: {str(e)}'
            }

    def dupont_analysis(self, net_profit_margin: float, asset_turnover: float, equity_multiplier: float) -> Dict[str, Any]:
        """
        14. تحليل ديبونت
        ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
        """
        try:
            roe = net_profit_margin * asset_turnover * equity_multiplier

            # تحليل مكونات ديبونت
            profitability_analysis = "ممتاز" if net_profit_margin >= 15 else "جيد" if net_profit_margin >= 8 else "مقبول" if net_profit_margin >= 3 else "ضعيف"
            efficiency_analysis = "ممتاز" if asset_turnover >= 2 else "جيد" if asset_turnover >= 1.2 else "مقبول" if asset_turnover >= 0.8 else "ضعيف"
            leverage_analysis = "ممتاز" if 1.5 <= equity_multiplier <= 3 else "جيد" if 1.2 <= equity_multiplier <= 4 else "مقبول" if equity_multiplier <= 5 else "مخاطر عالية"

            # التفسير العام
            if roe >= 20:
                interpretation_ar = 'عائد ممتاز على حقوق الملكية وفقاً لتحليل ديبونت'
                interpretation_en = 'Excellent ROE according to DuPont analysis'
                performance = 'ممتاز'
                risk_level = 'منخفض'
            elif roe >= 12:
                interpretation_ar = 'عائد جيد على حقوق الملكية وفقاً لتحليل ديبونت'
                interpretation_en = 'Good ROE according to DuPont analysis'
                performance = 'جيد'
                risk_level = 'منخفض'
            elif roe >= 6:
                interpretation_ar = 'عائد مقبول على حقوق الملكية وفقاً لتحليل ديبونت'
                interpretation_en = 'Acceptable ROE according to DuPont analysis'
                performance = 'مقبول'
                risk_level = 'متوسط'
            else:
                interpretation_ar = 'عائد ضعيف على حقوق الملكية وفقاً لتحليل ديبونت'
                interpretation_en = 'Poor ROE according to DuPont analysis'
                performance = 'ضعيف'
                risk_level = 'عالي'

            return {
                'roe': round(roe, 2),
                'roe_percentage': f"{roe:.2f}%",
                'components': {
                    'net_profit_margin': {
                        'value': round(net_profit_margin, 2),
                        'analysis': profitability_analysis,
                        'description_ar': 'هامش الربح الصافي - مؤشر الربحية',
                        'description_en': 'Net Profit Margin - Profitability Indicator'
                    },
                    'asset_turnover': {
                        'value': round(asset_turnover, 2),
                        'analysis': efficiency_analysis,
                        'description_ar': 'معدل دوران الأصول - مؤشر الكفاءة',
                        'description_en': 'Asset Turnover - Efficiency Indicator'
                    },
                    'equity_multiplier': {
                        'value': round(equity_multiplier, 2),
                        'analysis': leverage_analysis,
                        'description_ar': 'مضاعف حقوق الملكية - مؤشر الرافعة المالية',
                        'description_en': 'Equity Multiplier - Financial Leverage Indicator'
                    }
                },
                'formula': 'هامش الربح الصافي × معدل دوران الأصول × مضاعف حقوق الملكية',
                'formula_en': 'Net Profit Margin × Asset Turnover × Equity Multiplier',
                'interpretation_ar': interpretation_ar,
                'interpretation_en': interpretation_en,
                'performance': performance,
                'risk_level': risk_level,
                'recommendations': {
                    'profitability': 'تحسين هامش الربح من خلال زيادة الإيرادات أو تقليل التكاليف' if profitability_analysis in ['ضعيف', 'مقبول'] else 'الحفاظ على مستوى الربحية الحالي',
                    'efficiency': 'تحسين كفاءة استخدام الأصول' if efficiency_analysis in ['ضعيف', 'مقبول'] else 'الحفاظ على مستوى الكفاءة الحالي',
                    'leverage': 'مراجعة هيكل التمويل' if leverage_analysis == 'مخاطر عالية' else 'هيكل التمويل مناسب'
                }
            }

        except Exception as e:
            return {
                'error': f'خطأ في تحليل ديبونت: {str(e)}',
                'error_en': f'Error in DuPont analysis: {str(e)}'
            }

    def comprehensive_profitability_analysis(self, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """تحليل شامل للربحية"""
        try:
            results = {}

            # 1. هامش الربح الإجمالي
            if all(k in financial_data for k in ['gross_profit', 'revenue']):
                results['gross_profit_margin'] = self.gross_profit_margin(
                    financial_data['gross_profit'],
                    financial_data['revenue']
                )

            # 2. هامش الربح التشغيلي
            if all(k in financial_data for k in ['operating_profit', 'revenue']):
                results['operating_profit_margin'] = self.operating_profit_margin(
                    financial_data['operating_profit'],
                    financial_data['revenue']
                )

            # 3. هامش الربح الصافي
            if all(k in financial_data for k in ['net_profit', 'revenue']):
                results['net_profit_margin'] = self.net_profit_margin(
                    financial_data['net_profit'],
                    financial_data['revenue']
                )

            # 4. العائد على الأصول
            if all(k in financial_data for k in ['net_profit', 'total_assets']):
                results['return_on_assets'] = self.return_on_assets(
                    financial_data['net_profit'],
                    financial_data['total_assets']
                )

            # 5. العائد على حقوق الملكية
            if all(k in financial_data for k in ['net_profit', 'shareholders_equity']):
                results['return_on_equity'] = self.return_on_equity(
                    financial_data['net_profit'],
                    financial_data['shareholders_equity']
                )

            # 6. العائد على الاستثمار
            if all(k in financial_data for k in ['net_profit', 'total_investment']):
                results['return_on_investment'] = self.return_on_investment(
                    financial_data['net_profit'],
                    financial_data['total_investment']
                )

            # 7. ربحية السهم
            if all(k in financial_data for k in ['net_profit', 'number_of_shares']):
                results['earnings_per_share'] = self.earnings_per_share(
                    financial_data['net_profit'],
                    financial_data['number_of_shares']
                )

            # 8. نسبة السعر إلى الربحية
            if all(k in financial_data for k in ['market_price_per_share', 'earnings_per_share']):
                results['price_to_earnings_ratio'] = self.price_to_earnings_ratio(
                    financial_data['market_price_per_share'],
                    financial_data['earnings_per_share']
                )

            # 9. عائد التوزيعات
            if all(k in financial_data for k in ['annual_dividends_per_share', 'market_price_per_share']):
                results['dividend_yield'] = self.dividend_yield(
                    financial_data['annual_dividends_per_share'],
                    financial_data['market_price_per_share']
                )

            # 10. نسبة توزيع الأرباح
            if all(k in financial_data for k in ['dividends_paid', 'net_profit']):
                results['dividend_payout_ratio'] = self.dividend_payout_ratio(
                    financial_data['dividends_paid'],
                    financial_data['net_profit']
                )

            # 11. هامش EBITDA
            if all(k in financial_data for k in ['ebitda', 'revenue']):
                results['ebitda_margin'] = self.ebitda_margin(
                    financial_data['ebitda'],
                    financial_data['revenue']
                )

            # 12. الرافعة التشغيلية
            if all(k in financial_data for k in ['percentage_change_ebit', 'percentage_change_sales']):
                results['operating_leverage'] = self.operating_leverage(
                    financial_data['percentage_change_ebit'],
                    financial_data['percentage_change_sales']
                )

            # 13. معدل دوران الأصول
            if all(k in financial_data for k in ['revenue', 'average_total_assets']):
                results['asset_turnover'] = self.asset_turnover(
                    financial_data['revenue'],
                    financial_data['average_total_assets']
                )

            # 14. تحليل ديبونت
            if all(k in financial_data for k in ['net_profit_margin_decimal', 'asset_turnover_value', 'equity_multiplier']):
                results['dupont_analysis'] = self.dupont_analysis(
                    financial_data['net_profit_margin_decimal'],
                    financial_data['asset_turnover_value'],
                    financial_data['equity_multiplier']
                )

            # تقييم عام للربحية
            overall_assessment = self._assess_overall_profitability(results)

            return {
                'individual_analyses': results,
                'overall_assessment': overall_assessment,
                'analysis_date': financial_data.get('analysis_date', 'غير محدد'),
                'company_name': financial_data.get('company_name', 'غير محدد')
            }

        except Exception as e:
            return {
                'error': f'خطأ في التحليل الشامل للربحية: {str(e)}',
                'error_en': f'Error in comprehensive profitability analysis: {str(e)}'
            }

    def _assess_overall_profitability(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم الوضع العام للربحية"""
        try:
            scores = []
            performances = []

            # جمع النقاط والأداء
            for analysis_name, analysis_result in results.items():
                if isinstance(analysis_result, dict) and 'performance' in analysis_result:
                    performances.append(analysis_result['performance'])

                    # تحويل الأداء إلى نقاط
                    if analysis_result['performance'] == 'ممتاز':
                        scores.append(5)
                    elif analysis_result['performance'] == 'جيد':
                        scores.append(4)
                    elif analysis_result['performance'] == 'مقبول':
                        scores.append(3)
                    elif analysis_result['performance'] == 'ضعيف':
                        scores.append(2)
                    else:  # خطير
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
                recommendation_ar = 'وضع الربحية ممتاز - الحفاظ على الأداء والنمو المستدام'
                recommendation_en = 'Excellent profitability - maintain performance and sustainable growth'
            elif average_score >= 3.5:
                overall_rating = 'جيد'
                overall_rating_en = 'Good'
                recommendation_ar = 'وضع الربحية جيد - البحث عن فرص تحسين إضافية'
                recommendation_en = 'Good profitability - seek additional improvement opportunities'
            elif average_score >= 2.5:
                overall_rating = 'مقبول'
                overall_rating_en = 'Acceptable'
                recommendation_ar = 'وضع الربحية يحتاج للتحسين - تطوير استراتيجيات الربحية'
                recommendation_en = 'Profitability needs improvement - develop profitability strategies'
            elif average_score >= 1.5:
                overall_rating = 'ضعيف'
                overall_rating_en = 'Poor'
                recommendation_ar = 'وضع الربحية ضعيف - إعادة هيكلة استراتيجية الأعمال'
                recommendation_en = 'Poor profitability - restructure business strategy'
            else:
                overall_rating = 'خطير'
                overall_rating_en = 'Critical'
                recommendation_ar = 'وضع الربحية خطير - إجراءات عاجلة وجذرية مطلوبة'
                recommendation_en = 'Critical profitability - urgent and radical actions required'

            return {
                'overall_score': round(average_score, 2),
                'overall_rating': overall_rating,
                'overall_rating_en': overall_rating_en,
                'total_analyses': len(scores),
                'performance_distribution': {
                    'ممتاز': performances.count('ممتاز'),
                    'جيد': performances.count('جيد'),
                    'مقبول': performances.count('مقبول'),
                    'ضعيف': performances.count('ضعيف'),
                    'خطير': performances.count('خطير')
                },
                'recommendation_ar': recommendation_ar,
                'recommendation_en': recommendation_en
            }

        except Exception as e:
            return {
                'error': f'خطأ في تقييم الوضع العام للربحية: {str(e)}',
                'error_en': f'Error in overall profitability assessment: {str(e)}'
            }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مثيل من فئة تحليل الربحية
    profitability_analyzer = ProfitabilityAnalysis()

    # بيانات مالية تجريبية
    sample_data = {
        'revenue': 1000000,
        'gross_profit': 400000,
        'operating_profit': 200000,
        'net_profit': 150000,
        'total_assets': 800000,
        'shareholders_equity': 500000,
        'total_investment': 600000,
        'number_of_shares': 100000,
        'market_price_per_share': 25,
        'earnings_per_share': 1.5,
        'annual_dividends_per_share': 0.5,
        'dividends_paid': 50000,
        'ebitda': 250000,
        'percentage_change_ebit': 15,
        'percentage_change_sales': 10,
        'average_total_assets': 750000,
        'net_profit_margin_decimal': 0.15,
        'asset_turnover_value': 1.33,
        'equity_multiplier': 1.6,
        'company_name': 'شركة المثال التجارية',
        'analysis_date': '2024-12-31'
    }

    # تشغيل التحليل الشامل
    comprehensive_results = profitability_analyzer.comprehensive_profitability_analysis(sample_data)

    print("=== تحليل الربحية الشامل ===")
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
            print(f"  الأداء: {result.get('performance', 'غير محدد')}")

    print(f"\n=== التقييم العام ===")
    overall = comprehensive_results.get('overall_assessment', {})
    print(f"التقييم العام: {overall.get('overall_rating', 'غير محدد')}")
    print(f"النقاط: {overall.get('overall_score', 0)}")
    print(f"التوصية: {overall.get('recommendation_ar', 'غير محدد')}")