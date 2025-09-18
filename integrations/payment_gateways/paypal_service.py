"""
PayPal Payment Gateway Service
Handles PayPal payments and recurring billing for FinClick.AI platform
"""

import requests
import logging
import base64
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import time

# Configure logging
logger = logging.getLogger(__name__)

class PayPalEnvironment(Enum):
    SANDBOX = "sandbox"
    LIVE = "live"

class SubscriptionStatus(Enum):
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

@dataclass
class PayPalPaymentResult:
    success: bool
    payment_id: Optional[str] = None
    approval_url: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None

@dataclass
class PayPalSubscriptionResult:
    success: bool
    subscription_id: Optional[str] = None
    approval_url: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None

def retry_on_paypal_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry PayPal API calls on specific errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except aiohttp.ClientError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"PayPal API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class PayPalService:
    """Comprehensive PayPal payment service for FinClick.AI"""

    def __init__(self, client_id: str, client_secret: str, environment: PayPalEnvironment = PayPalEnvironment.SANDBOX):
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment

        if environment == PayPalEnvironment.SANDBOX:
            self.base_url = "https://api-m.sandbox.paypal.com"
        else:
            self.base_url = "https://api-m.paypal.com"

        self.access_token = None
        self.token_expires_at = None

        # Rate limiting
        self.rate_limit_delay = 0.2  # 200ms between requests
        self.last_request_time = 0

        logger.info(f"PayPal service initialized for {environment.value} environment")

    async def _rate_limit_check(self):
        """Ensure we don't exceed PayPal rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    async def _get_access_token(self) -> str:
        """Get or refresh PayPal access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        await self._rate_limit_check()

        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = 'grant_type=client_credentials'

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/v1/oauth2/token",
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    logger.info("PayPal access token obtained successfully")
                    return self.access_token
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get PayPal access token: {error_text}")
                    raise Exception(f"Failed to get PayPal access token: {response.status}")

    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to PayPal API"""
        await self._rate_limit_check()

        access_token = await self._get_access_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'PayPal-Request-Id': f"finclick-{int(time.time())}"
        }

        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession() as session:
            if method.upper() == 'GET':
                async with session.get(url, headers=headers) as response:
                    return await self._handle_response(response)
            elif method.upper() == 'POST':
                async with session.post(url, headers=headers, json=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == 'PATCH':
                async with session.patch(url, headers=headers, json=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == 'DELETE':
                async with session.delete(url, headers=headers) as response:
                    return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict:
        """Handle PayPal API response"""
        response_text = await response.text()

        if response.status in [200, 201, 204]:
            if response_text:
                return json.loads(response_text)
            else:
                return {'success': True}
        else:
            logger.error(f"PayPal API error {response.status}: {response_text}")
            error_data = {}
            try:
                error_data = json.loads(response_text) if response_text else {}
            except json.JSONDecodeError:
                pass

            raise Exception(f"PayPal API error {response.status}: {error_data.get('message', response_text)}")

    @retry_on_paypal_error()
    async def create_payment(
        self,
        amount: float,
        currency: str = 'USD',
        description: str = 'Payment',
        return_url: str = None,
        cancel_url: str = None
    ) -> PayPalPaymentResult:
        """Create a one-time payment"""
        try:
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": f"{amount:.2f}",
                        "currency": currency
                    },
                    "description": description
                }],
                "redirect_urls": {
                    "return_url": return_url or "https://finclick.ai/payment/success",
                    "cancel_url": cancel_url or "https://finclick.ai/payment/cancel"
                }
            }

            response = await self._make_request('POST', '/v1/payments/payment', payment_data)

            approval_url = None
            for link in response.get('links', []):
                if link.get('rel') == 'approval_url':
                    approval_url = link.get('href')
                    break

            logger.info(f"Created PayPal payment: {response.get('id')}")
            return PayPalPaymentResult(
                success=True,
                payment_id=response.get('id'),
                approval_url=approval_url,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Failed to create PayPal payment: {str(e)}")
            return PayPalPaymentResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_paypal_error()
    async def execute_payment(self, payment_id: str, payer_id: str) -> Dict:
        """Execute approved payment"""
        try:
            execution_data = {
                "payer_id": payer_id
            }

            response = await self._make_request(
                'POST',
                f'/v1/payments/payment/{payment_id}/execute',
                execution_data
            )

            logger.info(f"Executed PayPal payment: {payment_id}")
            return {
                'success': True,
                'payment': response
            }

        except Exception as e:
            logger.error(f"Failed to execute PayPal payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paypal_error()
    async def create_product(self, name: str, description: str, product_type: str = 'SERVICE') -> Dict:
        """Create a product for subscriptions"""
        try:
            product_data = {
                "name": name,
                "description": description,
                "type": product_type,
                "category": "SOFTWARE"
            }

            response = await self._make_request('POST', '/v1/catalogs/products', product_data)

            logger.info(f"Created PayPal product: {response.get('id')}")
            return {
                'success': True,
                'product_id': response.get('id'),
                'product': response
            }

        except Exception as e:
            logger.error(f"Failed to create PayPal product: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paypal_error()
    async def create_plan(
        self,
        product_id: str,
        name: str,
        description: str,
        amount: float,
        currency: str = 'USD',
        interval_unit: str = 'MONTH',
        interval_count: int = 1
    ) -> Dict:
        """Create a billing plan for subscriptions"""
        try:
            plan_data = {
                "product_id": product_id,
                "name": name,
                "description": description,
                "billing_cycles": [{
                    "frequency": {
                        "interval_unit": interval_unit,
                        "interval_count": interval_count
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,  # 0 means infinite
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": f"{amount:.2f}",
                            "currency_code": currency
                        }
                    }
                }],
                "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "setup_fee": {
                        "value": "0",
                        "currency_code": currency
                    },
                    "setup_fee_failure_action": "CONTINUE",
                    "payment_failure_threshold": 3
                },
                "taxes": {
                    "percentage": "0",
                    "inclusive": False
                }
            }

            response = await self._make_request('POST', '/v1/billing/plans', plan_data)

            logger.info(f"Created PayPal plan: {response.get('id')}")
            return {
                'success': True,
                'plan_id': response.get('id'),
                'plan': response
            }

        except Exception as e:
            logger.error(f"Failed to create PayPal plan: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paypal_error()
    async def create_subscription(
        self,
        plan_id: str,
        subscriber_email: str,
        subscriber_name: str,
        return_url: str = None,
        cancel_url: str = None
    ) -> PayPalSubscriptionResult:
        """Create a subscription"""
        try:
            subscription_data = {
                "plan_id": plan_id,
                "subscriber": {
                    "email_address": subscriber_email,
                    "name": {
                        "given_name": subscriber_name.split()[0],
                        "surname": " ".join(subscriber_name.split()[1:]) if len(subscriber_name.split()) > 1 else ""
                    }
                },
                "application_context": {
                    "brand_name": "FinClick.AI",
                    "locale": "en-US",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "SUBSCRIBE_NOW",
                    "payment_method": {
                        "payer_selected": "PAYPAL",
                        "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                    },
                    "return_url": return_url or "https://finclick.ai/subscription/success",
                    "cancel_url": cancel_url or "https://finclick.ai/subscription/cancel"
                }
            }

            response = await self._make_request('POST', '/v1/billing/subscriptions', subscription_data)

            approval_url = None
            for link in response.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break

            logger.info(f"Created PayPal subscription: {response.get('id')}")
            return PayPalSubscriptionResult(
                success=True,
                subscription_id=response.get('id'),
                approval_url=approval_url,
                status=response.get('status'),
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Failed to create PayPal subscription: {str(e)}")
            return PayPalSubscriptionResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_paypal_error()
    async def cancel_subscription(self, subscription_id: str, reason: str = "User requested cancellation") -> Dict:
        """Cancel a subscription"""
        try:
            cancel_data = {
                "reason": reason
            }

            response = await self._make_request(
                'POST',
                f'/v1/billing/subscriptions/{subscription_id}/cancel',
                cancel_data
            )

            logger.info(f"Canceled PayPal subscription: {subscription_id}")
            return {
                'success': True,
                'response': response
            }

        except Exception as e:
            logger.error(f"Failed to cancel PayPal subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paypal_error()
    async def get_subscription_details(self, subscription_id: str) -> Dict:
        """Get subscription details"""
        try:
            response = await self._make_request('GET', f'/v1/billing/subscriptions/{subscription_id}')

            return {
                'success': True,
                'subscription': response
            }

        except Exception as e:
            logger.error(f"Failed to get PayPal subscription details: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paypal_error()
    async def suspend_subscription(self, subscription_id: str, reason: str = "Temporary suspension") -> Dict:
        """Suspend a subscription"""
        try:
            suspend_data = {
                "reason": reason
            }

            response = await self._make_request(
                'POST',
                f'/v1/billing/subscriptions/{subscription_id}/suspend',
                suspend_data
            )

            logger.info(f"Suspended PayPal subscription: {subscription_id}")
            return {
                'success': True,
                'response': response
            }

        except Exception as e:
            logger.error(f"Failed to suspend PayPal subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paypal_error()
    async def activate_subscription(self, subscription_id: str, reason: str = "Reactivation") -> Dict:
        """Activate a suspended subscription"""
        try:
            activate_data = {
                "reason": reason
            }

            response = await self._make_request(
                'POST',
                f'/v1/billing/subscriptions/{subscription_id}/activate',
                activate_data
            )

            logger.info(f"Activated PayPal subscription: {subscription_id}")
            return {
                'success': True,
                'response': response
            }

        except Exception as e:
            logger.error(f"Failed to activate PayPal subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def verify_webhook_signature(self, headers: Dict, body: str, webhook_id: str) -> bool:
        """Verify PayPal webhook signature"""
        try:
            # PayPal webhook verification requires specific implementation
            # This is a simplified version - in production, implement full verification
            auth_algo = headers.get('PAYPAL-AUTH-ALGO')
            transmission_id = headers.get('PAYPAL-TRANSMISSION-ID')
            cert_id = headers.get('PAYPAL-CERT-ID')
            transmission_sig = headers.get('PAYPAL-TRANSMISSION-SIG')
            transmission_time = headers.get('PAYPAL-TRANSMISSION-TIME')

            if not all([auth_algo, transmission_id, cert_id, transmission_sig, transmission_time]):
                logger.error("Missing required PayPal webhook headers")
                return False

            # In production, implement full signature verification
            # For now, return True if all headers are present
            return True

        except Exception as e:
            logger.error(f"Error verifying PayPal webhook signature: {str(e)}")
            return False

    async def handle_webhook_event(self, event: Dict) -> Dict:
        """Handle incoming PayPal webhook events"""
        event_type = event.get('event_type')
        logger.info(f"Handling PayPal webhook event: {event_type}")

        try:
            if event_type == 'PAYMENT.SALE.COMPLETED':
                return await self._handle_payment_completed(event)
            elif event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
                return await self._handle_subscription_activated(event)
            elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
                return await self._handle_subscription_cancelled(event)
            elif event_type == 'BILLING.SUBSCRIPTION.PAYMENT.FAILED':
                return await self._handle_subscription_payment_failed(event)
            elif event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
                return await self._handle_subscription_suspended(event)
            else:
                logger.info(f"Unhandled PayPal event type: {event_type}")
                return {'success': True, 'message': f'Event {event_type} received but not handled'}

        except Exception as e:
            logger.error(f"Error handling PayPal webhook event {event_type}: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _handle_payment_completed(self, event: Dict) -> Dict:
        """Handle completed payment"""
        payment_id = event.get('resource', {}).get('parent_payment')
        logger.info(f"PayPal payment completed: {payment_id}")
        # Add your business logic here
        return {'success': True, 'message': 'Payment completed successfully'}

    async def _handle_subscription_activated(self, event: Dict) -> Dict:
        """Handle subscription activation"""
        subscription_id = event.get('resource', {}).get('id')
        logger.info(f"PayPal subscription activated: {subscription_id}")
        # Add your business logic here
        return {'success': True, 'message': 'Subscription activated successfully'}

    async def _handle_subscription_cancelled(self, event: Dict) -> Dict:
        """Handle subscription cancellation"""
        subscription_id = event.get('resource', {}).get('id')
        logger.info(f"PayPal subscription cancelled: {subscription_id}")
        # Add your business logic here
        return {'success': True, 'message': 'Subscription cancellation processed'}

    async def _handle_subscription_payment_failed(self, event: Dict) -> Dict:
        """Handle subscription payment failure"""
        subscription_id = event.get('resource', {}).get('id')
        logger.warning(f"PayPal subscription payment failed: {subscription_id}")
        # Add your business logic here
        return {'success': True, 'message': 'Subscription payment failure processed'}

    async def _handle_subscription_suspended(self, event: Dict) -> Dict:
        """Handle subscription suspension"""
        subscription_id = event.get('resource', {}).get('id')
        logger.info(f"PayPal subscription suspended: {subscription_id}")
        # Add your business logic here
        return {'success': True, 'message': 'Subscription suspension processed'}

# Utility functions
async def create_paypal_service(
    client_id: str,
    client_secret: str,
    environment: PayPalEnvironment = PayPalEnvironment.SANDBOX
) -> PayPalService:
    """Factory function to create PayPalService instance"""
    return PayPalService(client_id, client_secret, environment)