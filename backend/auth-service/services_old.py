import os
import jwt
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import db
from models import User, UserSession, OAuthAccount, UserRole
import logging
import uuid

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for user management"""

    @staticmethod
    def create_user(email, username, password, first_name, last_name, phone=None, role=UserRole.USER):
        """Create a new user"""
        user = User(
            email=email.lower(),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        return user

    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = User.query.filter_by(email=email.lower()).first()

        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def create_session(user_id, session_token, refresh_token, ip_address=None, user_agent=None):
        """Create a new user session"""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.session.add(session)
        return session

    @staticmethod
    def verify_email_token(token):
        """Verify email verification token"""
        try:
            # In a real implementation, you would decode a JWT token
            # For now, we'll implement a simple token verification
            user = User.query.filter_by(id=token).first()
            return user
        except Exception as e:
            logger.error(f"Email token verification error: {str(e)}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def update_user_last_login(user_id):
        """Update user's last login timestamp"""
        user = User.query.get(user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def deactivate_user_sessions(user_id):
        """Deactivate all user sessions"""
        sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
        for session in sessions:
            session.is_active = False
        db.session.commit()

class OAuthService:
    """OAuth authentication service"""

    @staticmethod
    def verify_google_token(access_token):
        """Verify Google OAuth access token"""
        try:
            # Verify token with Google
            response = requests.get(
                f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}'
            )

            if response.status_code == 200:
                return response.json()
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
            app_id = os.getenv('FACEBOOK_CLIENT_ID')
            app_secret = os.getenv('FACEBOOK_CLIENT_SECRET')

            # Verify token with Facebook
            response = requests.get(
                f'https://graph.facebook.com/me?access_token={access_token}&fields=id,email,first_name,last_name'
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Facebook token verification failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Facebook token verification error: {str(e)}")
            return None

    @staticmethod
    def find_or_create_oauth_user(provider, provider_user_id, email, first_name, last_name, access_token):
        """Find existing OAuth user or create new one"""
        # Check if OAuth account exists
        oauth_account = OAuthAccount.query.filter_by(
            provider=provider,
            provider_user_id=provider_user_id
        ).first()

        if oauth_account:
            # Update tokens
            oauth_account.access_token = access_token
            oauth_account.updated_at = datetime.utcnow()
            return oauth_account.user

        # Check if user exists with email
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            # Create new user
            username = f"{provider}_{provider_user_id}"
            user = User(
                email=email.lower(),
                username=username,
                first_name=first_name,
                last_name=last_name,
                password_hash=generate_password_hash(str(uuid.uuid4())),  # Random password
                is_verified=True,  # OAuth users are automatically verified
                role=UserRole.USER
            )
            db.session.add(user)
            db.session.flush()  # Get user ID

        # Create OAuth account
        oauth_account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token
        )
        db.session.add(oauth_account)

        return user

class EmailService:
    """Email service for notifications"""

    @staticmethod
    def send_verification_email(user):
        """Send email verification"""
        try:
            smtp_server = os.getenv('SMTP_SERVER', 'localhost')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('FROM_EMAIL', 'noreply@finclick.ai')

            if not smtp_username or not smtp_password:
                logger.warning("SMTP credentials not configured, skipping email")
                return

            # Create verification token (in production, use JWT)
            verification_token = user.id

            # Create email
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = user.email
            msg['Subject'] = 'Verify Your FinClick.AI Account'

            body = f"""
            Hello {user.first_name},

            Thank you for registering with FinClick.AI!

            Please verify your email address by clicking the link below:
            http://localhost:3000/verify-email?token={verification_token}

            If you didn't create this account, please ignore this email.

            Best regards,
            FinClick.AI Team
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(from_email, user.email, text)
            server.quit()

            logger.info(f"Verification email sent to {user.email}")

        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise

    @staticmethod
    def send_password_reset_email(user, reset_token):
        """Send password reset email"""
        try:
            smtp_server = os.getenv('SMTP_SERVER', 'localhost')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('FROM_EMAIL', 'noreply@finclick.ai')

            if not smtp_username or not smtp_password:
                logger.warning("SMTP credentials not configured, skipping email")
                return

            # Create email
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = user.email
            msg['Subject'] = 'Reset Your FinClick.AI Password'

            body = f"""
            Hello {user.first_name},

            You requested to reset your password for your FinClick.AI account.

            Please click the link below to reset your password:
            http://localhost:3000/reset-password?token={reset_token}

            This link will expire in 24 hours.

            If you didn't request this password reset, please ignore this email.

            Best regards,
            FinClick.AI Team
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(from_email, user.email, text)
            server.quit()

            logger.info(f"Password reset email sent to {user.email}")

        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            raise

class SecurityService:
    """Security-related services"""

    @staticmethod
    def check_password_strength(password):
        """Check password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"

    @staticmethod
    def generate_secure_token():
        """Generate a secure random token"""
        return str(uuid.uuid4())

    @staticmethod
    def hash_password(password):
        """Hash password using werkzeug"""
        return generate_password_hash(password)

class PermissionService:
    """Permission and role management service"""

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
        """Get all permissions for user"""
        role_permissions = {
            UserRole.ADMIN: ['read', 'write', 'delete', 'admin', 'manage', 'analyze'],
            UserRole.MANAGER: ['read', 'write', 'manage', 'analyze'],
            UserRole.ANALYST: ['read', 'analyze'],
            UserRole.USER: ['read']
        }
        return role_permissions.get(user.role, [])

class SessionService:
    """Session management service"""

    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions"""
        try:
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime.utcnow()
            ).all()

            for session in expired_sessions:
                session.is_active = False

            db.session.commit()
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        except Exception as e:
            logger.error(f"Session cleanup error: {str(e)}")
            db.session.rollback()

    @staticmethod
    def get_active_session_count(user_id):
        """Get count of active sessions for user"""
        return UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).count()

    @staticmethod
    def revoke_session(session_id, user_id):
        """Revoke a specific session"""
        session = UserSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()

        if session:
            session.is_active = False
            db.session.commit()
            return True
        return False