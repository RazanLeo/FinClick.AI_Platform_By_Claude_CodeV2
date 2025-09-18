"""
Twilio SMS and Communication Service
Handles SMS notifications and voice communications for FinClick.AI platform
"""

import aiohttp
import asyncio
import logging
import json
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import urllib.parse

# Configure logging
logger = logging.getLogger(__name__)

class MessageStatus(Enum):
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    UNDELIVERED = "undelivered"
    FAILED = "failed"
    RECEIVED = "received"

class MessageDirection(Enum):
    INBOUND = "inbound"
    OUTBOUND_API = "outbound-api"
    OUTBOUND_CALL = "outbound-call"
    OUTBOUND_REPLY = "outbound-reply"

class CallStatus(Enum):
    QUEUED = "queued"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BUSY = "busy"
    FAILED = "failed"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"

class SMSType(Enum):
    VERIFICATION = "verification"
    ALERT = "alert"
    NOTIFICATION = "notification"
    MARKETING = "marketing"
    REMINDER = "reminder"
    SECURITY = "security"

@dataclass
class SMSResult:
    success: bool
    message_sid: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[int] = None

@dataclass
class CallResult:
    success: bool
    call_sid: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[int] = None

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry API calls on specific errors"""
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
                        logger.warning(f"Twilio API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class TwilioService:
    """Comprehensive Twilio communication service for FinClick.AI"""

    def __init__(self, account_sid: str, auth_token: str, from_phone: str, from_name: str = "FinClick.AI"):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_phone = from_phone
        self.from_name = from_name
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}"

        # Rate limiting
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0

        # SMS templates
        self.sms_templates = {
            SMSType.VERIFICATION: "Your FinClick.AI verification code is: {code}. Valid for {minutes} minutes.",
            SMSType.ALERT: "FinClick.AI Alert: {message}",
            SMSType.NOTIFICATION: "FinClick.AI: {message}",
            SMSType.MARKETING: "FinClick.AI: {message}. Reply STOP to unsubscribe.",
            SMSType.REMINDER: "Reminder from FinClick.AI: {message}",
            SMSType.SECURITY: "FinClick.AI Security Alert: {message}. If this wasn't you, contact support immediately."
        }

        logger.info("Twilio service initialized")

    async def _rate_limit_check(self):
        """Ensure we don't exceed Twilio rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _create_auth_header(self) -> str:
        """Create authentication header for Twilio API"""
        auth_string = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"

    async def _make_request(self, endpoint: str, data: Dict = None, method: str = 'POST') -> Dict:
        """Make request to Twilio API"""
        await self._rate_limit_check()

        headers = {
            'Authorization': self._create_auth_header(),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        url = f"{self.base_url}/{endpoint}"

        # Convert data to URL-encoded format
        if data:
            form_data = urllib.parse.urlencode(data)
        else:
            form_data = ""

        async with aiohttp.ClientSession() as session:
            if method.upper() == 'POST':
                async with session.post(url, headers=headers, data=form_data) as response:
                    return await self._handle_response(response)
            elif method.upper() == 'GET':
                async with session.get(url, headers=headers, params=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == 'DELETE':
                async with session.delete(url, headers=headers, data=form_data) as response:
                    return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict:
        """Handle Twilio API response"""
        response_text = await response.text()

        try:
            response_data = json.loads(response_text) if response_text else {}
        except json.JSONDecodeError:
            response_data = {'raw_response': response_text}

        if response.status in [200, 201]:
            return response_data
        else:
            logger.error(f"Twilio API error {response.status}: {response_text}")
            error_message = response_data.get('message', 'Unknown error')
            error_code = response_data.get('code', response.status)
            raise Exception(f"Twilio API error {error_code}: {error_message}")

    @retry_on_error()
    async def send_sms(
        self,
        to_phone: str,
        message: str,
        from_phone: str = None,
        media_url: List[str] = None,
        messaging_service_sid: str = None,
        status_callback: str = None,
        max_price: str = None,
        attempt: int = None,
        validity_period: int = None
    ) -> SMSResult:
        """Send SMS message"""
        try:
            # Clean phone numbers (remove non-digits except +)
            to_phone = self._format_phone_number(to_phone)
            if from_phone:
                from_phone = self._format_phone_number(from_phone)

            sms_data = {
                'To': to_phone,
                'Body': message
            }

            # Use messaging service or from number
            if messaging_service_sid:
                sms_data['MessagingServiceSid'] = messaging_service_sid
            else:
                sms_data['From'] = from_phone or self.from_phone

            # Optional parameters
            if media_url:
                sms_data['MediaUrl'] = media_url

            if status_callback:
                sms_data['StatusCallback'] = status_callback

            if max_price:
                sms_data['MaxPrice'] = max_price

            if attempt:
                sms_data['Attempt'] = attempt

            if validity_period:
                sms_data['ValidityPeriod'] = validity_period

            response = await self._make_request('Messages.json', sms_data)

            logger.info(f"SMS sent successfully: {response.get('sid')}")
            return SMSResult(
                success=True,
                message_sid=response.get('sid'),
                status=response.get('status')
            )

        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            error_parts = str(e).split(':')
            error_code = None
            if len(error_parts) > 1 and error_parts[1].strip().isdigit():
                error_code = int(error_parts[1].strip())

            return SMSResult(
                success=False,
                error_message=str(e),
                error_code=error_code
            )

    @retry_on_error()
    async def send_template_sms(
        self,
        sms_type: SMSType,
        to_phone: str,
        template_data: Dict,
        from_phone: str = None
    ) -> SMSResult:
        """Send SMS using predefined template"""
        try:
            if sms_type not in self.sms_templates:
                raise ValueError(f"Unknown SMS type: {sms_type}")

            template = self.sms_templates[sms_type]
            message = template.format(**template_data)

            return await self.send_sms(
                to_phone=to_phone,
                message=message,
                from_phone=from_phone
            )

        except Exception as e:
            logger.error(f"Failed to send template SMS: {str(e)}")
            return SMSResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_error()
    async def send_verification_code(
        self,
        to_phone: str,
        code: str,
        validity_minutes: int = 10,
        from_phone: str = None
    ) -> SMSResult:
        """Send verification code SMS"""
        return await self.send_template_sms(
            sms_type=SMSType.VERIFICATION,
            to_phone=to_phone,
            template_data={
                'code': code,
                'minutes': validity_minutes
            },
            from_phone=from_phone
        )

    @retry_on_error()
    async def send_bulk_sms(
        self,
        recipients: List[Dict],
        message: str = None,
        template_data: Dict = None,
        batch_size: int = 100
    ) -> List[SMSResult]:
        """Send bulk SMS messages"""
        results = []

        try:
            # Split recipients into batches
            for i in range(0, len(recipients), batch_size):
                batch = recipients[i:i + batch_size]

                # Send messages in batch
                batch_tasks = []
                for recipient in batch:
                    phone = recipient['phone']
                    recipient_message = message

                    # Apply personalization if template data provided
                    if template_data and 'personalization' in recipient:
                        recipient_template_data = {**template_data, **recipient['personalization']}
                        recipient_message = message.format(**recipient_template_data)

                    task = self.send_sms(
                        to_phone=phone,
                        message=recipient_message,
                        from_phone=recipient.get('from_phone')
                    )
                    batch_tasks.append(task)

                # Wait for batch to complete
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, Exception):
                        results.append(SMSResult(
                            success=False,
                            error_message=str(result)
                        ))
                    else:
                        results.append(result)

                # Add delay between batches
                if i + batch_size < len(recipients):
                    await asyncio.sleep(1)

            logger.info(f"Sent bulk SMS to {len(recipients)} recipients")
            return results

        except Exception as e:
            logger.error(f"Failed to send bulk SMS: {str(e)}")
            results.append(SMSResult(
                success=False,
                error_message=str(e)
            ))
            return results

    @retry_on_error()
    async def get_message_status(self, message_sid: str) -> Dict:
        """Get message status"""
        try:
            response = await self._make_request(f'Messages/{message_sid}.json', method='GET')

            logger.info(f"Retrieved message status for {message_sid}")
            return response

        except Exception as e:
            logger.error(f"Failed to get message status: {str(e)}")
            raise

    @retry_on_error()
    async def get_messages(
        self,
        to_phone: str = None,
        from_phone: str = None,
        date_sent: datetime = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get messages"""
        try:
            params = {
                'PageSize': limit
            }

            if to_phone:
                params['To'] = self._format_phone_number(to_phone)

            if from_phone:
                params['From'] = self._format_phone_number(from_phone)

            if date_sent:
                params['DateSent'] = date_sent.strftime('%Y-%m-%d')

            response = await self._make_request('Messages.json', params, method='GET')

            messages = response.get('messages', [])
            logger.info(f"Retrieved {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"Failed to get messages: {str(e)}")
            raise

    @retry_on_error()
    async def make_call(
        self,
        to_phone: str,
        twiml_url: str = None,
        twiml: str = None,
        from_phone: str = None,
        status_callback: str = None,
        timeout: int = 60,
        record: bool = False
    ) -> CallResult:
        """Make a phone call"""
        try:
            to_phone = self._format_phone_number(to_phone)
            if from_phone:
                from_phone = self._format_phone_number(from_phone)

            call_data = {
                'To': to_phone,
                'From': from_phone or self.from_phone,
                'Timeout': timeout
            }

            # Add TwiML URL or inline TwiML
            if twiml_url:
                call_data['Url'] = twiml_url
            elif twiml:
                call_data['Twiml'] = twiml
            else:
                # Default TwiML for basic call
                call_data['Twiml'] = '<Response><Say>Hello from FinClick.AI</Say></Response>'

            if status_callback:
                call_data['StatusCallback'] = status_callback

            if record:
                call_data['Record'] = 'true'

            response = await self._make_request('Calls.json', call_data)

            logger.info(f"Call initiated successfully: {response.get('sid')}")
            return CallResult(
                success=True,
                call_sid=response.get('sid'),
                status=response.get('status')
            )

        except Exception as e:
            logger.error(f"Failed to make call: {str(e)}")
            error_parts = str(e).split(':')
            error_code = None
            if len(error_parts) > 1 and error_parts[1].strip().isdigit():
                error_code = int(error_parts[1].strip())

            return CallResult(
                success=False,
                error_message=str(e),
                error_code=error_code
            )

    @retry_on_error()
    async def get_call_status(self, call_sid: str) -> Dict:
        """Get call status"""
        try:
            response = await self._make_request(f'Calls/{call_sid}.json', method='GET')

            logger.info(f"Retrieved call status for {call_sid}")
            return response

        except Exception as e:
            logger.error(f"Failed to get call status: {str(e)}")
            raise

    @retry_on_error()
    async def end_call(self, call_sid: str) -> Dict:
        """End an active call"""
        try:
            call_data = {
                'Status': 'completed'
            }

            response = await self._make_request(f'Calls/{call_sid}.json', call_data)

            logger.info(f"Call ended: {call_sid}")
            return response

        except Exception as e:
            logger.error(f"Failed to end call: {str(e)}")
            raise

    @retry_on_error()
    async def lookup_phone_number(self, phone_number: str) -> Dict:
        """Lookup phone number information"""
        try:
            phone_number = self._format_phone_number(phone_number)
            lookup_url = f"https://lookups.twilio.com/v1/PhoneNumbers/{phone_number}"

            headers = {
                'Authorization': self._create_auth_header(),
                'Accept': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(lookup_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Phone number lookup successful: {phone_number}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Phone lookup error {response.status}: {error_text}")
                        raise Exception(f"Phone lookup error {response.status}: {error_text}")

        except Exception as e:
            logger.error(f"Failed to lookup phone number: {str(e)}")
            raise

    async def handle_webhook_event(self, event_data: Dict) -> Dict:
        """Handle incoming Twilio webhook events"""
        try:
            message_status = event_data.get('MessageStatus')
            sms_status = event_data.get('SmsStatus')
            call_status = event_data.get('CallStatus')

            if message_status or sms_status:
                return await self._handle_sms_webhook(event_data)
            elif call_status:
                return await self._handle_call_webhook(event_data)
            else:
                logger.info("Unknown webhook event type")
                return {'success': True, 'message': 'Webhook received but not handled'}

        except Exception as e:
            logger.error(f"Error handling Twilio webhook: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _handle_sms_webhook(self, event_data: Dict) -> Dict:
        """Handle SMS webhook event"""
        message_sid = event_data.get('MessageSid')
        status = event_data.get('MessageStatus') or event_data.get('SmsStatus')
        to_phone = event_data.get('To')
        from_phone = event_data.get('From')

        logger.info(f"SMS webhook - SID: {message_sid}, Status: {status}")

        if status == 'delivered':
            return await self._handle_sms_delivered(event_data)
        elif status == 'failed':
            return await self._handle_sms_failed(event_data)
        elif status == 'undelivered':
            return await self._handle_sms_undelivered(event_data)
        else:
            return {'success': True, 'message': f'SMS status {status} processed'}

    async def _handle_call_webhook(self, event_data: Dict) -> Dict:
        """Handle call webhook event"""
        call_sid = event_data.get('CallSid')
        status = event_data.get('CallStatus')
        to_phone = event_data.get('To')
        from_phone = event_data.get('From')

        logger.info(f"Call webhook - SID: {call_sid}, Status: {status}")

        if status == 'completed':
            return await self._handle_call_completed(event_data)
        elif status == 'failed':
            return await self._handle_call_failed(event_data)
        elif status == 'no-answer':
            return await self._handle_call_no_answer(event_data)
        else:
            return {'success': True, 'message': f'Call status {status} processed'}

    async def _handle_sms_delivered(self, event_data: Dict) -> Dict:
        """Handle SMS delivered event"""
        message_sid = event_data.get('MessageSid')
        logger.info(f"SMS delivered: {message_sid}")
        # Add your business logic here
        return {'success': True, 'message': 'SMS delivered event processed'}

    async def _handle_sms_failed(self, event_data: Dict) -> Dict:
        """Handle SMS failed event"""
        message_sid = event_data.get('MessageSid')
        error_code = event_data.get('ErrorCode')
        logger.warning(f"SMS failed: {message_sid}, Error: {error_code}")
        # Add your business logic here
        return {'success': True, 'message': 'SMS failed event processed'}

    async def _handle_sms_undelivered(self, event_data: Dict) -> Dict:
        """Handle SMS undelivered event"""
        message_sid = event_data.get('MessageSid')
        logger.warning(f"SMS undelivered: {message_sid}")
        # Add your business logic here
        return {'success': True, 'message': 'SMS undelivered event processed'}

    async def _handle_call_completed(self, event_data: Dict) -> Dict:
        """Handle call completed event"""
        call_sid = event_data.get('CallSid')
        duration = event_data.get('CallDuration', 0)
        logger.info(f"Call completed: {call_sid}, Duration: {duration}s")
        # Add your business logic here
        return {'success': True, 'message': 'Call completed event processed'}

    async def _handle_call_failed(self, event_data: Dict) -> Dict:
        """Handle call failed event"""
        call_sid = event_data.get('CallSid')
        logger.warning(f"Call failed: {call_sid}")
        # Add your business logic here
        return {'success': True, 'message': 'Call failed event processed'}

    async def _handle_call_no_answer(self, event_data: Dict) -> Dict:
        """Handle call no answer event"""
        call_sid = event_data.get('CallSid')
        logger.info(f"Call no answer: {call_sid}")
        # Add your business logic here
        return {'success': True, 'message': 'Call no answer event processed'}

    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for Twilio"""
        # Remove all non-digit characters except +
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

        # Add + if not present and number is long enough
        if not clean_phone.startswith('+') and len(clean_phone) >= 10:
            clean_phone = '+' + clean_phone

        return clean_phone

    def generate_twiml_response(self, actions: List[Dict]) -> str:
        """Generate TwiML response for voice calls"""
        twiml_parts = ['<Response>']

        for action in actions:
            action_type = action.get('type')

            if action_type == 'say':
                text = action.get('text', '')
                voice = action.get('voice', 'alice')
                language = action.get('language', 'en')
                twiml_parts.append(f'<Say voice="{voice}" language="{language}">{text}</Say>')

            elif action_type == 'play':
                url = action.get('url', '')
                twiml_parts.append(f'<Play>{url}</Play>')

            elif action_type == 'gather':
                input_type = action.get('input', 'dtmf')
                action_url = action.get('action', '')
                method = action.get('method', 'POST')
                timeout = action.get('timeout', 5)
                twiml_parts.append(f'<Gather input="{input_type}" action="{action_url}" method="{method}" timeout="{timeout}">')

                # Add nested say or play
                if 'say' in action:
                    twiml_parts.append(f'<Say>{action["say"]}</Say>')

                twiml_parts.append('</Gather>')

            elif action_type == 'record':
                action_url = action.get('action', '')
                max_length = action.get('max_length', 60)
                twiml_parts.append(f'<Record action="{action_url}" maxLength="{max_length}"/>')

            elif action_type == 'dial':
                number = action.get('number', '')
                timeout = action.get('timeout', 30)
                twiml_parts.append(f'<Dial timeout="{timeout}">{number}</Dial>')

            elif action_type == 'hangup':
                twiml_parts.append('<Hangup/>')

        twiml_parts.append('</Response>')
        return ''.join(twiml_parts)

# Utility functions
async def create_twilio_service(
    account_sid: str,
    auth_token: str,
    from_phone: str,
    from_name: str = "FinClick.AI"
) -> TwilioService:
    """Factory function to create TwilioService instance"""
    return TwilioService(account_sid, auth_token, from_phone, from_name)

def create_verification_code() -> str:
    """Generate a 6-digit verification code"""
    import random
    return str(random.randint(100000, 999999))

def validate_phone_number(phone: str) -> bool:
    """Basic phone number validation"""
    # Remove non-digit characters except +
    clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

    # Check length and format
    if clean_phone.startswith('+'):
        return len(clean_phone) >= 11  # +1xxxxxxxxxx minimum
    else:
        return len(clean_phone) >= 10  # xxxxxxxxxx minimum

def format_phone_for_display(phone: str, country_code: str = 'US') -> str:
    """Format phone number for display"""
    # Remove all non-digit characters except +
    clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

    if country_code == 'US' and len(clean_phone) == 11 and clean_phone.startswith('+1'):
        # US format: +1 (XXX) XXX-XXXX
        digits = clean_phone[2:]  # Remove +1
        return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif country_code == 'US' and len(clean_phone) == 10:
        # US format without country code: (XXX) XXX-XXXX
        return f"({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}"
    else:
        return clean_phone