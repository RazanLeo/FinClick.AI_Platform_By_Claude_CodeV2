from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db, limiter
from models import (
    Analysis, FinancialData, AnalysisMetric, AnalysisComparison,
    CachedResult, AnalysisTemplate, PerformanceMetrics,
    AnalysisType, AnalysisStatus, Priority
)
from services import (
    AnalysisService, FinancialEngineService, CacheService,
    MetricsService, ComparisonService, TemplateService
)
import logging

logger = logging.getLogger(__name__)

@app.route('/api/analysis/request', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def request_analysis():
    """Request a new analysis"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required_fields = ['analysis_type', 'title']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate analysis type
        try:
            analysis_type = AnalysisType(data['analysis_type'])
        except ValueError:
            return jsonify({'error': 'Invalid analysis type'}), 400

        # Create analysis request
        analysis = AnalysisService.create_analysis(
            user_id=current_user_id,
            analysis_type=analysis_type,
            title=data['title'],
            description=data.get('description'),
            file_id=data.get('file_id'),
            parameters=data.get('parameters', {}),
            priority=Priority(data.get('priority', 'normal'))
        )

        # Start processing
        task_id = AnalysisService.start_processing(analysis.id)

        db.session.commit()

        return jsonify({
            'message': 'Analysis request created successfully',
            'analysis_id': analysis.id,
            'task_id': task_id,
            'analysis': analysis.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Analysis request error: {str(e)}")
        return jsonify({'error': 'Failed to create analysis request'}), 500

@app.route('/api/analysis', methods=['GET'])
@jwt_required()
def get_analyses():
    """Get user's analyses with pagination"""
    try:
        current_user_id = get_jwt_identity()

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        analysis_type = request.args.get('type')
        status = request.args.get('status')
        search = request.args.get('search')

        # Build query
        query = Analysis.query.filter_by(user_id=current_user_id)

        if analysis_type:
            try:
                type_enum = AnalysisType(analysis_type)
                query = query.filter_by(analysis_type=type_enum)
            except ValueError:
                pass

        if status:
            try:
                status_enum = AnalysisStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                pass

        if search:
            query = query.filter(
                db.or_(
                    Analysis.title.ilike(f'%{search}%'),
                    Analysis.description.ilike(f'%{search}%')
                )
            )

        # Paginate
        analyses = query.order_by(Analysis.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'analyses': [analysis.to_dict() for analysis in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': analyses.page,
            'per_page': analyses.per_page,
            'has_next': analyses.has_next,
            'has_prev': analyses.has_prev
        }), 200

    except Exception as e:
        logger.error(f"Get analyses error: {str(e)}")
        return jsonify({'error': 'Failed to get analyses'}), 500

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    """Get specific analysis details"""
    try:
        current_user_id = get_jwt_identity()

        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        # Get cached results if available
        cached_data = CacheService.get_cached_analysis(analysis_id)

        response_data = {
            'analysis': analysis.to_dict(),
            'financial_data': [data.to_dict() for data in analysis.financial_data],
            'metrics': [metric.to_dict() for metric in analysis.metrics],
            'cached_data': cached_data
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Get analysis error: {str(e)}")
        return jsonify({'error': 'Failed to get analysis'}), 500

@app.route('/api/analysis/<analysis_id>/status', methods=['GET'])
@jwt_required()
def get_analysis_status(analysis_id):
    """Get analysis status and progress"""
    try:
        current_user_id = get_jwt_identity()

        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        return jsonify({
            'analysis_id': analysis.id,
            'status': analysis.status.value,
            'progress_percentage': analysis.progress_percentage,
            'estimated_completion_time': analysis.estimated_completion_time.isoformat() if analysis.estimated_completion_time else None,
            'elapsed_time': analysis.get_elapsed_time(),
            'error_message': analysis.error_message
        }), 200

    except Exception as e:
        logger.error(f"Get analysis status error: {str(e)}")
        return jsonify({'error': 'Failed to get analysis status'}), 500

@app.route('/api/analysis/<analysis_id>/results', methods=['GET'])
@jwt_required()
def get_analysis_results(analysis_id):
    """Get analysis results"""
    try:
        current_user_id = get_jwt_identity()

        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        if analysis.status != AnalysisStatus.COMPLETED:
            return jsonify({'error': 'Analysis not completed yet'}), 400

        # Check cache first
        cache_key = f"analysis_results_{analysis_id}"
        cached_results = CacheService.get_from_cache(cache_key)

        if cached_results:
            return jsonify(cached_results), 200

        # Compile results
        results = {
            'analysis': analysis.to_dict(),
            'results': analysis.results,
            'summary': analysis.summary,
            'insights': analysis.insights,
            'recommendations': analysis.recommendations,
            'financial_data': [data.to_dict() for data in analysis.financial_data],
            'metrics': [metric.to_dict() for metric in analysis.metrics],
            'comparisons': [comp.to_dict() for comp in analysis.comparisons]
        }

        # Cache results
        CacheService.set_in_cache(cache_key, results, ttl=3600)  # 1 hour

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Get analysis results error: {str(e)}")
        return jsonify({'error': 'Failed to get analysis results'}), 500

@app.route('/api/analysis/<analysis_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_analysis(analysis_id):
    """Cancel an ongoing analysis"""
    try:
        current_user_id = get_jwt_identity()

        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        if analysis.status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED]:
            return jsonify({'error': 'Cannot cancel completed analysis'}), 400

        # Cancel analysis
        AnalysisService.cancel_analysis(analysis_id)

        db.session.commit()

        return jsonify({'message': 'Analysis cancelled successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Cancel analysis error: {str(e)}")
        return jsonify({'error': 'Failed to cancel analysis'}), 500

@app.route('/api/analysis/<analysis_id>/retry', methods=['POST'])
@jwt_required()
def retry_analysis(analysis_id):
    """Retry a failed analysis"""
    try:
        current_user_id = get_jwt_identity()

        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        if analysis.status != AnalysisStatus.FAILED:
            return jsonify({'error': 'Can only retry failed analyses'}), 400

        # Retry analysis
        task_id = AnalysisService.retry_analysis(analysis_id)

        db.session.commit()

        return jsonify({
            'message': 'Analysis retry started',
            'task_id': task_id
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Retry analysis error: {str(e)}")
        return jsonify({'error': 'Failed to retry analysis'}), 500

@app.route('/api/analysis/compare', methods=['POST'])
@jwt_required()
def compare_analyses():
    """Compare two analyses"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        required_fields = ['base_analysis_id', 'compared_analysis_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Verify user owns both analyses
        base_analysis = Analysis.query.filter_by(
            id=data['base_analysis_id'],
            user_id=current_user_id
        ).first()

        if not base_analysis:
            return jsonify({'error': 'Base analysis not found'}), 404

        # Create comparison
        comparison = ComparisonService.create_comparison(
            base_analysis_id=data['base_analysis_id'],
            compared_analysis_id=data['compared_analysis_id'],
            comparison_type=data.get('comparison_type', 'period_over_period'),
            title=data.get('title')
        )

        db.session.commit()

        return jsonify({
            'message': 'Comparison created successfully',
            'comparison': comparison.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Compare analyses error: {str(e)}")
        return jsonify({'error': 'Failed to create comparison'}), 500

@app.route('/api/analysis/templates', methods=['GET'])
@jwt_required()
def get_analysis_templates():
    """Get available analysis templates"""
    try:
        # Get query parameters
        analysis_type = request.args.get('type')
        industry = request.args.get('industry')
        complexity = request.args.get('complexity')

        templates = TemplateService.get_templates(
            analysis_type=analysis_type,
            industry=industry,
            complexity=complexity
        )

        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200

    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        return jsonify({'error': 'Failed to get templates'}), 500

@app.route('/api/analysis/templates/<template_id>/use', methods=['POST'])
@jwt_required()
def use_template(template_id):
    """Create analysis from template"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        template = AnalysisTemplate.query.get(template_id)
        if not template or not template.is_active:
            return jsonify({'error': 'Template not found'}), 404

        # Create analysis from template
        analysis = TemplateService.create_analysis_from_template(
            template_id=template_id,
            user_id=current_user_id,
            title=data.get('title'),
            parameters=data.get('parameters', {}),
            file_id=data.get('file_id')
        )

        # Start processing
        task_id = AnalysisService.start_processing(analysis.id)

        db.session.commit()

        return jsonify({
            'message': 'Analysis created from template',
            'analysis_id': analysis.id,
            'task_id': task_id,
            'analysis': analysis.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Use template error: {str(e)}")
        return jsonify({'error': 'Failed to create analysis from template'}), 500

@app.route('/api/analysis/metrics/summary', methods=['GET'])
@jwt_required()
def get_metrics_summary():
    """Get analysis metrics summary for user"""
    try:
        current_user_id = get_jwt_identity()

        # Get query parameters
        days = request.args.get('days', 30, type=int)

        summary = MetricsService.get_user_metrics_summary(current_user_id, days)

        return jsonify({'summary': summary}), 200

    except Exception as e:
        logger.error(f"Get metrics summary error: {str(e)}")
        return jsonify({'error': 'Failed to get metrics summary'}), 500

@app.route('/api/analysis/performance', methods=['GET'])
@jwt_required()
def get_performance_metrics():
    """Get system performance metrics"""
    try:
        # Get query parameters
        hours = request.args.get('hours', 24, type=int)
        component = request.args.get('component')

        metrics = MetricsService.get_performance_metrics(hours, component)

        return jsonify({'metrics': metrics}), 200

    except Exception as e:
        logger.error(f"Get performance metrics error: {str(e)}")
        return jsonify({'error': 'Failed to get performance metrics'}), 500

@app.route('/api/analysis/<analysis_id>/export', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def export_analysis(analysis_id):
    """Export analysis results"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        analysis = Analysis.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        if analysis.status != AnalysisStatus.COMPLETED:
            return jsonify({'error': 'Analysis not completed'}), 400

        export_format = data.get('format', 'pdf')
        include_charts = data.get('include_charts', True)
        include_raw_data = data.get('include_raw_data', False)

        # Request export from reporting service
        export_result = AnalysisService.export_analysis(
            analysis_id=analysis_id,
            export_format=export_format,
            include_charts=include_charts,
            include_raw_data=include_raw_data
        )

        return jsonify({
            'message': 'Export initiated successfully',
            'export_id': export_result['export_id'],
            'download_url': export_result.get('download_url'),
            'estimated_completion': export_result.get('estimated_completion')
        }), 200

    except Exception as e:
        logger.error(f"Export analysis error: {str(e)}")
        return jsonify({'error': 'Failed to export analysis'}), 500

@app.route('/api/analysis/batch', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def batch_analysis():
    """Create multiple analyses in batch"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'analyses' not in data:
            return jsonify({'error': 'Analysis list required'}), 400

        analyses_data = data['analyses']
        if len(analyses_data) > 10:  # Limit batch size
            return jsonify({'error': 'Maximum 10 analyses per batch'}), 400

        # Create analyses
        created_analyses = []
        task_ids = []

        for analysis_data in analyses_data:
            try:
                analysis_type = AnalysisType(analysis_data['analysis_type'])
                priority = Priority(analysis_data.get('priority', 'normal'))

                analysis = AnalysisService.create_analysis(
                    user_id=current_user_id,
                    analysis_type=analysis_type,
                    title=analysis_data['title'],
                    description=analysis_data.get('description'),
                    file_id=analysis_data.get('file_id'),
                    parameters=analysis_data.get('parameters', {}),
                    priority=priority
                )

                task_id = AnalysisService.start_processing(analysis.id)

                created_analyses.append(analysis.to_dict())
                task_ids.append(task_id)

            except Exception as e:
                logger.error(f"Failed to create analysis in batch: {str(e)}")
                continue

        db.session.commit()

        return jsonify({
            'message': f'{len(created_analyses)} analyses created successfully',
            'analyses': created_analyses,
            'task_ids': task_ids
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Batch analysis error: {str(e)}")
        return jsonify({'error': 'Failed to create batch analyses'}), 500