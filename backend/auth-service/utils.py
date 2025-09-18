import re
import secrets
import string
import hashlib
import hmac
import base64
import qrcode
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import smtplib
from twilio.rest import Client
from flask import current_app, request
import pyotp
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash

def validate_password(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password strength based on security requirements
    Returns (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < current_app.config.get('PASSWORD_MIN_LENGTH', 8):
        errors.append('Password must be at least 8 characters long')

    if current_app.config.get('PASSWORD_REQUIRE_UPPERCASE', True):
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')

    if current_app.config.get('PASSWORD_REQUIRE_LOWERCASE', True):
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')

    if current_app.config.get('PASSWORD_REQUIRE_NUMBERS', True):
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')

    if current_app.config.get('PASSWORD_REQUIRE_SYMBOLS', True):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')

    # Check for common patterns
    if re.search(r'(.)\1{3,}', password):
        errors.append('Password cannot contain more than 3 consecutive identical characters')

    # Check for common weak passwords
    weak_passwords = ['password', '12345678', 'qwerty', 'abc123', 'password123']
    if password.lower() in weak_passwords:
        errors.append('Password is too common and weak')

    return len(errors) == 0, errors

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format (international format)"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def generate_numeric_code(length: int = 6) -> str:
    """Generate a numeric verification code"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for MFA"""
    return [secrets.token_hex(4) for _ in range(count)]

def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage"""
    return generate_password_hash(api_key)

def verify_api_key(api_key: str, api_key_hash: str) -> bool:
    """Verify API key against stored hash"""
    from werkzeug.security import check_password_hash
    return check_password_hash(api_key_hash, api_key)

def generate_api_key() -> Tuple[str, str, str]:
    """
    Generate API key and return (key, hash, prefix)
    Prefix is first 8 characters for display purposes
    """
    key = f"fca_{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(key)
    prefix = key[:8] + "..."
    return key, key_hash, prefix

def get_client_ip() -> str:
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()

def get_user_agent() -> str:
    """Get user agent from request"""
    return request.headers.get('User-Agent', '')

def parse_user_agent(user_agent: str) -> Dict[str, str]:
    """Parse user agent string to extract browser and OS info"""
    # Simple user agent parsing (in production, use a proper library like user-agents)
    device_info = {
        'browser': 'Unknown',
        'os': 'Unknown',
        'device': 'Unknown'
    }

    if 'Chrome' in user_agent:
        device_info['browser'] = 'Chrome'
    elif 'Firefox' in user_agent:
        device_info['browser'] = 'Firefox'
    elif 'Safari' in user_agent:
        device_info['browser'] = 'Safari'
    elif 'Edge' in user_agent:
        device_info['browser'] = 'Edge'

    if 'Windows' in user_agent:
        device_info['os'] = 'Windows'
    elif 'Mac' in user_agent:
        device_info['os'] = 'macOS'
    elif 'Linux' in user_agent:
        device_info['os'] = 'Linux'
    elif 'Android' in user_agent:
        device_info['os'] = 'Android'
    elif 'iOS' in user_agent:
        device_info['os'] = 'iOS'

    if 'Mobile' in user_agent:
        device_info['device'] = 'Mobile'
    elif 'Tablet' in user_agent:
        device_info['device'] = 'Tablet'
    else:
        device_info['device'] = 'Desktop'

    return device_info

def generate_qr_code(data: str) -> bytes:
    """Generate QR code for MFA setup"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return img_buffer.getvalue()

def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
    """Send email using SMTP"""
    try:
        msg = MimeMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email

        # Add text part
        text_part = MimeText(body, 'plain', 'utf-8')
        msg.attach(text_part)

        # Add HTML part if provided
        if html_body:
            html_part = MimeText(html_body, 'html', 'utf-8')
            msg.attach(html_part)

        # Send email
        server = smtplib.SMTP(
            current_app.config['MAIL_SERVER'],
            current_app.config['MAIL_PORT']
        )

        if current_app.config.get('MAIL_USE_TLS'):
            server.starttls()

        if current_app.config.get('MAIL_USERNAME'):
            server.login(
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD']
            )

        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_sms(to_phone: str, message: str) -> bool:
    """Send SMS using Twilio"""
    try:
        client = Client(
            current_app.config['TWILIO_ACCOUNT_SID'],
            current_app.config['TWILIO_AUTH_TOKEN']
        )

        client.messages.create(
            body=message,
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=to_phone
        )

        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {str(e)}")
        return False

def create_verification_email(email: str, token: str, language: str = 'en') -> Tuple[str, str]:
    """Create email verification email content"""
    verification_url = f"{current_app.config['EMAIL_VERIFICATION_URL']}?token={token}"

    if language == 'ar':
        subject = "تأكيد عنوان البريد الإلكتروني - FinClick.AI"
        body = f"""
مرحباً،

شكراً لانضمامك إلى FinClick.AI! لإكمال تسجيل حسابك، يرجى النقر على الرابط أدناه لتأكيد عنوان بريدك الإلكتروني:

{verification_url}

هذا الرابط صالح لمدة 24 ساعة.

إذا لم تقم بإنشاء حساب، يرجى تجاهل هذا البريد الإلكتروني.

مع أطيب التحيات،
فريق FinClick.AI
        """

        html_body = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>مرحباً،</h2>
            <p>شكراً لانضمامك إلى FinClick.AI! لإكمال تسجيل حسابك، يرجى النقر على الزر أدناه لتأكيد عنوان بريدك الإلكتروني:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">تأكيد البريد الإلكتروني</a>
            </div>
            <p>هذا الرابط صالح لمدة 24 ساعة.</p>
            <p>إذا لم تقم بإنشاء حساب، يرجى تجاهل هذا البريد الإلكتروني.</p>
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">مع أطيب التحيات،<br>فريق FinClick.AI</p>
        </div>
        """
    else:
        subject = "Email Verification - FinClick.AI"
        body = f"""
Hello,

Thank you for joining FinClick.AI! To complete your account registration, please click the link below to verify your email address:

{verification_url}

This link is valid for 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
FinClick.AI Team
        """

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Hello,</h2>
            <p>Thank you for joining FinClick.AI! To complete your account registration, please click the button below to verify your email address:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
            </div>
            <p>This link is valid for 24 hours.</p>
            <p>If you didn't create an account, please ignore this email.</p>
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">Best regards,<br>FinClick.AI Team</p>
        </div>
        """

    return subject, body, html_body

def create_password_reset_email(email: str, token: str, language: str = 'en') -> Tuple[str, str, str]:
    """Create password reset email content"""
    reset_url = f"{current_app.config['PASSWORD_RESET_URL']}?token={token}"

    if language == 'ar':
        subject = "إعادة تعيين كلمة المرور - FinClick.AI"
        body = f"""
مرحباً،

تلقينا طلباً لإعادة تعيين كلمة المرور لحسابك في FinClick.AI. إذا كنت قد طلبت ذلك، يرجى النقر على الرابط أدناه:

{reset_url}

هذا الرابط صالح لمدة ساعة واحدة.

إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذا البريد الإلكتروني. كلمة المرور الخاصة بك آمنة.

مع أطيب التحيات،
فريق FinClick.AI
        """

        html_body = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>مرحباً،</h2>
            <p>تلقينا طلباً لإعادة تعيين كلمة المرور لحسابك في FinClick.AI. إذا كنت قد طلبت ذلك، يرجى النقر على الزر أدناه:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">إعادة تعيين كلمة المرور</a>
            </div>
            <p>هذا الرابط صالح لمدة ساعة واحدة.</p>
            <p>إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذا البريد الإلكتروني. كلمة المرور الخاصة بك آمنة.</p>
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">مع أطيب التحيات،<br>فريق FinClick.AI</p>
        </div>
        """
    else:
        subject = "Password Reset - FinClick.AI"
        body = f"""
Hello,

We received a request to reset the password for your FinClick.AI account. If you requested this, please click the link below:

{reset_url}

This link is valid for 1 hour.

If you didn't request a password reset, please ignore this email. Your password is safe.

Best regards,
FinClick.AI Team
        """

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Hello,</h2>
            <p>We received a request to reset the password for your FinClick.AI account. If you requested this, please click the button below:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
            </div>
            <p>This link is valid for 1 hour.</p>
            <p>If you didn't request a password reset, please ignore this email. Your password is safe.</p>
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">Best regards,<br>FinClick.AI Team</p>
        </div>
        """

    return subject, body, html_body

def create_login_notification(ip_address: str, user_agent: str, language: str = 'en') -> Tuple[str, str, str]:
    """Create login notification email content"""
    device_info = parse_user_agent(user_agent)
    login_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    if language == 'ar':
        subject = "تسجيل دخول جديد إلى حسابك - FinClick.AI"
        body = f"""
مرحباً،

تم تسجيل دخول جديد إلى حسابك في FinClick.AI:

الوقت: {login_time}
عنوان IP: {ip_address}
المتصفح: {device_info['browser']}
نظام التشغيل: {device_info['os']}
الجهاز: {device_info['device']}

إذا لم تكن قد سجلت الدخول، يرجى تغيير كلمة المرور فوراً والاتصال بفريق الدعم.

مع أطيب التحيات،
فريق FinClick.AI
        """

        html_body = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>مرحباً،</h2>
            <p>تم تسجيل دخول جديد إلى حسابك في FinClick.AI:</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>الوقت:</strong> {login_time}</p>
                <p><strong>عنوان IP:</strong> {ip_address}</p>
                <p><strong>المتصفح:</strong> {device_info['browser']}</p>
                <p><strong>نظام التشغيل:</strong> {device_info['os']}</p>
                <p><strong>الجهاز:</strong> {device_info['device']}</p>
            </div>
            <p style="color: #dc3545;"><strong>إذا لم تكن قد سجلت الدخول، يرجى تغيير كلمة المرور فوراً والاتصال بفريق الدعم.</strong></p>
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">مع أطيب التحيات،<br>فريق FinClick.AI</p>
        </div>
        """
    else:
        subject = "New Login to Your Account - FinClick.AI"
        body = f"""
Hello,

A new login to your FinClick.AI account was detected:

Time: {login_time}
IP Address: {ip_address}
Browser: {device_info['browser']}
Operating System: {device_info['os']}
Device: {device_info['device']}

If this wasn't you, please change your password immediately and contact our support team.

Best regards,
FinClick.AI Team
        """

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Hello,</h2>
            <p>A new login to your FinClick.AI account was detected:</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Time:</strong> {login_time}</p>
                <p><strong>IP Address:</strong> {ip_address}</p>
                <p><strong>Browser:</strong> {device_info['browser']}</p>
                <p><strong>Operating System:</strong> {device_info['os']}</p>
                <p><strong>Device:</strong> {device_info['device']}</p>
            </div>
            <p style="color: #dc3545;"><strong>If this wasn't you, please change your password immediately and contact our support team.</strong></p>
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">Best regards,<br>FinClick.AI Team</p>
        </div>
        """

    return subject, body, html_body

def rate_limit_key(identifier: str, endpoint: str) -> str:
    """Generate rate limit key for Redis"""
    return f"rate_limit:{identifier}:{endpoint}"

def check_password_complexity_score(password: str) -> int:
    """
    Calculate password complexity score (0-100)
    """
    score = 0

    # Length score (max 25 points)
    if len(password) >= 8:
        score += 10
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 5

    # Character variety (max 40 points)
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 10

    # Bonus points (max 35 points)
    if len(set(password)) / len(password) > 0.7:  # Character uniqueness
        score += 10
    if not re.search(r'(.)\1{2,}', password):  # No repeated characters
        score += 10
    if not re.search(r'(abc|123|qwe)', password.lower()):  # No common sequences
        score += 15

    return min(score, 100)

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify CSRF token"""
    # Simple CSRF verification - in production use more sophisticated method
    return hmac.compare_digest(token, session_token)

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS"""
    import html
    return html.escape(input_str.strip())

def mask_email(email: str) -> str:
    """Mask email for privacy (e.g., john***@example.com)"""
    if '@' not in email:
        return email

    local, domain = email.split('@', 1)
    if len(local) <= 3:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        masked_local = local[:2] + '*' * (len(local) - 3) + local[-1]

    return f"{masked_local}@{domain}"

def mask_phone(phone: str) -> str:
    """Mask phone number for privacy (e.g., +1***-***-1234)"""
    if len(phone) < 4:
        return phone

    return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]