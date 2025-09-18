from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from datetime import timedelta
import redis
from celery import Celery

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/finclick_agents')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Redis and Celery configuration
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# AI Configuration
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')
app.config['HUGGINGFACE_API_KEY'] = os.getenv('HUGGINGFACE_API_KEY')
app.config['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

# Agent Configuration
app.config['MAX_AGENTS_PER_USER'] = int(os.getenv('MAX_AGENTS_PER_USER', 10))
app.config['MAX_WORKFLOW_STEPS'] = int(os.getenv('MAX_WORKFLOW_STEPS', 50))
app.config['AGENT_TIMEOUT_MINUTES'] = int(os.getenv('AGENT_TIMEOUT_MINUTES', 30))

# Service URLs
app.config['ANALYSIS_SERVICE_URL'] = os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:5004')
app.config['FILE_SERVICE_URL'] = os.getenv('FILE_SERVICE_URL', 'http://localhost:5003')
app.config['USER_SERVICE_URL'] = os.getenv('USER_SERVICE_URL', 'http://localhost:5002')
app.config['NOTIFICATION_SERVICE_URL'] = os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5008')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

# Initialize Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# Initialize Redis
try:
    redis_client = redis.from_url(app.config['REDIS_URL'])
    redis_client.ping()
    app.redis = redis_client
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Redis connection failed: {str(e)}")
    app.redis = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# JWT token verification
@jwt.token_verification_failed_loader
def token_verification_failed_callback():
    return jsonify({'error': 'Invalid token'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token format'}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

# Import models and routes after app initialization
from models import *
from routes import *

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')

        # Check Redis connection
        redis_status = "connected" if app.redis and app.redis.ping() else "disconnected"

        # Check Celery workers
        celery_inspect = celery.control.inspect()
        active_workers = celery_inspect.active()
        worker_count = len(active_workers) if active_workers else 0

        return jsonify({
            'status': 'healthy',
            'service': 'ai-agents-service',
            'database': 'connected',
            'redis': redis_status,
            'celery_workers': worker_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'ai-agents-service',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5005, debug=True)