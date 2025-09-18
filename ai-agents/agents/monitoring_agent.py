"""
Monitoring Agent
وكيل المراقبة والأداء

This agent monitors system performance, health metrics, and operational
status across all components of the FinClick.AI platform.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import psutil
import time

from ..core.agent_base import FinancialAgent, AgentType, AgentTask


class MetricType(Enum):
    """Types of metrics to monitor"""
    SYSTEM_PERFORMANCE = "system_performance"
    AGENT_PERFORMANCE = "agent_performance"
    WORKFLOW_METRICS = "workflow_metrics"
    USER_ACTIVITY = "user_activity"
    ERROR_RATES = "error_rates"
    RESPONSE_TIMES = "response_times"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_name: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    alert_level: AlertLevel
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    resolved: bool = False


class MonitoringAgent(FinancialAgent):
    """
    Specialized agent for system monitoring and performance tracking
    وكيل متخصص في مراقبة النظام وتتبع الأداء
    """

    def __init__(self, agent_id: str = "monitoring_agent",
                 agent_name_ar: str = "وكيل المراقبة والأداء",
                 agent_name_en: str = "Monitoring Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'MONITORING', 'monitoring')
        )

        self.metrics_history = []
        self.active_alerts = []
        self.monitoring_config = self._initialize_monitoring_config()
        self.thresholds = self._initialize_thresholds()

    def _initialize_capabilities(self) -> None:
        """Initialize monitoring capabilities"""
        self.capabilities = {
            "system_monitoring": {
                "cpu_usage": True,
                "memory_usage": True,
                "disk_usage": True,
                "network_io": True,
                "system_load": True
            },
            "application_monitoring": {
                "agent_performance": True,
                "workflow_execution": True,
                "response_times": True,
                "error_tracking": True,
                "throughput_metrics": True
            },
            "alerting": {
                "threshold_alerts": True,
                "anomaly_detection": True,
                "escalation_management": True,
                "alert_routing": True
            },
            "reporting": {
                "performance_dashboards": True,
                "trend_analysis": True,
                "capacity_planning": True,
                "sla_monitoring": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_monitoring_config(self) -> Dict[str, Any]:
        """Initialize monitoring configuration"""
        return {
            "collection_interval": 30,  # seconds
            "retention_period": 7,  # days
            "alert_evaluation_interval": 60,  # seconds
            "metrics_to_collect": [
                "cpu_usage", "memory_usage", "disk_usage",
                "agent_response_time", "workflow_success_rate",
                "error_rate", "throughput"
            ],
            "alert_channels": ["notification_agent", "email", "dashboard"]
        }

    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize monitoring thresholds"""
        return {
            "cpu_usage": {"warning": 70.0, "critical": 85.0},
            "memory_usage": {"warning": 75.0, "critical": 90.0},
            "disk_usage": {"warning": 80.0, "critical": 95.0},
            "response_time": {"warning": 5000.0, "critical": 10000.0},  # milliseconds
            "error_rate": {"warning": 5.0, "critical": 10.0},  # percentage
            "workflow_success_rate": {"warning": 95.0, "critical": 90.0}  # percentage (lower is worse)
        }

    async def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect system performance metrics
        جمع مقاييس أداء النظام
        """
        try:
            timestamp = datetime.now()
            metrics = {}

            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["cpu_usage"] = PerformanceMetric(
                metric_name="cpu_usage",
                metric_type=MetricType.SYSTEM_PERFORMANCE,
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                tags={"component": "system"},
                threshold_warning=self.thresholds["cpu_usage"]["warning"],
                threshold_critical=self.thresholds["cpu_usage"]["critical"]
            )

            # Memory Usage
            memory = psutil.virtual_memory()
            metrics["memory_usage"] = PerformanceMetric(
                metric_name="memory_usage",
                metric_type=MetricType.SYSTEM_PERFORMANCE,
                value=memory.percent,
                unit="percent",
                timestamp=timestamp,
                tags={"component": "system"},
                threshold_warning=self.thresholds["memory_usage"]["warning"],
                threshold_critical=self.thresholds["memory_usage"]["critical"]
            )

            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            metrics["disk_usage"] = PerformanceMetric(
                metric_name="disk_usage",
                metric_type=MetricType.SYSTEM_PERFORMANCE,
                value=disk_percent,
                unit="percent",
                timestamp=timestamp,
                tags={"component": "system"},
                threshold_warning=self.thresholds["disk_usage"]["warning"],
                threshold_critical=self.thresholds["disk_usage"]["critical"]
            )

            # Network I/O
            network = psutil.net_io_counters()
            metrics["network_bytes_sent"] = PerformanceMetric(
                metric_name="network_bytes_sent",
                metric_type=MetricType.SYSTEM_PERFORMANCE,
                value=network.bytes_sent,
                unit="bytes",
                timestamp=timestamp,
                tags={"component": "network", "direction": "sent"}
            )

            # Store metrics
            self.metrics_history.extend(metrics.values())

            # Evaluate alerts
            alerts = await self._evaluate_alerts(metrics)

            return {
                "collection_timestamp": timestamp.isoformat(),
                "metrics_collected": len(metrics),
                "metrics": {name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "warning_threshold": metric.threshold_warning,
                    "critical_threshold": metric.threshold_critical
                } for name, metric in metrics.items()},
                "alerts_triggered": len(alerts),
                "new_alerts": alerts
            }

        except Exception as e:
            return {"error": f"Metrics collection failed: {str(e)}"}

    async def collect_agent_metrics(self, agent_id: str,
                                  execution_time: float,
                                  success: bool,
                                  error_message: str = None) -> Dict[str, Any]:
        """
        Collect agent performance metrics
        جمع مقاييس أداء الوكلاء
        """
        try:
            timestamp = datetime.now()

            # Response time metric
            response_time_metric = PerformanceMetric(
                metric_name="agent_response_time",
                metric_type=MetricType.AGENT_PERFORMANCE,
                value=execution_time,
                unit="milliseconds",
                timestamp=timestamp,
                tags={"agent_id": agent_id},
                threshold_warning=self.thresholds["response_time"]["warning"],
                threshold_critical=self.thresholds["response_time"]["critical"]
            )

            # Success/failure tracking
            success_metric = PerformanceMetric(
                metric_name="agent_success_rate",
                metric_type=MetricType.AGENT_PERFORMANCE,
                value=1.0 if success else 0.0,
                unit="boolean",
                timestamp=timestamp,
                tags={"agent_id": agent_id}
            )

            metrics = [response_time_metric, success_metric]
            self.metrics_history.extend(metrics)

            # Calculate recent success rate for this agent
            recent_executions = [
                m for m in self.metrics_history[-100:]  # Last 100 executions
                if (m.metric_name == "agent_success_rate" and
                    m.tags.get("agent_id") == agent_id and
                    m.timestamp > datetime.now() - timedelta(hours=1))
            ]

            if recent_executions:
                success_rate = (sum(m.value for m in recent_executions) / len(recent_executions)) * 100
            else:
                success_rate = 100.0 if success else 0.0

            return {
                "agent_id": agent_id,
                "execution_time": execution_time,
                "success": success,
                "recent_success_rate": success_rate,
                "metrics_recorded": len(metrics),
                "timestamp": timestamp.isoformat()
            }

        except Exception as e:
            return {"error": f"Agent metrics collection failed: {str(e)}"}

    async def collect_workflow_metrics(self, workflow_id: str,
                                     workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect workflow execution metrics
        جمع مقاييس تنفيذ سير العمل
        """
        try:
            timestamp = datetime.now()

            execution_time = workflow_data.get("execution_time", 0)
            success = workflow_data.get("success", False)
            step_count = workflow_data.get("total_steps", 0)
            completed_steps = workflow_data.get("completed_steps", 0)

            # Workflow execution time
            execution_time_metric = PerformanceMetric(
                metric_name="workflow_execution_time",
                metric_type=MetricType.WORKFLOW_METRICS,
                value=execution_time,
                unit="seconds",
                timestamp=timestamp,
                tags={"workflow_id": workflow_id}
            )

            # Workflow success rate
            success_rate = (completed_steps / step_count) * 100 if step_count > 0 else 0
            success_metric = PerformanceMetric(
                metric_name="workflow_success_rate",
                metric_type=MetricType.WORKFLOW_METRICS,
                value=success_rate,
                unit="percent",
                timestamp=timestamp,
                tags={"workflow_id": workflow_id},
                threshold_warning=self.thresholds["workflow_success_rate"]["warning"],
                threshold_critical=self.thresholds["workflow_success_rate"]["critical"]
            )

            metrics = [execution_time_metric, success_metric]
            self.metrics_history.extend(metrics)

            return {
                "workflow_id": workflow_id,
                "execution_time": execution_time,
                "success_rate": success_rate,
                "completed_steps": completed_steps,
                "total_steps": step_count,
                "metrics_recorded": len(metrics),
                "timestamp": timestamp.isoformat()
            }

        except Exception as e:
            return {"error": f"Workflow metrics collection failed: {str(e)}"}

    async def _evaluate_alerts(self, metrics: Dict[str, PerformanceMetric]) -> List[Alert]:
        """Evaluate metrics against thresholds and generate alerts"""
        new_alerts = []

        for metric_name, metric in metrics.items():
            if metric.threshold_critical and metric.value >= metric.threshold_critical:
                alert = Alert(
                    alert_id=f"alert_{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_level=AlertLevel.CRITICAL,
                    metric_name=metric_name,
                    current_value=metric.value,
                    threshold_value=metric.threshold_critical,
                    message=f"Critical: {metric_name} is {metric.value}{metric.unit}, exceeds critical threshold of {metric.threshold_critical}{metric.unit}",
                    timestamp=datetime.now()
                )
                new_alerts.append(alert)
                self.active_alerts.append(alert)

            elif metric.threshold_warning and metric.value >= metric.threshold_warning:
                alert = Alert(
                    alert_id=f"alert_{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    alert_level=AlertLevel.WARNING,
                    metric_name=metric_name,
                    current_value=metric.value,
                    threshold_value=metric.threshold_warning,
                    message=f"Warning: {metric_name} is {metric.value}{metric.unit}, exceeds warning threshold of {metric.threshold_warning}{metric.unit}",
                    timestamp=datetime.now()
                )
                new_alerts.append(alert)
                self.active_alerts.append(alert)

        return new_alerts

    async def get_system_health_status(self) -> Dict[str, Any]:
        """
        Get overall system health status
        الحصول على حالة صحة النظام العامة
        """
        try:
            # Get recent metrics (last 5 minutes)
            recent_time = datetime.now() - timedelta(minutes=5)
            recent_metrics = [
                m for m in self.metrics_history
                if m.timestamp > recent_time
            ]

            # Calculate health scores
            health_scores = {}
            for metric_type in MetricType:
                type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
                if type_metrics:
                    # Simple health calculation based on threshold breaches
                    total_metrics = len(type_metrics)
                    warning_breaches = sum(1 for m in type_metrics
                                         if m.threshold_warning and m.value >= m.threshold_warning)
                    critical_breaches = sum(1 for m in type_metrics
                                          if m.threshold_critical and m.value >= m.threshold_critical)

                    health_score = max(0, 100 - (warning_breaches * 10) - (critical_breaches * 30))
                    health_scores[metric_type.value] = health_score

            # Overall health score
            overall_health = sum(health_scores.values()) / len(health_scores) if health_scores else 100

            # Determine health status
            if overall_health >= 90:
                health_status = "excellent"
                status_ar = "ممتاز"
            elif overall_health >= 75:
                health_status = "good"
                status_ar = "جيد"
            elif overall_health >= 60:
                health_status = "fair"
                status_ar = "مقبول"
            else:
                health_status = "poor"
                status_ar = "ضعيف"

            # Active alerts summary
            active_alerts_summary = {
                "critical": len([a for a in self.active_alerts if a.alert_level == AlertLevel.CRITICAL and not a.resolved]),
                "warning": len([a for a in self.active_alerts if a.alert_level == AlertLevel.WARNING and not a.resolved]),
                "total": len([a for a in self.active_alerts if not a.resolved])
            }

            return {
                "overall_health_score": overall_health,
                "health_status": health_status,
                "health_status_ar": status_ar,
                "component_health": health_scores,
                "active_alerts": active_alerts_summary,
                "last_updated": datetime.now().isoformat(),
                "metrics_analyzed": len(recent_metrics)
            }

        except Exception as e:
            return {"error": f"Health status calculation failed: {str(e)}"}

    async def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate performance report for specified time period
        إنشاء تقرير الأداء للفترة الزمنية المحددة
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            # Filter metrics for time period
            period_metrics = [
                m for m in self.metrics_history
                if start_time <= m.timestamp <= end_time
            ]

            report = {
                "report_period": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_hours": hours
                },
                "summary": {
                    "total_data_points": len(period_metrics),
                    "metrics_types": len(set(m.metric_type for m in period_metrics)),
                    "alerts_generated": len([a for a in self.active_alerts if start_time <= a.timestamp <= end_time])
                },
                "performance_metrics": {},
                "trend_analysis": {},
                "recommendations": []
            }

            # Analyze metrics by type
            for metric_type in MetricType:
                type_metrics = [m for m in period_metrics if m.metric_type == metric_type]
                if type_metrics:
                    # Calculate statistics
                    values = [m.value for m in type_metrics]
                    report["performance_metrics"][metric_type.value] = {
                        "data_points": len(values),
                        "average": sum(values) / len(values),
                        "minimum": min(values),
                        "maximum": max(values),
                        "latest": values[-1] if values else 0
                    }

            # Generate recommendations
            report["recommendations"] = await self._generate_performance_recommendations(period_metrics)

            return report

        except Exception as e:
            return {"error": f"Performance report generation failed: {str(e)}"}

    async def _generate_performance_recommendations(self, metrics: List[PerformanceMetric]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        # Analyze CPU usage
        cpu_metrics = [m for m in metrics if m.metric_name == "cpu_usage"]
        if cpu_metrics:
            avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
            if avg_cpu > 80:
                recommendations.append("نسبة استخدام المعالج عالية - النظر في توسيع الموارد")
            elif avg_cpu > 60:
                recommendations.append("مراقبة استخدام المعالج وتحسين كفاءة العمليات")

        # Analyze memory usage
        memory_metrics = [m for m in metrics if m.metric_name == "memory_usage"]
        if memory_metrics:
            avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
            if avg_memory > 85:
                recommendations.append("استخدام الذاكرة مرتفع - تنظيف الذاكرة أو زيادة سعة الذاكرة")

        # Analyze response times
        response_metrics = [m for m in metrics if m.metric_name == "agent_response_time"]
        if response_metrics:
            avg_response = sum(m.value for m in response_metrics) / len(response_metrics)
            if avg_response > 5000:
                recommendations.append("أوقات الاستجابة طويلة - تحسين خوارزميات المعالجة")

        if not recommendations:
            recommendations.append("الأداء ضمن المعدلات المقبولة - المتابعة الدورية")

        return recommendations

    async def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Resolve an active alert
        حل تنبيه نشط
        """
        try:
            for alert in self.active_alerts:
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    return {
                        "alert_id": alert_id,
                        "status": "resolved",
                        "resolved_at": datetime.now().isoformat()
                    }

            return {"error": f"Alert {alert_id} not found or already resolved"}

        except Exception as e:
            return {"error": f"Alert resolution failed: {str(e)}"}

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process monitoring tasks"""
        try:
            task_type = task.task_data.get("type", "collect_metrics")

            if task_type == "collect_system_metrics":
                return await self.collect_system_metrics()

            elif task_type == "collect_agent_metrics":
                agent_id = task.task_data.get("agent_id", "")
                execution_time = task.task_data.get("execution_time", 0)
                success = task.task_data.get("success", True)
                error_message = task.task_data.get("error_message")
                return await self.collect_agent_metrics(agent_id, execution_time, success, error_message)

            elif task_type == "collect_workflow_metrics":
                workflow_id = task.task_data.get("workflow_id", "")
                workflow_data = task.task_data.get("workflow_data", {})
                return await self.collect_workflow_metrics(workflow_id, workflow_data)

            elif task_type == "get_health_status":
                return await self.get_system_health_status()

            elif task_type == "generate_report":
                hours = task.task_data.get("hours", 24)
                return await self.generate_performance_report(hours)

            elif task_type == "resolve_alert":
                alert_id = task.task_data.get("alert_id", "")
                return await self.resolve_alert(alert_id)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}