import os
import jwt
import requests
import smtplib
import secrets
import hashlib
import pyotp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app import db
from models import (
    User, LoginSession, PasswordResetToken, EmailVerificationToken,
    BlacklistedToken, OAuthState, AuditLog, ApiKey, UserRole, AuthProvider
)
from utils import (
    validate_password, validate_email, validate_phone, generate_secure_token,
    generate_numeric_code, send_email, send_sms, create_verification_email,
    create_password_reset_email, create_login_notification, get_client_ip,
    get_user_agent, parse_user_agent, hash_api_key, generate_api_key,
    verify_api_key
)
import logging
import uuid

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for user management"""

    @staticmethod
    def create_user(email, username, password, first_name, last_name, phone=None, role=UserRole.TRIAL, language='en'):
        """Create a new user with comprehensive validation"""
        # Validate input
        if not validate_email(email):
            raise ValueError("Invalid email format")

        if phone and not validate_phone(phone):
            raise ValueError("Invalid phone format")

        # Check password strength
        is_strong, password_errors = validate_password(password)
        if not is_strong:
            raise ValueError(f"Password validation failed: {'; '.join(password_errors)}")

        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == email.lower()) | (User.username == username)
        ).first()

        if existing_user:
            if existing_user.email == email.lower():
                raise ValueError("Email already registered")
            else:
                raise ValueError("Username already taken")

        user = User(
            email=email.lower(),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            language=language,
            auth_provider=AuthProvider.LOCAL
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()  # Get user ID

        # Log user creation
        AuditLog.log_action(
            user_id=user.id,
            event_type='user_created',
            event_description=f'User account created: {email}',
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )

        return user

    @staticmethod
    def authenticate_user(email, password, ip_address=None, user_agent=None):
        """Authenticate user with comprehensive security checks"""
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            # Log failed login attempt
            AuditLog.log_action(
                user_id=None,
                event_type='login_failed',
                event_description=f'Login attempt with non-existent email: {email}',
                success=False,
                error_message='User not found',
                ip_address=ip_address,
                user_agent=user_agent
            )
            return None, "Invalid credentials"

        # Check if account is locked
        if user.is_locked():
            AuditLog.log_action(
                user_id=user.id,
                event_type='login_blocked',
                event_description='Login attempt on locked account',
                success=False,
                error_message='Account locked',
                ip_address=ip_address,
                user_agent=user_agent
            )
            return None, "Account is temporarily locked. Please try again later."

        # Check if account is active
        if not user.is_active:
            AuditLog.log_action(
                user_id=user.id,
                event_type='login_blocked',
                event_description='Login attempt on inactive account',
                success=False,
                error_message='Account inactive',
                ip_address=ip_address,
                user_agent=user_agent
            )
            return None, "Account is deactivated"

        # Verify password
        if user.check_password(password):
            # Reset failed login attempts on successful login
            user.unlock_account()
            user.last_login = datetime.utcnow()

            # Log successful login
            AuditLog.log_action(
                user_id=user.id,
                event_type='login_success',
                event_description='User successfully logged in',
                ip_address=ip_address,
                user_agent=user_agent
            )

            return user, None
        else:
            # Increment failed login attempts
            user.failed_login_attempts += 1

            # Lock account if too many failed attempts
            max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
            if user.failed_login_attempts >= max_attempts:
                lockout_duration = current_app.config.get('LOCKOUT_DURATION_MINUTES', 30)
                user.lock_account(lockout_duration)

                AuditLog.log_action(
                    user_id=user.id,
                    event_type='account_locked',
                    event_description=f'Account locked after {max_attempts} failed login attempts',
                    success=False,
                    error_message='Too many failed attempts',
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            else:
                AuditLog.log_action(
                    user_id=user.id,
                    event_type='login_failed',
                    event_description=f'Failed login attempt ({user.failed_login_attempts}/{max_attempts})',
                    success=False,
                    error_message='Invalid password',
                    ip_address=ip_address,
                    user_agent=user_agent
                )

            db.session.commit()
            return None, "Invalid credentials"

    @staticmethod
    def create_session(user_id, session_token, refresh_token, ip_address=None, user_agent=None, remember_me=False):
        """Create a new user login session with device tracking"""
        # Parse device information
        device_info = parse_user_agent(user_agent) if user_agent else {}

        # Set expiration based on remember me option
        if remember_me:
            expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            expires_at = datetime.utcnow() + timedelta(hours=24)

        session = LoginSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info
        )

        db.session.add(session)

        # Log session creation
        AuditLog.log_action(
            user_id=user_id,
            event_type='session_created',
            event_description='New login session created',
            metadata={
                'device_info': device_info,
                'remember_me': remember_me
            },
            ip_address=ip_address,
            user_agent=user_agent
        )

        return session

    @staticmethod
    def verify_email_token(token):
        """Verify email verification token"""
        try:
            verification_token = EmailVerificationToken.query.filter_by(
                token=token,
                is_verified=False
            ).first()

            if not verification_token:
                return None, "Invalid or expired verification token"

            if verification_token.is_expired():
                return None, "Verification token has expired"

            # Mark token as verified
            verification_token.mark_as_verified()

            # Update user's email verification status
            user = verification_token.user
            user.email_verified = True
            user.is_verified = True

            # Log email verification
            AuditLog.log_action(
                user_id=user.id,
                event_type='email_verified',
                event_description=f'Email address verified: {verification_token.email}',
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()
            return user, None

        except Exception as e:
            logger.error(f"Email token verification error: {str(e)}")
            db.session.rollback()
            return None, "Verification failed"

    @staticmethod
    def send_verification_email(user):
        """Send email verification token"""
        try:
            # Create verification token
            token = generate_secure_token()
            verification_token = EmailVerificationToken(
                user_id=user.id,
                token=token,
                email=user.email,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )

            db.session.add(verification_token)
            db.session.flush()

            # Send email
            subject, body, html_body = create_verification_email(
                user.email, token, user.language
            )

            success = send_email(user.email, subject, body, html_body)

            if success:
                # Log email sent
                AuditLog.log_action(
                    user_id=user.id,
                    event_type='verification_email_sent',
                    event_description=f'Verification email sent to {user.email}',
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent()
                )
                db.session.commit()
                return True, "Verification email sent successfully"
            else:
                db.session.rollback()
                return False, "Failed to send verification email"

        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            db.session.rollback()
            return False, "Error sending verification email"

    @staticmethod
    def deactivate_user_sessions(user_id, exclude_session_id=None):
        """Deactivate all user sessions except the specified one"""
        sessions = LoginSession.query.filter_by(user_id=user_id, is_active=True)

        if exclude_session_id:
            sessions = sessions.filter(LoginSession.id != exclude_session_id)

        session_count = 0
        for session in sessions:
            session.revoke()
            session_count += 1

        # Log session deactivation
        AuditLog.log_action(
            user_id=user_id,
            event_type='sessions_revoked',
            event_description=f'Revoked {session_count} active sessions',
            metadata={'excluded_session': exclude_session_id},
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )

        db.session.commit()
        return session_count

    @staticmethod
    def create_password_reset_token(email):
        """Create password reset token"""
        try:
            user = User.query.filter_by(email=email.lower()).first()
            if not user:
                return False, "User not found"

            # Create reset token
            token = generate_secure_token()
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )

            db.session.add(reset_token)
            db.session.flush()

            # Send reset email
            subject, body, html_body = create_password_reset_email(
                user.email, token, user.language
            )

            success = send_email(user.email, subject, body, html_body)

            if success:
                # Log password reset request
                AuditLog.log_action(
                    user_id=user.id,
                    event_type='password_reset_requested',
                    event_description=f'Password reset requested for {user.email}',
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent()
                )
                db.session.commit()
                return True, "Password reset email sent"
            else:
                db.session.rollback()
                return False, "Failed to send reset email"

        except Exception as e:
            logger.error(f"Failed to create password reset token: {str(e)}")
            db.session.rollback()
            return False, "Error processing password reset request"

    @staticmethod
    def reset_password(token, new_password):
        """Reset password using token"""
        try:
            # Validate new password
            is_strong, password_errors = validate_password(new_password)
            if not is_strong:
                return False, f"Password validation failed: {'; '.join(password_errors)}"

            # Find and validate token
            reset_token = PasswordResetToken.query.filter_by(
                token=token,
                is_used=False
            ).first()

            if not reset_token:
                return False, "Invalid or expired reset token"

            if reset_token.is_expired():
                return False, "Reset token has expired"

            # Update user password
            user = reset_token.user
            user.set_password(new_password)
            user.failed_login_attempts = 0
            user.locked_until = None

            # Mark token as used
            reset_token.mark_as_used()

            # Revoke all user sessions (force re-login)
            AuthService.deactivate_user_sessions(user.id)

            # Log password reset
            AuditLog.log_action(
                user_id=user.id,
                event_type='password_reset',
                event_description='Password successfully reset',
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()
            return True, "Password reset successfully"

        except Exception as e:
            logger.error(f"Failed to reset password: {str(e)}")
            db.session.rollback()
            return False, "Error resetting password"

class MFAService:
    """Multi-Factor Authentication service"""

    @staticmethod
    def setup_mfa(user):
        """Setup MFA for user"""
        try:
            secret = user.setup_mfa()
            qr_url = user.get_mfa_qr_code_url()

            # Log MFA setup
            AuditLog.log_action(
                user_id=user.id,
                event_type='mfa_setup',
                event_description='MFA setup initiated',
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()

            return {
                'secret': secret,
                'qr_url': qr_url,
                'backup_codes': user.backup_codes
            }

        except Exception as e:
            logger.error(f"Failed to setup MFA: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def enable_mfa(user, token):
        """Enable MFA after verification"""
        try:
            if not user.mfa_secret:
                return False, "MFA not set up"

            if not user.verify_mfa_token(token):
                return False, "Invalid MFA token"

            user.mfa_enabled = True

            # Log MFA enabled
            AuditLog.log_action(
                user_id=user.id,
                event_type='mfa_enabled',
                event_description='MFA successfully enabled',
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()
            return True, "MFA enabled successfully"

        except Exception as e:
            logger.error(f"Failed to enable MFA: {str(e)}")
            db.session.rollback()
            return False, "Error enabling MFA"

    @staticmethod
    def disable_mfa(user, password):
        """Disable MFA with password confirmation"""
        try:
            if not user.check_password(password):
                return False, "Invalid password"

            user.mfa_enabled = False
            user.mfa_secret = None
            user.backup_codes = []

            # Log MFA disabled
            AuditLog.log_action(
                user_id=user.id,
                event_type='mfa_disabled',
                event_description='MFA disabled',
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()
            return True, "MFA disabled successfully"

        except Exception as e:
            logger.error(f"Failed to disable MFA: {str(e)}")
            db.session.rollback()
            return False, "Error disabling MFA"

    @staticmethod
    def verify_mfa(user, token, is_backup_code=False):
        """Verify MFA token or backup code"""
        try:
            if not user.mfa_enabled:
                return True, "MFA not enabled"

            if is_backup_code:
                if user.verify_backup_code(token):
                    # Log backup code used
                    AuditLog.log_action(
                        user_id=user.id,
                        event_type='mfa_backup_code_used',
                        event_description='MFA backup code used',
                        ip_address=get_client_ip(),
                        user_agent=get_user_agent()
                    )
                    db.session.commit()
                    return True, "Backup code verified"
                else:
                    return False, "Invalid backup code"
            else:
                if user.verify_mfa_token(token):
                    return True, "MFA token verified"
                else:
                    return False, "Invalid MFA token"

        except Exception as e:
            logger.error(f"Failed to verify MFA: {str(e)}")
            return False, "Error verifying MFA"

class OAuthService:
    """OAuth authentication service"""

    @staticmethod
    def create_oauth_state(provider):
        """Create OAuth state parameter"""
        try:
            state = generate_secure_token()
            oauth_state = OAuthState(
                state=state,
                provider=provider,
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )

            db.session.add(oauth_state)
            db.session.commit()

            return state

        except Exception as e:
            logger.error(f"Failed to create OAuth state: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def verify_oauth_state(state, provider):
        """Verify OAuth state parameter"""
        try:
            oauth_state = OAuthState.query.filter_by(
                state=state,
                provider=provider,
                used=False
            ).first()

            if not oauth_state:
                return False

            if oauth_state.is_expired():
                return False

            oauth_state.mark_as_used()
            db.session.commit()

            return True

        except Exception as e:
            logger.error(f"Failed to verify OAuth state: {str(e)}")
            return False

    @staticmethod
    def verify_google_token(access_token):
        """Verify Google OAuth access token"""
        try:
            # Verify token with Google
            response = requests.get(
                f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}',
                timeout=10
            )

            if response.status_code == 200:
                user_info = response.json()

                # Additional token verification
                token_info_response = requests.get(
                    f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}',
                    timeout=10
                )

                if token_info_response.status_code == 200:
                    token_info = token_info_response.json()

                    # Verify the token is for our app
                    if token_info.get('audience') == current_app.config.get('GOOGLE_CLIENT_ID'):
                        return user_info
                    else:
                        logger.error("Google token audience mismatch")
                        return None
                else:
                    logger.error(f"Google token info verification failed: {token_info_response.status_code}")
                    return None
            else:
                logger.error(f"Google token verification failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Google token verification error: {str(e)}")
            return None

    @staticmethod
    def verify_facebook_token(access_token):
        """Verify Facebook OAuth access token"""
        try:
            app_id = current_app.config.get('FACEBOOK_CLIENT_ID')
            app_secret = current_app.config.get('FACEBOOK_CLIENT_SECRET')

            # Verify token with Facebook
            response = requests.get(
                f'https://graph.facebook.com/me?access_token={access_token}&fields=id,email,first_name,last_name',
                timeout=10
            )

            if response.status_code == 200:
                user_info = response.json()

                # Additional verification
                debug_response = requests.get(
                    f'https://graph.facebook.com/debug_token?input_token={access_token}&access_token={app_id}|{app_secret}',
                    timeout=10
                )

                if debug_response.status_code == 200:
                    debug_info = debug_response.json()
                    if debug_info.get('data', {}).get('is_valid'):
                        return user_info
                    else:
                        logger.error("Facebook token validation failed")
                        return None
                else:
                    logger.error(f"Facebook token debug failed: {debug_response.status_code}")
                    return None
            else:
                logger.error(f"Facebook token verification failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Facebook token verification error: {str(e)}")
            return None

    @staticmethod
    def find_or_create_oauth_user(provider, provider_user_id, email, first_name, last_name):
        """Find existing OAuth user or create new one"""
        try:
            # Check if user exists with this OAuth provider
            user = User.query.filter_by(
                auth_provider=provider,
                provider_id=provider_user_id
            ).first()

            if user:
                # Update last login
                user.last_login = datetime.utcnow()

                # Log OAuth login
                AuditLog.log_action(
                    user_id=user.id,
                    event_type='oauth_login',
                    event_description=f'OAuth login via {provider.value}',
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent()
                )

                return user

            # Check if user exists with email (for account linking)
            existing_user = User.query.filter_by(email=email.lower()).first()

            if existing_user:
                # Link OAuth account to existing user
                if existing_user.auth_provider == AuthProvider.LOCAL:
                    # Update user to include OAuth provider
                    existing_user.auth_provider = provider
                    existing_user.provider_id = provider_user_id
                    existing_user.email_verified = True
                    existing_user.is_verified = True
                    existing_user.last_login = datetime.utcnow()

                    # Log account linking
                    AuditLog.log_action(
                        user_id=existing_user.id,
                        event_type='oauth_account_linked',
                        event_description=f'OAuth account linked via {provider.value}',
                        ip_address=get_client_ip(),
                        user_agent=get_user_agent()
                    )

                    return existing_user
                else:
                    # User already has different OAuth provider
                    raise ValueError("Email already associated with another OAuth provider")

            # Create new user
            username = f"{provider.value}_{provider_user_id}_{generate_numeric_code(4)}"

            user = User(
                email=email.lower(),
                username=username,
                first_name=first_name,
                last_name=last_name,
                auth_provider=provider,
                provider_id=provider_user_id,
                email_verified=True,  # OAuth users are automatically verified
                is_verified=True,
                role=UserRole.TRIAL,
                last_login=datetime.utcnow()
            )

            db.session.add(user)
            db.session.flush()  # Get user ID

            # Log OAuth user creation
            AuditLog.log_action(
                user_id=user.id,
                event_type='oauth_user_created',
                event_description=f'New user created via {provider.value} OAuth',
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            return user

        except Exception as e:
            logger.error(f"Failed to find or create OAuth user: {str(e)}")
            db.session.rollback()
            raise

class ApiKeyService:
    """API Key management service"""

    @staticmethod
    def create_api_key(user_id, name, permissions=None, rate_limit=1000, expires_days=None):
        """Create new API key for user"""
        try:
            key, key_hash, prefix = generate_api_key()

            expires_at = None
            if expires_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_days)

            api_key = ApiKey(
                user_id=user_id,
                name=name,
                key_hash=key_hash,
                key_prefix=prefix,
                permissions=permissions or [],
                rate_limit=rate_limit,
                expires_at=expires_at
            )

            db.session.add(api_key)
            db.session.flush()

            # Log API key creation
            AuditLog.log_action(
                user_id=user_id,
                event_type='api_key_created',
                event_description=f'API key created: {name}',
                metadata={'api_key_id': api_key.id},
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()

            return {
                'id': api_key.id,
                'key': key,  # Return only once
                'name': name,
                'prefix': prefix,
                'permissions': permissions,
                'rate_limit': rate_limit,
                'expires_at': expires_at.isoformat() if expires_at else None
            }

        except Exception as e:
            logger.error(f"Failed to create API key: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def verify_api_key(api_key):
        """Verify API key and return user"""
        try:
            # Extract prefix
            if not api_key.startswith('fca_'):
                return None, "Invalid API key format"

            prefix = api_key[:8] + "..."

            # Find API key by prefix
            api_key_record = ApiKey.query.filter_by(
                key_prefix=prefix,
                is_active=True
            ).first()

            if not api_key_record:
                return None, "Invalid API key"

            # Check if expired
            if api_key_record.is_expired():
                return None, "API key expired"

            # Verify hash
            if not verify_api_key(api_key, api_key_record.key_hash):
                return None, "Invalid API key"

            # Update last used
            api_key_record.last_used_at = datetime.utcnow()
            db.session.commit()

            return api_key_record.user, None

        except Exception as e:
            logger.error(f"Failed to verify API key: {str(e)}")
            return None, "Error verifying API key"

    @staticmethod
    def revoke_api_key(user_id, api_key_id):
        """Revoke API key"""
        try:
            api_key = ApiKey.query.filter_by(
                id=api_key_id,
                user_id=user_id
            ).first()

            if not api_key:
                return False, "API key not found"

            api_key.revoke()

            # Log API key revocation
            AuditLog.log_action(
                user_id=user_id,
                event_type='api_key_revoked',
                event_description=f'API key revoked: {api_key.name}',
                metadata={'api_key_id': api_key_id},
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()
            return True, "API key revoked successfully"

        except Exception as e:
            logger.error(f"Failed to revoke API key: {str(e)}")
            db.session.rollback()
            return False, "Error revoking API key"

class EmailService:
    """Email service for notifications"""

    @staticmethod
    def send_login_notification(user, ip_address, user_agent):
        """Send login notification email"""
        try:
            subject, body, html_body = create_login_notification(
                ip_address, user_agent, user.language
            )

            success = send_email(user.email, subject, body, html_body)

            if success:
                AuditLog.log_action(
                    user_id=user.id,
                    event_type='login_notification_sent',
                    event_description=f'Login notification sent to {user.email}',
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Failed to send login notification: {str(e)}")
            return False

    @staticmethod
    def send_security_alert(user, alert_type, details):
        """Send security alert email"""
        try:
            if user.language == 'ar':
                subject = f"تنبيه أمني - {alert_type} - FinClick.AI"
                body = f"""
مرحباً {user.first_name},

تم رصد نشاط أمني في حسابك:

نوع التنبيه: {alert_type}
التفاصيل: {details}
الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

إذا لم تكن قد قمت بهذا الإجراء، يرجى الاتصال بفريق الدعم فوراً.

مع أطيب التحيات،
فريق FinClick.AI
                """
            else:
                subject = f"Security Alert - {alert_type} - FinClick.AI"
                body = f"""
Hello {user.first_name},

A security event has been detected on your account:

Alert Type: {alert_type}
Details: {details}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

If you didn't perform this action, please contact our support team immediately.

Best regards,
FinClick.AI Team
                """

            success = send_email(user.email, subject, body)

            if success:
                AuditLog.log_action(
                    user_id=user.id,
                    event_type='security_alert_sent',
                    event_description=f'Security alert sent: {alert_type}',
                    metadata={'alert_details': details}
                )
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Failed to send security alert: {str(e)}")
            return False

class SecurityService:
    """Enhanced security-related services"""

    @staticmethod
    def blacklist_token(jti, token_type, user_id, expires_at):
        """Add token to blacklist"""
        try:
            blacklisted_token = BlacklistedToken(
                jti=jti,
                token_type=token_type,
                user_id=user_id,
                expires_at=expires_at
            )

            db.session.add(blacklisted_token)
            db.session.commit()

            return True

        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def is_token_blacklisted(jti):
        """Check if token is blacklisted"""
        try:
            blacklisted = BlacklistedToken.query.filter_by(jti=jti).first()
            return blacklisted is not None

        except Exception as e:
            logger.error(f"Failed to check token blacklist: {str(e)}")
            return False

    @staticmethod
    def cleanup_expired_tokens():
        """Clean up expired blacklisted tokens"""
        try:
            expired_tokens = BlacklistedToken.query.filter(
                BlacklistedToken.expires_at < datetime.utcnow()
            ).all()

            count = len(expired_tokens)
            for token in expired_tokens:
                db.session.delete(token)

            db.session.commit()
            logger.info(f"Cleaned up {count} expired blacklisted tokens")

            return count

        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens: {str(e)}")
            db.session.rollback()
            return 0

    @staticmethod
    def detect_suspicious_activity(user_id, activity_type, details):
        """Detect and log suspicious activity"""
        try:
            # Check for multiple failed logins
            if activity_type == 'failed_login':
                recent_failures = AuditLog.query.filter(
                    AuditLog.user_id == user_id,
                    AuditLog.event_type == 'login_failed',
                    AuditLog.created_at > datetime.utcnow() - timedelta(hours=1)
                ).count()

                if recent_failures >= 3:
                    return True, "Multiple failed login attempts detected"

            # Check for logins from different locations
            if activity_type == 'new_location_login':
                ip_address = details.get('ip_address')
                if ip_address:
                    recent_logins = AuditLog.query.filter(
                        AuditLog.user_id == user_id,
                        AuditLog.event_type == 'login_success',
                        AuditLog.created_at > datetime.utcnow() - timedelta(days=7)
                    ).all()

                    recent_ips = set([log.ip_address for log in recent_logins if log.ip_address])

                    if ip_address not in recent_ips and len(recent_ips) > 0:
                        return True, "Login from new location detected"

            return False, None

        except Exception as e:
            logger.error(f"Failed to detect suspicious activity: {str(e)}")
            return False, None

class PermissionService:
    """Enhanced permission and role management service"""

    @staticmethod
    def check_permission(user, permission):
        """Check if user has specific permission"""
        return user.has_permission(permission)

    @staticmethod
    def check_role(user, role):
        """Check if user has specific role"""
        return user.has_role(role)

    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for user based on role and custom permissions"""
        role_permissions = {
            UserRole.ADMIN: [
                'read', 'write', 'delete', 'admin', 'manage_users',
                'financial_analysis', 'advanced_reports', 'ai_agents',
                'system_config', 'audit_logs', 'manage_subscriptions'
            ],
            UserRole.PREMIUM: [
                'read', 'write', 'financial_analysis', 'advanced_reports',
                'ai_agents', 'export_data', 'api_access', 'premium_features'
            ],
            UserRole.STANDARD: [
                'read', 'write', 'basic_analysis', 'basic_reports',
                'standard_features', 'limited_export'
            ],
            UserRole.TRIAL: [
                'read', 'basic_analysis', 'trial_features', 'limited_access'
            ]
        }

        base_permissions = role_permissions.get(user.role, [])
        custom_permissions = user.permissions or []

        return list(set(base_permissions + custom_permissions))

    @staticmethod
    def add_user_permission(user_id, permission):
        """Add custom permission to user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            if not user.permissions:
                user.permissions = []

            if permission not in user.permissions:
                user.permissions.append(permission)

                # Log permission added
                AuditLog.log_action(
                    user_id=user_id,
                    event_type='permission_added',
                    event_description=f'Permission added: {permission}',
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent()
                )

                db.session.commit()
                return True, "Permission added successfully"
            else:
                return True, "Permission already exists"

        except Exception as e:
            logger.error(f"Failed to add user permission: {str(e)}")
            db.session.rollback()
            return False, "Error adding permission"

    @staticmethod
    def remove_user_permission(user_id, permission):
        """Remove custom permission from user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            if user.permissions and permission in user.permissions:
                user.permissions.remove(permission)

                # Log permission removed
                AuditLog.log_action(
                    user_id=user_id,
                    event_type='permission_removed',
                    event_description=f'Permission removed: {permission}',
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent()
                )

                db.session.commit()
                return True, "Permission removed successfully"
            else:
                return True, "Permission not found"

        except Exception as e:
            logger.error(f"Failed to remove user permission: {str(e)}")
            db.session.rollback()
            return False, "Error removing permission"

    @staticmethod
    def update_user_role(user_id, new_role, admin_user_id):
        """Update user role (admin only)"""
        try:
            user = User.query.get(user_id)
            admin = User.query.get(admin_user_id)

            if not user:
                return False, "User not found"

            if not admin or not admin.has_role(UserRole.ADMIN):
                return False, "Insufficient permissions"

            old_role = user.role
            user.role = new_role

            # Log role change
            AuditLog.log_action(
                user_id=user_id,
                event_type='role_changed',
                event_description=f'Role changed from {old_role.value} to {new_role.value}',
                metadata={
                    'old_role': old_role.value,
                    'new_role': new_role.value,
                    'changed_by': admin_user_id
                },
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )

            db.session.commit()
            return True, "Role updated successfully"

        except Exception as e:
            logger.error(f"Failed to update user role: {str(e)}")
            db.session.rollback()
            return False, "Error updating role"

class SessionService:
    """Enhanced session management service"""

    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions"""
        try:
            expired_sessions = LoginSession.query.filter(
                LoginSession.expires_at < datetime.utcnow(),
                LoginSession.is_active == True
            ).all()

            count = 0
            for session in expired_sessions:
                session.revoke()
                count += 1

            db.session.commit()
            logger.info(f"Cleaned up {count} expired sessions")
            return count

        except Exception as e:
            logger.error(f"Session cleanup error: {str(e)}")
            db.session.rollback()
            return 0

    @staticmethod
    def get_active_session_count(user_id):
        """Get count of active sessions for user"""
        return LoginSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            LoginSession.expires_at > datetime.utcnow()
        ).count()

    @staticmethod
    def get_user_sessions(user_id):
        """Get all active sessions for user with details"""
        try:
            sessions = LoginSession.query.filter_by(
                user_id=user_id,
                is_active=True
            ).filter(
                LoginSession.expires_at > datetime.utcnow()
            ).order_by(LoginSession.last_activity.desc()).all()

            session_list = []
            for session in sessions:
                session_data = {
                    'id': session.id,
                    'ip_address': session.ip_address,
                    'device_info': session.device_info,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'expires_at': session.expires_at.isoformat()
                }
                session_list.append(session_data)

            return session_list

        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []

    @staticmethod
    def revoke_session(session_id, user_id):
        """Revoke a specific session"""
        try:
            session = LoginSession.query.filter_by(
                id=session_id,
                user_id=user_id
            ).first()

            if session:
                session.revoke()

                # Log session revocation
                AuditLog.log_action(
                    user_id=user_id,
                    event_type='session_revoked',
                    event_description=f'Session manually revoked: {session_id}',
                    metadata={'session_id': session_id},
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent()
                )

                db.session.commit()
                return True, "Session revoked successfully"
            else:
                return False, "Session not found"

        except Exception as e:
            logger.error(f"Failed to revoke session: {str(e)}")
            db.session.rollback()
            return False, "Error revoking session"

    @staticmethod
    def extend_session(session_id, user_id, hours=24):
        """Extend session expiration"""
        try:
            session = LoginSession.query.filter_by(
                id=session_id,
                user_id=user_id,
                is_active=True
            ).first()

            if session and not session.is_expired():
                session.extend_session(hours)

                # Log session extension
                AuditLog.log_action(
                    user_id=user_id,
                    event_type='session_extended',
                    event_description=f'Session extended: {session_id}',
                    metadata={
                        'session_id': session_id,
                        'extended_hours': hours
                    },
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent()
                )

                db.session.commit()
                return True, "Session extended successfully"
            else:
                return False, "Session not found or expired"

        except Exception as e:
            logger.error(f"Failed to extend session: {str(e)}")
            db.session.rollback()
            return False, "Error extending session"

class AuditService:
    """Audit and logging service"""

    @staticmethod
    def get_user_audit_logs(user_id, limit=50, offset=0, event_type=None):
        """Get audit logs for specific user"""
        try:
            query = AuditLog.query.filter_by(user_id=user_id)

            if event_type:
                query = query.filter_by(event_type=event_type)

            logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

            log_list = []
            for log in logs:
                log_data = {
                    'id': log.id,
                    'event_type': log.event_type,
                    'event_description': log.event_description,
                    'success': log.success,
                    'error_message': log.error_message,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'metadata': log.metadata,
                    'created_at': log.created_at.isoformat()
                }
                log_list.append(log_data)

            return log_list

        except Exception as e:
            logger.error(f"Failed to get audit logs: {str(e)}")
            return []

    @staticmethod
    def get_system_audit_logs(limit=100, offset=0, event_type=None, start_date=None, end_date=None):
        """Get system-wide audit logs (admin only)"""
        try:
            query = AuditLog.query

            if event_type:
                query = query.filter_by(event_type=event_type)

            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)

            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)

            logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

            log_list = []
            for log in logs:
                log_data = {
                    'id': log.id,
                    'user_id': log.user_id,
                    'event_type': log.event_type,
                    'event_description': log.event_description,
                    'success': log.success,
                    'error_message': log.error_message,
                    'ip_address': log.ip_address,
                    'metadata': log.metadata,
                    'created_at': log.created_at.isoformat()
                }
                log_list.append(log_data)

            return log_list

        except Exception as e:
            logger.error(f"Failed to get system audit logs: {str(e)}")
            return []

    @staticmethod
    def cleanup_old_audit_logs(days=90):
        """Clean up old audit logs"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            old_logs = AuditLog.query.filter(
                AuditLog.created_at < cutoff_date
            ).all()

            count = len(old_logs)
            for log in old_logs:
                db.session.delete(log)

            db.session.commit()
            logger.info(f"Cleaned up {count} old audit logs")

            return count

        except Exception as e:
            logger.error(f"Failed to cleanup audit logs: {str(e)}")
            db.session.rollback()
            return 0