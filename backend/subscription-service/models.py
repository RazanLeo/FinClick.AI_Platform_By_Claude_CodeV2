from app import db
from datetime import datetime, timedelta
import uuid
import enum

class PlanType(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    plan_type = db.Column(db.Enum(PlanType), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Pricing
    price_monthly = db.Column(db.Numeric(10, 2), nullable=False)
    price_yearly = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), default='USD')

    # Limits
    file_upload_limit = db.Column(db.Integer, default=10)
    analysis_limit = db.Column(db.Integer, default=50)
    storage_limit_gb = db.Column(db.Float, default=1.0)
    api_calls_limit = db.Column(db.Integer, default=1000)

    # Features
    features = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'plan_type': self.plan_type.value,
            'description': self.description,
            'price_monthly': float(self.price_monthly),
            'price_yearly': float(self.price_yearly) if self.price_yearly else None,
            'currency': self.currency,
            'file_upload_limit': self.file_upload_limit,
            'analysis_limit': self.analysis_limit,
            'storage_limit_gb': self.storage_limit_gb,
            'api_calls_limit': self.api_calls_limit,
            'features': self.features,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    plan_id = db.Column(db.String(36), db.ForeignKey('subscription_plans.id'), nullable=False)

    # Subscription details
    status = db.Column(db.Enum(SubscriptionStatus), nullable=False)
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, yearly

    # Dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    trial_end_date = db.Column(db.DateTime, nullable=True)
    next_billing_date = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    # Payment integration
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    stripe_customer_id = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plan = db.relationship('SubscriptionPlan', backref='subscriptions')
    payments = db.relationship('Payment', backref='subscription', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'status': self.status.value,
            'billing_cycle': self.billing_cycle,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'created_at': self.created_at.isoformat()
        }

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = db.Column(db.String(36), db.ForeignKey('subscriptions.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False, index=True)

    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.Enum(PaymentStatus), nullable=False)

    # Payment method
    payment_method = db.Column(db.String(50), nullable=False)  # stripe, paypal, etc.
    payment_provider_id = db.Column(db.String(100), nullable=True)

    # Billing period
    billing_period_start = db.Column(db.DateTime, nullable=True)
    billing_period_end = db.Column(db.DateTime, nullable=True)

    # Metadata
    metadata = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status.value,
            'payment_method': self.payment_method,
            'billing_period_start': self.billing_period_start.isoformat() if self.billing_period_start else None,
            'billing_period_end': self.billing_period_end.isoformat() if self.billing_period_end else None,
            'created_at': self.created_at.isoformat()
        }