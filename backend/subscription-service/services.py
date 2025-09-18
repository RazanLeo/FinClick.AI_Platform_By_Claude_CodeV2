import os
from datetime import datetime, timedelta
from app import db, current_app
from models import Subscription, SubscriptionPlan, Payment, SubscriptionStatus, PaymentStatus
import logging
import stripe

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Subscription management service"""

    @staticmethod
    def create_subscription(user_id, plan_id, billing_cycle='monthly', payment_method='stripe', payment_details=None):
        """Create a new subscription"""
        try:
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan:
                raise ValueError("Plan not found")

            # Check for existing active subscription
            existing = Subscription.query.filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).first()

            if existing:
                raise ValueError("User already has an active subscription")

            # Create subscription
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.TRIAL,
                billing_cycle=billing_cycle,
                trial_end_date=datetime.utcnow() + timedelta(days=14)
            )

            if billing_cycle == 'yearly':
                subscription.next_billing_date = datetime.utcnow() + timedelta(days=365)
            else:
                subscription.next_billing_date = datetime.utcnow() + timedelta(days=30)

            db.session.add(subscription)
            db.session.flush()

            # Process payment if not trial
            if payment_method and payment_details:
                PaymentService.process_payment(subscription.id, payment_details)

            return subscription

        except Exception as e:
            logger.error(f"Create subscription error: {str(e)}")
            raise

    @staticmethod
    def cancel_subscription(user_id):
        """Cancel user's active subscription"""
        try:
            subscription = Subscription.query.filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).first()

            if not subscription:
                raise ValueError("No active subscription found")

            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()

            return {
                'cancelled_at': subscription.cancelled_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Cancel subscription error: {str(e)}")
            raise

class PaymentService:
    """Payment processing service"""

    @staticmethod
    def process_payment(subscription_id, payment_details):
        """Process payment for subscription"""
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                raise ValueError("Subscription not found")

            plan = subscription.plan
            amount = plan.price_monthly if subscription.billing_cycle == 'monthly' else plan.price_yearly

            # Create payment record
            payment = Payment(
                subscription_id=subscription_id,
                user_id=subscription.user_id,
                amount=amount,
                currency=plan.currency,
                status=PaymentStatus.PENDING,
                payment_method='stripe'
            )

            db.session.add(payment)
            db.session.flush()

            # Process with Stripe (mock implementation)
            stripe_result = PaymentService.process_stripe_payment(payment, payment_details)

            if stripe_result['success']:
                payment.status = PaymentStatus.COMPLETED
                payment.payment_provider_id = stripe_result['payment_id']
                subscription.status = SubscriptionStatus.ACTIVE
            else:
                payment.status = PaymentStatus.FAILED

            return payment

        except Exception as e:
            logger.error(f"Process payment error: {str(e)}")
            raise

    @staticmethod
    def process_stripe_payment(payment, payment_details):
        """Process payment with Stripe"""
        try:
            # Mock Stripe payment processing
            return {
                'success': True,
                'payment_id': f'stripe_payment_{payment.id}',
                'message': 'Payment processed successfully'
            }

        except Exception as e:
            logger.error(f"Stripe payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def handle_stripe_webhook(payload, signature):
        """Handle Stripe webhook events"""
        try:
            # Mock webhook processing
            logger.info("Stripe webhook received")
            return {'status': 'processed'}

        except Exception as e:
            logger.error(f"Stripe webhook error: {str(e)}")
            raise