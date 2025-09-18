from app import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import enum
import secrets
import pyotp

class UserRole(enum.Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    STANDARD = "standard"
    TRIAL = "trial"

class AuthProvider(enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.TRIAL, nullable=False)
    permissions = db.Column(db.JSON, default=list)

    # Authentication providers
    auth_provider = db.Column(db.Enum(AuthProvider), default=AuthProvider.LOCAL)
    provider_id = db.Column(db.String(255), nullable=True)  # OAuth provider user ID

    # Security settings
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    backup_codes = db.Column(db.JSON, default=list)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)

    # Account lockout
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Privacy and preferences
    language = db.Column(db.String(5), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # OAuth fields
    google_id = db.Column(db.String(100), nullable=True)
    facebook_id = db.Column(db.String(100), nullable=True)

    # Relationships
    login_sessions = db.relationship('LoginSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    email_verification_tokens = db.relationship('EmailVerificationToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()

    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role

    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        role_permissions = {
            UserRole.ADMIN: ['read', 'write', 'delete', 'admin', 'manage_users', 'financial_analysis'],
            UserRole.PREMIUM: ['read', 'write', 'financial_analysis', 'advanced_reports', 'ai_agents'],
            UserRole.STANDARD: ['read', 'write', 'basic_analysis', 'basic_reports'],
            UserRole.TRIAL: ['read', 'basic_analysis']
        }
        return permission in role_permissions.get(self.role, []) or permission in self.permissions

    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False

    def lock_account(self, minutes=30):
        """Lock account for specified minutes"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.failed_login_attempts += 1

    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0

    def setup_mfa(self):
        """Setup MFA and return secret key"""
        self.mfa_secret = pyotp.random_base32()
        self.backup_codes = [secrets.token_hex(4) for _ in range(10)]
        return self.mfa_secret

    def verify_mfa_token(self, token):
        """Verify MFA token"""
        if not self.mfa_enabled or not self.mfa_secret:
            return False

        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token, valid_window=1)

    def verify_backup_code(self, code):
        """Verify and consume backup code"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            return True
        return False

    def get_mfa_qr_code_url(self, app_name="FinClick.AI"):
        """Get QR code URL for MFA setup"""
        if not self.mfa_secret:
            return None

        totp = pyotp.TOTP(self.mfa_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name=app_name
        )

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'role': self.role.value,
            'permissions': self.permissions,
            'auth_provider': self.auth_provider.value,
            'mfa_enabled': self.mfa_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'language': self.language,
            'timezone': self.timezone
        }

        if include_sensitive:
            data.update({
                'backup_codes': self.backup_codes,
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None
            })

        return data

class LoginSession(db.Model):
    __tablename__ = 'login_sessions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    refresh_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at

    def extend_session(self, hours=24):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()

    def revoke(self):
        """Revoke the session"""
        self.is_active = False

    device_info = db.Column(db.JSON, default=dict)

class OAuthState(db.Model):
    __tablename__ = 'oauth_states'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state = db.Column(db.String(255), unique=True, nullable=False)
    provider = db.Column(db.Enum(AuthProvider), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<OAuthState {self.provider.value}>'

    def is_expired(self):
        """Check if state is expired"""
        return datetime.utcnow() > self.expires_at

    def mark_as_used(self):
        """Mark state as used"""
        self.used = True

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    used_at = db.Column(db.DateTime, nullable=True)
    is_used = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<PasswordResetToken {self.id}>'

    def is_expired(self):
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()

    @staticmethod
    def create_reset_token(user_id, hours=24):
        """Create a new password reset token"""
        token = str(uuid.uuid4())
        reset = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=hours)
        )
        return reset

class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)  # In case user changes email

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<EmailVerificationToken {self.id}>'

    def is_expired(self):
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at

    def mark_as_verified(self):
        """Mark token as verified"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()

class BlacklistedToken(db.Model):
    __tablename__ = 'blacklisted_tokens'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    jti = db.Column(db.String(36), unique=True, nullable=False)  # JWT ID
    token_type = db.Column(db.String(10), nullable=False)  # access or refresh
    user_id = db.Column(db.String(36), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<BlacklistedToken {self.jti}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # login, logout, password_change, etc.
    event_description = db.Column(db.Text, nullable=True)

    # Request details
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    request_url = db.Column(db.Text, nullable=True)

    # Status
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)

    # Metadata
    metadata = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.event_type}>'

    @staticmethod
    def log_action(user_id, event_type, event_description=None, success=True,
                  error_message=None, metadata=None, ip_address=None,
                  user_agent=None, request_method=None, request_url=None):
        """Log user action for audit trail"""
        log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            event_description=event_description,
            success=success,
            error_message=error_message,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_url=request_url
        )
        db.session.add(log)
        return log

class ApiKey(db.Model):
    __tablename__ = 'api_keys'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    key_prefix = db.Column(db.String(10), nullable=False)  # First 8 chars for display

    # Permissions and limits
    permissions = db.Column(db.JSON, default=list)
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour

    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<ApiKey {self.name}>'

    def is_expired(self):
        """Check if API key is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def revoke(self):
        """Revoke the API key"""
        self.is_active = False