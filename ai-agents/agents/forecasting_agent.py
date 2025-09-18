"""
Forecasting Agent
وكيل التنبؤات المالية

This agent specializes in financial forecasting and predictive analytics using
advanced statistical models, machine learning, and economic indicators.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import math

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class ForecastHorizon(Enum):
    """Forecast time horizons"""
    SHORT_TERM = "short_term"      # 1-3 months
    MEDIUM_TERM = "medium_term"    # 3-12 months
    LONG_TERM = "long_term"        # 1-5 years
    STRATEGIC = "strategic"        # 5+ years


class ForecastMethod(Enum):
    """Forecasting methodologies"""
    TIME_SERIES = "time_series"
    REGRESSION = "regression"
    MACHINE_LEARNING = "machine_learning"
    ECONOMETRIC = "econometric"
    SCENARIO_ANALYSIS = "scenario_analysis"
    MONTE_CARLO = "monte_carlo"
    ARIMA = "arima"
    NEURAL_NETWORK = "neural_network"


class ForecastConfidence(Enum):
    """Confidence levels for forecasts"""
    VERY_HIGH = "very_high"    # 95%+
    HIGH = "high"              # 85-95%
    MEDIUM = "medium"          # 70-85%
    LOW = "low"               # 50-70%
    VERY_LOW = "very_low"     # <50%


@dataclass
class ForecastResult:
    """Represents a forecast result"""
    metric_name: str
    forecast_horizon: ForecastHorizon
    method_used: ForecastMethod
    predicted_value: float
    confidence_level: ForecastConfidence
    confidence_interval: Tuple[float, float]
    forecast_date: datetime
    assumptions: List[str]
    risk_factors: List[str]
    scenario_analysis: Dict[str, float]


@dataclass
class EconomicIndicator:
    """Economic indicator for forecasting"""
    indicator_name: str
    current_value: float
    historical_values: List[float]
    impact_weight: float
    correlation_coefficient: float
    trend_direction: str


class ForecastingAgent(FinancialAgent):
    """
    Specialized agent for financial forecasting and predictive analytics
    وكيل متخصص في التنبؤات المالية والتحليل التنبؤي
    """

    def __init__(self, agent_id: str = "forecasting_agent",
                 agent_name_ar: str = "وكيل التنبؤات المالية",
                 agent_name_en: str = "Forecasting Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'FORECASTING', 'forecasting')
        )

        # Forecasting models and parameters
        self.forecast_models = self._initialize_forecast_models()
        self.economic_indicators = self._initialize_economic_indicators()
        self.forecast_parameters = self._initialize_forecast_parameters()
        self.scenario_templates = self._initialize_scenario_templates()

    def _initialize_capabilities(self) -> None:
        """Initialize forecasting capabilities"""
        self.capabilities = {
            "forecasting_methods": {
                "time_series_analysis": True,
                "regression_modeling": True,
                "machine_learning": True,
                "econometric_modeling": True,
                "scenario_planning": True,
                "monte_carlo_simulation": True
            },
            "forecast_horizons": {
                "short_term": "1-3 months",
                "medium_term": "3-12 months",
                "long_term": "1-5 years",
                "strategic": "5+ years"
            },
            "metrics_forecasting": {
                "financial_performance": True,
                "market_indicators": True,
                "risk_metrics": True,
                "economic_variables": True,
                "business_kpis": True
            },
            "uncertainty_analysis": {
                "confidence_intervals": True,
                "sensitivity_analysis": True,
                "stress_testing": True,
                "scenario_modeling": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_forecast_models(self) -> Dict[str, Any]:
        """Initialize forecasting models and algorithms"""
        return {
            "time_series_models": {
                "arima": {
                    "description": "نموذج الانحدار الذاتي المتكامل للمتوسط المتحرك",
                    "best_for": ["revenue", "expenses", "loan_growth"],
                    "parameters": {"p": 2, "d": 1, "q": 2},
                    "min_data_points": 24
                },
                "exponential_smoothing": {
                    "description": "التنعيم الأسي للاتجاهات والموسمية",
                    "best_for": ["seasonal_data", "demand_forecasting"],
                    "parameters": {"alpha": 0.3, "beta": 0.1, "gamma": 0.1},
                    "min_data_points": 12
                },
                "prophet": {
                    "description": "نموذج فيسبوك للتنبؤ بالسلاسل الزمنية",
                    "best_for": ["long_term_trends", "irregular_patterns"],
                    "parameters": {"seasonality_mode": "multiplicative"},
                    "min_data_points": 36
                }
            },
            "regression_models": {
                "linear_regression": {
                    "description": "الانحدار الخطي متعدد المتغيرات",
                    "best_for": ["linear_relationships", "simple_predictions"],
                    "parameters": {"regularization": "ridge"},
                    "min_data_points": 20
                },
                "polynomial_regression": {
                    "description": "الانحدار متعدد الحدود",
                    "best_for": ["non_linear_trends", "curved_relationships"],
                    "parameters": {"degree": 2},
                    "min_data_points": 30
                }
            },
            "machine_learning_models": {
                "random_forest": {
                    "description": "الغابة العشوائية للتنبؤ",
                    "best_for": ["complex_patterns", "multiple_variables"],
                    "parameters": {"n_estimators": 100, "max_depth": 10},
                    "min_data_points": 50
                },
                "neural_networks": {
                    "description": "الشبكات العصبية للتنبؤ",
                    "best_for": ["complex_non_linear", "large_datasets"],
                    "parameters": {"hidden_layers": [50, 30], "epochs": 100},
                    "min_data_points": 100
                }
            }
        }

    def _initialize_economic_indicators(self) -> Dict[str, EconomicIndicator]:
        """Initialize economic indicators for forecasting"""
        return {
            "gdp_growth": EconomicIndicator(
                indicator_name="نمو الناتج المحلي الإجمالي",
                current_value=0.032,  # 3.2%
                historical_values=[0.025, 0.028, 0.031, 0.029, 0.032],
                impact_weight=0.8,
                correlation_coefficient=0.75,
                trend_direction="stable"
            ),
            "inflation_rate": EconomicIndicator(
                indicator_name="معدل التضخم",
                current_value=0.024,  # 2.4%
                historical_values=[0.022, 0.025, 0.023, 0.026, 0.024],
                impact_weight=0.6,
                correlation_coefficient=-0.45,
                trend_direction="stable"
            ),
            "interest_rates": EconomicIndicator(
                indicator_name="أسعار الفائدة",
                current_value=0.055,  # 5.5%
                historical_values=[0.050, 0.052, 0.054, 0.056, 0.055],
                impact_weight=0.9,
                correlation_coefficient=0.65,
                trend_direction="rising"
            ),
            "oil_prices": EconomicIndicator(
                indicator_name="أسعار النفط",
                current_value=85.0,   # $85/barrel
                historical_values=[78.0, 82.0, 88.0, 83.0, 85.0],
                impact_weight=0.7,
                correlation_coefficient=0.55,
                trend_direction="volatile"
            ),
            "usd_sar_exchange": EconomicIndicator(
                indicator_name="سعر صرف الدولار/الريال",
                current_value=3.75,
                historical_values=[3.75, 3.75, 3.75, 3.75, 3.75],
                impact_weight=0.3,
                correlation_coefficient=0.1,
                trend_direction="stable"
            )
        }

    def _initialize_forecast_parameters(self) -> Dict[str, Any]:
        """Initialize forecasting parameters and settings"""
        return {
            "confidence_levels": {
                "default": 0.95,
                "conservative": 0.99,
                "aggressive": 0.90
            },
            "validation_methods": {
                "holdout": {"test_size": 0.2},
                "cross_validation": {"cv_folds": 5},
                "walk_forward": {"window_size": 12}
            },
            "error_metrics": {
                "mae": "Mean Absolute Error",
                "mse": "Mean Squared Error",
                "mape": "Mean Absolute Percentage Error",
                "rmse": "Root Mean Squared Error"
            },
            "outlier_detection": {
                "method": "isolation_forest",
                "threshold": 0.1
            }
        }

    def _initialize_scenario_templates(self) -> Dict[str, Any]:
        """Initialize scenario analysis templates"""
        return {
            "economic_scenarios": {
                "base_case": {
                    "description": "السيناريو الأساسي - استمرار الظروف الحالية",
                    "gdp_growth": 0.032,
                    "inflation": 0.024,
                    "oil_prices": 85.0,
                    "probability": 0.5
                },
                "optimistic": {
                    "description": "السيناريو المتفائل - نمو اقتصادي قوي",
                    "gdp_growth": 0.045,
                    "inflation": 0.020,
                    "oil_prices": 95.0,
                    "probability": 0.25
                },
                "pessimistic": {
                    "description": "السيناريو المتشائم - تباطؤ اقتصادي",
                    "gdp_growth": 0.015,
                    "inflation": 0.035,
                    "oil_prices": 70.0,
                    "probability": 0.25
                }
            },
            "market_scenarios": {
                "bull_market": {
                    "description": "سوق صاعد - نمو قوي في الأسواق",
                    "market_return": 0.15,
                    "volatility": 0.18,
                    "probability": 0.3
                },
                "bear_market": {
                    "description": "سوق هابط - انخفاض في الأسواق",
                    "market_return": -0.10,
                    "volatility": 0.25,
                    "probability": 0.2
                },
                "sideways_market": {
                    "description": "سوق متوازن - حركة جانبية",
                    "market_return": 0.05,
                    "volatility": 0.15,
                    "probability": 0.5
                }
            }
        }

    async def generate_forecast(self, historical_data: List[Dict[str, Any]],
                              target_metric: str,
                              forecast_horizon: ForecastHorizon,
                              method: ForecastMethod = ForecastMethod.TIME_SERIES) -> ForecastResult:
        """
        Generate comprehensive financial forecast
        إنشاء تنبؤ مالي شامل
        """
        try:
            # Prepare and validate data
            validated_data = await self._prepare_forecast_data(historical_data, target_metric)
            if not validated_data:
                raise ValueError("Insufficient or invalid historical data")

            # Select appropriate model
            model_config = await self._select_forecast_model(method, len(validated_data))

            # Generate base forecast
            base_forecast = await self._calculate_base_forecast(
                validated_data, target_metric, forecast_horizon, model_config
            )

            # Calculate confidence intervals
            confidence_interval = await self._calculate_confidence_interval(
                validated_data, base_forecast, model_config
            )

            # Determine confidence level
            confidence_level = await self._assess_forecast_confidence(
                validated_data, model_config, forecast_horizon
            )

            # Generate scenario analysis
            scenario_analysis = await self._generate_scenario_analysis(
                base_forecast, target_metric, forecast_horizon
            )

            # Identify assumptions and risk factors
            assumptions = await self._identify_forecast_assumptions(target_metric, forecast_horizon)
            risk_factors = await self._identify_risk_factors(target_metric, forecast_horizon)

            forecast_result = ForecastResult(
                metric_name=target_metric,
                forecast_horizon=forecast_horizon,
                method_used=method,
                predicted_value=base_forecast,
                confidence_level=confidence_level,
                confidence_interval=confidence_interval,
                forecast_date=datetime.now(),
                assumptions=assumptions,
                risk_factors=risk_factors,
                scenario_analysis=scenario_analysis
            )

            return forecast_result

        except Exception as e:
            raise Exception(f"Forecast generation failed: {str(e)}")

    async def _prepare_forecast_data(self, historical_data: List[Dict[str, Any]],
                                   target_metric: str) -> List[float]:
        """Prepare and validate historical data for forecasting"""
        try:
            values = []
            for data_point in historical_data:
                if target_metric in data_point and data_point[target_metric] is not None:
                    values.append(float(data_point[target_metric]))

            # Remove outliers
            if len(values) > 3:
                q75, q25 = np.percentile(values, [75, 25])
                iqr = q75 - q25
                lower_bound = q25 - (1.5 * iqr)
                upper_bound = q75 + (1.5 * iqr)
                values = [v for v in values if lower_bound <= v <= upper_bound]

            return values

        except Exception as e:
            return []

    async def _select_forecast_model(self, method: ForecastMethod, data_length: int) -> Dict[str, Any]:
        """Select appropriate forecasting model based on method and data"""
        models = self.forecast_models

        if method == ForecastMethod.TIME_SERIES:
            if data_length >= 36:
                return models["time_series_models"]["prophet"]
            elif data_length >= 24:
                return models["time_series_models"]["arima"]
            else:
                return models["time_series_models"]["exponential_smoothing"]

        elif method == ForecastMethod.REGRESSION:
            if data_length >= 30:
                return models["regression_models"]["polynomial_regression"]
            else:
                return models["regression_models"]["linear_regression"]

        elif method == ForecastMethod.MACHINE_LEARNING:
            if data_length >= 100:
                return models["machine_learning_models"]["neural_networks"]
            elif data_length >= 50:
                return models["machine_learning_models"]["random_forest"]
            else:
                return models["regression_models"]["linear_regression"]

        else:
            # Default to exponential smoothing
            return models["time_series_models"]["exponential_smoothing"]

    async def _calculate_base_forecast(self, historical_values: List[float],
                                     target_metric: str,
                                     horizon: ForecastHorizon,
                                     model_config: Dict[str, Any]) -> float:
        """Calculate base forecast using selected model"""

        if not historical_values:
            return 0.0

        # Simple trend-based forecasting (in real implementation, use actual models)
        recent_trend = await self._calculate_trend(historical_values[-12:] if len(historical_values) >= 12 else historical_values)

        # Apply trend based on forecast horizon
        horizon_multiplier = {
            ForecastHorizon.SHORT_TERM: 3,   # 3 months
            ForecastHorizon.MEDIUM_TERM: 9,  # 9 months
            ForecastHorizon.LONG_TERM: 24,   # 24 months
            ForecastHorizon.STRATEGIC: 60    # 60 months
        }

        periods = horizon_multiplier.get(horizon, 12)

        # Base value (most recent)
        base_value = historical_values[-1]

        # Apply trend projection
        forecast_value = base_value * (1 + recent_trend * periods / 12)

        # Apply economic adjustments
        economic_adjustment = await self._apply_economic_indicators(target_metric, forecast_value)

        return forecast_value * economic_adjustment

    async def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend from historical values"""
        if len(values) < 2:
            return 0.0

        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))

        # Calculate slope using least squares
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Convert to monthly growth rate
        return slope / y_mean if y_mean != 0 else 0.0

    async def _apply_economic_indicators(self, target_metric: str, base_forecast: float) -> float:
        """Apply economic indicators to adjust forecast"""
        adjustment_factor = 1.0

        # Get relevant economic indicators
        gdp_indicator = self.economic_indicators.get("gdp_growth")
        inflation_indicator = self.economic_indicators.get("inflation_rate")
        oil_indicator = self.economic_indicators.get("oil_prices")

        # Apply adjustments based on metric type
        if "revenue" in target_metric.lower() or "income" in target_metric.lower():
            if gdp_indicator:
                adjustment_factor *= (1 + gdp_indicator.current_value * gdp_indicator.impact_weight)
            if oil_indicator and oil_indicator.current_value > 80:
                adjustment_factor *= 1.02  # Positive oil price impact

        elif "cost" in target_metric.lower() or "expense" in target_metric.lower():
            if inflation_indicator:
                adjustment_factor *= (1 + inflation_indicator.current_value * inflation_indicator.impact_weight)

        return min(max(adjustment_factor, 0.8), 1.3)  # Cap adjustments between 80% and 130%

    async def _calculate_confidence_interval(self, historical_values: List[float],
                                           forecast_value: float,
                                           model_config: Dict[str, Any]) -> Tuple[float, float]:
        """Calculate confidence interval for forecast"""
        if len(historical_values) < 3:
            # Wide interval for insufficient data
            return (forecast_value * 0.7, forecast_value * 1.3)

        # Calculate historical volatility
        recent_values = historical_values[-12:] if len(historical_values) >= 12 else historical_values
        volatility = statistics.stdev(recent_values) / statistics.mean(recent_values) if recent_values else 0.1

        # Confidence level (95% default)
        confidence_level = 0.95
        z_score = 1.96  # For 95% confidence

        # Calculate margin of error
        margin_of_error = z_score * volatility * forecast_value

        lower_bound = max(0, forecast_value - margin_of_error)
        upper_bound = forecast_value + margin_of_error

        return (lower_bound, upper_bound)

    async def _assess_forecast_confidence(self, historical_values: List[float],
                                        model_config: Dict[str, Any],
                                        horizon: ForecastHorizon) -> ForecastConfidence:
        """Assess overall confidence in forecast"""
        confidence_score = 1.0

        # Data quality factor
        if len(historical_values) < 12:
            confidence_score *= 0.6
        elif len(historical_values) < 24:
            confidence_score *= 0.8

        # Volatility factor
        if len(historical_values) >= 3:
            volatility = statistics.stdev(historical_values) / statistics.mean(historical_values)
            if volatility > 0.3:
                confidence_score *= 0.7
            elif volatility > 0.15:
                confidence_score *= 0.85

        # Horizon factor
        horizon_factors = {
            ForecastHorizon.SHORT_TERM: 1.0,
            ForecastHorizon.MEDIUM_TERM: 0.85,
            ForecastHorizon.LONG_TERM: 0.65,
            ForecastHorizon.STRATEGIC: 0.45
        }
        confidence_score *= horizon_factors.get(horizon, 0.8)

        # Convert to confidence level
        if confidence_score >= 0.85:
            return ForecastConfidence.VERY_HIGH
        elif confidence_score >= 0.75:
            return ForecastConfidence.HIGH
        elif confidence_score >= 0.6:
            return ForecastConfidence.MEDIUM
        elif confidence_score >= 0.4:
            return ForecastConfidence.LOW
        else:
            return ForecastConfidence.VERY_LOW

    async def _generate_scenario_analysis(self, base_forecast: float,
                                        target_metric: str,
                                        horizon: ForecastHorizon) -> Dict[str, float]:
        """Generate scenario analysis for forecast"""
        scenarios = {}

        economic_scenarios = self.scenario_templates["economic_scenarios"]

        for scenario_name, scenario_data in economic_scenarios.items():
            # Adjust forecast based on scenario
            gdp_impact = scenario_data["gdp_growth"] / 0.032  # Relative to base case
            oil_impact = scenario_data["oil_prices"] / 85.0   # Relative to base case

            # Calculate scenario-adjusted forecast
            scenario_adjustment = (gdp_impact * 0.6 + oil_impact * 0.4)
            scenarios[scenario_name] = base_forecast * scenario_adjustment

        return scenarios

    async def _identify_forecast_assumptions(self, target_metric: str,
                                           horizon: ForecastHorizon) -> List[str]:
        """Identify key assumptions underlying the forecast"""
        assumptions = [
            "استمرار الاتجاهات التاريخية الحالية",
            "عدم حدوث أحداث اقتصادية استثنائية",
            "الحفاظ على السياسات النقدية والمالية الحالية"
        ]

        # Add metric-specific assumptions
        if "revenue" in target_metric.lower():
            assumptions.extend([
                "استقرار الحصة السوقية",
                "عدم ظهور منافسة جديدة قوية",
                "استمرار النمو في الطلب"
            ])

        elif "risk" in target_metric.lower():
            assumptions.extend([
                "استقرار البيئة التنظيمية",
                "عدم تغير كبير في ملف المخاطر",
                "فعالية أنظمة إدارة المخاطر الحالية"
            ])

        # Add horizon-specific assumptions
        if horizon in [ForecastHorizon.LONG_TERM, ForecastHorizon.STRATEGIC]:
            assumptions.extend([
                "استقرار الإطار التنظيمي طويل الأجل",
                "عدم حدوث تغييرات جذرية في نموذج العمل",
                "استمرار النمو الاقتصادي المعتدل"
            ])

        return assumptions

    async def _identify_risk_factors(self, target_metric: str,
                                   horizon: ForecastHorizon) -> List[str]:
        """Identify key risk factors that could affect the forecast"""
        risk_factors = [
            "تقلبات أسعار النفط",
            "التغيرات في السياسة النقدية",
            "عدم الاستقرار الجيوسياسي الإقليمي"
        ]

        # Add metric-specific risks
        if "credit" in target_metric.lower() or "loan" in target_metric.lower():
            risk_factors.extend([
                "تدهور جودة الائتمان",
                "زيادة معدلات التعثر",
                "تشديد المعايير التنظيمية"
            ])

        elif "market" in target_metric.lower():
            risk_factors.extend([
                "تقلبات أسواق رأس المال",
                "تغيرات أسعار الفائدة",
                "انخفاض السيولة السوقية"
            ])

        # Add horizon-specific risks
        if horizon in [ForecastHorizon.LONG_TERM, ForecastHorizon.STRATEGIC]:
            risk_factors.extend([
                "التطورات التكنولوجية المعطلة",
                "تغيرات ديموغرافية كبيرة",
                "مخاطر تغير المناخ"
            ])

        return risk_factors

    async def monte_carlo_simulation(self, base_forecast: float,
                                   volatility: float,
                                   num_simulations: int = 10000) -> Dict[str, Any]:
        """
        Perform Monte Carlo simulation for forecast uncertainty
        إجراء محاكاة مونت كارلو لعدم اليقين في التنبؤات
        """
        try:
            simulations = []

            for _ in range(num_simulations):
                # Generate random shock using normal distribution
                random_shock = np.random.normal(0, volatility)
                simulated_value = base_forecast * (1 + random_shock)
                simulations.append(max(0, simulated_value))  # Ensure non-negative

            # Calculate statistics
            simulation_results = {
                "mean": statistics.mean(simulations),
                "median": statistics.median(simulations),
                "std_dev": statistics.stdev(simulations),
                "min_value": min(simulations),
                "max_value": max(simulations),
                "percentiles": {
                    "5th": np.percentile(simulations, 5),
                    "25th": np.percentile(simulations, 25),
                    "75th": np.percentile(simulations, 75),
                    "95th": np.percentile(simulations, 95)
                },
                "probability_analysis": {
                    "prob_above_base": sum(1 for s in simulations if s > base_forecast) / num_simulations,
                    "prob_below_80pct": sum(1 for s in simulations if s < base_forecast * 0.8) / num_simulations,
                    "prob_above_120pct": sum(1 for s in simulations if s > base_forecast * 1.2) / num_simulations
                }
            }

            return simulation_results

        except Exception as e:
            return {"error": f"Monte Carlo simulation failed: {str(e)}"}

    async def stress_test_forecast(self, base_forecast: float,
                                 stress_scenarios: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Perform stress testing on forecasts
        إجراء اختبارات الضغط على التنبؤات
        """
        try:
            stress_results = {
                "base_forecast": base_forecast,
                "stress_scenarios": {},
                "worst_case": None,
                "best_case": None,
                "stress_summary": {}
            }

            scenario_values = []

            for scenario_name, scenario_params in stress_scenarios.items():
                # Apply stress factors
                stressed_forecast = base_forecast

                for factor, impact in scenario_params.items():
                    if factor == "gdp_shock":
                        stressed_forecast *= (1 + impact)
                    elif factor == "interest_rate_shock":
                        stressed_forecast *= (1 + impact * 0.5)  # Moderate impact
                    elif factor == "market_shock":
                        stressed_forecast *= (1 + impact * 0.7)  # High impact
                    elif factor == "credit_shock":
                        stressed_forecast *= (1 + impact * 0.8)  # Very high impact

                stress_results["stress_scenarios"][scenario_name] = {
                    "stressed_value": stressed_forecast,
                    "change_from_base": ((stressed_forecast - base_forecast) / base_forecast) * 100,
                    "scenario_params": scenario_params
                }

                scenario_values.append(stressed_forecast)

            # Summary statistics
            if scenario_values:
                stress_results["worst_case"] = min(scenario_values)
                stress_results["best_case"] = max(scenario_values)
                stress_results["stress_summary"] = {
                    "max_downside": ((min(scenario_values) - base_forecast) / base_forecast) * 100,
                    "max_upside": ((max(scenario_values) - base_forecast) / base_forecast) * 100,
                    "average_scenario": statistics.mean(scenario_values),
                    "scenario_volatility": statistics.stdev(scenario_values) if len(scenario_values) > 1 else 0
                }

            return stress_results

        except Exception as e:
            return {"error": f"Stress testing failed: {str(e)}"}

    async def forecast_validation(self, historical_forecasts: List[Dict[str, Any]],
                                actual_values: List[float]) -> Dict[str, Any]:
        """
        Validate forecast accuracy using historical data
        التحقق من دقة التنبؤات باستخدام البيانات التاريخية
        """
        try:
            if len(historical_forecasts) != len(actual_values):
                return {"error": "Mismatch between forecasts and actual values"}

            validation_results = {
                "accuracy_metrics": {},
                "bias_analysis": {},
                "performance_summary": {},
                "recommendations": []
            }

            forecasted_values = [f.get("predicted_value", 0) for f in historical_forecasts]

            # Calculate accuracy metrics
            errors = [actual - forecast for actual, forecast in zip(actual_values, forecasted_values)]
            absolute_errors = [abs(e) for e in errors]
            percentage_errors = [abs(e) / actual * 100 for e, actual in zip(errors, actual_values) if actual != 0]

            validation_results["accuracy_metrics"] = {
                "mae": statistics.mean(absolute_errors),  # Mean Absolute Error
                "mse": statistics.mean([e**2 for e in errors]),  # Mean Squared Error
                "rmse": math.sqrt(statistics.mean([e**2 for e in errors])),  # Root Mean Squared Error
                "mape": statistics.mean(percentage_errors) if percentage_errors else float('inf'),  # Mean Absolute Percentage Error
                "bias": statistics.mean(errors)  # Forecast bias
            }

            # Bias analysis
            positive_errors = sum(1 for e in errors if e > 0)
            validation_results["bias_analysis"] = {
                "systematic_bias": "overestimation" if statistics.mean(errors) > 0 else "underestimation",
                "bias_magnitude": abs(statistics.mean(errors)),
                "forecast_accuracy_rate": sum(1 for e in percentage_errors if e <= 10) / len(percentage_errors) * 100 if percentage_errors else 0,
                "directional_accuracy": sum(1 for i in range(1, len(actual_values))
                                          if (actual_values[i] > actual_values[i-1]) == (forecasted_values[i] > forecasted_values[i-1])) / (len(actual_values) - 1) * 100 if len(actual_values) > 1 else 0
            }

            # Performance summary
            mape = validation_results["accuracy_metrics"]["mape"]
            if mape <= 5:
                performance_level = "ممتاز"
            elif mape <= 10:
                performance_level = "جيد جداً"
            elif mape <= 20:
                performance_level = "مقبول"
            else:
                performance_level = "يحتاج تحسين"

            validation_results["performance_summary"] = {
                "overall_performance": performance_level,
                "accuracy_score": max(0, 100 - mape) if mape != float('inf') else 0,
                "consistency_score": max(0, 100 - (statistics.stdev(percentage_errors) if len(percentage_errors) > 1 else 100))
            }

            # Generate recommendations
            if mape > 15:
                validation_results["recommendations"].append("تحسين نموذج التنبؤ أو إضافة متغيرات جديدة")
            if abs(validation_results["accuracy_metrics"]["bias"]) > statistics.mean(absolute_errors) * 0.5:
                validation_results["recommendations"].append("معالجة التحيز المنهجي في التنبؤات")
            if validation_results["bias_analysis"]["directional_accuracy"] < 70:
                validation_results["recommendations"].append("تحسين قدرة النموذج على التنبؤ بالاتجاه")

            return validation_results

        except Exception as e:
            return {"error": f"Forecast validation failed: {str(e)}"}

    async def generate_forecast_report(self, forecast_results: List[ForecastResult],
                                     language: str = "ar") -> Dict[str, Any]:
        """
        Generate comprehensive forecast report
        إنشاء تقرير شامل للتنبؤات
        """
        try:
            if language == "ar":
                report = {
                    "عنوان_التقرير": "تقرير التنبؤات المالية",
                    "تاريخ_التقرير": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ملخص_تنفيذي": {},
                    "التنبؤات_التفصيلية": [],
                    "تحليل_المخاطر": {},
                    "التوصيات": [],
                    "الافتراضات_الرئيسية": [],
                    "تحليل_السيناريوهات": {}
                }

                # Executive summary
                high_confidence_forecasts = [f for f in forecast_results if f.confidence_level in [ForecastConfidence.HIGH, ForecastConfidence.VERY_HIGH]]
                report["ملخص_تنفيذي"] = {
                    "عدد_التنبؤات": len(forecast_results),
                    "التنبؤات_عالية_الثقة": len(high_confidence_forecasts),
                    "الآفاق_الزمنية": list(set(f.forecast_horizon.value for f in forecast_results)),
                    "النظرة_العامة": "إيجابية" if sum(f.predicted_value for f in forecast_results) > 0 else "محايدة"
                }

            else:  # English
                report = {
                    "report_title": "Financial Forecasting Report",
                    "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "executive_summary": {},
                    "detailed_forecasts": [],
                    "risk_analysis": {},
                    "recommendations": [],
                    "key_assumptions": [],
                    "scenario_analysis": {}
                }

                # Executive summary
                high_confidence_forecasts = [f for f in forecast_results if f.confidence_level in [ForecastConfidence.HIGH, ForecastConfidence.VERY_HIGH]]
                report["executive_summary"] = {
                    "total_forecasts": len(forecast_results),
                    "high_confidence_forecasts": len(high_confidence_forecasts),
                    "forecast_horizons": list(set(f.forecast_horizon.value for f in forecast_results)),
                    "overall_outlook": "positive" if sum(f.predicted_value for f in forecast_results) > 0 else "neutral"
                }

            # Add detailed forecasts
            for forecast in forecast_results:
                forecast_detail = {
                    "metric": forecast.metric_name,
                    "predicted_value": forecast.predicted_value,
                    "confidence_level": forecast.confidence_level.value,
                    "confidence_interval": forecast.confidence_interval,
                    "horizon": forecast.forecast_horizon.value,
                    "method": forecast.method_used.value,
                    "scenarios": forecast.scenario_analysis
                }

                if language == "ar":
                    report["التنبؤات_التفصيلية"].append(forecast_detail)
                else:
                    report["detailed_forecasts"].append(forecast_detail)

            # Compile assumptions and risk factors
            all_assumptions = set()
            all_risks = set()

            for forecast in forecast_results:
                all_assumptions.update(forecast.assumptions)
                all_risks.update(forecast.risk_factors)

            if language == "ar":
                report["الافتراضات_الرئيسية"] = list(all_assumptions)
                report["تحليل_المخاطر"]["عوامل_المخاطر"] = list(all_risks)
            else:
                report["key_assumptions"] = list(all_assumptions)
                report["risk_analysis"]["risk_factors"] = list(all_risks)

            return report

        except Exception as e:
            return {"error": f"Report generation failed: {str(e)}"}

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process forecasting-related tasks"""
        try:
            task_type = task.task_data.get("type", "generate_forecast")

            if task_type == "generate_forecast":
                historical_data = task.task_data.get("historical_data", [])
                target_metric = task.task_data.get("target_metric", "")
                horizon = ForecastHorizon(task.task_data.get("horizon", "medium_term"))
                method = ForecastMethod(task.task_data.get("method", "time_series"))

                result = await self.generate_forecast(historical_data, target_metric, horizon, method)
                return {
                    "forecast_result": {
                        "metric": result.metric_name,
                        "predicted_value": result.predicted_value,
                        "confidence_level": result.confidence_level.value,
                        "confidence_interval": result.confidence_interval,
                        "scenario_analysis": result.scenario_analysis,
                        "assumptions": result.assumptions,
                        "risk_factors": result.risk_factors
                    }
                }

            elif task_type == "monte_carlo_simulation":
                base_forecast = task.task_data.get("base_forecast", 0)
                volatility = task.task_data.get("volatility", 0.1)
                num_simulations = task.task_data.get("num_simulations", 10000)
                return await self.monte_carlo_simulation(base_forecast, volatility, num_simulations)

            elif task_type == "stress_test":
                base_forecast = task.task_data.get("base_forecast", 0)
                stress_scenarios = task.task_data.get("stress_scenarios", {})
                return await self.stress_test_forecast(base_forecast, stress_scenarios)

            elif task_type == "validate_forecast":
                historical_forecasts = task.task_data.get("historical_forecasts", [])
                actual_values = task.task_data.get("actual_values", [])
                return await self.forecast_validation(historical_forecasts, actual_values)

            elif task_type == "generate_report":
                forecast_results = task.task_data.get("forecast_results", [])
                language = task.task_data.get("language", "ar")
                # Convert dictionaries to ForecastResult objects
                forecast_objects = []
                for fr in forecast_results:
                    forecast_obj = ForecastResult(
                        metric_name=fr.get("metric_name", ""),
                        forecast_horizon=ForecastHorizon(fr.get("forecast_horizon", "medium_term")),
                        method_used=ForecastMethod(fr.get("method_used", "time_series")),
                        predicted_value=fr.get("predicted_value", 0),
                        confidence_level=ForecastConfidence(fr.get("confidence_level", "medium")),
                        confidence_interval=tuple(fr.get("confidence_interval", [0, 0])),
                        forecast_date=datetime.now(),
                        assumptions=fr.get("assumptions", []),
                        risk_factors=fr.get("risk_factors", []),
                        scenario_analysis=fr.get("scenario_analysis", {})
                    )
                    forecast_objects.append(forecast_obj)
                return await self.generate_forecast_report(forecast_objects, language)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}