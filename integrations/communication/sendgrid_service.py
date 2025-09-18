"""
SendGrid Email Service
Handles transactional emails for FinClick.AI platform
"""

import aiohttp
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import base64

# Configure logging
logger = logging.getLogger(__name__)

class EmailType(Enum):
    WELCOME = "welcome"
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    SUBSCRIPTION_CONFIRMATION = "subscription_confirmation"
    PAYMENT_RECEIPT = "payment_receipt"
    ACCOUNT_UPDATE = "account_update"
    NEWSLETTER = "newsletter"
    ALERT = "alert"
    REPORT = "report"

class Priority(Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

@dataclass
class EmailRecipient:
    email: str
    name: Optional[str] = None
    substitutions: Optional[Dict[str, str]] = None

@dataclass
class EmailAttachment:
    content: str  # Base64 encoded content
    filename: str
    type: str  # MIME type
    disposition: str = "attachment"
    content_id: Optional[str] = None

@dataclass
class EmailResult:
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None

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
                        logger.warning(f"SendGrid API error, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class SendGridService:
    """Comprehensive SendGrid email service for FinClick.AI"""

    def __init__(self, api_key: str, default_from_email: str, default_from_name: str = "FinClick.AI"):
        self.api_key = api_key
        self.default_from_email = default_from_email
        self.default_from_name = default_from_name
        self.base_url = "https://api.sendgrid.com/v3"

        # Rate limiting
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0

        # Email templates
        self.templates = {
            EmailType.WELCOME: {
                'template_id': 'd-welcome-template-id',
                'subject': 'Welcome to FinClick.AI'
            },
            EmailType.VERIFICATION: {
                'template_id': 'd-verification-template-id',
                'subject': 'Verify Your Email Address'
            },
            EmailType.PASSWORD_RESET: {
                'template_id': 'd-password-reset-template-id',
                'subject': 'Reset Your Password'
            },
            EmailType.SUBSCRIPTION_CONFIRMATION: {
                'template_id': 'd-subscription-template-id',
                'subject': 'Subscription Confirmation'
            },
            EmailType.PAYMENT_RECEIPT: {
                'template_id': 'd-payment-receipt-template-id',
                'subject': 'Payment Receipt'
            },
            EmailType.ACCOUNT_UPDATE: {
                'template_id': 'd-account-update-template-id',
                'subject': 'Account Update Notification'
            },
            EmailType.NEWSLETTER: {
                'template_id': 'd-newsletter-template-id',
                'subject': 'FinClick.AI Newsletter'
            },
            EmailType.ALERT: {
                'template_id': 'd-alert-template-id',
                'subject': 'Important Alert'
            },
            EmailType.REPORT: {
                'template_id': 'd-report-template-id',
                'subject': 'Your Financial Report'
            }
        }

        logger.info("SendGrid service initialized")

    async def _rate_limit_check(self):
        """Ensure we don't exceed SendGrid rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    async def _make_request(self, endpoint: str, data: Dict, method: str = 'POST') -> Dict:
        """Make request to SendGrid API"""
        await self._rate_limit_check()

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        url = f"{self.base_url}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            if method.upper() == 'POST':
                async with session.post(url, headers=headers, json=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == 'GET':
                async with session.get(url, headers=headers, params=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == 'DELETE':
                async with session.delete(url, headers=headers, json=data) as response:
                    return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict:
        """Handle SendGrid API response"""
        response_text = await response.text()

        if response.status in [200, 201, 202]:
            try:
                return json.loads(response_text) if response_text else {'success': True}
            except json.JSONDecodeError:
                return {'success': True, 'response': response_text}
        else:
            logger.error(f"SendGrid API error {response.status}: {response_text}")
            try:
                error_data = json.loads(response_text) if response_text else {}
            except json.JSONDecodeError:
                error_data = {'message': response_text}

            raise Exception(f"SendGrid API error {response.status}: {error_data.get('message', 'Unknown error')}")

    @retry_on_error()
    async def send_email(
        self,
        to_recipients: List[EmailRecipient],
        subject: str,
        html_content: str = None,
        text_content: str = None,
        from_email: str = None,
        from_name: str = None,
        reply_to: str = None,
        cc_recipients: List[EmailRecipient] = None,
        bcc_recipients: List[EmailRecipient] = None,
        attachments: List[EmailAttachment] = None,
        template_id: str = None,
        dynamic_template_data: Dict = None,
        send_at: datetime = None,
        priority: Priority = Priority.NORMAL,
        categories: List[str] = None,
        custom_args: Dict[str, str] = None
    ) -> EmailResult:
        """Send email using SendGrid"""
        try:
            # Build email data
            email_data = {
                'personalizations': [],
                'from': {
                    'email': from_email or self.default_from_email,
                    'name': from_name or self.default_from_name
                },
                'subject': subject
            }

            # Add reply-to if specified
            if reply_to:
                email_data['reply_to'] = {'email': reply_to}

            # Build personalizations
            personalization = {
                'to': [{'email': r.email, 'name': r.name} for r in to_recipients]
            }

            # Add CC and BCC if specified
            if cc_recipients:
                personalization['cc'] = [{'email': r.email, 'name': r.name} for r in cc_recipients]

            if bcc_recipients:
                personalization['bcc'] = [{'email': r.email, 'name': r.name} for r in bcc_recipients]

            # Add dynamic template data for each recipient
            if dynamic_template_data:
                personalization['dynamic_template_data'] = dynamic_template_data
            elif to_recipients[0].substitutions:
                personalization['substitutions'] = to_recipients[0].substitutions

            # Add send_at if specified
            if send_at:
                personalization['send_at'] = int(send_at.timestamp())

            email_data['personalizations'].append(personalization)

            # Add content or template
            if template_id:
                email_data['template_id'] = template_id
            else:
                content = []
                if text_content:
                    content.append({'type': 'text/plain', 'value': text_content})
                if html_content:
                    content.append({'type': 'text/html', 'value': html_content})
                email_data['content'] = content

            # Add attachments
            if attachments:
                email_data['attachments'] = []
                for attachment in attachments:
                    attachment_data = {
                        'content': attachment.content,
                        'filename': attachment.filename,
                        'type': attachment.type,
                        'disposition': attachment.disposition
                    }
                    if attachment.content_id:
                        attachment_data['content_id'] = attachment.content_id
                    email_data['attachments'].append(attachment_data)

            # Add categories
            if categories:
                email_data['categories'] = categories

            # Add custom arguments
            if custom_args:
                email_data['custom_args'] = custom_args

            # Add tracking settings
            email_data['tracking_settings'] = {
                'click_tracking': {'enable': True, 'enable_text': False},
                'open_tracking': {'enable': True},
                'subscription_tracking': {'enable': False}
            }

            # Add mail settings
            email_data['mail_settings'] = {
                'spam_check': {'enable': True, 'threshold': 1, 'post_to_url': ''}
            }

            # Send email
            response = await self._make_request('mail/send', email_data)

            # Extract message ID from headers (if available)
            message_id = response.get('message_id', f"sendgrid_{int(time.time())}")

            logger.info(f"Email sent successfully: {message_id}")
            return EmailResult(
                success=True,
                message_id=message_id
            )

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return EmailResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_error()
    async def send_template_email(
        self,
        email_type: EmailType,
        to_recipients: List[EmailRecipient],
        template_data: Dict = None,
        from_email: str = None,
        from_name: str = None,
        send_at: datetime = None,
        categories: List[str] = None
    ) -> EmailResult:
        """Send email using predefined template"""
        try:
            if email_type not in self.templates:
                raise ValueError(f"Unknown email type: {email_type}")

            template_config = self.templates[email_type]
            template_id = template_config['template_id']
            subject = template_config['subject']

            # Add default categories
            if not categories:
                categories = [email_type.value]

            return await self.send_email(
                to_recipients=to_recipients,
                subject=subject,
                from_email=from_email,
                from_name=from_name,
                template_id=template_id,
                dynamic_template_data=template_data,
                send_at=send_at,
                categories=categories
            )

        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            return EmailResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_error()
    async def send_bulk_emails(
        self,
        recipients_data: List[Dict],
        template_id: str,
        subject: str,
        from_email: str = None,
        from_name: str = None,
        batch_size: int = 1000
    ) -> List[EmailResult]:
        """Send bulk emails with personalization"""
        results = []

        try:
            # Split recipients into batches
            for i in range(0, len(recipients_data), batch_size):
                batch = recipients_data[i:i + batch_size]

                # Build personalizations for batch
                personalizations = []
                for recipient_data in batch:
                    personalization = {
                        'to': [{'email': recipient_data['email'], 'name': recipient_data.get('name', '')}],
                        'dynamic_template_data': recipient_data.get('template_data', {})
                    }
                    personalizations.append(personalization)

                # Build email data
                email_data = {
                    'personalizations': personalizations,
                    'from': {
                        'email': from_email or self.default_from_email,
                        'name': from_name or self.default_from_name
                    },
                    'template_id': template_id,
                    'subject': subject
                }

                # Send batch
                response = await self._make_request('mail/send', email_data)
                message_id = response.get('message_id', f"bulk_{int(time.time())}_{i}")

                results.append(EmailResult(
                    success=True,
                    message_id=message_id
                ))

                # Add delay between batches
                await asyncio.sleep(1)

            logger.info(f"Sent bulk emails to {len(recipients_data)} recipients in {len(results)} batches")
            return results

        except Exception as e:
            logger.error(f"Failed to send bulk emails: {str(e)}")
            results.append(EmailResult(
                success=False,
                error_message=str(e)
            ))
            return results

    @retry_on_error()
    async def create_list(self, name: str) -> Dict:
        """Create a contact list"""
        try:
            list_data = {
                'name': name
            }

            response = await self._make_request('marketing/lists', list_data)

            logger.info(f"Created contact list: {name}")
            return response

        except Exception as e:
            logger.error(f"Failed to create contact list: {str(e)}")
            raise

    @retry_on_error()
    async def add_contacts_to_list(self, list_id: str, contacts: List[Dict]) -> Dict:
        """Add contacts to a list"""
        try:
            contact_data = {
                'list_ids': [list_id],
                'contacts': contacts
            }

            response = await self._make_request('marketing/contacts', contact_data, method='PUT')

            logger.info(f"Added {len(contacts)} contacts to list {list_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to add contacts to list: {str(e)}")
            raise

    @retry_on_error()
    async def get_email_stats(self, start_date: datetime, end_date: datetime = None) -> Dict:
        """Get email statistics"""
        try:
            if not end_date:
                end_date = datetime.now()

            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'aggregated_by': 'day'
            }

            response = await self._make_request('stats', params, method='GET')

            logger.info(f"Retrieved email stats from {start_date.date()} to {end_date.date()}")
            return response

        except Exception as e:
            logger.error(f"Failed to get email stats: {str(e)}")
            raise

    @retry_on_error()
    async def get_bounces(self, start_time: datetime = None, end_time: datetime = None) -> List[Dict]:
        """Get bounced emails"""
        try:
            params = {}
            if start_time:
                params['start_time'] = int(start_time.timestamp())
            if end_time:
                params['end_time'] = int(end_time.timestamp())

            response = await self._make_request('suppression/bounces', params, method='GET')

            logger.info(f"Retrieved {len(response)} bounces")
            return response

        except Exception as e:
            logger.error(f"Failed to get bounces: {str(e)}")
            raise

    @retry_on_error()
    async def delete_bounce(self, email: str) -> Dict:
        """Delete a bounce"""
        try:
            response = await self._make_request(f'suppression/bounces/{email}', {}, method='DELETE')

            logger.info(f"Deleted bounce for email: {email}")
            return response

        except Exception as e:
            logger.error(f"Failed to delete bounce: {str(e)}")
            raise

    @retry_on_error()
    async def get_blocks(self, start_time: datetime = None, end_time: datetime = None) -> List[Dict]:
        """Get blocked emails"""
        try:
            params = {}
            if start_time:
                params['start_time'] = int(start_time.timestamp())
            if end_time:
                params['end_time'] = int(end_time.timestamp())

            response = await self._make_request('suppression/blocks', params, method='GET')

            logger.info(f"Retrieved {len(response)} blocks")
            return response

        except Exception as e:
            logger.error(f"Failed to get blocks: {str(e)}")
            raise

    @retry_on_error()
    async def delete_block(self, email: str) -> Dict:
        """Delete a block"""
        try:
            response = await self._make_request(f'suppression/blocks/{email}', {}, method='DELETE')

            logger.info(f"Deleted block for email: {email}")
            return response

        except Exception as e:
            logger.error(f"Failed to delete block: {str(e)}")
            raise

    @retry_on_error()
    async def validate_email(self, email: str) -> Dict:
        """Validate email address"""
        try:
            validation_data = {
                'email': email
            }

            response = await self._make_request('validations/email', validation_data)

            logger.info(f"Validated email: {email}")
            return response

        except Exception as e:
            logger.error(f"Failed to validate email: {str(e)}")
            raise

    async def create_email_attachment_from_file(self, file_path: str, filename: str = None) -> EmailAttachment:
        """Create email attachment from file"""
        try:
            import aiofiles
            import mimetypes

            if not filename:
                filename = file_path.split('/')[-1]

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            # Read file and encode to base64
            async with aiofiles.open(file_path, 'rb') as file:
                file_content = await file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            return EmailAttachment(
                content=encoded_content,
                filename=filename,
                type=mime_type
            )

        except Exception as e:
            logger.error(f"Failed to create attachment from file: {str(e)}")
            raise

    def get_webhook_event_types(self) -> List[str]:
        """Get list of supported webhook event types"""
        return [
            'processed',
            'dropped',
            'delivered',
            'deferred',
            'bounce',
            'open',
            'click',
            'spam_report',
            'unsubscribe',
            'group_unsubscribe',
            'group_resubscribe'
        ]

    async def handle_webhook_event(self, event_data: Dict) -> Dict:
        """Handle incoming SendGrid webhook event"""
        try:
            event_type = event_data.get('event')
            email = event_data.get('email')
            timestamp = event_data.get('timestamp')

            logger.info(f"Handling SendGrid webhook event: {event_type} for {email}")

            if event_type == 'bounce':
                return await self._handle_bounce_event(event_data)
            elif event_type == 'dropped':
                return await self._handle_dropped_event(event_data)
            elif event_type == 'delivered':
                return await self._handle_delivered_event(event_data)
            elif event_type == 'open':
                return await self._handle_open_event(event_data)
            elif event_type == 'click':
                return await self._handle_click_event(event_data)
            elif event_type == 'spam_report':
                return await self._handle_spam_report_event(event_data)
            elif event_type == 'unsubscribe':
                return await self._handle_unsubscribe_event(event_data)
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return {'success': True, 'message': f'Event {event_type} received but not handled'}

        except Exception as e:
            logger.error(f"Error handling SendGrid webhook event: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _handle_bounce_event(self, event_data: Dict) -> Dict:
        """Handle bounce event"""
        email = event_data.get('email')
        reason = event_data.get('reason')
        logger.warning(f"Email bounced: {email}, reason: {reason}")
        # Add your business logic here
        return {'success': True, 'message': 'Bounce event processed'}

    async def _handle_dropped_event(self, event_data: Dict) -> Dict:
        """Handle dropped event"""
        email = event_data.get('email')
        reason = event_data.get('reason')
        logger.warning(f"Email dropped: {email}, reason: {reason}")
        # Add your business logic here
        return {'success': True, 'message': 'Dropped event processed'}

    async def _handle_delivered_event(self, event_data: Dict) -> Dict:
        """Handle delivered event"""
        email = event_data.get('email')
        logger.info(f"Email delivered: {email}")
        # Add your business logic here
        return {'success': True, 'message': 'Delivered event processed'}

    async def _handle_open_event(self, event_data: Dict) -> Dict:
        """Handle open event"""
        email = event_data.get('email')
        logger.info(f"Email opened: {email}")
        # Add your business logic here
        return {'success': True, 'message': 'Open event processed'}

    async def _handle_click_event(self, event_data: Dict) -> Dict:
        """Handle click event"""
        email = event_data.get('email')
        url = event_data.get('url')
        logger.info(f"Email clicked: {email}, URL: {url}")
        # Add your business logic here
        return {'success': True, 'message': 'Click event processed'}

    async def _handle_spam_report_event(self, event_data: Dict) -> Dict:
        """Handle spam report event"""
        email = event_data.get('email')
        logger.warning(f"Spam report: {email}")
        # Add your business logic here
        return {'success': True, 'message': 'Spam report event processed'}

    async def _handle_unsubscribe_event(self, event_data: Dict) -> Dict:
        """Handle unsubscribe event"""
        email = event_data.get('email')
        logger.info(f"User unsubscribed: {email}")
        # Add your business logic here
        return {'success': True, 'message': 'Unsubscribe event processed'}

# Utility functions
async def create_sendgrid_service(
    api_key: str,
    default_from_email: str,
    default_from_name: str = "FinClick.AI"
) -> SendGridService:
    """Factory function to create SendGridService instance"""
    return SendGridService(api_key, default_from_email, default_from_name)

def create_email_recipient(email: str, name: str = None, **substitutions) -> EmailRecipient:
    """Create email recipient with substitutions"""
    return EmailRecipient(
        email=email,
        name=name,
        substitutions=substitutions if substitutions else None
    )

def create_welcome_email_data(user_name: str, verification_link: str) -> Dict:
    """Create template data for welcome email"""
    return {
        'user_name': user_name,
        'verification_link': verification_link,
        'company_name': 'FinClick.AI',
        'support_email': 'support@finclick.ai'
    }

def create_password_reset_email_data(user_name: str, reset_link: str, expiry_hours: int = 24) -> Dict:
    """Create template data for password reset email"""
    return {
        'user_name': user_name,
        'reset_link': reset_link,
        'expiry_hours': expiry_hours,
        'company_name': 'FinClick.AI',
        'support_email': 'support@finclick.ai'
    }

def create_payment_receipt_email_data(
    user_name: str,
    amount: float,
    currency: str,
    transaction_id: str,
    service: str,
    date: datetime
) -> Dict:
    """Create template data for payment receipt email"""
    return {
        'user_name': user_name,
        'amount': f"{amount:.2f}",
        'currency': currency.upper(),
        'transaction_id': transaction_id,
        'service': service,
        'date': date.strftime('%B %d, %Y'),
        'company_name': 'FinClick.AI',
        'support_email': 'support@finclick.ai'
    }