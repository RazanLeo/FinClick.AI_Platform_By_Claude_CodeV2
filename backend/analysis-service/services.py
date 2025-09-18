import os
import json
import requests
import time
import uuid
from datetime import datetime, timedelta
from app import db, current_app
from models import (
    Analysis, FinancialData, AnalysisMetric, AnalysisComparison,
    CachedResult, AnalysisTemplate, PerformanceMetrics,
    AnalysisType, AnalysisStatus, Priority
)
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    """Core analysis service"""

    @staticmethod
    def create_analysis(user_id, analysis_type, title, description=None, file_id=None, parameters=None, priority=Priority.NORMAL):
        """Create a new analysis"""
        try:
            analysis = Analysis(
                user_id=user_id,
                file_id=file_id,
                analysis_type=analysis_type,
                title=title,
                description=description,
                parameters=parameters or {},
                priority=priority,
                status=AnalysisStatus.PENDING
            )

            db.session.add(analysis)
            db.session.flush()

            return analysis

        except Exception as e:
            logger.error(f"Create analysis error: {str(e)}")
            raise

    @staticmethod
    def start_processing(analysis_id):
        """Start analysis processing"""
        try:
            analysis = Analysis.query.get(analysis_id)
            if not analysis:
                raise ValueError("Analysis not found")

            # Update status
            analysis.status = AnalysisStatus.QUEUED
            analysis.started_at = datetime.utcnow()

            # Estimate completion time based on analysis type and queue
            estimated_duration = AnalysisService.estimate_processing_time(analysis.analysis_type)
            analysis.estimated_completion_time = datetime.utcnow() + timedelta(minutes=estimated_duration)

            # Record performance metric
            PerformanceMetrics(
                analysis_id=analysis_id,
                metric_name='analysis_queued',
                metric_value=1,
                service_name='analysis-service',
                component='queue_manager'
            )

            # Process based on type
            task_id = str(uuid.uuid4())

            if analysis.analysis_type in [AnalysisType.FINANCIAL_STATEMENT, AnalysisType.RATIO_ANALYSIS]:
                AnalysisService.process_financial_analysis(analysis_id, task_id)
            elif analysis.analysis_type == AnalysisType.TREND_ANALYSIS:
                AnalysisService.process_trend_analysis(analysis_id, task_id)
            elif analysis.analysis_type == AnalysisType.RISK_ASSESSMENT:
                AnalysisService.process_risk_analysis(analysis_id, task_id)
            else:
                AnalysisService.process_generic_analysis(analysis_id, task_id)

            return task_id

        except Exception as e:
            logger.error(f"Start processing error: {str(e)}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            raise

    @staticmethod
    def process_financial_analysis(analysis_id, task_id):
        """Process financial statement analysis"""
        try:
            analysis = Analysis.query.get(analysis_id)
            analysis.status = AnalysisStatus.PROCESSING
            analysis.progress_percentage = 10

            # Get file data if available
            file_data = None
            if analysis.file_id:
                file_data = AnalysisService.get_file_data(analysis.file_id)

            analysis.progress_percentage = 30

            # Extract financial data
            if file_data:
                financial_data = FinancialEngineService.extract_financial_data(file_data)
                AnalysisService.store_financial_data(analysis_id, financial_data)

            analysis.progress_percentage = 50

            # Calculate financial ratios
            ratios = FinancialEngineService.calculate_financial_ratios(analysis_id)
            AnalysisService.store_metrics(analysis_id, ratios)

            analysis.progress_percentage = 70

            # Generate insights
            insights = AnalysisService.generate_insights(analysis_id)
            recommendations = AnalysisService.generate_recommendations(analysis_id)

            analysis.progress_percentage = 90

            # Compile results
            results = {
                'financial_ratios': ratios,
                'data_quality_score': 0.85,
                'completeness_score': 0.92,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }

            analysis.results = results
            analysis.insights = insights
            analysis.recommendations = recommendations
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress_percentage = 100
            analysis.processing_time_seconds = (analysis.completed_at - analysis.started_at).total_seconds()

            # Cache results
            CacheService.cache_analysis_results(analysis_id, results)

            # Record performance metrics
            PerformanceMetrics(
                analysis_id=analysis_id,
                metric_name='processing_time',
                metric_value=analysis.processing_time_seconds,
                metric_unit='seconds',
                service_name='analysis-service',
                component='financial_processor'
            )

            logger.info(f"Financial analysis {analysis_id} completed successfully")

        except Exception as e:
            logger.error(f"Process financial analysis error: {str(e)}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            analysis.completed_at = datetime.utcnow()

    @staticmethod
    def process_trend_analysis(analysis_id, task_id):
        """Process trend analysis"""
        try:
            analysis = Analysis.query.get(analysis_id)
            analysis.status = AnalysisStatus.PROCESSING

            # Implement trend analysis logic
            # This would include time series analysis, pattern recognition, etc.

            results = {
                'trends': [],
                'seasonality': {},
                'forecasts': [],
                'analysis_period': '12_months'
            }

            analysis.results = results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress_percentage = 100

            logger.info(f"Trend analysis {analysis_id} completed successfully")

        except Exception as e:
            logger.error(f"Process trend analysis error: {str(e)}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)

    @staticmethod
    def process_risk_analysis(analysis_id, task_id):
        """Process risk assessment analysis"""
        try:
            analysis = Analysis.query.get(analysis_id)
            analysis.status = AnalysisStatus.PROCESSING

            # Implement risk analysis logic
            # This would include risk scoring, vulnerability assessment, etc.

            results = {
                'risk_score': 65,
                'risk_level': 'moderate',
                'risk_factors': [],
                'mitigation_strategies': []
            }

            analysis.results = results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress_percentage = 100

            logger.info(f"Risk analysis {analysis_id} completed successfully")

        except Exception as e:
            logger.error(f"Process risk analysis error: {str(e)}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)

    @staticmethod
    def process_generic_analysis(analysis_id, task_id):
        """Process generic analysis types"""
        try:
            analysis = Analysis.query.get(analysis_id)
            analysis.status = AnalysisStatus.PROCESSING

            # Basic processing logic for other analysis types
            results = {
                'analysis_type': analysis.analysis_type.value,
                'processed_at': datetime.utcnow().isoformat(),
                'status': 'completed'
            }

            analysis.results = results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress_percentage = 100

            logger.info(f"Generic analysis {analysis_id} completed successfully")

        except Exception as e:
            logger.error(f"Process generic analysis error: {str(e)}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)

    @staticmethod
    def cancel_analysis(analysis_id):
        """Cancel an ongoing analysis"""
        try:
            analysis = Analysis.query.get(analysis_id)
            if analysis:
                analysis.status = AnalysisStatus.CANCELLED
                analysis.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Cancel analysis error: {str(e)}")
            raise

    @staticmethod
    def retry_analysis(analysis_id):
        """Retry a failed analysis"""
        try:
            analysis = Analysis.query.get(analysis_id)
            if analysis:
                # Reset analysis state
                analysis.status = AnalysisStatus.PENDING
                analysis.progress_percentage = 0
                analysis.error_message = None
                analysis.error_details = None
                analysis.started_at = None
                analysis.completed_at = None

                # Start processing again
                return AnalysisService.start_processing(analysis_id)

        except Exception as e:
            logger.error(f"Retry analysis error: {str(e)}")
            raise

    @staticmethod
    def estimate_processing_time(analysis_type):
        """Estimate processing time based on analysis type"""
        time_estimates = {
            AnalysisType.FINANCIAL_STATEMENT: 5,
            AnalysisType.RATIO_ANALYSIS: 3,
            AnalysisType.CASH_FLOW: 4,
            AnalysisType.TREND_ANALYSIS: 8,
            AnalysisType.RISK_ASSESSMENT: 10,
            AnalysisType.BENCHMARKING: 6
        }
        return time_estimates.get(analysis_type, 5)

    @staticmethod
    def get_file_data(file_id):
        """Get file data from file service"""
        try:
            file_service_url = current_app.config.get('FILE_SERVICE_URL')
            if file_service_url:
                response = requests.get(f"{file_service_url}/api/files/{file_id}")
                if response.status_code == 200:
                    return response.json()
            return None
        except Exception as e:
            logger.error(f"Get file data error: {str(e)}")
            return None

    @staticmethod
    def store_financial_data(analysis_id, financial_data):
        """Store extracted financial data"""
        try:
            for data_item in financial_data:
                financial_record = FinancialData(
                    analysis_id=analysis_id,
                    data_type=data_item.get('type'),
                    category=data_item.get('category'),
                    value=data_item.get('value'),
                    currency=data_item.get('currency', 'USD'),
                    period_start=data_item.get('period_start'),
                    period_end=data_item.get('period_end'),
                    confidence=data_item.get('confidence'),
                    source=data_item.get('source', 'extracted')
                )
                db.session.add(financial_record)

        except Exception as e:
            logger.error(f"Store financial data error: {str(e)}")
            raise

    @staticmethod
    def store_metrics(analysis_id, metrics):
        """Store calculated metrics"""
        try:
            for metric_name, metric_data in metrics.items():
                metric_record = AnalysisMetric(
                    analysis_id=analysis_id,
                    metric_name=metric_name,
                    metric_category=metric_data.get('category', 'general'),
                    value=metric_data.get('value'),
                    unit=metric_data.get('unit'),
                    industry_average=metric_data.get('industry_average'),
                    interpretation=metric_data.get('interpretation'),
                    trend=metric_data.get('trend')
                )
                db.session.add(metric_record)

        except Exception as e:
            logger.error(f"Store metrics error: {str(e)}")
            raise

    @staticmethod
    def generate_insights(analysis_id):
        """Generate insights from analysis"""
        try:
            # This would typically use AI/ML models to generate insights
            insights = [
                {
                    'category': 'profitability',
                    'insight': 'Strong profit margins indicate healthy operations',
                    'confidence': 0.85,
                    'importance': 'high'
                },
                {
                    'category': 'liquidity',
                    'insight': 'Current ratio suggests good short-term liquidity',
                    'confidence': 0.78,
                    'importance': 'medium'
                }
            ]
            return insights

        except Exception as e:
            logger.error(f"Generate insights error: {str(e)}")
            return []

    @staticmethod
    def generate_recommendations(analysis_id):
        """Generate recommendations from analysis"""
        try:
            recommendations = [
                {
                    'category': 'operational',
                    'recommendation': 'Consider optimizing working capital management',
                    'priority': 'medium',
                    'impact': 'positive',
                    'timeline': '3-6 months'
                },
                {
                    'category': 'financial',
                    'recommendation': 'Maintain current debt levels to preserve financial flexibility',
                    'priority': 'low',
                    'impact': 'neutral',
                    'timeline': 'ongoing'
                }
            ]
            return recommendations

        except Exception as e:
            logger.error(f"Generate recommendations error: {str(e)}")
            return []

    @staticmethod
    def export_analysis(analysis_id, export_format='pdf', include_charts=True, include_raw_data=False):
        """Export analysis results"""
        try:
            reporting_service_url = current_app.config.get('REPORTING_SERVICE_URL')
            if reporting_service_url:
                payload = {
                    'analysis_id': analysis_id,
                    'format': export_format,
                    'include_charts': include_charts,
                    'include_raw_data': include_raw_data
                }

                response = requests.post(
                    f"{reporting_service_url}/api/reports/analysis/export",
                    json=payload
                )

                if response.status_code == 200:
                    return response.json()

            # Fallback: create basic export
            return {
                'export_id': str(uuid.uuid4()),
                'download_url': f"/api/analysis/{analysis_id}/download",
                'estimated_completion': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }

        except Exception as e:
            logger.error(f"Export analysis error: {str(e)}")
            raise

class FinancialEngineService:
    """Financial analysis engine service"""

    @staticmethod
    def extract_financial_data(file_data):
        """Extract financial data from file"""
        try:
            # Mock financial data extraction
            # In reality, this would parse financial statements, invoices, etc.
            financial_data = [
                {
                    'type': 'revenue',
                    'category': 'sales',
                    'value': 1000000,
                    'currency': 'USD',
                    'period_start': '2023-01-01',
                    'period_end': '2023-12-31',
                    'confidence': 0.95,
                    'source': 'extracted'
                },
                {
                    'type': 'expenses',
                    'category': 'operating',
                    'value': 750000,
                    'currency': 'USD',
                    'period_start': '2023-01-01',
                    'period_end': '2023-12-31',
                    'confidence': 0.90,
                    'source': 'extracted'
                }
            ]
            return financial_data

        except Exception as e:
            logger.error(f"Extract financial data error: {str(e)}")
            return []

    @staticmethod
    def calculate_financial_ratios(analysis_id):
        """Calculate financial ratios"""
        try:
            # Get financial data for analysis
            financial_data = FinancialData.query.filter_by(analysis_id=analysis_id).all()

            # Mock ratio calculations
            ratios = {
                'gross_profit_margin': {
                    'value': 25.0,
                    'unit': 'percentage',
                    'category': 'profitability',
                    'industry_average': 22.5,
                    'interpretation': 'good',
                    'trend': 'improving'
                },
                'current_ratio': {
                    'value': 2.1,
                    'unit': 'ratio',
                    'category': 'liquidity',
                    'industry_average': 1.8,
                    'interpretation': 'excellent',
                    'trend': 'stable'
                },
                'debt_to_equity': {
                    'value': 0.4,
                    'unit': 'ratio',
                    'category': 'solvency',
                    'industry_average': 0.6,
                    'interpretation': 'good',
                    'trend': 'improving'
                }
            }
            return ratios

        except Exception as e:
            logger.error(f"Calculate financial ratios error: {str(e)}")
            return {}

class CacheService:
    """Caching service for analysis results"""

    @staticmethod
    def get_from_cache(cache_key):
        """Get data from cache"""
        try:
            if current_app.redis:
                cached_data = current_app.redis.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    @staticmethod
    def set_in_cache(cache_key, data, ttl=3600):
        """Set data in cache"""
        try:
            if current_app.redis:
                current_app.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(data, default=str)
                )
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")

    @staticmethod
    def cache_analysis_results(analysis_id, results):
        """Cache analysis results"""
        try:
            cache_key = f"analysis_results_{analysis_id}"
            CacheService.set_in_cache(cache_key, results, ttl=7200)  # 2 hours

            # Store in database cache table
            cached_result = CachedResult(
                analysis_id=analysis_id,
                cache_key=cache_key,
                result_type='complete_results',
                result_data=results,
                expires_at=datetime.utcnow() + timedelta(hours=2)
            )
            db.session.add(cached_result)

        except Exception as e:
            logger.error(f"Cache analysis results error: {str(e)}")

    @staticmethod
    def get_cached_analysis(analysis_id):
        """Get cached analysis data"""
        try:
            cached_result = CachedResult.query.filter_by(
                analysis_id=analysis_id,
                result_type='complete_results'
            ).first()

            if cached_result and not cached_result.is_expired():
                cached_result.access_count += 1
                cached_result.last_accessed_at = datetime.utcnow()
                return cached_result.result_data

            return None
        except Exception as e:
            logger.error(f"Get cached analysis error: {str(e)}")
            return None

class MetricsService:
    """Metrics and performance tracking service"""

    @staticmethod
    def get_user_metrics_summary(user_id, days=30):
        """Get metrics summary for user"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Count analyses by status
            analyses_count = db.session.query(
                Analysis.status,
                db.func.count(Analysis.id)
            ).filter(
                Analysis.user_id == user_id,
                Analysis.created_at >= start_date
            ).group_by(Analysis.status).all()

            # Calculate average processing time
            avg_processing_time = db.session.query(
                db.func.avg(Analysis.processing_time_seconds)
            ).filter(
                Analysis.user_id == user_id,
                Analysis.status == AnalysisStatus.COMPLETED,
                Analysis.created_at >= start_date
            ).scalar()

            # Get most used analysis types
            analysis_types = db.session.query(
                Analysis.analysis_type,
                db.func.count(Analysis.id)
            ).filter(
                Analysis.user_id == user_id,
                Analysis.created_at >= start_date
            ).group_by(Analysis.analysis_type).all()

            summary = {
                'total_analyses': sum(count for _, count in analyses_count),
                'analyses_by_status': {status.value: count for status, count in analyses_count},
                'avg_processing_time': avg_processing_time or 0,
                'analysis_types': {type_.value: count for type_, count in analysis_types},
                'period_days': days
            }

            return summary

        except Exception as e:
            logger.error(f"Get user metrics summary error: {str(e)}")
            return {}

    @staticmethod
    def get_performance_metrics(hours=24, component=None):
        """Get system performance metrics"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)

            query = PerformanceMetrics.query.filter(
                PerformanceMetrics.recorded_at >= start_time
            )

            if component:
                query = query.filter(PerformanceMetrics.component == component)

            metrics = query.all()

            # Group metrics by name
            grouped_metrics = {}
            for metric in metrics:
                if metric.metric_name not in grouped_metrics:
                    grouped_metrics[metric.metric_name] = []
                grouped_metrics[metric.metric_name].append(metric.to_dict())

            return grouped_metrics

        except Exception as e:
            logger.error(f"Get performance metrics error: {str(e)}")
            return {}

    @staticmethod
    def record_performance_metric(metric_name, value, unit=None, component=None, metadata=None):
        """Record a performance metric"""
        try:
            metric = PerformanceMetrics(
                metric_name=metric_name,
                metric_value=value,
                metric_unit=unit,
                service_name='analysis-service',
                component=component,
                metadata=metadata
            )
            db.session.add(metric)

        except Exception as e:
            logger.error(f"Record performance metric error: {str(e)}")

class ComparisonService:
    """Analysis comparison service"""

    @staticmethod
    def create_comparison(base_analysis_id, compared_analysis_id, comparison_type, title=None):
        """Create analysis comparison"""
        try:
            base_analysis = Analysis.query.get(base_analysis_id)
            if not base_analysis:
                raise ValueError("Base analysis not found")

            # Generate title if not provided
            if not title:
                title = f"Comparison: {base_analysis.title} vs Analysis {compared_analysis_id}"

            comparison = AnalysisComparison(
                base_analysis_id=base_analysis_id,
                compared_analysis_id=compared_analysis_id,
                comparison_type=comparison_type,
                comparison_title=title
            )

            # Perform comparison analysis
            comparison_results = ComparisonService.perform_comparison(
                base_analysis_id,
                compared_analysis_id,
                comparison_type
            )

            comparison.variance_analysis = comparison_results.get('variance_analysis')
            comparison.key_differences = comparison_results.get('key_differences')
            comparison.trend_analysis = comparison_results.get('trend_analysis')

            db.session.add(comparison)

            return comparison

        except Exception as e:
            logger.error(f"Create comparison error: {str(e)}")
            raise

    @staticmethod
    def perform_comparison(base_analysis_id, compared_analysis_id, comparison_type):
        """Perform actual comparison analysis"""
        try:
            # Mock comparison results
            results = {
                'variance_analysis': {
                    'revenue_variance': 15.2,
                    'profit_variance': -5.8,
                    'efficiency_variance': 8.3
                },
                'key_differences': [
                    'Revenue increased by 15.2% compared to previous period',
                    'Profit margin decreased by 5.8%',
                    'Operational efficiency improved by 8.3%'
                ],
                'trend_analysis': {
                    'overall_trend': 'positive',
                    'growth_rate': 12.5,
                    'stability_score': 0.78
                }
            }

            return results

        except Exception as e:
            logger.error(f"Perform comparison error: {str(e)}")
            return {}

class TemplateService:
    """Analysis template service"""

    @staticmethod
    def get_templates(analysis_type=None, industry=None, complexity=None):
        """Get analysis templates"""
        try:
            query = AnalysisTemplate.query.filter_by(is_active=True)

            if analysis_type:
                try:
                    type_enum = AnalysisType(analysis_type)
                    query = query.filter_by(analysis_type=type_enum)
                except ValueError:
                    pass

            if industry:
                query = query.filter_by(industry=industry)

            if complexity:
                query = query.filter_by(complexity_level=complexity)

            return query.order_by(AnalysisTemplate.usage_count.desc()).all()

        except Exception as e:
            logger.error(f"Get templates error: {str(e)}")
            return []

    @staticmethod
    def create_analysis_from_template(template_id, user_id, title=None, parameters=None, file_id=None):
        """Create analysis from template"""
        try:
            template = AnalysisTemplate.query.get(template_id)
            if not template:
                raise ValueError("Template not found")

            # Merge parameters
            merged_parameters = template.default_parameters.copy() if template.default_parameters else {}
            if parameters:
                merged_parameters.update(parameters)

            # Generate title if not provided
            if not title:
                title = f"{template.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

            # Create analysis
            analysis = AnalysisService.create_analysis(
                user_id=user_id,
                analysis_type=template.analysis_type,
                title=title,
                description=template.description,
                file_id=file_id,
                parameters=merged_parameters
            )

            # Update template usage
            template.usage_count += 1

            return analysis

        except Exception as e:
            logger.error(f"Create analysis from template error: {str(e)}")
            raise