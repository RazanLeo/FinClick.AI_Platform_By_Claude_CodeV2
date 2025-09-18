from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import logging
import os
from datetime import datetime, timedelta
import stripe
import paypal_sdk
from decimal import Decimal
import json

# تهيئة التطبيق
app = Flask(__name__)
CORS(app)

# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/finclick_subscriptions')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')

# تهيئة الملحقات
db = SQLAlchemy(app)
jwt = JWTManager(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# إعداد بوابات الدفع
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# النماذج
class SubscriptionPlan(db.Model):
    """نموذج خطط الاشتراك"""
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    price_usd = db.Column(db.Numeric(10, 2), nullable=False)
    price_sar = db.Column(db.Numeric(10, 2), nullable=False)
    analyses_limit = db.Column(db.Integer, nullable=False)  # -1 for unlimited
    features = db.Column(db.JSON)
    features_ar = db.Column(db.JSON)
    stripe_price_id = db.Column(db.String(100))
    paypal_plan_id = db.Column(db.String(100))
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, yearly
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, language='en'):
        return {
            'id': self.id,
            'name': self.name_ar if language == 'ar' else self.name,
            'description': self.description_ar if language == 'ar' else self.description,
            'price_usd': float(self.price_usd),
            'price_sar': float(self.price_sar),
            'analyses_limit': self.analyses_limit,
            'features': self.features_ar if language == 'ar' else self.features,
            'billing_cycle': self.billing_cycle,
            'stripe_price_id': self.stripe_price_id,
            'paypal_plan_id': self.paypal_plan_id
        }

class UserSubscription(db.Model):
    """نموذج اشتراكات المستخدمين"""
    __tablename__ = 'user_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired, suspended
    stripe_subscription_id = db.Column(db.String(100))
    paypal_subscription_id = db.Column(db.String(100))
    current_period_start = db.Column(db.DateTime, nullable=False)
    current_period_end = db.Column(db.DateTime, nullable=False)
    analyses_used = db.Column(db.Integer, default=0)
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = db.relationship('SubscriptionPlan', backref='subscriptions')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan.to_dict(),
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat(),
            'current_period_end': self.current_period_end.isoformat(),
            'analyses_used': self.analyses_used,
            'analyses_remaining': self.get_analyses_remaining(),
            'cancel_at_period_end': self.cancel_at_period_end
        }

    def get_analyses_remaining(self):
        if self.plan.analyses_limit == -1:
            return -1  # Unlimited
        return max(0, self.plan.analyses_limit - self.analyses_used)

    def can_perform_analysis(self):
        if self.status != 'active':
            return False
        if self.current_period_end < datetime.utcnow():
            return False
        return self.get_analyses_remaining() > 0 or self.plan.analyses_limit == -1

class Payment(db.Model):
    """نموذج المدفوعات"""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_method = db.Column(db.String(20), nullable=False)  # stripe, paypal, paytabs
    payment_intent_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, succeeded, failed, cancelled
    failure_reason = db.Column(db.String(255))
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subscription = db.relationship('UserSubscription', backref='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

# خدمات الاشتراكات
class SubscriptionService:
    """خدمة إدارة الاشتراكات"""

    @staticmethod
    def create_stripe_subscription(user_id, plan_id, payment_method_id):
        """إنشاء اشتراك جديد في Stripe"""
        try:
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan or not plan.stripe_price_id:
                raise ValueError("Invalid plan or missing Stripe price ID")

            # إنشاء العميل في Stripe
            customer = stripe.Customer.create(
                metadata={'user_id': str(user_id)}
            )

            # ربط طريقة الدفع بالعميل
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer.id
            )

            # إنشاء الاشتراك
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': plan.stripe_price_id}],
                default_payment_method=payment_method_id,
                metadata={'user_id': str(user_id), 'plan_id': str(plan_id)}
            )

            # حفظ الاشتراك في قاعدة البيانات
            period_start = datetime.fromtimestamp(subscription.current_period_start)
            period_end = datetime.fromtimestamp(subscription.current_period_end)

            user_subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                stripe_subscription_id=subscription.id,
                status='active' if subscription.status == 'active' else 'pending',
                current_period_start=period_start,
                current_period_end=period_end
            )

            db.session.add(user_subscription)
            db.session.commit()

            return user_subscription

        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def create_paypal_subscription(user_id, plan_id):
        """إنشاء اشتراك جديد في PayPal"""
        try:
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan or not plan.paypal_plan_id:
                raise ValueError("Invalid plan or missing PayPal plan ID")

            # إنشاء اشتراك PayPal (يتطلب SDK PayPal)
            # هذا مثال مبسط - يحتاج تطوير أكثر

            user_subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                status='pending',
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )

            db.session.add(user_subscription)
            db.session.commit()

            return user_subscription

        except Exception as e:
            logger.error(f"Error creating PayPal subscription: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def cancel_subscription(subscription_id, user_id):
        """إلغاء الاشتراك"""
        try:
            subscription = UserSubscription.query.filter_by(
                id=subscription_id,
                user_id=user_id
            ).first()

            if not subscription:
                raise ValueError("Subscription not found")

            # إلغاء في Stripe
            if subscription.stripe_subscription_id:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )

            # إلغاء في PayPal
            if subscription.paypal_subscription_id:
                # PayPal cancellation logic
                pass

            subscription.cancel_at_period_end = True
            subscription.updated_at = datetime.utcnow()

            db.session.commit()

            return subscription

        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def update_usage(user_id, analyses_count=1):
        """تحديث استخدام التحليلات"""
        try:
            subscription = UserSubscription.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()

            if not subscription:
                raise ValueError("No active subscription found")

            if not subscription.can_perform_analysis():
                raise ValueError("Analysis limit exceeded or subscription expired")

            subscription.analyses_used += analyses_count
            subscription.updated_at = datetime.utcnow()

            db.session.commit()

            return subscription

        except Exception as e:
            logger.error(f"Error updating usage: {str(e)}")
            db.session.rollback()
            raise

# Routes - نقاط النهاية

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة الخدمة"""
    return jsonify({
        'status': 'healthy',
        'service': 'subscription-service',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/plans', methods=['GET'])
@limiter.limit("10 per minute")
def get_subscription_plans():
    """الحصول على جميع خطط الاشتراك"""
    try:
        language = request.args.get('lang', 'en')
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()

        return jsonify({
            'success': True,
            'plans': [plan.to_dict(language) for plan in plans]
        })

    except Exception as e:
        logger.error(f"Error fetching plans: {str(e)}")
        return jsonify({'error': 'Failed to fetch plans'}), 500

@app.route('/subscribe', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def create_subscription():
    """إنشاء اشتراك جديد"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        plan_id = data.get('plan_id')
        payment_method = data.get('payment_method', 'stripe')
        payment_method_id = data.get('payment_method_id')

        if not plan_id:
            return jsonify({'error': 'Plan ID is required'}), 400

        # التحقق من وجود اشتراك نشط
        existing_subscription = UserSubscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

        if existing_subscription:
            return jsonify({'error': 'User already has an active subscription'}), 400

        # إنشاء الاشتراك حسب طريقة الدفع
        if payment_method == 'stripe':
            if not payment_method_id:
                return jsonify({'error': 'Payment method ID is required for Stripe'}), 400

            subscription = SubscriptionService.create_stripe_subscription(
                user_id, plan_id, payment_method_id
            )
        elif payment_method == 'paypal':
            subscription = SubscriptionService.create_paypal_subscription(
                user_id, plan_id
            )
        else:
            return jsonify({'error': 'Unsupported payment method'}), 400

        return jsonify({
            'success': True,
            'subscription': subscription.to_dict()
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return jsonify({'error': 'Failed to create subscription'}), 500

@app.route('/subscription', methods=['GET'])
@jwt_required()
def get_user_subscription():
    """الحصول على اشتراك المستخدم الحالي"""
    try:
        user_id = get_jwt_identity()

        subscription = UserSubscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404

        return jsonify({
            'success': True,
            'subscription': subscription.to_dict()
        })

    except Exception as e:
        logger.error(f"Error fetching subscription: {str(e)}")
        return jsonify({'error': 'Failed to fetch subscription'}), 500

@app.route('/subscription/<int:subscription_id>/cancel', methods=['POST'])
@jwt_required()
@limiter.limit("2 per minute")
def cancel_subscription(subscription_id):
    """إلغاء الاشتراك"""
    try:
        user_id = get_jwt_identity()

        subscription = SubscriptionService.cancel_subscription(subscription_id, user_id)

        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully',
            'subscription': subscription.to_dict()
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500

@app.route('/usage/update', methods=['POST'])
@jwt_required()
@limiter.limit("100 per hour")
def update_usage():
    """تحديث استخدام التحليلات"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        analyses_count = data.get('analyses_count', 1)

        subscription = SubscriptionService.update_usage(user_id, analyses_count)

        return jsonify({
            'success': True,
            'subscription': subscription.to_dict()
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating usage: {str(e)}")
        return jsonify({'error': 'Failed to update usage'}), 500

@app.route('/usage/check', methods=['GET'])
@jwt_required()
def check_usage_limits():
    """فحص حدود الاستخدام"""
    try:
        user_id = get_jwt_identity()

        subscription = UserSubscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

        if not subscription:
            return jsonify({
                'can_perform_analysis': False,
                'reason': 'No active subscription'
            })

        can_perform = subscription.can_perform_analysis()

        return jsonify({
            'success': True,
            'can_perform_analysis': can_perform,
            'analyses_used': subscription.analyses_used,
            'analyses_remaining': subscription.get_analyses_remaining(),
            'subscription': subscription.to_dict()
        })

    except Exception as e:
        logger.error(f"Error checking usage limits: {str(e)}")
        return jsonify({'error': 'Failed to check usage limits'}), 500

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """معالج webhook للـ Stripe"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        # معالجة أحداث Stripe المختلفة
        if event['type'] == 'invoice.payment_succeeded':
            # تحديث حالة الاشتراك
            invoice = event['data']['object']
            subscription_id = invoice['subscription']

            subscription = UserSubscription.query.filter_by(
                stripe_subscription_id=subscription_id
            ).first()

            if subscription:
                subscription.status = 'active'
                subscription.updated_at = datetime.utcnow()
                db.session.commit()

        elif event['type'] == 'invoice.payment_failed':
            # معالجة فشل الدفع
            invoice = event['data']['object']
            subscription_id = invoice['subscription']

            subscription = UserSubscription.query.filter_by(
                stripe_subscription_id=subscription_id
            ).first()

            if subscription:
                subscription.status = 'suspended'
                subscription.updated_at = datetime.utcnow()
                db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 400

@app.route('/payments/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """الحصول على تاريخ المدفوعات"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        payments = Payment.query.filter_by(user_id=user_id)\
            .order_by(Payment.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'payments': [payment.to_dict() for payment in payments.items],
            'pagination': {
                'page': page,
                'pages': payments.pages,
                'per_page': per_page,
                'total': payments.total
            }
        })

    except Exception as e:
        logger.error(f"Error fetching payment history: {str(e)}")
        return jsonify({'error': 'Failed to fetch payment history'}), 500

# معالجات الأخطاء
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded'}), 429

# تهيئة قاعدة البيانات
@app.before_first_request
def create_tables():
    """إنشاء الجداول عند بدء التطبيق"""
    db.create_all()

    # إضافة خطط الاشتراك الافتراضية
    if SubscriptionPlan.query.count() == 0:
        plans = [
            SubscriptionPlan(
                name='Free',
                name_ar='مجاني',
                description='Basic analysis capabilities',
                description_ar='إمكانيات تحليل أساسية',
                price_usd=0.00,
                price_sar=0.00,
                analyses_limit=5,
                features=['5 analyses per month', 'Basic reports', 'Email support'],
                features_ar=['5 تحليلات شهرياً', 'تقارير أساسية', 'دعم بريد إلكتروني'],
                billing_cycle='monthly'
            ),
            SubscriptionPlan(
                name='Basic',
                name_ar='أساسي',
                description='Enhanced analysis features',
                description_ar='ميزات تحليل محسنة',
                price_usd=29.00,
                price_sar=109.00,
                analyses_limit=50,
                features=['50 analyses per month', 'Advanced reports', 'Priority support'],
                features_ar=['50 تحليل شهرياً', 'تقارير متقدمة', 'دعم أولوية'],
                billing_cycle='monthly'
            ),
            SubscriptionPlan(
                name='Advanced',
                name_ar='متقدم',
                description='Professional analysis suite',
                description_ar='مجموعة تحليل احترافية',
                price_usd=99.00,
                price_sar=371.00,
                analyses_limit=200,
                features=['200 analyses per month', 'Professional reports', 'API access'],
                features_ar=['200 تحليل شهرياً', 'تقارير احترافية', 'وصول API'],
                billing_cycle='monthly'
            ),
            SubscriptionPlan(
                name='Enterprise',
                name_ar='مؤسسي',
                description='Unlimited analysis capabilities',
                description_ar='إمكانيات تحليل غير محدودة',
                price_usd=299.00,
                price_sar=1121.00,
                analyses_limit=-1,
                features=['Unlimited analyses', 'Custom reports', 'Dedicated support'],
                features_ar=['تحليلات غير محدودة', 'تقارير مخصصة', 'دعم مخصص'],
                billing_cycle='monthly'
            )
        ]

        for plan in plans:
            db.session.add(plan)

        db.session.commit()
        logger.info("Default subscription plans created")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)