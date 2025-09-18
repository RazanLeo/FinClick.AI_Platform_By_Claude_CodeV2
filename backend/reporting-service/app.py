from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/finclick_reports')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')

# Report configuration
app.config['REPORTS_STORAGE_PATH'] = os.getenv('REPORTS_STORAGE_PATH', '/tmp/reports')
app.config['AWS_S3_REPORTS_BUCKET'] = os.getenv('AWS_S3_REPORTS_BUCKET')

# Service URLs
app.config['ANALYSIS_SERVICE_URL'] = os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:5004')
app.config['USER_SERVICE_URL'] = os.getenv('USER_SERVICE_URL', 'http://localhost:5002')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import models and routes
from models import *
from routes import *

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'reporting-service'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5006, debug=True)