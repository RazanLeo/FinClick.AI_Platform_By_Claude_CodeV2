import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from app import db, current_app
from models import Notification, NotificationTemplate, UserNotificationSettings, NotificationType, NotificationStatus
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Notification management service"""

    @staticmethod
    def send_notification(user_id, type, title, message, recipient=None, data=None, scheduled_at=None):
        """Send a notification"""
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                recipient=recipient or NotificationService.get_user_recipient(user_id, type),
                data=data or {},
                scheduled_at=scheduled_at
            )

            db.session.add(notification)
            db.session.flush()

            # Send immediately if not scheduled
            if not scheduled_at:
                NotificationService.deliver_notification(notification.id)

            return notification

        except Exception as e:
            logger.error(f"Send notification error: {str(e)}")
            raise

    @staticmethod
    def deliver_notification(notification_id):
        """Deliver a notification"""
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                raise ValueError("Notification not found")

            # Check user preferences
            settings = UserNotificationSettings.query.filter_by(
                user_id=notification.user_id
            ).first()

            if not NotificationService.should_send_notification(notification, settings):
                notification.status = NotificationStatus.FAILED
                return

            # Deliver based on type
            if notification.type == NotificationType.EMAIL:
                NotificationService.send_email(notification)
            elif notification.type == NotificationType.PUSH:
                NotificationService.send_push_notification(notification)
            elif notification.type == NotificationType.SMS:
                NotificationService.send_sms(notification)
            elif notification.type == NotificationType.IN_APP:
                notification.status = NotificationStatus.DELIVERED

            notification.sent_at = datetime.utcnow()
            notification.delivery_attempts += 1

        except Exception as e:
            logger.error(f"Deliver notification error: {str(e)}")
            notification.status = NotificationStatus.FAILED
            notification.delivery_attempts += 1

    @staticmethod
    def send_email(notification):
        """Send email notification"""
        try:
            smtp_server = current_app.config.get('SMTP_SERVER')
            smtp_port = current_app.config.get('SMTP_PORT')
            smtp_username = current_app.config.get('SMTP_USERNAME')
            smtp_password = current_app.config.get('SMTP_PASSWORD')
            from_email = current_app.config.get('FROM_EMAIL')

            if not all([smtp_server, smtp_username, smtp_password]):
                logger.warning("SMTP not configured")
                return

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = notification.recipient
            msg['Subject'] = notification.title

            msg.attach(MIMEText(notification.message, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, notification.recipient, msg.as_string())
            server.quit()

            notification.status = NotificationStatus.SENT
            notification.delivered_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Send email error: {str(e)}")
            notification.status = NotificationStatus.FAILED

    @staticmethod
    def send_push_notification(notification):
        """Send push notification"""
        try:
            # Mock push notification implementation
            logger.info(f"Push notification sent to {notification.recipient}: {notification.title}")
            notification.status = NotificationStatus.SENT
            notification.delivered_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Send push notification error: {str(e)}")
            notification.status = NotificationStatus.FAILED

    @staticmethod
    def send_sms(notification):
        """Send SMS notification"""
        try:
            # Mock SMS implementation
            logger.info(f"SMS sent to {notification.recipient}: {notification.message}")
            notification.status = NotificationStatus.SENT
            notification.delivered_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Send SMS error: {str(e)}")
            notification.status = NotificationStatus.FAILED

    @staticmethod
    def mark_as_read(notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.query.get(notification_id)
            if notification:
                notification.read_at = datetime.utcnow()
                notification.status = NotificationStatus.READ

        except Exception as e:
            logger.error(f"Mark as read error: {str(e)}")
            raise

    @staticmethod
    def get_user_recipient(user_id, notification_type):
        """Get user's recipient for notification type"""
        try:
            # Mock implementation - would get from user service
            if notification_type == NotificationType.EMAIL:
                return f"user{user_id}@example.com"
            elif notification_type == NotificationType.SMS:
                return f"+1234567890"
            elif notification_type == NotificationType.PUSH:
                return f"device_token_{user_id}"
            else:
                return user_id

        except Exception as e:
            logger.error(f"Get user recipient error: {str(e)}")
            return None

    @staticmethod
    def should_send_notification(notification, settings):
        """Check if notification should be sent based on user settings"""
        try:
            if not settings:
                return True

            # Check type-specific settings
            if notification.type == NotificationType.EMAIL and not settings.email_enabled:
                return False
            elif notification.type == NotificationType.PUSH and not settings.push_enabled:
                return False
            elif notification.type == NotificationType.SMS and not settings.sms_enabled:
                return False
            elif notification.type == NotificationType.IN_APP and not settings.in_app_enabled:
                return False

            # Check quiet hours
            if settings.quiet_hours_enabled and settings.quiet_hours_start and settings.quiet_hours_end:
                current_time = datetime.utcnow().time()
                if settings.quiet_hours_start <= current_time <= settings.quiet_hours_end:
                    return False

            return True

        except Exception as e:
            logger.error(f"Should send notification error: {str(e)}")
            return True

    @staticmethod
    def create_default_settings(user_id):
        """Create default notification settings for user"""
        try:
            settings = UserNotificationSettings(user_id=user_id)
            db.session.add(settings)
            return settings

        except Exception as e:
            logger.error(f"Create default settings error: {str(e)}")
            raise

    @staticmethod
    def update_settings(user_id, data):
        """Update user notification settings"""
        try:
            settings = UserNotificationSettings.query.filter_by(user_id=user_id).first()

            if not settings:
                settings = NotificationService.create_default_settings(user_id)

            # Update settings
            updatable_fields = [
                'email_enabled', 'push_enabled', 'sms_enabled', 'in_app_enabled',
                'analysis_complete', 'report_ready', 'subscription_changes',
                'security_alerts', 'marketing_updates', 'quiet_hours_enabled',
                'quiet_hours_start', 'quiet_hours_end'
            ]

            for field in updatable_fields:
                if field in data:
                    setattr(settings, field, data[field])

            settings.updated_at = datetime.utcnow()

            return settings

        except Exception as e:
            logger.error(f"Update settings error: {str(e)}")
            raise

    @staticmethod
    def handle_internal_notification(notification_type, user_id, data):
        """Handle notifications from other services"""
        try:
            # Map internal notification types to templates
            templates = {
                'analysis_complete': {
                    'title': 'Analysis Complete',
                    'message': 'Your financial analysis has been completed.',
                    'type': NotificationType.EMAIL
                },
                'report_ready': {
                    'title': 'Report Ready',
                    'message': 'Your requested report is ready for download.',
                    'type': NotificationType.EMAIL
                },
                'subscription_changed': {
                    'title': 'Subscription Updated',
                    'message': 'Your subscription has been updated.',
                    'type': NotificationType.EMAIL
                }
            }

            template = templates.get(notification_type)
            if template:
                NotificationService.send_notification(
                    user_id=user_id,
                    type=template['type'],
                    title=template['title'],
                    message=template['message'],
                    data=data
                )

        except Exception as e:
            logger.error(f"Handle internal notification error: {str(e)}")
            raise