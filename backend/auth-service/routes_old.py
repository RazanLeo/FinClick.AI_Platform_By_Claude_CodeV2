from flask import request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt
)
from app import app, db, limiter, blacklisted_tokens
from models import User, UserSession, OAuthAccount, PasswordReset, AuditLog, UserRole
from services import AuthService, OAuthService, EmailService
import logging

logger = logging.getLogger(__name__)

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409

        # Create new user
        user = AuthService.create_user(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=UserRole.USER
        )

        # Log registration
        AuditLog.log_action(
            user_id=user.id,
            action='user_registered',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        # Send verification email
        try:
            EmailService.send_verification_email(user)
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        # Authenticate user
        user = AuthService.authenticate_user(data['email'], data['password'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Create session
        session = AuthService.create_session(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        # Update last login
        user.last_login = db.func.now()

        # Log login
        AuditLog.log_action(
            user_id=user.id,
            action='user_login',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()['jti']

        # Add token to blacklist
        blacklisted_tokens.add(jti)

        # Deactivate session
        session = UserSession.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).first()

        if session:
            session.is_active = False

        # Log logout
        AuditLog.log_action(
            user_id=current_user_id,
            action='user_logout',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({'message': 'Logged out successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()

        # Check if user exists and is active
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401

        # Create new access token
        new_access_token = create_access_token(identity=current_user_id)

        return jsonify({
            'access_token': new_access_token
        }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500

@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    """Email verification endpoint"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Verification token required'}), 400

        # Verify email token
        user = AuthService.verify_email_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 400

        user.is_verified = True

        # Log email verification
        AuditLog.log_action(
            user_id=user.id,
            action='email_verified',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({'message': 'Email verified successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Email verification error: {str(e)}")
        return jsonify({'error': 'Email verification failed'}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """Forgot password endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email required'}), 400

        user = User.query.filter_by(email=email).first()
        if user:
            # Create password reset token
            reset_token = PasswordReset.create_reset_token(user.id)
            db.session.add(reset_token)

            # Send reset email
            try:
                EmailService.send_password_reset_email(user, reset_token.token)
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")

            # Log password reset request
            AuditLog.log_action(
                user_id=user.id,
                action='password_reset_requested',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )

            db.session.commit()

        # Always return success for security
        return jsonify({'message': 'Password reset email sent if account exists'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password endpoint"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')

        if not token or not new_password:
            return jsonify({'error': 'Token and password required'}), 400

        # Validate reset token
        reset = PasswordReset.query.filter_by(token=token, used=False).first()
        if not reset or reset.is_expired():
            return jsonify({'error': 'Invalid or expired token'}), 400

        # Update password
        user = User.query.get(reset.user_id)
        user.set_password(new_password)
        reset.used = True

        # Log password reset
        AuditLog.log_action(
            user_id=user.id,
            action='password_reset',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({'message': 'Password reset successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password endpoint"""
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

        user.set_password(new_password)

        # Log password change
        AuditLog.log_action(
            user_id=user.id,
            action='password_changed',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/auth/oauth/google', methods=['POST'])
def oauth_google():
    """Google OAuth authentication"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')

        if not access_token:
            return jsonify({'error': 'Access token required'}), 400

        # Verify Google token and get user info
        google_user = OAuthService.verify_google_token(access_token)
        if not google_user:
            return jsonify({'error': 'Invalid Google token'}), 401

        # Find or create user
        user = OAuthService.find_or_create_oauth_user(
            provider='google',
            provider_user_id=google_user['id'],
            email=google_user['email'],
            first_name=google_user.get('given_name', ''),
            last_name=google_user.get('family_name', ''),
            access_token=access_token
        )

        # Create JWT tokens
        jwt_access_token = create_access_token(identity=user.id)
        jwt_refresh_token = create_refresh_token(identity=user.id)

        # Create session
        session = AuthService.create_session(
            user_id=user.id,
            session_token=jwt_access_token,
            refresh_token=jwt_refresh_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        # Log OAuth login
        AuditLog.log_action(
            user_id=user.id,
            action='oauth_login',
            resource='google',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({
            'message': 'Google OAuth login successful',
            'access_token': jwt_access_token,
            'refresh_token': jwt_refresh_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Google OAuth error: {str(e)}")
        return jsonify({'error': 'Google OAuth failed'}), 500

@app.route('/api/auth/validate', methods=['POST'])
@jwt_required()
def validate_token():
    """Validate JWT token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify({'valid': False, 'error': 'User not found or inactive'}), 401

        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401

@app.route('/api/auth/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Get user's active sessions"""
    try:
        current_user_id = get_jwt_identity()

        sessions = UserSession.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).order_by(UserSession.last_activity.desc()).all()

        session_list = []
        for session in sessions:
            session_list.append({
                'id': session.id,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'expires_at': session.expires_at.isoformat()
            })

        return jsonify({'sessions': session_list}), 200

    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        return jsonify({'error': 'Failed to get sessions'}), 500