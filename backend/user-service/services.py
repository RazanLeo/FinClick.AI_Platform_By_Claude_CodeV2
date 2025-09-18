import os
import requests
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from app import db, current_app
from models import (
    UserProfile, UserSubscription, UsageRecord, UserSettings,
    UserActivity, UserPreferences, UsageType, SubscriptionStatus
)
import logging
import json

logger = logging.getLogger(__name__)

class UserService:
    """User management service"""

    @staticmethod
    def get_or_create_profile(user_id):
        """Get existing profile or create new one"""
        profile = UserProfile.query.filter_by(user_id=user_id).first()

        if not profile:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                onboarding_step=1,
                onboarding_completed=False,
                tutorial_completed=False
            )
            db.session.add(profile)
            db.session.flush()  # Get profile ID

            # Create default subscription (trial)
            subscription = UserSubscription(
                user_profile_id=profile.id,
                plan_id='trial',
                plan_name='Trial Plan',
                status=SubscriptionStatus.TRIAL,
                trial_end_date=datetime.utcnow() + timedelta(days=14)
            )
            db.session.add(subscription)

            # Create default preferences
            preferences = UserPreferences(
                user_profile_id=profile.id
            )
            db.session.add(preferences)

        return profile

    @staticmethod
    def update_profile(user_id, profile_data):
        """Update user profile"""
        profile = UserService.get_or_create_profile(user_id)

        updatable_fields = [
            'company_name', 'job_title', 'department', 'industry', 'company_size',
            'country', 'timezone', 'language', 'bio', 'website', 'linkedin_url',
            'email_notifications', 'sms_notifications', 'marketing_emails', 'weekly_reports'
        ]

        for field in updatable_fields:
            if field in profile_data:
                setattr(profile, field, profile_data[field])

        return profile

    @staticmethod
    def get_user_settings(user_id):
        """Get user settings as dictionary"""
        profile = UserService.get_or_create_profile(user_id)

        settings = UserSettings.query.filter_by(user_profile_id=profile.id).all()

        settings_dict = {}
        for setting in settings:
            settings_dict[setting.setting_key] = setting.setting_value

        return settings_dict

    @staticmethod
    def update_setting(user_profile_id, key, value):
        """Update or create a user setting"""
        setting = UserSettings.query.filter_by(
            user_profile_id=user_profile_id,
            setting_key=key
        ).first()

        if setting:
            setting.setting_value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = UserSettings(
                user_profile_id=user_profile_id,
                setting_key=key,
                setting_value=value
            )
            db.session.add(setting)

        return setting

    @staticmethod
    def get_user_preferences(user_id):
        """Get user preferences"""
        profile = UserService.get_or_create_profile(user_id)

        preferences = UserPreferences.query.filter_by(user_profile_id=profile.id).first()

        if not preferences:
            preferences = UserPreferences(user_profile_id=profile.id)
            db.session.add(preferences)
            db.session.commit()

        return preferences

    @staticmethod
    def update_user_preferences(user_id, preferences_data):
        """Update user preferences"""
        profile = UserService.get_or_create_profile(user_id)

        preferences = UserPreferences.query.filter_by(user_profile_id=profile.id).first()

        if not preferences:
            preferences = UserPreferences(user_profile_id=profile.id)
            db.session.add(preferences)

        # Update preferences fields
        updatable_fields = [
            'dashboard_layout', 'default_currency', 'date_format', 'number_format',
            'default_analysis_type', 'auto_save_analyses', 'analysis_templates',
            'notification_frequency', 'notification_channels', 'quiet_hours_start',
            'quiet_hours_end', 'default_export_format', 'include_charts_in_export',
            'watermark_exports'
        ]

        for field in updatable_fields:
            if field in preferences_data:
                setattr(preferences, field, preferences_data[field])

        preferences.updated_at = datetime.utcnow()

        return preferences

    @staticmethod
    def log_activity(user_profile_id, activity_type, description, metadata=None, ip_address=None, user_agent=None):
        """Log user activity"""
        activity = UserActivity(
            user_profile_id=user_profile_id,
            activity_type=activity_type,
            description=description,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(activity)
        return activity

    @staticmethod
    def get_user_activities(user_id, page=1, per_page=20, activity_type=None):
        """Get user activities with pagination"""
        profile = UserService.get_or_create_profile(user_id)

        query = UserActivity.query.filter_by(user_profile_id=profile.id)

        if activity_type:
            query = query.filter_by(activity_type=activity_type)

        activities = query.order_by(UserActivity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return activities

    @staticmethod
    def get_dashboard_stats(user_id):
        """Get dashboard statistics for user"""
        profile = UserService.get_or_create_profile(user_id)
        subscription = profile.subscription

        # Get recent activities count
        recent_activities = UserActivity.query.filter(
            UserActivity.user_profile_id == profile.id,
            UserActivity.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()

        # Get usage statistics
        usage_stats = UsageService.get_usage_statistics(user_id, days=30)

        stats = {
            'subscription': subscription.to_dict() if subscription else None,
            'recent_activities': recent_activities,
            'usage_statistics': usage_stats,
            'profile_completion': UserService.calculate_profile_completion(profile),
            'onboarding_status': {
                'step': profile.onboarding_step,
                'completed': profile.onboarding_completed,
                'tutorial_completed': profile.tutorial_completed
            }
        }

        return stats

    @staticmethod
    def calculate_profile_completion(profile):
        """Calculate profile completion percentage"""
        fields_to_check = [
            'company_name', 'job_title', 'department', 'industry',
            'country', 'bio', 'avatar_url'
        ]

        completed_fields = 0
        for field in fields_to_check:
            if getattr(profile, field):
                completed_fields += 1

        return int((completed_fields / len(fields_to_check)) * 100)

    @staticmethod
    def export_user_data(user_id):
        """Export user data for GDPR compliance"""
        profile = UserService.get_or_create_profile(user_id)

        # Collect all user data
        export_data = {
            'profile': profile.to_dict(),
            'subscription': profile.subscription.to_dict() if profile.subscription else None,
            'usage_records': [record.to_dict() for record in profile.usage_records],
            'activities': [activity.to_dict() for activity in UserActivity.query.filter_by(user_profile_id=profile.id).all()],
            'settings': UserService.get_user_settings(user_id),
            'preferences': UserService.get_user_preferences(user_id).to_dict(),
            'exported_at': datetime.utcnow().isoformat()
        }

        # In a real implementation, you would save this to a file and provide download URL
        download_url = f"https://api.finclick.ai/exports/{uuid.uuid4()}.json"
        expires_at = datetime.utcnow() + timedelta(days=7)

        return {
            'download_url': download_url,
            'expires_at': expires_at.isoformat(),
            'data': export_data
        }

    @staticmethod
    def soft_delete_user(user_id):
        """Soft delete user account"""
        try:
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return False

            # Mark for deletion (soft delete)
            profile.deleted_at = datetime.utcnow()

            # Log activity
            UserService.log_activity(
                user_profile_id=profile.id,
                activity_type='account_deletion_requested',
                description='User requested account deletion'
            )

            # Notify other services about account deletion
            try:
                auth_service_url = current_app.config.get('AUTH_SERVICE_URL')
                if auth_service_url:
                    requests.post(f"{auth_service_url}/api/auth/deactivate/{user_id}")
            except Exception as e:
                logger.error(f"Failed to notify auth service: {str(e)}")

            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Soft delete error: {str(e)}")
            db.session.rollback()
            return False

class SubscriptionService:
    """Subscription management service"""

    @staticmethod
    def get_user_subscription(user_id):
        """Get user subscription"""
        profile = UserService.get_or_create_profile(user_id)
        return profile.subscription

    @staticmethod
    def update_subscription(user_id, plan_id, plan_name, limits):
        """Update user subscription"""
        profile = UserService.get_or_create_profile(user_id)
        subscription = profile.subscription

        if not subscription:
            subscription = UserSubscription(user_profile_id=profile.id)
            db.session.add(subscription)

        subscription.plan_id = plan_id
        subscription.plan_name = plan_name
        subscription.status = SubscriptionStatus.ACTIVE

        # Update limits
        subscription.monthly_file_limit = limits.get('files', 10)
        subscription.monthly_analysis_limit = limits.get('analyses', 50)
        subscription.storage_limit_gb = limits.get('storage', 1.0)
        subscription.api_calls_limit = limits.get('api_calls', 1000)

        # Reset usage counters
        subscription.files_used = 0
        subscription.analyses_used = 0
        subscription.storage_used_gb = 0.0
        subscription.api_calls_used = 0

        subscription.updated_at = datetime.utcnow()

        return subscription

    @staticmethod
    def update_usage(subscription, usage_type, amount):
        """Update subscription usage counters"""
        if usage_type == UsageType.FILE_UPLOAD:
            subscription.files_used += amount
        elif usage_type == UsageType.ANALYSIS_REQUEST:
            subscription.analyses_used += amount
        elif usage_type == UsageType.STORAGE_USAGE:
            subscription.storage_used_gb += amount
        elif usage_type == UsageType.API_CALL:
            subscription.api_calls_used += amount

        subscription.updated_at = datetime.utcnow()

    @staticmethod
    def check_usage_limits(user_id, usage_type, amount=1):
        """Check if user can perform action within limits"""
        subscription = SubscriptionService.get_user_subscription(user_id)

        if not subscription:
            return False

        return subscription.can_use_feature(usage_type.value, amount)

class UsageService:
    """Usage tracking service"""

    @staticmethod
    def record_usage(user_profile_id, usage_type, amount, resource_id=None, resource_name=None, metadata=None):
        """Record usage"""
        usage_record = UsageRecord(
            user_profile_id=user_profile_id,
            usage_type=usage_type,
            amount=amount,
            resource_id=resource_id,
            resource_name=resource_name,
            metadata=metadata
        )
        db.session.add(usage_record)
        return usage_record

    @staticmethod
    def get_usage_statistics(user_id, days=30, usage_type=None):
        """Get usage statistics"""
        profile = UserService.get_or_create_profile(user_id)

        # Base query
        query = UsageRecord.query.filter(
            UsageRecord.user_profile_id == profile.id,
            UsageRecord.created_at >= datetime.utcnow() - timedelta(days=days)
        )

        if usage_type:
            try:
                usage_type_enum = UsageType(usage_type)
                query = query.filter_by(usage_type=usage_type_enum)
            except ValueError:
                pass

        records = query.all()

        # Aggregate statistics
        stats = {
            'total_records': len(records),
            'by_type': {},
            'by_day': {},
            'current_subscription': profile.subscription.to_dict() if profile.subscription else None
        }

        # Group by type
        for record in records:
            type_name = record.usage_type.value
            if type_name not in stats['by_type']:
                stats['by_type'][type_name] = {
                    'count': 0,
                    'total_amount': 0
                }
            stats['by_type'][type_name]['count'] += 1
            stats['by_type'][type_name]['total_amount'] += record.amount

        # Group by day
        for record in records:
            day = record.created_at.date().isoformat()
            if day not in stats['by_day']:
                stats['by_day'][day] = {
                    'count': 0,
                    'total_amount': 0
                }
            stats['by_day'][day]['count'] += 1
            stats['by_day'][day]['total_amount'] += record.amount

        return stats

class ProfileService:
    """Profile management service"""

    @staticmethod
    def upload_avatar(file, user_id):
        """Upload user avatar"""
        try:
            # Validate file
            if not file or file.filename == '':
                raise ValueError("No file provided")

            # Secure filename
            filename = secure_filename(file.filename)
            if not filename:
                raise ValueError("Invalid filename")

            # Generate unique filename
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"

            # In a real implementation, you would upload to cloud storage (S3, etc.)
            # For now, we'll return a mock URL
            avatar_url = f"https://cdn.finclick.ai/avatars/{unique_filename}"

            logger.info(f"Avatar uploaded for user {user_id}: {avatar_url}")

            return avatar_url

        except Exception as e:
            logger.error(f"Avatar upload error: {str(e)}")
            raise

    @staticmethod
    def validate_profile_data(data):
        """Validate profile data"""
        errors = []

        # Validate email format if provided
        if 'email' in data:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("Invalid email format")

        # Validate URL formats
        url_fields = ['website', 'linkedin_url']
        for field in url_fields:
            if field in data and data[field]:
                if not data[field].startswith(('http://', 'https://')):
                    errors.append(f"Invalid {field} format")

        return errors

class NotificationService:
    """Service for sending notifications to other services"""

    @staticmethod
    def notify_profile_updated(user_id, profile_data):
        """Notify other services about profile update"""
        try:
            notification_service_url = current_app.config.get('NOTIFICATION_SERVICE_URL')
            if notification_service_url:
                payload = {
                    'type': 'profile_updated',
                    'user_id': user_id,
                    'data': profile_data
                }
                requests.post(f"{notification_service_url}/api/notifications/internal", json=payload)
        except Exception as e:
            logger.error(f"Failed to send profile update notification: {str(e)}")

    @staticmethod
    def notify_subscription_changed(user_id, subscription_data):
        """Notify about subscription changes"""
        try:
            notification_service_url = current_app.config.get('NOTIFICATION_SERVICE_URL')
            if notification_service_url:
                payload = {
                    'type': 'subscription_changed',
                    'user_id': user_id,
                    'data': subscription_data
                }
                requests.post(f"{notification_service_url}/api/notifications/internal", json=payload)
        except Exception as e:
            logger.error(f"Failed to send subscription change notification: {str(e)}")