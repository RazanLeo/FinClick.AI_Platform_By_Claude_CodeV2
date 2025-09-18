"""
محرك التحليل المالي الرئيسي - Main Financial Analysis Engine
يدير ويربط جميع التحاليل المالية الـ 180
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json

# استيراد جميع فئات التحليل
from analysis_types.liquidity_analysis import LiquidityAnalysis
from analysis_types.profitability_analysis import ProfitabilityAnalysis
from analysis_types.efficiency_analysis import EfficiencyAnalysis
from analysis_types.leverage_analysis import LeverageAnalysis
from analysis_types.market_analysis import MarketAnalysis
from analysis_types.investment_analysis import InvestmentAnalysis

class FinancialAnalysisEngine:
    """محرك التحليل المالي الشامل"""

    def __init__(self):
        self.analysis_engines = {
            'liquidity': LiquidityAnalysis(),
            'profitability': ProfitabilityAnalysis(),
            'efficiency': EfficiencyAnalysis(),
            'leverage': LeverageAnalysis(),
            'market': MarketAnalysis(),
            'investment': InvestmentAnalysis()
        }

        # إعداد نظام السجلات
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # قاموس التحاليل المتاحة
        self.available_analyses = {
            # تحاليل السيولة (10)
            'current_ratio': {'engine': 'liquidity', 'method': 'current_ratio'},
            'quick_ratio': {'engine': 'liquidity', 'method': 'quick_ratio'},
            'cash_ratio': {'engine': 'liquidity', 'method': 'cash_ratio'},
            'working_capital': {'engine': 'liquidity', 'method': 'working_capital'},
            'operating_cash_flow_ratio': {'engine': 'liquidity', 'method': 'operating_cash_flow_ratio'},
            'days_inventory_outstanding': {'engine': 'liquidity', 'method': 'days_inventory_outstanding'},
            'days_payable_outstanding': {'engine': 'liquidity', 'method': 'days_payable_outstanding'},
            'working_capital_ratio': {'engine': 'liquidity', 'method': 'working_capital_ratio'},
            'cash_to_current_liabilities': {'engine': 'liquidity', 'method': 'cash_to_current_liabilities'},
            'liquidity_index': {'engine': 'liquidity', 'method': 'liquidity_index'},

            # تحاليل الربحية (15)
            'gross_profit_margin': {'engine': 'profitability', 'method': 'gross_profit_margin'},
            'operating_profit_margin': {'engine': 'profitability', 'method': 'operating_profit_margin'},
            'net_profit_margin': {'engine': 'profitability', 'method': 'net_profit_margin'},
            'return_on_assets': {'engine': 'profitability', 'method': 'return_on_assets'},
            'return_on_equity': {'engine': 'profitability', 'method': 'return_on_equity'},
            'return_on_investment': {'engine': 'profitability', 'method': 'return_on_investment'},
            'earnings_per_share': {'engine': 'profitability', 'method': 'earnings_per_share'},
            'price_to_earnings_ratio': {'engine': 'profitability', 'method': 'price_to_earnings_ratio'},
            'dividend_yield': {'engine': 'profitability', 'method': 'dividend_yield'},
            'dividend_payout_ratio': {'engine': 'profitability', 'method': 'dividend_payout_ratio'},
            'ebitda_margin': {'engine': 'profitability', 'method': 'ebitda_margin'},
            'operating_leverage': {'engine': 'profitability', 'method': 'operating_leverage'},
            'asset_turnover': {'engine': 'profitability', 'method': 'asset_turnover'},
            'dupont_analysis': {'engine': 'profitability', 'method': 'dupont_analysis'},

            # تحاليل الكفاءة (20)
            'inventory_turnover': {'engine': 'efficiency', 'method': 'inventory_turnover'},
            'accounts_receivable_turnover': {'engine': 'efficiency', 'method': 'accounts_receivable_turnover'},
            'accounts_payable_turnover': {'engine': 'efficiency', 'method': 'accounts_payable_turnover'},
            'total_asset_turnover': {'engine': 'efficiency', 'method': 'total_asset_turnover'},
            'fixed_asset_turnover': {'engine': 'efficiency', 'method': 'fixed_asset_turnover'},
            'working_capital_turnover': {'engine': 'efficiency', 'method': 'working_capital_turnover'},
            'cash_conversion_cycle': {'engine': 'efficiency', 'method': 'cash_conversion_cycle'},
            'receivables_to_sales_ratio': {'engine': 'efficiency', 'method': 'receivables_to_sales_ratio'},
            'inventory_to_sales_ratio': {'engine': 'efficiency', 'method': 'inventory_to_sales_ratio'},
            'operating_cycle': {'engine': 'efficiency', 'method': 'operating_cycle'},
            'employee_productivity': {'engine': 'efficiency', 'method': 'employee_productivity'},
            'cost_efficiency_ratio': {'engine': 'efficiency', 'method': 'cost_efficiency_ratio'},
            'sales_per_square_meter': {'engine': 'efficiency', 'method': 'sales_per_square_meter'},
            'marketing_efficiency_ratio': {'engine': 'efficiency', 'method': 'marketing_efficiency_ratio'},
            'operating_expense_ratio': {'engine': 'efficiency', 'method': 'operating_expense_ratio'},

            # تحاليل الرافعة المالية (15)
            'debt_to_equity_ratio': {'engine': 'leverage', 'method': 'debt_to_equity_ratio'},
            'debt_ratio': {'engine': 'leverage', 'method': 'debt_ratio'},
            'equity_multiplier': {'engine': 'leverage', 'method': 'equity_multiplier'},
            'times_interest_earned': {'engine': 'leverage', 'method': 'times_interest_earned'},
            'debt_service_coverage_ratio': {'engine': 'leverage', 'method': 'debt_service_coverage_ratio'},
            'long_term_debt_to_equity': {'engine': 'leverage', 'method': 'long_term_debt_to_equity'},
            'capitalization_ratio': {'engine': 'leverage', 'method': 'capitalization_ratio'},
            'financial_leverage_multiplier': {'engine': 'leverage', 'method': 'financial_leverage_multiplier'},
            'cash_coverage_ratio': {'engine': 'leverage', 'method': 'cash_coverage_ratio'},
            'degree_of_financial_leverage': {'engine': 'leverage', 'method': 'degree_of_financial_leverage'},

            # تحاليل السوق (25)
            'market_capitalization': {'engine': 'market', 'method': 'market_capitalization'},
            'book_value_per_share': {'engine': 'market', 'method': 'book_value_per_share'},
            'price_to_book_ratio': {'engine': 'market', 'method': 'price_to_book_ratio'},
            'market_to_book_ratio': {'engine': 'market', 'method': 'market_to_book_ratio'},
            'enterprise_value': {'engine': 'market', 'method': 'enterprise_value'},
            'ev_to_revenue': {'engine': 'market', 'method': 'ev_to_revenue'},
            'ev_to_ebitda': {'engine': 'market', 'method': 'ev_to_ebitda'},
            'price_to_sales_ratio': {'engine': 'market', 'method': 'price_to_sales_ratio'},
            'peg_ratio': {'engine': 'market', 'method': 'peg_ratio'},

            # تحاليل الاستثمار (21)
            'net_present_value': {'engine': 'investment', 'method': 'net_present_value'},
            'internal_rate_of_return': {'engine': 'investment', 'method': 'internal_rate_of_return'},
            'payback_period': {'engine': 'investment', 'method': 'payback_period'},
            'profitability_index': {'engine': 'investment', 'method': 'profitability_index'},
            'return_on_investment_simple': {'engine': 'investment', 'method': 'return_on_investment_simple'},
            'discounted_payback_period': {'engine': 'investment', 'method': 'discounted_payback_period'},
            'modified_internal_rate_of_return': {'engine': 'investment', 'method': 'modified_internal_rate_of_return'},
            'equivalent_annual_annuity': {'engine': 'investment', 'method': 'equivalent_annual_annuity'},
        }

    def run_single_analysis(self, analysis_type: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """تشغيل تحليل مالي واحد"""
        try:
            if analysis_type not in self.available_analyses:
                return {
                    'error': f'نوع التحليل غير مدعوم: {analysis_type}',
                    'available_types': list(self.available_analyses.keys())
                }

            config = self.available_analyses[analysis_type]
            engine = self.analysis_engines[config['engine']]
            method = getattr(engine, config['method'])

            # استخراج المعاملات المطلوبة للتحليل
            result = self._execute_analysis_method(method, financial_data)

            return {
                'analysis_type': analysis_type,
                'engine': config['engine'],
                'timestamp': datetime.now().isoformat(),
                'result': result
            }

        except Exception as e:
            self.logger.error(f"خطأ في تشغيل التحليل {analysis_type}: {str(e)}")
            return {
                'error': f'خطأ في تشغيل التحليل: {str(e)}',
                'analysis_type': analysis_type
            }

    def run_comprehensive_analysis(self, financial_data: Dict[str, Any],
                                 selected_categories: List[str] = None) -> Dict[str, Any]:
        """تشغيل تحليل مالي شامل"""
        try:
            if selected_categories is None:
                selected_categories = ['liquidity', 'profitability', 'efficiency', 'leverage', 'market', 'investment']

            results = {}

            # تشغيل التحاليل لكل فئة مختارة
            for category in selected_categories:
                if category in self.analysis_engines:
                    try:
                        # تشغيل التحليل الشامل للفئة
                        comprehensive_method = f'comprehensive_{category}_analysis'
                        engine = self.analysis_engines[category]

                        if hasattr(engine, comprehensive_method):
                            method = getattr(engine, comprehensive_method)
                            results[category] = method(financial_data)
                        else:
                            self.logger.warning(f"التحليل الشامل غير متوفر للفئة: {category}")

                    except Exception as e:
                        self.logger.error(f"خطأ في تحليل فئة {category}: {str(e)}")
                        results[category] = {'error': str(e)}

            # تجميع التقييم العام
            overall_assessment = self._create_overall_assessment(results)

            return {
                'analysis_date': datetime.now().isoformat(),
                'company_name': financial_data.get('company_name', 'غير محدد'),
                'categories_analyzed': selected_categories,
                'detailed_results': results,
                'overall_assessment': overall_assessment,
                'total_analyses': sum(len(cat_result.get('individual_analyses', {}))
                                    for cat_result in results.values()
                                    if isinstance(cat_result, dict))
            }

        except Exception as e:
            self.logger.error(f"خطأ في التحليل الشامل: {str(e)}")
            return {'error': f'خطأ في التحليل الشامل: {str(e)}'}

    def run_custom_analysis(self, analysis_list: List[str], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """تشغيل قائمة مخصصة من التحاليل"""
        try:
            results = {}

            for analysis_type in analysis_list:
                result = self.run_single_analysis(analysis_type, financial_data)
                results[analysis_type] = result

            return {
                'analysis_date': datetime.now().isoformat(),
                'company_name': financial_data.get('company_name', 'غير محدد'),
                'custom_analyses': results,
                'total_analyses': len(analysis_list)
            }

        except Exception as e:
            self.logger.error(f"خطأ في التحليل المخصص: {str(e)}")
            return {'error': f'خطأ في التحليل المخصص: {str(e)}'}

    def get_analysis_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج التوصيات من نتائج التحليل"""
        try:
            recommendations = {
                'priority_actions': [],
                'strengths': [],
                'weaknesses': [],
                'opportunities': [],
                'risks': []
            }

            # تحليل نتائج كل فئة
            for category, results in analysis_results.get('detailed_results', {}).items():
                if isinstance(results, dict) and 'overall_assessment' in results:
                    assessment = results['overall_assessment']

                    # استخراج التوصيات حسب الفئة
                    if 'recommendation_ar' in assessment:
                        recommendations['priority_actions'].append({
                            'category': category,
                            'recommendation': assessment['recommendation_ar'],
                            'priority': self._determine_priority(assessment)
                        })

            return recommendations

        except Exception as e:
            self.logger.error(f"خطأ في استخراج التوصيات: {str(e)}")
            return {'error': f'خطأ في استخراج التوصيات: {str(e)}'}

    def _execute_analysis_method(self, method, financial_data: Dict[str, Any]) -> Any:
        """تنفيذ دالة التحليل مع استخراج المعاملات المناسبة"""
        try:
            # استخراج أسماء المعاملات من دالة التحليل
            import inspect
            sig = inspect.signature(method)
            params = {}

            for param_name in sig.parameters.keys():
                if param_name in financial_data:
                    params[param_name] = financial_data[param_name]

            return method(**params)

        except Exception as e:
            return {'error': f'خطأ في تنفيذ التحليل: {str(e)}'}

    def _create_overall_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء تقييم عام لجميع التحاليل"""
        try:
            total_score = 0
            total_categories = 0
            risk_levels = []

            for category, result in results.items():
                if isinstance(result, dict) and 'overall_assessment' in result:
                    assessment = result['overall_assessment']
                    if 'overall_score' in assessment:
                        total_score += assessment['overall_score']
                        total_categories += 1

                    # جمع مستويات المخاطر
                    if 'risk_distribution' in assessment:
                        risk_dist = assessment['risk_distribution']
                        for risk_level, count in risk_dist.items():
                            risk_levels.extend([risk_level] * count)

            # حساب المتوسط العام
            overall_score = total_score / total_categories if total_categories > 0 else 0

            # تحديد التقييم العام
            if overall_score >= 4:
                overall_rating = 'ممتاز'
                overall_rating_en = 'Excellent'
            elif overall_score >= 3:
                overall_rating = 'جيد'
                overall_rating_en = 'Good'
            elif overall_score >= 2:
                overall_rating = 'مقبول'
                overall_rating_en = 'Acceptable'
            else:
                overall_rating = 'يحتاج تحسين'
                overall_rating_en = 'Needs Improvement'

            return {
                'overall_score': round(overall_score, 2),
                'overall_rating': overall_rating,
                'overall_rating_en': overall_rating_en,
                'categories_analyzed': total_categories,
                'risk_summary': self._summarize_risks(risk_levels),
                'financial_health': self._assess_financial_health(overall_score)
            }

        except Exception as e:
            return {'error': f'خطأ في إنشاء التقييم العام: {str(e)}'}

    def _summarize_risks(self, risk_levels: List[str]) -> Dict[str, Any]:
        """تلخيص مستويات المخاطر"""
        if not risk_levels:
            return {'total_risks': 0}

        risk_counts = {}
        for risk in risk_levels:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

        total_risks = len(risk_levels)
        high_risk_percentage = (risk_counts.get('عالي', 0) + risk_counts.get('عالي جداً', 0)) / total_risks * 100

        return {
            'total_risks': total_risks,
            'distribution': risk_counts,
            'high_risk_percentage': round(high_risk_percentage, 2),
            'overall_risk_level': self._determine_overall_risk(high_risk_percentage)
        }

    def _assess_financial_health(self, score: float) -> Dict[str, Any]:
        """تقييم الصحة المالية العامة"""
        if score >= 4:
            health_status = 'ممتازة'
            health_status_en = 'Excellent'
            description = 'الشركة تتمتع بصحة مالية ممتازة في جميع المجالات'
        elif score >= 3:
            health_status = 'جيدة'
            health_status_en = 'Good'
            description = 'الشركة تتمتع بصحة مالية جيدة مع بعض المجالات للتحسين'
        elif score >= 2:
            health_status = 'مقبولة'
            health_status_en = 'Acceptable'
            description = 'الشركة تحتاج لتحسينات في عدة مجالات مالية'
        else:
            health_status = 'ضعيفة'
            health_status_en = 'Poor'
            description = 'الشركة تواجه تحديات مالية كبيرة تحتاج لإجراءات عاجلة'

        return {
            'status': health_status,
            'status_en': health_status_en,
            'description': description,
            'score': score
        }

    def _determine_overall_risk(self, high_risk_percentage: float) -> str:
        """تحديد مستوى المخاطر العام"""
        if high_risk_percentage >= 50:
            return 'عالي'
        elif high_risk_percentage >= 25:
            return 'متوسط'
        else:
            return 'منخفض'

    def _determine_priority(self, assessment: Dict[str, Any]) -> str:
        """تحديد أولوية التوصية"""
        score = assessment.get('overall_score', 3)
        if score <= 1.5:
            return 'عاجل'
        elif score <= 2.5:
            return 'عالي'
        elif score <= 3.5:
            return 'متوسط'
        else:
            return 'منخفض'

    def get_available_analyses(self) -> Dict[str, Any]:
        """الحصول على قائمة بجميع التحاليل المتاحة"""
        analyses_by_category = {}

        for analysis_name, config in self.available_analyses.items():
            category = config['engine']
            if category not in analyses_by_category:
                analyses_by_category[category] = []
            analyses_by_category[category].append(analysis_name)

        return {
            'total_analyses': len(self.available_analyses),
            'categories': analyses_by_category,
            'engines': list(self.analysis_engines.keys())
        }

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء محرك التحليل المالي
    engine = FinancialAnalysisEngine()

    # بيانات مالية تجريبية شاملة
    sample_financial_data = {
        # بيانات عامة
        'company_name': 'شركة فين كليك التجريبية',
        'analysis_date': '2024-12-31',

        # بيانات الميزانية العمومية
        'current_assets': 500000,
        'current_liabilities': 300000,
        'inventory': 150000,
        'prepaid_expenses': 20000,
        'cash_and_equivalents': 100000,
        'short_term_investments': 50000,
        'accounts_receivable': 180000,
        'accounts_payable': 120000,
        'total_assets': 1200000,
        'total_debt': 400000,
        'shareholders_equity': 600000,
        'long_term_debt': 280000,

        # بيانات قائمة الدخل
        'revenue': 1000000,
        'gross_profit': 400000,
        'operating_profit': 200000,
        'net_profit': 150000,
        'cost_of_goods_sold': 600000,
        'operating_expenses': 200000,
        'ebitda': 250000,
        'ebit': 220000,
        'interest_expense': 20000,

        # بيانات السوق
        'shares_outstanding': 100000,
        'market_price_per_share': 25,
        'book_value_per_share': 6,
        'earnings_per_share': 1.5,
        'dividends_paid': 30000,

        # بيانات أخرى
        'number_of_employees': 50,
        'operating_cash_flow': 180000,
        'total_costs': 850000
    }

    print("=== محرك التحليل المالي الشامل - فين كليك ===\n")

    # 1. تشغيل تحليل شامل
    print("🔍 تشغيل التحليل المالي الشامل...")
    comprehensive_results = engine.run_comprehensive_analysis(sample_financial_data)

    if 'error' not in comprehensive_results:
        print(f"✅ تم تحليل {comprehensive_results['total_analyses']} مؤشر مالي بنجاح!")
        print(f"📊 التقييم العام: {comprehensive_results['overall_assessment']['overall_rating']}")
        print(f"🏥 الصحة المالية: {comprehensive_results['overall_assessment']['financial_health']['status']}")

        # 2. استخراج التوصيات
        print("\n📋 استخراج التوصيات...")
        recommendations = engine.get_analysis_recommendations(comprehensive_results)

        if recommendations.get('priority_actions'):
            print("🎯 أهم التوصيات:")
            for rec in recommendations['priority_actions'][:3]:
                print(f"   • {rec['category']}: {rec['recommendation']} (أولوية: {rec['priority']})")

    # 3. تشغيل تحليل مخصص
    print("\n🎛️ تشغيل تحاليل مخصصة...")
    custom_analyses = ['current_ratio', 'net_profit_margin', 'debt_to_equity_ratio', 'market_capitalization']
    custom_results = engine.run_custom_analysis(custom_analyses, sample_financial_data)

    if 'error' not in custom_results:
        print(f"✅ تم تشغيل {custom_results['total_analyses']} تحليل مخصص بنجاح!")

    # 4. عرض التحاليل المتاحة
    print("\n📚 التحاليل المتاحة:")
    available = engine.get_available_analyses()
    print(f"📈 إجمالي التحاليل المتاحة: {available['total_analyses']}")
    for category, analyses in available['categories'].items():
        print(f"   📁 {category}: {len(analyses)} تحليل")

    print("\n🎉 انتهى اختبار محرك التحليل المالي بنجاح!")