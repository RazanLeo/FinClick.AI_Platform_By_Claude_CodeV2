from app import db
from datetime import datetime
import uuid
import enum

class ReportType(enum.Enum):
    FINANCIAL_ANALYSIS = "financial_analysis"
    MONTHLY_SUMMARY = "monthly_summary"
    QUARTERLY_REPORT = "quarterly_report"
    ANNUAL_REPORT = "annual_report"
    CUSTOM = "custom"

class ReportStatus(enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.Enum(ReportType), nullable=False)
    status = db.Column(db.Enum(ReportStatus), default=ReportStatus.PENDING)

    # Content and metadata
    content = db.Column(db.JSON, nullable=True)
    template_id = db.Column(db.String(36), nullable=True)
    parameters = db.Column(db.JSON, nullable=True)

    # File information
    file_path = db.Column(db.String(500), nullable=True)
    file_size = db.Column(db.BigInteger, nullable=True)
    download_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'report_type': self.report_type.value,
            'status': self.status.value,
            'content': self.content,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'download_url': self.download_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ReportTemplate(db.Model):
    __tablename__ = 'report_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    report_type = db.Column(db.Enum(ReportType), nullable=False)
    template_content = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type.value,
            'template_content': self.template_content,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }