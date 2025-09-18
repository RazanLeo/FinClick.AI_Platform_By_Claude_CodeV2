"""
AI Agent Base Classes
فئات الوكلاء الذكيين الأساسية

This module provides the foundational classes for all AI agents in the FinClick.AI platform.
Each agent specializes in specific financial analysis tasks and can communicate with other agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import json
import logging
from uuid import uuid4

# LangGraph imports for multi-agent orchestration
from langgraph.graph import Graph, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class AgentType(Enum):
    """Types of AI agents in the system"""
    DATA_EXTRACTION = "data_extraction"
    FINANCIAL_ANALYSIS = "financial_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_ANALYSIS = "market_analysis"
    REPORT_GENERATION = "report_generation"
    RECOMMENDATION = "recommendation"
    VALIDATION = "validation"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


@dataclass
class AgentTask:
    """Task assigned to an agent"""
    task_id: str = field(default_factory=lambda: str(uuid4()))
    task_type: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    priority: int = 1  # 1-10, 10 being highest
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)  # Task IDs this task depends on
    assigned_agent: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentState:
    """State of an AI agent"""
    agent_id: str
    agent_name: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[AgentTask] = None
    capabilities: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    total_tasks_completed: int = 0
    success_rate: float = 100.0
    average_execution_time: float = 0.0


@dataclass
class AgentMessage:
    """Message between agents"""
    message_id: str = field(default_factory=lambda: str(uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: str = "info"  # info, request, response, error, broadcast
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False
    response_to: Optional[str] = None  # Message ID this is responding to


class BaseAgent(ABC):
    """
    Base class for all AI agents
    الفئة الأساسية لجميع الوكلاء الذكيين
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: AgentType,
        model_name: str = "gpt-4",
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        self.state = AgentState(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type
        )

        # LLM configuration
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Communication
        self.message_queue: List[AgentMessage] = []
        self.message_handlers: Dict[str, Callable] = {}

        # Task management
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []

        # Logging
        self.logger = logging.getLogger(f"agent_{agent_id}")

        # Performance tracking
        self.execution_times: List[float] = []
        self.error_count: int = 0

        # Initialize agent-specific capabilities
        self._initialize_capabilities()
        self._initialize_prompts()

    @abstractmethod
    def _initialize_capabilities(self) -> None:
        """Initialize agent-specific capabilities"""
        pass

    @abstractmethod
    def _initialize_prompts(self) -> None:
        """Initialize agent-specific prompts and templates"""
        pass

    @abstractmethod
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a specific task assigned to this agent"""
        pass

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task with full lifecycle management
        تنفيذ مهمة مع إدارة دورة الحياة الكاملة
        """
        start_time = datetime.now()
        task.started_at = start_time
        task.status = AgentStatus.WORKING
        self.state.current_task = task
        self.state.status = AgentStatus.WORKING

        try:
            self.logger.info(f"Starting task {task.task_id} of type {task.task_type}")

            # Validate task requirements
            validation_result = await self._validate_task(task)
            if not validation_result["valid"]:
                raise ValueError(f"Task validation failed: {validation_result['errors']}")

            # Pre-processing
            await self._pre_process_task(task)

            # Main processing
            result = await self.process_task(task)

            # Post-processing
            result = await self._post_process_task(task, result)

            # Mark as completed
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result

            # Update performance metrics
            execution_time = (task.completed_at - start_time).total_seconds()
            self._update_performance_metrics(execution_time, success=True)

            self.completed_tasks.append(task)
            self.state.current_task = None
            self.state.status = AgentStatus.IDLE
            self.state.total_tasks_completed += 1

            self.logger.info(f"Completed task {task.task_id} in {execution_time:.2f} seconds")

            return result

        except Exception as e:
            # Handle errors
            error_msg = str(e)
            task.status = AgentStatus.ERROR
            task.error = error_msg
            task.completed_at = datetime.now()

            # Update performance metrics
            execution_time = (task.completed_at - start_time).total_seconds()
            self._update_performance_metrics(execution_time, success=False)

            self.state.current_task = None
            self.state.status = AgentStatus.IDLE
            self.error_count += 1

            self.logger.error(f"Task {task.task_id} failed: {error_msg}")

            raise

    async def _validate_task(self, task: AgentTask) -> Dict[str, Any]:
        """Validate task before execution"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Check if agent can handle this task type
        if task.task_type not in self.state.capabilities:
            validation["valid"] = False
            validation["errors"].append(f"Agent cannot handle task type: {task.task_type}")

        # Check input data requirements
        for req in task.requirements:
            if req not in task.input_data:
                validation["valid"] = False
                validation["errors"].append(f"Missing required input: {req}")

        return validation

    async def _pre_process_task(self, task: AgentTask) -> None:
        """Pre-process task before main execution"""
        # Default implementation - can be overridden by specific agents
        self.logger.debug(f"Pre-processing task {task.task_id}")

    async def _post_process_task(self, task: AgentTask, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process task result"""
        # Default implementation - can be overridden by specific agents
        result["processing_metadata"] = {
            "agent_id": self.state.agent_id,
            "agent_name": self.state.agent_name,
            "task_id": task.task_id,
            "execution_time": (datetime.now() - task.started_at).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }

        return result

    def _update_performance_metrics(self, execution_time: float, success: bool) -> None:
        """Update agent performance metrics"""
        self.execution_times.append(execution_time)

        # Keep only last 100 execution times for rolling average
        if len(self.execution_times) > 100:
            self.execution_times = self.execution_times[-100:]

        # Update average execution time
        self.state.average_execution_time = sum(self.execution_times) / len(self.execution_times)

        # Update success rate
        total_tasks = self.state.total_tasks_completed + self.error_count + (1 if success else 0)
        if not success:
            self.error_count += 1

        if total_tasks > 0:
            self.state.success_rate = ((total_tasks - self.error_count) / total_tasks) * 100

        # Update last activity
        self.state.last_activity = datetime.now()

    async def send_message(self, receiver_id: str, message_type: str, content: Dict[str, Any],
                          requires_response: bool = False) -> str:
        """Send message to another agent"""
        message = AgentMessage(
            sender_id=self.state.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            requires_response=requires_response
        )

        self.logger.debug(f"Sending message {message.message_id} to {receiver_id}")

        # In a real implementation, this would use the message broker
        # For now, we'll just add to a queue that the orchestrator can process
        return message.message_id

    async def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Receive and process a message from another agent"""
        self.logger.debug(f"Received message {message.message_id} from {message.sender_id}")

        # Check if there's a specific handler for this message type
        handler = self.message_handlers.get(message.message_type)

        if handler:
            response_content = await handler(message)

            if message.requires_response and response_content:
                response = AgentMessage(
                    sender_id=self.state.agent_id,
                    receiver_id=message.sender_id,
                    message_type="response",
                    content=response_content,
                    response_to=message.message_id
                )
                return response

        return None

    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler

    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "agent_id": self.state.agent_id,
            "agent_name": self.state.agent_name,
            "agent_type": self.state.agent_type.value,
            "status": self.state.status.value,
            "current_task": self.state.current_task.task_id if self.state.current_task else None,
            "capabilities": self.state.capabilities,
            "specializations": self.state.specializations,
            "performance_metrics": {
                "total_tasks_completed": self.state.total_tasks_completed,
                "success_rate": self.state.success_rate,
                "average_execution_time": self.state.average_execution_time,
                "current_queue_size": len(self.task_queue)
            },
            "last_activity": self.state.last_activity.isoformat()
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown the agent"""
        self.logger.info(f"Shutting down agent {self.state.agent_id}")

        # Complete current task if any
        if self.state.current_task:
            self.logger.warning("Interrupting current task due to shutdown")
            self.state.current_task.status = AgentStatus.ERROR
            self.state.current_task.error = "Agent shutdown"

        # Clear queues
        self.task_queue.clear()
        self.message_queue.clear()

        self.state.status = AgentStatus.IDLE

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.state.agent_id}, name={self.state.agent_name}, status={self.state.status.value})>"


class FinancialAgent(BaseAgent):
    """
    Specialized base class for financial analysis agents
    الفئة الأساسية المتخصصة لوكلاء التحليل المالي
    """

    def __init__(self, agent_id: str, agent_name: str, agent_type: AgentType, **kwargs):
        super().__init__(agent_id, agent_name, agent_type, **kwargs)

        # Financial analysis specific configuration
        self.financial_knowledge_base = {}
        self.industry_benchmarks = {}
        self.analysis_templates = {}

    def _initialize_capabilities(self) -> None:
        """Initialize financial analysis capabilities"""
        base_capabilities = [
            "financial_data_processing",
            "ratio_calculation",
            "trend_analysis",
            "benchmark_comparison",
            "insight_generation"
        ]
        self.state.capabilities.extend(base_capabilities)

    def _initialize_prompts(self) -> None:
        """Initialize financial analysis prompts"""
        self.base_system_prompt = """
        أنت وكيل ذكي متخصص في التحليل المالي لمنصة FinClick.AI.
        مهمتك هي تحليل البيانات المالية وتقديم رؤى دقيقة ومفيدة.

        You are an intelligent financial analysis agent for the FinClick.AI platform.
        Your task is to analyze financial data and provide accurate, useful insights.

        قواعد مهمة:
        - استخدم البيانات المالية الفعلية فقط
        - قدم تحليلاً موضوعياً ومبنياً على الأدلة
        - اربط النتائج بالمعايير الصناعية
        - قدم توصيات عملية قابلة للتنفيذ

        Important guidelines:
        - Use only actual financial data
        - Provide objective, evidence-based analysis
        - Connect results to industry standards
        - Provide actionable recommendations
        """

    async def analyze_financial_data(self, data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Generic financial data analysis method"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.base_system_prompt),
            ("human", f"""
            قم بتحليل البيانات المالية التالية من نوع {analysis_type}:

            البيانات: {json.dumps(data, indent=2, ensure_ascii=False)}

            Please analyze the following financial data for {analysis_type}:

            Data: {json.dumps(data, indent=2)}

            قدم تحليلاً شاملاً يتضمن:
            1. النتائج الرئيسية
            2. المؤشرات المهمة
            3. المقارنات مع المعايير
            4. التوصيات

            Provide comprehensive analysis including:
            1. Key findings
            2. Important indicators
            3. Benchmark comparisons
            4. Recommendations
            """)
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({"data": data, "analysis_type": analysis_type})

        return {
            "analysis_type": analysis_type,
            "raw_response": response.content,
            "structured_insights": self._extract_insights_from_response(response.content),
            "confidence_score": self._calculate_confidence_score(data, analysis_type)
        }

    def _extract_insights_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract structured insights from LLM response"""
        # This would implement NLP parsing to extract structured insights
        # For now, return a simplified structure
        insights = []

        # Simple keyword-based extraction (would be more sophisticated in production)
        if "مرتفع" in response or "high" in response.lower():
            insights.append({
                "type": "warning",
                "level": "high",
                "message": "High level indicator detected"
            })

        if "منخفض" in response or "low" in response.lower():
            insights.append({
                "type": "alert",
                "level": "low",
                "message": "Low level indicator detected"
            })

        if "ممتاز" in response or "excellent" in response.lower():
            insights.append({
                "type": "positive",
                "level": "high",
                "message": "Excellent performance indicator"
            })

        return insights

    def _calculate_confidence_score(self, data: Dict[str, Any], analysis_type: str) -> float:
        """Calculate confidence score for the analysis"""
        # Base confidence
        confidence = 0.8

        # Adjust based on data completeness
        if isinstance(data, dict):
            total_fields = len(data)
            non_null_fields = len([v for v in data.values() if v is not None and v != 0])
            completeness_ratio = non_null_fields / total_fields if total_fields > 0 else 0
            confidence *= (0.5 + 0.5 * completeness_ratio)

        # Adjust based on analysis type complexity
        complex_analyses = ["valuation", "risk_assessment", "market_analysis"]
        if analysis_type in complex_analyses:
            confidence *= 0.9

        return min(1.0, max(0.1, confidence))


# Utility functions for agent management
def create_agent_id(agent_type: str, instance_number: int = 1) -> str:
    """Create standardized agent ID"""
    return f"{agent_type}_agent_{instance_number:03d}"


def validate_agent_communication(sender: BaseAgent, receiver: BaseAgent, message_type: str) -> bool:
    """Validate if two agents can communicate"""
    # Define communication rules
    communication_matrix = {
        AgentType.DATA_EXTRACTION: [AgentType.FINANCIAL_ANALYSIS, AgentType.VALIDATION],
        AgentType.FINANCIAL_ANALYSIS: [AgentType.RISK_ASSESSMENT, AgentType.MARKET_ANALYSIS, AgentType.REPORT_GENERATION],
        AgentType.RISK_ASSESSMENT: [AgentType.RECOMMENDATION, AgentType.REPORT_GENERATION],
        AgentType.MARKET_ANALYSIS: [AgentType.RECOMMENDATION, AgentType.REPORT_GENERATION],
        AgentType.REPORT_GENERATION: [AgentType.VALIDATION],
        AgentType.RECOMMENDATION: [AgentType.REPORT_GENERATION],
        AgentType.VALIDATION: []  # Can communicate with all
    }

    # Check if communication is allowed
    allowed_receivers = communication_matrix.get(sender.state.agent_type, [])

    # Validation agents can communicate with anyone
    if sender.state.agent_type == AgentType.VALIDATION or receiver.state.agent_type == AgentType.VALIDATION:
        return True

    return receiver.state.agent_type in allowed_receivers