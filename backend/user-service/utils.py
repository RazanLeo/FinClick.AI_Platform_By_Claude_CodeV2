import re
import os
import boto3
import hashlib
import secrets
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from werkzeug.utils import secure_filename
from PIL import Image
import io
from flask import current_app
import json
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS"""
    import html
    return html.escape(input_str.strip())

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format (international format)"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None

def validate_linkedin_url(url: str) -> bool:
    """Validate LinkedIn URL format"""
    pattern = r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$'
    return re.match(pattern, url) is not None

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_file_size(file) -> int:
    """Get file size in bytes"""
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    return size

def generate_filename(original_filename: str, user_id: str) -> str:
    """Generate secure filename with user prefix"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    random_suffix = secrets.token_hex(8)
    return f"user_{user_id}_{timestamp}_{random_suffix}.{ext}"

def resize_image(image_data: bytes, max_width: int = 300, max_height: int = 300) -> bytes:
    """Resize image while maintaining aspect ratio"""
    try:
        img = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img, mask=img.split()[-1])
            img = background

        # Calculate new dimensions
        ratio = min(max_width / img.width, max_height / img.height)
        if ratio < 1:
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()

    except Exception as e:
        logger.error(f"Image resize error: {str(e)}")
        return image_data

def upload_to_s3(file_data: bytes, filename: str, content_type: str = 'image/jpeg') -> Optional[str]:
    """Upload file to S3 and return URL"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION']
        )

        bucket_name = current_app.config['AWS_BUCKET_NAME']
        key = f"avatars/{filename}"

        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=file_data,
            ContentType=content_type,
            ACL='public-read'
        )

        return f"https://{bucket_name}.s3.{current_app.config['AWS_REGION']}.amazonaws.com/{key}"

    except Exception as e:
        logger.error(f"S3 upload error: {str(e)}")
        return None

def delete_from_s3(file_url: str) -> bool:
    """Delete file from S3"""
    try:
        # Extract key from URL
        bucket_name = current_app.config['AWS_BUCKET_NAME']
        if bucket_name not in file_url:
            return False

        key = file_url.split(f"{bucket_name}.s3.")[1].split("/", 1)[1]

        s3_client = boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION']
        )

        s3_client.delete_object(Bucket=bucket_name, Key=key)
        return True

    except Exception as e:
        logger.error(f"S3 delete error: {str(e)}")
        return False

def get_country_list() -> List[Dict[str, str]]:
    """Get list of countries with codes"""
    return [
        {"code": "US", "name": "United States"},
        {"code": "SA", "name": "Saudi Arabia"},
        {"code": "AE", "name": "United Arab Emirates"},
        {"code": "EG", "name": "Egypt"},
        {"code": "GB", "name": "United Kingdom"},
        {"code": "CA", "name": "Canada"},
        {"code": "AU", "name": "Australia"},
        {"code": "DE", "name": "Germany"},
        {"code": "FR", "name": "France"},
        {"code": "JP", "name": "Japan"},
        {"code": "IN", "name": "India"},
        {"code": "BR", "name": "Brazil"},
        {"code": "CN", "name": "China"},
        {"code": "KW", "name": "Kuwait"},
        {"code": "QA", "name": "Qatar"},
        {"code": "BH", "name": "Bahrain"},
        {"code": "OM", "name": "Oman"},
        {"code": "JO", "name": "Jordan"},
        {"code": "LB", "name": "Lebanon"},
        {"code": "MA", "name": "Morocco"},
        {"code": "TN", "name": "Tunisia"},
        {"code": "DZ", "name": "Algeria"},
        {"code": "IQ", "name": "Iraq"},
        {"code": "SY", "name": "Syria"},
        {"code": "YE", "name": "Yemen"},
        {"code": "LY", "name": "Libya"},
        {"code": "SD", "name": "Sudan"},
        {"code": "TR", "name": "Turkey"},
        {"code": "IR", "name": "Iran"},
        {"code": "PK", "name": "Pakistan"},
        {"code": "BD", "name": "Bangladesh"},
        {"code": "MY", "name": "Malaysia"},
        {"code": "ID", "name": "Indonesia"},
        {"code": "SG", "name": "Singapore"},
        {"code": "TH", "name": "Thailand"},
        {"code": "VN", "name": "Vietnam"},
        {"code": "PH", "name": "Philippines"},
        {"code": "KR", "name": "South Korea"},
        {"code": "TW", "name": "Taiwan"},
        {"code": "HK", "name": "Hong Kong"},
        {"code": "MX", "name": "Mexico"},
        {"code": "AR", "name": "Argentina"},
        {"code": "CL", "name": "Chile"},
        {"code": "CO", "name": "Colombia"},
        {"code": "PE", "name": "Peru"},
        {"code": "VE", "name": "Venezuela"},
        {"code": "ZA", "name": "South Africa"},
        {"code": "NG", "name": "Nigeria"},
        {"code": "KE", "name": "Kenya"},
        {"code": "GH", "name": "Ghana"},
        {"code": "ET", "name": "Ethiopia"},
        {"code": "TZ", "name": "Tanzania"},
        {"code": "UG", "name": "Uganda"},
        {"code": "ZW", "name": "Zimbabwe"},
        {"code": "MW", "name": "Malawi"},
        {"code": "ZM", "name": "Zambia"},
        {"code": "BW", "name": "Botswana"},
        {"code": "NA", "name": "Namibia"},
        {"code": "SZ", "name": "Eswatini"},
        {"code": "LS", "name": "Lesotho"},
        {"code": "MG", "name": "Madagascar"},
        {"code": "MU", "name": "Mauritius"},
        {"code": "SC", "name": "Seychelles"},
        {"code": "CV", "name": "Cape Verde"},
        {"code": "ST", "name": "São Tomé and Príncipe"},
        {"code": "GQ", "name": "Equatorial Guinea"},
        {"code": "GA", "name": "Gabon"},
        {"code": "CG", "name": "Republic of the Congo"},
        {"code": "CD", "name": "Democratic Republic of the Congo"},
        {"code": "CF", "name": "Central African Republic"},
        {"code": "TD", "name": "Chad"},
        {"code": "CM", "name": "Cameroon"},
        {"code": "NG", "name": "Nigeria"},
        {"code": "NE", "name": "Niger"},
        {"code": "BF", "name": "Burkina Faso"},
        {"code": "ML", "name": "Mali"},
        {"code": "SN", "name": "Senegal"},
        {"code": "GM", "name": "Gambia"},
        {"code": "GW", "name": "Guinea-Bissau"},
        {"code": "GN", "name": "Guinea"},
        {"code": "SL", "name": "Sierra Leone"},
        {"code": "LR", "name": "Liberia"},
        {"code": "CI", "name": "Côte d'Ivoire"},
        {"code": "BJ", "name": "Benin"},
        {"code": "TG", "name": "Togo"},
        {"code": "GI", "name": "Gibraltar"},
        {"code": "MT", "name": "Malta"},
        {"code": "CY", "name": "Cyprus"},
        {"code": "GR", "name": "Greece"},
        {"code": "IT", "name": "Italy"},
        {"code": "ES", "name": "Spain"},
        {"code": "PT", "name": "Portugal"},
        {"code": "AD", "name": "Andorra"},
        {"code": "MC", "name": "Monaco"},
        {"code": "SM", "name": "San Marino"},
        {"code": "VA", "name": "Vatican City"},
        {"code": "LI", "name": "Liechtenstein"},
        {"code": "CH", "name": "Switzerland"},
        {"code": "AT", "name": "Austria"},
        {"code": "LU", "name": "Luxembourg"},
        {"code": "BE", "name": "Belgium"},
        {"code": "NL", "name": "Netherlands"},
        {"code": "DK", "name": "Denmark"},
        {"code": "SE", "name": "Sweden"},
        {"code": "NO", "name": "Norway"},
        {"code": "FI", "name": "Finland"},
        {"code": "IS", "name": "Iceland"},
        {"code": "IE", "name": "Ireland"},
        {"code": "PL", "name": "Poland"},
        {"code": "CZ", "name": "Czech Republic"},
        {"code": "SK", "name": "Slovakia"},
        {"code": "HU", "name": "Hungary"},
        {"code": "SI", "name": "Slovenia"},
        {"code": "HR", "name": "Croatia"},
        {"code": "BA", "name": "Bosnia and Herzegovina"},
        {"code": "ME", "name": "Montenegro"},
        {"code": "RS", "name": "Serbia"},
        {"code": "MK", "name": "North Macedonia"},
        {"code": "AL", "name": "Albania"},
        {"code": "XK", "name": "Kosovo"},
        {"code": "BG", "name": "Bulgaria"},
        {"code": "RO", "name": "Romania"},
        {"code": "MD", "name": "Moldova"},
        {"code": "UA", "name": "Ukraine"},
        {"code": "BY", "name": "Belarus"},
        {"code": "LT", "name": "Lithuania"},
        {"code": "LV", "name": "Latvia"},
        {"code": "EE", "name": "Estonia"},
        {"code": "RU", "name": "Russia"},
        {"code": "GE", "name": "Georgia"},
        {"code": "AM", "name": "Armenia"},
        {"code": "AZ", "name": "Azerbaijan"},
        {"code": "KZ", "name": "Kazakhstan"},
        {"code": "KG", "name": "Kyrgyzstan"},
        {"code": "TJ", "name": "Tajikistan"},
        {"code": "TM", "name": "Turkmenistan"},
        {"code": "UZ", "name": "Uzbekistan"},
        {"code": "AF", "name": "Afghanistan"},
        {"code": "MN", "name": "Mongolia"},
        {"code": "NP", "name": "Nepal"},
        {"code": "BT", "name": "Bhutan"},
        {"code": "LK", "name": "Sri Lanka"},
        {"code": "MV", "name": "Maldives"},
        {"code": "MM", "name": "Myanmar"},
        {"code": "LA", "name": "Laos"},
        {"code": "KH", "name": "Cambodia"},
        {"code": "BN", "name": "Brunei"},
        {"code": "TL", "name": "Timor-Leste"},
        {"code": "PG", "name": "Papua New Guinea"},
        {"code": "SB", "name": "Solomon Islands"},
        {"code": "VU", "name": "Vanuatu"},
        {"code": "NC", "name": "New Caledonia"},
        {"code": "FJ", "name": "Fiji"},
        {"code": "NZ", "name": "New Zealand"},
        {"code": "TO", "name": "Tonga"},
        {"code": "WS", "name": "Samoa"},
        {"code": "KI", "name": "Kiribati"},
        {"code": "TV", "name": "Tuvalu"},
        {"code": "NR", "name": "Nauru"},
        {"code": "PW", "name": "Palau"},
        {"code": "FM", "name": "Federated States of Micronesia"},
        {"code": "MH", "name": "Marshall Islands"}
    ]

def get_industry_list() -> List[str]:
    """Get list of industries"""
    return [
        "Technology",
        "Financial Services",
        "Healthcare",
        "Manufacturing",
        "Retail",
        "Education",
        "Government",
        "Non-profit",
        "Consulting",
        "Media & Entertainment",
        "Transportation",
        "Energy",
        "Real Estate",
        "Agriculture",
        "Construction",
        "Telecommunications",
        "Automotive",
        "Aerospace",
        "Pharmaceutical",
        "Food & Beverage",
        "Fashion",
        "Sports",
        "Travel & Tourism",
        "Insurance",
        "Legal",
        "Accounting",
        "Marketing & Advertising",
        "Research",
        "Mining",
        "Utilities",
        "Other"
    ]

def get_company_size_list() -> List[str]:
    """Get list of company sizes"""
    return [
        "1-10 employees",
        "11-50 employees",
        "51-200 employees",
        "201-500 employees",
        "501-1000 employees",
        "1001-5000 employees",
        "5001-10000 employees",
        "10000+ employees"
    ]

def get_timezone_list() -> List[Dict[str, str]]:
    """Get list of common timezones"""
    return [
        {"value": "UTC", "label": "UTC (Coordinated Universal Time)"},
        {"value": "America/New_York", "label": "Eastern Time (US & Canada)"},
        {"value": "America/Chicago", "label": "Central Time (US & Canada)"},
        {"value": "America/Denver", "label": "Mountain Time (US & Canada)"},
        {"value": "America/Los_Angeles", "label": "Pacific Time (US & Canada)"},
        {"value": "Europe/London", "label": "London"},
        {"value": "Europe/Paris", "label": "Paris"},
        {"value": "Europe/Berlin", "label": "Berlin"},
        {"value": "Europe/Rome", "label": "Rome"},
        {"value": "Europe/Madrid", "label": "Madrid"},
        {"value": "Asia/Riyadh", "label": "Riyadh"},
        {"value": "Asia/Dubai", "label": "Dubai"},
        {"value": "Asia/Kuwait", "label": "Kuwait"},
        {"value": "Asia/Qatar", "label": "Qatar"},
        {"value": "Asia/Bahrain", "label": "Bahrain"},
        {"value": "Asia/Muscat", "label": "Muscat"},
        {"value": "Asia/Baghdad", "label": "Baghdad"},
        {"value": "Asia/Damascus", "label": "Damascus"},
        {"value": "Asia/Amman", "label": "Amman"},
        {"value": "Asia/Beirut", "label": "Beirut"},
        {"value": "Africa/Cairo", "label": "Cairo"},
        {"value": "Africa/Casablanca", "label": "Casablanca"},
        {"value": "Africa/Tunis", "label": "Tunis"},
        {"value": "Africa/Algiers", "label": "Algiers"},
        {"value": "Asia/Tehran", "label": "Tehran"},
        {"value": "Asia/Karachi", "label": "Karachi"},
        {"value": "Asia/Kolkata", "label": "Mumbai, Kolkata, New Delhi"},
        {"value": "Asia/Dhaka", "label": "Dhaka"},
        {"value": "Asia/Bangkok", "label": "Bangkok"},
        {"value": "Asia/Singapore", "label": "Singapore"},
        {"value": "Asia/Manila", "label": "Manila"},
        {"value": "Asia/Jakarta", "label": "Jakarta"},
        {"value": "Asia/Kuala_Lumpur", "label": "Kuala Lumpur"},
        {"value": "Asia/Hong_Kong", "label": "Hong Kong"},
        {"value": "Asia/Shanghai", "label": "Shanghai"},
        {"value": "Asia/Tokyo", "label": "Tokyo"},
        {"value": "Asia/Seoul", "label": "Seoul"},
        {"value": "Australia/Sydney", "label": "Sydney"},
        {"value": "Australia/Melbourne", "label": "Melbourne"},
        {"value": "Pacific/Auckland", "label": "Auckland"}
    ]

def call_external_service(service_url: str, endpoint: str, method: str = 'GET',
                         data: Optional[Dict] = None, headers: Optional[Dict] = None,
                         timeout: int = 30) -> Optional[Dict]:
    """Make HTTP call to external service"""
    try:
        url = f"{service_url.rstrip('/')}/{endpoint.lstrip('/')}"

        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        if method.upper() == 'GET':
            response = requests.get(url, headers=default_headers, timeout=timeout)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=default_headers, timeout=timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=default_headers, timeout=timeout)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return None

        if response.status_code < 300:
            return response.json() if response.content else {}
        else:
            logger.error(f"External service call failed: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"External service call error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in external service call: {str(e)}")
        return None

def validate_user_exists(user_id: str) -> bool:
    """Validate user exists in auth service"""
    auth_service_url = current_app.config.get('AUTH_SERVICE_URL')
    if not auth_service_url:
        return False

    result = call_external_service(
        auth_service_url,
        f'api/auth/users/{user_id}/exists',
        method='GET'
    )

    return result.get('exists', False) if result else False

def notify_user(user_id: str, notification_type: str, data: Dict) -> bool:
    """Send notification via notification service"""
    notification_service_url = current_app.config.get('NOTIFICATION_SERVICE_URL')
    if not notification_service_url:
        return False

    payload = {
        'user_id': user_id,
        'type': notification_type,
        'data': data
    }

    result = call_external_service(
        notification_service_url,
        'api/notifications/send',
        method='POST',
        data=payload
    )

    return result is not None

def calculate_storage_usage(user_profile_id: str) -> float:
    """Calculate user's storage usage in GB"""
    # This would typically call the file service to get actual usage
    # For now, return a placeholder
    return 0.0

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def generate_usage_report(user_profile_id: str, start_date: datetime, end_date: datetime) -> Dict:
    """Generate usage report for user"""
    from models import UsageRecord, UserSubscription

    # Get usage records for the period
    usage_records = UsageRecord.query.filter(
        UsageRecord.user_profile_id == user_profile_id,
        UsageRecord.created_at >= start_date,
        UsageRecord.created_at <= end_date
    ).all()

    # Aggregate usage by type
    usage_summary = {}
    for record in usage_records:
        usage_type = record.usage_type.value
        if usage_type not in usage_summary:
            usage_summary[usage_type] = {'count': 0, 'amount': 0.0}

        usage_summary[usage_type]['count'] += 1
        usage_summary[usage_type]['amount'] += record.amount

    # Get subscription info
    subscription = UserSubscription.query.filter_by(user_profile_id=user_profile_id).first()

    return {
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'usage_summary': usage_summary,
        'subscription': subscription.to_dict() if subscription else None,
        'total_records': len(usage_records)
    }

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 3) -> str:
    """Mask sensitive data keeping only first and last few characters visible"""
    if not data or len(data) <= visible_chars * 2:
        return data

    start = data[:visible_chars]
    end = data[-visible_chars:]
    middle = mask_char * (len(data) - visible_chars * 2)

    return f"{start}{middle}{end}"

def validate_json_schema(data: Dict, schema: Dict) -> Tuple[bool, List[str]]:
    """Validate JSON data against schema"""
    try:
        import jsonschema
        jsonschema.validate(data, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]
    except Exception as e:
        return False, [f"Schema validation error: {str(e)}"]

def cache_key_for_user(user_id: str, key_suffix: str) -> str:
    """Generate cache key for user-specific data"""
    return f"user:{user_id}:{key_suffix}"

def rate_limit_key(user_id: str, endpoint: str) -> str:
    """Generate rate limit key for user and endpoint"""
    return f"rate_limit:user:{user_id}:{endpoint}"

def get_client_ip(request) -> str:
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', '127.0.0.1')

def get_user_agent(request) -> str:
    """Get user agent from request"""
    return request.headers.get('User-Agent', 'Unknown')

def log_user_activity(user_profile_id: str, activity_type: str, description: str,
                     metadata: Optional[Dict] = None, request_obj=None):
    """Log user activity"""
    from models import UserActivity
    from app import db

    try:
        activity = UserActivity(
            user_profile_id=user_profile_id,
            activity_type=activity_type,
            description=description,
            metadata=metadata or {},
            ip_address=get_client_ip(request_obj) if request_obj else None,
            user_agent=get_user_agent(request_obj) if request_obj else None
        )

        db.session.add(activity)
        db.session.commit()

    except Exception as e:
        logger.error(f"Failed to log user activity: {str(e)}")

def paginate_query(query, page: int, per_page: int, max_per_page: int = 100):
    """Paginate SQLAlchemy query with safety limits"""
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)

    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def require_profile_completion(f):
    """Decorator to require profile completion"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_jwt_extended import get_jwt_identity
        from models import UserProfile

        current_user_id = get_jwt_identity()
        profile = UserProfile.query.filter_by(user_id=current_user_id).first()

        if not profile or not profile.onboarding_completed:
            from flask import jsonify
            return jsonify({'error': 'Profile completion required'}), 400

        return f(*args, **kwargs)
    return decorated_function

def require_subscription(f):
    """Decorator to require active subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_jwt_extended import get_jwt_identity
        from models import UserProfile, UserSubscription, SubscriptionStatus

        current_user_id = get_jwt_identity()
        profile = UserProfile.query.filter_by(user_id=current_user_id).first()

        if not profile:
            from flask import jsonify
            return jsonify({'error': 'Profile not found'}), 404

        subscription = profile.subscription
        if not subscription or subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]:
            from flask import jsonify
            return jsonify({'error': 'Active subscription required'}), 402

        return f(*args, **kwargs)
    return decorated_function