"""
PayTabs Payment Gateway Service
Handles PayTabs payments for MENA region for FinClick.AI platform
"""

import aiohttp
import hashlib
import hmac
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import time

# Configure logging
logger = logging.getLogger(__name__)

class PayTabsEnvironment(Enum):
    SANDBOX = "sandbox"
    LIVE = "live"

class PaymentStatus(Enum):
    PENDING = "P"
    SUCCESS = "A"
    FAILED = "F"
    HOLD = "H"
    CANCELLED = "C"

@dataclass
class PayTabsPaymentResult:
    success: bool
    transaction_id: Optional[str] = None
    payment_url: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None

def retry_on_paytabs_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry PayTabs API calls on specific errors"""
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
                        logger.warning(f"PayTabs API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class PayTabsService:
    """Comprehensive PayTabs payment service for MENA region - FinClick.AI"""

    def __init__(self, profile_id: str, server_key: str, environment: PayTabsEnvironment = PayTabsEnvironment.SANDBOX):
        self.profile_id = profile_id
        self.server_key = server_key
        self.environment = environment

        if environment == PayTabsEnvironment.SANDBOX:
            self.base_url = "https://secure.paytabs.com"
        else:
            self.base_url = "https://secure.paytabs.com"

        # Rate limiting
        self.rate_limit_delay = 0.3  # 300ms between requests
        self.last_request_time = 0

        logger.info(f"PayTabs service initialized for {environment.value} environment")

    async def _rate_limit_check(self):
        """Ensure we don't exceed PayTabs rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _generate_signature(self, data: Dict) -> str:
        """Generate PayTabs signature for request validation"""
        # Sort the data alphabetically by keys
        sorted_data = dict(sorted(data.items()))

        # Create the string to sign
        sign_string = ""
        for key, value in sorted_data.items():
            if value is not None and value != "":
                sign_string += f"{key}={value}"

        # Generate HMAC SHA256 signature
        signature = hmac.new(
            self.server_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()

        return signature

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make authenticated request to PayTabs API"""
        await self._rate_limit_check()

        # Add required fields
        data['profile_id'] = self.profile_id

        # Generate signature
        signature = self._generate_signature(data)
        data['signature'] = signature

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.server_key
        }

        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict:
        """Handle PayTabs API response"""
        response_text = await response.text()

        try:
            response_data = json.loads(response_text) if response_text else {}
        except json.JSONDecodeError:
            response_data = {'raw_response': response_text}

        if response.status in [200, 201]:
            return response_data
        else:
            logger.error(f"PayTabs API error {response.status}: {response_text}")
            raise Exception(f"PayTabs API error {response.status}: {response_data.get('result', response_text)}")

    @retry_on_paytabs_error()
    async def create_payment_page(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_details: Dict,
        return_url: str,
        callback_url: str = None,
        description: str = "Payment for FinClick.AI services"
    ) -> PayTabsPaymentResult:
        """Create a payment page for one-time payments"""
        try:
            payment_data = {
                "tran_type": "sale",
                "tran_class": "ecom",
                "cart_id": order_id,
                "cart_description": description,
                "cart_currency": currency,
                "cart_amount": amount,
                "callback": callback_url or return_url,
                "return": return_url,
                "customer_details": {
                    "name": customer_details.get('name', ''),
                    "email": customer_details.get('email', ''),
                    "phone": customer_details.get('phone', ''),
                    "street1": customer_details.get('address', ''),
                    "city": customer_details.get('city', ''),
                    "state": customer_details.get('state', ''),
                    "country": customer_details.get('country', 'SA'),  # Default to Saudi Arabia
                    "zip": customer_details.get('zip', '')
                },
                "shipping_details": {
                    "name": customer_details.get('name', ''),
                    "email": customer_details.get('email', ''),
                    "phone": customer_details.get('phone', ''),
                    "street1": customer_details.get('address', ''),
                    "city": customer_details.get('city', ''),
                    "state": customer_details.get('state', ''),
                    "country": customer_details.get('country', 'SA'),
                    "zip": customer_details.get('zip', '')
                },
                "user_defined": {
                    "udf1": "FinClick.AI",
                    "udf2": customer_details.get('user_id', ''),
                    "udf3": datetime.now().isoformat()
                }
            }

            response = await self._make_request('/payment/request', payment_data)

            payment_url = response.get('redirect_url')
            transaction_ref = response.get('tran_ref')

            logger.info(f"Created PayTabs payment page: {transaction_ref}")
            return PayTabsPaymentResult(
                success=True,
                transaction_id=transaction_ref,
                payment_url=payment_url,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Failed to create PayTabs payment page: {str(e)}")
            return PayTabsPaymentResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_paytabs_error()
    async def verify_payment(self, transaction_ref: str) -> Dict:
        """Verify payment status"""
        try:
            verify_data = {
                "tran_ref": transaction_ref
            }

            response = await self._make_request('/payment/query', verify_data)

            payment_result = response.get('payment_result', {})
            response_status = payment_result.get('response_status')
            response_code = payment_result.get('response_code')

            logger.info(f"Verified PayTabs payment: {transaction_ref}, Status: {response_status}")
            return {
                'success': True,
                'status': response_status,
                'response_code': response_code,
                'transaction_ref': transaction_ref,
                'response': response
            }

        except Exception as e:
            logger.error(f"Failed to verify PayTabs payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paytabs_error()
    async def create_recurring_payment(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_details: Dict,
        token: str,
        description: str = "Recurring payment for FinClick.AI services"
    ) -> PayTabsPaymentResult:
        """Create a recurring payment using saved token"""
        try:
            payment_data = {
                "tran_type": "sale",
                "tran_class": "recurring",
                "cart_id": order_id,
                "cart_description": description,
                "cart_currency": currency,
                "cart_amount": amount,
                "token": token,
                "customer_details": {
                    "name": customer_details.get('name', ''),
                    "email": customer_details.get('email', ''),
                    "phone": customer_details.get('phone', ''),
                    "street1": customer_details.get('address', ''),
                    "city": customer_details.get('city', ''),
                    "state": customer_details.get('state', ''),
                    "country": customer_details.get('country', 'SA'),
                    "zip": customer_details.get('zip', '')
                }
            }

            response = await self._make_request('/payment/request', payment_data)

            transaction_ref = response.get('tran_ref')
            payment_result = response.get('payment_result', {})
            response_status = payment_result.get('response_status')

            logger.info(f"Created PayTabs recurring payment: {transaction_ref}")
            return PayTabsPaymentResult(
                success=True,
                transaction_id=transaction_ref,
                status=response_status,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Failed to create PayTabs recurring payment: {str(e)}")
            return PayTabsPaymentResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_paytabs_error()
    async def create_token(
        self,
        customer_details: Dict,
        return_url: str,
        callback_url: str = None
    ) -> Dict:
        """Create a payment token for future recurring payments"""
        try:
            token_data = {
                "tran_type": "register",
                "tran_class": "recurring",
                "cart_id": f"token_{int(time.time())}",
                "cart_description": "Token creation for recurring payments",
                "cart_currency": "SAR",
                "cart_amount": 0,
                "callback": callback_url or return_url,
                "return": return_url,
                "customer_details": {
                    "name": customer_details.get('name', ''),
                    "email": customer_details.get('email', ''),
                    "phone": customer_details.get('phone', ''),
                    "street1": customer_details.get('address', ''),
                    "city": customer_details.get('city', ''),
                    "state": customer_details.get('state', ''),
                    "country": customer_details.get('country', 'SA'),
                    "zip": customer_details.get('zip', '')
                }
            }

            response = await self._make_request('/payment/request', token_data)

            token_url = response.get('redirect_url')
            transaction_ref = response.get('tran_ref')

            logger.info(f"Created PayTabs token request: {transaction_ref}")
            return {
                'success': True,
                'transaction_ref': transaction_ref,
                'token_url': token_url,
                'response': response
            }

        except Exception as e:
            logger.error(f"Failed to create PayTabs token: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @retry_on_paytabs_error()
    async def refund_payment(self, transaction_ref: str, amount: float, reason: str = "Customer request") -> Dict:
        """Refund a payment"""
        try:
            refund_data = {
                "tran_type": "refund",
                "tran_class": "ecom",
                "tran_ref": transaction_ref,
                "cart_id": f"refund_{int(time.time())}",
                "cart_description": f"Refund: {reason}",
                "cart_amount": amount
            }

            response = await self._make_request('/payment/request', refund_data)

            refund_ref = response.get('tran_ref')
            payment_result = response.get('payment_result', {})
            response_status = payment_result.get('response_status')

            logger.info(f"Created PayTabs refund: {refund_ref}")
            return {
                'success': True,
                'refund_ref': refund_ref,
                'status': response_status,
                'response': response
            }

        except Exception as e:
            logger.error(f"Failed to create PayTabs refund: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def verify_callback_signature(self, data: Dict, signature: str) -> bool:
        """Verify PayTabs callback signature"""
        try:
            # Generate expected signature
            expected_signature = self._generate_signature(data)

            # Compare signatures
            is_valid = hmac.compare_digest(expected_signature, signature.upper())

            if not is_valid:
                logger.error("PayTabs callback signature verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying PayTabs callback signature: {str(e)}")
            return False

    async def handle_callback(self, callback_data: Dict) -> Dict:
        """Handle PayTabs payment callback"""
        try:
            transaction_ref = callback_data.get('tranRef')
            response_code = callback_data.get('respCode')
            response_status = callback_data.get('respStatus')
            response_message = callback_data.get('respMessage')

            logger.info(f"Handling PayTabs callback for transaction: {transaction_ref}")

            # Verify payment status
            verification = await self.verify_payment(transaction_ref)

            if verification['success']:
                if response_status == 'A':  # Approved
                    return await self._handle_payment_success(callback_data)
                elif response_status in ['F', 'C']:  # Failed or Cancelled
                    return await self._handle_payment_failure(callback_data)
                elif response_status == 'H':  # Hold
                    return await self._handle_payment_hold(callback_data)
                elif response_status == 'P':  # Pending
                    return await self._handle_payment_pending(callback_data)

            return {
                'success': True,
                'status': response_status,
                'message': response_message
            }

        except Exception as e:
            logger.error(f"Error handling PayTabs callback: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _handle_payment_success(self, callback_data: Dict) -> Dict:
        """Handle successful payment callback"""
        transaction_ref = callback_data.get('tranRef')
        logger.info(f"PayTabs payment successful: {transaction_ref}")
        # Add your business logic here
        return {
            'success': True,
            'status': 'success',
            'message': 'Payment processed successfully'
        }

    async def _handle_payment_failure(self, callback_data: Dict) -> Dict:
        """Handle failed payment callback"""
        transaction_ref = callback_data.get('tranRef')
        logger.warning(f"PayTabs payment failed: {transaction_ref}")
        # Add your business logic here
        return {
            'success': True,
            'status': 'failed',
            'message': 'Payment failed'
        }

    async def _handle_payment_hold(self, callback_data: Dict) -> Dict:
        """Handle payment on hold callback"""
        transaction_ref = callback_data.get('tranRef')
        logger.info(f"PayTabs payment on hold: {transaction_ref}")
        # Add your business logic here
        return {
            'success': True,
            'status': 'hold',
            'message': 'Payment on hold for review'
        }

    async def _handle_payment_pending(self, callback_data: Dict) -> Dict:
        """Handle pending payment callback"""
        transaction_ref = callback_data.get('tranRef')
        logger.info(f"PayTabs payment pending: {transaction_ref}")
        # Add your business logic here
        return {
            'success': True,
            'status': 'pending',
            'message': 'Payment is pending'
        }

    @retry_on_paytabs_error()
    async def get_transaction_details(self, transaction_ref: str) -> Dict:
        """Get detailed transaction information"""
        try:
            query_data = {
                "tran_ref": transaction_ref
            }

            response = await self._make_request('/payment/query', query_data)

            logger.info(f"Retrieved PayTabs transaction details: {transaction_ref}")
            return {
                'success': True,
                'transaction': response
            }

        except Exception as e:
            logger.error(f"Failed to get PayTabs transaction details: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return [
            'SAR',  # Saudi Riyal
            'AED',  # UAE Dirham
            'KWD',  # Kuwaiti Dinar
            'BHD',  # Bahraini Dinar
            'QAR',  # Qatari Riyal
            'OMR',  # Omani Rial
            'JOD',  # Jordanian Dinar
            'EGP',  # Egyptian Pound
            'USD',  # US Dollar
            'EUR',  # Euro
            'GBP'   # British Pound
        ]

    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries"""
        return [
            'SA',  # Saudi Arabia
            'AE',  # UAE
            'KW',  # Kuwait
            'BH',  # Bahrain
            'QA',  # Qatar
            'OM',  # Oman
            'JO',  # Jordan
            'EG',  # Egypt
            'LB',  # Lebanon
            'IQ',  # Iraq
            'MA',  # Morocco
            'TN',  # Tunisia
            'DZ',  # Algeria
            'LY'   # Libya
        ]

# Utility functions
async def create_paytabs_service(
    profile_id: str,
    server_key: str,
    environment: PayTabsEnvironment = PayTabsEnvironment.SANDBOX
) -> PayTabsService:
    """Factory function to create PayTabsService instance"""
    return PayTabsService(profile_id, server_key, environment)

def format_phone_number(phone: str, country_code: str = '+966') -> str:
    """Format phone number for PayTabs"""
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone))

    # Add country code if not present
    if not phone.startswith(country_code.replace('+', '')):
        phone = country_code.replace('+', '') + phone

    return phone