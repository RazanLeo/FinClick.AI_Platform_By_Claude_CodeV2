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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/finclick_notifications')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')

# Email configuration
app.config['SMTP_SERVER'] = os.getenv('SMTP_SERVER', 'localhost')
app.config['SMTP_PORT'] = int(os.getenv('SMTP_PORT', 587))
app.config['SMTP_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD')
app.config['FROM_EMAIL'] = os.getenv('FROM_EMAIL', 'noreply@finclick.ai')

# Push notification configuration
app.config['FCM_SERVER_KEY'] = os.getenv('FCM_SERVER_KEY')
app.config['APNS_CERTIFICATE_PATH'] = os.getenv('APNS_CERTIFICATE_PATH')

# Service URLs
app.config['USER_SERVICE_URL'] = os.getenv('USER_SERVICE_URL', 'http://localhost:5002')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["1000 per day", "100 per hour"])

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
    return jsonify({'status': 'healthy', 'service': 'notification-service'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5008, debug=True)