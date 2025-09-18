from app import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import enum

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"

class UsageType(enum.Enum):
    FILE_UPLOAD = "file_upload"
    ANALYSIS_REQUEST = "analysis_request"
    REPORT_GENERATION = "report_generation"
    API_CALL = "api_call"
    STORAGE_USAGE = "storage_usage"

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # From auth service
    company_name = db.Column(db.String(200), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    timezone = db.Column(db.String(50), default='UTC', nullable=False)
    language = db.Column(db.String(10), default='en', nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)

    # Preferences
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    sms_notifications = db.Column(db.Boolean, default=False, nullable=False)
    marketing_emails = db.Column(db.Boolean, default=True, nullable=False)
    weekly_reports = db.Column(db.Boolean, default=True, nullable=False)

    # Onboarding
    onboarding_completed = db.Column(db.Boolean, default=False, nullable=False)
    onboarding_step = db.Column(db.Integer, default=1, nullable=False)
    tutorial_completed = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    usage_records = db.relationship('UsageRecord', backref='user_profile', lazy=True)
    subscription = db.relationship('UserSubscription', uselist=False, backref='user_profile', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'department': self.department,
            'industry': self.industry,
            'company_size': self.company_size,
            'country': self.country,
            'timezone': self.timezone,
            'language': self.language,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'website': self.website,
            'linkedin_url': self.linkedin_url,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'marketing_emails': self.marketing_emails,
            'weekly_reports': self.weekly_reports,
            'onboarding_completed': self.onboarding_completed,
            'onboarding_step': self.onboarding_step,
            'tutorial_completed': self.tutorial_completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserSubscription(db.Model):
    __tablename__ = 'user_subscriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_profile_id = db.Column(db.String(36), db.ForeignKey('user_profiles.id'), nullable=False)
    plan_id = db.Column(db.String(36), nullable=False)  # From subscription service
    plan_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL, nullable=False)

    # Limits
    monthly_file_limit = db.Column(db.Integer, default=10, nullable=False)
    monthly_analysis_limit = db.Column(db.Integer, default=50, nullable=False)
    storage_limit_gb = db.Column(db.Float, default=1.0, nullable=False)
    api_calls_limit = db.Column(db.Integer, default=1000, nullable=False)

    # Current usage
    files_used = db.Column(db.Integer, default=0, nullable=False)
    analyses_used = db.Column(db.Integer, default=0, nullable=False)
    storage_used_gb = db.Column(db.Float, default=0.0, nullable=False)
    api_calls_used = db.Column(db.Integer, default=0, nullable=False)

    # Dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    next_billing_date = db.Column(db.DateTime, nullable=True)
    trial_end_date = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def is_trial_expired(self):
        """Check if trial period is expired"""
        if self.trial_end_date:
            return datetime.utcnow() > self.trial_end_date
        return False

    def is_subscription_expired(self):
        """Check if subscription is expired"""
        if self.end_date:
            return datetime.utcnow() > self.end_date
        return False

    def get_usage_percentage(self, usage_type):
        """Get usage percentage for specific type"""
        if usage_type == 'files':
            return (self.files_used / self.monthly_file_limit) * 100 if self.monthly_file_limit > 0 else 0
        elif usage_type == 'analyses':
            return (self.analyses_used / self.monthly_analysis_limit) * 100 if self.monthly_analysis_limit > 0 else 0
        elif usage_type == 'storage':
            return (self.storage_used_gb / self.storage_limit_gb) * 100 if self.storage_limit_gb > 0 else 0
        elif usage_type == 'api_calls':
            return (self.api_calls_used / self.api_calls_limit) * 100 if self.api_calls_limit > 0 else 0
        return 0

    def can_use_feature(self, feature_type, amount=1):
        """Check if user can use a specific feature"""
        if feature_type == 'file_upload':
            return self.files_used + amount <= self.monthly_file_limit
        elif feature_type == 'analysis':
            return self.analyses_used + amount <= self.monthly_analysis_limit
        elif feature_type == 'storage':
            return self.storage_used_gb + amount <= self.storage_limit_gb
        elif feature_type == 'api_call':
            return self.api_calls_used + amount <= self.api_calls_limit
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'plan_name': self.plan_name,
            'status': self.status.value,
            'monthly_file_limit': self.monthly_file_limit,
            'monthly_analysis_limit': self.monthly_analysis_limit,
            'storage_limit_gb': self.storage_limit_gb,
            'api_calls_limit': self.api_calls_limit,
            'files_used': self.files_used,
            'analyses_used': self.analyses_used,
            'storage_used_gb': self.storage_used_gb,
            'api_calls_used': self.api_calls_used,
            'usage_percentages': {
                'files': self.get_usage_percentage('files'),
                'analyses': self.get_usage_percentage('analyses'),
                'storage': self.get_usage_percentage('storage'),
                'api_calls': self.get_usage_percentage('api_calls')
            },
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UsageRecord(db.Model):
    __tablename__ = 'usage_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_profile_id = db.Column(db.String(36), db.ForeignKey('user_profiles.id'), nullable=False)
    usage_type = db.Column(db.Enum(UsageType), nullable=False)
    amount = db.Column(db.Float, default=1.0, nullable=False)
    resource_id = db.Column(db.String(36), nullable=True)  # ID of file, analysis, etc.
    resource_name = db.Column(db.String(200), nullable=True)
    metadata = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'usage_type': self.usage_type.value,
            'amount': self.amount,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }

class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_profile_id = db.Column(db.String(36), db.ForeignKey('user_profiles.id'), nullable=False)
    setting_key = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint('user_profile_id', 'setting_key'),)

class UserActivity(db.Model):
    __tablename__ = 'user_activities'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_profile_id = db.Column(db.String(36), db.ForeignKey('user_profiles.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    metadata = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'description': self.description,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_profile_id = db.Column(db.String(36), db.ForeignKey('user_profiles.id'), nullable=False)

    # Dashboard preferences
    dashboard_layout = db.Column(db.JSON, nullable=True)
    default_currency = db.Column(db.String(3), default='USD', nullable=False)
    date_format = db.Column(db.String(20), default='YYYY-MM-DD', nullable=False)
    number_format = db.Column(db.String(20), default='en-US', nullable=False)

    # Analysis preferences
    default_analysis_type = db.Column(db.String(50), nullable=True)
    auto_save_analyses = db.Column(db.Boolean, default=True, nullable=False)
    analysis_templates = db.Column(db.JSON, nullable=True)

    # Notification preferences
    notification_frequency = db.Column(db.String(20), default='immediate', nullable=False)
    notification_channels = db.Column(db.JSON, nullable=True)
    quiet_hours_start = db.Column(db.Time, nullable=True)
    quiet_hours_end = db.Column(db.Time, nullable=True)

    # Export preferences
    default_export_format = db.Column(db.String(10), default='pdf', nullable=False)
    include_charts_in_export = db.Column(db.Boolean, default=True, nullable=False)
    watermark_exports = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'dashboard_layout': self.dashboard_layout,
            'default_currency': self.default_currency,
            'date_format': self.date_format,
            'number_format': self.number_format,
            'default_analysis_type': self.default_analysis_type,
            'auto_save_analyses': self.auto_save_analyses,
            'analysis_templates': self.analysis_templates,
            'notification_frequency': self.notification_frequency,
            'notification_channels': self.notification_channels,
            'quiet_hours_start': self.quiet_hours_start.isoformat() if self.quiet_hours_start else None,
            'quiet_hours_end': self.quiet_hours_end.isoformat() if self.quiet_hours_end else None,
            'default_export_format': self.default_export_format,
            'include_charts_in_export': self.include_charts_in_export,
            'watermark_exports': self.watermark_exports,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }