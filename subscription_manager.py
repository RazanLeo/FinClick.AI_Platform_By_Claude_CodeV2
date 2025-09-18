"""
FinClick.AI Subscription & Payment Management System
نظام إدارة الاشتراكات والمدفوعات لمنصة FinClick.AI

This module manages the complete subscription lifecycle:
- Three-tier subscription plans (Free, Professional, Enterprise)
- Stripe payment processing
- Usage limits and enforcement
- Billing and invoice generation
- Subscription upgrades and downgrades
- Real-time usage tracking

يدير هذا الوحدة دورة حياة الاشتراك الكاملة:
- خطط الاشتراك ثلاثية المستويات (مجاني، مهني، مؤسسي)
- معالجة المدفوعات عبر Stripe
- حدود الاستخدام وتطبيقها
- إنتاج الفواتير والمحاسبة
- ترقية وتخفيض الاشتراكات
- تتبع الاستخدام في الوقت الفعلي
"""

import stripe
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from decimal import Decimal
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import redis

# Stripe configuration
stripe.api_key = "sk_test_..." # Will be loaded from environment


class SubscriptionPlan(Enum):
    """Subscription plan types"""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(Enum):
    """Subscription status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class PaymentStatus(Enum):
    """Payment status types"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


@dataclass
class PlanLimits:
    """Subscription plan limits and features"""
    analyses_per_month: int
    ai_agents_access: int  # Number of AI agents available
    analysis_types: int    # Number of analysis types available
    file_storage_gb: int
    api_calls_per_month: int
    real_time_data: bool
    white_label: bool
    custom_integrations: bool
    priority_support: bool
    advanced_analytics: bool
    export_formats: List[str]
    concurrent_analyses: int


@dataclass
class SubscriptionData:
    """User subscription information"""
    user_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    stripe_subscription_id: Optional[str]
    stripe_customer_id: Optional[str]
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime
    updated_at: datetime
    trial_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    billing_cycle_anchor: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageData:
    """User usage tracking"""
    user_id: str
    subscription_id: str
    period_start: datetime
    period_end: datetime
    analyses_used: int
    ai_agents_used: int
    file_storage_used_gb: float
    api_calls_used: int
    last_updated: datetime
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentRecord:
    """Payment transaction record"""
    payment_id: str
    user_id: str
    subscription_id: str
    stripe_payment_intent_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SubscriptionManager:
    """
    Comprehensive subscription and payment management system
    نظام إدارة شامل للاشتراكات والمدفوعات
    """

    def __init__(self, postgres_pool, mongodb_client, redis_client):
        self.logger = logging.getLogger(__name__)
        self.postgres_pool = postgres_pool
        self.mongodb_client = mongodb_client
        self.redis_client = redis_client

        # Plan configurations
        self.plan_configs = self._initialize_plan_configs()

        # Stripe webhooks
        self.webhook_handlers = {
            'customer.subscription.created': self._handle_subscription_created,
            'customer.subscription.updated': self._handle_subscription_updated,
            'customer.subscription.deleted': self._handle_subscription_deleted,
            'invoice.payment_succeeded': self._handle_payment_succeeded,
            'invoice.payment_failed': self._handle_payment_failed,
            'customer.created': self._handle_customer_created,
        }

    def _initialize_plan_configs(self) -> Dict[SubscriptionPlan, PlanLimits]:
        """Initialize subscription plan configurations"""
        return {
            SubscriptionPlan.FREE: PlanLimits(
                analyses_per_month=5,
                ai_agents_access=3,  # Basic agents only
                analysis_types=15,   # Basic analysis types
                file_storage_gb=1,
                api_calls_per_month=100,
                real_time_data=False,
                white_label=False,
                custom_integrations=False,
                priority_support=False,
                advanced_analytics=False,
                export_formats=['PDF'],
                concurrent_analyses=1
            ),

            SubscriptionPlan.PROFESSIONAL: PlanLimits(
                analyses_per_month=100,
                ai_agents_access=15,  # Most agents
                analysis_types=120,   # Most analysis types
                file_storage_gb=50,
                api_calls_per_month=10000,
                real_time_data=True,
                white_label=False,
                custom_integrations=True,
                priority_support=True,
                advanced_analytics=True,
                export_formats=['PDF', 'Excel', 'PowerPoint'],
                concurrent_analyses=3
            ),

            SubscriptionPlan.ENTERPRISE: PlanLimits(
                analyses_per_month=-1,  # Unlimited
                ai_agents_access=23,    # All agents
                analysis_types=180,     # All analysis types
                file_storage_gb=500,
                api_calls_per_month=100000,
                real_time_data=True,
                white_label=True,
                custom_integrations=True,
                priority_support=True,
                advanced_analytics=True,
                export_formats=['PDF', 'Excel', 'PowerPoint', 'Word', 'JSON', 'XML'],
                concurrent_analyses=10
            )
        }

    async def create_subscription(self, user_id: str, plan: SubscriptionPlan,
                                payment_method_id: str, trial_days: int = 14) -> Dict[str, Any]:
        """
        Create a new subscription for a user
        إنشاء اشتراك جديد للمستخدم
        """
        try:
            # Get or create Stripe customer
            customer = await self._get_or_create_stripe_customer(user_id)

            # Attach payment method to customer
            await self._attach_payment_method(customer.id, payment_method_id)

            # Set default payment method
            stripe.Customer.modify(
                customer.id,
                invoice_settings={'default_payment_method': payment_method_id}
            )

            # Create Stripe subscription
            stripe_subscription = self._create_stripe_subscription(
                customer.id, plan, trial_days
            )

            # Create subscription record in database
            subscription_data = SubscriptionData(
                user_id=user_id,
                plan=plan,
                status=SubscriptionStatus.TRIALING if trial_days > 0 else SubscriptionStatus.ACTIVE,
                stripe_subscription_id=stripe_subscription.id,
                stripe_customer_id=customer.id,
                current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                trial_end=datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None
            )

            await self._save_subscription_to_db(subscription_data)

            # Initialize usage tracking
            await self._initialize_usage_tracking(user_id, subscription_data)

            # Update user subscription cache
            await self._update_subscription_cache(user_id, subscription_data)

            self.logger.info(f"Created subscription for user {user_id}: {plan.value}")

            return {
                'success': True,
                'subscription_id': stripe_subscription.id,
                'status': subscription_data.status.value,
                'trial_end': subscription_data.trial_end.isoformat() if subscription_data.trial_end else None,
                'current_period_end': subscription_data.current_period_end.isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to create subscription for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _get_or_create_stripe_customer(self, user_id: str) -> stripe.Customer:
        """Get existing or create new Stripe customer"""
        # Check if customer already exists
        async with self.postgres_pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT stripe_customer_id FROM users WHERE id = $1",
                user_id
            )

            if result and result['stripe_customer_id']:
                try:
                    return stripe.Customer.retrieve(result['stripe_customer_id'])
                except stripe.error.InvalidRequestError:
                    # Customer doesn't exist in Stripe, create new one
                    pass

        # Get user details
        async with self.postgres_pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT email, first_name, last_name FROM users WHERE id = $1",
                user_id
            )

        # Create new Stripe customer
        customer = stripe.Customer.create(
            email=user['email'],
            name=f"{user['first_name']} {user['last_name']}",
            metadata={'user_id': user_id}
        )

        # Update user record with Stripe customer ID
        async with self.postgres_pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET stripe_customer_id = $1 WHERE id = $2",
                customer.id, user_id
            )

        return customer

    def _create_stripe_subscription(self, customer_id: str, plan: SubscriptionPlan,
                                  trial_days: int) -> stripe.Subscription:
        """Create Stripe subscription"""
        # Get price ID based on plan
        price_ids = {
            SubscriptionPlan.FREE: None,  # Free plan doesn't need Stripe subscription
            SubscriptionPlan.PROFESSIONAL: 'price_professional_monthly',
            SubscriptionPlan.ENTERPRISE: 'price_enterprise_monthly'
        }

        if plan == SubscriptionPlan.FREE:
            raise ValueError("Free plan doesn't require Stripe subscription")

        subscription_params = {
            'customer': customer_id,
            'items': [{'price': price_ids[plan]}],
            'metadata': {'plan': plan.value},
            'expand': ['latest_invoice.payment_intent']
        }

        if trial_days > 0:
            subscription_params['trial_period_days'] = trial_days

        return stripe.Subscription.create(**subscription_params)

    async def _attach_payment_method(self, customer_id: str, payment_method_id: str):
        """Attach payment method to customer"""
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )

    async def _save_subscription_to_db(self, subscription_data: SubscriptionData):
        """Save subscription data to PostgreSQL"""
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO subscriptions (
                    user_id, plan, status, stripe_subscription_id, stripe_customer_id,
                    current_period_start, current_period_end, created_at, updated_at,
                    trial_end, cancel_at_period_end, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (user_id) DO UPDATE SET
                    plan = EXCLUDED.plan,
                    status = EXCLUDED.status,
                    stripe_subscription_id = EXCLUDED.stripe_subscription_id,
                    current_period_start = EXCLUDED.current_period_start,
                    current_period_end = EXCLUDED.current_period_end,
                    updated_at = EXCLUDED.updated_at,
                    trial_end = EXCLUDED.trial_end,
                    cancel_at_period_end = EXCLUDED.cancel_at_period_end,
                    metadata = EXCLUDED.metadata
            """,
                subscription_data.user_id,
                subscription_data.plan.value,
                subscription_data.status.value,
                subscription_data.stripe_subscription_id,
                subscription_data.stripe_customer_id,
                subscription_data.current_period_start,
                subscription_data.current_period_end,
                subscription_data.created_at,
                subscription_data.updated_at,
                subscription_data.trial_end,
                subscription_data.cancel_at_period_end,
                json.dumps(subscription_data.metadata)
            )

    async def _initialize_usage_tracking(self, user_id: str, subscription_data: SubscriptionData):
        """Initialize usage tracking for new subscription period"""
        usage_data = UsageData(
            user_id=user_id,
            subscription_id=subscription_data.stripe_subscription_id or f"free_{user_id}",
            period_start=subscription_data.current_period_start,
            period_end=subscription_data.current_period_end,
            analyses_used=0,
            ai_agents_used=0,
            file_storage_used_gb=0.0,
            api_calls_used=0,
            last_updated=datetime.now(),
            details={}
        )

        # Save to MongoDB
        db = self.mongodb_client.finclick_usage
        collection = db.usage_tracking

        await collection.replace_one(
            {'user_id': user_id, 'period_start': usage_data.period_start},
            usage_data.__dict__,
            upsert=True
        )

    async def _update_subscription_cache(self, user_id: str, subscription_data: SubscriptionData):
        """Update subscription data in Redis cache"""
        cache_key = f"subscription:{user_id}"
        cache_data = {
            'plan': subscription_data.plan.value,
            'status': subscription_data.status.value,
            'limits': self.plan_configs[subscription_data.plan].__dict__,
            'period_end': subscription_data.current_period_end.isoformat(),
            'trial_end': subscription_data.trial_end.isoformat() if subscription_data.trial_end else None
        }

        self.redis_client.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(cache_data, default=str)
        )

    async def check_usage_limits(self, user_id: str, resource_type: str,
                               amount: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if user can consume specified resource amount
        فحص ما إذا كان بإمكان المستخدم استهلاك الكمية المحددة من المورد
        """
        try:
            # Get subscription from cache first
            subscription = await self._get_subscription_from_cache(user_id)
            if not subscription:
                subscription = await self._get_subscription_from_db(user_id)
                if subscription:
                    await self._update_subscription_cache(user_id, subscription)

            if not subscription:
                # No subscription found, treat as free plan
                subscription_plan = SubscriptionPlan.FREE
            else:
                subscription_plan = subscription.plan

            # Get plan limits
            limits = self.plan_configs[subscription_plan]

            # Get current usage
            usage = await self._get_current_usage(user_id)

            # Check specific resource limits
            can_proceed = True
            limit_info = {}

            if resource_type == 'analysis':
                if limits.analyses_per_month != -1:  # Not unlimited
                    can_proceed = (usage.analyses_used + amount) <= limits.analyses_per_month
                    limit_info = {
                        'used': usage.analyses_used,
                        'limit': limits.analyses_per_month,
                        'remaining': max(0, limits.analyses_per_month - usage.analyses_used)
                    }
                else:
                    limit_info = {'used': usage.analyses_used, 'limit': 'unlimited', 'remaining': 'unlimited'}

            elif resource_type == 'api_call':
                if limits.api_calls_per_month != -1:
                    can_proceed = (usage.api_calls_used + amount) <= limits.api_calls_per_month
                    limit_info = {
                        'used': usage.api_calls_used,
                        'limit': limits.api_calls_per_month,
                        'remaining': max(0, limits.api_calls_per_month - usage.api_calls_used)
                    }
                else:
                    limit_info = {'used': usage.api_calls_used, 'limit': 'unlimited', 'remaining': 'unlimited'}

            elif resource_type == 'file_storage':
                can_proceed = (usage.file_storage_used_gb + amount) <= limits.file_storage_gb
                limit_info = {
                    'used_gb': usage.file_storage_used_gb,
                    'limit_gb': limits.file_storage_gb,
                    'remaining_gb': max(0, limits.file_storage_gb - usage.file_storage_used_gb)
                }

            elif resource_type == 'concurrent_analysis':
                # Check current active analyses
                active_analyses = await self._get_active_analyses_count(user_id)
                can_proceed = (active_analyses + amount) <= limits.concurrent_analyses
                limit_info = {
                    'active': active_analyses,
                    'limit': limits.concurrent_analyses,
                    'remaining': max(0, limits.concurrent_analyses - active_analyses)
                }

            return can_proceed, {
                'allowed': can_proceed,
                'plan': subscription_plan.value,
                'resource_type': resource_type,
                'limit_info': limit_info,
                'subscription_status': subscription.status.value if subscription else 'free'
            }

        except Exception as e:
            self.logger.error(f"Error checking usage limits for user {user_id}: {str(e)}")
            return False, {'error': str(e)}

    async def record_usage(self, user_id: str, resource_type: str,
                          amount: int = 1, metadata: Dict[str, Any] = None):
        """
        Record resource usage for a user
        تسجيل استخدام المورد للمستخدم
        """
        try:
            # Get current usage
            usage = await self._get_current_usage(user_id)

            # Update usage based on resource type
            if resource_type == 'analysis':
                usage.analyses_used += amount
            elif resource_type == 'api_call':
                usage.api_calls_used += amount
            elif resource_type == 'file_storage':
                usage.file_storage_used_gb += amount

            # Add metadata
            if metadata:
                if 'usage_history' not in usage.details:
                    usage.details['usage_history'] = []

                usage.details['usage_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'resource_type': resource_type,
                    'amount': amount,
                    'metadata': metadata
                })

                # Keep only last 100 usage records
                usage.details['usage_history'] = usage.details['usage_history'][-100:]

            usage.last_updated = datetime.now()

            # Save to MongoDB
            db = self.mongodb_client.finclick_usage
            collection = db.usage_tracking

            await collection.replace_one(
                {'user_id': user_id, 'period_start': usage.period_start},
                usage.__dict__,
                upsert=True
            )

            # Update usage cache
            await self._update_usage_cache(user_id, usage)

            self.logger.debug(f"Recorded usage for user {user_id}: {resource_type} +{amount}")

        except Exception as e:
            self.logger.error(f"Error recording usage for user {user_id}: {str(e)}")

    async def _get_subscription_from_cache(self, user_id: str) -> Optional[SubscriptionData]:
        """Get subscription data from Redis cache"""
        cache_key = f"subscription:{user_id}"
        data = self.redis_client.get(cache_key)

        if data:
            try:
                cache_data = json.loads(data)
                # Convert back to SubscriptionData object
                # This is a simplified version - in production, implement proper deserialization
                return SubscriptionData(
                    user_id=user_id,
                    plan=SubscriptionPlan(cache_data['plan']),
                    status=SubscriptionStatus(cache_data['status']),
                    stripe_subscription_id=None,  # Not stored in cache
                    stripe_customer_id=None,      # Not stored in cache
                    current_period_start=datetime.now(),  # Would be properly stored
                    current_period_end=datetime.fromisoformat(cache_data['period_end']),
                    created_at=datetime.now(),    # Would be properly stored
                    updated_at=datetime.now()     # Would be properly stored
                )
            except (json.JSONDecodeError, KeyError, ValueError):
                return None

        return None

    async def _get_subscription_from_db(self, user_id: str) -> Optional[SubscriptionData]:
        """Get subscription data from PostgreSQL"""
        async with self.postgres_pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT * FROM subscriptions WHERE user_id = $1",
                user_id
            )

            if result:
                return SubscriptionData(
                    user_id=result['user_id'],
                    plan=SubscriptionPlan(result['plan']),
                    status=SubscriptionStatus(result['status']),
                    stripe_subscription_id=result['stripe_subscription_id'],
                    stripe_customer_id=result['stripe_customer_id'],
                    current_period_start=result['current_period_start'],
                    current_period_end=result['current_period_end'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    trial_end=result['trial_end'],
                    cancel_at_period_end=result['cancel_at_period_end'],
                    metadata=json.loads(result['metadata']) if result['metadata'] else {}
                )

        return None

    async def _get_current_usage(self, user_id: str) -> UsageData:
        """Get current period usage for user"""
        # Try cache first
        cache_key = f"usage:{user_id}"
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            try:
                data = json.loads(cached_data)
                return UsageData(**data)
            except (json.JSONDecodeError, TypeError):
                pass

        # Get from MongoDB
        db = self.mongodb_client.finclick_usage
        collection = db.usage_tracking

        # Get current subscription period
        subscription = await self._get_subscription_from_db(user_id)
        if subscription:
            period_start = subscription.current_period_start
        else:
            # For free users, use monthly periods starting from account creation
            period_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        usage_doc = await collection.find_one({
            'user_id': user_id,
            'period_start': period_start
        })

        if usage_doc:
            # Convert ObjectId to string and remove it
            usage_doc.pop('_id', None)
            return UsageData(**usage_doc)
        else:
            # Create new usage record
            period_end = period_start + timedelta(days=30)  # Default 30-day period
            return UsageData(
                user_id=user_id,
                subscription_id=subscription.stripe_subscription_id if subscription else f"free_{user_id}",
                period_start=period_start,
                period_end=period_end,
                analyses_used=0,
                ai_agents_used=0,
                file_storage_used_gb=0.0,
                api_calls_used=0,
                last_updated=datetime.now()
            )

    async def _update_usage_cache(self, user_id: str, usage: UsageData):
        """Update usage data in Redis cache"""
        cache_key = f"usage:{user_id}"
        cache_data = usage.__dict__.copy()

        # Convert datetime objects to ISO strings for JSON serialization
        for key, value in cache_data.items():
            if isinstance(value, datetime):
                cache_data[key] = value.isoformat()

        self.redis_client.setex(
            cache_key,
            1800,  # 30 minutes TTL
            json.dumps(cache_data, default=str)
        )

    async def _get_active_analyses_count(self, user_id: str) -> int:
        """Get count of currently active analyses for user"""
        # This would query the analysis queue/active analyses
        # Placeholder implementation
        cache_key = f"active_analyses:{user_id}"
        count = self.redis_client.get(cache_key)
        return int(count) if count else 0

    # Stripe webhook handlers
    async def handle_webhook(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        if event_type in self.webhook_handlers:
            try:
                return await self.webhook_handlers[event_type](event_data)
            except Exception as e:
                self.logger.error(f"Error handling webhook {event_type}: {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            self.logger.warning(f"Unhandled webhook event type: {event_type}")
            return {'success': False, 'error': 'Unhandled event type'}

    async def _handle_subscription_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created webhook"""
        subscription = event_data['data']['object']
        customer_id = subscription['customer']

        # Get user ID from customer metadata
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get('user_id')

        if user_id:
            # Update subscription in database
            await self._sync_subscription_from_stripe(user_id, subscription['id'])

        return {'success': True}

    async def _handle_subscription_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updated webhook"""
        subscription = event_data['data']['object']
        customer_id = subscription['customer']

        # Get user ID and sync subscription
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get('user_id')

        if user_id:
            await self._sync_subscription_from_stripe(user_id, subscription['id'])

        return {'success': True}

    async def _handle_subscription_deleted(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted webhook"""
        subscription = event_data['data']['object']
        customer_id = subscription['customer']

        # Get user ID and update status
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get('user_id')

        if user_id:
            # Set subscription to cancelled
            async with self.postgres_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE subscriptions SET status = $1, updated_at = $2 WHERE user_id = $3",
                    SubscriptionStatus.CANCELLED.value, datetime.now(), user_id
                )

            # Clear cache
            self.redis_client.delete(f"subscription:{user_id}")

        return {'success': True}

    async def _handle_payment_succeeded(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment webhook"""
        invoice = event_data['data']['object']
        subscription_id = invoice['subscription']

        # Record payment
        payment_record = PaymentRecord(
            payment_id=f"payment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id="",  # Will be filled from subscription
            subscription_id=subscription_id,
            stripe_payment_intent_id=invoice['payment_intent'],
            amount=Decimal(str(invoice['amount_paid'] / 100)),  # Convert from cents
            currency=invoice['currency'],
            status=PaymentStatus.SUCCEEDED,
            payment_method="stripe",
            created_at=datetime.fromtimestamp(invoice['created']),
            processed_at=datetime.now()
        )

        # Save payment record to database
        await self._save_payment_record(payment_record)

        return {'success': True}

    async def _handle_payment_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment webhook"""
        invoice = event_data['data']['object']

        # Handle payment failure - could suspend account, send notifications, etc.
        self.logger.warning(f"Payment failed for subscription {invoice['subscription']}")

        return {'success': True}

    async def _handle_customer_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer created webhook"""
        customer = event_data['data']['object']

        # Update user record with customer ID if needed
        user_id = customer['metadata'].get('user_id')
        if user_id:
            async with self.postgres_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET stripe_customer_id = $1 WHERE id = $2",
                    customer['id'], user_id
                )

        return {'success': True}

    async def _sync_subscription_from_stripe(self, user_id: str, stripe_subscription_id: str):
        """Sync subscription data from Stripe"""
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)

        # Update database
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                UPDATE subscriptions SET
                    status = $1,
                    current_period_start = $2,
                    current_period_end = $3,
                    trial_end = $4,
                    cancel_at_period_end = $5,
                    updated_at = $6
                WHERE user_id = $7
            """,
                subscription['status'],
                datetime.fromtimestamp(subscription['current_period_start']),
                datetime.fromtimestamp(subscription['current_period_end']),
                datetime.fromtimestamp(subscription['trial_end']) if subscription['trial_end'] else None,
                subscription['cancel_at_period_end'],
                datetime.now(),
                user_id
            )

        # Clear cache to force refresh
        self.redis_client.delete(f"subscription:{user_id}")

    async def _save_payment_record(self, payment: PaymentRecord):
        """Save payment record to database"""
        # This would save to a payments table in PostgreSQL
        # Implementation depends on your database schema
        pass

    async def get_subscription_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans with pricing"""
        plans = []

        for plan, limits in self.plan_configs.items():
            plan_data = {
                'id': plan.value,
                'name': self._get_plan_display_name(plan),
                'name_ar': self._get_plan_display_name_ar(plan),
                'price_monthly': self._get_plan_price(plan),
                'limits': limits.__dict__,
                'features': self._get_plan_features(plan),
                'features_ar': self._get_plan_features_ar(plan),
                'is_popular': plan == SubscriptionPlan.PROFESSIONAL
            }
            plans.append(plan_data)

        return plans

    def _get_plan_display_name(self, plan: SubscriptionPlan) -> str:
        """Get plan display name in English"""
        names = {
            SubscriptionPlan.FREE: "Free Plan",
            SubscriptionPlan.PROFESSIONAL: "Professional Plan",
            SubscriptionPlan.ENTERPRISE: "Enterprise Plan"
        }
        return names[plan]

    def _get_plan_display_name_ar(self, plan: SubscriptionPlan) -> str:
        """Get plan display name in Arabic"""
        names = {
            SubscriptionPlan.FREE: "الخطة المجانية",
            SubscriptionPlan.PROFESSIONAL: "الخطة المهنية",
            SubscriptionPlan.ENTERPRISE: "الخطة المؤسسية"
        }
        return names[plan]

    def _get_plan_price(self, plan: SubscriptionPlan) -> int:
        """Get plan monthly price in USD"""
        prices = {
            SubscriptionPlan.FREE: 0,
            SubscriptionPlan.PROFESSIONAL: 99,
            SubscriptionPlan.ENTERPRISE: 299
        }
        return prices[plan]

    def _get_plan_features(self, plan: SubscriptionPlan) -> List[str]:
        """Get plan features list in English"""
        features = {
            SubscriptionPlan.FREE: [
                "5 analyses per month",
                "Basic AI agents",
                "PDF reports",
                "1GB file storage",
                "Community support"
            ],
            SubscriptionPlan.PROFESSIONAL: [
                "100 analyses per month",
                "Advanced AI agents",
                "Real-time data",
                "Multiple export formats",
                "50GB file storage",
                "Priority support",
                "API access"
            ],
            SubscriptionPlan.ENTERPRISE: [
                "Unlimited analyses",
                "All AI agents (23 total)",
                "All analysis types (180 total)",
                "White-label solution",
                "Custom integrations",
                "500GB file storage",
                "Dedicated support",
                "Full API access"
            ]
        }
        return features[plan]

    def _get_plan_features_ar(self, plan: SubscriptionPlan) -> List[str]:
        """Get plan features list in Arabic"""
        features = {
            SubscriptionPlan.FREE: [
                "5 تحليلات شهرياً",
                "الوكلاء الأساسيين",
                "تقارير PDF",
                "1 جيجابايت تخزين",
                "دعم المجتمع"
            ],
            SubscriptionPlan.PROFESSIONAL: [
                "100 تحليل شهرياً",
                "الوكلاء المتقدمين",
                "بيانات فورية",
                "تنسيقات تصدير متعددة",
                "50 جيجابايت تخزين",
                "دعم أولوية",
                "وصول API"
            ],
            SubscriptionPlan.ENTERPRISE: [
                "تحليلات غير محدودة",
                "جميع الوكلاء (23 وكيل)",
                "جميع أنواع التحليل (180 نوع)",
                "حل العلامة البيضاء",
                "تكاملات مخصصة",
                "500 جيجابايت تخزين",
                "دعم مخصص",
                "وصول API كامل"
            ]
        }
        return features[plan]