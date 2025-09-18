"""
Orchestrator Agent
وكيل تنسيق العمليات

This agent coordinates and orchestrates the workflow between all 23 AI agents,
managing task distribution, data flow, and ensuring coherent analysis execution.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class WorkflowType(Enum):
    """Types of analysis workflows"""
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    INVESTMENT_RESEARCH = "investment_research"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    MARKET_ANALYSIS = "market_analysis"
    FINANCIAL_FORECAST = "financial_forecast"
    ESG_EVALUATION = "esg_evaluation"
    CUSTOM_WORKFLOW = "custom_workflow"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExecutionStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    step_name: str
    agent_id: str
    dependencies: List[str] = field(default_factory=list)
    task_data: Dict[str, Any] = field(default_factory=dict)
    timeout_minutes: int = 10
    retry_count: int = 0
    max_retries: int = 2
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class AnalysisWorkflow:
    """Complete analysis workflow definition"""
    workflow_id: str
    workflow_name: str
    workflow_type: WorkflowType
    priority: TaskPriority
    steps: List[WorkflowStep]
    created_at: datetime
    requested_by: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None


class OrchestratorAgent(FinancialAgent):
    """
    Master orchestrator agent coordinating all financial analysis workflows
    وكيل تنسيق رئيسي لجميع سير العمل للتحليل المالي
    """

    def __init__(self, agent_id: str = "orchestrator_agent",
                 agent_name_ar: str = "وكيل تنسيق العمليات",
                 agent_name_en: str = "Orchestrator Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'ORCHESTRATOR', 'orchestrator')
        )

        # Workflow management
        self.active_workflows: Dict[str, AnalysisWorkflow] = {}
        self.workflow_templates = self._initialize_workflow_templates()
        self.agent_registry = self._initialize_agent_registry()
        self.execution_engine = self._initialize_execution_engine()

    def _initialize_capabilities(self) -> None:
        """Initialize orchestration capabilities"""
        self.capabilities = {
            "workflow_management": {
                "workflow_creation": True,
                "task_scheduling": True,
                "dependency_resolution": True,
                "parallel_execution": True,
                "error_handling": True,
                "progress_tracking": True
            },
            "agent_coordination": {
                "agent_discovery": True,
                "load_balancing": True,
                "failover_handling": True,
                "result_aggregation": True,
                "data_flow_management": True
            },
            "analysis_types": {
                "comprehensive_analysis": True,
                "risk_assessment": True,
                "investment_research": True,
                "regulatory_compliance": True,
                "market_analysis": True,
                "esg_evaluation": True,
                "forecasting": True
            },
            "quality_assurance": {
                "result_validation": True,
                "consistency_checking": True,
                "completeness_verification": True,
                "accuracy_assessment": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined workflow templates"""
        return {
            "comprehensive_analysis": {
                "name_ar": "التحليل المالي الشامل",
                "name_en": "Comprehensive Financial Analysis",
                "description": "تحليل مالي شامل يغطي جميع جوانب الشركة أو الاستثمار",
                "estimated_duration": 45,  # minutes
                "steps": [
                    {
                        "step_name": "data_extraction",
                        "agent_id": "data_extraction_agent",
                        "dependencies": [],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "data_validation",
                        "agent_id": "data_validation_agent",
                        "dependencies": ["data_extraction"],
                        "timeout_minutes": 3
                    },
                    {
                        "step_name": "financial_analysis",
                        "agent_id": "financial_analysis_agent",
                        "dependencies": ["data_validation"],
                        "timeout_minutes": 8
                    },
                    {
                        "step_name": "risk_assessment",
                        "agent_id": "risk_assessment_agent",
                        "dependencies": ["financial_analysis"],
                        "timeout_minutes": 6
                    },
                    {
                        "step_name": "market_analysis",
                        "agent_id": "market_analysis_agent",
                        "dependencies": ["data_validation"],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "industry_analysis",
                        "agent_id": "industry_expert_agent",
                        "dependencies": ["market_analysis"],
                        "timeout_minutes": 4
                    },
                    {
                        "step_name": "benchmarking",
                        "agent_id": "benchmarking_agent",
                        "dependencies": ["financial_analysis", "industry_analysis"],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "esg_analysis",
                        "agent_id": "esg_analysis_agent",
                        "dependencies": ["data_validation"],
                        "timeout_minutes": 6
                    },
                    {
                        "step_name": "technical_analysis",
                        "agent_id": "technical_analysis_agent",
                        "dependencies": ["market_analysis"],
                        "timeout_minutes": 4
                    },
                    {
                        "step_name": "forecasting",
                        "agent_id": "forecasting_agent",
                        "dependencies": ["financial_analysis", "market_analysis"],
                        "timeout_minutes": 7
                    },
                    {
                        "step_name": "compliance_check",
                        "agent_id": "compliance_agent",
                        "dependencies": ["financial_analysis", "risk_assessment"],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "recommendations",
                        "agent_id": "recommendation_agent",
                        "dependencies": ["benchmarking", "forecasting", "compliance_check"],
                        "timeout_minutes": 6
                    },
                    {
                        "step_name": "quality_assurance",
                        "agent_id": "quality_assurance_agent",
                        "dependencies": ["recommendations"],
                        "timeout_minutes": 4
                    },
                    {
                        "step_name": "report_generation",
                        "agent_id": "report_generation_agent",
                        "dependencies": ["quality_assurance"],
                        "timeout_minutes": 8
                    }
                ]
            },
            "risk_assessment": {
                "name_ar": "تقييم المخاطر المتخصص",
                "name_en": "Specialized Risk Assessment",
                "description": "تقييم شامل للمخاطر المالية والتشغيلية والسوقية",
                "estimated_duration": 25,
                "steps": [
                    {
                        "step_name": "data_extraction",
                        "agent_id": "data_extraction_agent",
                        "dependencies": [],
                        "timeout_minutes": 4
                    },
                    {
                        "step_name": "data_validation",
                        "agent_id": "data_validation_agent",
                        "dependencies": ["data_extraction"],
                        "timeout_minutes": 3
                    },
                    {
                        "step_name": "financial_analysis",
                        "agent_id": "financial_analysis_agent",
                        "dependencies": ["data_validation"],
                        "timeout_minutes": 6
                    },
                    {
                        "step_name": "risk_assessment",
                        "agent_id": "risk_assessment_agent",
                        "dependencies": ["financial_analysis"],
                        "timeout_minutes": 8
                    },
                    {
                        "step_name": "compliance_check",
                        "agent_id": "compliance_agent",
                        "dependencies": ["risk_assessment"],
                        "timeout_minutes": 4
                    },
                    {
                        "step_name": "recommendations",
                        "agent_id": "recommendation_agent",
                        "dependencies": ["compliance_check"],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "report_generation",
                        "agent_id": "report_generation_agent",
                        "dependencies": ["recommendations"],
                        "timeout_minutes": 6
                    }
                ]
            },
            "investment_research": {
                "name_ar": "بحث استثماري متقدم",
                "name_en": "Advanced Investment Research",
                "description": "بحث استثماري شامل مع تحليل القطاع والمقارنات",
                "estimated_duration": 35,
                "steps": [
                    {
                        "step_name": "data_extraction",
                        "agent_id": "data_extraction_agent",
                        "dependencies": [],
                        "timeout_minutes": 4
                    },
                    {
                        "step_name": "market_analysis",
                        "agent_id": "market_analysis_agent",
                        "dependencies": ["data_extraction"],
                        "timeout_minutes": 6
                    },
                    {
                        "step_name": "industry_analysis",
                        "agent_id": "industry_expert_agent",
                        "dependencies": ["market_analysis"],
                        "timeout_minutes": 7
                    },
                    {
                        "step_name": "regional_analysis",
                        "agent_id": "regional_analysis_agent",
                        "dependencies": ["market_analysis"],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "technical_analysis",
                        "agent_id": "technical_analysis_agent",
                        "dependencies": ["market_analysis"],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "benchmarking",
                        "agent_id": "benchmarking_agent",
                        "dependencies": ["industry_analysis"],
                        "timeout_minutes": 6
                    },
                    {
                        "step_name": "forecasting",
                        "agent_id": "forecasting_agent",
                        "dependencies": ["benchmarking", "technical_analysis"],
                        "timeout_minutes": 8
                    },
                    {
                        "step_name": "recommendations",
                        "agent_id": "recommendation_agent",
                        "dependencies": ["forecasting"],
                        "timeout_minutes": 6
                    },
                    {
                        "step_name": "report_generation",
                        "agent_id": "report_generation_agent",
                        "dependencies": ["recommendations"],
                        "timeout_minutes": 8
                    }
                ]
            },
            "esg_evaluation": {
                "name_ar": "تقييم الاستدامة والحوكمة",
                "name_en": "ESG Sustainability Evaluation",
                "description": "تقييم شامل للأداء البيئي والاجتماعي والحوكمة",
                "estimated_duration": 20,
                "steps": [
                    {
                        "step_name": "data_extraction",
                        "agent_id": "data_extraction_agent",
                        "dependencies": [],
                        "timeout_minutes": 3
                    },
                    {
                        "step_name": "esg_analysis",
                        "agent_id": "esg_analysis_agent",
                        "dependencies": ["data_extraction"],
                        "timeout_minutes": 10
                    },
                    {
                        "step_name": "compliance_check",
                        "agent_id": "compliance_agent",
                        "dependencies": ["esg_analysis"],
                        "timeout_minutes": 4
                    },
                    {
                        "step_name": "recommendations",
                        "agent_id": "recommendation_agent",
                        "dependencies": ["compliance_check"],
                        "timeout_minutes": 5
                    },
                    {
                        "step_name": "report_generation",
                        "agent_id": "report_generation_agent",
                        "dependencies": ["recommendations"],
                        "timeout_minutes": 6
                    }
                ]
            }
        }

    def _initialize_agent_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize registry of all available agents"""
        return {
            "data_extraction_agent": {
                "name_ar": "وكيل استخراج البيانات",
                "name_en": "Data Extraction Agent",
                "capabilities": ["document_processing", "data_extraction", "ocr"],
                "average_execution_time": 5,
                "reliability_score": 0.95,
                "max_concurrent_tasks": 3
            },
            "financial_analysis_agent": {
                "name_ar": "وكيل التحليل المالي",
                "name_en": "Financial Analysis Agent",
                "capabilities": ["ratio_analysis", "cash_flow", "profitability"],
                "average_execution_time": 8,
                "reliability_score": 0.92,
                "max_concurrent_tasks": 2
            },
            "risk_assessment_agent": {
                "name_ar": "وكيل تقييم المخاطر",
                "name_en": "Risk Assessment Agent",
                "capabilities": ["credit_risk", "market_risk", "operational_risk"],
                "average_execution_time": 6,
                "reliability_score": 0.90,
                "max_concurrent_tasks": 2
            },
            "market_analysis_agent": {
                "name_ar": "وكيل تحليل السوق",
                "name_en": "Market Analysis Agent",
                "capabilities": ["market_trends", "sector_analysis", "competition"],
                "average_execution_time": 5,
                "reliability_score": 0.88,
                "max_concurrent_tasks": 3
            },
            "recommendation_agent": {
                "name_ar": "وكيل التوصيات",
                "name_en": "Recommendation Agent",
                "capabilities": ["investment_advice", "strategic_recommendations"],
                "average_execution_time": 6,
                "reliability_score": 0.91,
                "max_concurrent_tasks": 2
            },
            "report_generation_agent": {
                "name_ar": "وكيل إنشاء التقارير",
                "name_en": "Report Generation Agent",
                "capabilities": ["report_writing", "visualization", "formatting"],
                "average_execution_time": 8,
                "reliability_score": 0.94,
                "max_concurrent_tasks": 2
            },
            "validation_agent": {
                "name_ar": "وكيل التحقق",
                "name_en": "Validation Agent",
                "capabilities": ["data_validation", "quality_control"],
                "average_execution_time": 3,
                "reliability_score": 0.96,
                "max_concurrent_tasks": 4
            },
            "compliance_agent": {
                "name_ar": "وكيل الامتثال",
                "name_en": "Compliance Agent",
                "capabilities": ["regulatory_compliance", "risk_compliance"],
                "average_execution_time": 5,
                "reliability_score": 0.93,
                "max_concurrent_tasks": 2
            },
            "benchmarking_agent": {
                "name_ar": "وكيل المقارنات المعيارية",
                "name_en": "Benchmarking Agent",
                "capabilities": ["peer_comparison", "industry_benchmarks"],
                "average_execution_time": 5,
                "reliability_score": 0.89,
                "max_concurrent_tasks": 2
            },
            "forecasting_agent": {
                "name_ar": "وكيل التنبؤات المالية",
                "name_en": "Forecasting Agent",
                "capabilities": ["financial_forecasting", "scenario_analysis"],
                "average_execution_time": 7,
                "reliability_score": 0.87,
                "max_concurrent_tasks": 2
            },
            "esg_analysis_agent": {
                "name_ar": "وكيل تحليل الاستدامة",
                "name_en": "ESG Analysis Agent",
                "capabilities": ["esg_assessment", "sustainability_reporting"],
                "average_execution_time": 6,
                "reliability_score": 0.90,
                "max_concurrent_tasks": 2
            },
            "industry_expert_agent": {
                "name_ar": "وكيل الخبرة القطاعية",
                "name_en": "Industry Expert Agent",
                "capabilities": ["sector_expertise", "industry_insights"],
                "average_execution_time": 4,
                "reliability_score": 0.91,
                "max_concurrent_tasks": 3
            },
            "regional_analysis_agent": {
                "name_ar": "وكيل التحليل الإقليمي",
                "name_en": "Regional Analysis Agent",
                "capabilities": ["regional_economics", "cross_border_analysis"],
                "average_execution_time": 5,
                "reliability_score": 0.88,
                "max_concurrent_tasks": 2
            },
            "technical_analysis_agent": {
                "name_ar": "وكيل التحليل الفني",
                "name_en": "Technical Analysis Agent",
                "capabilities": ["chart_analysis", "technical_indicators"],
                "average_execution_time": 4,
                "reliability_score": 0.85,
                "max_concurrent_tasks": 3
            },
            "macroeconomic_agent": {
                "name_ar": "وكيل التحليل الاقتصادي الكلي",
                "name_en": "Macroeconomic Agent",
                "capabilities": ["macroeconomic_analysis", "policy_analysis"],
                "average_execution_time": 6,
                "reliability_score": 0.89,
                "max_concurrent_tasks": 2
            },
            "quality_assurance_agent": {
                "name_ar": "وكيل ضمان الجودة",
                "name_en": "Quality Assurance Agent",
                "capabilities": ["quality_control", "accuracy_verification"],
                "average_execution_time": 4,
                "reliability_score": 0.95,
                "max_concurrent_tasks": 3
            },
            "data_validation_agent": {
                "name_ar": "وكيل التحقق من البيانات",
                "name_en": "Data Validation Agent",
                "capabilities": ["data_verification", "consistency_checking"],
                "average_execution_time": 3,
                "reliability_score": 0.97,
                "max_concurrent_tasks": 4
            },
            "notification_agent": {
                "name_ar": "وكيل إدارة الإشعارات",
                "name_en": "Notification Agent",
                "capabilities": ["notifications", "alerts", "communication"],
                "average_execution_time": 1,
                "reliability_score": 0.98,
                "max_concurrent_tasks": 10
            },
            "security_agent": {
                "name_ar": "وكيل الأمان والحماية",
                "name_en": "Security Agent",
                "capabilities": ["security_monitoring", "access_control"],
                "average_execution_time": 2,
                "reliability_score": 0.99,
                "max_concurrent_tasks": 5
            },
            "monitoring_agent": {
                "name_ar": "وكيل المراقبة والأداء",
                "name_en": "Monitoring Agent",
                "capabilities": ["performance_monitoring", "system_health"],
                "average_execution_time": 2,
                "reliability_score": 0.96,
                "max_concurrent_tasks": 8
            },
            "integration_agent": {
                "name_ar": "وكيل التكامل مع الأنظمة الخارجية",
                "name_en": "Integration Agent",
                "capabilities": ["external_apis", "data_integration"],
                "average_execution_time": 4,
                "reliability_score": 0.92,
                "max_concurrent_tasks": 3
            },
            "learning_agent": {
                "name_ar": "وكيل التعلم المستمر والتحسين",
                "name_en": "Learning Agent",
                "capabilities": ["machine_learning", "model_improvement"],
                "average_execution_time": 10,
                "reliability_score": 0.85,
                "max_concurrent_tasks": 1
            }
        }

    def _initialize_execution_engine(self) -> Dict[str, Any]:
        """Initialize workflow execution engine configuration"""
        return {
            "max_concurrent_workflows": 5,
            "max_concurrent_steps": 10,
            "default_timeout_minutes": 30,
            "retry_policy": {
                "max_retries": 2,
                "retry_delay_seconds": 30,
                "exponential_backoff": True
            },
            "monitoring": {
                "progress_update_interval": 10,  # seconds
                "health_check_interval": 60,     # seconds
                "log_level": "INFO"
            }
        }

    async def create_workflow(self, workflow_type: WorkflowType,
                            input_data: Dict[str, Any],
                            priority: TaskPriority = TaskPriority.MEDIUM,
                            requested_by: str = "system") -> str:
        """
        Create a new analysis workflow
        إنشاء سير عمل تحليل جديد
        """
        try:
            workflow_id = str(uuid.uuid4())

            # Get workflow template
            template = self.workflow_templates.get(workflow_type.value)
            if not template:
                raise ValueError(f"Unknown workflow type: {workflow_type.value}")

            # Create workflow steps
            steps = []
            for step_template in template["steps"]:
                step = WorkflowStep(
                    step_id=f"{workflow_id}_{step_template['step_name']}",
                    step_name=step_template["step_name"],
                    agent_id=step_template["agent_id"],
                    dependencies=step_template.get("dependencies", []),
                    task_data=input_data.copy(),
                    timeout_minutes=step_template.get("timeout_minutes", 10)
                )
                steps.append(step)

            # Create workflow
            workflow = AnalysisWorkflow(
                workflow_id=workflow_id,
                workflow_name=template["name_ar"],
                workflow_type=workflow_type,
                priority=priority,
                steps=steps,
                created_at=datetime.now(),
                requested_by=requested_by,
                input_data=input_data,
                estimated_completion=datetime.now() + timedelta(minutes=template["estimated_duration"])
            )

            # Register workflow
            self.active_workflows[workflow_id] = workflow

            # Send notification
            await self._send_notification({
                "type": "workflow_created",
                "workflow_id": workflow_id,
                "workflow_name": workflow.workflow_name,
                "estimated_duration": template["estimated_duration"]
            })

            return workflow_id

        except Exception as e:
            raise Exception(f"Workflow creation failed: {str(e)}")

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow with all its steps
        تنفيذ سير العمل مع جميع خطواته
        """
        try:
            if workflow_id not in self.active_workflows:
                return {"error": f"Workflow {workflow_id} not found"}

            workflow = self.active_workflows[workflow_id]
            workflow.status = ExecutionStatus.RUNNING

            # Send start notification
            await self._send_notification({
                "type": "workflow_started",
                "workflow_id": workflow_id,
                "workflow_name": workflow.workflow_name
            })

            # Execute workflow steps
            execution_result = await self._execute_workflow_steps(workflow)

            # Update workflow status
            if execution_result["success"]:
                workflow.status = ExecutionStatus.COMPLETED
                workflow.progress_percentage = 100.0
                workflow.output_data = execution_result["results"]
            else:
                workflow.status = ExecutionStatus.FAILED

            # Send completion notification
            await self._send_notification({
                "type": "workflow_completed" if execution_result["success"] else "workflow_failed",
                "workflow_id": workflow_id,
                "workflow_name": workflow.workflow_name,
                "success": execution_result["success"],
                "execution_time": execution_result.get("execution_time", 0)
            })

            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "progress": workflow.progress_percentage,
                "results": workflow.output_data,
                "execution_summary": execution_result
            }

        except Exception as e:
            # Update workflow as failed
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id].status = ExecutionStatus.FAILED

            return {"error": f"Workflow execution failed: {str(e)}"}

    async def _execute_workflow_steps(self, workflow: AnalysisWorkflow) -> Dict[str, Any]:
        """Execute workflow steps in correct order with dependency management"""
        start_time = datetime.now()
        completed_steps = set()
        failed_steps = set()
        step_results = {}

        try:
            # Create dependency graph
            dependency_graph = self._build_dependency_graph(workflow.steps)

            # Execute steps in batches based on dependencies
            while len(completed_steps) < len(workflow.steps) and not failed_steps:
                # Find ready steps (dependencies completed)
                ready_steps = []
                for step in workflow.steps:
                    if (step.step_id not in completed_steps and
                        step.step_id not in failed_steps and
                        all(dep in completed_steps for dep in step.dependencies)):
                        ready_steps.append(step)

                if not ready_steps:
                    if failed_steps:
                        break
                    else:
                        # Circular dependency or other issue
                        raise Exception("No ready steps found - possible circular dependency")

                # Execute ready steps in parallel
                parallel_results = await self._execute_parallel_steps(ready_steps, step_results)

                # Process results
                for step_id, result in parallel_results.items():
                    if result.get("success", False):
                        completed_steps.add(step_id)
                        step_results[step_id] = result.get("data", {})

                        # Update step status
                        for step in workflow.steps:
                            if step.step_id == step_id:
                                step.status = ExecutionStatus.COMPLETED
                                step.result = result.get("data", {})
                                step.end_time = datetime.now()
                                break
                    else:
                        failed_steps.add(step_id)

                        # Update step status
                        for step in workflow.steps:
                            if step.step_id == step_id:
                                step.status = ExecutionStatus.FAILED
                                step.error_message = result.get("error", "Unknown error")
                                step.end_time = datetime.now()
                                break

                # Update progress
                workflow.progress_percentage = (len(completed_steps) / len(workflow.steps)) * 100

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return {
                "success": len(failed_steps) == 0,
                "completed_steps": len(completed_steps),
                "failed_steps": len(failed_steps),
                "total_steps": len(workflow.steps),
                "execution_time": execution_time,
                "results": step_results,
                "step_details": [
                    {
                        "step_id": step.step_id,
                        "step_name": step.step_name,
                        "status": step.status.value,
                        "execution_time": (step.end_time - step.start_time).total_seconds() if step.start_time and step.end_time else 0,
                        "error": step.error_message
                    } for step in workflow.steps
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "completed_steps": len(completed_steps),
                "failed_steps": len(failed_steps) + 1,  # +1 for the exception
                "execution_time": (datetime.now() - start_time).total_seconds()
            }

    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """Build dependency graph for workflow steps"""
        graph = {}
        for step in steps:
            graph[step.step_id] = step.dependencies.copy()
        return graph

    async def _execute_parallel_steps(self, steps: List[WorkflowStep],
                                    previous_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Execute multiple steps in parallel"""
        results = {}

        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=min(len(steps), 5)) as executor:
            # Submit all tasks
            future_to_step = {}
            for step in steps:
                # Prepare task data with previous results
                task_data = step.task_data.copy()
                task_data.update(previous_results)

                # Create task
                task = AgentTask(
                    task_id=step.step_id,
                    task_type=step.step_name,
                    task_data=task_data,
                    priority=1,
                    max_retries=step.max_retries
                )

                # Submit for execution
                future = executor.submit(self._execute_agent_task, step.agent_id, task)
                future_to_step[future] = step

            # Collect results
            for future in as_completed(future_to_step, timeout=300):  # 5 minute timeout
                step = future_to_step[future]
                step.start_time = datetime.now()

                try:
                    result = future.result()
                    results[step.step_id] = {
                        "success": True,
                        "data": result,
                        "agent_id": step.agent_id,
                        "execution_time": (datetime.now() - step.start_time).total_seconds() if step.start_time else 0
                    }
                except Exception as e:
                    results[step.step_id] = {
                        "success": False,
                        "error": str(e),
                        "agent_id": step.agent_id
                    }

        return results

    def _execute_agent_task(self, agent_id: str, task: AgentTask) -> Dict[str, Any]:
        """Execute a task using the specified agent (placeholder implementation)"""
        # This is a placeholder - in real implementation, this would:
        # 1. Load the actual agent instance
        # 2. Execute the task using the agent's process_task method
        # 3. Handle retries and error recovery

        # Simulate agent execution
        import time
        time.sleep(1)  # Simulate processing time

        # Mock successful result
        return {
            "agent_id": agent_id,
            "task_id": task.task_id,
            "status": "completed",
            "result": f"Mock result from {agent_id}",
            "execution_time": 1.0
        }

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get current status of a workflow
        الحصول على حالة سير العمل الحالية
        """
        if workflow_id not in self.active_workflows:
            return {"error": f"Workflow {workflow_id} not found"}

        workflow = self.active_workflows[workflow_id]

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.workflow_name,
            "workflow_type": workflow.workflow_type.value,
            "status": workflow.status.value,
            "progress_percentage": workflow.progress_percentage,
            "created_at": workflow.created_at.isoformat(),
            "estimated_completion": workflow.estimated_completion.isoformat() if workflow.estimated_completion else None,
            "steps_total": len(workflow.steps),
            "steps_completed": len([s for s in workflow.steps if s.status == ExecutionStatus.COMPLETED]),
            "steps_failed": len([s for s in workflow.steps if s.status == ExecutionStatus.FAILED]),
            "current_step": next((s.step_name for s in workflow.steps if s.status == ExecutionStatus.RUNNING), None),
            "step_details": [
                {
                    "step_name": step.step_name,
                    "agent_id": step.agent_id,
                    "status": step.status.value,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "error_message": step.error_message
                } for step in workflow.steps
            ]
        }

    async def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Cancel a running workflow
        إلغاء سير عمل قيد التنفيذ
        """
        if workflow_id not in self.active_workflows:
            return {"error": f"Workflow {workflow_id} not found"}

        workflow = self.active_workflows[workflow_id]

        if workflow.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
            return {"error": f"Workflow {workflow_id} cannot be cancelled (status: {workflow.status.value})"}

        # Update workflow status
        workflow.status = ExecutionStatus.CANCELLED

        # Cancel running steps
        for step in workflow.steps:
            if step.status == ExecutionStatus.RUNNING:
                step.status = ExecutionStatus.CANCELLED
                step.end_time = datetime.now()

        # Send notification
        await self._send_notification({
            "type": "workflow_cancelled",
            "workflow_id": workflow_id,
            "workflow_name": workflow.workflow_name
        })

        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": "cancelled",
            "message": "Workflow cancelled successfully"
        }

    async def list_active_workflows(self) -> Dict[str, Any]:
        """
        List all active workflows
        عرض جميع سير العمل النشطة
        """
        workflows = []

        for workflow_id, workflow in self.active_workflows.items():
            workflows.append({
                "workflow_id": workflow_id,
                "workflow_name": workflow.workflow_name,
                "workflow_type": workflow.workflow_type.value,
                "status": workflow.status.value,
                "progress_percentage": workflow.progress_percentage,
                "created_at": workflow.created_at.isoformat(),
                "requested_by": workflow.requested_by,
                "priority": workflow.priority.value
            })

        # Sort by creation time (newest first)
        workflows.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "total_workflows": len(workflows),
            "active_count": len([w for w in workflows if w["status"] == "running"]),
            "completed_count": len([w for w in workflows if w["status"] == "completed"]),
            "failed_count": len([w for w in workflows if w["status"] == "failed"]),
            "workflows": workflows
        }

    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all registered agents
        الحصول على حالة جميع الوكلاء المسجلين
        """
        agent_status = {}

        for agent_id, agent_info in self.agent_registry.items():
            # Calculate current load (mock implementation)
            current_tasks = 0  # Would be calculated from actual running tasks
            max_tasks = agent_info["max_concurrent_tasks"]

            agent_status[agent_id] = {
                "name_ar": agent_info["name_ar"],
                "name_en": agent_info["name_en"],
                "status": "active" if current_tasks < max_tasks else "busy",
                "current_tasks": current_tasks,
                "max_concurrent_tasks": max_tasks,
                "load_percentage": (current_tasks / max_tasks) * 100,
                "average_execution_time": agent_info["average_execution_time"],
                "reliability_score": agent_info["reliability_score"],
                "capabilities": agent_info["capabilities"]
            }

        return {
            "total_agents": len(agent_status),
            "active_agents": len([a for a in agent_status.values() if a["status"] == "active"]),
            "busy_agents": len([a for a in agent_status.values() if a["status"] == "busy"]),
            "average_load": sum(a["load_percentage"] for a in agent_status.values()) / len(agent_status),
            "agents": agent_status
        }

    async def _send_notification(self, notification_data: Dict[str, Any]) -> None:
        """Send notification through notification agent"""
        try:
            # In real implementation, would call notification_agent
            notification_task = AgentTask(
                task_id=str(uuid.uuid4()),
                task_type="send_notification",
                task_data=notification_data
            )
            # await self.notification_agent.process_task(notification_task)
            pass
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Notification failed: {str(e)}")

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process orchestrator tasks"""
        try:
            task_type = task.task_data.get("type", "create_workflow")

            if task_type == "create_workflow":
                workflow_type = WorkflowType(task.task_data.get("workflow_type", "comprehensive_analysis"))
                input_data = task.task_data.get("input_data", {})
                priority = TaskPriority(task.task_data.get("priority", "medium"))
                requested_by = task.task_data.get("requested_by", "system")

                workflow_id = await self.create_workflow(workflow_type, input_data, priority, requested_by)
                return {"workflow_id": workflow_id, "status": "created"}

            elif task_type == "execute_workflow":
                workflow_id = task.task_data.get("workflow_id")
                return await self.execute_workflow(workflow_id)

            elif task_type == "get_status":
                workflow_id = task.task_data.get("workflow_id")
                return await self.get_workflow_status(workflow_id)

            elif task_type == "cancel_workflow":
                workflow_id = task.task_data.get("workflow_id")
                return await self.cancel_workflow(workflow_id)

            elif task_type == "list_workflows":
                return await self.list_active_workflows()

            elif task_type == "agent_status":
                return await self.get_agent_status()

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}