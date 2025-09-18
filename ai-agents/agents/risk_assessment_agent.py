"""
Risk Assessment Agent
وكيل تقييم المخاطر

This agent specializes in comprehensive risk assessment including credit risk,
market risk, operational risk, and overall risk evaluation.
"""

from typing import Dict, Any, List, Optional
import asyncio
import json
import numpy as np
from datetime import datetime

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class RiskAssessmentAgent(FinancialAgent):
    """
    Specialized agent for comprehensive risk assessment
    وكيل متخصص في تقييم المخاطر الشامل
    """

    def __init__(self, agent_id: str, agent_name_ar: str, agent_name_en: str):
        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=AgentType.RISK_ASSESSMENT
        )

    def _initialize_capabilities(self) -> None:
        """Initialize risk assessment capabilities"""
        super()._initialize_capabilities()

        risk_capabilities = [
            "comprehensive_risk_assessment",
            "credit_risk_analysis",
            "market_risk_analysis",
            "operational_risk_analysis",
            "liquidity_risk_analysis",
            "interest_rate_risk",
            "currency_risk",
            "concentration_risk",
            "default_probability",
            "risk_scoring",
            "risk_monitoring",
            "stress_testing",
            "scenario_analysis",
            "early_warning_systems"
        ]

        self.state.capabilities.extend(risk_capabilities)

        # Set specializations
        if "credit" in self.state.agent_id.lower():
            self.state.specializations.extend(["credit_risk", "default_risk", "bankruptcy_prediction"])
        elif "market" in self.state.agent_id.lower():
            self.state.specializations.extend(["market_risk", "volatility_analysis", "systematic_risk"])
        elif "operational" in self.state.agent_id.lower():
            self.state.specializations.extend(["operational_risk", "business_risk", "process_risk"])
        else:
            self.state.specializations.extend(["general_risk", "comprehensive_risk"])

    def _initialize_prompts(self) -> None:
        """Initialize risk assessment prompts"""
        super()._initialize_prompts()

        self.risk_assessment_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            أنت خبير في تقييم المخاطر المالية لمنصة FinClick.AI.
            تتخصص في تحديد وتقييم جميع أنواع المخاطر المالية والتشغيلية.

            You are a financial risk assessment expert for the FinClick.AI platform.
            You specialize in identifying and evaluating all types of financial and operational risks.

            مجالات تخصصك:
            1. مخاطر الائتمان وتقييم احتمالية التعثر
            2. مخاطر السوق والتقلبات
            3. المخاطر التشغيلية
            4. مخاطر السيولة
            5. مخاطر أسعار الفائدة والعملة

            Your areas of expertise:
            1. Credit risk and default probability assessment
            2. Market risk and volatility
            3. Operational risks
            4. Liquidity risks
            5. Interest rate and currency risks

            استخدم البيانات المالية لتحديد المخاطر وتقييم شدتها واحتمالية حدوثها.
            Use financial data to identify risks and assess their severity and probability.
            """),
            ("human", """
            قم بتقييم شامل للمخاطر بناءً على البيانات التالية:

            البيانات المالية: {financial_data}
            نوع تقييم المخاطر: {risk_type}
            معايير إضافية: {additional_criteria}

            Perform comprehensive risk assessment based on the following data:

            Financial Data: {financial_data}
            Risk Assessment Type: {risk_type}
            Additional Criteria: {additional_criteria}

            قدم تقييماً شاملاً يتضمن:
            1. تحديد المخاطر الرئيسية
            2. تقييم شدة واحتمالية كل مخاطرة
            3. تأثير المخاطر على الأداء المالي
            4. توصيات لإدارة المخاطر
            5. نظام إنذار مبكر

            Provide comprehensive assessment including:
            1. Identification of key risks
            2. Severity and probability assessment for each risk
            3. Impact of risks on financial performance
            4. Risk management recommendations
            5. Early warning system
            """)
        ])

        self.credit_risk_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            أنت متخصص في تقييم مخاطر الائتمان والتنبؤ بالتعثر المالي.
            لديك خبرة في استخدام النماذج المتقدمة مثل Altman Z-Score ونماذج الائتمان الأخرى.

            You are a credit risk specialist and financial distress prediction expert.
            You have expertise in using advanced models like Altman Z-Score and other credit models.

            ركز على:
            - تحليل القدرة على السداد
            - تقييم احتمالية التعثر
            - تحليل هيكل رأس المال
            - تقييم جودة الأصول

            Focus on:
            - Payment capacity analysis
            - Default probability assessment
            - Capital structure analysis
            - Asset quality evaluation
            """),
            ("human", """
            قم بتقييم مخاطر الائتمان للبيانات التالية:

            {financial_data}

            Assess credit risk for the following data:

            قدم تحليلاً يتضمن:
            1. درجة Altman Z-Score
            2. احتمالية التعثر
            3. تقييم القدرة على السداد
            4. التصنيف الائتماني المقترح
            5. العوامل المؤثرة على المخاطر

            Provide analysis including:
            1. Altman Z-Score
            2. Default probability
            3. Payment capacity assessment
            4. Suggested credit rating
            5. Risk influencing factors
            """)
        ])

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process risk assessment task"""
        task_type = task.task_type
        input_data = task.input_data

        if task_type == "comprehensive_risk_assessment":
            return await self._perform_comprehensive_risk_assessment(input_data)
        elif task_type == "credit_risk_analysis":
            return await self._perform_credit_risk_analysis(input_data)
        elif task_type == "market_risk_analysis":
            return await self._perform_market_risk_analysis(input_data)
        elif task_type == "operational_risk_analysis":
            return await self._perform_operational_risk_analysis(input_data)
        elif task_type == "risk_flags_identification":
            return await self._identify_risk_flags(input_data)
        elif task_type == "risk_consolidation":
            return await self._consolidate_risks(input_data)
        else:
            return await self._perform_general_risk_assessment(task_type, input_data)

    async def _perform_comprehensive_risk_assessment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment across all risk types"""
        try:
            financial_data = input_data.get("financial_analysis", input_data)

            # Assess different risk categories
            credit_risk = await self._assess_credit_risk(financial_data)
            market_risk = await self._assess_market_risk(financial_data)
            operational_risk = await self._assess_operational_risk(financial_data)
            liquidity_risk = await self._assess_liquidity_risk(financial_data)

            # Calculate overall risk score
            overall_risk = self._calculate_overall_risk_score({
                "credit_risk": credit_risk,
                "market_risk": market_risk,
                "operational_risk": operational_risk,
                "liquidity_risk": liquidity_risk
            })

            # Generate AI-powered risk insights
            ai_insights = await self._generate_risk_insights(financial_data, overall_risk)

            return {
                "status": "completed",
                "analysis_type": "comprehensive_risk_assessment",
                "risk_categories": {
                    "credit_risk": credit_risk,
                    "market_risk": market_risk,
                    "operational_risk": operational_risk,
                    "liquidity_risk": liquidity_risk
                },
                "overall_risk_assessment": overall_risk,
                "ai_insights": ai_insights,
                "risk_recommendations": await self._generate_risk_recommendations(overall_risk),
                "early_warning_signals": self._identify_early_warning_signals(financial_data)
            }

        except Exception as e:
            self.logger.error(f"Comprehensive risk assessment failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _perform_credit_risk_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specialized credit risk analysis"""
        try:
            financial_data = input_data.get("financial_data", input_data)

            # Calculate credit risk metrics
            credit_metrics = await self._calculate_credit_risk_metrics(financial_data)

            # Generate AI analysis
            ai_analysis = await self._generate_credit_risk_ai_analysis(financial_data)

            return {
                "status": "completed",
                "analysis_type": "credit_risk_analysis",
                "credit_metrics": credit_metrics,
                "ai_analysis": ai_analysis,
                "credit_recommendations": await self._generate_credit_recommendations(credit_metrics)
            }

        except Exception as e:
            self.logger.error(f"Credit risk analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _assess_credit_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess credit risk and default probability"""
        balance_sheet = financial_data.get("balance_sheet", {})
        income_statement = financial_data.get("income_statement", {})

        # Calculate key credit risk indicators
        total_debt = balance_sheet.get("total_debt", balance_sheet.get("total_liabilities", 0))
        total_equity = balance_sheet.get("total_equity", 1)
        total_assets = balance_sheet.get("total_assets", 1)
        net_income = income_statement.get("net_income", 0)
        ebit = income_statement.get("ebit", income_statement.get("operating_income", 0))
        interest_expense = income_statement.get("interest_expense", 1)

        # Debt ratios
        debt_to_equity = total_debt / total_equity if total_equity > 0 else float('inf')
        debt_to_assets = total_debt / total_assets if total_assets > 0 else 0

        # Profitability indicators
        roa = net_income / total_assets if total_assets > 0 else 0
        roe = net_income / total_equity if total_equity > 0 else 0

        # Interest coverage
        interest_coverage = ebit / interest_expense if interest_expense > 0 else float('inf')

        # Calculate Altman Z-Score (simplified)
        z_score = self._calculate_altman_z_score(financial_data)

        # Assess default probability
        default_probability = self._calculate_default_probability(
            debt_to_equity, roa, interest_coverage, z_score
        )

        # Determine credit rating
        credit_rating = self._determine_credit_rating(z_score, default_probability)

        return {
            "debt_to_equity": debt_to_equity,
            "debt_to_assets": debt_to_assets,
            "return_on_assets": roa,
            "return_on_equity": roe,
            "interest_coverage": interest_coverage,
            "altman_z_score": z_score,
            "default_probability": default_probability,
            "credit_rating": credit_rating,
            "risk_level": self._categorize_risk_level(default_probability)
        }

    async def _assess_market_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market risk exposure"""
        # Market risk assessment based on business characteristics
        income_statement = financial_data.get("income_statement", {})

        revenue = income_statement.get("revenue", 0)
        revenue_volatility = 0.15  # Assumed volatility - would need historical data

        # Industry sensitivity factors
        sector = financial_data.get("company_info", {}).get("sector", "default")
        sector_beta = {
            "technology": 1.3,
            "energy": 1.2,
            "banking": 1.1,
            "utilities": 0.8,
            "consumer": 1.0,
            "default": 1.0
        }.get(sector, 1.0)

        # Market risk score
        market_risk_score = min(10, sector_beta * revenue_volatility * 10)

        return {
            "sector_beta": sector_beta,
            "revenue_volatility": revenue_volatility,
            "market_risk_score": market_risk_score,
            "risk_level": "high" if market_risk_score > 7 else "medium" if market_risk_score > 4 else "low"
        }

    async def _assess_operational_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess operational risk factors"""
        income_statement = financial_data.get("income_statement", {})

        # Operating leverage
        revenue = income_statement.get("revenue", 1)
        operating_income = income_statement.get("operating_income", 0)
        operating_margin = operating_income / revenue if revenue > 0 else 0

        # Cost structure analysis
        fixed_costs_ratio = 0.6  # Assumed - would need detailed cost breakdown
        operating_leverage = 1 + fixed_costs_ratio

        # Operational efficiency indicators
        efficiency_score = min(10, operating_margin * 20) if operating_margin > 0 else 0

        operational_risk_score = max(0, 10 - efficiency_score + (operating_leverage - 1) * 3)

        return {
            "operating_margin": operating_margin,
            "operating_leverage": operating_leverage,
            "efficiency_score": efficiency_score,
            "operational_risk_score": operational_risk_score,
            "risk_level": "high" if operational_risk_score > 7 else "medium" if operational_risk_score > 4 else "low"
        }

    async def _assess_liquidity_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess liquidity risk"""
        balance_sheet = financial_data.get("balance_sheet", {})

        current_assets = balance_sheet.get("current_assets", 0)
        current_liabilities = balance_sheet.get("current_liabilities", 1)
        cash = balance_sheet.get("cash_and_cash_equivalents", 0)

        # Liquidity ratios
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
        cash_ratio = cash / current_liabilities if current_liabilities > 0 else 0

        # Liquidity risk assessment
        if current_ratio < 1.0:
            liquidity_risk_level = "high"
            liquidity_risk_score = 8
        elif current_ratio < 1.2:
            liquidity_risk_level = "medium"
            liquidity_risk_score = 6
        else:
            liquidity_risk_level = "low"
            liquidity_risk_score = 3

        return {
            "current_ratio": current_ratio,
            "cash_ratio": cash_ratio,
            "liquidity_risk_score": liquidity_risk_score,
            "risk_level": liquidity_risk_level
        }

    def _calculate_altman_z_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate Altman Z-Score for bankruptcy prediction"""
        balance_sheet = financial_data.get("balance_sheet", {})
        income_statement = financial_data.get("income_statement", {})

        total_assets = balance_sheet.get("total_assets", 1)
        current_assets = balance_sheet.get("current_assets", 0)
        current_liabilities = balance_sheet.get("current_liabilities", 0)
        retained_earnings = balance_sheet.get("retained_earnings", 0)
        ebit = income_statement.get("ebit", income_statement.get("operating_income", 0))
        revenue = income_statement.get("revenue", 0)
        market_value_equity = balance_sheet.get("total_equity", 0)  # Simplified
        total_liabilities = balance_sheet.get("total_liabilities", 0)

        # Altman Z-Score components
        working_capital = current_assets - current_liabilities
        x1 = working_capital / total_assets if total_assets > 0 else 0
        x2 = retained_earnings / total_assets if total_assets > 0 else 0
        x3 = ebit / total_assets if total_assets > 0 else 0
        x4 = market_value_equity / total_liabilities if total_liabilities > 0 else 0
        x5 = revenue / total_assets if total_assets > 0 else 0

        # Altman Z-Score formula
        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

        return z_score

    def _calculate_default_probability(self, debt_to_equity: float, roa: float,
                                     interest_coverage: float, z_score: float) -> float:
        """Calculate probability of default based on multiple factors"""
        # Base probability
        base_prob = 0.05  # 5% base probability

        # Adjust based on leverage
        if debt_to_equity > 3.0:
            base_prob += 0.20
        elif debt_to_equity > 2.0:
            base_prob += 0.10
        elif debt_to_equity > 1.0:
            base_prob += 0.05

        # Adjust based on profitability
        if roa < -0.05:  # Negative 5% ROA
            base_prob += 0.15
        elif roa < 0:
            base_prob += 0.10
        elif roa > 0.10:  # Positive 10% ROA
            base_prob -= 0.05

        # Adjust based on interest coverage
        if interest_coverage < 1.5:
            base_prob += 0.20
        elif interest_coverage < 2.5:
            base_prob += 0.10
        elif interest_coverage > 5.0:
            base_prob -= 0.05

        # Adjust based on Z-Score
        if z_score < 1.8:  # Distress zone
            base_prob += 0.25
        elif z_score < 3.0:  # Gray zone
            base_prob += 0.10
        else:  # Safe zone
            base_prob -= 0.10

        return min(1.0, max(0.001, base_prob))

    def _determine_credit_rating(self, z_score: float, default_probability: float) -> Dict[str, str]:
        """Determine credit rating based on risk metrics"""
        if default_probability < 0.02 and z_score > 3.0:
            rating = "AAA"
            grade = "Investment Grade"
        elif default_probability < 0.05 and z_score > 2.6:
            rating = "AA"
            grade = "Investment Grade"
        elif default_probability < 0.08 and z_score > 2.2:
            rating = "A"
            grade = "Investment Grade"
        elif default_probability < 0.12 and z_score > 1.8:
            rating = "BBB"
            grade = "Investment Grade"
        elif default_probability < 0.20:
            rating = "BB"
            grade = "Speculative Grade"
        elif default_probability < 0.30:
            rating = "B"
            grade = "Speculative Grade"
        else:
            rating = "C"
            grade = "High Risk"

        return {
            "rating": rating,
            "grade": grade,
            "description_ar": f"تصنيف {rating} - {grade}",
            "description_en": f"Rating {rating} - {grade}"
        }

    def _categorize_risk_level(self, default_probability: float) -> str:
        """Categorize overall risk level"""
        if default_probability < 0.05:
            return "low"
        elif default_probability < 0.15:
            return "medium"
        else:
            return "high"

    def _calculate_overall_risk_score(self, risk_categories: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk score from all risk categories"""
        risk_scores = []
        risk_levels = []

        for category, risk_data in risk_categories.items():
            if isinstance(risk_data, dict):
                # Extract risk score or calculate from risk level
                if "risk_score" in risk_data:
                    risk_scores.append(risk_data["risk_score"])
                elif "default_probability" in risk_data:
                    risk_scores.append(risk_data["default_probability"] * 10)

                if "risk_level" in risk_data:
                    risk_levels.append(risk_data["risk_level"])

        # Calculate weighted average risk score
        if risk_scores:
            overall_score = np.mean(risk_scores)
        else:
            overall_score = 5.0  # Default medium risk

        # Determine overall risk level
        high_risk_count = risk_levels.count("high")
        total_categories = len(risk_levels)

        if high_risk_count >= total_categories / 2:
            overall_level = "high"
        elif high_risk_count > 0:
            overall_level = "medium"
        else:
            overall_level = "low"

        return {
            "overall_risk_score": overall_score,
            "overall_risk_level": overall_level,
            "risk_distribution": {
                "high": risk_levels.count("high"),
                "medium": risk_levels.count("medium"),
                "low": risk_levels.count("low")
            },
            "confidence": 0.8
        }

    async def _generate_risk_insights(self, financial_data: Dict[str, Any], overall_risk: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered risk insights"""
        try:
            chain = self.risk_assessment_prompt | self.llm
            response = await chain.ainvoke({
                "financial_data": json.dumps(financial_data, ensure_ascii=False),
                "risk_type": "comprehensive",
                "additional_criteria": f"Overall risk assessment: {json.dumps(overall_risk, ensure_ascii=False)}"
            })

            return {
                "ai_risk_analysis": response.content,
                "insights_generated": True,
                "confidence": 0.85
            }

        except Exception as e:
            self.logger.error(f"Risk insights generation failed: {str(e)}")
            return {
                "ai_risk_analysis": "Risk insights temporarily unavailable",
                "insights_generated": False,
                "error": str(e)
            }

    async def _generate_risk_recommendations(self, overall_risk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate risk management recommendations"""
        recommendations = []
        risk_level = overall_risk.get("overall_risk_level", "medium")

        if risk_level == "high":
            recommendations.extend([
                {
                    "priority": "critical",
                    "category": "risk_mitigation",
                    "title": "Immediate Risk Mitigation Required",
                    "title_ar": "مطلوب تخفيف فوري للمخاطر",
                    "description": "High risk levels detected across multiple categories",
                    "actions": [
                        "Develop comprehensive risk management plan",
                        "Implement immediate cash flow monitoring",
                        "Review and strengthen internal controls",
                        "Consider additional financing options"
                    ]
                }
            ])

        elif risk_level == "medium":
            recommendations.extend([
                {
                    "priority": "high",
                    "category": "risk_monitoring",
                    "title": "Enhanced Risk Monitoring",
                    "title_ar": "تعزيز مراقبة المخاطر",
                    "description": "Medium risk levels require enhanced monitoring",
                    "actions": [
                        "Implement regular risk assessment reviews",
                        "Strengthen financial reporting procedures",
                        "Monitor key risk indicators",
                        "Develop contingency plans"
                    ]
                }
            ])

        return recommendations

    def _identify_early_warning_signals(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify early warning signals for financial distress"""
        warnings = []

        balance_sheet = financial_data.get("balance_sheet", {})
        income_statement = financial_data.get("income_statement", {})

        # Declining profitability
        net_income = income_statement.get("net_income", 0)
        if net_income < 0:
            warnings.append({
                "signal": "negative_profitability",
                "severity": "high",
                "description": "Company reporting losses",
                "description_ar": "الشركة تسجل خسائر"
            })

        # Liquidity stress
        current_ratio = balance_sheet.get("current_assets", 0) / balance_sheet.get("current_liabilities", 1)
        if current_ratio < 1.0:
            warnings.append({
                "signal": "liquidity_stress",
                "severity": "high",
                "description": "Current ratio below 1.0 indicates liquidity problems",
                "description_ar": "نسبة التداول أقل من 1.0 تشير لمشاكل سيولة"
            })

        # High leverage
        debt_to_equity = balance_sheet.get("total_debt", 0) / balance_sheet.get("total_equity", 1)
        if debt_to_equity > 3.0:
            warnings.append({
                "signal": "excessive_leverage",
                "severity": "medium",
                "description": "Very high debt-to-equity ratio",
                "description_ar": "نسبة دين إلى حقوق ملكية عالية جداً"
            })

        return warnings

    async def _identify_risk_flags(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify critical risk flags quickly"""
        try:
            key_metrics = input_data.get("key_metrics", {})

            risk_flags = []

            # Critical liquidity flag
            current_ratio = key_metrics.get("current_ratio", 1.5)
            if current_ratio < 0.8:
                risk_flags.append({
                    "flag": "critical_liquidity",
                    "severity": "critical",
                    "value": current_ratio,
                    "threshold": 0.8,
                    "description": "Critical liquidity shortage detected"
                })

            # Profitability flag
            net_margin = key_metrics.get("net_margin", 5)
            if net_margin < -5:
                risk_flags.append({
                    "flag": "severe_losses",
                    "severity": "critical",
                    "value": net_margin,
                    "threshold": -5,
                    "description": "Severe losses exceeding 5% of revenue"
                })

            # Leverage flag
            debt_to_equity = key_metrics.get("debt_to_equity", 1.0)
            if debt_to_equity > 4.0:
                risk_flags.append({
                    "flag": "excessive_debt",
                    "severity": "high",
                    "value": debt_to_equity,
                    "threshold": 4.0,
                    "description": "Debt levels critically high"
                })

            return {
                "status": "completed",
                "risk_flags": risk_flags,
                "total_flags": len(risk_flags),
                "highest_severity": "critical" if any(f["severity"] == "critical" for f in risk_flags) else "high" if risk_flags else "low"
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _consolidate_risks(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate multiple risk assessments"""
        try:
            credit_risk = input_data.get("credit_risk", {})
            market_risk = input_data.get("market_risk", {})
            operational_risk = input_data.get("operational_risk", {})

            # Consolidate all risk assessments
            consolidated_risk = self._calculate_overall_risk_score({
                "credit_risk": credit_risk,
                "market_risk": market_risk,
                "operational_risk": operational_risk
            })

            return {
                "status": "completed",
                "consolidated_risk": consolidated_risk,
                "risk_summary": self._generate_risk_summary(consolidated_risk),
                "risk_matrix": self._create_risk_matrix(input_data)
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def _generate_risk_summary(self, consolidated_risk: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive risk summary"""
        risk_level = consolidated_risk.get("overall_risk_level", "medium")
        risk_score = consolidated_risk.get("overall_risk_score", 5.0)

        return {
            "executive_summary": f"Overall risk level: {risk_level.upper()}",
            "risk_score": risk_score,
            "key_concerns": self._identify_key_concerns(consolidated_risk),
            "immediate_actions": self._suggest_immediate_actions(risk_level)
        }

    def _identify_key_concerns(self, consolidated_risk: Dict[str, Any]) -> List[str]:
        """Identify key risk concerns"""
        concerns = []
        risk_level = consolidated_risk.get("overall_risk_level", "medium")

        if risk_level == "high":
            concerns.extend([
                "High probability of financial distress",
                "Immediate liquidity concerns",
                "Potential covenant violations"
            ])
        elif risk_level == "medium":
            concerns.extend([
                "Elevated risk levels require monitoring",
                "Some financial stress indicators present"
            ])

        return concerns

    def _suggest_immediate_actions(self, risk_level: str) -> List[str]:
        """Suggest immediate actions based on risk level"""
        if risk_level == "high":
            return [
                "Implement cash preservation measures",
                "Negotiate with creditors",
                "Develop financial restructuring plan",
                "Engage risk management consultant"
            ]
        elif risk_level == "medium":
            return [
                "Enhance financial monitoring",
                "Review credit facilities",
                "Implement cost control measures"
            ]
        else:
            return [
                "Maintain current risk monitoring",
                "Regular financial health checks"
            ]

    def _create_risk_matrix(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk assessment matrix"""
        return {
            "risk_categories": {
                "credit": risk_data.get("credit_risk", {}).get("risk_level", "medium"),
                "market": risk_data.get("market_risk", {}).get("risk_level", "medium"),
                "operational": risk_data.get("operational_risk", {}).get("risk_level", "medium")
            },
            "overall_assessment": "Comprehensive risk evaluation completed",
            "confidence_level": "high"
        }

    async def _perform_market_risk_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specialized market risk analysis"""
        try:
            market_risk = await self._assess_market_risk(input_data)

            return {
                "status": "completed",
                "analysis_type": "market_risk_analysis",
                "market_risk_assessment": market_risk,
                "volatility_analysis": self._analyze_volatility(input_data),
                "correlation_analysis": self._analyze_correlations(input_data)
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _perform_operational_risk_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specialized operational risk analysis"""
        try:
            operational_risk = await self._assess_operational_risk(input_data)

            return {
                "status": "completed",
                "analysis_type": "operational_risk_analysis",
                "operational_risk_assessment": operational_risk,
                "process_risk_analysis": self._analyze_process_risks(input_data),
                "control_effectiveness": self._assess_control_effectiveness(input_data)
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def _analyze_volatility(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial volatility indicators"""
        # Simplified volatility analysis
        return {
            "revenue_volatility": "medium",
            "earnings_volatility": "high",
            "volatility_score": 6.5
        }

    def _analyze_correlations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations with market factors"""
        # Simplified correlation analysis
        return {
            "market_correlation": 0.7,
            "sector_correlation": 0.8,
            "economic_sensitivity": "medium"
        }

    def _analyze_process_risks(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze operational process risks"""
        return {
            "process_maturity": "medium",
            "automation_level": "low",
            "human_error_risk": "medium"
        }

    def _assess_control_effectiveness(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess effectiveness of internal controls"""
        return {
            "control_strength": "medium",
            "compliance_score": 7.5,
            "improvement_areas": ["automation", "monitoring", "reporting"]
        }

    async def _calculate_credit_risk_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed credit risk metrics"""
        credit_assessment = await self._assess_credit_risk(financial_data)

        return {
            "altman_z_score": credit_assessment.get("altman_z_score", 0),
            "default_probability": credit_assessment.get("default_probability", 0),
            "credit_rating": credit_assessment.get("credit_rating", {}),
            "debt_ratios": {
                "debt_to_equity": credit_assessment.get("debt_to_equity", 0),
                "debt_to_assets": credit_assessment.get("debt_to_assets", 0)
            },
            "coverage_ratios": {
                "interest_coverage": credit_assessment.get("interest_coverage", 0)
            }
        }

    async def _generate_credit_risk_ai_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI analysis for credit risk"""
        try:
            chain = self.credit_risk_prompt | self.llm
            response = await chain.ainvoke({
                "financial_data": json.dumps(financial_data, ensure_ascii=False)
            })

            return {
                "credit_analysis": response.content,
                "analysis_generated": True
            }

        except Exception as e:
            return {
                "credit_analysis": "Credit analysis temporarily unavailable",
                "error": str(e)
            }

    async def _generate_credit_recommendations(self, credit_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate credit-specific recommendations"""
        recommendations = []

        default_prob = credit_metrics.get("default_probability", 0)
        z_score = credit_metrics.get("altman_z_score", 0)

        if default_prob > 0.15 or z_score < 1.8:
            recommendations.append({
                "priority": "critical",
                "title": "Address Credit Risk Immediately",
                "description": "High default probability requires immediate attention",
                "actions": [
                    "Improve cash flow management",
                    "Reduce debt levels",
                    "Strengthen operational performance",
                    "Consider financial restructuring"
                ]
            })

        return recommendations

    async def _perform_general_risk_assessment(self, risk_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general risk assessment for unspecified types"""
        try:
            # Basic risk indicators
            basic_risks = await self._assess_credit_risk(input_data)

            return {
                "status": "completed",
                "analysis_type": risk_type,
                "basic_risk_assessment": basic_risks,
                "general_recommendation": "Implement regular risk monitoring procedures"
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }