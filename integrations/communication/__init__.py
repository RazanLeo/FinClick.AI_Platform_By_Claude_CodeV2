"""
Communication APIs Integration Package
Provides unified access to all communication services for FinClick.AI platform
"""

from .sendgrid_service import (
    SendGridService,
    EmailType as SendGridEmailType,
    Priority as SendGridPriority,
    EmailRecipient,
    EmailAttachment,
    EmailResult,
    create_sendgrid_service,
    create_email_recipient,
    create_welcome_email_data,
    create_password_reset_email_data,
    create_payment_receipt_email_data
)

from .twilio_service import (
    TwilioService,
    MessageStatus,
    MessageDirection,
    CallStatus,
    SMSType,
    SMSResult,
    CallResult,
    create_twilio_service,
    create_verification_code,
    validate_phone_number,
    format_phone_for_display
)

from .aws_ses_service import (
    AWSSESService,
    EmailType as SESEmailType,
    ConfigurationSetEvent,
    SuppressionReason,
    SESEmailResult,
    SESRecipient,
    SESAttachment,
    create_aws_ses_service,
    create_ses_recipient,
    create_ses_attachment_from_file
)

from .websocket_service import (
    WebSocketService,
    MessageType,
    NotificationPriority,
    SubscriptionType,
    WebSocketMessage,
    ClientConnection,
    create_websocket_service,
    create_jwt_token,
    create_notification_message
)

__all__ = [
    # SendGrid
    'SendGridService',
    'SendGridEmailType',
    'SendGridPriority',
    'EmailRecipient',
    'EmailAttachment',
    'EmailResult',
    'create_sendgrid_service',
    'create_email_recipient',
    'create_welcome_email_data',
    'create_password_reset_email_data',
    'create_payment_receipt_email_data',

    # Twilio
    'TwilioService',
    'MessageStatus',
    'MessageDirection',
    'CallStatus',
    'SMSType',
    'SMSResult',
    'CallResult',
    'create_twilio_service',
    'create_verification_code',
    'validate_phone_number',
    'format_phone_for_display',

    # AWS SES
    'AWSSESService',
    'SESEmailType',
    'ConfigurationSetEvent',
    'SuppressionReason',
    'SESEmailResult',
    'SESRecipient',
    'SESAttachment',
    'create_aws_ses_service',
    'create_ses_recipient',
    'create_ses_attachment_from_file',

    # WebSocket
    'WebSocketService',
    'MessageType',
    'NotificationPriority',
    'SubscriptionType',
    'WebSocketMessage',
    'ClientConnection',
    'create_websocket_service',
    'create_jwt_token',
    'create_notification_message'
]