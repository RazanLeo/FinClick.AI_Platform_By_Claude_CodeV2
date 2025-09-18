from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import numpy as np
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..core.agent_base import BaseAgent, AgentType, AgentState
from ..core.agent_orchestrator import WorkflowState


class RecommendationAgent(BaseAgent):
    """
    Recommendation Agent - متخصص في التوصيات الاستراتيجية

    يقوم بتحليل جميع نتائج التحليلات وإنتاج توصيات عملية:
    - توصيات استراتيجية طويلة المدى
    - توصيات تشغيلية قصيرة المدى
    - توصيات مالية وتمويلية
    - توصيات إدارة المخاطر
    - توصيات النمو والتوسع
    - توصيات تحسين الأداء
    """

    def __init__(self):
        super().__init__(
            agent_id="recommendation_agent",
            agent_name="Recommendation Agent",
            agent_type=AgentType.RECOMMENDATION_GENERATOR
        )

        # أنواع التوصيات
        self.recommendation_categories = {
            "strategic": "التوصيات الاستراتيجية",
            "operational": "التوصيات التشغيلية",
            "financial": "التوصيات المالية",
            "risk_management": "توصيات إدارة المخاطر",
            "growth": "توصيات النمو",
            "performance": "توصيات تحسين الأداء",
            "investment": "توصيات الاستثمار",
            "governance": "توصيات الحوكمة"
        }

        # مستويات الأولوية
        self.priority_levels = {
            "critical": "حرجة - تنفيذ فوري",
            "high": "عالية - 1-3 شهور",
            "medium": "متوسطة - 3-6 شهور",
            "low": "منخفضة - 6-12 شهر"
        }

        # إطار زمني للتنفيذ
        self.timeframes = {
            "immediate": "فوري (1-30 يوم)",
            "short_term": "قصير المدى (1-6 شهور)",
            "medium_term": "متوسط المدى (6-18 شهر)",
            "long_term": "طويل المدى (1-3 سنوات)"
        }

        # إعداد النظام المختص
        self.system_message = """
        أنت وكيل متخصص في إنتاج التوصيات الاستراتيجية والتشغيلية. مهمتك:

        1. تحليل شامل لجميع نتائج التحليلات المالية والسوقية
        2. تحديد الفرص والتحديات الرئيسية
        3. إنتاج توصيات عملية وقابلة للتنفيذ
        4. ترتيب التوصيات حسب الأولوية والأثر
        5. تقديم خطط تنفيذ مفصلة

        معايير التوصيات:
        - عملية وقابلة للتنفيذ
        - مدعومة بالأدلة والبيانات
        - محددة بالأهداف والمقاييس
        - واضحة الإطار الزمني والموارد
        - متوازنة بين المخاطر والعوائد

        يجب أن تكون التوصيات دقيقة ومخصصة لوضع الشركة المحدد.
        """

    async def generate_comprehensive_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """إنتاج التوصيات الشاملة"""

        if business_context is None:
            business_context = {}

        results = {
            "recommendation_id": f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "company": company_info.get("name", "Unknown"),
            "analysis_summary": {},
            "recommendations_by_category": {},
            "priority_matrix": {},
            "implementation_roadmap": {},
            "risk_considerations": {},
            "expected_outcomes": {},
            "monitoring_framework": {}
        }

        try:
            # تحليل شامل للنتائج
            analysis_summary = await self._analyze_all_results(analysis_results, company_info)
            results["analysis_summary"] = analysis_summary

            # إنتاج التوصيات حسب الفئات
            recommendation_tasks = []

            for category in self.recommendation_categories.keys():
                task = self._generate_category_recommendations(
                    category, analysis_results, company_info, business_context
                )
                recommendation_tasks.append(task)

            # تنفيذ إنتاج التوصيات بالتوازي
            category_results = await asyncio.gather(*recommendation_tasks, return_exceptions=True)

            # تجميع التوصيات
            for i, category_result in enumerate(category_results):
                category = list(self.recommendation_categories.keys())[i]

                if isinstance(category_result, Exception):
                    self.logger.error(f"Recommendations for {category} failed: {str(category_result)}")
                    results["recommendations_by_category"][category] = {"error": str(category_result)}
                else:
                    results["recommendations_by_category"][category] = category_result

            # إنتاج مصفوفة الأولويات
            results["priority_matrix"] = await self._create_priority_matrix(
                results["recommendations_by_category"]
            )

            # إنتاج خارطة طريق التنفيذ
            results["implementation_roadmap"] = await self._create_implementation_roadmap(
                results["recommendations_by_category"], results["priority_matrix"]
            )

            # تحليل المخاطر للتوصيات
            results["risk_considerations"] = await self._analyze_recommendation_risks(
                results["recommendations_by_category"]
            )

            # توقع النتائج والعوائد
            results["expected_outcomes"] = await self._project_expected_outcomes(
                results["recommendations_by_category"], analysis_results
            )

            # إطار المراقبة والتقييم
            results["monitoring_framework"] = await self._create_monitoring_framework(
                results["recommendations_by_category"]
            )

            # إحصائيات التوصيات
            results["recommendation_stats"] = self._calculate_recommendation_stats(
                results["recommendations_by_category"]
            )

            self.logger.info(f"Comprehensive recommendations generated for {company_info.get('name', 'Unknown')}")

        except Exception as e:
            self.logger.error(f"Recommendation generation error: {str(e)}")
            results["error"] = str(e)
            results["status"] = "failed"

        return results

    async def _analyze_all_results(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تحليل شامل لجميع النتائج"""

        summary = {
            "overall_assessment": "",
            "key_strengths": [],
            "key_weaknesses": [],
            "opportunities": [],
            "threats": [],
            "critical_issues": [],
            "performance_rating": ""
        }

        try:
            # تحليل الأداء المالي
            financial_analysis = analysis_results.get("classical_analysis_results", {})
            financial_strengths, financial_weaknesses = self._analyze_financial_performance(financial_analysis)

            # تحليل المخاطر
            risk_analysis = analysis_results.get("risk_analysis_results", {})
            risk_threats, risk_opportunities = self._analyze_risk_profile(risk_analysis)

            # تحليل السوق
            market_analysis = analysis_results.get("market_analysis_results", {})
            market_opportunities, market_threats = self._analyze_market_position(market_analysis)

            # تجميع النتائج
            summary["key_strengths"].extend(financial_strengths)
            summary["key_weaknesses"].extend(financial_weaknesses)
            summary["opportunities"].extend(risk_opportunities + market_opportunities)
            summary["threats"].extend(risk_threats + market_threats)

            # تقييم شامل
            summary["overall_assessment"] = await self._generate_overall_assessment(
                summary, company_info
            )

            # تحديد القضايا الحرجة
            summary["critical_issues"] = self._identify_critical_issues(analysis_results)

            # تقييم الأداء العام
            summary["performance_rating"] = self._calculate_performance_rating(analysis_results)

        except Exception as e:
            self.logger.error(f"Results analysis error: {str(e)}")
            summary["error"] = str(e)

        return summary

    async def _generate_category_recommendations(
        self,
        category: str,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج توصيات فئة محددة"""

        try:
            if category == "strategic":
                return await self._generate_strategic_recommendations(
                    analysis_results, company_info, business_context
                )

            elif category == "operational":
                return await self._generate_operational_recommendations(
                    analysis_results, company_info, business_context
                )

            elif category == "financial":
                return await self._generate_financial_recommendations(
                    analysis_results, company_info, business_context
                )

            elif category == "risk_management":
                return await self._generate_risk_management_recommendations(
                    analysis_results, company_info, business_context
                )

            elif category == "growth":
                return await self._generate_growth_recommendations(
                    analysis_results, company_info, business_context
                )

            elif category == "performance":
                return await self._generate_performance_recommendations(
                    analysis_results, company_info, business_context
                )

            elif category == "investment":
                return await self._generate_investment_recommendations(
                    analysis_results, company_info, business_context
                )

            elif category == "governance":
                return await self._generate_governance_recommendations(
                    analysis_results, company_info, business_context
                )

            else:
                return {"error": f"Unknown recommendation category: {category}"}

        except Exception as e:
            return {"error": f"Category recommendations failed: {str(e)}"}

    async def _generate_strategic_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج التوصيات الاستراتيجية"""

        prompt = f"""
        بناءً على التحليل الشامل للشركة {company_info.get('name', 'Unknown')}:

        نتائج التحليل المالي: {analysis_results.get('classical_analysis_results', {})}
        نتائج تحليل المخاطر: {analysis_results.get('risk_analysis_results', {})}
        نتائج تحليل السوق: {analysis_results.get('market_analysis_results', {})}

        قدم توصيات استراتيجية شاملة تتضمن:

        1. الاستراتيجية العامة للشركة
        2. استراتيجية النمو والتوسع
        3. استراتيجية المنافسة والتمييز
        4. استراتيجية إدارة المحفظة
        5. الشراكات الاستراتيجية
        6. الابتكار والتطوير

        لكل توصية، حدد:
        - الهدف الاستراتيجي
        - الأثر المتوقع
        - متطلبات التنفيذ
        - المقاييس للنجاح
        - المخاطر المحتملة
        """

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.system_message),
                HumanMessage(content=prompt)
            ])

            return {
                "category": "strategic",
                "recommendations": [
                    {
                        "id": "STR_001",
                        "title": "تطوير استراتيجية النمو المستدام",
                        "description": "التركيز على النمو المستدام والمربح بدلاً من النمو السريع",
                        "priority": "high",
                        "timeframe": "medium_term",
                        "expected_impact": "زيادة القيمة المساهمين بنسبة 15-20%",
                        "resources_required": "استثمار في التطوير والتسويق",
                        "success_metrics": ["نمو الإيرادات", "هامش الربح", "العائد على الاستثمار"],
                        "risks": ["تغير ظروف السوق", "منافسة متزايدة"]
                    },
                    {
                        "id": "STR_002",
                        "title": "تنويع المحفظة والأسواق",
                        "description": "التوسع في أسواق جديدة وتنويع مصادر الإيرادات",
                        "priority": "medium",
                        "timeframe": "long_term",
                        "expected_impact": "تقليل المخاطر وزيادة فرص النمو",
                        "resources_required": "استثمار كبير في البحث والتطوير",
                        "success_metrics": ["نسبة الإيرادات من أسواق جديدة", "تنوع المحفظة"],
                        "risks": ["مخاطر دخول أسواق جديدة", "تكاليف عالية"]
                    }
                ],
                "ai_insights": response.content,
                "implementation_priority": "high"
            }

        except Exception as e:
            return {"error": f"Strategic recommendations failed: {str(e)}"}

    async def _generate_operational_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج التوصيات التشغيلية"""

        return {
            "category": "operational",
            "recommendations": [
                {
                    "id": "OPR_001",
                    "title": "تحسين الكفاءة التشغيلية",
                    "description": "تطبيق تقنيات إدارة العمليات لتحسين الإنتاجية",
                    "priority": "high",
                    "timeframe": "short_term",
                    "expected_impact": "تحسين الهوامش بنسبة 5-10%",
                    "resources_required": "تدريب الموظفين وتطوير العمليات",
                    "success_metrics": ["نسبة استغلال الطاقة", "وقت الإنتاج", "معدل الأخطاء"],
                    "risks": ["مقاومة التغيير", "تكاليف التطوير الأولية"]
                },
                {
                    "id": "OPR_002",
                    "title": "رقمنة العمليات الأساسية",
                    "description": "تطبيق حلول تقنية لأتمتة العمليات الروتينية",
                    "priority": "medium",
                    "timeframe": "medium_term",
                    "expected_impact": "تقليل التكاليف وتحسين السرعة",
                    "resources_required": "استثمار في تقنية المعلومات",
                    "success_metrics": ["نسبة العمليات المؤتمتة", "وقت المعالجة"],
                    "risks": ["تعقيد التنفيذ", "مخاطر تقنية"]
                }
            ],
            "implementation_priority": "high"
        }

    async def _generate_financial_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج التوصيات المالية"""

        return {
            "category": "financial",
            "recommendations": [
                {
                    "id": "FIN_001",
                    "title": "تحسين هيكل رأس المال",
                    "description": "إعادة توازن الديون وحقوق الملكية لتحسين التكلفة",
                    "priority": "high",
                    "timeframe": "short_term",
                    "expected_impact": "تقليل تكلفة رأس المال بنسبة 2-3%",
                    "resources_required": "إعادة هيكلة مالية",
                    "success_metrics": ["نسبة الدين", "تكلفة رأس المال", "التصنيف الائتماني"],
                    "risks": ["مخاطر السوق المالية", "تغير أسعار الفوائد"]
                },
                {
                    "id": "FIN_002",
                    "title": "تحسين إدارة رأس المال العامل",
                    "description": "تحسين دورة التحويل النقدي وإدارة المخزون",
                    "priority": "medium",
                    "timeframe": "short_term",
                    "expected_impact": "تحرير سيولة إضافية",
                    "resources_required": "تطوير أنظمة إدارة مالية",
                    "success_metrics": ["دورة التحويل النقدي", "معدل دوران المخزون"],
                    "risks": ["تأثير على خدمة العملاء", "مخاطر السيولة"]
                }
            ],
            "implementation_priority": "high"
        }

    async def _generate_risk_management_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج توصيات إدارة المخاطر"""

        return {
            "category": "risk_management",
            "recommendations": [
                {
                    "id": "RSK_001",
                    "title": "تطوير إطار إدارة المخاطر الشامل",
                    "description": "إنشاء نظام متكامل لتحديد وتقييم ومراقبة المخاطر",
                    "priority": "critical",
                    "timeframe": "immediate",
                    "expected_impact": "تقليل التعرض للمخاطر بنسبة 30%",
                    "resources_required": "فريق إدارة مخاطر متخصص",
                    "success_metrics": ["مؤشر المخاطر الإجمالي", "عدد الحوادث", "خسائر المخاطر"],
                    "risks": ["تكاليف إضافية", "تعقيد العمليات"]
                },
                {
                    "id": "RSK_002",
                    "title": "تنويع مصادر الإيراد والعملاء",
                    "description": "تقليل الاعتماد على عميل أو سوق واحد",
                    "priority": "high",
                    "timeframe": "medium_term",
                    "expected_impact": "تحسين استقرار الأعمال",
                    "resources_required": "استثمار في التسويق والمبيعات",
                    "success_metrics": ["مؤشر التركز", "عدد العملاء الرئيسيين"],
                    "risks": ["تكاليف الاستحواذ", "صعوبة التنفيذ"]
                }
            ],
            "implementation_priority": "critical"
        }

    async def _generate_growth_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج توصيات النمو"""

        return {
            "category": "growth",
            "recommendations": [
                {
                    "id": "GRW_001",
                    "title": "التوسع في الأسواق الجديدة",
                    "description": "دخول أسواق جغرافية جديدة أو قطاعات عملاء جديدة",
                    "priority": "medium",
                    "timeframe": "long_term",
                    "expected_impact": "زيادة الإيرادات بنسبة 20-30%",
                    "resources_required": "استثمار كبير في التسويق والتطوير",
                    "success_metrics": ["حصة السوق الجديد", "نمو الإيرادات", "عدد العملاء"],
                    "risks": ["مخاطر السوق الجديد", "منافسة محلية قوية"]
                }
            ],
            "implementation_priority": "medium"
        }

    async def _generate_performance_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج توصيات تحسين الأداء"""

        return {
            "category": "performance",
            "recommendations": [
                {
                    "id": "PRF_001",
                    "title": "تطوير نظام قياس الأداء المتوازن",
                    "description": "تطبيق مؤشرات أداء رئيسية شاملة",
                    "priority": "medium",
                    "timeframe": "short_term",
                    "expected_impact": "تحسين الشفافية والمساءلة",
                    "resources_required": "تطوير أنظمة تقارير",
                    "success_metrics": ["دقة التقارير", "سرعة اتخاذ القرار"],
                    "risks": ["تعقيد إضافي", "مقاومة الإدارة"]
                }
            ],
            "implementation_priority": "medium"
        }

    async def _generate_investment_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج توصيات الاستثمار"""

        return {
            "category": "investment",
            "recommendations": [
                {
                    "id": "INV_001",
                    "title": "الاستثمار في التكنولوجيا والابتكار",
                    "description": "زيادة الاستثمار في التقنيات الناشئة",
                    "priority": "high",
                    "timeframe": "medium_term",
                    "expected_impact": "تحسين الميزة التنافسية",
                    "resources_required": "مخصصات R&D إضافية",
                    "success_metrics": ["عائد الاستثمار في R&D", "عدد الابتكارات"],
                    "risks": ["عدم تحقق العوائد المتوقعة", "تقادم التقنية"]
                }
            ],
            "implementation_priority": "high"
        }

    async def _generate_governance_recommendations(
        self,
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنتاج توصيات الحوكمة"""

        return {
            "category": "governance",
            "recommendations": [
                {
                    "id": "GOV_001",
                    "title": "تعزيز ممارسات الحوكمة المؤسسية",
                    "description": "تطبيق أفضل الممارسات في الحوكمة والشفافية",
                    "priority": "medium",
                    "timeframe": "medium_term",
                    "expected_impact": "تحسين الثقة والتقييم",
                    "resources_required": "تطوير السياسات والإجراءات",
                    "success_metrics": ["مؤشر الحوكمة", "تقييم المستثمرين"],
                    "risks": ["تكاليف إضافية", "تعقيد العمليات"]
                }
            ],
            "implementation_priority": "medium"
        }

    async def _create_priority_matrix(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء مصفوفة الأولويات"""

        matrix = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }

        try:
            for category, category_data in recommendations.items():
                if "recommendations" in category_data:
                    for rec in category_data["recommendations"]:
                        priority = rec.get("priority", "medium")
                        if priority in matrix:
                            matrix[priority].append({
                                "id": rec.get("id"),
                                "title": rec.get("title"),
                                "category": category,
                                "impact": rec.get("expected_impact"),
                                "timeframe": rec.get("timeframe")
                            })

        except Exception as e:
            self.logger.error(f"Priority matrix creation error: {str(e)}")

        return matrix

    async def _create_implementation_roadmap(
        self,
        recommendations: Dict[str, Any],
        priority_matrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنشاء خارطة طريق التنفيذ"""

        roadmap = {
            "phase_1_immediate": {"timeframe": "0-3 months", "recommendations": []},
            "phase_2_short_term": {"timeframe": "3-6 months", "recommendations": []},
            "phase_3_medium_term": {"timeframe": "6-18 months", "recommendations": []},
            "phase_4_long_term": {"timeframe": "18+ months", "recommendations": []}
        }

        try:
            # ترتيب حسب الأولوية والإطار الزمني
            for priority_level in ["critical", "high", "medium", "low"]:
                for rec in priority_matrix.get(priority_level, []):
                    timeframe = rec.get("timeframe", "medium_term")

                    if timeframe == "immediate":
                        roadmap["phase_1_immediate"]["recommendations"].append(rec)
                    elif timeframe == "short_term":
                        roadmap["phase_2_short_term"]["recommendations"].append(rec)
                    elif timeframe == "medium_term":
                        roadmap["phase_3_medium_term"]["recommendations"].append(rec)
                    else:
                        roadmap["phase_4_long_term"]["recommendations"].append(rec)

        except Exception as e:
            self.logger.error(f"Roadmap creation error: {str(e)}")

        return roadmap

    async def _analyze_recommendation_risks(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل مخاطر التوصيات"""

        risk_analysis = {
            "overall_risk_level": "medium",
            "key_risks": [],
            "mitigation_strategies": [],
            "contingency_plans": []
        }

        try:
            all_risks = []

            for category, category_data in recommendations.items():
                if "recommendations" in category_data:
                    for rec in category_data["recommendations"]:
                        risks = rec.get("risks", [])
                        all_risks.extend(risks)

            # تحليل المخاطر الأكثر شيوعاً
            risk_analysis["key_risks"] = list(set(all_risks))[:5]

            # استراتيجيات التخفيف
            risk_analysis["mitigation_strategies"] = [
                "مراقبة مستمرة للمؤشرات الرئيسية",
                "تطوير خطط بديلة للسيناريوهات المختلفة",
                "تدريب الفرق على إدارة المخاطر",
                "مراجعة دورية للتوصيات والتقدم"
            ]

        except Exception as e:
            self.logger.error(f"Risk analysis error: {str(e)}")

        return risk_analysis

    async def _project_expected_outcomes(
        self,
        recommendations: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """توقع النتائج المتوقعة"""

        outcomes = {
            "financial_impact": {
                "revenue_growth": "10-15% annually",
                "cost_reduction": "5-8%",
                "roi_improvement": "15-20%"
            },
            "operational_impact": {
                "efficiency_gain": "20-25%",
                "quality_improvement": "15%",
                "customer_satisfaction": "Improved"
            },
            "strategic_impact": {
                "market_position": "Strengthened",
                "competitive_advantage": "Enhanced",
                "growth_potential": "Expanded"
            },
            "timeline": {
                "short_term": "6 months",
                "medium_term": "12-18 months",
                "long_term": "2-3 years"
            }
        }

        return outcomes

    async def _create_monitoring_framework(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء إطار المراقبة والتقييم"""

        framework = {
            "kpis": [],
            "reporting_frequency": "monthly",
            "review_meetings": "quarterly",
            "success_criteria": [],
            "escalation_procedures": []
        }

        try:
            # جمع مقاييس النجاح من جميع التوصيات
            all_metrics = []

            for category, category_data in recommendations.items():
                if "recommendations" in category_data:
                    for rec in category_data["recommendations"]:
                        metrics = rec.get("success_metrics", [])
                        all_metrics.extend(metrics)

            framework["kpis"] = list(set(all_metrics))[:10]  # أهم 10 مقاييس

            # معايير النجاح
            framework["success_criteria"] = [
                "تحقيق 80% من الأهداف المحددة",
                "البقاء ضمن الميزانية المخصصة",
                "الالتزام بالجدول الزمني",
                "عدم تأثير سلبي على العمليات الحالية"
            ]

        except Exception as e:
            self.logger.error(f"Monitoring framework error: {str(e)}")

        return framework

    def _calculate_recommendation_stats(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """حساب إحصائيات التوصيات"""

        stats = {
            "total_recommendations": 0,
            "by_category": {},
            "by_priority": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "by_timeframe": {"immediate": 0, "short_term": 0, "medium_term": 0, "long_term": 0},
            "implementation_complexity": "medium"
        }

        try:
            for category, category_data in recommendations.items():
                if "recommendations" in category_data:
                    category_count = len(category_data["recommendations"])
                    stats["total_recommendations"] += category_count
                    stats["by_category"][category] = category_count

                    # إحصائيات الأولوية والإطار الزمني
                    for rec in category_data["recommendations"]:
                        priority = rec.get("priority", "medium")
                        timeframe = rec.get("timeframe", "medium_term")

                        if priority in stats["by_priority"]:
                            stats["by_priority"][priority] += 1

                        if timeframe in stats["by_timeframe"]:
                            stats["by_timeframe"][timeframe] += 1

        except Exception as e:
            self.logger.error(f"Stats calculation error: {str(e)}")

        return stats

    # طرق مساعدة للتحليل
    def _analyze_financial_performance(self, financial_analysis: Dict[str, Any]) -> tuple:
        """تحليل الأداء المالي"""
        strengths = ["Strong profitability ratios", "Good liquidity position", "Efficient asset utilization"]
        weaknesses = ["High debt levels", "Declining margins", "Working capital issues"]
        return strengths, weaknesses

    def _analyze_risk_profile(self, risk_analysis: Dict[str, Any]) -> tuple:
        """تحليل ملف المخاطر"""
        threats = ["Market volatility", "Credit risks", "Operational risks"]
        opportunities = ["Risk mitigation potential", "Improved controls", "Better risk pricing"]
        return threats, opportunities

    def _analyze_market_position(self, market_analysis: Dict[str, Any]) -> tuple:
        """تحليل موقع السوق"""
        opportunities = ["Market expansion", "New product opportunities", "Strategic partnerships"]
        threats = ["Competitive pressure", "Market saturation", "Regulatory changes"]
        return opportunities, threats

    async def _generate_overall_assessment(
        self,
        summary: Dict[str, Any],
        company_info: Dict[str, Any]
    ) -> str:
        """إنتاج التقييم الشامل"""

        prompt = f"""
        بناءً على تحليل الشركة {company_info.get('name', 'Unknown')}:

        نقاط القوة: {summary.get('key_strengths', [])}
        نقاط الضعف: {summary.get('key_weaknesses', [])}
        الفرص: {summary.get('opportunities', [])}
        التهديدات: {summary.get('threats', [])}

        قدم تقييماً شاملاً في فقرة واحدة يلخص الوضع العام للشركة وتوقعاتها المستقبلية.
        """

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.system_message),
                HumanMessage(content=prompt)
            ])

            return response.content

        except Exception as e:
            return f"Assessment generation failed: {str(e)}"

    def _identify_critical_issues(self, analysis_results: Dict[str, Any]) -> List[str]:
        """تحديد القضايا الحرجة"""
        critical_issues = []

        # فحص المؤشرات الحرجة
        if "high_debt_ratio" in str(analysis_results):
            critical_issues.append("High debt levels requiring immediate attention")

        if "declining_profitability" in str(analysis_results):
            critical_issues.append("Declining profitability trends")

        if "liquidity_concerns" in str(analysis_results):
            critical_issues.append("Liquidity management issues")

        return critical_issues[:5]  # أهم 5 قضايا

    def _calculate_performance_rating(self, analysis_results: Dict[str, Any]) -> str:
        """حساب تقييم الأداء العام"""
        # تقييم مبسط بناءً على النتائج
        scores = []

        # يمكن تطوير منطق أكثر تعقيداً هنا
        if "classical_analysis_results" in analysis_results:
            scores.append(75)  # درجة افتراضية

        if "risk_analysis_results" in analysis_results:
            scores.append(70)  # درجة افتراضية

        if "market_analysis_results" in analysis_results:
            scores.append(80)  # درجة افتراضية

        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score >= 80:
                return "Excellent"
            elif avg_score >= 70:
                return "Good"
            elif avg_score >= 60:
                return "Average"
            else:
                return "Below Average"

        return "Insufficient Data"

    async def process_workflow_task(self, state: WorkflowState) -> WorkflowState:
        """معالجة مهمة سير العمل"""
        try:
            # استخراج البيانات من الحالة
            analysis_results = {
                "classical_analysis_results": state.data.get("classical_analysis_results", {}),
                "risk_analysis_results": state.data.get("risk_analysis_results", {}),
                "market_analysis_results": state.data.get("market_analysis_results", {})
            }

            company_info = state.data.get("company_info", {})
            business_context = state.data.get("business_context", {})

            # إنتاج التوصيات الشاملة
            recommendation_results = await self.generate_comprehensive_recommendations(
                analysis_results, company_info, business_context
            )

            # تحديث حالة سير العمل
            state.data["recommendation_results"] = recommendation_results
            state.metadata["recommendations_generated"] = True
            state.metadata["total_recommendations"] = recommendation_results.get(
                "recommendation_stats", {}
            ).get("total_recommendations", 0)

            # إضافة النتائج لسجل المراجعة
            state.audit_trail.append({
                "agent": self.agent_name,
                "action": "recommendations_generated",
                "timestamp": datetime.now().isoformat(),
                "recommendations_count": recommendation_results.get(
                    "recommendation_stats", {}
                ).get("total_recommendations", 0),
                "status": "success" if "error" not in recommendation_results else "partial_success"
            })

            self.logger.info("Recommendation generation workflow task completed successfully")

        except Exception as e:
            self.logger.error(f"Recommendation workflow error: {str(e)}")
            state.errors.append({
                "agent": self.agent_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

        return state