import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads/avatars'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # External Services
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
    SUBSCRIPTION_SERVICE_URL = os.getenv('SUBSCRIPTION_SERVICE_URL', 'http://localhost:5007')
    NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5008')

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_DEFAULT = "1000 per day, 100 per hour"

    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@finclick.ai')

    # Cloud Storage (AWS S3)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'finclick-user-assets')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

    # Cache Configuration
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300

    # Internationalization
    LANGUAGES = ['en', 'ar']
    DEFAULT_LANGUAGE = 'en'
    DEFAULT_TIMEZONE = 'UTC'

    # Subscription Limits (Default Trial)
    DEFAULT_TRIAL_DURATION_DAYS = 14
    DEFAULT_FILE_LIMIT = 10
    DEFAULT_ANALYSIS_LIMIT = 50
    DEFAULT_STORAGE_LIMIT_GB = 1.0
    DEFAULT_API_CALLS_LIMIT = 1000

    # Analytics
    ANALYTICS_RETENTION_DAYS = 90
    USAGE_AGGREGATION_INTERVAL_HOURS = 24

    # Security
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES = 30

    # Profile Validation
    MAX_BIO_LENGTH = 1000
    MAX_COMPANY_NAME_LENGTH = 200
    MAX_JOB_TITLE_LENGTH = 100

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/finclick_user_dev'
    )

    # More lenient settings for development
    CACHE_DEFAULT_TIMEOUT = 60

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # Production specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Longer cache timeouts in production
    CACHE_DEFAULT_TIMEOUT = 600

    # SSL Settings
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable cache during testing
    CACHE_TYPE = "null"

    # Fast settings for testing
    CACHE_DEFAULT_TIMEOUT = 1

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])