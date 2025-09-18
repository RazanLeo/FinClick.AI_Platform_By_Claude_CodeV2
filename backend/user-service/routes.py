from flask import request, jsonify, current_app, send_file, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import io
import json
from datetime import datetime
from typing import Dict, Any, Optional

from app import app, db, limiter
from models import UserProfile, UsageType
from services import (
    ProfileService, SubscriptionService, UsageService, PreferencesService,
    ActivityService, SettingsService, DashboardService, DataExportService
)
from utils import (
    validate_auth_token, get_user_id_from_token, sanitize_input,
    validate_json_data, handle_errors, require_auth, get_countries_list,
    get_industries_list, get_company_sizes_list, get_languages_list,
    get_timezones_list, get_currencies_list, validate_file_upload,
    log_request, create_response, mask_sensitive_data
)
import logging

logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

def require_profile(f):
    """Decorator to ensure user has a profile"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = g.get('user_id')
        if not user_id:
            return create_response({'error': 'Authentication required'}, 401)

        profile = ProfileService.get_profile(user_id)
        if not profile:
            return create_response({'error': 'Profile not found'}, 404)

        g.profile = profile
        return f(*args, **kwargs)
    return decorated_function

def check_subscription_limits(usage_type: str, amount: float = 1.0):
    """Decorator to check subscription limits before executing action"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.get('user_id')
            if not user_id:
                return create_response({'error': 'Authentication required'}, 401)

            can_use, error = SubscriptionService.check_usage_limits(user_id, usage_type, amount)
            if not can_use:
                return create_response({'error': error}, 403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== Profile Management Routes ====================

@app.route('/api/v1/profile', methods=['POST'])
@require_auth
@limiter.limit("10 per hour")
def create_profile():
    """Create user profile"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return create_response({'error': 'Invalid JSON data'}, 400)

        # Validate required fields
        required_fields = ['company_name', 'job_title', 'industry', 'country']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return create_response({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, 400)

        # Create profile
        profile, error = ProfileService.create_profile(user_id, data)
        if error:
            return create_response({'error': error}, 400)

        # Log profile creation
        log_request(user_id, 'profile_created', 'Profile created successfully')

        return create_response({
            'message': 'Profile created successfully',
            'profile': profile.to_dict()
        }, 201)

    except Exception as e:
        logger.error(f"Profile creation error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/profile', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("100 per hour")
def get_profile():
    """Get user profile"""
    try:
        profile = g.profile

        # Get related data
        subscription = SubscriptionService.get_subscription(g.user_id)
        preferences = PreferencesService.get_preferences(g.user_id)

        profile_data = profile.to_dict()
        profile_data['subscription'] = subscription.to_dict() if subscription else None
        profile_data['preferences'] = preferences.to_dict() if preferences else None

        return create_response({
            'profile': profile_data
        }, 200)

    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/profile', methods=['PUT'])
@require_auth
@require_profile
@limiter.limit("20 per hour")
def update_profile():
    """Update user profile"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return create_response({'error': 'Invalid JSON data'}, 400)

        # Update profile
        profile, error = ProfileService.update_profile(user_id, data)
        if error:
            return create_response({'error': error}, 400)

        # Log profile update
        log_request(user_id, 'profile_updated', 'Profile updated successfully')

        return create_response({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }, 200)

    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/profile/avatar', methods=['POST'])
@require_auth
@require_profile
@limiter.limit("5 per hour")
@check_subscription_limits('file_upload', 1)
def upload_avatar():
    """Upload user avatar"""
    try:
        user_id = g.user_id

        if 'avatar' not in request.files:
            return create_response({'error': 'No avatar file provided'}, 400)

        file = request.files['avatar']
        if file.filename == '':
            return create_response({'error': 'No file selected'}, 400)

        # Validate file
        valid, error = validate_file_upload(file, ['png', 'jpg', 'jpeg', 'gif'], max_size=5*1024*1024)
        if not valid:
            return create_response({'error': error}, 400)

        # Upload avatar
        file_data = file.read()
        avatar_url, error = ProfileService.upload_avatar(user_id, file_data, file.filename)
        if error:
            return create_response({'error': error}, 500)

        # Record usage
        UsageService.record_usage(
            user_id,
            UsageType.FILE_UPLOAD,
            1,
            resource_name=file.filename,
            metadata={'type': 'avatar', 'size': len(file_data)}
        )

        # Log avatar upload
        log_request(user_id, 'avatar_uploaded', 'Avatar uploaded successfully')

        return create_response({
            'message': 'Avatar uploaded successfully',
            'avatar_url': avatar_url
        }, 200)

    except Exception as e:
        logger.error(f"Avatar upload error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/profile/avatar', methods=['DELETE'])
@require_auth
@require_profile
@limiter.limit("10 per hour")
def delete_avatar():
    """Delete user avatar"""
    try:
        user_id = g.user_id

        success, error = ProfileService.delete_avatar(user_id)
        if not success:
            return create_response({'error': error}, 400)

        # Log avatar deletion
        log_request(user_id, 'avatar_deleted', 'Avatar deleted successfully')

        return create_response({
            'message': 'Avatar deleted successfully'
        }, 200)

    except Exception as e:
        logger.error(f"Avatar deletion error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/profile/onboarding', methods=['POST'])
@require_auth
@require_profile
@limiter.limit("5 per hour")
def complete_onboarding():
    """Complete user onboarding"""
    try:
        user_id = g.user_id
        data = request.get_json() or {}

        success, error = ProfileService.complete_onboarding(user_id, data)
        if not success:
            return create_response({'error': error}, 400)

        # Log onboarding completion
        log_request(user_id, 'onboarding_completed', 'Onboarding completed successfully')

        return create_response({
            'message': 'Onboarding completed successfully'
        }, 200)

    except Exception as e:
        logger.error(f"Onboarding completion error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Subscription Management Routes ====================

@app.route('/api/v1/subscription', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("100 per hour")
def get_subscription():
    """Get user subscription details"""
    try:
        user_id = g.user_id
        subscription = SubscriptionService.get_subscription(user_id)

        if not subscription:
            return create_response({'error': 'Subscription not found'}, 404)

        return create_response({
            'subscription': subscription.to_dict()
        }, 200)

    except Exception as e:
        logger.error(f"Get subscription error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/subscription', methods=['PUT'])
@require_auth
@require_profile
@limiter.limit("10 per hour")
def update_subscription():
    """Update user subscription (admin or billing webhook)"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return create_response({'error': 'Invalid JSON data'}, 400)

        subscription, error = SubscriptionService.update_subscription(user_id, data)
        if error:
            return create_response({'error': error}, 400)

        # Log subscription update
        log_request(user_id, 'subscription_updated', 'Subscription updated successfully')

        return create_response({
            'message': 'Subscription updated successfully',
            'subscription': subscription.to_dict()
        }, 200)

    except Exception as e:
        logger.error(f"Subscription update error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/subscription/cancel', methods=['POST'])
@require_auth
@require_profile
@limiter.limit("5 per hour")
def cancel_subscription():
    """Cancel user subscription"""
    try:
        user_id = g.user_id

        success, error = SubscriptionService.cancel_subscription(user_id)
        if not success:
            return create_response({'error': error}, 400)

        # Log subscription cancellation
        log_request(user_id, 'subscription_cancelled', 'Subscription cancelled successfully')

        return create_response({
            'message': 'Subscription cancelled successfully'
        }, 200)

    except Exception as e:
        logger.error(f"Subscription cancellation error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Usage Tracking Routes ====================

@app.route('/api/v1/usage/stats', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("100 per hour")
def get_usage_stats():
    """Get user usage statistics"""
    try:
        user_id = g.user_id
        period_days = request.args.get('period_days', 30, type=int)

        if period_days not in [7, 30, 90]:
            period_days = 30

        usage_stats = UsageService.get_usage_stats(user_id, period_days)

        if not usage_stats:
            return create_response({'error': 'Unable to retrieve usage statistics'}, 500)

        return create_response({
            'usage_stats': usage_stats
        }, 200)

    except Exception as e:
        logger.error(f"Get usage stats error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/usage/record', methods=['POST'])
@require_auth
@require_profile
@limiter.limit("1000 per hour")
def record_usage():
    """Record usage (internal API for other services)"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data or 'usage_type' not in data:
            return create_response({'error': 'Missing usage_type'}, 400)

        usage_type = UsageType(data['usage_type'])
        amount = data.get('amount', 1.0)
        resource_id = data.get('resource_id')
        resource_name = data.get('resource_name')
        metadata = data.get('metadata', {})

        success, error = UsageService.record_usage(
            user_id, usage_type, amount, resource_id, resource_name, metadata
        )

        if not success:
            return create_response({'error': error}, 400)

        return create_response({
            'message': 'Usage recorded successfully'
        }, 200)

    except ValueError as e:
        return create_response({'error': f'Invalid usage_type: {str(e)}'}, 400)
    except Exception as e:
        logger.error(f"Record usage error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Preferences Management Routes ====================

@app.route('/api/v1/preferences', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("100 per hour")
def get_preferences():
    """Get user preferences"""
    try:
        user_id = g.user_id
        preferences = PreferencesService.get_preferences(user_id)

        return create_response({
            'preferences': preferences.to_dict() if preferences else None
        }, 200)

    except Exception as e:
        logger.error(f"Get preferences error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/preferences', methods=['PUT'])
@require_auth
@require_profile
@limiter.limit("20 per hour")
def update_preferences():
    """Update user preferences"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data:
            return create_response({'error': 'Invalid JSON data'}, 400)

        preferences, error = PreferencesService.update_preferences(user_id, data)
        if error:
            return create_response({'error': error}, 400)

        # Log preferences update
        log_request(user_id, 'preferences_updated', 'Preferences updated successfully')

        return create_response({
            'message': 'Preferences updated successfully',
            'preferences': preferences.to_dict()
        }, 200)

    except Exception as e:
        logger.error(f"Preferences update error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Activity Tracking Routes ====================

@app.route('/api/v1/activities', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("100 per hour")
def get_activities():
    """Get user activities with pagination"""
    try:
        user_id = g.user_id
        limit = min(request.args.get('limit', 50, type=int), 100)
        offset = request.args.get('offset', 0, type=int)
        activity_type = request.args.get('activity_type')

        activities = ActivityService.get_user_activities(user_id, limit, offset, activity_type)

        return create_response({
            'activities': [activity.to_dict() for activity in activities],
            'limit': limit,
            'offset': offset,
            'count': len(activities)
        }, 200)

    except Exception as e:
        logger.error(f"Get activities error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/activities/summary', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("50 per hour")
def get_activity_summary():
    """Get activity summary"""
    try:
        user_id = g.user_id
        days = request.args.get('days', 7, type=int)

        if days not in [7, 30, 90]:
            days = 7

        summary = ActivityService.get_activity_summary(user_id, days)

        if not summary:
            return create_response({'error': 'Unable to retrieve activity summary'}, 500)

        return create_response({
            'activity_summary': summary
        }, 200)

    except Exception as e:
        logger.error(f"Get activity summary error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Settings Management Routes ====================

@app.route('/api/v1/settings', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("100 per hour")
def get_all_settings():
    """Get all user settings"""
    try:
        user_id = g.user_id
        settings = SettingsService.get_all_settings(user_id)

        return create_response({
            'settings': settings
        }, 200)

    except Exception as e:
        logger.error(f"Get settings error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/settings/<setting_key>', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("200 per hour")
def get_setting(setting_key):
    """Get specific user setting"""
    try:
        user_id = g.user_id
        setting_value = SettingsService.get_setting(user_id, setting_key)

        return create_response({
            'setting_key': setting_key,
            'setting_value': setting_value
        }, 200)

    except Exception as e:
        logger.error(f"Get setting error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/settings/<setting_key>', methods=['PUT'])
@require_auth
@require_profile
@limiter.limit("50 per hour")
def set_setting(setting_key):
    """Set user setting"""
    try:
        user_id = g.user_id
        data = request.get_json()

        if not data or 'setting_value' not in data:
            return create_response({'error': 'Missing setting_value'}, 400)

        setting_value = data['setting_value']

        success, error = SettingsService.set_setting(user_id, setting_key, setting_value)
        if not success:
            return create_response({'error': error}, 400)

        # Log setting change
        log_request(user_id, 'setting_changed', f'Setting {setting_key} updated')

        return create_response({
            'message': 'Setting updated successfully',
            'setting_key': setting_key,
            'setting_value': setting_value
        }, 200)

    except Exception as e:
        logger.error(f"Set setting error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/settings/<setting_key>', methods=['DELETE'])
@require_auth
@require_profile
@limiter.limit("20 per hour")
def delete_setting(setting_key):
    """Delete user setting"""
    try:
        user_id = g.user_id

        success, error = SettingsService.delete_setting(user_id, setting_key)
        if not success:
            return create_response({'error': error}, 400)

        # Log setting deletion
        log_request(user_id, 'setting_deleted', f'Setting {setting_key} deleted')

        return create_response({
            'message': 'Setting deleted successfully'
        }, 200)

    except Exception as e:
        logger.error(f"Delete setting error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Dashboard Routes ====================

@app.route('/api/v1/dashboard', methods=['GET'])
@require_auth
@require_profile
@limiter.limit("50 per hour")
def get_dashboard():
    """Get comprehensive dashboard data"""
    try:
        user_id = g.user_id
        dashboard_data = DashboardService.get_dashboard_data(user_id)

        if not dashboard_data:
            return create_response({'error': 'Unable to retrieve dashboard data'}, 500)

        return create_response({
            'dashboard': dashboard_data
        }, 200)

    except Exception as e:
        logger.error(f"Get dashboard error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Data Export & GDPR Routes ====================

@app.route('/api/v1/data/export', methods=['POST'])
@require_auth
@require_profile
@limiter.limit("3 per day")
def export_user_data():
    """Export all user data (GDPR compliance)"""
    try:
        user_id = g.user_id
        export_data = DataExportService.export_user_data(user_id)

        if not export_data:
            return create_response({'error': 'Unable to export user data'}, 500)

        # Create JSON file in memory
        json_data = json.dumps(export_data, indent=2, default=str)
        json_bytes = io.BytesIO(json_data.encode('utf-8'))

        # Log data export
        log_request(user_id, 'data_exported', 'User data exported (GDPR)')

        return send_file(
            json_bytes,
            as_attachment=True,
            download_name=f'finclick_user_data_{user_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json',
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Data export error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/data/delete', methods=['DELETE'])
@require_auth
@require_profile
@limiter.limit("1 per day")
def delete_user_data():
    """Delete all user data (GDPR right to be forgotten)"""
    try:
        user_id = g.user_id
        data = request.get_json()

        # Require confirmation
        if not data or data.get('confirmation') != 'DELETE_ALL_MY_DATA':
            return create_response({
                'error': 'Data deletion requires confirmation. Send {"confirmation": "DELETE_ALL_MY_DATA"}'
            }, 400)

        success, error = DataExportService.delete_user_data(user_id)
        if not success:
            return create_response({'error': error}, 400)

        return create_response({
            'message': 'All user data has been permanently deleted'
        }, 200)

    except Exception as e:
        logger.error(f"Data deletion error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Helper & Utility Routes ====================

@app.route('/api/v1/utils/countries', methods=['GET'])
@limiter.limit("100 per hour")
def get_countries():
    """Get list of countries"""
    try:
        countries = get_countries_list()
        return create_response({'countries': countries}, 200)
    except Exception as e:
        logger.error(f"Get countries error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/utils/industries', methods=['GET'])
@limiter.limit("100 per hour")
def get_industries():
    """Get list of industries"""
    try:
        industries = get_industries_list()
        return create_response({'industries': industries}, 200)
    except Exception as e:
        logger.error(f"Get industries error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/utils/company-sizes', methods=['GET'])
@limiter.limit("100 per hour")
def get_company_sizes():
    """Get list of company sizes"""
    try:
        company_sizes = get_company_sizes_list()
        return create_response({'company_sizes': company_sizes}, 200)
    except Exception as e:
        logger.error(f"Get company sizes error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/utils/languages', methods=['GET'])
@limiter.limit("100 per hour")
def get_languages():
    """Get list of supported languages"""
    try:
        languages = get_languages_list()
        return create_response({'languages': languages}, 200)
    except Exception as e:
        logger.error(f"Get languages error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/utils/timezones', methods=['GET'])
@limiter.limit("100 per hour")
def get_timezones():
    """Get list of timezones"""
    try:
        timezones = get_timezones_list()
        return create_response({'timezones': timezones}, 200)
    except Exception as e:
        logger.error(f"Get timezones error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

@app.route('/api/v1/utils/currencies', methods=['GET'])
@limiter.limit("100 per hour")
def get_currencies():
    """Get list of currencies"""
    try:
        currencies = get_currencies_list()
        return create_response({'currencies': currencies}, 200)
    except Exception as e:
        logger.error(f"Get currencies error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Health Check Routes ====================

@app.route('/health', methods=['GET'])
@limiter.limit("1000 per hour")
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')

        return create_response({
            'status': 'healthy',
            'service': 'user-service',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }, 200)

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return create_response({
            'status': 'unhealthy',
            'service': 'user-service',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }, 503)

@app.route('/api/v1/status', methods=['GET'])
@require_auth
@limiter.limit("100 per hour")
def service_status():
    """Service status for authenticated users"""
    try:
        user_id = g.user_id
        profile = ProfileService.get_profile(user_id)

        return create_response({
            'service': 'user-service',
            'status': 'operational',
            'user_status': 'authenticated',
            'profile_exists': profile is not None,
            'timestamp': datetime.utcnow().isoformat()
        }, 200)

    except Exception as e:
        logger.error(f"Service status error: {str(e)}")
        return create_response({'error': 'Internal server error'}, 500)

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_response({
        'error': 'Endpoint not found',
        'message': 'The requested resource was not found'
    }, 404)

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return create_response({
        'error': 'Method not allowed',
        'message': 'The request method is not allowed for this endpoint'
    }, 405)

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return create_response({
        'error': 'Rate limit exceeded',
        'message': f'Rate limit exceeded: {e.description}'
    }, 429)

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return create_response({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }, 500)

# ==================== Request/Response Middleware ====================

@app.before_request
def before_request():
    """Before request middleware"""
    # Set request start time for logging
    g.start_time = datetime.utcnow()

    # Log request (exclude health checks)
    if not request.endpoint or request.endpoint not in ['health_check']:
        logger.info(f"{request.method} {request.path} - {get_remote_address()}")

@app.after_request
def after_request(response):
    """After request middleware"""
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Log response time (exclude health checks)
    if hasattr(g, 'start_time') and (not request.endpoint or request.endpoint not in ['health_check']):
        duration = (datetime.utcnow() - g.start_time).total_seconds()
        logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")

    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)