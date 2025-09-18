"""
AI Agent Orchestrator
منسق الوكلاء الذكيين

This module orchestrates the 23 AI agents, manages their communication,
coordinates multi-agent workflows, and ensures efficient task distribution.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum
import json
from collections import defaultdict, deque
import heapq
from uuid import uuid4

# LangGraph imports for multi-agent workflow orchestration
from langgraph.graph import StateGraph, Graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolExecutor

from .agent_base import BaseAgent, FinancialAgent, AgentType, AgentStatus, AgentTask, AgentMessage
from ..agents.data_extraction_agent import DataExtractionAgent
from ..agents.financial_analysis_agent import FinancialAnalysisAgent
from ..agents.risk_assessment_agent import RiskAssessmentAgent
from ..agents.market_analysis_agent import MarketAnalysisAgent
from ..agents.report_generation_agent import ReportGenerationAgent
from ..agents.recommendation_agent import RecommendationAgent
from ..agents.validation_agent import ValidationAgent


class WorkflowType(Enum):
    """Types of agent workflows"""
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    VALUATION = "valuation"
    REPORT_GENERATION = "report_generation"
    QUICK_ANALYSIS = "quick_analysis"


@dataclass
class WorkflowState:
    """State of a multi-agent workflow"""
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    workflow_type: WorkflowType = WorkflowType.COMPREHENSIVE_ANALYSIS
    status: str = "initialized"
    current_step: int = 0
    total_steps: int = 0
    participating_agents: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    final_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentWorkload:
    """Track agent workload for load balancing"""
    agent_id: str
    current_tasks: int = 0
    queued_tasks: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 100.0
    last_task_completion: Optional[datetime] = None
    specialization_score: Dict[str, float] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Orchestrates all 23 AI agents for comprehensive financial analysis
    ينسق جميع الوكلاء الذكيين الـ 23 للتحليل المالي الشامل
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Agent registry
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[AgentType, List[str]] = defaultdict(list)

        # Workflow management
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.workflow_graphs: Dict[WorkflowType, StateGraph] = {}

        # Task scheduling and load balancing
        self.task_queue = asyncio.PriorityQueue()
        self.agent_workloads: Dict[str, AgentWorkload] = {}

        # Communication management
        self.message_broker = MessageBroker()
        self.communication_history: List[AgentMessage] = []

        # Performance monitoring
        self.performance_metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_workflow_time": 0.0,
            "agent_utilization": {},
            "bottlenecks": []
        }

        # Initialize agents and workflows
        self._initialize_agents()
        self._initialize_workflows()

    def _initialize_agents(self) -> None:
        """Initialize all 23 AI agents according to the specification"""

        # Core Financial Analysis Agents (7 agents)
        core_agents = [
            DataExtractionAgent("data_extraction_001", "مستخرج البيانات الرئيسي", "Primary Data Extractor"),
            FinancialAnalysisAgent("financial_analysis_001", "محلل مالي أساسي", "Primary Financial Analyzer"),
            RiskAssessmentAgent("risk_assessment_001", "محلل المخاطر الرئيسي", "Primary Risk Assessor"),
            MarketAnalysisAgent("market_analysis_001", "محلل السوق الرئيسي", "Primary Market Analyzer"),
            ReportGenerationAgent("report_generation_001", "مولد التقارير الرئيسي", "Primary Report Generator"),
            RecommendationAgent("recommendation_001", "محرك التوصيات الرئيسي", "Primary Recommendation Engine"),
            ValidationAgent("validation_001", "مدقق الجودة الرئيسي", "Primary Quality Validator")
        ]

        # Specialized Financial Analysis Agents (4 agents)
        specialized_financial = [
            FinancialAnalysisAgent("liquidity_specialist_001", "متخصص السيولة", "Liquidity Specialist"),
            FinancialAnalysisAgent("profitability_specialist_001", "متخصص الربحية", "Profitability Specialist"),
            FinancialAnalysisAgent("efficiency_specialist_001", "متخصص الكفاءة", "Efficiency Specialist"),
            FinancialAnalysisAgent("leverage_specialist_001", "متخصص الرافعة المالية", "Leverage Specialist")
        ]

        # Risk Analysis Specialists (3 agents)
        risk_specialists = [
            RiskAssessmentAgent("credit_risk_specialist_001", "متخصص مخاطر الائتمان", "Credit Risk Specialist"),
            RiskAssessmentAgent("market_risk_specialist_001", "متخصص مخاطر السوق", "Market Risk Specialist"),
            RiskAssessmentAgent("operational_risk_specialist_001", "متخصص المخاطر التشغيلية", "Operational Risk Specialist")
        ]

        # Market Analysis Specialists (3 agents)
        market_specialists = [
            MarketAnalysisAgent("valuation_specialist_001", "متخصص التقييم", "Valuation Specialist"),
            MarketAnalysisAgent("competitive_analyst_001", "محلل المنافسة", "Competitive Analyst"),
            MarketAnalysisAgent("sector_analyst_001", "محلل القطاع", "Sector Analyst")
        ]

        # Data Processing Specialists (2 agents)
        data_specialists = [
            DataExtractionAgent("ocr_specialist_001", "متخصص استخراج النصوص", "OCR Specialist"),
            DataExtractionAgent("data_validator_001", "مدقق البيانات", "Data Validator")
        ]

        # Report Generation Specialists (2 agents)
        report_specialists = [
            ReportGenerationAgent("executive_report_specialist_001", "متخصص التقارير التنفيذية", "Executive Report Specialist"),
            ReportGenerationAgent("technical_report_specialist_001", "متخصص التقارير الفنية", "Technical Report Specialist")
        ]

        # Quality Assurance Agents (2 agents)
        qa_agents = [
            ValidationAgent("accuracy_validator_001", "مدقق الدقة", "Accuracy Validator"),
            ValidationAgent("compliance_validator_001", "مدقق الامتثال", "Compliance Validator")
        ]

        # Combine all agents
        all_agents = (
            core_agents + specialized_financial + risk_specialists +
            market_specialists + data_specialists + report_specialists + qa_agents
        )

        # Register agents
        for agent in all_agents:
            self._register_agent(agent)

        self.logger.info(f"Initialized {len(all_agents)} AI agents across {len(self.agent_types)} types")

    def _register_agent(self, agent: BaseAgent) -> None:
        """Register an agent in the orchestrator"""
        self.agents[agent.state.agent_id] = agent
        self.agent_types[agent.state.agent_type].append(agent.state.agent_id)

        # Initialize workload tracking
        self.agent_workloads[agent.state.agent_id] = AgentWorkload(
            agent_id=agent.state.agent_id,
            specialization_score=self._calculate_specialization_scores(agent)
        )

        # Register with message broker
        self.message_broker.register_agent(agent)

        self.logger.debug(f"Registered agent {agent.state.agent_id} ({agent.state.agent_name})")

    def _calculate_specialization_scores(self, agent: BaseAgent) -> Dict[str, float]:
        """Calculate agent specialization scores for task assignment"""
        scores = {}

        # Base scores by agent type
        type_scores = {
            AgentType.DATA_EXTRACTION: {
                "data_extraction": 1.0,
                "ocr_processing": 0.8,
                "data_validation": 0.7
            },
            AgentType.FINANCIAL_ANALYSIS: {
                "financial_analysis": 1.0,
                "ratio_analysis": 0.9,
                "trend_analysis": 0.8,
                "liquidity_analysis": 0.7,
                "profitability_analysis": 0.7
            },
            AgentType.RISK_ASSESSMENT: {
                "risk_analysis": 1.0,
                "credit_risk": 0.9,
                "market_risk": 0.8,
                "operational_risk": 0.8
            },
            AgentType.MARKET_ANALYSIS: {
                "market_analysis": 1.0,
                "valuation": 0.9,
                "competitive_analysis": 0.8,
                "sector_analysis": 0.8
            },
            AgentType.REPORT_GENERATION: {
                "report_generation": 1.0,
                "executive_reporting": 0.8,
                "technical_reporting": 0.8
            },
            AgentType.RECOMMENDATION: {
                "recommendation_generation": 1.0,
                "strategic_advice": 0.8
            },
            AgentType.VALIDATION: {
                "validation": 1.0,
                "quality_assurance": 0.9,
                "compliance_check": 0.8
            }
        }

        base_scores = type_scores.get(agent.state.agent_type, {})

        # Enhance scores based on agent specializations
        for task_type, base_score in base_scores.items():
            enhanced_score = base_score

            # Check if agent has specific specializations
            for specialization in agent.state.specializations:
                if specialization.lower() in task_type.lower():
                    enhanced_score = min(1.0, enhanced_score + 0.1)

            scores[task_type] = enhanced_score

        return scores

    def _initialize_workflows(self) -> None:
        """Initialize LangGraph workflows for different analysis types"""

        # Comprehensive Analysis Workflow
        self.workflow_graphs[WorkflowType.COMPREHENSIVE_ANALYSIS] = self._create_comprehensive_workflow()

        # Risk Assessment Workflow
        self.workflow_graphs[WorkflowType.RISK_ASSESSMENT] = self._create_risk_assessment_workflow()

        # Valuation Workflow
        self.workflow_graphs[WorkflowType.VALUATION] = self._create_valuation_workflow()

        # Report Generation Workflow
        self.workflow_graphs[WorkflowType.REPORT_GENERATION] = self._create_report_generation_workflow()

        # Quick Analysis Workflow
        self.workflow_graphs[WorkflowType.QUICK_ANALYSIS] = self._create_quick_analysis_workflow()

        self.logger.info(f"Initialized {len(self.workflow_graphs)} workflow types")

    def _create_comprehensive_workflow(self) -> StateGraph:
        """Create comprehensive analysis workflow (all 180 analysis types)"""
        workflow = StateGraph(WorkflowState)

        # Define workflow steps
        workflow.add_node("data_extraction", self._data_extraction_step)
        workflow.add_node("data_validation", self._data_validation_step)
        workflow.add_node("financial_analysis", self._financial_analysis_step)
        workflow.add_node("risk_assessment", self._risk_assessment_step)
        workflow.add_node("market_analysis", self._market_analysis_step)
        workflow.add_node("report_generation", self._report_generation_step)
        workflow.add_node("validation", self._validation_step)
        workflow.add_node("recommendation", self._recommendation_step)

        # Define workflow edges
        workflow.add_edge("data_extraction", "data_validation")
        workflow.add_edge("data_validation", "financial_analysis")
        workflow.add_edge("financial_analysis", "risk_assessment")
        workflow.add_edge("risk_assessment", "market_analysis")
        workflow.add_edge("market_analysis", "report_generation")
        workflow.add_edge("report_generation", "validation")
        workflow.add_edge("validation", "recommendation")

        # Set entry and exit points
        workflow.set_entry_point("data_extraction")
        workflow.set_finish_point("recommendation")

        return workflow.compile(checkpointer=MemorySaver())

    def _create_risk_assessment_workflow(self) -> StateGraph:
        """Create specialized risk assessment workflow"""
        workflow = StateGraph(WorkflowState)

        workflow.add_node("data_extraction", self._data_extraction_step)
        workflow.add_node("financial_analysis", self._financial_analysis_step)
        workflow.add_node("credit_risk", self._credit_risk_step)
        workflow.add_node("market_risk", self._market_risk_step)
        workflow.add_node("operational_risk", self._operational_risk_step)
        workflow.add_node("risk_consolidation", self._risk_consolidation_step)
        workflow.add_node("risk_reporting", self._risk_reporting_step)

        # Define workflow edges
        workflow.add_edge("data_extraction", "financial_analysis")
        workflow.add_edge("financial_analysis", "credit_risk")
        workflow.add_edge("financial_analysis", "market_risk")
        workflow.add_edge("financial_analysis", "operational_risk")
        workflow.add_edge("credit_risk", "risk_consolidation")
        workflow.add_edge("market_risk", "risk_consolidation")
        workflow.add_edge("operational_risk", "risk_consolidation")
        workflow.add_edge("risk_consolidation", "risk_reporting")

        workflow.set_entry_point("data_extraction")
        workflow.set_finish_point("risk_reporting")

        return workflow.compile(checkpointer=MemorySaver())

    def _create_valuation_workflow(self) -> StateGraph:
        """Create specialized valuation workflow"""
        workflow = StateGraph(WorkflowState)

        workflow.add_node("data_extraction", self._data_extraction_step)
        workflow.add_node("financial_analysis", self._financial_analysis_step)
        workflow.add_node("dcf_valuation", self._dcf_valuation_step)
        workflow.add_node("comparable_analysis", self._comparable_analysis_step)
        workflow.add_node("market_analysis", self._market_analysis_step)
        workflow.add_node("valuation_consolidation", self._valuation_consolidation_step)
        workflow.add_node("valuation_reporting", self._valuation_reporting_step)

        # Define workflow edges
        workflow.add_edge("data_extraction", "financial_analysis")
        workflow.add_edge("financial_analysis", "dcf_valuation")
        workflow.add_edge("financial_analysis", "comparable_analysis")
        workflow.add_edge("financial_analysis", "market_analysis")
        workflow.add_edge("dcf_valuation", "valuation_consolidation")
        workflow.add_edge("comparable_analysis", "valuation_consolidation")
        workflow.add_edge("market_analysis", "valuation_consolidation")
        workflow.add_edge("valuation_consolidation", "valuation_reporting")

        workflow.set_entry_point("data_extraction")
        workflow.set_finish_point("valuation_reporting")

        return workflow.compile(checkpointer=MemorySaver())

    def _create_report_generation_workflow(self) -> StateGraph:
        """Create report generation workflow"""
        workflow = StateGraph(WorkflowState)

        workflow.add_node("data_consolidation", self._data_consolidation_step)
        workflow.add_node("executive_summary", self._executive_summary_step)
        workflow.add_node("detailed_analysis", self._detailed_analysis_step)
        workflow.add_node("charts_generation", self._charts_generation_step)
        workflow.add_node("recommendations", self._recommendation_step)
        workflow.add_node("formatting", self._formatting_step)
        workflow.add_node("quality_check", self._quality_check_step)

        # Define workflow edges
        workflow.add_edge("data_consolidation", "executive_summary")
        workflow.add_edge("data_consolidation", "detailed_analysis")
        workflow.add_edge("data_consolidation", "charts_generation")
        workflow.add_edge("executive_summary", "formatting")
        workflow.add_edge("detailed_analysis", "formatting")
        workflow.add_edge("charts_generation", "formatting")
        workflow.add_edge("recommendations", "formatting")
        workflow.add_edge("formatting", "quality_check")

        workflow.set_entry_point("data_consolidation")
        workflow.set_finish_point("quality_check")

        return workflow.compile(checkpointer=MemorySaver())

    def _create_quick_analysis_workflow(self) -> StateGraph:
        """Create quick analysis workflow for urgent requests"""
        workflow = StateGraph(WorkflowState)

        workflow.add_node("quick_data_extraction", self._quick_data_extraction_step)
        workflow.add_node("key_metrics", self._key_metrics_step)
        workflow.add_node("risk_flags", self._risk_flags_step)
        workflow.add_node("quick_summary", self._quick_summary_step)

        # Define workflow edges
        workflow.add_edge("quick_data_extraction", "key_metrics")
        workflow.add_edge("key_metrics", "risk_flags")
        workflow.add_edge("risk_flags", "quick_summary")

        workflow.set_entry_point("quick_data_extraction")
        workflow.set_finish_point("quick_summary")

        return workflow.compile(checkpointer=MemorySaver())

    async def execute_workflow(
        self,
        workflow_type: WorkflowType,
        input_data: Dict[str, Any],
        priority: int = 5,
        timeout_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow
        تنفيذ سير عمل متعدد الوكلاء
        """
        workflow_id = str(uuid4())
        start_time = datetime.now()

        # Create workflow state
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            status="running",
            input_data=input_data,
            started_at=start_time,
            metadata={
                "priority": priority,
                "timeout_minutes": timeout_minutes,
                "requested_by": input_data.get("user_id", "system")
            }
        )

        self.active_workflows[workflow_id] = workflow_state

        try:
            self.logger.info(f"Starting workflow {workflow_id} of type {workflow_type.value}")

            # Get the appropriate workflow graph
            workflow_graph = self.workflow_graphs[workflow_type]

            # Execute workflow with timeout
            result = await asyncio.wait_for(
                workflow_graph.ainvoke(workflow_state),
                timeout=timeout_minutes * 60
            )

            # Update workflow state
            workflow_state.status = "completed"
            workflow_state.completed_at = datetime.now()
            workflow_state.final_result = result

            # Update performance metrics
            execution_time = (workflow_state.completed_at - start_time).total_seconds()
            self._update_workflow_metrics(workflow_type, execution_time, success=True)

            self.logger.info(f"Completed workflow {workflow_id} in {execution_time:.2f} seconds")

            return result

        except asyncio.TimeoutError:
            error_msg = f"Workflow {workflow_id} timed out after {timeout_minutes} minutes"
            workflow_state.status = "timeout"
            workflow_state.error = error_msg
            workflow_state.completed_at = datetime.now()

            self.logger.error(error_msg)
            self._update_workflow_metrics(workflow_type, timeout_minutes * 60, success=False)

            raise

        except Exception as e:
            error_msg = f"Workflow {workflow_id} failed: {str(e)}"
            workflow_state.status = "failed"
            workflow_state.error = error_msg
            workflow_state.completed_at = datetime.now()

            execution_time = (workflow_state.completed_at - start_time).total_seconds()
            self._update_workflow_metrics(workflow_type, execution_time, success=False)

            self.logger.error(error_msg)
            raise

        finally:
            # Clean up completed workflow
            if workflow_id in self.active_workflows:
                # Move to history (implement if needed)
                del self.active_workflows[workflow_id]

    # Workflow step implementations
    async def _data_extraction_step(self, state: WorkflowState) -> WorkflowState:
        """Execute data extraction step"""
        agent_id = await self._select_best_agent("data_extraction")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="data_extraction",
            input_data=state.input_data,
            requirements=["financial_documents"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["data_extraction"] = result
        state.current_step += 1

        return state

    async def _data_validation_step(self, state: WorkflowState) -> WorkflowState:
        """Execute data validation step"""
        agent_id = await self._select_best_agent("data_validation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="data_validation",
            input_data=state.intermediate_results.get("data_extraction", {}),
            requirements=["extracted_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["data_validation"] = result
        state.current_step += 1

        return state

    async def _financial_analysis_step(self, state: WorkflowState) -> WorkflowState:
        """Execute comprehensive financial analysis step"""
        # Run multiple financial analysis agents in parallel
        financial_tasks = [
            ("liquidity_analysis", "liquidity_specialist_001"),
            ("profitability_analysis", "profitability_specialist_001"),
            ("efficiency_analysis", "efficiency_specialist_001"),
            ("leverage_analysis", "leverage_specialist_001")
        ]

        results = {}
        tasks = []

        for analysis_type, preferred_agent in financial_tasks:
            agent_id = preferred_agent if preferred_agent in self.agents else await self._select_best_agent("financial_analysis")
            agent = self.agents[agent_id]

            task = AgentTask(
                task_type=analysis_type,
                input_data=state.intermediate_results.get("data_validation", {}),
                requirements=["validated_financial_data"]
            )

            tasks.append(agent.execute_task(task))

        # Execute all financial analysis tasks in parallel
        parallel_results = await asyncio.gather(*tasks)

        for i, (analysis_type, _) in enumerate(financial_tasks):
            results[analysis_type] = parallel_results[i]

        state.intermediate_results["financial_analysis"] = results
        state.current_step += 1

        return state

    async def _risk_assessment_step(self, state: WorkflowState) -> WorkflowState:
        """Execute risk assessment step"""
        agent_id = await self._select_best_agent("risk_analysis")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="comprehensive_risk_assessment",
            input_data={
                "financial_analysis": state.intermediate_results.get("financial_analysis", {}),
                "original_data": state.input_data
            },
            requirements=["financial_analysis_results"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["risk_assessment"] = result
        state.current_step += 1

        return state

    async def _market_analysis_step(self, state: WorkflowState) -> WorkflowState:
        """Execute market analysis step"""
        agent_id = await self._select_best_agent("market_analysis")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="comprehensive_market_analysis",
            input_data={
                "financial_analysis": state.intermediate_results.get("financial_analysis", {}),
                "risk_assessment": state.intermediate_results.get("risk_assessment", {}),
                "original_data": state.input_data
            },
            requirements=["financial_analysis_results", "risk_assessment_results"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["market_analysis"] = result
        state.current_step += 1

        return state

    async def _report_generation_step(self, state: WorkflowState) -> WorkflowState:
        """Execute report generation step"""
        agent_id = await self._select_best_agent("report_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="comprehensive_report",
            input_data={
                "all_analyses": state.intermediate_results,
                "original_data": state.input_data
            },
            requirements=["all_analysis_results"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["report_generation"] = result
        state.current_step += 1

        return state

    async def _validation_step(self, state: WorkflowState) -> WorkflowState:
        """Execute validation step"""
        agent_id = await self._select_best_agent("validation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="quality_validation",
            input_data={
                "report": state.intermediate_results.get("report_generation", {}),
                "all_analyses": state.intermediate_results
            },
            requirements=["generated_report"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["validation"] = result
        state.current_step += 1

        return state

    async def _recommendation_step(self, state: WorkflowState) -> WorkflowState:
        """Execute recommendation generation step"""
        agent_id = await self._select_best_agent("recommendation_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="strategic_recommendations",
            input_data={
                "validated_report": state.intermediate_results.get("validation", {}),
                "all_analyses": state.intermediate_results
            },
            requirements=["validated_report"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["recommendations"] = result
        state.current_step += 1

        return state

    # Additional workflow steps for specialized workflows
    async def _credit_risk_step(self, state: WorkflowState) -> WorkflowState:
        """Execute credit risk analysis step"""
        agent_id = "credit_risk_specialist_001"
        if agent_id not in self.agents:
            agent_id = await self._select_best_agent("risk_analysis")

        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="credit_risk_analysis",
            input_data=state.intermediate_results.get("financial_analysis", {}),
            requirements=["financial_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["credit_risk"] = result
        return state

    async def _market_risk_step(self, state: WorkflowState) -> WorkflowState:
        """Execute market risk analysis step"""
        agent_id = "market_risk_specialist_001"
        if agent_id not in self.agents:
            agent_id = await self._select_best_agent("risk_analysis")

        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="market_risk_analysis",
            input_data=state.intermediate_results.get("financial_analysis", {}),
            requirements=["financial_data", "market_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["market_risk"] = result
        return state

    async def _operational_risk_step(self, state: WorkflowState) -> WorkflowState:
        """Execute operational risk analysis step"""
        agent_id = "operational_risk_specialist_001"
        if agent_id not in self.agents:
            agent_id = await self._select_best_agent("risk_analysis")

        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="operational_risk_analysis",
            input_data=state.intermediate_results.get("financial_analysis", {}),
            requirements=["financial_data", "operational_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["operational_risk"] = result
        return state

    async def _risk_consolidation_step(self, state: WorkflowState) -> WorkflowState:
        """Consolidate all risk analysis results"""
        agent_id = await self._select_best_agent("risk_analysis")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="risk_consolidation",
            input_data={
                "credit_risk": state.intermediate_results.get("credit_risk", {}),
                "market_risk": state.intermediate_results.get("market_risk", {}),
                "operational_risk": state.intermediate_results.get("operational_risk", {})
            },
            requirements=["risk_analysis_results"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["risk_consolidation"] = result
        return state

    async def _risk_reporting_step(self, state: WorkflowState) -> WorkflowState:
        """Generate risk assessment report"""
        agent_id = await self._select_best_agent("report_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="risk_report_generation",
            input_data=state.intermediate_results.get("risk_consolidation", {}),
            requirements=["consolidated_risk_analysis"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["risk_reporting"] = result
        return state

    # Valuation workflow steps
    async def _dcf_valuation_step(self, state: WorkflowState) -> WorkflowState:
        """Execute DCF valuation step"""
        agent_id = "valuation_specialist_001"
        if agent_id not in self.agents:
            agent_id = await self._select_best_agent("market_analysis")

        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="dcf_valuation",
            input_data=state.intermediate_results.get("financial_analysis", {}),
            requirements=["financial_statements", "cash_flow_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["dcf_valuation"] = result
        return state

    async def _comparable_analysis_step(self, state: WorkflowState) -> WorkflowState:
        """Execute comparable company analysis step"""
        agent_id = "competitive_analyst_001"
        if agent_id not in self.agents:
            agent_id = await self._select_best_agent("market_analysis")

        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="comparable_analysis",
            input_data=state.intermediate_results.get("financial_analysis", {}),
            requirements=["financial_ratios", "market_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["comparable_analysis"] = result
        return state

    async def _valuation_consolidation_step(self, state: WorkflowState) -> WorkflowState:
        """Consolidate valuation results"""
        agent_id = await self._select_best_agent("market_analysis")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="valuation_consolidation",
            input_data={
                "dcf_valuation": state.intermediate_results.get("dcf_valuation", {}),
                "comparable_analysis": state.intermediate_results.get("comparable_analysis", {}),
                "market_analysis": state.intermediate_results.get("market_analysis", {})
            },
            requirements=["valuation_results"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["valuation_consolidation"] = result
        return state

    async def _valuation_reporting_step(self, state: WorkflowState) -> WorkflowState:
        """Generate valuation report"""
        agent_id = await self._select_best_agent("report_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="valuation_report",
            input_data=state.intermediate_results.get("valuation_consolidation", {}),
            requirements=["consolidated_valuation"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["valuation_reporting"] = result
        return state

    # Report generation workflow steps
    async def _data_consolidation_step(self, state: WorkflowState) -> WorkflowState:
        """Consolidate all analysis data for reporting"""
        agent_id = await self._select_best_agent("report_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="data_consolidation",
            input_data=state.input_data,
            requirements=["analysis_results"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["data_consolidation"] = result
        return state

    async def _executive_summary_step(self, state: WorkflowState) -> WorkflowState:
        """Generate executive summary"""
        agent_id = "executive_report_specialist_001"
        if agent_id not in self.agents:
            agent_id = await self._select_best_agent("report_generation")

        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="executive_summary",
            input_data=state.intermediate_results.get("data_consolidation", {}),
            requirements=["consolidated_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["executive_summary"] = result
        return state

    async def _detailed_analysis_step(self, state: WorkflowState) -> WorkflowState:
        """Generate detailed analysis section"""
        agent_id = "technical_report_specialist_001"
        if agent_id not in self.agents:
            agent_id = await self._select_best_agent("report_generation")

        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="detailed_analysis",
            input_data=state.intermediate_results.get("data_consolidation", {}),
            requirements=["consolidated_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["detailed_analysis"] = result
        return state

    async def _charts_generation_step(self, state: WorkflowState) -> WorkflowState:
        """Generate charts and visualizations"""
        agent_id = await self._select_best_agent("report_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="charts_generation",
            input_data=state.intermediate_results.get("data_consolidation", {}),
            requirements=["consolidated_data"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["charts_generation"] = result
        return state

    async def _formatting_step(self, state: WorkflowState) -> WorkflowState:
        """Format final report"""
        agent_id = await self._select_best_agent("report_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="report_formatting",
            input_data={
                "executive_summary": state.intermediate_results.get("executive_summary", {}),
                "detailed_analysis": state.intermediate_results.get("detailed_analysis", {}),
                "charts": state.intermediate_results.get("charts_generation", {}),
                "recommendations": state.intermediate_results.get("recommendations", {})
            },
            requirements=["report_sections"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["formatting"] = result
        return state

    async def _quality_check_step(self, state: WorkflowState) -> WorkflowState:
        """Perform final quality check"""
        agent_id = await self._select_best_agent("validation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="quality_check",
            input_data=state.intermediate_results.get("formatting", {}),
            requirements=["formatted_report"]
        )

        result = await agent.execute_task(task)
        state.intermediate_results["quality_check"] = result
        return state

    # Quick analysis workflow steps
    async def _quick_data_extraction_step(self, state: WorkflowState) -> WorkflowState:
        """Quick data extraction for urgent analysis"""
        agent_id = await self._select_best_agent("data_extraction")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="quick_data_extraction",
            input_data=state.input_data,
            requirements=["financial_documents"],
            priority=10  # High priority
        )

        result = await agent.execute_task(task)
        state.intermediate_results["quick_data_extraction"] = result
        return state

    async def _key_metrics_step(self, state: WorkflowState) -> WorkflowState:
        """Calculate key financial metrics quickly"""
        agent_id = await self._select_best_agent("financial_analysis")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="key_metrics_calculation",
            input_data=state.intermediate_results.get("quick_data_extraction", {}),
            requirements=["extracted_data"],
            priority=10
        )

        result = await agent.execute_task(task)
        state.intermediate_results["key_metrics"] = result
        return state

    async def _risk_flags_step(self, state: WorkflowState) -> WorkflowState:
        """Identify critical risk flags"""
        agent_id = await self._select_best_agent("risk_analysis")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="risk_flags_identification",
            input_data=state.intermediate_results.get("key_metrics", {}),
            requirements=["key_metrics"],
            priority=10
        )

        result = await agent.execute_task(task)
        state.intermediate_results["risk_flags"] = result
        return state

    async def _quick_summary_step(self, state: WorkflowState) -> WorkflowState:
        """Generate quick analysis summary"""
        agent_id = await self._select_best_agent("report_generation")
        agent = self.agents[agent_id]

        task = AgentTask(
            task_type="quick_summary_generation",
            input_data={
                "key_metrics": state.intermediate_results.get("key_metrics", {}),
                "risk_flags": state.intermediate_results.get("risk_flags", {})
            },
            requirements=["key_metrics", "risk_flags"],
            priority=10
        )

        result = await agent.execute_task(task)
        state.intermediate_results["quick_summary"] = result
        return state

    async def _select_best_agent(self, task_type: str) -> str:
        """Select the best agent for a specific task type using load balancing and specialization"""
        candidate_agents = []

        # Find agents capable of handling this task type
        for agent_id, workload in self.agent_workloads.items():
            if task_type in workload.specialization_score:
                score = workload.specialization_score[task_type]

                # Calculate overall suitability score
                load_factor = 1.0 / (1 + workload.current_tasks + workload.queued_tasks)
                performance_factor = workload.success_rate / 100.0
                specialization_factor = score

                # Weighted scoring
                overall_score = (
                    specialization_factor * 0.5 +
                    performance_factor * 0.3 +
                    load_factor * 0.2
                )

                candidate_agents.append((agent_id, overall_score))

        if not candidate_agents:
            # Fallback: select any available agent
            available_agents = [aid for aid, agent in self.agents.items()
                             if agent.state.status == AgentStatus.IDLE]
            if available_agents:
                return available_agents[0]
            else:
                # Select least busy agent
                return min(self.agent_workloads.keys(),
                          key=lambda aid: self.agent_workloads[aid].current_tasks)

        # Select agent with highest score
        best_agent_id = max(candidate_agents, key=lambda x: x[1])[0]
        return best_agent_id

    def _update_workflow_metrics(self, workflow_type: WorkflowType, execution_time: float, success: bool) -> None:
        """Update workflow performance metrics"""
        self.performance_metrics["total_workflows"] += 1

        if success:
            self.performance_metrics["successful_workflows"] += 1
        else:
            self.performance_metrics["failed_workflows"] += 1

        # Update average workflow time
        total_workflows = self.performance_metrics["total_workflows"]
        current_avg = self.performance_metrics["average_workflow_time"]
        self.performance_metrics["average_workflow_time"] = (
            (current_avg * (total_workflows - 1) + execution_time) / total_workflows
        )

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = await agent.get_status()

        return {
            "total_agents": len(self.agents),
            "active_workflows": len(self.active_workflows),
            "agent_types_distribution": {
                agent_type.value: len(agent_ids)
                for agent_type, agent_ids in self.agent_types.items()
            },
            "performance_metrics": self.performance_metrics,
            "agent_statuses": agent_statuses,
            "system_health": self._calculate_system_health(),
            "resource_utilization": self._calculate_resource_utilization()
        }

    def _calculate_system_health(self) -> str:
        """Calculate overall system health"""
        total_agents = len(self.agents)
        healthy_agents = len([
            agent for agent in self.agents.values()
            if agent.state.status != AgentStatus.ERROR
        ])

        health_ratio = healthy_agents / total_agents if total_agents > 0 else 0

        if health_ratio >= 0.9:
            return "excellent"
        elif health_ratio >= 0.7:
            return "good"
        elif health_ratio >= 0.5:
            return "fair"
        else:
            return "poor"

    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate resource utilization metrics"""
        total_agents = len(self.agents)
        busy_agents = len([
            agent for agent in self.agents.values()
            if agent.state.status == AgentStatus.WORKING
        ])

        return {
            "agent_utilization": busy_agents / total_agents if total_agents > 0 else 0,
            "workflow_utilization": len(self.active_workflows) / 10,  # Assuming max 10 concurrent workflows
            "average_queue_length": sum(
                workload.queued_tasks for workload in self.agent_workloads.values()
            ) / len(self.agent_workloads) if self.agent_workloads else 0
        }


class MessageBroker:
    """
    Message broker for inter-agent communication
    وسيط الرسائل للتواصل بين الوكلاء
    """

    def __init__(self):
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[AgentMessage] = []
        self.running = False

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the message broker"""
        self.registered_agents[agent.state.agent_id] = agent

    async def start(self) -> None:
        """Start the message broker"""
        self.running = True
        asyncio.create_task(self._process_messages())

    async def stop(self) -> None:
        """Stop the message broker"""
        self.running = False

    async def send_message(self, message: AgentMessage) -> None:
        """Send a message through the broker"""
        await self.message_queue.put(message)

    async def _process_messages(self) -> None:
        """Process messages in the queue"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._deliver_message(message)
                self.message_history.append(message)

                # Keep only last 1000 messages
                if len(self.message_history) > 1000:
                    self.message_history = self.message_history[-1000:]

            except asyncio.TimeoutError:
                continue

    async def _deliver_message(self, message: AgentMessage) -> None:
        """Deliver a message to the target agent"""
        target_agent = self.registered_agents.get(message.receiver_id)

        if target_agent:
            response = await target_agent.receive_message(message)

            if response:
                await self.send_message(response)
        else:
            # Log undeliverable message
            print(f"Cannot deliver message {message.message_id} to unknown agent {message.receiver_id}")