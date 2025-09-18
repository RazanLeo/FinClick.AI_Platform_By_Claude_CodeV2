import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from app import db, current_app, celery
from models import (
    Agent, AgentTask, Workflow, WorkflowExecution, TaskExecution,
    AgentTemplate, AgentType, AgentStatus, TaskStatus, WorkflowStatus
)
import logging
import requests

logger = logging.getLogger(__name__)

class AgentService:
    """Core agent management service"""

    @staticmethod
    def create_agent(user_id, name, agent_type, description=None, configuration=None, capabilities=None):
        """Create a new AI agent"""
        try:
            agent = Agent(
                user_id=user_id,
                name=name,
                description=description,
                agent_type=agent_type,
                configuration=configuration or {},
                capabilities=capabilities or [],
                status=AgentStatus.INACTIVE
            )

            db.session.add(agent)
            db.session.flush()

            # Initialize agent with default configuration
            AgentService.initialize_agent(agent.id)

            return agent

        except Exception as e:
            logger.error(f"Create agent error: {str(e)}")
            raise

    @staticmethod
    def initialize_agent(agent_id):
        """Initialize agent with default settings"""
        try:
            agent = Agent.query.get(agent_id)
            if not agent:
                raise ValueError("Agent not found")

            # Set default configuration based on agent type
            default_configs = {
                AgentType.FINANCIAL_ANALYST: {
                    'model': 'gpt-4',
                    'temperature': 0.1,
                    'max_tokens': 2000,
                    'capabilities': ['financial_analysis', 'ratio_calculation', 'trend_analysis']
                },
                AgentType.DATA_PROCESSOR: {
                    'model': 'gpt-3.5-turbo',
                    'temperature': 0.0,
                    'max_tokens': 1500,
                    'capabilities': ['data_extraction', 'data_cleaning', 'data_validation']
                },
                AgentType.REPORT_GENERATOR: {
                    'model': 'gpt-4',
                    'temperature': 0.3,
                    'max_tokens': 3000,
                    'capabilities': ['report_writing', 'chart_generation', 'summarization']
                }
            }

            default_config = default_configs.get(agent.agent_type, {})
            if default_config:
                agent.configuration.update(default_config)
                agent.capabilities = default_config.get('capabilities', [])

        except Exception as e:
            logger.error(f"Initialize agent error: {str(e)}")
            raise

    @staticmethod
    def activate_agent(agent_id):
        """Activate an agent"""
        try:
            agent = Agent.query.get(agent_id)
            if agent:
                agent.status = AgentStatus.ACTIVE
                agent.updated_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Activate agent error: {str(e)}")
            raise

    @staticmethod
    def deactivate_agent(agent_id):
        """Deactivate an agent"""
        try:
            agent = Agent.query.get(agent_id)
            if agent:
                agent.status = AgentStatus.INACTIVE
                agent.updated_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Deactivate agent error: {str(e)}")
            raise

class TaskService:
    """Task management service"""

    @staticmethod
    def create_task(agent_id, user_id, task_name, task_type, task_description=None,
                   input_data=None, parameters=None, priority=5):
        """Create a new task"""
        try:
            task = AgentTask(
                agent_id=agent_id,
                user_id=user_id,
                task_name=task_name,
                task_description=task_description,
                task_type=task_type,
                input_data=input_data or {},
                parameters=parameters or {},
                priority=priority,
                status=TaskStatus.PENDING
            )

            db.session.add(task)
            db.session.flush()

            return task

        except Exception as e:
            logger.error(f"Create task error: {str(e)}")
            raise

    @staticmethod
    def execute_task_async(task_id):
        """Execute task asynchronously using Celery"""
        try:
            result = execute_agent_task.delay(task_id)
            return result.id

        except Exception as e:
            logger.error(f"Execute task async error: {str(e)}")
            raise

    @staticmethod
    def execute_task(task_id):
        """Execute a task"""
        try:
            task = AgentTask.query.get(task_id)
            if not task:
                raise ValueError("Task not found")

            agent = Agent.query.get(task.agent_id)
            if not agent:
                raise ValueError("Agent not found")

            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            task.progress_percentage = 0

            # Create execution record
            execution = TaskExecution(
                task_id=task_id,
                execution_log="Task execution started"
            )
            db.session.add(execution)

            # Execute based on agent type
            if agent.agent_type == AgentType.FINANCIAL_ANALYST:
                result = TaskService.execute_financial_analysis_task(task, agent)
            elif agent.agent_type == AgentType.DATA_PROCESSOR:
                result = TaskService.execute_data_processing_task(task, agent)
            elif agent.agent_type == AgentType.REPORT_GENERATOR:
                result = TaskService.execute_report_generation_task(task, agent)
            else:
                result = TaskService.execute_generic_task(task, agent)

            # Update task with results
            task.output_data = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.progress_percentage = 100
            task.actual_duration = int((task.completed_at - task.started_at).total_seconds())

            # Update agent statistics
            agent.total_tasks += 1
            agent.successful_tasks += 1
            agent.last_used_at = datetime.utcnow()

            # Update execution record
            execution.completed_at = datetime.utcnow()
            execution.execution_log += "\nTask completed successfully"

            return result

        except Exception as e:
            logger.error(f"Execute task error: {str(e)}")

            # Update task with error
            if 'task' in locals():
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.utcnow()

            raise

    @staticmethod
    def execute_financial_analysis_task(task, agent):
        """Execute financial analysis task"""
        try:
            # Mock financial analysis
            input_data = task.input_data

            result = {
                'analysis_type': 'financial_statement_analysis',
                'metrics': {
                    'liquidity_ratio': 2.5,
                    'profitability_margin': 15.2,
                    'debt_to_equity': 0.4
                },
                'insights': [
                    'Strong liquidity position',
                    'Healthy profit margins',
                    'Conservative debt levels'
                ],
                'recommendations': [
                    'Consider expanding operations',
                    'Optimize working capital'
                ],
                'confidence_score': 0.85,
                'processed_at': datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Execute financial analysis task error: {str(e)}")
            raise

    @staticmethod
    def execute_data_processing_task(task, agent):
        """Execute data processing task"""
        try:
            # Mock data processing
            input_data = task.input_data

            result = {
                'processing_type': 'data_extraction_cleaning',
                'processed_records': 1250,
                'valid_records': 1180,
                'invalid_records': 70,
                'data_quality_score': 94.4,
                'extracted_fields': [
                    'company_name', 'revenue', 'expenses',
                    'assets', 'liabilities', 'date'
                ],
                'processing_summary': 'Data successfully extracted and validated',
                'processed_at': datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Execute data processing task error: {str(e)}")
            raise

    @staticmethod
    def execute_report_generation_task(task, agent):
        """Execute report generation task"""
        try:
            # Mock report generation
            input_data = task.input_data

            result = {
                'report_type': 'financial_summary_report',
                'report_id': str(uuid.uuid4()),
                'pages_generated': 15,
                'charts_created': 8,
                'tables_created': 12,
                'sections': [
                    'Executive Summary',
                    'Financial Performance',
                    'Key Metrics',
                    'Recommendations'
                ],
                'download_url': f'/api/reports/download/{uuid.uuid4()}',
                'generated_at': datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Execute report generation task error: {str(e)}")
            raise

    @staticmethod
    def execute_generic_task(task, agent):
        """Execute generic task"""
        try:
            result = {
                'task_type': task.task_type,
                'status': 'completed',
                'message': f'Task {task.task_name} completed successfully',
                'processed_at': datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Execute generic task error: {str(e)}")
            raise

class WorkflowService:
    """Workflow management service"""

    @staticmethod
    def create_workflow(user_id, name, primary_agent_id, description=None,
                       workflow_definition=None, trigger_config=None, schedule_config=None):
        """Create a new workflow"""
        try:
            workflow = Workflow(
                user_id=user_id,
                primary_agent_id=primary_agent_id,
                name=name,
                description=description,
                workflow_definition=workflow_definition or {},
                trigger_config=trigger_config,
                schedule_config=schedule_config,
                status=WorkflowStatus.DRAFT,
                total_steps=len(workflow_definition.get('steps', [])) if workflow_definition else 0
            )

            db.session.add(workflow)
            db.session.flush()

            return workflow

        except Exception as e:
            logger.error(f"Create workflow error: {str(e)}")
            raise

    @staticmethod
    def execute_workflow(workflow_id, execution_context=None):
        """Execute a workflow"""
        try:
            workflow = Workflow.query.get(workflow_id)
            if not workflow:
                raise ValueError("Workflow not found")

            # Create execution record
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                execution_context=execution_context or {},
                status=WorkflowStatus.RUNNING
            )
            db.session.add(execution)
            db.session.flush()

            # Execute workflow steps asynchronously
            execute_workflow_steps.delay(execution.id)

            # Update workflow statistics
            workflow.execution_count += 1
            workflow.last_execution_at = datetime.utcnow()

            return execution

        except Exception as e:
            logger.error(f"Execute workflow error: {str(e)}")
            raise

class TemplateService:
    """Agent template service"""

    @staticmethod
    def get_templates(agent_type=None, category=None):
        """Get available templates"""
        try:
            query = AgentTemplate.query.filter_by(is_active=True)

            if agent_type:
                try:
                    type_enum = AgentType(agent_type)
                    query = query.filter_by(agent_type=type_enum)
                except ValueError:
                    pass

            if category:
                query = query.filter_by(category=category)

            return query.order_by(AgentTemplate.usage_count.desc()).all()

        except Exception as e:
            logger.error(f"Get templates error: {str(e)}")
            return []

    @staticmethod
    def create_agent_from_template(template_id, user_id, name=None, customizations=None):
        """Create agent from template"""
        try:
            template = AgentTemplate.query.get(template_id)
            if not template:
                raise ValueError("Template not found")

            # Generate name if not provided
            if not name:
                name = f"{template.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

            # Merge configurations
            configuration = template.template_config.copy()
            if customizations:
                configuration.update(customizations)

            # Create agent
            agent = AgentService.create_agent(
                user_id=user_id,
                name=name,
                agent_type=template.agent_type,
                description=template.description,
                configuration=configuration,
                capabilities=template.default_capabilities or []
            )

            # Update template usage
            template.usage_count += 1

            return agent

        except Exception as e:
            logger.error(f"Create agent from template error: {str(e)}")
            raise

class OrchestrationService:
    """Agent orchestration service"""

    @staticmethod
    def get_user_orchestration_status(user_id):
        """Get orchestration status for user"""
        try:
            # Count active agents
            active_agents = Agent.query.filter_by(
                user_id=user_id,
                status=AgentStatus.ACTIVE
            ).count()

            # Count running tasks
            running_tasks = AgentTask.query.filter_by(
                user_id=user_id,
                status=TaskStatus.RUNNING
            ).count()

            # Count active workflows
            active_workflows = Workflow.query.filter_by(
                user_id=user_id,
                status=WorkflowStatus.ACTIVE
            ).count()

            return {
                'active_agents': active_agents,
                'running_tasks': running_tasks,
                'active_workflows': active_workflows,
                'system_load': OrchestrationService.get_system_load()
            }

        except Exception as e:
            logger.error(f"Get orchestration status error: {str(e)}")
            return {}

    @staticmethod
    def get_system_load():
        """Get current system load"""
        try:
            # Mock system load calculation
            return {
                'cpu_usage': 45.2,
                'memory_usage': 62.8,
                'active_tasks': 23,
                'queue_size': 8
            }

        except Exception as e:
            logger.error(f"Get system load error: {str(e)}")
            return {}

    @staticmethod
    def batch_execute_tasks(user_id, tasks):
        """Execute multiple tasks in batch"""
        try:
            execution_results = []

            for task_data in tasks:
                try:
                    task = TaskService.create_task(
                        agent_id=task_data['agent_id'],
                        user_id=user_id,
                        task_name=task_data['task_name'],
                        task_type=task_data['task_type'],
                        input_data=task_data.get('input_data'),
                        parameters=task_data.get('parameters', {}),
                        priority=task_data.get('priority', 5)
                    )

                    execution_id = TaskService.execute_task_async(task.id)

                    execution_results.append({
                        'task_id': task.id,
                        'execution_id': execution_id,
                        'status': 'queued'
                    })

                except Exception as e:
                    execution_results.append({
                        'error': str(e),
                        'status': 'failed'
                    })

            return execution_results

        except Exception as e:
            logger.error(f"Batch execute tasks error: {str(e)}")
            raise

    @staticmethod
    def communicate_with_agent(agent_id, user_id, message, context=None):
        """Communicate with an agent"""
        try:
            agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
            if not agent:
                raise ValueError("Agent not found")

            # Mock agent communication
            response = {
                'agent_id': agent_id,
                'agent_name': agent.name,
                'response': f"Hello! I'm {agent.name}, your {agent.agent_type.value} agent. How can I help you with your request: '{message}'?",
                'capabilities': agent.capabilities,
                'suggested_actions': [
                    'Run financial analysis',
                    'Generate report',
                    'Process data'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }

            return response

        except Exception as e:
            logger.error(f"Communicate with agent error: {str(e)}")
            raise

# Celery Tasks
@celery.task
def execute_agent_task(task_id):
    """Celery task to execute agent task"""
    try:
        with current_app.app_context():
            return TaskService.execute_task(task_id)
    except Exception as e:
        logger.error(f"Celery execute task error: {str(e)}")
        raise

@celery.task
def execute_workflow_steps(execution_id):
    """Celery task to execute workflow steps"""
    try:
        with current_app.app_context():
            execution = WorkflowExecution.query.get(execution_id)
            if not execution:
                raise ValueError("Workflow execution not found")

            workflow = execution.workflow
            steps = workflow.workflow_definition.get('steps', [])

            for i, step in enumerate(steps):
                try:
                    # Execute step
                    execution.current_step = i + 1
                    execution.completed_steps = i
                    db.session.commit()

                    # Mock step execution
                    time.sleep(2)  # Simulate processing time

                except Exception as e:
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = str(e)
                    execution.failed_step = i + 1
                    execution.completed_at = datetime.utcnow()
                    db.session.commit()
                    raise

            # Mark as completed
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_steps = len(steps)
            execution.completed_at = datetime.utcnow()

            # Update workflow statistics
            workflow.success_count += 1

            db.session.commit()

    except Exception as e:
        logger.error(f"Celery execute workflow error: {str(e)}")
        raise