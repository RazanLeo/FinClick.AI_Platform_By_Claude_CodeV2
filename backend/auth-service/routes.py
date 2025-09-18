from flask import request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt
)
from functools import wraps
import qrcode
import io
import base64
from datetime import datetime, timedelta

from app import app, db, limiter
from models import (
    User, LoginSession, PasswordResetToken, EmailVerificationToken,
    BlacklistedToken, OAuthState, AuditLog, ApiKey, UserRole, AuthProvider
)
from services import (
    AuthService, MFAService, OAuthService, EmailService, SecurityService,
    PermissionService, SessionService, ApiKeyService, AuditService
)
from utils import (
    validate_password, validate_email, get_client_ip, get_user_agent,
    generate_qr_code, sanitize_input, mask_email, mask_phone
)
import logging

logger = logging.getLogger(__name__)

# Decorators
def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user or not user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user or not user.has_role(role):
                return jsonify({'error': 'Insufficient role permissions'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Enhanced user registration endpoint"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Sanitize input
        for field in ['email', 'username', 'first_name', 'last_name']:
            data[field] = sanitize_input(data[field])

        # Additional validation
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check password strength
        is_strong, password_errors = validate_password(data['password'])
        if not is_strong:
            return jsonify({
                'error': 'Password does not meet requirements',
                'details': password_errors
            }), 400

        # Create new user
        try:
            user = AuthService.create_user(
                email=data['email'],
                username=data['username'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone'),
                role=UserRole.TRIAL,
                language=data.get('language', 'en')
            )

            db.session.commit()

            # Send verification email
            success, message = AuthService.send_verification_email(user)
            if not success:
                logger.warning(f"Failed to send verification email: {message}")

            return jsonify({
                'message': 'User registered successfully',
                'user': user.to_dict(),
                'verification_email_sent': success
            }), 201

        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Enhanced user login endpoint with MFA support"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        email = sanitize_input(data['email'])
        password = data['password']
        mfa_token = data.get('mfa_token')
        remember_me = data.get('remember_me', False)

        # Get client info
        ip_address = get_client_ip()
        user_agent = get_user_agent()

        # Authenticate user
        user, error_message = AuthService.authenticate_user(
            email, password, ip_address, user_agent
        )

        if not user:
            return jsonify({'error': error_message}), 401

        # Check MFA if enabled
        if user.mfa_enabled:
            if not mfa_token:
                return jsonify({
                    'mfa_required': True,
                    'message': 'MFA token required'
                }), 200

            # Verify MFA token
            mfa_valid, mfa_message = MFAService.verify_mfa(user, mfa_token)
            if not mfa_valid:
                return jsonify({'error': mfa_message}), 401

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Create session
        session = AuthService.create_session(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            remember_me=remember_me
        )

        db.session.commit()

        # Send login notification if from new location
        is_suspicious, _ = SecurityService.detect_suspicious_activity(
            user.id, 'new_location_login', {'ip_address': ip_address}
        )

        if is_suspicious:
            EmailService.send_login_notification(user, ip_address, user_agent)

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'session_id': session.id
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Enhanced user logout endpoint"""
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()['jti']

        # Get token expiration from JWT
        token_exp = get_jwt().get('exp')
        expires_at = datetime.fromtimestamp(token_exp) if token_exp else datetime.utcnow() + timedelta(hours=24)

        # Add token to blacklist
        SecurityService.blacklist_token(jti, 'access', current_user_id, expires_at)

        # Deactivate current session
        session_count = AuthService.deactivate_user_sessions(
            current_user_id,
            exclude_session_id=request.headers.get('X-Session-ID')
        )

        db.session.commit()

        return jsonify({
            'message': 'Logged out successfully',
            'sessions_revoked': session_count
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/logout-all', methods=['POST'])
@jwt_required()
def logout_all():
    """Logout from all sessions"""
    try:
        current_user_id = get_jwt_identity()

        # Revoke all user sessions
        session_count = AuthService.deactivate_user_sessions(current_user_id)

        db.session.commit()

        return jsonify({
            'message': 'Logged out from all sessions',
            'sessions_revoked': session_count
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Logout all error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Enhanced refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()['jti']

        # Check if refresh token is blacklisted
        if SecurityService.is_token_blacklisted(jti):
            return jsonify({'error': 'Token has been revoked'}), 401

        # Check if user exists and is active
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401

        # Create new access token
        new_access_token = create_access_token(identity=current_user_id)

        return jsonify({
            'access_token': new_access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500

# Email Verification Routes
@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    """Enhanced email verification endpoint"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Verification token required'}), 400

        # Verify email token
        user, error_message = AuthService.verify_email_token(token)
        if not user:
            return jsonify({'error': error_message}), 400

        return jsonify({
            'message': 'Email verified successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Email verification error: {str(e)}")
        return jsonify({'error': 'Email verification failed'}), 500

@app.route('/api/auth/resend-verification', methods=['POST'])
@limiter.limit("3 per hour")
@jwt_required()
def resend_verification():
    """Resend email verification"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.email_verified:
            return jsonify({'message': 'Email already verified'}), 200

        # Send verification email
        success, message = AuthService.send_verification_email(user)

        if success:
            return jsonify({'message': 'Verification email sent successfully'}), 200
        else:
            return jsonify({'error': message}), 500

    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        return jsonify({'error': 'Failed to resend verification email'}), 500

# Password Management Routes
@app.route('/api/auth/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """Enhanced forgot password endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email required'}), 400

        email = sanitize_input(email)

        # Always return success for security (prevent email enumeration)
        success, message = AuthService.create_password_reset_token(email)

        return jsonify({
            'message': 'Password reset email sent if account exists'
        }), 200

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    """Enhanced reset password endpoint"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')

        if not token or not new_password:
            return jsonify({'error': 'Token and password required'}), 400

        # Reset password
        success, message = AuthService.reset_password(token, new_password)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Enhanced change password endpoint"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password required'}), 400

        user = User.query.get(current_user_id)
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Validate new password
        is_strong, password_errors = validate_password(new_password)
        if not is_strong:
            return jsonify({
                'error': 'New password does not meet requirements',
                'details': password_errors
            }), 400

        # Update password
        user.set_password(new_password)

        # Log password change
        AuditLog.log_action(
            user_id=user.id,
            event_type='password_changed',
            event_description='Password changed by user',
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )

        # Revoke all other sessions for security
        AuthService.deactivate_user_sessions(
            user.id,
            exclude_session_id=request.headers.get('X-Session-ID')
        )

        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500

# MFA Routes
@app.route('/api/auth/mfa/setup', methods=['POST'])
@jwt_required()
def setup_mfa():
    """Setup MFA for user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.mfa_enabled:
            return jsonify({'error': 'MFA already enabled'}), 400

        # Setup MFA
        mfa_data = MFAService.setup_mfa(user)
        if not mfa_data:
            return jsonify({'error': 'Failed to setup MFA'}), 500

        # Generate QR code
        qr_code_data = generate_qr_code(mfa_data['qr_url'])
        qr_code_b64 = base64.b64encode(qr_code_data).decode('utf-8')

        return jsonify({
            'secret': mfa_data['secret'],
            'qr_code': f"data:image/png;base64,{qr_code_b64}",
            'backup_codes': mfa_data['backup_codes'],
            'qr_url': mfa_data['qr_url']
        }), 200

    except Exception as e:
        logger.error(f"MFA setup error: {str(e)}")
        return jsonify({'error': 'MFA setup failed'}), 500

@app.route('/api/auth/mfa/enable', methods=['POST'])
@jwt_required()
def enable_mfa():
    """Enable MFA after verification"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()

        token = data.get('token')
        if not token:
            return jsonify({'error': 'MFA token required'}), 400

        # Enable MFA
        success, message = MFAService.enable_mfa(user, token)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        logger.error(f"MFA enable error: {str(e)}")
        return jsonify({'error': 'Failed to enable MFA'}), 500

@app.route('/api/auth/mfa/disable', methods=['POST'])
@jwt_required()
def disable_mfa():
    """Disable MFA with password confirmation"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()

        password = data.get('password')
        if not password:
            return jsonify({'error': 'Password required to disable MFA'}), 400

        # Disable MFA
        success, message = MFAService.disable_mfa(user, password)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        logger.error(f"MFA disable error: {str(e)}")
        return jsonify({'error': 'Failed to disable MFA'}), 500

@app.route('/api/auth/mfa/verify', methods=['POST'])
@jwt_required()
def verify_mfa():
    """Verify MFA token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()

        token = data.get('token')
        is_backup_code = data.get('is_backup_code', False)

        if not token:
            return jsonify({'error': 'Token required'}), 400

        # Verify MFA
        success, message = MFAService.verify_mfa(user, token, is_backup_code)

        return jsonify({
            'valid': success,
            'message': message
        }), 200 if success else 400

    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}")
        return jsonify({'error': 'MFA verification failed'}), 500

# OAuth Routes
@app.route('/api/auth/oauth/<provider>/url', methods=['GET'])
def get_oauth_url(provider):
    """Get OAuth authorization URL"""
    try:
        if provider not in ['google', 'facebook']:
            return jsonify({'error': 'Unsupported OAuth provider'}), 400

        # Create OAuth state
        auth_provider = AuthProvider.GOOGLE if provider == 'google' else AuthProvider.FACEBOOK
        state = OAuthService.create_oauth_state(auth_provider)

        if not state:
            return jsonify({'error': 'Failed to create OAuth state'}), 500

        # Generate OAuth URL
        if provider == 'google':
            client_id = current_app.config.get('GOOGLE_CLIENT_ID')
            redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
            scope = 'openid email profile'

            oauth_url = (
                f"https://accounts.google.com/o/oauth2/auth?"
                f"client_id={client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={scope}&"
                f"response_type=code&"
                f"state={state}"
            )
        else:  # Facebook
            client_id = current_app.config.get('FACEBOOK_CLIENT_ID')
            redirect_uri = current_app.config.get('FACEBOOK_REDIRECT_URI')
            scope = 'email'

            oauth_url = (
                f"https://www.facebook.com/v18.0/dialog/oauth?"
                f"client_id={client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={scope}&"
                f"response_type=code&"
                f"state={state}"
            )

        return jsonify({
            'oauth_url': oauth_url,
            'state': state
        }), 200

    except Exception as e:
        logger.error(f"OAuth URL generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate OAuth URL'}), 500

@app.route('/api/auth/oauth/<provider>/callback', methods=['POST'])
def oauth_callback(provider):
    """Handle OAuth callback"""
    try:
        data = request.get_json()
        code = data.get('code')
        state = data.get('state')

        if not code or not state:
            return jsonify({'error': 'Code and state required'}), 400

        # Verify OAuth state
        auth_provider = AuthProvider.GOOGLE if provider == 'google' else AuthProvider.FACEBOOK
        if not OAuthService.verify_oauth_state(state, auth_provider):
            return jsonify({'error': 'Invalid OAuth state'}), 400

        # Exchange code for access token and get user info
        if provider == 'google':
            # Exchange code for token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'client_id': current_app.config.get('GOOGLE_CLIENT_ID'),
                'client_secret': current_app.config.get('GOOGLE_CLIENT_SECRET'),
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': current_app.config.get('GOOGLE_REDIRECT_URI')
            }

            import requests
            token_response = requests.post(token_url, data=token_data)
            token_json = token_response.json()

            if 'access_token' not in token_json:
                return jsonify({'error': 'Failed to get access token'}), 400

            # Get user info
            user_info = OAuthService.verify_google_token(token_json['access_token'])
            if not user_info:
                return jsonify({'error': 'Failed to get user info'}), 400

            email = user_info.get('email')
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            provider_user_id = user_info.get('id')

        else:  # Facebook
            # Similar implementation for Facebook
            return jsonify({'error': 'Facebook OAuth not fully implemented'}), 501

        if not email or not provider_user_id:
            return jsonify({'error': 'Incomplete user information from provider'}), 400

        # Find or create user
        user = OAuthService.find_or_create_oauth_user(
            auth_provider, provider_user_id, email, first_name, last_name
        )

        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Create session
        session = AuthService.create_session(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )

        db.session.commit()

        return jsonify({
            'message': f'{provider.title()} OAuth login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'session_id': session.id
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"{provider} OAuth error: {str(e)}")
        return jsonify({'error': f'{provider.title()} OAuth failed'}), 500

# Profile Routes
@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile with enhanced information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get additional profile information
        profile_data = user.to_dict()
        profile_data.update({
            'active_sessions': SessionService.get_active_session_count(user.id),
            'permissions': PermissionService.get_user_permissions(user),
            'masked_email': mask_email(user.email),
            'masked_phone': mask_phone(user.phone) if user.phone else None
        })

        return jsonify({'user': profile_data}), 200

    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'phone', 'language', 'timezone']

        for field in updatable_fields:
            if field in data:
                if field in ['first_name', 'last_name']:
                    setattr(user, field, sanitize_input(data[field]))
                else:
                    setattr(user, field, data[field])

        # Log profile update
        AuditLog.log_action(
            user_id=user.id,
            event_type='profile_updated',
            event_description='User profile updated',
            metadata={'updated_fields': list(data.keys())},
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

# Session Management Routes
@app.route('/api/auth/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Get user's active sessions with enhanced details"""
    try:
        current_user_id = get_jwt_identity()
        sessions = SessionService.get_user_sessions(current_user_id)

        return jsonify({'sessions': sessions}), 200

    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        return jsonify({'error': 'Failed to get sessions'}), 500

@app.route('/api/auth/sessions/<session_id>', methods=['DELETE'])
@jwt_required()
def revoke_session(session_id):
    """Revoke a specific session"""
    try:
        current_user_id = get_jwt_identity()

        success, message = SessionService.revoke_session(session_id, current_user_id)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 404

    except Exception as e:
        logger.error(f"Revoke session error: {str(e)}")
        return jsonify({'error': 'Failed to revoke session'}), 500

# API Key Management Routes
@app.route('/api/auth/api-keys', methods=['GET'])
@jwt_required()
def get_api_keys():
    """Get user's API keys"""
    try:
        current_user_id = get_jwt_identity()

        api_keys = ApiKey.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).all()

        keys_data = []
        for key in api_keys:
            keys_data.append({
                'id': key.id,
                'name': key.name,
                'prefix': key.key_prefix,
                'permissions': key.permissions,
                'rate_limit': key.rate_limit,
                'created_at': key.created_at.isoformat(),
                'last_used_at': key.last_used_at.isoformat() if key.last_used_at else None,
                'expires_at': key.expires_at.isoformat() if key.expires_at else None
            })

        return jsonify({'api_keys': keys_data}), 200

    except Exception as e:
        logger.error(f"Get API keys error: {str(e)}")
        return jsonify({'error': 'Failed to get API keys'}), 500

@app.route('/api/auth/api-keys', methods=['POST'])
@jwt_required()
def create_api_key():
    """Create new API key"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        name = data.get('name')
        permissions = data.get('permissions', [])
        rate_limit = data.get('rate_limit', 1000)
        expires_days = data.get('expires_days')

        if not name:
            return jsonify({'error': 'API key name required'}), 400

        # Create API key
        api_key_data = ApiKeyService.create_api_key(
            current_user_id, name, permissions, rate_limit, expires_days
        )

        if api_key_data:
            return jsonify({
                'message': 'API key created successfully',
                'api_key': api_key_data
            }), 201
        else:
            return jsonify({'error': 'Failed to create API key'}), 500

    except Exception as e:
        logger.error(f"Create API key error: {str(e)}")
        return jsonify({'error': 'Failed to create API key'}), 500

@app.route('/api/auth/api-keys/<api_key_id>', methods=['DELETE'])
@jwt_required()
def revoke_api_key(api_key_id):
    """Revoke API key"""
    try:
        current_user_id = get_jwt_identity()

        success, message = ApiKeyService.revoke_api_key(current_user_id, api_key_id)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 404

    except Exception as e:
        logger.error(f"Revoke API key error: {str(e)}")
        return jsonify({'error': 'Failed to revoke API key'}), 500

# Admin Routes
@app.route('/api/auth/admin/users', methods=['GET'])
@require_role(UserRole.ADMIN)
def admin_get_users():
    """Admin: Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')

        query = User.query

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.email.ilike(search_term)) |
                (User.username.ilike(search_term)) |
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term))
            )

        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        users_data = [user.to_dict() for user in pagination.items]

        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total
            }
        }), 200

    except Exception as e:
        logger.error(f"Admin get users error: {str(e)}")
        return jsonify({'error': 'Failed to get users'}), 500

@app.route('/api/auth/admin/users/<user_id>/role', methods=['PUT'])
@require_role(UserRole.ADMIN)
def admin_update_user_role(user_id):
    """Admin: Update user role"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        new_role_str = data.get('role')
        if not new_role_str:
            return jsonify({'error': 'Role required'}), 400

        # Validate role
        try:
            new_role = UserRole(new_role_str)
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400

        # Update role
        success, message = PermissionService.update_user_role(
            user_id, new_role, current_user_id
        )

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        logger.error(f"Admin update user role error: {str(e)}")
        return jsonify({'error': 'Failed to update user role'}), 500

# Audit Routes
@app.route('/api/auth/audit/logs', methods=['GET'])
@jwt_required()
def get_user_audit_logs():
    """Get user's audit logs"""
    try:
        current_user_id = get_jwt_identity()

        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        event_type = request.args.get('event_type')

        logs = AuditService.get_user_audit_logs(
            current_user_id, limit, offset, event_type
        )

        return jsonify({'audit_logs': logs}), 200

    except Exception as e:
        logger.error(f"Get audit logs error: {str(e)}")
        return jsonify({'error': 'Failed to get audit logs'}), 500

@app.route('/api/auth/admin/audit/logs', methods=['GET'])
@require_role(UserRole.ADMIN)
def admin_get_audit_logs():
    """Admin: Get system audit logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        event_type = request.args.get('event_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Parse dates if provided
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.fromisoformat(start_date)
        if end_date:
            end_datetime = datetime.fromisoformat(end_date)

        logs = AuditService.get_system_audit_logs(
            limit, offset, event_type, start_datetime, end_datetime
        )

        return jsonify({'audit_logs': logs}), 200

    except Exception as e:
        logger.error(f"Admin get audit logs error: {str(e)}")
        return jsonify({'error': 'Failed to get audit logs'}), 500

# Utility Routes
@app.route('/api/auth/validate', methods=['GET'])
@jwt_required()
def validate_token():
    """Validate JWT token and return user info"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify({'valid': False, 'error': 'User not found or inactive'}), 401

        return jsonify({
            'valid': True,
            'user': user.to_dict(),
            'permissions': PermissionService.get_user_permissions(user)
        }), 200

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401

@app.route('/api/auth/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')

        # Get service stats
        total_users = User.query.count()
        active_sessions = LoginSession.query.filter_by(is_active=True).count()

        return jsonify({
            'status': 'healthy',
            'service': 'auth-service',
            'timestamp': datetime.utcnow().isoformat(),
            'stats': {
                'total_users': total_users,
                'active_sessions': active_sessions
            }
        }), 200

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'auth-service',
            'error': str(e)
        }), 500

# Error Handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded', 'message': 'Too many requests'}), 429

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500