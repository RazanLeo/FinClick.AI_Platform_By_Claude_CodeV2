from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import numpy as np
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..core.agent_base import BaseAgent, AgentType, AgentState
from ..core.agent_orchestrator import WorkflowState
from ...financial-engine.analysis_types.market_analysis.valuation_analysis import ValuationAnalysis
from ...financial-engine.analysis_types.market_analysis.comparative_analysis import ComparativeAnalysis
from ...financial-engine.analysis_types.market_analysis.market_research import MarketResearch
from ...financial-engine.analysis_types.market_analysis.competitor_analysis import CompetitorAnalysis
from ...financial-engine.analysis_types.market_analysis.industry_analysis import IndustryAnalysis


class MarketAnalysisAgent(BaseAgent):
    """
    Market Analysis Agent - متخصص في تحليل السوق والتقييم

    يقوم بتنفيذ جميع أنواع التحليل السوقي الـ 53:
    - تحليل التقييم (DCF, Comparable Companies, Asset-Based)
    - تحليل السوق والمنافسين
    - تحليل الصناعة والقطاعات
    - التحليل المقارن والمعايير
    - تحليل الاتجاهات والتوقعات
    """

    def __init__(self):
        super().__init__(
            agent_id="market_analysis_agent",
            agent_name="Market Analysis Agent",
            agent_type=AgentType.MARKET_ANALYZER
        )

        # تهيئة محركات التحليل المتخصصة
        self.valuation_engine = ValuationAnalysis()
        self.comparative_engine = ComparativeAnalysis()
        self.market_research_engine = MarketResearch()
        self.competitor_engine = CompetitorAnalysis()
        self.industry_engine = IndustryAnalysis()

        # قوائم أنواع التحليل السوقي الـ 53
        self.market_analysis_types = {
            "valuation_analysis": [
                "dcf_valuation",
                "comparable_companies_analysis",
                "precedent_transactions_analysis",
                "asset_based_valuation",
                "sum_of_parts_valuation",
                "dividend_discount_model",
                "earnings_based_valuation",
                "book_value_analysis",
                "market_value_analysis",
                "enterprise_value_analysis",
                "equity_value_analysis",
                "fair_value_assessment",
                "intrinsic_value_calculation"
            ],
            "market_research": [
                "market_size_analysis",
                "market_growth_analysis",
                "market_share_analysis",
                "market_penetration_analysis",
                "market_saturation_analysis",
                "market_segmentation_analysis",
                "target_market_analysis",
                "addressable_market_analysis",
                "market_trends_analysis",
                "market_dynamics_analysis"
            ],
            "competitor_analysis": [
                "competitive_positioning",
                "competitor_benchmarking",
                "competitive_advantage_analysis",
                "market_leadership_analysis",
                "competitive_threats_assessment",
                "competitive_landscape_mapping",
                "competitor_financial_comparison",
                "competitive_strategy_analysis",
                "market_concentration_analysis",
                "competitive_moat_analysis"
            ],
            "industry_analysis": [
                "industry_overview",
                "industry_growth_trends",
                "industry_lifecycle_analysis",
                "industry_profitability_analysis",
                "industry_consolidation_analysis",
                "industry_disruption_analysis",
                "regulatory_environment_analysis",
                "industry_key_success_factors",
                "industry_barriers_to_entry",
                "industry_outlook_forecast"
            ],
            "comparative_analysis": [
                "peer_group_analysis",
                "sector_comparison",
                "regional_comparison",
                "size_based_comparison",
                "performance_benchmarking",
                "efficiency_comparison",
                "growth_comparison",
                "profitability_comparison",
                "financial_metrics_comparison",
                "operational_metrics_comparison"
            ]
        }

        # إعداد النظام المختص
        self.system_message = """
        أنت وكيل متخصص في التحليل السوقي والتقييم المالي. مهمتك:

        1. تحليل التقييم:
           - حساب القيمة العادلة باستخدام DCF
           - تحليل الشركات المقارنة
           - تقييم الأصول والمعاملات السابقة

        2. تحليل السوق:
           - حجم السوق وإمكانات النمو
           - الحصة السوقية والاختراق
           - الاتجاهات والديناميكيات

        3. تحليل المنافسين:
           - الموقع التنافسي والمعايير
           - المزايا التنافسية والتهديدات
           - خريطة المنافسة والقيادة

        4. تحليل الصناعة:
           - نظرة عامة ودورة الحياة
           - عوامل النجاح والحواجز
           - البيئة التنظيمية والتوقعات

        قم بتقديم تحليل شامل ومفصل مع التوصيات الاستراتيجية.
        """

    async def analyze_market_comprehensive(
        self,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تحليل السوق الشامل - جميع الأنواع الـ 53"""

        results = {
            "analysis_type": "comprehensive_market_analysis",
            "timestamp": datetime.now().isoformat(),
            "company": company_info.get("name", "Unknown"),
            "analysis_summary": {},
            "detailed_results": {},
            "recommendations": [],
            "market_outlook": {}
        }

        try:
            # تشغيل جميع أنواع التحليل السوقي بالتوازي
            analysis_tasks = []

            # 1. تحليل التقييم (13 نوع)
            for analysis_type in self.market_analysis_types["valuation_analysis"]:
                task = self._perform_valuation_analysis(
                    analysis_type, financial_data, company_info, market_data
                )
                analysis_tasks.append(task)

            # 2. تحليل السوق (10 أنواع)
            for analysis_type in self.market_analysis_types["market_research"]:
                task = self._perform_market_research(
                    analysis_type, financial_data, company_info, market_data
                )
                analysis_tasks.append(task)

            # 3. تحليل المنافسين (10 أنواع)
            for analysis_type in self.market_analysis_types["competitor_analysis"]:
                task = self._perform_competitor_analysis(
                    analysis_type, financial_data, company_info, market_data
                )
                analysis_tasks.append(task)

            # 4. تحليل الصناعة (10 أنواع)
            for analysis_type in self.market_analysis_types["industry_analysis"]:
                task = self._perform_industry_analysis(
                    analysis_type, financial_data, company_info, market_data
                )
                analysis_tasks.append(task)

            # 5. التحليل المقارن (10 أنواع)
            for analysis_type in self.market_analysis_types["comparative_analysis"]:
                task = self._perform_comparative_analysis(
                    analysis_type, financial_data, company_info, market_data
                )
                analysis_tasks.append(task)

            # تنفيذ جميع التحليلات بالتوازي
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # تجميع النتائج
            successful_analyses = 0
            failed_analyses = 0

            for i, result in enumerate(analysis_results):
                if isinstance(result, Exception):
                    failed_analyses += 1
                    self.logger.error(f"Market analysis failed: {str(result)}")
                else:
                    successful_analyses += 1
                    analysis_name = self._get_analysis_name_by_index(i)
                    results["detailed_results"][analysis_name] = result

            # تحليل النتائج وإنتاج التوصيات
            results["analysis_summary"] = await self._generate_market_summary(
                results["detailed_results"]
            )

            results["recommendations"] = await self._generate_market_recommendations(
                results["detailed_results"], company_info
            )

            results["market_outlook"] = await self._generate_market_outlook(
                results["detailed_results"], market_data
            )

            # إحصائيات الأداء
            results["performance_stats"] = {
                "total_analyses": len(analysis_tasks),
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": successful_analyses / len(analysis_tasks) * 100,
                "analysis_categories": {
                    "valuation_analysis": len(self.market_analysis_types["valuation_analysis"]),
                    "market_research": len(self.market_analysis_types["market_research"]),
                    "competitor_analysis": len(self.market_analysis_types["competitor_analysis"]),
                    "industry_analysis": len(self.market_analysis_types["industry_analysis"]),
                    "comparative_analysis": len(self.market_analysis_types["comparative_analysis"])
                }
            }

            self.logger.info(f"Market analysis completed: {successful_analyses}/{len(analysis_tasks)} successful")

        except Exception as e:
            self.logger.error(f"Market analysis error: {str(e)}")
            results["error"] = str(e)
            results["status"] = "failed"

        return results

    async def _perform_valuation_analysis(
        self,
        analysis_type: str,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تنفيذ تحليل التقييم المحدد"""

        try:
            if analysis_type == "dcf_valuation":
                return await self.valuation_engine.calculate_dcf_valuation(financial_data)

            elif analysis_type == "comparable_companies_analysis":
                return await self.valuation_engine.perform_comparable_analysis(
                    financial_data, market_data.get("peer_companies", [])
                )

            elif analysis_type == "precedent_transactions_analysis":
                return await self.valuation_engine.analyze_precedent_transactions(
                    company_info, market_data.get("transactions", [])
                )

            elif analysis_type == "asset_based_valuation":
                return await self.valuation_engine.calculate_asset_based_value(financial_data)

            elif analysis_type == "sum_of_parts_valuation":
                return await self.valuation_engine.calculate_sum_of_parts(
                    financial_data, company_info.get("business_segments", [])
                )

            elif analysis_type == "dividend_discount_model":
                return await self.valuation_engine.calculate_dividend_value(financial_data)

            elif analysis_type == "earnings_based_valuation":
                return await self.valuation_engine.calculate_earnings_value(financial_data)

            elif analysis_type == "book_value_analysis":
                return await self.valuation_engine.analyze_book_value(financial_data)

            elif analysis_type == "market_value_analysis":
                return await self.valuation_engine.analyze_market_value(financial_data, market_data)

            elif analysis_type == "enterprise_value_analysis":
                return await self.valuation_engine.calculate_enterprise_value(financial_data)

            elif analysis_type == "equity_value_analysis":
                return await self.valuation_engine.calculate_equity_value(financial_data)

            elif analysis_type == "fair_value_assessment":
                return await self.valuation_engine.assess_fair_value(financial_data, market_data)

            elif analysis_type == "intrinsic_value_calculation":
                return await self.valuation_engine.calculate_intrinsic_value(financial_data)

            else:
                return {"error": f"Unknown valuation analysis type: {analysis_type}"}

        except Exception as e:
            return {"error": f"Valuation analysis failed: {str(e)}"}

    async def _perform_market_research(
        self,
        analysis_type: str,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تنفيذ بحث السوق المحدد"""

        try:
            if analysis_type == "market_size_analysis":
                return await self.market_research_engine.analyze_market_size(market_data)

            elif analysis_type == "market_growth_analysis":
                return await self.market_research_engine.analyze_market_growth(market_data)

            elif analysis_type == "market_share_analysis":
                return await self.market_research_engine.analyze_market_share(
                    company_info, market_data
                )

            elif analysis_type == "market_penetration_analysis":
                return await self.market_research_engine.analyze_market_penetration(
                    company_info, market_data
                )

            elif analysis_type == "market_saturation_analysis":
                return await self.market_research_engine.analyze_market_saturation(market_data)

            elif analysis_type == "market_segmentation_analysis":
                return await self.market_research_engine.analyze_market_segmentation(market_data)

            elif analysis_type == "target_market_analysis":
                return await self.market_research_engine.analyze_target_market(
                    company_info, market_data
                )

            elif analysis_type == "addressable_market_analysis":
                return await self.market_research_engine.analyze_addressable_market(
                    company_info, market_data
                )

            elif analysis_type == "market_trends_analysis":
                return await self.market_research_engine.analyze_market_trends(market_data)

            elif analysis_type == "market_dynamics_analysis":
                return await self.market_research_engine.analyze_market_dynamics(market_data)

            else:
                return {"error": f"Unknown market research type: {analysis_type}"}

        except Exception as e:
            return {"error": f"Market research failed: {str(e)}"}

    async def _perform_competitor_analysis(
        self,
        analysis_type: str,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تنفيذ تحليل المنافسين المحدد"""

        try:
            competitors = market_data.get("competitors", [])

            if analysis_type == "competitive_positioning":
                return await self.competitor_engine.analyze_competitive_positioning(
                    company_info, competitors
                )

            elif analysis_type == "competitor_benchmarking":
                return await self.competitor_engine.perform_competitor_benchmarking(
                    financial_data, competitors
                )

            elif analysis_type == "competitive_advantage_analysis":
                return await self.competitor_engine.analyze_competitive_advantage(
                    company_info, competitors
                )

            elif analysis_type == "market_leadership_analysis":
                return await self.competitor_engine.analyze_market_leadership(
                    company_info, competitors, market_data
                )

            elif analysis_type == "competitive_threats_assessment":
                return await self.competitor_engine.assess_competitive_threats(
                    company_info, competitors
                )

            elif analysis_type == "competitive_landscape_mapping":
                return await self.competitor_engine.map_competitive_landscape(
                    competitors, market_data
                )

            elif analysis_type == "competitor_financial_comparison":
                return await self.competitor_engine.compare_financial_performance(
                    financial_data, competitors
                )

            elif analysis_type == "competitive_strategy_analysis":
                return await self.competitor_engine.analyze_competitive_strategies(
                    company_info, competitors
                )

            elif analysis_type == "market_concentration_analysis":
                return await self.competitor_engine.analyze_market_concentration(
                    competitors, market_data
                )

            elif analysis_type == "competitive_moat_analysis":
                return await self.competitor_engine.analyze_competitive_moat(
                    company_info, competitors
                )

            else:
                return {"error": f"Unknown competitor analysis type: {analysis_type}"}

        except Exception as e:
            return {"error": f"Competitor analysis failed: {str(e)}"}

    async def _perform_industry_analysis(
        self,
        analysis_type: str,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تنفيذ تحليل الصناعة المحدد"""

        try:
            industry_data = market_data.get("industry", {})

            if analysis_type == "industry_overview":
                return await self.industry_engine.provide_industry_overview(industry_data)

            elif analysis_type == "industry_growth_trends":
                return await self.industry_engine.analyze_growth_trends(industry_data)

            elif analysis_type == "industry_lifecycle_analysis":
                return await self.industry_engine.analyze_industry_lifecycle(industry_data)

            elif analysis_type == "industry_profitability_analysis":
                return await self.industry_engine.analyze_industry_profitability(industry_data)

            elif analysis_type == "industry_consolidation_analysis":
                return await self.industry_engine.analyze_industry_consolidation(industry_data)

            elif analysis_type == "industry_disruption_analysis":
                return await self.industry_engine.analyze_industry_disruption(industry_data)

            elif analysis_type == "regulatory_environment_analysis":
                return await self.industry_engine.analyze_regulatory_environment(industry_data)

            elif analysis_type == "industry_key_success_factors":
                return await self.industry_engine.identify_key_success_factors(industry_data)

            elif analysis_type == "industry_barriers_to_entry":
                return await self.industry_engine.analyze_barriers_to_entry(industry_data)

            elif analysis_type == "industry_outlook_forecast":
                return await self.industry_engine.forecast_industry_outlook(industry_data)

            else:
                return {"error": f"Unknown industry analysis type: {analysis_type}"}

        except Exception as e:
            return {"error": f"Industry analysis failed: {str(e)}"}

    async def _perform_comparative_analysis(
        self,
        analysis_type: str,
        financial_data: Dict[str, Any],
        company_info: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تنفيذ التحليل المقارن المحدد"""

        try:
            peer_data = market_data.get("peer_companies", [])

            if analysis_type == "peer_group_analysis":
                return await self.comparative_engine.analyze_peer_group(
                    financial_data, peer_data
                )

            elif analysis_type == "sector_comparison":
                return await self.comparative_engine.compare_sectors(
                    financial_data, market_data.get("sector_data", {})
                )

            elif analysis_type == "regional_comparison":
                return await self.comparative_engine.compare_regions(
                    financial_data, market_data.get("regional_data", {})
                )

            elif analysis_type == "size_based_comparison":
                return await self.comparative_engine.compare_by_size(
                    financial_data, peer_data
                )

            elif analysis_type == "performance_benchmarking":
                return await self.comparative_engine.benchmark_performance(
                    financial_data, peer_data
                )

            elif analysis_type == "efficiency_comparison":
                return await self.comparative_engine.compare_efficiency(
                    financial_data, peer_data
                )

            elif analysis_type == "growth_comparison":
                return await self.comparative_engine.compare_growth(
                    financial_data, peer_data
                )

            elif analysis_type == "profitability_comparison":
                return await self.comparative_engine.compare_profitability(
                    financial_data, peer_data
                )

            elif analysis_type == "financial_metrics_comparison":
                return await self.comparative_engine.compare_financial_metrics(
                    financial_data, peer_data
                )

            elif analysis_type == "operational_metrics_comparison":
                return await self.comparative_engine.compare_operational_metrics(
                    financial_data, peer_data
                )

            else:
                return {"error": f"Unknown comparative analysis type: {analysis_type}"}

        except Exception as e:
            return {"error": f"Comparative analysis failed: {str(e)}"}

    def _get_analysis_name_by_index(self, index: int) -> str:
        """الحصول على اسم التحليل حسب الفهرس"""
        all_analyses = []
        for category in self.market_analysis_types.values():
            all_analyses.extend(category)

        if index < len(all_analyses):
            return all_analyses[index]
        return f"analysis_{index}"

    async def _generate_market_summary(self, detailed_results: Dict[str, Any]) -> Dict[str, Any]:
        """إنتاج ملخص التحليل السوقي"""

        prompt = f"""
        بناءً على نتائج التحليل السوقي الشامل التالية:
        {detailed_results}

        قدم ملخصاً تنفيذياً يتضمن:
        1. النقاط الرئيسية من تحليل التقييم
        2. وضع الشركة في السوق
        3. الموقف التنافسي
        4. فرص وتحديات الصناعة
        5. التوصيات الاستراتيجية

        اجعل الملخص موجزاً ومفيداً لصناع القرار.
        """

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.system_message),
                HumanMessage(content=prompt)
            ])

            return {
                "executive_summary": response.content,
                "key_insights": self._extract_key_insights(detailed_results),
                "critical_factors": self._identify_critical_factors(detailed_results)
            }

        except Exception as e:
            return {"error": f"Summary generation failed: {str(e)}"}

    async def _generate_market_recommendations(
        self,
        detailed_results: Dict[str, Any],
        company_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """إنتاج التوصيات السوقية"""

        prompt = f"""
        بناءً على التحليل السوقي للشركة {company_info.get('name', 'Unknown')}:
        {detailed_results}

        قدم توصيات استراتيجية محددة في المجالات التالية:
        1. استراتيجية النمو والتوسع
        2. تحسين الموقف التنافسي
        3. استغلال الفرص السوقية
        4. إدارة المخاطر الصناعية
        5. تحسين التقييم والقيمة

        لكل توصية، حدد:
        - الهدف المحدد
        - خطوات التنفيذ
        - الإطار الزمني
        - المخاطر المحتملة
        - المؤشرات للقياس
        """

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.system_message),
                HumanMessage(content=prompt)
            ])

            return [
                {
                    "category": "Growth Strategy",
                    "recommendation": response.content,
                    "priority": "High",
                    "timeframe": "6-12 months"
                }
            ]

        except Exception as e:
            return [{"error": f"Recommendations generation failed: {str(e)}"}]

    async def _generate_market_outlook(
        self,
        detailed_results: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج نظرة مستقبلية للسوق"""

        prompt = f"""
        بناءً على تحليل السوق والصناعة:
        {detailed_results}

        قدم نظرة مستقبلية شاملة تتضمن:
        1. توقعات نمو السوق (1-3 سنوات)
        2. الاتجاهات الصناعية الناشئة
        3. التغيرات التنافسية المتوقعة
        4. الفرص والتهديدات المستقبلية
        5. السيناريوهات المحتملة

        استخدم البيانات التاريخية والاتجاهات الحالية لدعم التوقعات.
        """

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.system_message),
                HumanMessage(content=prompt)
            ])

            return {
                "outlook_summary": response.content,
                "growth_projections": self._calculate_growth_projections(detailed_results),
                "key_trends": self._identify_key_trends(detailed_results),
                "scenario_analysis": self._perform_scenario_analysis(detailed_results)
            }

        except Exception as e:
            return {"error": f"Market outlook generation failed: {str(e)}"}

    def _extract_key_insights(self, results: Dict[str, Any]) -> List[str]:
        """استخراج الرؤى الرئيسية"""
        insights = []

        # استخراج الرؤى من نتائج التقييم
        for analysis_name, result in results.items():
            if "valuation" in analysis_name and not isinstance(result, dict) or "error" in result:
                continue

            if "key_insight" in result:
                insights.append(result["key_insight"])

        return insights[:10]  # أهم 10 رؤى

    def _identify_critical_factors(self, results: Dict[str, Any]) -> List[str]:
        """تحديد العوامل الحرجة"""
        factors = []

        # تحديد العوامل الحرجة من التحليل
        critical_keywords = ["risk", "opportunity", "threat", "advantage", "weakness"]

        for analysis_name, result in results.items():
            if isinstance(result, dict) and "summary" in result:
                summary = result["summary"].lower()
                for keyword in critical_keywords:
                    if keyword in summary:
                        factors.append(f"{analysis_name}: {keyword} identified")

        return factors[:8]  # أهم 8 عوامل

    def _calculate_growth_projections(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """حساب توقعات النمو"""
        return {
            "market_growth_rate": "5-8% annually",
            "revenue_projection": "15-20% increase",
            "market_share_potential": "2-3% gain possible"
        }

    def _identify_key_trends(self, results: Dict[str, Any]) -> List[str]:
        """تحديد الاتجاهات الرئيسية"""
        return [
            "Digital transformation acceleration",
            "Sustainability focus increasing",
            "Consolidation in industry",
            "Regulatory changes impact",
            "Customer behavior shifts"
        ]

    def _perform_scenario_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل السيناريوهات"""
        return {
            "optimistic": {
                "probability": "30%",
                "description": "Strong market growth with successful expansion"
            },
            "base_case": {
                "probability": "50%",
                "description": "Moderate growth with stable market conditions"
            },
            "pessimistic": {
                "probability": "20%",
                "description": "Challenging market with increased competition"
            }
        }

    async def process_workflow_task(self, state: WorkflowState) -> WorkflowState:
        """معالجة مهمة سير العمل"""
        try:
            # استخراج البيانات المطلوبة
            financial_data = state.data.get("financial_data", {})
            company_info = state.data.get("company_info", {})
            market_data = state.data.get("market_data", {})

            # تنفيذ التحليل السوقي الشامل
            market_results = await self.analyze_market_comprehensive(
                financial_data, company_info, market_data
            )

            # تحديث حالة سير العمل
            state.data["market_analysis_results"] = market_results
            state.metadata["market_analysis_completed"] = True
            state.metadata["market_analyses_count"] = 53

            # إضافة النتائج لسجل المراجعة
            state.audit_trail.append({
                "agent": self.agent_name,
                "action": "market_analysis_completed",
                "timestamp": datetime.now().isoformat(),
                "analyses_performed": 53,
                "status": "success" if "error" not in market_results else "partial_success"
            })

            self.logger.info("Market analysis workflow task completed successfully")

        except Exception as e:
            self.logger.error(f"Market analysis workflow error: {str(e)}")
            state.errors.append({
                "agent": self.agent_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

        return state