from app import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import enum
import json

class AgentType(enum.Enum):
    FINANCIAL_ANALYST = "financial_analyst"
    DATA_PROCESSOR = "data_processor"
    REPORT_GENERATOR = "report_generator"
    RISK_ASSESSOR = "risk_assessor"
    COMPLIANCE_CHECKER = "compliance_checker"
    MARKET_RESEARCHER = "market_researcher"
    CUSTOM = "custom"

class AgentStatus(enum.Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TaskStatus(enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class Agent(db.Model):
    __tablename__ = 'agents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    agent_type = db.Column(db.Enum(AgentType), nullable=False)

    # Agent configuration
    configuration = db.Column(db.JSON, nullable=False)
    capabilities = db.Column(db.JSON, nullable=True)
    model_config = db.Column(db.JSON, nullable=True)

    # Status and metadata
    status = db.Column(db.Enum(AgentStatus), default=AgentStatus.INACTIVE, nullable=False)
    version = db.Column(db.String(20), default='1.0.0', nullable=False)

    # Performance metrics
    total_tasks = db.Column(db.Integer, default=0, nullable=False)
    successful_tasks = db.Column(db.Integer, default=0, nullable=False)
    avg_execution_time = db.Column(db.Float, nullable=True)
    last_used_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tasks = db.relationship('AgentTask', backref='agent', lazy=True)
    workflows = db.relationship('Workflow', backref='primary_agent', lazy=True)

    def get_success_rate(self):
        """Calculate agent success rate"""
        if self.total_tasks == 0:
            return 0
        return (self.successful_tasks / self.total_tasks) * 100

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'agent_type': self.agent_type.value,
            'configuration': self.configuration,
            'capabilities': self.capabilities,
            'status': self.status.value,
            'version': self.version,
            'total_tasks': self.total_tasks,
            'successful_tasks': self.successful_tasks,
            'success_rate': self.get_success_rate(),
            'avg_execution_time': self.avg_execution_time,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AgentTask(db.Model):
    __tablename__ = 'agent_tasks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = db.Column(db.String(36), db.ForeignKey('agents.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False, index=True)
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=True)

    # Task details
    task_name = db.Column(db.String(200), nullable=False)
    task_description = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(100), nullable=False)

    # Input and output
    input_data = db.Column(db.JSON, nullable=True)
    output_data = db.Column(db.JSON, nullable=True)
    parameters = db.Column(db.JSON, nullable=True)

    # Status and execution
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = db.Column(db.Integer, default=5, nullable=False)  # 1-10 scale
    progress_percentage = db.Column(db.Integer, default=0, nullable=False)

    # Timing
    estimated_duration = db.Column(db.Integer, nullable=True)  # seconds
    actual_duration = db.Column(db.Integer, nullable=True)  # seconds
    timeout_duration = db.Column(db.Integer, nullable=True)  # seconds

    # Error handling
    error_message = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    max_retries = db.Column(db.Integer, default=3, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    executions = db.relationship('TaskExecution', backref='task', lazy=True)

    def is_expired(self):
        """Check if task has expired"""
        if self.timeout_duration and self.started_at:
            timeout_time = self.started_at + timedelta(seconds=self.timeout_duration)
            return datetime.utcnow() > timeout_time
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'user_id': self.user_id,
            'workflow_id': self.workflow_id,
            'task_name': self.task_name,
            'task_description': self.task_description,
            'task_type': self.task_type,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'parameters': self.parameters,
            'status': self.status.value,
            'priority': self.priority,
            'progress_percentage': self.progress_percentage,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Workflow(db.Model):
    __tablename__ = 'workflows'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    primary_agent_id = db.Column(db.String(36), db.ForeignKey('agents.id'), nullable=False)

    # Workflow details
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    workflow_definition = db.Column(db.JSON, nullable=False)

    # Configuration
    trigger_config = db.Column(db.JSON, nullable=True)
    schedule_config = db.Column(db.JSON, nullable=True)
    notification_config = db.Column(db.JSON, nullable=True)

    # Status and execution
    status = db.Column(db.Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, nullable=False)
    current_step = db.Column(db.Integer, default=0, nullable=False)
    total_steps = db.Column(db.Integer, default=0, nullable=False)

    # Statistics
    execution_count = db.Column(db.Integer, default=0, nullable=False)
    success_count = db.Column(db.Integer, default=0, nullable=False)
    last_execution_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tasks = db.relationship('AgentTask', backref='workflow', lazy=True)
    executions = db.relationship('WorkflowExecution', backref='workflow', lazy=True)

    def get_success_rate(self):
        """Calculate workflow success rate"""
        if self.execution_count == 0:
            return 0
        return (self.success_count / self.execution_count) * 100

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'primary_agent_id': self.primary_agent_id,
            'name': self.name,
            'description': self.description,
            'workflow_definition': self.workflow_definition,
            'trigger_config': self.trigger_config,
            'schedule_config': self.schedule_config,
            'status': self.status.value,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'success_rate': self.get_success_rate(),
            'last_execution_at': self.last_execution_at.isoformat() if self.last_execution_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WorkflowExecution(db.Model):
    __tablename__ = 'workflow_executions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('workflows.id'), nullable=False)

    # Execution details
    execution_context = db.Column(db.JSON, nullable=True)
    execution_results = db.Column(db.JSON, nullable=True)

    # Status and progress
    status = db.Column(db.Enum(WorkflowStatus), default=WorkflowStatus.RUNNING, nullable=False)
    current_step = db.Column(db.Integer, default=0, nullable=False)
    completed_steps = db.Column(db.Integer, default=0, nullable=False)

    # Error handling
    error_message = db.Column(db.Text, nullable=True)
    failed_step = db.Column(db.Integer, nullable=True)

    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'execution_context': self.execution_context,
            'execution_results': self.execution_results,
            'status': self.status.value,
            'current_step': self.current_step,
            'completed_steps': self.completed_steps,
            'error_message': self.error_message,
            'failed_step': self.failed_step,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class TaskExecution(db.Model):
    __tablename__ = 'task_executions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey('agent_tasks.id'), nullable=False)

    # Execution details
    execution_log = db.Column(db.Text, nullable=True)
    resource_usage = db.Column(db.JSON, nullable=True)
    performance_metrics = db.Column(db.JSON, nullable=True)

    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'execution_log': self.execution_log,
            'resource_usage': self.resource_usage,
            'performance_metrics': self.performance_metrics,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AgentTemplate(db.Model):
    __tablename__ = 'agent_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    agent_type = db.Column(db.Enum(AgentType), nullable=False)

    # Template configuration
    template_config = db.Column(db.JSON, nullable=False)
    default_capabilities = db.Column(db.JSON, nullable=True)
    required_parameters = db.Column(db.JSON, nullable=True)

    # Template metadata
    category = db.Column(db.String(100), nullable=True)
    difficulty_level = db.Column(db.String(20), nullable=True)
    estimated_setup_time = db.Column(db.Integer, nullable=True)

    # Usage statistics
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    avg_rating = db.Column(db.Float, nullable=True)

    # Template management
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.String(36), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'agent_type': self.agent_type.value,
            'template_config': self.template_config,
            'default_capabilities': self.default_capabilities,
            'required_parameters': self.required_parameters,
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'estimated_setup_time': self.estimated_setup_time,
            'usage_count': self.usage_count,
            'avg_rating': self.avg_rating,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }