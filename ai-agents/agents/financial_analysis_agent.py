"""
Financial Analysis Agent
وكيل التحليل المالي

This agent specializes in performing comprehensive financial analysis using the
180 financial analysis types from the FinClick.AI analysis engine.
"""

from typing import Dict, Any, List, Optional
import asyncio
import json
from datetime import datetime
import numpy as np

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from ...financial-engine.core.analysis_orchestrator import AnalysisOrchestrator, AnalysisConfiguration, WorkflowType
from ...financial-engine.core.data_models import FinancialStatements, CompanyInfo
from langchain_core.prompts import ChatPromptTemplate


class FinancialAnalysisAgent(FinancialAgent):
    """
    Specialized agent for comprehensive financial analysis
    وكيل متخصص في التحليل المالي الشامل
    """

    def __init__(self, agent_id: str, agent_name_ar: str, agent_name_en: str):
        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=AgentType.FINANCIAL_ANALYSIS
        )

        # Initialize financial analysis engine
        self.analysis_orchestrator = AnalysisOrchestrator()

        # Analysis specialization mapping
        self.specialization_mapping = self._initialize_specialization_mapping()

    def _initialize_capabilities(self) -> None:
        """Initialize financial analysis capabilities"""
        super()._initialize_capabilities()

        analysis_capabilities = [
            "comprehensive_financial_analysis",
            "liquidity_analysis",
            "profitability_analysis",
            "efficiency_analysis",
            "leverage_analysis",
            "growth_analysis",
            "ratio_analysis",
            "trend_analysis",
            "comparative_analysis",
            "scenario_analysis",
            "sensitivity_analysis",
            "cash_flow_analysis",
            "working_capital_analysis",
            "capital_structure_analysis",
            "performance_evaluation"
        ]

        self.state.capabilities.extend(analysis_capabilities)

        # Set specializations based on agent name/ID
        if "liquidity" in self.state.agent_id.lower():
            self.state.specializations.extend(["liquidity_analysis", "working_capital", "cash_flow"])
        elif "profitability" in self.state.agent_id.lower():
            self.state.specializations.extend(["profitability_analysis", "margin_analysis", "return_analysis"])
        elif "efficiency" in self.state.agent_id.lower():
            self.state.specializations.extend(["efficiency_analysis", "turnover_ratios", "productivity"])
        elif "leverage" in self.state.agent_id.lower():
            self.state.specializations.extend(["leverage_analysis", "debt_analysis", "capital_structure"])
        else:
            self.state.specializations.extend(["general_analysis", "comprehensive_analysis"])

    def _initialize_prompts(self) -> None:
        """Initialize financial analysis prompts"""
        super()._initialize_prompts()

        self.comprehensive_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            أنت خبير في التحليل المالي الشامل لمنصة FinClick.AI.
            تمتلك القدرة على تنفيذ 180 نوع تحليل مالي مختلف.

            You are a comprehensive financial analysis expert for the FinClick.AI platform.
            You have the capability to perform 180 different types of financial analysis.

            مهامك الأساسية:
            1. تحليل القوائم المالية بشكل شامل
            2. حساب جميع النسب المالية المطلوبة
            3. تقييم الأداء المالي والتشغيلي
            4. تحديد نقاط القوة والضعف
            5. تقديم رؤى استراتيجية مدعومة بالأدلة

            Your primary tasks:
            1. Comprehensive financial statement analysis
            2. Calculate all required financial ratios
            3. Evaluate financial and operational performance
            4. Identify strengths and weaknesses
            5. Provide evidence-based strategic insights

            استخدم البيانات المالية المقدمة فقط ولا تفترض أي أرقام.
            Use only the provided financial data and do not assume any numbers.
            """),
            ("human", """
            قم بتحليل البيانات المالية التالية:

            معلومات الشركة: {company_info}
            القوائم المالية: {financial_statements}
            نوع التحليل المطلوب: {analysis_type}
            متطلبات إضافية: {additional_requirements}

            Analyze the following financial data:

            Company Information: {company_info}
            Financial Statements: {financial_statements}
            Required Analysis Type: {analysis_type}
            Additional Requirements: {additional_requirements}

            قدم تحليلاً شاملاً ومنظماً يتضمن:
            1. ملخص تنفيذي
            2. النتائج الرئيسية والمؤشرات
            3. نقاط القوة والضعف
            4. المقارنات مع المعايير الصناعية
            5. التوصيات الاستراتيجية

            Provide a comprehensive and organized analysis including:
            1. Executive summary
            2. Key findings and indicators
            3. Strengths and weaknesses
            4. Industry benchmark comparisons
            5. Strategic recommendations
            """)
        ])

        self.specialized_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            أنت متخصص في {specialization} ضمن منصة FinClick.AI.
            لديك خبرة عميقة في هذا المجال المحدد من التحليل المالي.

            You are a specialist in {specialization} within the FinClick.AI platform.
            You have deep expertise in this specific area of financial analysis.

            ركز على:
            - التحليل المتعمق للمجال المتخصص
            - استخدام المقاييس والنسب المتخصصة
            - تقديم رؤى دقيقة ومفصلة
            - ربط النتائج بالسياق التجاري

            Focus on:
            - In-depth analysis of the specialized area
            - Use specialized metrics and ratios
            - Provide precise and detailed insights
            - Connect results to business context
            """),
            ("human", """
            قم بتحليل متخصص في {specialization} للبيانات التالية:

            {financial_data}

            Perform specialized {specialization} analysis for the following data:

            قدم تحليلاً متخصصاً يتضمن:
            1. المؤشرات المتخصصة
            2. التفسير التفصيلي للنتائج
            3. المخاطر والفرص المحددة
            4. التوصيات المتخصصة

            Provide specialized analysis including:
            1. Specialized indicators
            2. Detailed interpretation of results
            3. Specific risks and opportunities
            4. Specialized recommendations
            """)
        ])

        self.quick_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            أنت محلل مالي سريع لمنصة FinClick.AI.
            مهمتك تقديم تحليل سريع وأساسي للبيانات المالية في الحالات العاجلة.

            You are a quick financial analyst for the FinClick.AI platform.
            Your task is to provide rapid, essential financial analysis for urgent situations.

            ركز على:
            - النسب المالية الأساسية
            - المؤشرات الحرجة
            - إشارات الإنذار المبكر
            - التوصيات الفورية

            Focus on:
            - Basic financial ratios
            - Critical indicators
            - Early warning signals
            - Immediate recommendations
            """),
            ("human", """
            قم بتحليل سريع للبيانات المالية التالية:

            {financial_data}

            Perform quick analysis of the following financial data:

            قدم تحليلاً سريعاً يتضمن:
            1. النسب الأساسية
            2. التقييم السريع للوضع المالي
            3. المخاطر الفورية
            4. التوصيات العاجلة

            Provide quick analysis including:
            1. Basic ratios
            2. Rapid financial position assessment
            3. Immediate risks
            4. Urgent recommendations
            """)
        ])

    def _initialize_specialization_mapping(self) -> Dict[str, List[str]]:
        """Map specializations to specific analysis types"""
        return {
            "liquidity_analysis": [
                "current_ratio_analysis",
                "quick_ratio_analysis",
                "cash_ratio_analysis",
                "working_capital_analysis",
                "cash_conversion_cycle",
                "operating_cash_flow_ratio"
            ],
            "profitability_analysis": [
                "gross_profit_margin",
                "operating_profit_margin",
                "net_profit_margin",
                "return_on_assets",
                "return_on_equity",
                "return_on_invested_capital",
                "earnings_per_share"
            ],
            "efficiency_analysis": [
                "asset_turnover",
                "inventory_turnover",
                "receivables_turnover",
                "fixed_asset_turnover",
                "working_capital_turnover"
            ],
            "leverage_analysis": [
                "debt_to_equity",
                "debt_to_assets",
                "interest_coverage",
                "debt_service_coverage",
                "financial_leverage"
            ]
        }

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process financial analysis task"""
        task_type = task.task_type
        input_data = task.input_data

        if task_type == "comprehensive_financial_analysis":
            return await self._perform_comprehensive_analysis(input_data)
        elif task_type == "financial_analysis":
            return await self._perform_comprehensive_analysis(input_data)
        elif task_type in ["liquidity_analysis", "profitability_analysis", "efficiency_analysis", "leverage_analysis"]:
            return await self._perform_specialized_analysis(task_type, input_data)
        elif task_type == "key_metrics_calculation":
            return await self._calculate_key_metrics(input_data)
        elif task_type == "quick_financial_analysis":
            return await self._perform_quick_analysis(input_data)
        elif task_type == "ratio_analysis":
            return await self._perform_ratio_analysis(input_data)
        elif task_type == "trend_analysis":
            return await self._perform_trend_analysis(input_data)
        else:
            return await self._perform_general_analysis(task_type, input_data)

    async def _perform_comprehensive_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive financial analysis using all 180 analysis types"""
        try:
            # Convert input data to FinancialStatements format
            financial_statements = self._convert_to_financial_statements(input_data)
            company_info = self._extract_company_info(input_data)

            # Configure comprehensive analysis
            config = AnalysisConfiguration(
                include_all=True,  # All 180 analysis types
                analysis_categories=["classical_foundational", "risk_analysis", "market_analysis"],
                parallel_execution=True,
                max_workers=5,
                timeout_seconds=300
            )

            # Execute comprehensive analysis using the analysis orchestrator
            self.logger.info("Starting comprehensive financial analysis with all 180 analysis types")

            analysis_report = await self.analysis_orchestrator.perform_comprehensive_analysis(
                financial_statements=financial_statements,
                company_info=company_info,
                config=config
            )

            # Generate AI-enhanced insights
            ai_insights = await self._generate_ai_insights(
                financial_statements.__dict__,
                analysis_report.analysis_summary,
                "comprehensive_analysis"
            )

            return {
                "status": "completed",
                "analysis_type": "comprehensive_financial_analysis",
                "analysis_report": analysis_report.__dict__,
                "ai_insights": ai_insights,
                "total_analyses_performed": analysis_report.execution_metadata["total_analyses"],
                "execution_time": analysis_report.execution_metadata["duration_seconds"],
                "confidence_score": self._calculate_analysis_confidence(analysis_report),
                "recommendations": analysis_report.recommendations[:10],  # Top 10 recommendations
                "critical_alerts": self._extract_critical_alerts(analysis_report)
            }

        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "analysis_type": "comprehensive_financial_analysis"
            }

    async def _perform_specialized_analysis(self, analysis_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specialized analysis in specific area"""
        try:
            # Convert input data
            financial_statements = self._convert_to_financial_statements(input_data)
            company_info = self._extract_company_info(input_data)

            # Get specific analysis types for this specialization
            specific_analyses = self.specialization_mapping.get(analysis_type, [])

            # Configure specialized analysis
            config = AnalysisConfiguration(
                analysis_types=specific_analyses,
                analysis_categories=["classical_foundational"],  # Focus on foundational analysis
                parallel_execution=True,
                timeout_seconds=120
            )

            # Execute specialized analysis
            analysis_report = await self.analysis_orchestrator.perform_comprehensive_analysis(
                financial_statements=financial_statements,
                company_info=company_info,
                config=config
            )

            # Generate specialized AI insights
            ai_insights = await self._generate_specialized_insights(
                financial_statements.__dict__,
                analysis_type,
                analysis_report.category_results.get("classical_foundational", [])
            )

            return {
                "status": "completed",
                "analysis_type": analysis_type,
                "specialized_results": analysis_report.category_results.get("classical_foundational", []),
                "ai_insights": ai_insights,
                "key_metrics": self._extract_key_metrics_for_specialization(analysis_type, analysis_report),
                "performance_score": self._calculate_specialization_score(analysis_type, analysis_report),
                "recommendations": self._filter_recommendations_by_specialization(analysis_type, analysis_report.recommendations)
            }

        except Exception as e:
            self.logger.error(f"Specialized analysis failed for {analysis_type}: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "analysis_type": analysis_type
            }

    async def _calculate_key_metrics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial metrics quickly"""
        try:
            # Extract essential financial data
            financial_data = input_data.get("extracted_data", input_data)

            key_metrics = {}

            # Balance Sheet Metrics
            balance_sheet = financial_data.get("balance_sheet", {})
            if balance_sheet:
                total_assets = balance_sheet.get("total_assets", 0)
                total_liabilities = balance_sheet.get("total_liabilities", 0)
                total_equity = balance_sheet.get("total_equity", 0)

                if total_assets > 0:
                    key_metrics["debt_to_assets_ratio"] = total_liabilities / total_assets
                if total_equity > 0:
                    key_metrics["debt_to_equity_ratio"] = total_liabilities / total_equity

                # Current ratio if current assets/liabilities available
                current_assets = balance_sheet.get("current_assets", 0)
                current_liabilities = balance_sheet.get("current_liabilities", 0)
                if current_liabilities > 0:
                    key_metrics["current_ratio"] = current_assets / current_liabilities

            # Income Statement Metrics
            income_statement = financial_data.get("income_statement", {})
            if income_statement:
                revenue = income_statement.get("revenue", 0)
                net_income = income_statement.get("net_income", 0)
                gross_profit = income_statement.get("gross_profit", 0)

                if revenue > 0:
                    key_metrics["net_profit_margin"] = (net_income / revenue) * 100
                    if gross_profit > 0:
                        key_metrics["gross_profit_margin"] = (gross_profit / revenue) * 100

                if total_assets > 0 and net_income:
                    key_metrics["return_on_assets"] = (net_income / total_assets) * 100
                if total_equity > 0 and net_income:
                    key_metrics["return_on_equity"] = (net_income / total_equity) * 100

            # Cash Flow Metrics
            cash_flow = financial_data.get("cash_flow_statement", {})
            if cash_flow:
                operating_cash_flow = cash_flow.get("operating_cash_flow", 0)
                if current_liabilities > 0 and operating_cash_flow:
                    key_metrics["operating_cash_flow_ratio"] = operating_cash_flow / current_liabilities

            # Generate AI interpretation
            ai_interpretation = await self._generate_metrics_interpretation(key_metrics, financial_data)

            return {
                "status": "completed",
                "key_metrics": key_metrics,
                "ai_interpretation": ai_interpretation,
                "metric_categories": self._categorize_metrics(key_metrics),
                "performance_indicators": self._assess_performance_indicators(key_metrics)
            }

        except Exception as e:
            self.logger.error(f"Key metrics calculation failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _perform_quick_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quick financial analysis for urgent situations"""
        try:
            financial_data = input_data.get("extracted_data", input_data)

            # Calculate essential ratios quickly
            quick_metrics = await self._calculate_essential_ratios(financial_data)

            # Identify immediate concerns
            concerns = self._identify_immediate_concerns(quick_metrics, financial_data)

            # Generate quick AI analysis
            ai_analysis = await self._generate_quick_ai_analysis(financial_data)

            return {
                "status": "completed",
                "analysis_type": "quick_analysis",
                "essential_metrics": quick_metrics,
                "immediate_concerns": concerns,
                "ai_analysis": ai_analysis,
                "health_score": self._calculate_quick_health_score(quick_metrics),
                "urgent_recommendations": self._generate_urgent_recommendations(concerns)
            }

        except Exception as e:
            self.logger.error(f"Quick analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _perform_ratio_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive ratio analysis"""
        try:
            financial_data = input_data.get("financial_statements", input_data)

            # Calculate all major ratio categories
            liquidity_ratios = self._calculate_liquidity_ratios(financial_data)
            profitability_ratios = self._calculate_profitability_ratios(financial_data)
            efficiency_ratios = self._calculate_efficiency_ratios(financial_data)
            leverage_ratios = self._calculate_leverage_ratios(financial_data)

            all_ratios = {
                "liquidity_ratios": liquidity_ratios,
                "profitability_ratios": profitability_ratios,
                "efficiency_ratios": efficiency_ratios,
                "leverage_ratios": leverage_ratios
            }

            # Generate ratio analysis insights
            ratio_insights = await self._generate_ratio_insights(all_ratios)

            return {
                "status": "completed",
                "analysis_type": "ratio_analysis",
                "ratio_categories": all_ratios,
                "ratio_insights": ratio_insights,
                "benchmark_comparisons": self._compare_ratios_with_benchmarks(all_ratios, financial_data.get("sector", "default")),
                "ratio_trends": self._analyze_ratio_trends(all_ratios, financial_data)
            }

        except Exception as e:
            self.logger.error(f"Ratio analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _perform_trend_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform trend analysis using historical data"""
        try:
            current_data = input_data.get("current_financial_statements", {})
            historical_data = input_data.get("historical_data", [])

            if not historical_data:
                return {
                    "status": "completed",
                    "analysis_type": "trend_analysis",
                    "message": "No historical data available for trend analysis",
                    "current_metrics": await self._calculate_key_metrics({"extracted_data": current_data})
                }

            # Calculate trends for key metrics
            trend_analysis = self._calculate_financial_trends(current_data, historical_data)

            # Generate trend insights
            trend_insights = await self._generate_trend_insights(trend_analysis)

            return {
                "status": "completed",
                "analysis_type": "trend_analysis",
                "trend_analysis": trend_analysis,
                "trend_insights": trend_insights,
                "trend_direction": self._assess_overall_trend_direction(trend_analysis),
                "future_projections": self._generate_simple_projections(trend_analysis)
            }

        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _perform_general_analysis(self, analysis_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general analysis for unspecified types"""
        try:
            financial_data = input_data.get("financial_statements", input_data)

            # Use comprehensive analysis approach for unknown types
            basic_analysis = await self._calculate_key_metrics({"extracted_data": financial_data})

            # Generate general insights using AI
            ai_insights = await self._generate_general_insights(financial_data, analysis_type)

            return {
                "status": "completed",
                "analysis_type": analysis_type,
                "basic_metrics": basic_analysis,
                "ai_insights": ai_insights,
                "general_assessment": self._generate_general_assessment(basic_analysis)
            }

        except Exception as e:
            self.logger.error(f"General analysis failed for {analysis_type}: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    # Helper methods for analysis
    def _convert_to_financial_statements(self, input_data: Dict[str, Any]) -> FinancialStatements:
        """Convert input data to FinancialStatements object"""
        extracted_data = input_data.get("extracted_data", input_data)

        return FinancialStatements(
            balance_sheet=extracted_data.get("balance_sheet", {}),
            income_statement=extracted_data.get("income_statement", {}),
            cash_flow_statement=extracted_data.get("cash_flow_statement", {}),
            sector=extracted_data.get("company_info", {}).get("sector", "default"),
            shares_outstanding=extracted_data.get("shares_outstanding", 1000000),  # Default
            share_price=extracted_data.get("share_price", 0),
            currency=extracted_data.get("currency", "SAR")
        )

    def _extract_company_info(self, input_data: Dict[str, Any]) -> CompanyInfo:
        """Extract company information"""
        company_data = input_data.get("extracted_data", {}).get("company_info", {})

        return CompanyInfo(
            company_name=company_data.get("name", "Unknown Company"),
            sector=company_data.get("sector", "default"),
            country="Saudi Arabia",  # Default
            currency=input_data.get("currency", "SAR"),
            fiscal_year_end="December",  # Default
            employees=company_data.get("employees"),
            market_cap=company_data.get("market_cap")
        )

    async def _generate_ai_insights(self, financial_data: Dict[str, Any], analysis_summary: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Generate AI-enhanced insights"""
        try:
            chain = self.comprehensive_analysis_prompt | self.llm
            response = await chain.ainvoke({
                "company_info": json.dumps(financial_data.get("company_info", {}), ensure_ascii=False),
                "financial_statements": json.dumps({
                    "balance_sheet": financial_data.get("balance_sheet", {}),
                    "income_statement": financial_data.get("income_statement", {}),
                    "cash_flow_statement": financial_data.get("cash_flow_statement", {})
                }, ensure_ascii=False),
                "analysis_type": analysis_type,
                "additional_requirements": f"Analysis summary: {json.dumps(analysis_summary, ensure_ascii=False)}"
            })

            return {
                "ai_analysis": response.content,
                "insights_generated": True,
                "confidence": 0.85
            }

        except Exception as e:
            self.logger.error(f"AI insights generation failed: {str(e)}")
            return {
                "ai_analysis": "AI analysis temporarily unavailable",
                "insights_generated": False,
                "error": str(e)
            }

    async def _generate_specialized_insights(self, financial_data: Dict[str, Any], specialization: str, analysis_results: List[Any]) -> Dict[str, Any]:
        """Generate specialized insights for specific analysis areas"""
        try:
            chain = self.specialized_analysis_prompt | self.llm
            response = await chain.ainvoke({
                "specialization": specialization,
                "financial_data": json.dumps(financial_data, ensure_ascii=False)
            })

            return {
                "specialized_analysis": response.content,
                "specialization": specialization,
                "insights_generated": True
            }

        except Exception as e:
            self.logger.error(f"Specialized insights generation failed: {str(e)}")
            return {
                "specialized_analysis": "Specialized analysis temporarily unavailable",
                "insights_generated": False,
                "error": str(e)
            }

    async def _generate_metrics_interpretation(self, metrics: Dict[str, float], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI interpretation of calculated metrics"""
        try:
            interpretation_prompt = f"""
            فسر النسب المالية التالية للشركة:
            {json.dumps(metrics, ensure_ascii=False)}

            Interpret the following financial ratios for the company:
            {json.dumps(metrics)}

            قدم تفسيراً واضحاً لكل نسبة وما تعنيه للوضع المالي للشركة.
            Provide a clear interpretation of each ratio and what it means for the company's financial position.
            """

            response = await self.llm.ainvoke([{"role": "user", "content": interpretation_prompt}])

            return {
                "interpretation": response.content,
                "metrics_analyzed": len(metrics),
                "interpretation_confidence": 0.8
            }

        except Exception as e:
            return {
                "interpretation": "Metrics interpretation temporarily unavailable",
                "error": str(e)
            }

    async def _generate_quick_ai_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quick AI analysis for urgent situations"""
        try:
            chain = self.quick_analysis_prompt | self.llm
            response = await chain.ainvoke({
                "financial_data": json.dumps(financial_data, ensure_ascii=False)
            })

            return {
                "quick_analysis": response.content,
                "analysis_type": "urgent",
                "generated_successfully": True
            }

        except Exception as e:
            return {
                "quick_analysis": "Quick analysis temporarily unavailable",
                "error": str(e)
            }

    def _calculate_essential_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate essential financial ratios quickly"""
        ratios = {}

        balance_sheet = financial_data.get("balance_sheet", {})
        income_statement = financial_data.get("income_statement", {})

        # Essential liquidity ratio
        current_assets = balance_sheet.get("current_assets", 0)
        current_liabilities = balance_sheet.get("current_liabilities", 0)
        if current_liabilities > 0:
            ratios["current_ratio"] = current_assets / current_liabilities

        # Essential profitability ratios
        revenue = income_statement.get("revenue", 0)
        net_income = income_statement.get("net_income", 0)
        if revenue > 0:
            ratios["net_margin"] = (net_income / revenue) * 100

        # Essential leverage ratio
        total_debt = balance_sheet.get("total_debt", balance_sheet.get("total_liabilities", 0))
        total_equity = balance_sheet.get("total_equity", 0)
        if total_equity > 0:
            ratios["debt_to_equity"] = total_debt / total_equity

        return ratios

    def _identify_immediate_concerns(self, metrics: Dict[str, float], financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify immediate financial concerns"""
        concerns = []

        # Liquidity concerns
        current_ratio = metrics.get("current_ratio", 0)
        if current_ratio < 1.0:
            concerns.append({
                "type": "liquidity",
                "severity": "high",
                "description": f"Current ratio of {current_ratio:.2f} indicates potential liquidity problems",
                "description_ar": f"نسبة التداول {current_ratio:.2f} تشير إلى مشاكل سيولة محتملة"
            })

        # Profitability concerns
        net_margin = metrics.get("net_margin", 0)
        if net_margin < 0:
            concerns.append({
                "type": "profitability",
                "severity": "high",
                "description": f"Negative net margin of {net_margin:.1f}% indicates losses",
                "description_ar": f"هامش ربح سالب {net_margin:.1f}% يشير إلى خسائر"
            })

        # Leverage concerns
        debt_to_equity = metrics.get("debt_to_equity", 0)
        if debt_to_equity > 2.0:
            concerns.append({
                "type": "leverage",
                "severity": "medium",
                "description": f"High debt-to-equity ratio of {debt_to_equity:.2f} indicates high leverage",
                "description_ar": f"نسبة دين عالية {debt_to_equity:.2f} تشير إلى رافعة مالية عالية"
            })

        return concerns

    def _calculate_quick_health_score(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Calculate quick financial health score"""
        score = 100  # Start with perfect score

        # Deduct points for poor ratios
        current_ratio = metrics.get("current_ratio", 1.5)
        if current_ratio < 1.0:
            score -= 30
        elif current_ratio < 1.2:
            score -= 15

        net_margin = metrics.get("net_margin", 5)
        if net_margin < 0:
            score -= 25
        elif net_margin < 5:
            score -= 10

        debt_to_equity = metrics.get("debt_to_equity", 1.0)
        if debt_to_equity > 2.0:
            score -= 20
        elif debt_to_equity > 1.5:
            score -= 10

        # Determine grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return {
            "score": max(0, score),
            "grade": grade,
            "health_level": "excellent" if score >= 90 else "good" if score >= 70 else "fair" if score >= 50 else "poor"
        }

    def _generate_urgent_recommendations(self, concerns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate urgent recommendations based on immediate concerns"""
        recommendations = []

        for concern in concerns:
            if concern["type"] == "liquidity" and concern["severity"] == "high":
                recommendations.append({
                    "priority": "critical",
                    "category": "liquidity",
                    "title": "Immediate Liquidity Action Required",
                    "title_ar": "مطلوب إجراء فوري للسيولة",
                    "action": "Secure additional short-term financing or accelerate receivables collection",
                    "action_ar": "تأمين تمويل قصير الأجل إضافي أو تسريع تحصيل الذمم"
                })

            elif concern["type"] == "profitability" and concern["severity"] == "high":
                recommendations.append({
                    "priority": "critical",
                    "category": "profitability",
                    "title": "Address Negative Profitability",
                    "title_ar": "معالجة الربحية السالبة",
                    "action": "Review cost structure and implement immediate cost reduction measures",
                    "action_ar": "مراجعة هيكل التكاليف وتطبيق تدابير تخفيض فورية"
                })

        return recommendations

    def _calculate_liquidity_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive liquidity ratios"""
        ratios = {}
        balance_sheet = financial_data.get("balance_sheet", {})
        cash_flow = financial_data.get("cash_flow_statement", {})

        current_assets = balance_sheet.get("current_assets", 0)
        current_liabilities = balance_sheet.get("current_liabilities", 0)
        cash = balance_sheet.get("cash_and_cash_equivalents", 0)
        inventory = balance_sheet.get("inventory", 0)
        operating_cash_flow = cash_flow.get("operating_cash_flow", 0)

        if current_liabilities > 0:
            ratios["current_ratio"] = current_assets / current_liabilities
            ratios["quick_ratio"] = (current_assets - inventory) / current_liabilities
            ratios["cash_ratio"] = cash / current_liabilities
            if operating_cash_flow > 0:
                ratios["operating_cash_flow_ratio"] = operating_cash_flow / current_liabilities

        return ratios

    def _calculate_profitability_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive profitability ratios"""
        ratios = {}
        income_statement = financial_data.get("income_statement", {})
        balance_sheet = financial_data.get("balance_sheet", {})

        revenue = income_statement.get("revenue", 0)
        gross_profit = income_statement.get("gross_profit", 0)
        operating_income = income_statement.get("operating_income", 0)
        net_income = income_statement.get("net_income", 0)
        total_assets = balance_sheet.get("total_assets", 0)
        total_equity = balance_sheet.get("total_equity", 0)

        if revenue > 0:
            ratios["gross_margin"] = (gross_profit / revenue) * 100
            ratios["operating_margin"] = (operating_income / revenue) * 100
            ratios["net_margin"] = (net_income / revenue) * 100

        if total_assets > 0:
            ratios["return_on_assets"] = (net_income / total_assets) * 100

        if total_equity > 0:
            ratios["return_on_equity"] = (net_income / total_equity) * 100

        return ratios

    def _calculate_efficiency_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate efficiency ratios"""
        ratios = {}
        income_statement = financial_data.get("income_statement", {})
        balance_sheet = financial_data.get("balance_sheet", {})

        revenue = income_statement.get("revenue", 0)
        total_assets = balance_sheet.get("total_assets", 0)
        fixed_assets = balance_sheet.get("fixed_assets", 0)
        inventory = balance_sheet.get("inventory", 0)
        accounts_receivable = balance_sheet.get("accounts_receivable", 0)
        cost_of_goods_sold = income_statement.get("cost_of_goods_sold", 0)

        if total_assets > 0:
            ratios["asset_turnover"] = revenue / total_assets

        if fixed_assets > 0:
            ratios["fixed_asset_turnover"] = revenue / fixed_assets

        if inventory > 0 and cost_of_goods_sold > 0:
            ratios["inventory_turnover"] = cost_of_goods_sold / inventory

        if accounts_receivable > 0:
            ratios["receivables_turnover"] = revenue / accounts_receivable

        return ratios

    def _calculate_leverage_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate leverage ratios"""
        ratios = {}
        balance_sheet = financial_data.get("balance_sheet", {})
        income_statement = financial_data.get("income_statement", {})

        total_debt = balance_sheet.get("total_debt", balance_sheet.get("total_liabilities", 0))
        total_equity = balance_sheet.get("total_equity", 0)
        total_assets = balance_sheet.get("total_assets", 0)
        ebit = income_statement.get("ebit", income_statement.get("operating_income", 0))
        interest_expense = income_statement.get("interest_expense", 0)

        if total_equity > 0:
            ratios["debt_to_equity"] = total_debt / total_equity

        if total_assets > 0:
            ratios["debt_to_assets"] = total_debt / total_assets

        if interest_expense > 0:
            ratios["interest_coverage"] = ebit / interest_expense

        return ratios

    async def _generate_ratio_insights(self, all_ratios: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Generate insights from ratio analysis"""
        insights = {
            "strengths": [],
            "weaknesses": [],
            "neutral_areas": []
        }

        # Analyze liquidity ratios
        liquidity = all_ratios.get("liquidity_ratios", {})
        current_ratio = liquidity.get("current_ratio", 0)

        if current_ratio > 2.0:
            insights["strengths"].append("Strong liquidity position with current ratio above 2.0")
        elif current_ratio < 1.0:
            insights["weaknesses"].append("Weak liquidity position with current ratio below 1.0")
        else:
            insights["neutral_areas"].append("Adequate liquidity position")

        # Analyze profitability ratios
        profitability = all_ratios.get("profitability_ratios", {})
        net_margin = profitability.get("net_margin", 0)

        if net_margin > 10:
            insights["strengths"].append("Strong profitability with net margin above 10%")
        elif net_margin < 0:
            insights["weaknesses"].append("Negative profitability - company is making losses")
        else:
            insights["neutral_areas"].append("Moderate profitability levels")

        return insights

    def _compare_ratios_with_benchmarks(self, all_ratios: Dict[str, Dict[str, float]], sector: str) -> Dict[str, Any]:
        """Compare ratios with industry benchmarks"""
        # Simplified benchmark comparison
        benchmarks = {
            "manufacturing": {
                "current_ratio": 1.5,
                "net_margin": 8.0,
                "debt_to_equity": 1.0,
                "asset_turnover": 1.2
            },
            "retail": {
                "current_ratio": 1.3,
                "net_margin": 5.0,
                "debt_to_equity": 0.8,
                "asset_turnover": 2.0
            },
            "default": {
                "current_ratio": 1.5,
                "net_margin": 7.0,
                "debt_to_equity": 1.0,
                "asset_turnover": 1.0
            }
        }

        sector_benchmarks = benchmarks.get(sector, benchmarks["default"])
        comparisons = {}

        for ratio_category, ratios in all_ratios.items():
            for ratio_name, ratio_value in ratios.items():
                benchmark_value = sector_benchmarks.get(ratio_name)
                if benchmark_value:
                    if ratio_value > benchmark_value * 1.1:  # 10% above benchmark
                        performance = "above_benchmark"
                    elif ratio_value < benchmark_value * 0.9:  # 10% below benchmark
                        performance = "below_benchmark"
                    else:
                        performance = "at_benchmark"

                    comparisons[ratio_name] = {
                        "actual": ratio_value,
                        "benchmark": benchmark_value,
                        "performance": performance,
                        "difference_percent": ((ratio_value - benchmark_value) / benchmark_value) * 100
                    }

        return comparisons

    def _analyze_ratio_trends(self, all_ratios: Dict[str, Dict[str, float]], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in ratios (simplified without historical data)"""
        # This would require historical data for proper trend analysis
        # For now, return current ratio assessment
        return {
            "trend_analysis_available": False,
            "message": "Historical data required for trend analysis",
            "current_ratios_summary": {
                "total_ratios_calculated": sum(len(ratios) for ratios in all_ratios.values()),
                "categories_analyzed": list(all_ratios.keys())
            }
        }

    def _calculate_financial_trends(self, current_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends in key financial metrics"""
        trends = {}

        # Revenue trend
        revenues = []
        for hist_data in historical_data:
            revenue = hist_data.get("income_statement", {}).get("revenue", 0)
            if revenue > 0:
                revenues.append(revenue)

        current_revenue = current_data.get("income_statement", {}).get("revenue", 0)
        if current_revenue > 0:
            revenues.append(current_revenue)

        if len(revenues) >= 2:
            # Calculate growth rate
            growth_rate = ((revenues[-1] - revenues[0]) / revenues[0]) * 100
            trends["revenue_growth"] = {
                "values": revenues,
                "growth_rate_percent": growth_rate,
                "trend_direction": "increasing" if growth_rate > 0 else "decreasing"
            }

        return trends

    async def _generate_trend_insights(self, trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from trend analysis"""
        insights = {
            "positive_trends": [],
            "negative_trends": [],
            "stable_trends": []
        }

        for metric, trend_data in trend_analysis.items():
            if isinstance(trend_data, dict) and "growth_rate_percent" in trend_data:
                growth_rate = trend_data["growth_rate_percent"]

                if growth_rate > 5:
                    insights["positive_trends"].append({
                        "metric": metric,
                        "growth_rate": growth_rate,
                        "description": f"{metric} showing strong growth of {growth_rate:.1f}%"
                    })
                elif growth_rate < -5:
                    insights["negative_trends"].append({
                        "metric": metric,
                        "growth_rate": growth_rate,
                        "description": f"{metric} declining by {abs(growth_rate):.1f}%"
                    })
                else:
                    insights["stable_trends"].append({
                        "metric": metric,
                        "growth_rate": growth_rate,
                        "description": f"{metric} relatively stable with {growth_rate:.1f}% change"
                    })

        return insights

    def _assess_overall_trend_direction(self, trend_analysis: Dict[str, Any]) -> str:
        """Assess overall trend direction"""
        positive_trends = 0
        negative_trends = 0

        for trend_data in trend_analysis.values():
            if isinstance(trend_data, dict) and "growth_rate_percent" in trend_data:
                if trend_data["growth_rate_percent"] > 0:
                    positive_trends += 1
                else:
                    negative_trends += 1

        if positive_trends > negative_trends:
            return "improving"
        elif negative_trends > positive_trends:
            return "declining"
        else:
            return "stable"

    def _generate_simple_projections(self, trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple projections based on trends"""
        projections = {}

        for metric, trend_data in trend_analysis.items():
            if isinstance(trend_data, dict) and "values" in trend_data:
                values = trend_data["values"]
                if len(values) >= 2:
                    # Simple linear projection
                    avg_growth = trend_data.get("growth_rate_percent", 0) / 100
                    current_value = values[-1]
                    projected_value = current_value * (1 + avg_growth)

                    projections[metric] = {
                        "current_value": current_value,
                        "projected_value": projected_value,
                        "projection_method": "linear_trend",
                        "confidence": "low"  # Simple projection has low confidence
                    }

        return projections

    async def _generate_general_insights(self, financial_data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Generate general insights for unspecified analysis types"""
        try:
            insight_prompt = f"""
            قم بتحليل البيانات المالية التالية وقدم رؤى عامة:
            {json.dumps(financial_data, ensure_ascii=False)}

            نوع التحليل المطلوب: {analysis_type}

            Analyze the following financial data and provide general insights:
            {json.dumps(financial_data)}

            Required analysis type: {analysis_type}
            """

            response = await self.llm.ainvoke([{"role": "user", "content": insight_prompt}])

            return {
                "general_insights": response.content,
                "analysis_type": analysis_type,
                "insights_generated": True
            }

        except Exception as e:
            return {
                "general_insights": "General insights temporarily unavailable",
                "error": str(e)
            }

    def _generate_general_assessment(self, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general financial assessment"""
        assessment = {
            "overall_rating": "fair",
            "key_observations": [],
            "areas_for_improvement": []
        }

        # Basic assessment logic
        key_metrics = basic_analysis.get("key_metrics", {})

        if key_metrics.get("current_ratio", 0) > 1.5:
            assessment["key_observations"].append("Strong liquidity position")
        elif key_metrics.get("current_ratio", 0) < 1.0:
            assessment["areas_for_improvement"].append("Improve liquidity management")

        if key_metrics.get("net_profit_margin", 0) > 10:
            assessment["key_observations"].append("Strong profitability")
        elif key_metrics.get("net_profit_margin", 0) < 0:
            assessment["areas_for_improvement"].append("Address profitability issues")

        # Determine overall rating
        positive_indicators = len(assessment["key_observations"])
        negative_indicators = len(assessment["areas_for_improvement"])

        if positive_indicators > negative_indicators:
            assessment["overall_rating"] = "good"
        elif negative_indicators > positive_indicators:
            assessment["overall_rating"] = "poor"

        return assessment

    def _calculate_analysis_confidence(self, analysis_report) -> float:
        """Calculate confidence score for analysis results"""
        confidence = 0.7  # Base confidence

        # Increase confidence based on successful analyses
        if hasattr(analysis_report, 'execution_metadata'):
            success_rate = analysis_report.execution_metadata.get("successful_analyses", 0) / analysis_report.execution_metadata.get("total_analyses", 1)
            confidence += success_rate * 0.2

        # Increase confidence based on data completeness
        if hasattr(analysis_report, 'analysis_summary'):
            completeness = analysis_report.analysis_summary.get("success_rate", 0) / 100
            confidence += completeness * 0.1

        return min(1.0, max(0.1, confidence))

    def _extract_critical_alerts(self, analysis_report) -> List[Dict[str, Any]]:
        """Extract critical alerts from analysis report"""
        alerts = []

        if hasattr(analysis_report, 'analysis_summary') and analysis_report.analysis_summary.get("critical_alerts"):
            for alert in analysis_report.analysis_summary["critical_alerts"][:5]:  # Top 5 alerts
                alerts.append({
                    "type": alert.get("type", "warning"),
                    "title": alert.get("title_en", "Critical Issue"),
                    "title_ar": alert.get("title_ar", "مشكلة حرجة"),
                    "severity": alert.get("impact", "medium"),
                    "description": alert.get("description_en", ""),
                    "description_ar": alert.get("description_ar", "")
                })

        return alerts

    def _extract_key_metrics_for_specialization(self, specialization: str, analysis_report) -> Dict[str, Any]:
        """Extract key metrics for specific specialization"""
        key_metrics = {}

        if hasattr(analysis_report, 'category_results'):
            foundational_results = analysis_report.category_results.get("classical_foundational", [])

            for result in foundational_results:
                if hasattr(result, 'analysis_type') and specialization in result.analysis_type:
                    if hasattr(result, 'metrics'):
                        key_metrics.update(result.metrics)

        return key_metrics

    def _calculate_specialization_score(self, specialization: str, analysis_report) -> float:
        """Calculate performance score for specialization"""
        score = 75.0  # Base score

        # Extract relevant metrics and calculate score
        key_metrics = self._extract_key_metrics_for_specialization(specialization, analysis_report)

        if specialization == "liquidity_analysis":
            current_ratio = key_metrics.get("current_ratio", 1.0)
            if current_ratio > 1.5:
                score += 15
            elif current_ratio < 1.0:
                score -= 20

        elif specialization == "profitability_analysis":
            net_margin = key_metrics.get("net_profit_margin", 0)
            if net_margin > 10:
                score += 20
            elif net_margin < 0:
                score -= 25

        # Add more specialization-specific scoring logic as needed

        return min(100.0, max(0.0, score))

    def _filter_recommendations_by_specialization(self, specialization: str, all_recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter recommendations relevant to specialization"""
        relevant_recommendations = []

        specialization_keywords = {
            "liquidity_analysis": ["liquidity", "cash", "working capital", "current ratio"],
            "profitability_analysis": ["profit", "margin", "return", "earnings"],
            "efficiency_analysis": ["efficiency", "turnover", "utilization", "productivity"],
            "leverage_analysis": ["debt", "leverage", "capital structure", "interest"]
        }

        keywords = specialization_keywords.get(specialization, [])

        for rec in all_recommendations:
            title = rec.get("title_en", "").lower()
            category = rec.get("category", "").lower()

            if any(keyword in title or keyword in category for keyword in keywords):
                relevant_recommendations.append(rec)

        return relevant_recommendations[:5]  # Return top 5 relevant recommendations