from app import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import enum

class FileStatus(enum.Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    DELETED = "deleted"

class FileType(enum.Enum):
    PDF = "pdf"
    IMAGE = "image"
    EXCEL = "excel"
    CSV = "csv"
    WORD = "word"
    POWERPOINT = "powerpoint"
    TEXT = "text"
    OTHER = "other"

class OCRStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class FileRecord(db.Model):
    __tablename__ = 'file_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_type = db.Column(db.Enum(FileType), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False, index=True)  # SHA-256 hash

    # Status and metadata
    status = db.Column(db.Enum(FileStatus), default=FileStatus.UPLOADING, nullable=False)
    metadata = db.Column(db.JSON, nullable=True)

    # File validation
    is_valid = db.Column(db.Boolean, default=None, nullable=True)
    validation_errors = db.Column(db.JSON, nullable=True)

    # Storage information
    storage_provider = db.Column(db.String(50), default='local', nullable=False)  # local, s3, etc.
    storage_path = db.Column(db.String(500), nullable=True)
    public_url = db.Column(db.String(500), nullable=True)

    # Processing timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processing_started_at = db.Column(db.DateTime, nullable=True)
    processing_completed_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    ocr_results = db.relationship('OCRResult', backref='file_record', lazy=True, cascade='all, delete-orphan')
    analysis_requests = db.relationship('FileAnalysisRequest', backref='file_record', lazy=True)

    def get_file_type_from_extension(self, filename):
        """Determine file type from extension"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''

        type_mapping = {
            'pdf': FileType.PDF,
            'jpg': FileType.IMAGE,
            'jpeg': FileType.IMAGE,
            'png': FileType.IMAGE,
            'gif': FileType.IMAGE,
            'bmp': FileType.IMAGE,
            'tiff': FileType.IMAGE,
            'xlsx': FileType.EXCEL,
            'xls': FileType.EXCEL,
            'csv': FileType.CSV,
            'doc': FileType.WORD,
            'docx': FileType.WORD,
            'ppt': FileType.POWERPOINT,
            'pptx': FileType.POWERPOINT,
            'txt': FileType.TEXT,
        }

        return type_mapping.get(extension, FileType.OTHER)

    def is_supported_for_ocr(self):
        """Check if file type is supported for OCR"""
        ocr_supported_types = [FileType.PDF, FileType.IMAGE]
        return self.file_type in ocr_supported_types

    def is_supported_for_analysis(self):
        """Check if file type is supported for financial analysis"""
        analysis_supported_types = [
            FileType.PDF, FileType.EXCEL, FileType.CSV,
            FileType.IMAGE, FileType.WORD
        ]
        return self.file_type in analysis_supported_types

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_size': self.file_size,
            'file_type': self.file_type.value,
            'mime_type': self.mime_type,
            'file_hash': self.file_hash,
            'status': self.status.value,
            'metadata': self.metadata,
            'is_valid': self.is_valid,
            'validation_errors': self.validation_errors,
            'storage_provider': self.storage_provider,
            'public_url': self.public_url,
            'uploaded_at': self.uploaded_at.isoformat(),
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processing_completed_at': self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'ocr_status': self.ocr_results[0].status.value if self.ocr_results else None,
            'can_analyze': self.is_supported_for_analysis(),
            'can_ocr': self.is_supported_for_ocr()
        }

class OCRResult(db.Model):
    __tablename__ = 'ocr_results'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_record_id = db.Column(db.String(36), db.ForeignKey('file_records.id'), nullable=False)

    # OCR processing info
    ocr_provider = db.Column(db.String(50), nullable=False)  # tesseract, google_vision, aws_textract
    status = db.Column(db.Enum(OCRStatus), default=OCRStatus.PENDING, nullable=False)

    # Extracted content
    extracted_text = db.Column(db.Text, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    page_count = db.Column(db.Integer, default=1, nullable=False)

    # Structured data
    structured_data = db.Column(db.JSON, nullable=True)  # Tables, forms, etc.
    entities = db.Column(db.JSON, nullable=True)  # Named entities, amounts, dates

    # Processing metadata
    processing_time_seconds = db.Column(db.Float, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'file_record_id': self.file_record_id,
            'ocr_provider': self.ocr_provider,
            'status': self.status.value,
            'extracted_text': self.extracted_text,
            'confidence_score': self.confidence_score,
            'page_count': self.page_count,
            'structured_data': self.structured_data,
            'entities': self.entities,
            'processing_time_seconds': self.processing_time_seconds,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class FileAnalysisRequest(db.Model):
    __tablename__ = 'file_analysis_requests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_record_id = db.Column(db.String(36), db.ForeignKey('file_records.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False, index=True)

    # Analysis parameters
    analysis_type = db.Column(db.String(100), nullable=False)
    parameters = db.Column(db.JSON, nullable=True)

    # Status
    status = db.Column(db.String(50), default='pending', nullable=False)
    progress_percentage = db.Column(db.Integer, default=0, nullable=False)

    # Results
    analysis_id = db.Column(db.String(36), nullable=True)  # ID from analysis service
    result_summary = db.Column(db.JSON, nullable=True)

    # Timestamps
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'file_record_id': self.file_record_id,
            'user_id': self.user_id,
            'analysis_type': self.analysis_type,
            'parameters': self.parameters,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'analysis_id': self.analysis_id,
            'result_summary': self.result_summary,
            'requested_at': self.requested_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class FileValidationRule(db.Model):
    __tablename__ = 'file_validation_rules'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_name = db.Column(db.String(100), nullable=False, unique=True)
    file_types = db.Column(db.JSON, nullable=False)  # List of supported file types
    max_file_size = db.Column(db.BigInteger, nullable=True)
    allowed_mime_types = db.Column(db.JSON, nullable=True)
    validation_script = db.Column(db.Text, nullable=True)  # Custom validation logic
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class FileShare(db.Model):
    __tablename__ = 'file_shares'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_record_id = db.Column(db.String(36), db.ForeignKey('file_records.id'), nullable=False)
    owner_user_id = db.Column(db.String(36), nullable=False)
    shared_with_user_id = db.Column(db.String(36), nullable=True)  # Null for public shares

    # Sharing configuration
    share_token = db.Column(db.String(255), unique=True, nullable=False)
    permissions = db.Column(db.JSON, nullable=False)  # read, download, analyze
    is_public = db.Column(db.Boolean, default=False, nullable=False)

    # Expiration
    expires_at = db.Column(db.DateTime, nullable=True)
    max_downloads = db.Column(db.Integer, nullable=True)
    download_count = db.Column(db.Integer, default=0, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = db.Column(db.DateTime, nullable=True)

    def is_expired(self):
        """Check if share is expired"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        if self.max_downloads and self.download_count >= self.max_downloads:
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'file_record_id': self.file_record_id,
            'owner_user_id': self.owner_user_id,
            'shared_with_user_id': self.shared_with_user_id,
            'share_token': self.share_token,
            'permissions': self.permissions,
            'is_public': self.is_public,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'max_downloads': self.max_downloads,
            'download_count': self.download_count,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat(),
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None
        }

class FileVersion(db.Model):
    __tablename__ = 'file_versions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_record_id = db.Column(db.String(36), db.ForeignKey('file_records.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    upload_reason = db.Column(db.String(200), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint('file_record_id', 'version_number'),)

class FileActivity(db.Model):
    __tablename__ = 'file_activities'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_record_id = db.Column(db.String(36), db.ForeignKey('file_records.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # upload, download, share, analyze, delete
    description = db.Column(db.String(500), nullable=False)
    metadata = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'file_record_id': self.file_record_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }