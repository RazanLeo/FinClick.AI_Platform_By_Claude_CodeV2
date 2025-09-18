"""
Macroeconomic Agent
وكيل التحليل الاقتصادي الكلي

This agent analyzes macroeconomic indicators, monetary policy, fiscal policy,
and their impact on financial markets and investment decisions.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..core.agent_base import FinancialAgent, AgentType, AgentTask


class EconomicIndicator(Enum):
    """Macroeconomic indicators"""
    GDP_GROWTH = "gdp_growth"
    INFLATION_RATE = "inflation_rate"
    UNEMPLOYMENT_RATE = "unemployment_rate"
    INTEREST_RATES = "interest_rates"
    MONEY_SUPPLY = "money_supply"
    GOVERNMENT_DEBT = "government_debt"
    TRADE_BALANCE = "trade_balance"
    CURRENCY_EXCHANGE = "currency_exchange"
    OIL_PRICES = "oil_prices"
    COMMODITY_PRICES = "commodity_prices"


class PolicyType(Enum):
    """Economic policy types"""
    MONETARY_POLICY = "monetary_policy"
    FISCAL_POLICY = "fiscal_policy"
    TRADE_POLICY = "trade_policy"
    REGULATORY_POLICY = "regulatory_policy"


@dataclass
class EconomicForecast:
    """Economic forecast data"""
    indicator: EconomicIndicator
    current_value: float
    forecast_value: float
    forecast_period: str
    confidence_level: float
    supporting_factors: List[str]
    risk_factors: List[str]


class MacroeconomicAgent(FinancialAgent):
    """
    Specialized agent for macroeconomic analysis
    وكيل متخصص في التحليل الاقتصادي الكلي
    """

    def __init__(self, agent_id: str = "macroeconomic_agent",
                 agent_name_ar: str = "وكيل التحليل الاقتصادي الكلي",
                 agent_name_en: str = "Macroeconomic Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'MACROECONOMIC', 'macroeconomic')
        )

        self.economic_data = self._initialize_economic_data()
        self.policy_frameworks = self._initialize_policy_frameworks()
        self.forecasting_models = self._initialize_forecasting_models()

    def _initialize_capabilities(self) -> None:
        """Initialize macroeconomic analysis capabilities"""
        self.capabilities = {
            "economic_indicators": {
                "gdp_analysis": True,
                "inflation_analysis": True,
                "employment_analysis": True,
                "monetary_indicators": True,
                "fiscal_indicators": True,
                "trade_indicators": True
            },
            "policy_analysis": {
                "monetary_policy": True,
                "fiscal_policy": True,
                "central_bank_decisions": True,
                "government_policies": True
            },
            "forecasting": {
                "economic_forecasts": True,
                "policy_impact_analysis": True,
                "scenario_modeling": True,
                "risk_assessment": True
            },
            "regional_coverage": {
                "saudi_arabia": True,
                "gcc_countries": True,
                "global_markets": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_economic_data(self) -> Dict[str, Any]:
        """Initialize economic data and indicators"""
        return {
            "saudi_arabia": {
                "gdp_growth": {"current": 0.032, "historical": [0.025, 0.031, 0.028]},
                "inflation_rate": {"current": 0.025, "historical": [0.022, 0.028, 0.024]},
                "unemployment_rate": {"current": 0.049, "historical": [0.055, 0.052, 0.051]},
                "oil_revenues_share": {"current": 0.42, "target": 0.35},
                "non_oil_gdp_share": {"current": 0.52, "target": 0.65},
                "government_debt_gdp": {"current": 0.245, "target": 0.30}
            },
            "gcc_aggregate": {
                "gdp_growth": {"current": 0.038, "forecast": 0.042},
                "inflation_rate": {"current": 0.028, "forecast": 0.025},
                "oil_dependency": {"current": 0.65, "target": 0.50}
            },
            "global_context": {
                "us_fed_rate": {"current": 0.055, "trend": "stable"},
                "oil_price_brent": {"current": 85.0, "range": [70, 100]},
                "global_growth": {"current": 0.031, "forecast": 0.029}
            }
        }

    def _initialize_policy_frameworks(self) -> Dict[str, Any]:
        """Initialize policy analysis frameworks"""
        return {
            "monetary_policy": {
                "sama_tools": ["repo_rate", "reverse_repo", "reserve_requirements"],
                "transmission_channels": ["interest_rates", "credit_availability", "exchange_rate"],
                "policy_targets": {"inflation": 0.025, "growth": 0.045, "stability": True}
            },
            "fiscal_policy": {
                "tools": ["government_spending", "taxation", "subsidies", "transfers"],
                "objectives": ["economic_growth", "employment", "diversification", "stability"],
                "constraints": ["oil_revenues", "debt_sustainability", "fiscal_balance"]
            },
            "vision_2030": {
                "pillars": ["vibrant_society", "thriving_economy", "ambitious_nation"],
                "economic_targets": {
                    "non_oil_exports": {"current": 0.16, "target": 0.50},
                    "private_sector_gdp": {"current": 0.40, "target": 0.65},
                    "fdi_stock_gdp": {"current": 0.065, "target": 0.055}
                }
            }
        }

    def _initialize_forecasting_models(self) -> Dict[str, Any]:
        """Initialize economic forecasting models"""
        return {
            "gdp_model": {
                "factors": ["oil_prices", "government_spending", "private_investment", "exports"],
                "weights": [0.35, 0.25, 0.25, 0.15],
                "lag_periods": [1, 2, 1, 1]
            },
            "inflation_model": {
                "factors": ["oil_prices", "food_prices", "housing_costs", "exchange_rate"],
                "weights": [0.30, 0.25, 0.30, 0.15],
                "pass_through_rates": [0.15, 0.40, 0.60, 0.25]
            },
            "unemployment_model": {
                "factors": ["gdp_growth", "private_sector_jobs", "saudization_rate"],
                "elasticities": [-0.4, 0.6, -0.3]
            }
        }

    async def analyze_economic_indicators(self, region: str = "saudi_arabia") -> Dict[str, Any]:
        """
        Analyze current economic indicators
        تحليل المؤشرات الاقتصادية الحالية
        """
        try:
            regional_data = self.economic_data.get(region, {})
            if not regional_data:
                return {"error": f"No data available for region: {region}"}

            analysis = {
                "region": region,
                "analysis_date": datetime.now().isoformat(),
                "indicators_analysis": {},
                "overall_assessment": {},
                "trend_analysis": {},
                "policy_implications": []
            }

            # Analyze each economic indicator
            for indicator, data in regional_data.items():
                if isinstance(data, dict) and "current" in data:
                    indicator_analysis = await self._analyze_single_indicator(indicator, data)
                    analysis["indicators_analysis"][indicator] = indicator_analysis

            # Generate overall economic assessment
            analysis["overall_assessment"] = await self._generate_economic_assessment(analysis["indicators_analysis"])

            # Analyze trends
            analysis["trend_analysis"] = await self._analyze_economic_trends(regional_data)

            # Policy implications
            analysis["policy_implications"] = await self._identify_policy_implications(analysis)

            return analysis

        except Exception as e:
            return {"error": f"Economic indicators analysis failed: {str(e)}"}

    async def _analyze_single_indicator(self, indicator: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single economic indicator"""
        current_value = data.get("current", 0)
        historical = data.get("historical", [])
        target = data.get("target")
        
        analysis = {
            "current_value": current_value,
            "status": "stable",
            "trend": "neutral",
            "assessment": ""
        }

        # Trend analysis
        if historical:
            recent_avg = sum(historical[-3:]) / len(historical[-3:]) if len(historical) >= 3 else historical[-1]
            if current_value > recent_avg * 1.05:
                analysis["trend"] = "improving"
            elif current_value < recent_avg * 0.95:
                analysis["trend"] = "declining"
            else:
                analysis["trend"] = "stable"

        # Target comparison
        if target:
            if abs(current_value - target) / target < 0.05:
                analysis["status"] = "on_target"
            elif current_value > target:
                analysis["status"] = "above_target"
            else:
                analysis["status"] = "below_target"

        # Generate assessment
        if indicator == "gdp_growth":
            if current_value > 0.04:
                analysis["assessment"] = "نمو اقتصادي قوي"
            elif current_value > 0.02:
                analysis["assessment"] = "نمو اقتصادي معتدل"
            else:
                analysis["assessment"] = "نمو اقتصادي ضعيف"
        elif indicator == "inflation_rate":
            if current_value < 0.02:
                analysis["assessment"] = "تضخم منخفض"
            elif current_value < 0.04:
                analysis["assessment"] = "تضخم معتدل"
            else:
                analysis["assessment"] = "تضخم مرتفع"

        return analysis

    async def _generate_economic_assessment(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall economic assessment"""
        positive_indicators = 0
        negative_indicators = 0
        total_indicators = len(indicators)

        for indicator, analysis in indicators.items():
            if analysis.get("trend") == "improving":
                positive_indicators += 1
            elif analysis.get("trend") == "declining":
                negative_indicators += 1

        if positive_indicators > negative_indicators:
            overall_trend = "positive"
            outlook = "نظرة إيجابية"
        elif negative_indicators > positive_indicators:
            overall_trend = "negative"
            outlook = "نظرة سلبية"
        else:
            overall_trend = "mixed"
            outlook = "نظرة مختلطة"

        return {
            "overall_trend": overall_trend,
            "outlook": outlook,
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators,
            "stability_score": (total_indicators - negative_indicators) / total_indicators * 100
        }

    async def _analyze_economic_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze economic trends"""
        return {
            "short_term_trend": "مستقر",
            "medium_term_outlook": "إيجابي",
            "key_drivers": ["رؤية 2030", "أسعار النفط", "الإصلاحات الهيكلية"],
            "risk_factors": ["تقلبات أسعار النفط", "التوترات الجيوسياسية"]
        }

    async def _identify_policy_implications(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify policy implications from economic analysis"""
        implications = []
        
        overall_trend = analysis.get("overall_assessment", {}).get("overall_trend", "mixed")
        
        if overall_trend == "positive":
            implications.extend([
                "متابعة السياسات الحالية",
                "التركيز على تعزيز النمو"
            ])
        elif overall_trend == "negative":
            implications.extend([
                "الحاجة لتحفيز اقتصادي",
                "مراجعة السياسات النقدية والمالية"
            ])
        
        return implications

    async def forecast_economic_indicators(self, forecast_period: str = "12_months") -> Dict[str, Any]:
        """
        Generate economic forecasts
        إنشاء التنبؤات الاقتصادية
        """
        try:
            forecasts = {
                "forecast_period": forecast_period,
                "forecast_date": datetime.now().isoformat(),
                "economic_forecasts": {},
                "confidence_levels": {},
                "scenario_analysis": {},
                "key_assumptions": []
            }

            # Generate forecasts for key indicators
            indicators_to_forecast = ["gdp_growth", "inflation_rate", "unemployment_rate"]
            
            for indicator in indicators_to_forecast:
                forecast = await self._generate_indicator_forecast(indicator, forecast_period)
                forecasts["economic_forecasts"][indicator] = forecast

            # Scenario analysis
            forecasts["scenario_analysis"] = await self._generate_scenario_forecasts()

            # Key assumptions
            forecasts["key_assumptions"] = [
                "استقرار أسعار النفط في نطاق 70-90 دولار",
                "استمرار تنفيذ مشاريع رؤية 2030",
                "عدم حدوث صدمات اقتصادية جوهرية"
            ]

            return forecasts

        except Exception as e:
            return {"error": f"Economic forecasting failed: {str(e)}"}

    async def _generate_indicator_forecast(self, indicator: str, period: str) -> Dict[str, Any]:
        """Generate forecast for specific indicator"""
        current_data = self.economic_data["saudi_arabia"].get(indicator, {})
        current_value = current_data.get("current", 0)
        
        # Simple trend-based forecasting
        if indicator == "gdp_growth":
            forecast_value = current_value * 1.1  # Assume 10% improvement
            confidence = 0.75
        elif indicator == "inflation_rate":
            forecast_value = current_value * 0.95  # Assume slight decline
            confidence = 0.80
        elif indicator == "unemployment_rate":
            forecast_value = current_value * 0.90  # Assume improvement
            confidence = 0.70
        else:
            forecast_value = current_value
            confidence = 0.60

        return {
            "current_value": current_value,
            "forecast_value": forecast_value,
            "confidence_level": confidence,
            "change_percentage": ((forecast_value - current_value) / current_value * 100) if current_value != 0 else 0
        }

    async def _generate_scenario_forecasts(self) -> Dict[str, Any]:
        """Generate scenario-based forecasts"""
        return {
            "base_case": {
                "description": "السيناريو الأساسي",
                "gdp_growth": 0.042,
                "probability": 0.6
            },
            "optimistic": {
                "description": "السيناريو المتفائل",
                "gdp_growth": 0.055,
                "probability": 0.2
            },
            "pessimistic": {
                "description": "السيناريو المتشائم",
                "gdp_growth": 0.025,
                "probability": 0.2
            }
        }

    async def analyze_policy_impact(self, policy_type: PolicyType, policy_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze impact of economic policy changes
        تحليل تأثير تغييرات السياسة الاقتصادية
        """
        try:
            analysis = {
                "policy_type": policy_type.value,
                "policy_details": policy_details,
                "impact_assessment": {},
                "transmission_channels": [],
                "timeline": {},
                "recommendations": []
            }

            if policy_type == PolicyType.MONETARY_POLICY:
                analysis = await self._analyze_monetary_policy_impact(policy_details, analysis)
            elif policy_type == PolicyType.FISCAL_POLICY:
                analysis = await self._analyze_fiscal_policy_impact(policy_details, analysis)

            return analysis

        except Exception as e:
            return {"error": f"Policy impact analysis failed: {str(e)}"}

    async def _analyze_monetary_policy_impact(self, policy_details: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze monetary policy impact"""
        rate_change = policy_details.get("interest_rate_change", 0)
        
        analysis["impact_assessment"] = {
            "inflation": "decrease" if rate_change > 0 else "increase",
            "growth": "decrease" if rate_change > 0 else "increase",
            "currency": "strengthen" if rate_change > 0 else "weaken",
            "investment": "decrease" if rate_change > 0 else "increase"
        }
        
        analysis["transmission_channels"] = [
            "قناة أسعار الفائدة",
            "قناة الائتمان المصرفي",
            "قناة سعر الصرف"
        ]
        
        return analysis

    async def _analyze_fiscal_policy_impact(self, policy_details: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fiscal policy impact"""
        spending_change = policy_details.get("government_spending_change", 0)
        
        analysis["impact_assessment"] = {
            "growth": "increase" if spending_change > 0 else "decrease",
            "employment": "increase" if spending_change > 0 else "decrease",
            "debt": "increase" if spending_change > 0 else "decrease",
            "private_sector": "crowding_out" if spending_change > 0 else "crowding_in"
        }
        
        return analysis

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process macroeconomic analysis tasks"""
        try:
            task_type = task.task_data.get("type", "analyze_indicators")

            if task_type == "analyze_indicators":
                region = task.task_data.get("region", "saudi_arabia")
                return await self.analyze_economic_indicators(region)

            elif task_type == "forecast_indicators":
                period = task.task_data.get("forecast_period", "12_months")
                return await self.forecast_economic_indicators(period)

            elif task_type == "analyze_policy":
                policy_type = PolicyType(task.task_data.get("policy_type", "monetary_policy"))
                policy_details = task.task_data.get("policy_details", {})
                return await self.analyze_policy_impact(policy_type, policy_details)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}