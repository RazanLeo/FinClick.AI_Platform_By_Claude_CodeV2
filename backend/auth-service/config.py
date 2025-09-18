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
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"

    # OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')
    APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID')
    APPLE_CLIENT_SECRET = os.getenv('APPLE_CLIENT_SECRET')

    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@finclick.ai')

    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    # Security Settings
    BCRYPT_LOG_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SYMBOLS = True

    # Account Lockout Settings
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    # MFA Settings
    MFA_ISSUER_NAME = "FinClick.AI"
    BACKUP_CODES_COUNT = 10

    # Session Settings
    SESSION_TIMEOUT_HOURS = 24
    REMEMBER_ME_DURATION_DAYS = 30

    # API Settings
    API_RATE_LIMIT = 1000  # requests per hour
    API_KEY_EXPIRY_DAYS = 365

    # Internationalization
    LANGUAGES = ['en', 'ar']
    DEFAULT_LANGUAGE = 'en'

    # Frontend URLs
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    PASSWORD_RESET_URL = f"{FRONTEND_URL}/reset-password"
    EMAIL_VERIFICATION_URL = f"{FRONTEND_URL}/verify-email"

    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/finclick_auth_dev'
    )

    # More lenient settings for development
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    BCRYPT_LOG_ROUNDS = 4  # Faster for development

    # Development OAuth settings
    GOOGLE_REDIRECT_URI = 'http://localhost:5001/auth/google/callback'
    FACEBOOK_REDIRECT_URI = 'http://localhost:5001/auth/facebook/callback'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # Stricter security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Production OAuth settings
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    FACEBOOK_REDIRECT_URI = os.getenv('FACEBOOK_REDIRECT_URI')

    # SSL Settings
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Fast settings for testing
    BCRYPT_LOG_ROUNDS = 4
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

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