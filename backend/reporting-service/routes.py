from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app, db, limiter
from models import Report, ReportTemplate, ReportType, ReportStatus
from services import ReportService
import logging

logger = logging.getLogger(__name__)

@app.route('/api/reports/generate', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def generate_report():
    """Generate a new report"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        report = ReportService.generate_report(
            user_id=current_user_id,
            title=data['title'],
            report_type=ReportType(data['report_type']),
            parameters=data.get('parameters', {}),
            template_id=data.get('template_id')
        )

        db.session.commit()
        return jsonify({'message': 'Report generation started', 'report': report.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Generate report error: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500

@app.route('/api/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get user's reports"""
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        reports = Report.query.filter_by(user_id=current_user_id)\
                             .order_by(Report.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'reports': [report.to_dict() for report in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'current_page': reports.page
        }), 200

    except Exception as e:
        logger.error(f"Get reports error: {str(e)}")
        return jsonify({'error': 'Failed to get reports'}), 500

@app.route('/api/reports/<report_id>/download', methods=['GET'])
@jwt_required()
def download_report(report_id):
    """Download a report"""
    try:
        current_user_id = get_jwt_identity()

        report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404

        if report.status != ReportStatus.COMPLETED:
            return jsonify({'error': 'Report not ready for download'}), 400

        download_info = ReportService.get_download_info(report_id)
        return jsonify(download_info), 200

    except Exception as e:
        logger.error(f"Download report error: {str(e)}")
        return jsonify({'error': 'Failed to download report'}), 500

@app.route('/api/reports/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """Get available report templates"""
    try:
        templates = ReportTemplate.query.filter_by(is_active=True).all()
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200

    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        return jsonify({'error': 'Failed to get templates'}), 500