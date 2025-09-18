from app import db
from datetime import datetime
import uuid
import enum

class NotificationType(enum.Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

class NotificationPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    status = db.Column(db.Enum(NotificationStatus), default=NotificationStatus.PENDING)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.NORMAL)

    # Content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)

    # Delivery details
    recipient = db.Column(db.String(200), nullable=False)  # email, phone, device_token
    delivery_attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=3)

    # Timestamps
    scheduled_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value,
            'status': self.status.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'recipient': self.recipient,
            'delivery_attempts': self.delivery_attempts,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat()
        }

class NotificationTemplate(db.Model):
    __tablename__ = 'notification_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)

    # Template content
    subject_template = db.Column(db.String(200), nullable=True)  # For email
    title_template = db.Column(db.String(200), nullable=False)
    message_template = db.Column(db.Text, nullable=False)

    # Template metadata
    variables = db.Column(db.JSON, nullable=True)  # Available template variables
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'subject_template': self.subject_template,
            'title_template': self.title_template,
            'message_template': self.message_template,
            'variables': self.variables,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class UserNotificationSettings(db.Model):
    __tablename__ = 'user_notification_settings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, unique=True, index=True)

    # Notification preferences
    email_enabled = db.Column(db.Boolean, default=True)
    push_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    in_app_enabled = db.Column(db.Boolean, default=True)

    # Specific notification types
    analysis_complete = db.Column(db.Boolean, default=True)
    report_ready = db.Column(db.Boolean, default=True)
    subscription_changes = db.Column(db.Boolean, default=True)
    security_alerts = db.Column(db.Boolean, default=True)
    marketing_updates = db.Column(db.Boolean, default=False)

    # Quiet hours
    quiet_hours_enabled = db.Column(db.Boolean, default=False)
    quiet_hours_start = db.Column(db.Time, nullable=True)
    quiet_hours_end = db.Column(db.Time, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email_enabled': self.email_enabled,
            'push_enabled': self.push_enabled,
            'sms_enabled': self.sms_enabled,
            'in_app_enabled': self.in_app_enabled,
            'analysis_complete': self.analysis_complete,
            'report_ready': self.report_ready,
            'subscription_changes': self.subscription_changes,
            'security_alerts': self.security_alerts,
            'marketing_updates': self.marketing_updates,
            'quiet_hours_enabled': self.quiet_hours_enabled,
            'quiet_hours_start': self.quiet_hours_start.isoformat() if self.quiet_hours_start else None,
            'quiet_hours_end': self.quiet_hours_end.isoformat() if self.quiet_hours_end else None,
            'updated_at': self.updated_at.isoformat()
        }