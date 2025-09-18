from app import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import enum
import json

class AnalysisType(enum.Enum):
    FINANCIAL_STATEMENT = "financial_statement"
    RATIO_ANALYSIS = "ratio_analysis"
    CASH_FLOW = "cash_flow"
    BUDGET_ANALYSIS = "budget_analysis"
    TREND_ANALYSIS = "trend_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    PROFITABILITY = "profitability"
    LIQUIDITY = "liquidity"
    SOLVENCY = "solvency"
    EFFICIENCY = "efficiency"
    MARKET_ANALYSIS = "market_analysis"
    BENCHMARKING = "benchmarking"

class AnalysisStatus(enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Analysis(db.Model):
    __tablename__ = 'analyses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    file_id = db.Column(db.String(36), nullable=True, index=True)  # Source file if any

    # Analysis configuration
    analysis_type = db.Column(db.Enum(AnalysisType), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parameters = db.Column(db.JSON, nullable=True)

    # Processing information
    status = db.Column(db.Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    priority = db.Column(db.Enum(Priority), default=Priority.NORMAL, nullable=False)
    progress_percentage = db.Column(db.Integer, default=0, nullable=False)
    estimated_completion_time = db.Column(db.DateTime, nullable=True)

    # Results
    results = db.Column(db.JSON, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    insights = db.Column(db.JSON, nullable=True)
    recommendations = db.Column(db.JSON, nullable=True)

    # Metrics and scores
    confidence_score = db.Column(db.Float, nullable=True)
    accuracy_score = db.Column(db.Float, nullable=True)
    quality_score = db.Column(db.Float, nullable=True)

    # Processing metadata
    processing_time_seconds = db.Column(db.Float, nullable=True)
    engine_version = db.Column(db.String(50), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    error_details = db.Column(db.JSON, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    financial_data = db.relationship('FinancialData', backref='analysis', lazy=True, cascade='all, delete-orphan')
    metrics = db.relationship('AnalysisMetric', backref='analysis', lazy=True, cascade='all, delete-orphan')
    comparisons = db.relationship('AnalysisComparison', backref='analysis', lazy=True)
    cached_results = db.relationship('CachedResult', backref='analysis', lazy=True, cascade='all, delete-orphan')

    def get_elapsed_time(self):
        """Get elapsed processing time"""
        if self.started_at:
            end_time = self.completed_at or datetime.utcnow()
            return (end_time - self.started_at).total_seconds()
        return 0

    def is_expired(self):
        """Check if analysis results are expired"""
        if self.completed_at:
            # Results expire after 30 days
            expiry_date = self.completed_at + timedelta(days=30)
            return datetime.utcnow() > expiry_date
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'analysis_type': self.analysis_type.value,
            'title': self.title,
            'description': self.description,
            'parameters': self.parameters,
            'status': self.status.value,
            'priority': self.priority.value,
            'progress_percentage': self.progress_percentage,
            'estimated_completion_time': self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
            'results': self.results,
            'summary': self.summary,
            'insights': self.insights,
            'recommendations': self.recommendations,
            'confidence_score': self.confidence_score,
            'accuracy_score': self.accuracy_score,
            'quality_score': self.quality_score,
            'processing_time_seconds': self.processing_time_seconds,
            'engine_version': self.engine_version,
            'error_message': self.error_message,
            'elapsed_time': self.get_elapsed_time(),
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat()
        }

class FinancialData(db.Model):
    __tablename__ = 'financial_data'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analyses.id'), nullable=False)

    # Data classification
    data_type = db.Column(db.String(100), nullable=False)  # revenue, expenses, assets, liabilities, etc.
    category = db.Column(db.String(100), nullable=True)
    subcategory = db.Column(db.String(100), nullable=True)

    # Time period
    period_start = db.Column(db.Date, nullable=True)
    period_end = db.Column(db.Date, nullable=True)
    fiscal_year = db.Column(db.Integer, nullable=True)
    quarter = db.Column(db.Integer, nullable=True)

    # Values
    value = db.Column(db.Numeric(20, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD', nullable=False)
    unit = db.Column(db.String(20), nullable=True)  # thousands, millions, etc.

    # Additional metadata
    source = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    metadata = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'data_type': self.data_type,
            'category': self.category,
            'subcategory': self.subcategory,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'fiscal_year': self.fiscal_year,
            'quarter': self.quarter,
            'value': float(self.value),
            'currency': self.currency,
            'unit': self.unit,
            'source': self.source,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }

class AnalysisMetric(db.Model):
    __tablename__ = 'analysis_metrics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analyses.id'), nullable=False)

    # Metric information
    metric_name = db.Column(db.String(100), nullable=False)
    metric_category = db.Column(db.String(50), nullable=False)  # profitability, liquidity, efficiency, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=True)  # percentage, ratio, currency, etc.

    # Benchmarking
    industry_average = db.Column(db.Float, nullable=True)
    benchmark_value = db.Column(db.Float, nullable=True)
    percentile_rank = db.Column(db.Float, nullable=True)

    # Interpretation
    interpretation = db.Column(db.String(50), nullable=True)  # excellent, good, fair, poor, critical
    trend = db.Column(db.String(20), nullable=True)  # improving, declining, stable
    significance = db.Column(db.String(20), nullable=True)  # high, medium, low

    # Additional metadata
    calculation_method = db.Column(db.String(200), nullable=True)
    data_quality = db.Column(db.Float, nullable=True)
    metadata = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'metric_name': self.metric_name,
            'metric_category': self.metric_category,
            'value': self.value,
            'unit': self.unit,
            'industry_average': self.industry_average,
            'benchmark_value': self.benchmark_value,
            'percentile_rank': self.percentile_rank,
            'interpretation': self.interpretation,
            'trend': self.trend,
            'significance': self.significance,
            'calculation_method': self.calculation_method,
            'data_quality': self.data_quality,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }

class AnalysisComparison(db.Model):
    __tablename__ = 'analysis_comparisons'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    base_analysis_id = db.Column(db.String(36), db.ForeignKey('analyses.id'), nullable=False)
    compared_analysis_id = db.Column(db.String(36), nullable=False)  # Can be external reference

    # Comparison metadata
    comparison_type = db.Column(db.String(50), nullable=False)  # period_over_period, peer_comparison, etc.
    comparison_title = db.Column(db.String(200), nullable=False)
    comparison_summary = db.Column(db.Text, nullable=True)

    # Results
    variance_analysis = db.Column(db.JSON, nullable=True)
    key_differences = db.Column(db.JSON, nullable=True)
    trend_analysis = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'base_analysis_id': self.base_analysis_id,
            'compared_analysis_id': self.compared_analysis_id,
            'comparison_type': self.comparison_type,
            'comparison_title': self.comparison_title,
            'comparison_summary': self.comparison_summary,
            'variance_analysis': self.variance_analysis,
            'key_differences': self.key_differences,
            'trend_analysis': self.trend_analysis,
            'created_at': self.created_at.isoformat()
        }

class CachedResult(db.Model):
    __tablename__ = 'cached_results'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analyses.id'), nullable=False)

    # Cache metadata
    cache_key = db.Column(db.String(255), nullable=False, unique=True)
    result_type = db.Column(db.String(50), nullable=False)  # summary, chart_data, report, etc.
    result_data = db.Column(db.JSON, nullable=False)

    # Cache management
    expires_at = db.Column(db.DateTime, nullable=False)
    access_count = db.Column(db.Integer, default=0, nullable=False)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def is_expired(self):
        """Check if cache is expired"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'cache_key': self.cache_key,
            'result_type': self.result_type,
            'result_data': self.result_data,
            'expires_at': self.expires_at.isoformat(),
            'access_count': self.access_count,
            'last_accessed_at': self.last_accessed_at.isoformat(),
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat()
        }

class AnalysisTemplate(db.Model):
    __tablename__ = 'analysis_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    analysis_type = db.Column(db.Enum(AnalysisType), nullable=False)

    # Template configuration
    template_config = db.Column(db.JSON, nullable=False)
    default_parameters = db.Column(db.JSON, nullable=True)
    required_data_types = db.Column(db.JSON, nullable=True)

    # Template metadata
    industry = db.Column(db.String(100), nullable=True)
    complexity_level = db.Column(db.String(20), nullable=True)  # basic, intermediate, advanced
    estimated_duration = db.Column(db.Integer, nullable=True)  # in minutes

    # Usage statistics
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    avg_rating = db.Column(db.Float, nullable=True)

    # Template management
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.String(36), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'analysis_type': self.analysis_type.value,
            'template_config': self.template_config,
            'default_parameters': self.default_parameters,
            'required_data_types': self.required_data_types,
            'industry': self.industry,
            'complexity_level': self.complexity_level,
            'estimated_duration': self.estimated_duration,
            'usage_count': self.usage_count,
            'avg_rating': self.avg_rating,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PerformanceMetrics(db.Model):
    __tablename__ = 'performance_metrics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analyses.id'), nullable=True)

    # Performance data
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20), nullable=True)

    # System information
    service_name = db.Column(db.String(50), nullable=False)
    component = db.Column(db.String(50), nullable=True)
    environment = db.Column(db.String(20), nullable=True)  # dev, staging, prod

    # Metadata
    metadata = db.Column(db.JSON, nullable=True)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'service_name': self.service_name,
            'component': self.component,
            'environment': self.environment,
            'metadata': self.metadata,
            'recorded_at': self.recorded_at.isoformat()
        }