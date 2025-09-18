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

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/finclick_analysis')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Redis configuration for caching
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.getenv('CACHE_TIMEOUT', 300))

# Financial Engine Configuration
app.config['FINANCIAL_ENGINE_URL'] = os.getenv('FINANCIAL_ENGINE_URL', 'http://localhost:8000')
app.config['FINANCIAL_ENGINE_API_KEY'] = os.getenv('FINANCIAL_ENGINE_API_KEY')

# AI/ML Configuration
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['HUGGINGFACE_API_KEY'] = os.getenv('HUGGINGFACE_API_KEY')

# Service URLs
app.config['FILE_SERVICE_URL'] = os.getenv('FILE_SERVICE_URL', 'http://localhost:5003')
app.config['USER_SERVICE_URL'] = os.getenv('USER_SERVICE_URL', 'http://localhost:5002')
app.config['REPORTING_SERVICE_URL'] = os.getenv('REPORTING_SERVICE_URL', 'http://localhost:5006')
app.config['NOTIFICATION_SERVICE_URL'] = os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5008')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["500 per day", "50 per hour"]
)

# Initialize Redis for caching
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

        return jsonify({
            'status': 'healthy',
            'service': 'analysis-service',
            'database': 'connected',
            'redis': redis_status
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'analysis-service',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5004, debug=True)