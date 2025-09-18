"""
AWS SES (Simple Email Service) Integration
Handles email delivery and management for FinClick.AI platform
"""

import boto3
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
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logger = logging.getLogger(__name__)

class EmailType(Enum):
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    SYSTEM = "system"

class ConfigurationSetEvent(Enum):
    SEND = "send"
    REJECT = "reject"
    BOUNCE = "bounce"
    COMPLAINT = "complaint"
    DELIVERY = "delivery"
    OPEN = "open"
    CLICK = "click"
    RENDERING_FAILURE = "renderingFailure"
    DELIVERY_DELAY = "deliveryDelay"
    SUBSCRIPTION = "subscription"

class SuppressionReason(Enum):
    BOUNCE = "BOUNCE"
    COMPLAINT = "COMPLAINT"

@dataclass
class SESEmailResult:
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None

@dataclass
class SESRecipient:
    email: str
    name: Optional[str] = None
    replacement_data: Optional[Dict[str, str]] = None

@dataclass
class SESAttachment:
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"

def retry_on_aws_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry AWS API calls on specific errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ClientError, BotoCoreError) as e:
                    last_exception = e
                    error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', 'Unknown')

                    # Retry on throttling and temporary errors
                    if error_code in ['Throttling', 'ServiceUnavailable', 'TooManyRequestsException']:
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)
                            logger.warning(f"AWS SES error ({error_code}), retrying in {wait_time}s")
                            await asyncio.sleep(wait_time)
                        continue

                    # Don't retry on other errors
                    raise e
                except Exception as e:
                    # Don't retry on non-AWS exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class AWSSESService:
    """Comprehensive AWS SES service for FinClick.AI"""

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = 'us-east-1',
        default_from_email: str = None,
        default_from_name: str = "FinClick.AI",
        configuration_set: str = None
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.default_from_email = default_from_email
        self.default_from_name = default_from_name
        self.configuration_set = configuration_set

        # Initialize SES client
        self.ses_client = boto3.client(
            'ses',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        # Initialize SESv2 client for advanced features
        self.sesv2_client = boto3.client(
            'sesv2',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        # Rate limiting
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0

        logger.info(f"AWS SES service initialized for region: {region_name}")

    async def _rate_limit_check(self):
        """Ensure we don't exceed AWS SES rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _run_async(self, coro):
        """Run async function in sync context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @retry_on_aws_error()
    async def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        html_body: str = None,
        text_body: str = None,
        from_email: str = None,
        from_name: str = None,
        reply_to_addresses: List[str] = None,
        cc_addresses: List[str] = None,
        bcc_addresses: List[str] = None,
        configuration_set_name: str = None,
        tags: List[Dict[str, str]] = None,
        template_arn: str = None
    ) -> SESEmailResult:
        """Send email using AWS SES"""
        await self._rate_limit_check()

        try:
            # Prepare source address
            if from_name and from_email:
                source = f"{from_name} <{from_email}>"
            else:
                source = from_email or self.default_from_email

            if not source:
                raise ValueError("From email address is required")

            # Prepare destination
            destination = {
                'ToAddresses': to_addresses
            }

            if cc_addresses:
                destination['CcAddresses'] = cc_addresses

            if bcc_addresses:
                destination['BccAddresses'] = bcc_addresses

            # Prepare message
            message = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {}
            }

            if html_body:
                message['Body']['Html'] = {
                    'Data': html_body,
                    'Charset': 'UTF-8'
                }

            if text_body:
                message['Body']['Text'] = {
                    'Data': text_body,
                    'Charset': 'UTF-8'
                }

            # Prepare request parameters
            params = {
                'Source': source,
                'Destination': destination,
                'Message': message
            }

            if reply_to_addresses:
                params['ReplyToAddresses'] = reply_to_addresses

            if configuration_set_name or self.configuration_set:
                params['ConfigurationSetName'] = configuration_set_name or self.configuration_set

            if tags:
                params['Tags'] = tags

            if template_arn:
                params['TemplateArn'] = template_arn

            # Send email
            response = self.ses_client.send_email(**params)

            message_id = response['MessageId']
            logger.info(f"Email sent successfully: {message_id}")

            return SESEmailResult(
                success=True,
                message_id=message_id
            )

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS SES error {error_code}: {error_message}")

            return SESEmailResult(
                success=False,
                error_message=error_message,
                error_code=error_code
            )

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return SESEmailResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_aws_error()
    async def send_templated_email(
        self,
        to_addresses: List[str],
        template_name: str,
        template_data: Dict[str, Any],
        from_email: str = None,
        from_name: str = None,
        reply_to_addresses: List[str] = None,
        configuration_set_name: str = None,
        tags: List[Dict[str, str]] = None
    ) -> SESEmailResult:
        """Send email using SES template"""
        await self._rate_limit_check()

        try:
            # Prepare source address
            if from_name and from_email:
                source = f"{from_name} <{from_email}>"
            else:
                source = from_email or self.default_from_email

            # Prepare destination
            destination = {
                'ToAddresses': to_addresses
            }

            # Prepare request parameters
            params = {
                'Source': source,
                'Destination': destination,
                'Template': template_name,
                'TemplateData': json.dumps(template_data)
            }

            if reply_to_addresses:
                params['ReplyToAddresses'] = reply_to_addresses

            if configuration_set_name or self.configuration_set:
                params['ConfigurationSetName'] = configuration_set_name or self.configuration_set

            if tags:
                params['Tags'] = tags

            # Send templated email
            response = self.ses_client.send_templated_email(**params)

            message_id = response['MessageId']
            logger.info(f"Templated email sent successfully: {message_id}")

            return SESEmailResult(
                success=True,
                message_id=message_id
            )

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS SES templated email error {error_code}: {error_message}")

            return SESEmailResult(
                success=False,
                error_message=error_message,
                error_code=error_code
            )

        except Exception as e:
            logger.error(f"Failed to send templated email: {str(e)}")
            return SESEmailResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_aws_error()
    async def send_bulk_templated_email(
        self,
        recipients: List[SESRecipient],
        template_name: str,
        default_template_data: Dict[str, Any],
        from_email: str = None,
        from_name: str = None,
        reply_to_addresses: List[str] = None,
        configuration_set_name: str = None,
        tags: List[Dict[str, str]] = None
    ) -> List[SESEmailResult]:
        """Send bulk templated emails"""
        await self._rate_limit_check()

        try:
            # Prepare source address
            if from_name and from_email:
                source = f"{from_name} <{from_email}>"
            else:
                source = from_email or self.default_from_email

            # Prepare destinations with personalization
            destinations = []
            for recipient in recipients:
                destination = {
                    'Destination': {
                        'ToAddresses': [recipient.email]
                    },
                    'ReplacementTemplateData': json.dumps(
                        {**default_template_data, **(recipient.replacement_data or {})}
                    )
                }
                destinations.append(destination)

            # Prepare request parameters
            params = {
                'Source': source,
                'Template': template_name,
                'DefaultTemplateData': json.dumps(default_template_data),
                'Destinations': destinations
            }

            if reply_to_addresses:
                params['ReplyToAddresses'] = reply_to_addresses

            if configuration_set_name or self.configuration_set:
                params['ConfigurationSetName'] = configuration_set_name or self.configuration_set

            if tags:
                params['Tags'] = tags

            # Send bulk templated email
            response = self.ses_client.send_bulk_templated_email(**params)

            message_id = response['MessageId']
            status = response.get('Status', [])

            results = []
            for i, recipient in enumerate(recipients):
                if i < len(status):
                    recipient_status = status[i]
                    if recipient_status.get('Status') == 'Success':
                        results.append(SESEmailResult(
                            success=True,
                            message_id=recipient_status.get('MessageId', message_id)
                        ))
                    else:
                        results.append(SESEmailResult(
                            success=False,
                            error_message=recipient_status.get('Error', 'Unknown error')
                        ))
                else:
                    results.append(SESEmailResult(
                        success=True,
                        message_id=message_id
                    ))

            logger.info(f"Bulk templated email sent to {len(recipients)} recipients")
            return results

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS SES bulk email error {error_code}: {error_message}")

            return [SESEmailResult(
                success=False,
                error_message=error_message,
                error_code=error_code
            )]

        except Exception as e:
            logger.error(f"Failed to send bulk templated email: {str(e)}")
            return [SESEmailResult(
                success=False,
                error_message=str(e)
            )]

    @retry_on_aws_error()
    async def send_raw_email(
        self,
        raw_message: str,
        from_email: str = None,
        destinations: List[str] = None,
        configuration_set_name: str = None,
        tags: List[Dict[str, str]] = None
    ) -> SESEmailResult:
        """Send raw email message"""
        await self._rate_limit_check()

        try:
            params = {
                'RawMessage': {
                    'Data': raw_message.encode('utf-8')
                }
            }

            if from_email:
                params['Source'] = from_email

            if destinations:
                params['Destinations'] = destinations

            if configuration_set_name or self.configuration_set:
                params['ConfigurationSetName'] = configuration_set_name or self.configuration_set

            if tags:
                params['Tags'] = tags

            response = self.ses_client.send_raw_email(**params)

            message_id = response['MessageId']
            logger.info(f"Raw email sent successfully: {message_id}")

            return SESEmailResult(
                success=True,
                message_id=message_id
            )

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS SES raw email error {error_code}: {error_message}")

            return SESEmailResult(
                success=False,
                error_message=error_message,
                error_code=error_code
            )

        except Exception as e:
            logger.error(f"Failed to send raw email: {str(e)}")
            return SESEmailResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_aws_error()
    async def create_template(
        self,
        template_name: str,
        subject: str,
        html_part: str = None,
        text_part: str = None
    ) -> Dict:
        """Create email template"""
        await self._rate_limit_check()

        try:
            template = {
                'TemplateName': template_name,
                'Subject': subject
            }

            if html_part:
                template['HtmlPart'] = html_part

            if text_part:
                template['TextPart'] = text_part

            response = self.ses_client.create_template(Template=template)

            logger.info(f"Email template created: {template_name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to create template: {str(e)}")
            raise

    @retry_on_aws_error()
    async def update_template(
        self,
        template_name: str,
        subject: str = None,
        html_part: str = None,
        text_part: str = None
    ) -> Dict:
        """Update email template"""
        await self._rate_limit_check()

        try:
            # Get existing template
            response = self.ses_client.get_template(TemplateName=template_name)
            template = response['Template']

            # Update fields
            if subject is not None:
                template['Subject'] = subject
            if html_part is not None:
                template['HtmlPart'] = html_part
            if text_part is not None:
                template['TextPart'] = text_part

            # Update template
            response = self.ses_client.update_template(Template=template)

            logger.info(f"Email template updated: {template_name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to update template: {str(e)}")
            raise

    @retry_on_aws_error()
    async def delete_template(self, template_name: str) -> Dict:
        """Delete email template"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.delete_template(TemplateName=template_name)

            logger.info(f"Email template deleted: {template_name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to delete template: {str(e)}")
            raise

    @retry_on_aws_error()
    async def list_templates(self, max_items: int = 50, next_token: str = None) -> Dict:
        """List email templates"""
        await self._rate_limit_check()

        try:
            params = {
                'MaxItems': max_items
            }

            if next_token:
                params['NextToken'] = next_token

            response = self.ses_client.list_templates(**params)

            logger.info(f"Retrieved {len(response.get('TemplatesMetadata', []))} templates")
            return response

        except ClientError as e:
            logger.error(f"Failed to list templates: {str(e)}")
            raise

    @retry_on_aws_error()
    async def verify_email_identity(self, email: str) -> Dict:
        """Verify email identity"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.verify_email_identity(EmailAddress=email)

            logger.info(f"Email verification initiated: {email}")
            return response

        except ClientError as e:
            logger.error(f"Failed to verify email identity: {str(e)}")
            raise

    @retry_on_aws_error()
    async def verify_domain_identity(self, domain: str) -> Dict:
        """Verify domain identity"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.verify_domain_identity(Domain=domain)

            logger.info(f"Domain verification initiated: {domain}")
            return response

        except ClientError as e:
            logger.error(f"Failed to verify domain identity: {str(e)}")
            raise

    @retry_on_aws_error()
    async def get_identity_verification_attributes(self, identities: List[str]) -> Dict:
        """Get identity verification attributes"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.get_identity_verification_attributes(Identities=identities)

            logger.info(f"Retrieved verification attributes for {len(identities)} identities")
            return response

        except ClientError as e:
            logger.error(f"Failed to get identity verification attributes: {str(e)}")
            raise

    @retry_on_aws_error()
    async def put_identity_dkim_attributes(self, identity: str, dkim_enabled: bool) -> Dict:
        """Enable/disable DKIM for identity"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.put_identity_dkim_attributes(
                Identity=identity,
                DkimEnabled=dkim_enabled
            )

            logger.info(f"DKIM {'enabled' if dkim_enabled else 'disabled'} for: {identity}")
            return response

        except ClientError as e:
            logger.error(f"Failed to set DKIM attributes: {str(e)}")
            raise

    @retry_on_aws_error()
    async def get_send_statistics(self) -> Dict:
        """Get sending statistics"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.get_send_statistics()

            logger.info("Retrieved send statistics")
            return response

        except ClientError as e:
            logger.error(f"Failed to get send statistics: {str(e)}")
            raise

    @retry_on_aws_error()
    async def get_send_quota(self) -> Dict:
        """Get send quota"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.get_send_quota()

            logger.info("Retrieved send quota")
            return response

        except ClientError as e:
            logger.error(f"Failed to get send quota: {str(e)}")
            raise

    @retry_on_aws_error()
    async def put_suppressed_destination(
        self,
        email: str,
        reason: SuppressionReason
    ) -> Dict:
        """Add email to suppression list"""
        await self._rate_limit_check()

        try:
            response = self.sesv2_client.put_suppressed_destination(
                EmailAddress=email,
                Reason=reason.value
            )

            logger.info(f"Email added to suppression list: {email} ({reason.value})")
            return response

        except ClientError as e:
            logger.error(f"Failed to add email to suppression list: {str(e)}")
            raise

    @retry_on_aws_error()
    async def delete_suppressed_destination(self, email: str) -> Dict:
        """Remove email from suppression list"""
        await self._rate_limit_check()

        try:
            response = self.sesv2_client.delete_suppressed_destination(EmailAddress=email)

            logger.info(f"Email removed from suppression list: {email}")
            return response

        except ClientError as e:
            logger.error(f"Failed to remove email from suppression list: {str(e)}")
            raise

    @retry_on_aws_error()
    async def get_suppressed_destination(self, email: str) -> Dict:
        """Get suppressed destination details"""
        await self._rate_limit_check()

        try:
            response = self.sesv2_client.get_suppressed_destination(EmailAddress=email)

            logger.info(f"Retrieved suppressed destination details: {email}")
            return response

        except ClientError as e:
            logger.error(f"Failed to get suppressed destination: {str(e)}")
            raise

    @retry_on_aws_error()
    async def create_configuration_set(
        self,
        configuration_set_name: str,
        delivery_options: Dict = None,
        reputation_tracking_enabled: bool = True,
        sending_enabled: bool = True
    ) -> Dict:
        """Create configuration set"""
        await self._rate_limit_check()

        try:
            response = self.ses_client.create_configuration_set(
                ConfigurationSet={
                    'Name': configuration_set_name
                }
            )

            # Enable reputation tracking
            if reputation_tracking_enabled:
                self.ses_client.put_configuration_set_reputation_tracking(
                    ConfigurationSetName=configuration_set_name,
                    Enabled=True
                )

            # Set sending enabled/disabled
            if not sending_enabled:
                self.ses_client.put_configuration_set_sending_enabled(
                    ConfigurationSetName=configuration_set_name,
                    Enabled=False
                )

            # Set delivery options
            if delivery_options:
                self.ses_client.put_configuration_set_delivery_options(
                    ConfigurationSetName=configuration_set_name,
                    DeliveryOptions=delivery_options
                )

            logger.info(f"Configuration set created: {configuration_set_name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to create configuration set: {str(e)}")
            raise

    def create_email_with_attachments(
        self,
        to_addresses: List[str],
        subject: str,
        html_body: str = None,
        text_body: str = None,
        attachments: List[SESAttachment] = None,
        from_email: str = None,
        from_name: str = None
    ) -> str:
        """Create raw email message with attachments"""
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        from email.utils import formataddr
        import uuid

        # Create multipart message
        msg = MIMEMultipart()

        # Set headers
        if from_name and from_email:
            msg['From'] = formataddr((from_name, from_email))
        else:
            msg['From'] = from_email or self.default_from_email

        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = subject
        msg['Message-ID'] = f"<{uuid.uuid4()}@finclick.ai>"

        # Add text body
        if text_body:
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))

        # Add HTML body
        if html_body:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Add attachments
        if attachments:
            for attachment in attachments:
                part = MIMEApplication(attachment.content, _subtype=None)
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=attachment.filename
                )
                part.add_header('Content-Type', attachment.content_type)
                msg.attach(part)

        return msg.as_string()

    async def handle_sns_notification(self, message: Dict) -> Dict:
        """Handle SNS notification from SES"""
        try:
            message_type = message.get('Type')
            notification_type = message.get('notificationType')

            logger.info(f"Handling SES SNS notification: {notification_type}")

            if notification_type == 'Bounce':
                return await self._handle_bounce_notification(message)
            elif notification_type == 'Complaint':
                return await self._handle_complaint_notification(message)
            elif notification_type == 'Delivery':
                return await self._handle_delivery_notification(message)
            else:
                logger.info(f"Unhandled notification type: {notification_type}")
                return {'success': True, 'message': f'Notification {notification_type} received but not handled'}

        except Exception as e:
            logger.error(f"Error handling SES SNS notification: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _handle_bounce_notification(self, message: Dict) -> Dict:
        """Handle bounce notification"""
        bounce = message.get('bounce', {})
        bounce_type = bounce.get('bounceType')
        bounced_recipients = bounce.get('bouncedRecipients', [])

        for recipient in bounced_recipients:
            email = recipient.get('emailAddress')
            logger.warning(f"Email bounced: {email}, type: {bounce_type}")

        # Add bounced emails to suppression list if permanent bounce
        if bounce_type == 'Permanent':
            for recipient in bounced_recipients:
                email = recipient.get('emailAddress')
                try:
                    await self.put_suppressed_destination(email, SuppressionReason.BOUNCE)
                except Exception as e:
                    logger.error(f"Failed to add {email} to suppression list: {str(e)}")

        return {'success': True, 'message': 'Bounce notification processed'}

    async def _handle_complaint_notification(self, message: Dict) -> Dict:
        """Handle complaint notification"""
        complaint = message.get('complaint', {})
        complained_recipients = complaint.get('complainedRecipients', [])

        for recipient in complained_recipients:
            email = recipient.get('emailAddress')
            logger.warning(f"Email complaint: {email}")

            # Add complained emails to suppression list
            try:
                await self.put_suppressed_destination(email, SuppressionReason.COMPLAINT)
            except Exception as e:
                logger.error(f"Failed to add {email} to suppression list: {str(e)}")

        return {'success': True, 'message': 'Complaint notification processed'}

    async def _handle_delivery_notification(self, message: Dict) -> Dict:
        """Handle delivery notification"""
        delivery = message.get('delivery', {})
        delivered_recipients = delivery.get('recipients', [])

        for email in delivered_recipients:
            logger.info(f"Email delivered: {email}")

        return {'success': True, 'message': 'Delivery notification processed'}

# Utility functions
async def create_aws_ses_service(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str = 'us-east-1',
    default_from_email: str = None,
    default_from_name: str = "FinClick.AI",
    configuration_set: str = None
) -> AWSSESService:
    """Factory function to create AWSSESService instance"""
    return AWSSESService(
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        default_from_email,
        default_from_name,
        configuration_set
    )

def create_ses_recipient(email: str, name: str = None, **replacement_data) -> SESRecipient:
    """Create SES recipient with replacement data"""
    return SESRecipient(
        email=email,
        name=name,
        replacement_data=replacement_data if replacement_data else None
    )

def create_ses_attachment_from_file(file_path: str, filename: str = None) -> SESAttachment:
    """Create SES attachment from file"""
    import mimetypes

    if not filename:
        filename = file_path.split('/')[-1]

    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'

    # Read file content
    with open(file_path, 'rb') as file:
        content = file.read()

    return SESAttachment(
        filename=filename,
        content=content,
        content_type=content_type
    )