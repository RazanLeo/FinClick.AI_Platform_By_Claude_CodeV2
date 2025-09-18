from flask import request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import app, db, limiter
from models import (
    FileRecord, OCRResult, FileAnalysisRequest, FileShare,
    FileActivity, FileStatus, FileType, OCRStatus
)
from services import (
    FileStorageService, OCRService, FileValidationService,
    FileAnalysisService, FileShareService
)
import logging
import os

logger = logging.getLogger(__name__)

@app.route('/api/files/upload', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def upload_file():
    """Upload a file"""
    try:
        current_user_id = get_jwt_identity()

        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get optional parameters
        perform_ocr = request.form.get('perform_ocr', 'true').lower() == 'true'
        auto_analyze = request.form.get('auto_analyze', 'false').lower() == 'true'
        analysis_type = request.form.get('analysis_type', 'financial_statement')

        # Validate file
        validation_result = FileValidationService.validate_file(file)
        if not validation_result['is_valid']:
            return jsonify({
                'error': 'File validation failed',
                'validation_errors': validation_result['errors']
            }), 400

        # Check user limits
        usage_check = FileStorageService.check_user_limits(current_user_id, file)
        if not usage_check['allowed']:
            return jsonify({
                'error': 'Upload limit exceeded',
                'message': usage_check['message']
            }), 403

        # Store file
        file_record = FileStorageService.store_file(file, current_user_id)

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            current_user_id,
            'upload',
            f'File uploaded: {file_record.original_filename}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        # Start OCR if requested and supported
        ocr_task_id = None
        if perform_ocr and file_record.is_supported_for_ocr():
            ocr_task_id = OCRService.start_ocr_processing(file_record.id)

        # Start analysis if requested and supported
        analysis_task_id = None
        if auto_analyze and file_record.is_supported_for_analysis():
            analysis_task_id = FileAnalysisService.request_analysis(
                file_record.id,
                current_user_id,
                analysis_type
            )

        db.session.commit()

        response_data = {
            'message': 'File uploaded successfully',
            'file': file_record.to_dict()
        }

        if ocr_task_id:
            response_data['ocr_task_id'] = ocr_task_id

        if analysis_task_id:
            response_data['analysis_task_id'] = analysis_task_id

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'File upload failed'}), 500

@app.route('/api/files', methods=['GET'])
@jwt_required()
def get_files():
    """Get user's files with pagination"""
    try:
        current_user_id = get_jwt_identity()

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        file_type = request.args.get('type')
        status = request.args.get('status')
        search = request.args.get('search')

        # Build query
        query = FileRecord.query.filter_by(user_id=current_user_id)

        if file_type:
            try:
                file_type_enum = FileType(file_type)
                query = query.filter_by(file_type=file_type_enum)
            except ValueError:
                pass

        if status:
            try:
                status_enum = FileStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                pass

        if search:
            query = query.filter(
                FileRecord.original_filename.ilike(f'%{search}%')
            )

        # Exclude deleted files
        query = query.filter(FileRecord.deleted_at.is_(None))

        # Paginate
        files = query.order_by(FileRecord.uploaded_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'files': [file.to_dict() for file in files.items],
            'total': files.total,
            'pages': files.pages,
            'current_page': files.page,
            'per_page': files.per_page,
            'has_next': files.has_next,
            'has_prev': files.has_prev
        }), 200

    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        return jsonify({'error': 'Failed to get files'}), 500

@app.route('/api/files/<file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """Get specific file details"""
    try:
        current_user_id = get_jwt_identity()

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record or file_record.deleted_at:
            return jsonify({'error': 'File not found'}), 404

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            current_user_id,
            'view',
            f'File details viewed: {file_record.original_filename}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'file': file_record.to_dict(),
            'ocr_results': [ocr.to_dict() for ocr in file_record.ocr_results],
            'analysis_requests': [req.to_dict() for req in file_record.analysis_requests]
        }), 200

    except Exception as e:
        logger.error(f"Get file error: {str(e)}")
        return jsonify({'error': 'Failed to get file'}), 500

@app.route('/api/files/<file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Download a file"""
    try:
        current_user_id = get_jwt_identity()

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record or file_record.deleted_at:
            return jsonify({'error': 'File not found'}), 404

        # Get file path
        file_path = FileStorageService.get_file_path(file_record)

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not available'}), 404

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            current_user_id,
            'download',
            f'File downloaded: {file_record.original_filename}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_record.original_filename
        ), 200

    except Exception as e:
        logger.error(f"Download file error: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/api/files/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete a file (soft delete)"""
    try:
        current_user_id = get_jwt_identity()

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record or file_record.deleted_at:
            return jsonify({'error': 'File not found'}), 404

        # Soft delete
        file_record.deleted_at = db.func.now()
        file_record.status = FileStatus.DELETED

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            current_user_id,
            'delete',
            f'File deleted: {file_record.original_filename}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({'message': 'File deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete file error: {str(e)}")
        return jsonify({'error': 'Failed to delete file'}), 500

@app.route('/api/files/<file_id>/ocr', methods=['POST'])
@jwt_required()
def start_ocr(file_id):
    """Start OCR processing for a file"""
    try:
        current_user_id = get_jwt_identity()

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record or file_record.deleted_at:
            return jsonify({'error': 'File not found'}), 404

        if not file_record.is_supported_for_ocr():
            return jsonify({'error': 'File type not supported for OCR'}), 400

        # Get OCR provider preference
        ocr_provider = request.json.get('provider', 'tesseract') if request.json else 'tesseract'

        # Start OCR processing
        task_id = OCRService.start_ocr_processing(file_record.id, ocr_provider)

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            current_user_id,
            'ocr_started',
            f'OCR processing started for: {file_record.original_filename}',
            metadata={'provider': ocr_provider},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({
            'message': 'OCR processing started',
            'task_id': task_id
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Start OCR error: {str(e)}")
        return jsonify({'error': 'Failed to start OCR processing'}), 500

@app.route('/api/files/<file_id>/ocr', methods=['GET'])
@jwt_required()
def get_ocr_results(file_id):
    """Get OCR results for a file"""
    try:
        current_user_id = get_jwt_identity()

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record or file_record.deleted_at:
            return jsonify({'error': 'File not found'}), 404

        ocr_results = OCRResult.query.filter_by(file_record_id=file_id).all()

        return jsonify({
            'ocr_results': [result.to_dict() for result in ocr_results]
        }), 200

    except Exception as e:
        logger.error(f"Get OCR results error: {str(e)}")
        return jsonify({'error': 'Failed to get OCR results'}), 500

@app.route('/api/files/<file_id>/analyze', methods=['POST'])
@jwt_required()
def request_analysis(file_id):
    """Request analysis for a file"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'analysis_type' not in data:
            return jsonify({'error': 'Analysis type required'}), 400

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record or file_record.deleted_at:
            return jsonify({'error': 'File not found'}), 404

        if not file_record.is_supported_for_analysis():
            return jsonify({'error': 'File type not supported for analysis'}), 400

        # Request analysis
        analysis_request = FileAnalysisService.request_analysis(
            file_id,
            current_user_id,
            data['analysis_type'],
            data.get('parameters', {})
        )

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            current_user_id,
            'analysis_requested',
            f'Analysis requested for: {file_record.original_filename}',
            metadata={'analysis_type': data['analysis_type']},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({
            'message': 'Analysis requested successfully',
            'analysis_request': analysis_request.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Request analysis error: {str(e)}")
        return jsonify({'error': 'Failed to request analysis'}), 500

@app.route('/api/files/<file_id>/share', methods=['POST'])
@jwt_required()
def share_file(file_id):
    """Create a file share"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record or file_record.deleted_at:
            return jsonify({'error': 'File not found'}), 404

        # Create file share
        file_share = FileShareService.create_share(
            file_record.id,
            current_user_id,
            permissions=data.get('permissions', ['read']),
            expires_in_hours=data.get('expires_in_hours'),
            max_downloads=data.get('max_downloads'),
            is_public=data.get('is_public', False),
            shared_with_user_id=data.get('shared_with_user_id')
        )

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            current_user_id,
            'shared',
            f'File shared: {file_record.original_filename}',
            metadata={'share_id': file_share.id},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        return jsonify({
            'message': 'File shared successfully',
            'share': file_share.to_dict(),
            'share_url': f"{request.host_url}api/files/shared/{file_share.share_token}"
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Share file error: {str(e)}")
        return jsonify({'error': 'Failed to share file'}), 500

@app.route('/api/files/shared/<share_token>', methods=['GET'])
def get_shared_file(share_token):
    """Access a shared file"""
    try:
        file_share = FileShare.query.filter_by(share_token=share_token).first()

        if not file_share:
            return jsonify({'error': 'Share not found'}), 404

        if file_share.is_expired():
            return jsonify({'error': 'Share has expired'}), 410

        file_record = file_share.file_record

        if file_record.deleted_at:
            return jsonify({'error': 'File not available'}), 404

        # Update access tracking
        file_share.last_accessed_at = db.func.now()
        if 'download' in request.args:
            file_share.download_count += 1

        # Log activity
        FileStorageService.log_file_activity(
            file_record.id,
            file_share.shared_with_user_id or 'anonymous',
            'shared_access',
            f'Shared file accessed: {file_record.original_filename}',
            metadata={'share_token': share_token},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.commit()

        if 'download' in request.args and 'download' in file_share.permissions:
            file_path = FileStorageService.get_file_path(file_record)
            return send_file(
                file_path,
                as_attachment=True,
                download_name=file_record.original_filename
            )
        else:
            return jsonify({
                'file': {
                    'id': file_record.id,
                    'original_filename': file_record.original_filename,
                    'file_size': file_record.file_size,
                    'file_type': file_record.file_type.value,
                    'uploaded_at': file_record.uploaded_at.isoformat()
                },
                'permissions': file_share.permissions
            }), 200

    except Exception as e:
        logger.error(f"Get shared file error: {str(e)}")
        return jsonify({'error': 'Failed to access shared file'}), 500

@app.route('/api/files/<file_id>/activity', methods=['GET'])
@jwt_required()
def get_file_activity(file_id):
    """Get file activity log"""
    try:
        current_user_id = get_jwt_identity()

        file_record = FileRecord.query.filter_by(
            id=file_id,
            user_id=current_user_id
        ).first()

        if not file_record:
            return jsonify({'error': 'File not found'}), 404

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        activities = FileActivity.query.filter_by(
            file_record_id=file_id
        ).order_by(FileActivity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'activities': [activity.to_dict() for activity in activities.items],
            'total': activities.total,
            'pages': activities.pages,
            'current_page': activities.page,
            'per_page': activities.per_page,
            'has_next': activities.has_next,
            'has_prev': activities.has_prev
        }), 200

    except Exception as e:
        logger.error(f"Get file activity error: {str(e)}")
        return jsonify({'error': 'Failed to get file activity'}), 500

@app.route('/api/files/stats', methods=['GET'])
@jwt_required()
def get_file_stats():
    """Get file statistics for user"""
    try:
        current_user_id = get_jwt_identity()

        stats = FileStorageService.get_user_file_stats(current_user_id)

        return jsonify({'stats': stats}), 200

    except Exception as e:
        logger.error(f"Get file stats error: {str(e)}")
        return jsonify({'error': 'Failed to get file statistics'}), 500