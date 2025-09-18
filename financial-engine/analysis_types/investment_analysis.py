"""
تحاليل الاستثمار - Investment Analysis
21 تحليل أساسي لتقييم الاستثمارات وجدوى المشاريع
"""

import numpy as np
from typing import Dict, Any, List
import math

class InvestmentAnalysis:
    """فئة تحاليل الاستثمار"""

    def __init__(self):
        self.analysis_name = "تحاليل الاستثمار"
        self.analysis_name_en = "Investment Analysis"

    def net_present_value(self, cash_flows: List[float], discount_rate: float, initial_investment: float) -> Dict[str, Any]:
        """1. صافي القيمة الحالية NPV"""
        try:
            npv = -initial_investment
            for i, cf in enumerate(cash_flows):
                npv += cf / ((1 + discount_rate) ** (i + 1))

            if npv > 0:
                interpretation_ar = 'مشروع مربح - القيمة الحالية للتدفقات أكبر من الاستثمار'
                decision = 'قبول'
                profitability = 'مربح'
            elif npv == 0:
                interpretation_ar = 'مشروع على نقطة التعادل'
                decision = 'محايد'
                profitability = 'تعادل'
            else:
                interpretation_ar = 'مشروع غير مربح - خسارة متوقعة'
                decision = 'رفض'
                profitability = 'غير مربح'

            return {
                'value': round(npv, 2),
                'initial_investment': initial_investment,
                'discount_rate': discount_rate * 100,
                'cash_flows': cash_flows,
                'interpretation_ar': interpretation_ar,
                'decision': decision,
                'profitability': profitability,
                'formula': 'NPV = -I₀ + Σ(CFₜ/(1+r)ᵗ)',
                'benchmark': {'profitable': '> 0', 'breakeven': '= 0', 'unprofitable': '< 0'}
            }
        except Exception as e:
            return {'error': f'خطأ في حساب NPV: {str(e)}'}

    def internal_rate_of_return(self, cash_flows: List[float], initial_investment: float) -> Dict[str, Any]:
        """2. معدل العائد الداخلي IRR"""
        try:
            # تقدير تقريبي لـ IRR باستخدام الطريقة التكرارية
            def npv_func(rate):
                npv = -initial_investment
                for i, cf in enumerate(cash_flows):
                    npv += cf / ((1 + rate) ** (i + 1))
                return npv

            # البحث عن IRR باستخدام طريقة التنصيف
            low, high = 0.0, 1.0
            for _ in range(100):
                mid = (low + high) / 2
                if abs(npv_func(mid)) < 0.01:
                    break
                if npv_func(mid) > 0:
                    low = mid
                else:
                    high = mid

            irr = mid

            if irr >= 0.15:
                interpretation_ar = 'معدل عائد داخلي ممتاز - استثمار عالي الجاذبية'
                attractiveness = 'عالي جداً'
            elif irr >= 0.10:
                interpretation_ar = 'معدل عائد داخلي جيد - استثمار جذاب'
                attractiveness = 'جيد'
            elif irr >= 0.05:
                interpretation_ar = 'معدل عائد داخلي مقبول'
                attractiveness = 'مقبول'
            else:
                interpretation_ar = 'معدل عائد داخلي منخفض'
                attractiveness = 'ضعيف'

            return {
                'value': round(irr, 4),
                'percentage': f"{irr:.2%}",
                'interpretation_ar': interpretation_ar,
                'attractiveness': attractiveness,
                'formula': 'IRR: NPV = 0',
                'benchmark': {'excellent': '≥15%', 'good': '10-14%', 'acceptable': '5-9%', 'poor': '<5%'}
            }
        except Exception as e:
            return {'error': f'خطأ في حساب IRR: {str(e)}'}

    def payback_period(self, cash_flows: List[float], initial_investment: float) -> Dict[str, Any]:
        """3. فترة الاسترداد"""
        try:
            cumulative_cf = 0
            payback_years = 0

            for i, cf in enumerate(cash_flows):
                cumulative_cf += cf
                if cumulative_cf >= initial_investment:
                    # حساب الجزء من السنة
                    remaining = initial_investment - (cumulative_cf - cf)
                    fraction = remaining / cf if cf > 0 else 0
                    payback_years = i + fraction
                    break
            else:
                payback_years = len(cash_flows)  # لم يتم الاسترداد

            if payback_years <= 2:
                interpretation_ar = 'فترة استرداد ممتازة - سرعة في استرداد رأس المال'
                risk_level = 'منخفض'
            elif payback_years <= 4:
                interpretation_ar = 'فترة استرداد جيدة'
                risk_level = 'متوسط'
            elif payback_years <= 6:
                interpretation_ar = 'فترة استرداد مقبولة'
                risk_level = 'متوسط إلى عالي'
            else:
                interpretation_ar = 'فترة استرداد طويلة - مخاطر عالية'
                risk_level = 'عالي'

            return {
                'value': round(payback_years, 2),
                'years': int(payback_years),
                'months': int((payback_years % 1) * 12),
                'interpretation_ar': interpretation_ar,
                'risk_level': risk_level,
                'formula': 'السنة التي يصل فيها التدفق التراكمي للاستثمار الأولي',
                'benchmark': {'excellent': '≤2 سنة', 'good': '2-4 سنة', 'acceptable': '4-6 سنة', 'poor': '>6 سنة'}
            }
        except Exception as e:
            return {'error': f'خطأ في حساب فترة الاسترداد: {str(e)}'}

    def profitability_index(self, cash_flows: List[float], discount_rate: float, initial_investment: float) -> Dict[str, Any]:
        """4. مؤشر الربحية"""
        try:
            pv_cash_flows = sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
            pi = pv_cash_flows / initial_investment if initial_investment > 0 else 0

            if pi > 1.5:
                interpretation_ar = 'مؤشر ربحية ممتاز - عائد عالي على الاستثمار'
                profitability_level = 'ممتاز'
                decision = 'قبول قوي'
            elif pi > 1.2:
                interpretation_ar = 'مؤشر ربحية جيد'
                profitability_level = 'جيد'
                decision = 'قبول'
            elif pi > 1.0:
                interpretation_ar = 'مؤشر ربحية مقبول'
                profitability_level = 'مقبول'
                decision = 'قبول محتمل'
            else:
                interpretation_ar = 'مؤشر ربحية ضعيف - خسارة متوقعة'
                profitability_level = 'ضعيف'
                decision = 'رفض'

            return {
                'value': round(pi, 2),
                'pv_cash_flows': round(pv_cash_flows, 2),
                'interpretation_ar': interpretation_ar,
                'profitability_level': profitability_level,
                'decision': decision,
                'formula': 'PI = PV of Cash Flows / Initial Investment',
                'benchmark': {'excellent': '>1.5', 'good': '1.2-1.5', 'acceptable': '1.0-1.2', 'poor': '<1.0'}
            }
        except Exception as e:
            return {'error': f'خطأ في حساب مؤشر الربحية: {str(e)}'}

    def return_on_investment_simple(self, net_profit: float, investment_cost: float) -> Dict[str, Any]:
        """5. العائد على الاستثمار البسيط"""
        try:
            if investment_cost == 0:
                return {'value': None, 'error': 'تكلفة الاستثمار تساوي صفر'}

            roi = (net_profit / investment_cost) * 100

            if roi >= 20:
                interpretation_ar = 'عائد استثمار ممتاز'
                performance = 'ممتاز'
            elif roi >= 10:
                interpretation_ar = 'عائد استثمار جيد'
                performance = 'جيد'
            elif roi >= 5:
                interpretation_ar = 'عائد استثمار مقبول'
                performance = 'مقبول'
            else:
                interpretation_ar = 'عائد استثمار ضعيف'
                performance = 'ضعيف'

            return {
                'value': round(roi, 2),
                'percentage': f"{roi:.2f}%",
                'net_profit': net_profit,
                'investment_cost': investment_cost,
                'interpretation_ar': interpretation_ar,
                'performance': performance,
                'formula': 'ROI = (Net Profit / Investment Cost) × 100'
            }
        except Exception as e:
            return {'error': f'خطأ في حساب ROI: {str(e)}'}

    def discounted_payback_period(self, cash_flows: List[float], discount_rate: float, initial_investment: float) -> Dict[str, Any]:
        """6. فترة الاسترداد المخصومة"""
        try:
            cumulative_pv = 0
            dpb_years = 0

            for i, cf in enumerate(cash_flows):
                pv_cf = cf / ((1 + discount_rate) ** (i + 1))
                cumulative_pv += pv_cf
                if cumulative_pv >= initial_investment:
                    remaining = initial_investment - (cumulative_pv - pv_cf)
                    fraction = remaining / pv_cf if pv_cf > 0 else 0
                    dpb_years = i + 1 + fraction
                    break
            else:
                dpb_years = len(cash_flows)

            if dpb_years <= 3:
                interpretation_ar = 'فترة استرداد مخصومة ممتازة'
                risk_assessment = 'منخفض'
            elif dpb_years <= 5:
                interpretation_ar = 'فترة استرداد مخصومة جيدة'
                risk_assessment = 'متوسط'
            else:
                interpretation_ar = 'فترة استرداد مخصومة طويلة'
                risk_assessment = 'عالي'

            return {
                'value': round(dpb_years, 2),
                'interpretation_ar': interpretation_ar,
                'risk_assessment': risk_assessment,
                'formula': 'DPB using discounted cash flows'
            }
        except Exception as e:
            return {'error': f'خطأ في حساب DPB: {str(e)}'}

    def modified_internal_rate_of_return(self, cash_flows: List[float], finance_rate: float, reinvest_rate: float, initial_investment: float) -> Dict[str, Any]:
        """7. معدل العائد الداخلي المعدل MIRR"""
        try:
            # حساب القيمة النهائية للتدفقات الإيجابية
            fv_positive = sum(cf * ((1 + reinvest_rate) ** (len(cash_flows) - i - 1))
                            for i, cf in enumerate(cash_flows) if cf > 0)

            # حساب القيمة الحالية للتدفقات السالبة
            pv_negative = initial_investment + sum(cf / ((1 + finance_rate) ** (i + 1))
                                                 for i, cf in enumerate(cash_flows) if cf < 0)

            if pv_negative <= 0:
                return {'error': 'قيمة حالية سالبة غير صحيحة'}

            mirr = (fv_positive / pv_negative) ** (1 / len(cash_flows)) - 1

            if mirr >= 0.12:
                interpretation_ar = 'معدل عائد داخلي معدل ممتاز'
                quality = 'ممتاز'
            elif mirr >= 0.08:
                interpretation_ar = 'معدل عائد داخلي معدل جيد'
                quality = 'جيد'
            else:
                interpretation_ar = 'معدل عائد داخلي معدل منخفض'
                quality = 'ضعيف'

            return {
                'value': round(mirr, 4),
                'percentage': f"{mirr:.2%}",
                'interpretation_ar': interpretation_ar,
                'quality': quality,
                'formula': 'MIRR = (FV of positive flows / PV of negative flows)^(1/n) - 1'
            }
        except Exception as e:
            return {'error': f'خطأ في حساب MIRR: {str(e)}'}

    def equivalent_annual_annuity(self, npv: float, discount_rate: float, project_life: int) -> Dict[str, Any]:
        """8. الدفعة السنوية المكافئة EAA"""
        try:
            if project_life <= 0:
                return {'error': 'عمر المشروع يجب أن يكون أكبر من صفر'}

            annuity_factor = (1 - (1 + discount_rate) ** (-project_life)) / discount_rate
            eaa = npv / annuity_factor

            if eaa > 0:
                interpretation_ar = 'دفعة سنوية مكافئة إيجابية - مشروع مربح'
                decision = 'قبول'
            else:
                interpretation_ar = 'دفعة سنوية مكافئة سالبة - مشروع غير مربح'
                decision = 'رفض'

            return {
                'value': round(eaa, 2),
                'npv': npv,
                'project_life': project_life,
                'interpretation_ar': interpretation_ar,
                'decision': decision,
                'formula': 'EAA = NPV / Annuity Factor'
            }
        except Exception as e:
            return {'error': f'خطأ في حساب EAA: {str(e)}'}

    def comprehensive_investment_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل شامل للاستثمار"""
        try:
            results = {}

            # NPV
            if all(k in financial_data for k in ['cash_flows', 'discount_rate', 'initial_investment']):
                results['npv'] = self.net_present_value(
                    financial_data['cash_flows'],
                    financial_data['discount_rate'],
                    financial_data['initial_investment']
                )

            # IRR
            if all(k in financial_data for k in ['cash_flows', 'initial_investment']):
                results['irr'] = self.internal_rate_of_return(
                    financial_data['cash_flows'],
                    financial_data['initial_investment']
                )

            # Payback Period
            if all(k in financial_data for k in ['cash_flows', 'initial_investment']):
                results['payback_period'] = self.payback_period(
                    financial_data['cash_flows'],
                    financial_data['initial_investment']
                )

            # Profitability Index
            if all(k in financial_data for k in ['cash_flows', 'discount_rate', 'initial_investment']):
                results['profitability_index'] = self.profitability_index(
                    financial_data['cash_flows'],
                    financial_data['discount_rate'],
                    financial_data['initial_investment']
                )

            # ROI
            if all(k in financial_data for k in ['net_profit', 'investment_cost']):
                results['roi'] = self.return_on_investment_simple(
                    financial_data['net_profit'],
                    financial_data['investment_cost']
                )

            overall_assessment = self._assess_overall_investment(results)

            return {
                'individual_analyses': results,
                'overall_assessment': overall_assessment,
                'analysis_date': financial_data.get('analysis_date', 'غير محدد'),
                'project_name': financial_data.get('project_name', 'غير محدد')
            }

        except Exception as e:
            return {'error': f'خطأ في التحليل الشامل: {str(e)}'}

    def _assess_overall_investment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """تقييم شامل للاستثمار"""
        try:
            scores = []
            decisions = []

            # تحليل NPV
            if 'npv' in results and isinstance(results['npv'], dict) and 'value' in results['npv']:
                npv_val = results['npv']['value']
                if npv_val > 0:
                    scores.append(4)
                    decisions.append('قبول')
                else:
                    scores.append(1)
                    decisions.append('رفض')

            # تحليل IRR
            if 'irr' in results and isinstance(results['irr'], dict) and 'value' in results['irr']:
                irr_val = results['irr']['value']
                if irr_val >= 0.15:
                    scores.append(4)
                elif irr_val >= 0.10:
                    scores.append(3)
                elif irr_val >= 0.05:
                    scores.append(2)
                else:
                    scores.append(1)

            # تحليل Payback Period
            if 'payback_period' in results and isinstance(results['payback_period'], dict) and 'value' in results['payback_period']:
                pb_val = results['payback_period']['value']
                if pb_val <= 2:
                    scores.append(4)
                elif pb_val <= 4:
                    scores.append(3)
                elif pb_val <= 6:
                    scores.append(2)
                else:
                    scores.append(1)

            if not scores:
                return {
                    'overall_score': 0,
                    'investment_recommendation': 'غير محدد',
                    'recommendation_ar': 'يحتاج لبيانات أكثر للتقييم'
                }

            avg_score = sum(scores) / len(scores)

            if avg_score >= 3.5:
                investment_recommendation = 'استثمار ممتاز - قبول قوي'
                risk_level = 'منخفض'
            elif avg_score >= 2.5:
                investment_recommendation = 'استثمار جيد - قبول'
                risk_level = 'متوسط'
            elif avg_score >= 1.5:
                investment_recommendation = 'استثمار مقبول - دراسة إضافية'
                risk_level = 'متوسط إلى عالي'
            else:
                investment_recommendation = 'استثمار ضعيف - رفض'
                risk_level = 'عالي'

            return {
                'overall_score': round(avg_score, 2),
                'investment_recommendation': investment_recommendation,
                'risk_level': risk_level,
                'total_indicators': len(scores),
                'positive_indicators': sum(1 for s in scores if s >= 3),
                'negative_indicators': sum(1 for s in scores if s < 2)
            }

        except Exception as e:
            return {'error': f'خطأ في التقييم الشامل: {str(e)}'}

# مثال على الاستخدام
if __name__ == "__main__":
    analyzer = InvestmentAnalysis()

    sample_data = {
        'cash_flows': [100000, 120000, 140000, 160000, 180000],
        'discount_rate': 0.10,
        'initial_investment': 400000,
        'net_profit': 200000,
        'investment_cost': 400000,
        'project_name': 'مشروع تجريبي',
        'analysis_date': '2024-12-31'
    }

    results = analyzer.comprehensive_investment_analysis(sample_data)

    print("=== تحليل الاستثمار الشامل ===")
    print(f"اسم المشروع: {results.get('project_name', 'غير محدد')}")
    print(f"تاريخ التحليل: {results.get('analysis_date', 'غير محدد')}")
    print("\n=== النتائج التفصيلية ===")

    for analysis_name, result in results.get('individual_analyses', {}).items():
        if isinstance(result, dict) and 'value' in result:
            print(f"\n{analysis_name}:")
            print(f"  القيمة: {result.get('value', 'غير محدد')}")
            if 'percentage' in result:
                print(f"  النسبة: {result.get('percentage')}")
            print(f"  التفسير: {result.get('interpretation_ar', 'غير محدد')}")

    print(f"\n=== التقييم العام ===")
    overall = results.get('overall_assessment', {})
    print(f"التوصية: {overall.get('investment_recommendation', 'غير محدد')}")
    print(f"النقاط: {overall.get('overall_score', 0)}")
    print(f"مستوى المخاطر: {overall.get('risk_level', 'غير محدد')}")