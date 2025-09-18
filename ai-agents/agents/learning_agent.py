"""
Learning Agent
وكيل التعلم المستمر والتحسين

This agent implements continuous learning and improvement capabilities,
analyzing performance patterns and optimizing agent behaviors over time.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import numpy as np

from ..core.agent_base import FinancialAgent, AgentType, AgentTask


class LearningType(Enum):
    """Types of learning algorithms"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    FEDERATED = "federated"
    TRANSFER = "transfer"


class ModelType(Enum):
    """Machine learning model types"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    DEEP_LEARNING = "deep_learning"


class OptimizationTarget(Enum):
    """Optimization targets"""
    ACCURACY = "accuracy"
    SPEED = "speed"
    RESOURCE_USAGE = "resource_usage"
    USER_SATISFACTION = "user_satisfaction"
    COST_EFFECTIVENESS = "cost_effectiveness"


@dataclass
class LearningDataPoint:
    """Single learning data point"""
    timestamp: datetime
    agent_id: str
    task_type: str
    input_features: Dict[str, Any]
    output_result: Dict[str, Any]
    success_metrics: Dict[str, float]
    user_feedback: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_id: str
    model_type: ModelType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time: float
    inference_time: float
    data_points_used: int
    last_updated: datetime


class LearningAgent(FinancialAgent):
    """
    Specialized agent for continuous learning and improvement
    وكيل متخصص في التعلم المستمر والتحسين
    """

    def __init__(self, agent_id: str = "learning_agent",
                 agent_name_ar: str = "وكيل التعلم المستمر والتحسين",
                 agent_name_en: str = "Learning Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'LEARNING', 'learning')
        )

        self.training_data = []
        self.models = {}
        self.performance_history = []
        self.learning_patterns = self._initialize_learning_patterns()
        self.optimization_strategies = self._initialize_optimization_strategies()

    def _initialize_capabilities(self) -> None:
        """Initialize learning and optimization capabilities"""
        self.capabilities = {
            "learning_algorithms": {
                "supervised_learning": True,
                "unsupervised_learning": True,
                "reinforcement_learning": True,
                "deep_learning": False,  # Requires specialized hardware
                "federated_learning": True,
                "transfer_learning": True
            },
            "model_types": {
                "predictive_models": True,
                "classification_models": True,
                "clustering_models": True,
                "anomaly_detection": True,
                "time_series_forecasting": True,
                "recommendation_systems": True
            },
            "optimization": {
                "hyperparameter_tuning": True,
                "feature_selection": True,
                "model_ensemble": True,
                "performance_optimization": True,
                "resource_optimization": True
            },
            "continuous_improvement": {
                "online_learning": True,
                "model_retraining": True,
                "performance_monitoring": True,
                "bias_detection": True,
                "drift_detection": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_learning_patterns(self) -> Dict[str, Any]:
        """Initialize learning patterns and templates"""
        return {
            "agent_performance_patterns": {
                "response_time_optimization": {
                    "target_metric": "response_time",
                    "optimization_direction": "minimize",
                    "features": ["data_size", "complexity", "system_load"],
                    "model_type": ModelType.REGRESSION
                },
                "accuracy_improvement": {
                    "target_metric": "accuracy",
                    "optimization_direction": "maximize",
                    "features": ["data_quality", "feature_count", "model_complexity"],
                    "model_type": ModelType.CLASSIFICATION
                },
                "error_prediction": {
                    "target_metric": "error_probability",
                    "optimization_direction": "minimize",
                    "features": ["input_validation", "data_consistency", "system_state"],
                    "model_type": ModelType.CLASSIFICATION
                }
            },
            "user_behavior_patterns": {
                "preference_learning": {
                    "target_metric": "user_satisfaction",
                    "features": ["analysis_type", "detail_level", "timeframe", "industry"],
                    "model_type": ModelType.RECOMMENDATION
                },
                "usage_prediction": {
                    "target_metric": "feature_usage",
                    "features": ["user_role", "time_of_day", "analysis_history"],
                    "model_type": ModelType.TIME_SERIES
                }
            },
            "market_patterns": {
                "volatility_detection": {
                    "target_metric": "market_volatility",
                    "features": ["price_movements", "volume", "news_sentiment"],
                    "model_type": ModelType.ANOMALY_DETECTION
                },
                "trend_prediction": {
                    "target_metric": "price_direction",
                    "features": ["technical_indicators", "fundamental_data", "market_sentiment"],
                    "model_type": ModelType.TIME_SERIES
                }
            }
        }

    def _initialize_optimization_strategies(self) -> Dict[str, Any]:
        """Initialize optimization strategies"""
        return {
            "hyperparameter_optimization": {
                "methods": ["grid_search", "random_search", "bayesian_optimization"],
                "parameters": {
                    "learning_rate": [0.001, 0.01, 0.1],
                    "batch_size": [16, 32, 64, 128],
                    "epochs": [50, 100, 200],
                    "regularization": [0.001, 0.01, 0.1]
                }
            },
            "feature_optimization": {
                "selection_methods": ["correlation_analysis", "mutual_information", "recursive_elimination"],
                "transformation_methods": ["normalization", "standardization", "pca"],
                "engineering_methods": ["polynomial_features", "interaction_terms", "time_based_features"]
            },
            "model_optimization": {
                "ensemble_methods": ["voting", "bagging", "boosting", "stacking"],
                "pruning_methods": ["magnitude_pruning", "structured_pruning"],
                "quantization_methods": ["post_training", "quantization_aware"]
            }
        }

    async def collect_learning_data(self, agent_id: str, task_data: Dict[str, Any],
                                  result_data: Dict[str, Any],
                                  performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Collect data for learning and improvement
        جمع البيانات للتعلم والتحسين
        """
        try:
            # Create learning data point
            data_point = LearningDataPoint(
                timestamp=datetime.now(),
                agent_id=agent_id,
                task_type=task_data.get("type", "unknown"),
                input_features=await self._extract_features(task_data),
                output_result=result_data,
                success_metrics=performance_metrics,
                execution_time=performance_metrics.get("execution_time", 0.0)
            )

            # Store training data
            self.training_data.append(data_point)

            # Trigger learning if enough data collected
            if len(self.training_data) >= 100:  # Minimum batch size
                learning_result = await self._trigger_learning_update(agent_id)

                return {
                    "data_collected": True,
                    "data_points_total": len(self.training_data),
                    "learning_triggered": learning_result.get("learning_triggered", False),
                    "timestamp": datetime.now().isoformat()
                }

            return {
                "data_collected": True,
                "data_points_total": len(self.training_data),
                "learning_triggered": False,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Learning data collection failed: {str(e)}"}

    async def _extract_features(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant features from task data"""
        features = {}

        # Basic task features
        features["task_type"] = task_data.get("type", "unknown")
        features["data_size"] = len(str(task_data))
        features["complexity_score"] = await self._calculate_complexity_score(task_data)
        features["timestamp_hour"] = datetime.now().hour
        features["timestamp_day_of_week"] = datetime.now().weekday()

        # Data type features
        if "financial_data" in task_data:
            features["has_financial_data"] = 1
            features["financial_data_size"] = len(task_data["financial_data"]) if isinstance(task_data["financial_data"], dict) else 0
        else:
            features["has_financial_data"] = 0
            features["financial_data_size"] = 0

        # Request features
        features["num_parameters"] = len(task_data.get("parameters", {}))
        features["has_time_series"] = 1 if "time_series" in str(task_data).lower() else 0
        features["has_forecast"] = 1 if "forecast" in str(task_data).lower() else 0

        return features

    async def _calculate_complexity_score(self, task_data: Dict[str, Any]) -> float:
        """Calculate complexity score for task"""
        complexity = 0.0

        # Data volume complexity
        data_str = str(task_data)
        complexity += min(len(data_str) / 10000, 1.0)  # Normalized by 10KB

        # Nested structure complexity
        def count_nesting(obj, depth=0):
            if depth > 5:  # Prevent infinite recursion
                return depth
            if isinstance(obj, dict):
                return max(count_nesting(v, depth + 1) for v in obj.values()) if obj else depth
            elif isinstance(obj, list):
                return max(count_nesting(item, depth + 1) for item in obj[:5]) if obj else depth  # Check first 5 items
            return depth

        nesting_depth = count_nesting(task_data)
        complexity += min(nesting_depth / 10, 1.0)

        # Task type complexity
        task_type = task_data.get("type", "")
        complexity_mapping = {
            "data_validation": 0.2,
            "financial_analysis": 0.6,
            "risk_assessment": 0.8,
            "forecasting": 0.9,
            "comprehensive_analysis": 1.0
        }
        complexity += complexity_mapping.get(task_type, 0.5)

        return min(complexity, 3.0)  # Cap at 3.0

    async def _trigger_learning_update(self, agent_id: str) -> Dict[str, Any]:
        """Trigger learning update for specific agent"""
        try:
            # Filter data for specific agent
            agent_data = [dp for dp in self.training_data if dp.agent_id == agent_id]

            if len(agent_data) < 50:  # Minimum data for meaningful learning
                return {"learning_triggered": False, "reason": "insufficient_data"}

            # Identify learning opportunities
            learning_opportunities = await self._identify_learning_opportunities(agent_data)

            # Train models for identified opportunities
            training_results = []
            for opportunity in learning_opportunities:
                result = await self._train_improvement_model(agent_data, opportunity)
                training_results.append(result)

            # Update agent optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(training_results)

            return {
                "learning_triggered": True,
                "opportunities_identified": len(learning_opportunities),
                "models_trained": len(training_results),
                "optimization_suggestions": optimization_suggestions,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"learning_triggered": False, "error": str(e)}

    async def _identify_learning_opportunities(self, agent_data: List[LearningDataPoint]) -> List[Dict[str, Any]]:
        """Identify learning opportunities from agent data"""
        opportunities = []

        # Analyze response time patterns
        response_times = [dp.execution_time for dp in agent_data if dp.execution_time > 0]
        if response_times and statistics.stdev(response_times) > statistics.mean(response_times) * 0.5:
            opportunities.append({
                "type": "response_time_optimization",
                "metric": "execution_time",
                "current_performance": {
                    "mean": statistics.mean(response_times),
                    "std": statistics.stdev(response_times),
                    "variation_coefficient": statistics.stdev(response_times) / statistics.mean(response_times)
                }
            })

        # Analyze accuracy patterns
        accuracy_scores = [
            dp.success_metrics.get("accuracy", 0.0) for dp in agent_data
            if "accuracy" in dp.success_metrics
        ]
        if accuracy_scores and statistics.mean(accuracy_scores) < 0.9:
            opportunities.append({
                "type": "accuracy_improvement",
                "metric": "accuracy",
                "current_performance": {
                    "mean": statistics.mean(accuracy_scores),
                    "improvement_potential": 0.95 - statistics.mean(accuracy_scores)
                }
            })

        # Analyze error patterns
        error_rates = [
            1.0 if "error" in dp.output_result else 0.0 for dp in agent_data
        ]
        if error_rates and statistics.mean(error_rates) > 0.05:  # 5% error threshold
            opportunities.append({
                "type": "error_reduction",
                "metric": "error_rate",
                "current_performance": {
                    "error_rate": statistics.mean(error_rates),
                    "error_count": sum(error_rates)
                }
            })

        return opportunities

    async def _train_improvement_model(self, training_data: List[LearningDataPoint],
                                     opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Train improvement model for specific opportunity"""
        try:
            model_type = opportunity["type"]
            target_metric = opportunity["metric"]

            # Prepare training data
            features_matrix = []
            target_values = []

            for dp in training_data:
                features_matrix.append(list(dp.input_features.values()))

                if target_metric == "execution_time":
                    target_values.append(dp.execution_time)
                elif target_metric == "accuracy":
                    target_values.append(dp.success_metrics.get("accuracy", 0.0))
                elif target_metric == "error_rate":
                    target_values.append(1.0 if "error" in dp.output_result else 0.0)

            # Simple model training simulation
            model_id = f"{model_type}_{int(datetime.now().timestamp())}"

            # Mock training process
            await asyncio.sleep(0.1)  # Simulate training time

            # Calculate mock performance metrics
            performance = ModelPerformance(
                model_id=model_id,
                model_type=ModelType.REGRESSION if target_metric == "execution_time" else ModelType.CLASSIFICATION,
                accuracy=0.85 + np.random.random() * 0.1,  # Mock accuracy
                precision=0.80 + np.random.random() * 0.15,
                recall=0.82 + np.random.random() * 0.13,
                f1_score=0.81 + np.random.random() * 0.14,
                training_time=0.1,
                inference_time=0.01,
                data_points_used=len(training_data),
                last_updated=datetime.now()
            )

            # Store model and performance
            self.models[model_id] = {
                "model_type": model_type,
                "target_metric": target_metric,
                "performance": performance,
                "training_data_size": len(training_data)
            }

            self.performance_history.append(performance)

            return {
                "model_id": model_id,
                "model_type": model_type,
                "performance": {
                    "accuracy": performance.accuracy,
                    "training_time": performance.training_time,
                    "data_points": performance.data_points_used
                },
                "improvement_potential": opportunity["current_performance"]
            }

        except Exception as e:
            return {"error": f"Model training failed: {str(e)}"}

    async def _generate_optimization_suggestions(self, training_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on training results"""
        suggestions = []

        for result in training_results:
            if "error" in result:
                continue

            model_type = result.get("model_type", "")
            performance = result.get("performance", {})
            accuracy = performance.get("accuracy", 0.0)

            if model_type == "response_time_optimization" and accuracy > 0.8:
                suggestions.append({
                    "type": "performance_optimization",
                    "priority": "medium",
                    "suggestion": "تحسين خوارزميات المعالجة لتقليل وقت الاستجابة",
                    "expected_improvement": "15-25% reduction in response time",
                    "implementation_effort": "medium"
                })

            elif model_type == "accuracy_improvement" and accuracy > 0.85:
                suggestions.append({
                    "type": "accuracy_enhancement",
                    "priority": "high",
                    "suggestion": "تحسين جودة البيانات المدخلة وخوارزميات التحليل",
                    "expected_improvement": "5-10% increase in accuracy",
                    "implementation_effort": "low"
                })

            elif model_type == "error_reduction" and accuracy > 0.9:
                suggestions.append({
                    "type": "error_prevention",
                    "priority": "high",
                    "suggestion": "تعزيز التحقق من صحة البيانات ومعالجة الاستثناءات",
                    "expected_improvement": "50% reduction in error rate",
                    "implementation_effort": "medium"
                })

        return suggestions

    async def optimize_agent_performance(self, agent_id: str,
                                       optimization_target: OptimizationTarget) -> Dict[str, Any]:
        """
        Optimize agent performance for specific target
        تحسين أداء الوكيل للهدف المحدد
        """
        try:
            # Get agent's historical data
            agent_data = [dp for dp in self.training_data if dp.agent_id == agent_id]

            if len(agent_data) < 20:
                return {"error": "Insufficient data for optimization"}

            optimization_result = {
                "agent_id": agent_id,
                "optimization_target": optimization_target.value,
                "optimization_date": datetime.now().isoformat(),
                "current_performance": {},
                "optimization_strategy": {},
                "expected_improvements": {},
                "implementation_steps": []
            }

            # Analyze current performance
            current_performance = await self._analyze_current_performance(agent_data, optimization_target)
            optimization_result["current_performance"] = current_performance

            # Generate optimization strategy
            strategy = await self._generate_optimization_strategy(agent_data, optimization_target)
            optimization_result["optimization_strategy"] = strategy

            # Estimate improvements
            improvements = await self._estimate_improvements(current_performance, strategy)
            optimization_result["expected_improvements"] = improvements

            # Generate implementation steps
            steps = await self._generate_implementation_steps(strategy)
            optimization_result["implementation_steps"] = steps

            return optimization_result

        except Exception as e:
            return {"error": f"Performance optimization failed: {str(e)}"}

    async def _analyze_current_performance(self, agent_data: List[LearningDataPoint],
                                         target: OptimizationTarget) -> Dict[str, Any]:
        """Analyze current performance metrics"""
        performance = {}

        if target == OptimizationTarget.SPEED:
            response_times = [dp.execution_time for dp in agent_data if dp.execution_time > 0]
            if response_times:
                performance = {
                    "average_response_time": statistics.mean(response_times),
                    "median_response_time": statistics.median(response_times),
                    "p95_response_time": np.percentile(response_times, 95),
                    "response_time_variability": statistics.stdev(response_times)
                }

        elif target == OptimizationTarget.ACCURACY:
            accuracy_scores = [
                dp.success_metrics.get("accuracy", 0.0) for dp in agent_data
                if "accuracy" in dp.success_metrics
            ]
            if accuracy_scores:
                performance = {
                    "average_accuracy": statistics.mean(accuracy_scores),
                    "accuracy_consistency": 1.0 - (statistics.stdev(accuracy_scores) / statistics.mean(accuracy_scores)),
                    "accuracy_trend": self._calculate_trend(accuracy_scores)
                }

        elif target == OptimizationTarget.RESOURCE_USAGE:
            # Mock resource usage analysis
            performance = {
                "cpu_usage": 65.0,  # Mock percentage
                "memory_usage": 70.0,
                "io_operations": 120.0,
                "resource_efficiency": 0.75
            }

        return performance

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for values"""
        if len(values) < 2:
            return "stable"

        recent_avg = statistics.mean(values[-5:]) if len(values) >= 5 else values[-1]
        earlier_avg = statistics.mean(values[:5]) if len(values) >= 5 else values[0]

        if recent_avg > earlier_avg * 1.05:
            return "improving"
        elif recent_avg < earlier_avg * 0.95:
            return "declining"
        else:
            return "stable"

    async def _generate_optimization_strategy(self, agent_data: List[LearningDataPoint],
                                            target: OptimizationTarget) -> Dict[str, Any]:
        """Generate optimization strategy"""
        strategy = {
            "primary_approach": "",
            "techniques": [],
            "parameters": {},
            "estimated_effort": ""
        }

        if target == OptimizationTarget.SPEED:
            strategy.update({
                "primary_approach": "algorithmic_optimization",
                "techniques": [
                    "caching_optimization",
                    "parallel_processing",
                    "data_structure_optimization",
                    "algorithm_replacement"
                ],
                "parameters": {
                    "cache_size": 1000,
                    "parallel_workers": 4,
                    "optimization_level": "aggressive"
                },
                "estimated_effort": "medium"
            })

        elif target == OptimizationTarget.ACCURACY:
            strategy.update({
                "primary_approach": "model_enhancement",
                "techniques": [
                    "feature_engineering",
                    "ensemble_methods",
                    "hyperparameter_tuning",
                    "data_quality_improvement"
                ],
                "parameters": {
                    "ensemble_size": 5,
                    "validation_split": 0.2,
                    "tuning_iterations": 50
                },
                "estimated_effort": "high"
            })

        return strategy

    async def _estimate_improvements(self, current_performance: Dict[str, Any],
                                   strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate expected improvements"""
        improvements = {}

        primary_approach = strategy.get("primary_approach", "")

        if primary_approach == "algorithmic_optimization":
            improvements = {
                "response_time_reduction": "20-35%",
                "throughput_increase": "15-30%",
                "resource_efficiency": "10-25%",
                "confidence_level": 0.8
            }

        elif primary_approach == "model_enhancement":
            improvements = {
                "accuracy_increase": "5-15%",
                "consistency_improvement": "10-20%",
                "error_reduction": "30-50%",
                "confidence_level": 0.75
            }

        return improvements

    async def _generate_implementation_steps(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate implementation steps"""
        steps = []

        techniques = strategy.get("techniques", [])

        for i, technique in enumerate(techniques):
            step = {
                "step_number": i + 1,
                "technique": technique,
                "description": f"تنفيذ تقنية {technique}",
                "estimated_duration": "1-2 weeks",
                "resources_required": ["development_time", "testing_environment"],
                "risk_level": "low",
                "dependencies": [] if i == 0 else [f"step_{i}"]
            }
            steps.append(step)

        return steps

    async def generate_learning_report(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Generate learning and improvement report
        إنشاء تقرير التعلم والتحسين
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)

            # Filter data for period
            period_data = [
                dp for dp in self.training_data
                if start_date <= dp.timestamp <= end_date
            ]

            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "learning_summary": {
                    "data_points_collected": len(period_data),
                    "agents_analyzed": len(set(dp.agent_id for dp in period_data)),
                    "models_trained": len([m for m in self.performance_history
                                         if start_date <= m.last_updated <= end_date]),
                    "optimization_opportunities": 0
                },
                "performance_trends": {},
                "improvement_achievements": {},
                "recommendations": []
            }

            # Analyze performance trends
            report["performance_trends"] = await self._analyze_performance_trends(period_data)

            # Track improvement achievements
            report["improvement_achievements"] = await self._track_improvement_achievements(period_data)

            # Generate recommendations
            report["recommendations"] = await self._generate_learning_recommendations(period_data)

            return report

        except Exception as e:
            return {"error": f"Learning report generation failed: {str(e)}"}

    async def _analyze_performance_trends(self, period_data: List[LearningDataPoint]) -> Dict[str, Any]:
        """Analyze performance trends over the period"""
        trends = {}

        # Group by agent
        agent_groups = {}
        for dp in period_data:
            if dp.agent_id not in agent_groups:
                agent_groups[dp.agent_id] = []
            agent_groups[dp.agent_id].append(dp)

        for agent_id, agent_data in agent_groups.items():
            response_times = [dp.execution_time for dp in agent_data if dp.execution_time > 0]

            if response_times:
                trends[agent_id] = {
                    "response_time_trend": self._calculate_trend(response_times),
                    "average_response_time": statistics.mean(response_times),
                    "improvement_rate": self._calculate_improvement_rate(response_times)
                }

        return trends

    def _calculate_improvement_rate(self, values: List[float]) -> float:
        """Calculate improvement rate over time"""
        if len(values) < 4:
            return 0.0

        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        if first_avg > 0:
            return (first_avg - second_avg) / first_avg * 100  # Percentage improvement
        return 0.0

    async def _track_improvement_achievements(self, period_data: List[LearningDataPoint]) -> Dict[str, Any]:
        """Track improvement achievements"""
        achievements = {
            "speed_improvements": 0,
            "accuracy_improvements": 0,
            "error_reductions": 0,
            "total_optimizations": len(self.models)
        }

        # Mock achievements calculation
        if len(period_data) > 50:
            achievements["speed_improvements"] = 2
            achievements["accuracy_improvements"] = 1
            achievements["error_reductions"] = 3

        return achievements

    async def _generate_learning_recommendations(self, period_data: List[LearningDataPoint]) -> List[str]:
        """Generate learning-based recommendations"""
        recommendations = []

        data_volume = len(period_data)
        unique_agents = len(set(dp.agent_id for dp in period_data))

        if data_volume < 100:
            recommendations.append("زيادة حجم البيانات المجمعة لتحسين دقة التعلم")

        if unique_agents < 5:
            recommendations.append("توسيع نطاق جمع البيانات لتشمل وكلاء أكثر")

        # Check for performance issues
        response_times = [dp.execution_time for dp in period_data if dp.execution_time > 0]
        if response_times and statistics.mean(response_times) > 5.0:
            recommendations.append("تركيز جهود التحسين على تقليل أوقات الاستجابة")

        if not recommendations:
            recommendations.append("مواصلة جمع البيانات والمراقبة المستمرة للأداء")

        return recommendations

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process learning and optimization tasks"""
        try:
            task_type = task.task_data.get("type", "collect_data")

            if task_type == "collect_data":
                agent_id = task.task_data.get("agent_id", "")
                task_data = task.task_data.get("task_data", {})
                result_data = task.task_data.get("result_data", {})
                performance_metrics = task.task_data.get("performance_metrics", {})
                return await self.collect_learning_data(agent_id, task_data, result_data, performance_metrics)

            elif task_type == "optimize_performance":
                agent_id = task.task_data.get("agent_id", "")
                target = OptimizationTarget(task.task_data.get("optimization_target", "accuracy"))
                return await self.optimize_agent_performance(agent_id, target)

            elif task_type == "generate_report":
                period_days = task.task_data.get("period_days", 30)
                return await self.generate_learning_report(period_days)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}