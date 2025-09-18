from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db, limiter, celery
from models import (
    Agent, AgentTask, Workflow, WorkflowExecution, TaskExecution,
    AgentTemplate, AgentType, AgentStatus, TaskStatus, WorkflowStatus
)
from services import (
    AgentService, TaskService, WorkflowService, TemplateService,
    OrchestrationService
)
import logging

logger = logging.getLogger(__name__)

# Agent Management Routes
@app.route('/api/agents', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_agent():
    """Create a new AI agent"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        required_fields = ['name', 'agent_type', 'configuration']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        agent = AgentService.create_agent(
            user_id=current_user_id,
            name=data['name'],
            agent_type=AgentType(data['agent_type']),
            description=data.get('description'),
            configuration=data['configuration'],
            capabilities=data.get('capabilities', [])
        )

        db.session.commit()

        return jsonify({
            'message': 'Agent created successfully',
            'agent': agent.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Create agent error: {str(e)}")
        return jsonify({'error': 'Failed to create agent'}), 500

@app.route('/api/agents', methods=['GET'])
@jwt_required()
def get_agents():
    """Get user's agents"""
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        agent_type = request.args.get('type')
        status = request.args.get('status')

        query = Agent.query.filter_by(user_id=current_user_id)

        if agent_type:
            try:
                type_enum = AgentType(agent_type)
                query = query.filter_by(agent_type=type_enum)
            except ValueError:
                pass

        if status:
            try:
                status_enum = AgentStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                pass

        agents = query.order_by(Agent.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'agents': [agent.to_dict() for agent in agents.items],
            'total': agents.total,
            'pages': agents.pages,
            'current_page': agents.page,
            'has_next': agents.has_next,
            'has_prev': agents.has_prev
        }), 200

    except Exception as e:
        logger.error(f"Get agents error: {str(e)}")
        return jsonify({'error': 'Failed to get agents'}), 500

@app.route('/api/agents/<agent_id>', methods=['GET'])
@jwt_required()
def get_agent(agent_id):
    """Get specific agent details"""
    try:
        current_user_id = get_jwt_identity()

        agent = Agent.query.filter_by(
            id=agent_id,
            user_id=current_user_id
        ).first()

        if not agent:
            return jsonify({'error': 'Agent not found'}), 404

        return jsonify({'agent': agent.to_dict()}), 200

    except Exception as e:
        logger.error(f"Get agent error: {str(e)}")
        return jsonify({'error': 'Failed to get agent'}), 500

@app.route('/api/agents/<agent_id>/activate', methods=['POST'])
@jwt_required()
def activate_agent(agent_id):
    """Activate an agent"""
    try:
        current_user_id = get_jwt_identity()

        agent = Agent.query.filter_by(
            id=agent_id,
            user_id=current_user_id
        ).first()

        if not agent:
            return jsonify({'error': 'Agent not found'}), 404

        AgentService.activate_agent(agent_id)
        db.session.commit()

        return jsonify({'message': 'Agent activated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Activate agent error: {str(e)}")
        return jsonify({'error': 'Failed to activate agent'}), 500

# Task Management Routes
@app.route('/api/tasks', methods=['POST'])
@jwt_required()
@limiter.limit("50 per hour")
def create_task():
    """Create a new task for an agent"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        required_fields = ['agent_id', 'task_name', 'task_type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        task = TaskService.create_task(
            agent_id=data['agent_id'],
            user_id=current_user_id,
            task_name=data['task_name'],
            task_type=data['task_type'],
            task_description=data.get('task_description'),
            input_data=data.get('input_data'),
            parameters=data.get('parameters', {}),
            priority=data.get('priority', 5)
        )

        # Execute task asynchronously
        task_execution_id = TaskService.execute_task_async(task.id)

        db.session.commit()

        return jsonify({
            'message': 'Task created and queued for execution',
            'task': task.to_dict(),
            'execution_id': task_execution_id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Create task error: {str(e)}")
        return jsonify({'error': 'Failed to create task'}), 500

@app.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get user's tasks"""
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        agent_id = request.args.get('agent_id')

        query = AgentTask.query.filter_by(user_id=current_user_id)

        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                pass

        if agent_id:
            query = query.filter_by(agent_id=agent_id)

        tasks = query.order_by(AgentTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'tasks': [task.to_dict() for task in tasks.items],
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': tasks.page,
            'has_next': tasks.has_next,
            'has_prev': tasks.has_prev
        }), 200

    except Exception as e:
        logger.error(f"Get tasks error: {str(e)}")
        return jsonify({'error': 'Failed to get tasks'}), 500

@app.route('/api/tasks/<task_id>/status', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Get task status and progress"""
    try:
        current_user_id = get_jwt_identity()

        task = AgentTask.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        return jsonify({
            'task_id': task.id,
            'status': task.status.value,
            'progress_percentage': task.progress_percentage,
            'error_message': task.error_message
        }), 200

    except Exception as e:
        logger.error(f"Get task status error: {str(e)}")
        return jsonify({'error': 'Failed to get task status'}), 500

# Workflow Management Routes
@app.route('/api/workflows', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def create_workflow():
    """Create a new workflow"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        required_fields = ['name', 'primary_agent_id', 'workflow_definition']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        workflow = WorkflowService.create_workflow(
            user_id=current_user_id,
            name=data['name'],
            primary_agent_id=data['primary_agent_id'],
            description=data.get('description'),
            workflow_definition=data['workflow_definition'],
            trigger_config=data.get('trigger_config'),
            schedule_config=data.get('schedule_config')
        )

        db.session.commit()

        return jsonify({
            'message': 'Workflow created successfully',
            'workflow': workflow.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Create workflow error: {str(e)}")
        return jsonify({'error': 'Failed to create workflow'}), 500

@app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
@jwt_required()
def execute_workflow(workflow_id):
    """Execute a workflow"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        workflow = Workflow.query.filter_by(
            id=workflow_id,
            user_id=current_user_id
        ).first()

        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404

        execution = WorkflowService.execute_workflow(
            workflow_id=workflow_id,
            execution_context=data.get('context', {})
        )

        db.session.commit()

        return jsonify({
            'message': 'Workflow execution started',
            'execution': execution.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Execute workflow error: {str(e)}")
        return jsonify({'error': 'Failed to execute workflow'}), 500

# Agent Templates Routes
@app.route('/api/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """Get available agent templates"""
    try:
        agent_type = request.args.get('type')
        category = request.args.get('category')

        templates = TemplateService.get_templates(
            agent_type=agent_type,
            category=category
        )

        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200

    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        return jsonify({'error': 'Failed to get templates'}), 500

@app.route('/api/templates/<template_id>/use', methods=['POST'])
@jwt_required()
def use_template(template_id):
    """Create agent from template"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        agent = TemplateService.create_agent_from_template(
            template_id=template_id,
            user_id=current_user_id,
            name=data.get('name'),
            customizations=data.get('customizations', {})
        )

        db.session.commit()

        return jsonify({
            'message': 'Agent created from template',
            'agent': agent.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Use template error: {str(e)}")
        return jsonify({'error': 'Failed to create agent from template'}), 500

# Orchestration Routes
@app.route('/api/orchestration/status', methods=['GET'])
@jwt_required()
def get_orchestration_status():
    """Get orchestration system status"""
    try:
        current_user_id = get_jwt_identity()

        status = OrchestrationService.get_user_orchestration_status(current_user_id)

        return jsonify({'status': status}), 200

    except Exception as e:
        logger.error(f"Get orchestration status error: {str(e)}")
        return jsonify({'error': 'Failed to get orchestration status'}), 500

@app.route('/api/agents/batch-execute', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def batch_execute():
    """Execute multiple tasks across agents"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'tasks' not in data:
            return jsonify({'error': 'Tasks list required'}), 400

        execution_results = OrchestrationService.batch_execute_tasks(
            user_id=current_user_id,
            tasks=data['tasks']
        )

        return jsonify({
            'message': 'Batch execution initiated',
            'results': execution_results
        }), 200

    except Exception as e:
        logger.error(f"Batch execute error: {str(e)}")
        return jsonify({'error': 'Failed to execute batch tasks'}), 500

# Communication Routes
@app.route('/api/agents/<agent_id>/communicate', methods=['POST'])
@jwt_required()
def agent_communicate(agent_id):
    """Send message to agent for communication"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'Message required'}), 400

        response = OrchestrationService.communicate_with_agent(
            agent_id=agent_id,
            user_id=current_user_id,
            message=data['message'],
            context=data.get('context', {})
        )

        return jsonify({
            'response': response
        }), 200

    except Exception as e:
        logger.error(f"Agent communicate error: {str(e)}")
        return jsonify({'error': 'Failed to communicate with agent'}), 500