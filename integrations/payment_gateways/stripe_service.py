"""
Stripe Payment Gateway Service
Handles Stripe subscriptions, payments, and webhooks for FinClick.AI platform
"""

import stripe
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import time
import asyncio
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    UNPAID = "unpaid"

@dataclass
class PaymentResult:
    success: bool
    payment_id: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None

@dataclass
class SubscriptionResult:
    success: bool
    subscription_id: Optional[str] = None
    client_secret: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None

def retry_on_stripe_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry Stripe API calls on specific errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except stripe.error.RateLimitError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except stripe.error.APIConnectionError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"API connection error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except (stripe.error.StripeError, Exception) as e:
                    # Don't retry on other Stripe errors or general exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class StripeService:
    """Comprehensive Stripe payment service for FinClick.AI"""

    def __init__(self, api_key: str, webhook_secret: str):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        stripe.api_key = api_key

        # Rate limiting
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0

        logger.info("Stripe service initialized")

    async def _rate_limit_check(self):
        """Ensure we don't exceed Stripe rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    @retry_on_stripe_error()
    async def create_customer(self, email: str, name: str, metadata: Dict = None) -> Dict:
        """Create a new Stripe customer"""
        await self._rate_limit_check()

        try:
            customer_data = {
                'email': email,
                'name': name
            }
            if metadata:
                customer_data['metadata'] = metadata

            customer = stripe.Customer.create(**customer_data)
            logger.info(f"Created Stripe customer: {customer.id}")
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create customer: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_stripe_error()
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = 'usd',
        customer_id: str = None,
        metadata: Dict = None,
        automatic_payment_methods: bool = True
    ) -> PaymentResult:
        """Create a payment intent for one-time payments"""
        await self._rate_limit_check()

        try:
            payment_intent_data = {
                'amount': amount,
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': automatic_payment_methods
                }
            }

            if customer_id:
                payment_intent_data['customer'] = customer_id
            if metadata:
                payment_intent_data['metadata'] = metadata

            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)

            logger.info(f"Created payment intent: {payment_intent.id}")
            return PaymentResult(
                success=True,
                payment_id=payment_intent.id,
                raw_response=payment_intent
            )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {str(e)}")
            return PaymentResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_stripe_error()
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_period_days: int = None,
        metadata: Dict = None
    ) -> SubscriptionResult:
        """Create a subscription for recurring payments"""
        await self._rate_limit_check()

        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
                'payment_settings': {'save_default_payment_method': 'on_subscription'},
                'expand': ['latest_invoice.payment_intent']
            }

            if trial_period_days:
                subscription_data['trial_period_days'] = trial_period_days
            if metadata:
                subscription_data['metadata'] = metadata

            subscription = stripe.Subscription.create(**subscription_data)

            client_secret = None
            if subscription.latest_invoice and subscription.latest_invoice.payment_intent:
                client_secret = subscription.latest_invoice.payment_intent.client_secret

            logger.info(f"Created subscription: {subscription.id}")
            return SubscriptionResult(
                success=True,
                subscription_id=subscription.id,
                client_secret=client_secret,
                status=subscription.status,
                raw_response=subscription
            )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            return SubscriptionResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_stripe_error()
    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Dict:
        """Cancel a subscription"""
        await self._rate_limit_check()

        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)

            logger.info(f"Canceled subscription: {subscription_id}")
            return {
                'success': True,
                'subscription': subscription
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_stripe_error()
    async def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str = None,
        metadata: Dict = None
    ) -> Dict:
        """Update an existing subscription"""
        await self._rate_limit_check()

        try:
            update_data = {}

            if new_price_id:
                # Get current subscription
                subscription = stripe.Subscription.retrieve(subscription_id)
                update_data['items'] = [{
                    'id': subscription['items']['data'][0]['id'],
                    'price': new_price_id
                }]

            if metadata:
                update_data['metadata'] = metadata

            if update_data:
                subscription = stripe.Subscription.modify(subscription_id, **update_data)
                logger.info(f"Updated subscription: {subscription_id}")
                return {
                    'success': True,
                    'subscription': subscription
                }
            else:
                return {
                    'success': False,
                    'error': 'No update data provided'
                }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_stripe_error()
    async def get_customer_subscriptions(self, customer_id: str) -> Dict:
        """Get all subscriptions for a customer"""
        await self._rate_limit_check()

        try:
            subscriptions = stripe.Subscription.list(customer=customer_id)
            return {
                'success': True,
                'subscriptions': subscriptions.data
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get customer subscriptions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_stripe_error()
    async def get_payment_methods(self, customer_id: str) -> Dict:
        """Get payment methods for a customer"""
        await self._rate_limit_check()

        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            return {
                'success': True,
                'payment_methods': payment_methods.data
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get payment methods: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_stripe_error()
    async def create_setup_intent(self, customer_id: str) -> Dict:
        """Create setup intent for saving payment method"""
        await self._rate_limit_check()

        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=['card'],
                usage='off_session'
            )
            return {
                'success': True,
                'client_secret': setup_intent.client_secret
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create setup intent: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except ValueError:
            logger.error("Invalid payload in webhook")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in webhook")
            return False

    async def handle_webhook_event(self, event: Dict) -> Dict:
        """Handle incoming Stripe webhook events"""
        event_type = event['type']
        logger.info(f"Handling webhook event: {event_type}")

        try:
            if event_type == 'payment_intent.succeeded':
                return await self._handle_payment_succeeded(event['data']['object'])
            elif event_type == 'payment_intent.payment_failed':
                return await self._handle_payment_failed(event['data']['object'])
            elif event_type == 'invoice.payment_succeeded':
                return await self._handle_invoice_payment_succeeded(event['data']['object'])
            elif event_type == 'invoice.payment_failed':
                return await self._handle_invoice_payment_failed(event['data']['object'])
            elif event_type == 'customer.subscription.updated':
                return await self._handle_subscription_updated(event['data']['object'])
            elif event_type == 'customer.subscription.deleted':
                return await self._handle_subscription_deleted(event['data']['object'])
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return {'success': True, 'message': f'Event {event_type} received but not handled'}

        except Exception as e:
            logger.error(f"Error handling webhook event {event_type}: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _handle_payment_succeeded(self, payment_intent: Dict) -> Dict:
        """Handle successful payment"""
        logger.info(f"Payment succeeded: {payment_intent['id']}")
        # Add your business logic here
        return {'success': True, 'message': 'Payment processed successfully'}

    async def _handle_payment_failed(self, payment_intent: Dict) -> Dict:
        """Handle failed payment"""
        logger.warning(f"Payment failed: {payment_intent['id']}")
        # Add your business logic here
        return {'success': True, 'message': 'Payment failure processed'}

    async def _handle_invoice_payment_succeeded(self, invoice: Dict) -> Dict:
        """Handle successful invoice payment"""
        logger.info(f"Invoice payment succeeded: {invoice['id']}")
        # Add your business logic here
        return {'success': True, 'message': 'Invoice payment processed successfully'}

    async def _handle_invoice_payment_failed(self, invoice: Dict) -> Dict:
        """Handle failed invoice payment"""
        logger.warning(f"Invoice payment failed: {invoice['id']}")
        # Add your business logic here
        return {'success': True, 'message': 'Invoice payment failure processed'}

    async def _handle_subscription_updated(self, subscription: Dict) -> Dict:
        """Handle subscription update"""
        logger.info(f"Subscription updated: {subscription['id']}")
        # Add your business logic here
        return {'success': True, 'message': 'Subscription update processed'}

    async def _handle_subscription_deleted(self, subscription: Dict) -> Dict:
        """Handle subscription deletion"""
        logger.info(f"Subscription deleted: {subscription['id']}")
        # Add your business logic here
        return {'success': True, 'message': 'Subscription deletion processed'}

    @retry_on_stripe_error()
    async def refund_payment(self, payment_intent_id: str, amount: int = None) -> Dict:
        """Refund a payment"""
        await self._rate_limit_check()

        try:
            refund_data = {'payment_intent': payment_intent_id}
            if amount:
                refund_data['amount'] = amount

            refund = stripe.Refund.create(**refund_data)
            logger.info(f"Created refund: {refund.id}")
            return {
                'success': True,
                'refund_id': refund.id,
                'refund': refund
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create refund: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_stripe_error()
    async def get_balance(self) -> Dict:
        """Get account balance"""
        await self._rate_limit_check()

        try:
            balance = stripe.Balance.retrieve()
            return {
                'success': True,
                'balance': balance
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Utility functions for common operations
async def create_stripe_service(api_key: str, webhook_secret: str) -> StripeService:
    """Factory function to create StripeService instance"""
    return StripeService(api_key, webhook_secret)

def format_amount_for_stripe(amount: float, currency: str = 'usd') -> int:
    """Convert amount to Stripe format (cents)"""
    # Most currencies use 2 decimal places, but some use 0
    zero_decimal_currencies = ['bif', 'clp', 'djf', 'gnf', 'jpy', 'kmf', 'krw', 'mga', 'pyg', 'rwf', 'ugx', 'vnd', 'vuv', 'xaf', 'xof', 'xpf']

    if currency.lower() in zero_decimal_currencies:
        return int(amount)
    else:
        return int(amount * 100)

def format_amount_from_stripe(amount: int, currency: str = 'usd') -> float:
    """Convert amount from Stripe format to decimal"""
    zero_decimal_currencies = ['bif', 'clp', 'djf', 'gnf', 'jpy', 'kmf', 'krw', 'mga', 'pyg', 'rwf', 'ugx', 'vnd', 'vuv', 'xaf', 'xof', 'xpf']

    if currency.lower() in zero_decimal_currencies:
        return float(amount)
    else:
        return amount / 100.0