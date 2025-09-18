import os
import hashlib
import uuid
import shutil
import tempfile
import requests
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import boto3
from google.cloud import vision
from app import db, current_app
from models import (
    FileRecord, OCRResult, FileAnalysisRequest, FileShare,
    FileActivity, FileType, FileStatus, OCRStatus
)
import logging
import mimetypes

logger = logging.getLogger(__name__)

class FileStorageService:
    """File storage and management service"""

    @staticmethod
    def store_file(file, user_id):
        """Store uploaded file"""
        try:
            # Generate secure filename
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.split('.')[-1].lower()
            stored_filename = f"{uuid.uuid4()}.{file_extension}"

            # Determine file type
            file_type = FileRecord().get_file_type_from_extension(original_filename)

            # Get file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            # Calculate file hash
            file_hash = FileStorageService.calculate_file_hash(file)
            file.seek(0)

            # Check for duplicate files
            existing_file = FileRecord.query.filter_by(
                user_id=user_id,
                file_hash=file_hash,
                deleted_at=None
            ).first()

            if existing_file:
                raise ValueError(f"Duplicate file detected: {original_filename}")

            # Determine storage path
            upload_folder = current_app.config['UPLOAD_FOLDER']
            user_folder = os.path.join(upload_folder, user_id)
            os.makedirs(user_folder, exist_ok=True)

            file_path = os.path.join(user_folder, stored_filename)

            # Save file
            file.save(file_path)

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(original_filename)
            if not mime_type:
                mime_type = 'application/octet-stream'

            # Create file record
            file_record = FileRecord(
                user_id=user_id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                mime_type=mime_type,
                file_hash=file_hash,
                status=FileStatus.UPLOADED,
                storage_provider='local'
            )

            # Add metadata
            metadata = {
                'upload_ip': '127.0.0.1',  # Will be set in route
                'file_extension': file_extension
            }

            if file_type == FileType.IMAGE:
                try:
                    with Image.open(file_path) as img:
                        metadata['image_dimensions'] = f"{img.width}x{img.height}"
                        metadata['image_format'] = img.format
                except Exception as e:
                    logger.warning(f"Could not extract image metadata: {str(e)}")

            file_record.metadata = metadata

            db.session.add(file_record)
            db.session.flush()

            # Upload to cloud storage if configured
            if current_app.config.get('AWS_S3_BUCKET'):
                try:
                    cloud_url = FileStorageService.upload_to_s3(file_path, file_record)
                    file_record.public_url = cloud_url
                    file_record.storage_provider = 's3'
                except Exception as e:
                    logger.error(f"Failed to upload to S3: {str(e)}")

            return file_record

        except Exception as e:
            logger.error(f"File storage error: {str(e)}")
            raise

    @staticmethod
    def calculate_file_hash(file):
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        chunk_size = 8192

        while chunk := file.read(chunk_size):
            hash_sha256.update(chunk)

        return hash_sha256.hexdigest()

    @staticmethod
    def upload_to_s3(file_path, file_record):
        """Upload file to Amazon S3"""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                region_name=current_app.config['AWS_S3_REGION']
            )

            bucket_name = current_app.config['AWS_S3_BUCKET']
            s3_key = f"files/{file_record.user_id}/{file_record.stored_filename}"

            s3_client.upload_file(
                file_path,
                bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file_record.mime_type,
                    'Metadata': {
                        'original_filename': file_record.original_filename,
                        'user_id': file_record.user_id,
                        'file_id': file_record.id
                    }
                }
            )

            # Generate public URL
            public_url = f"https://{bucket_name}.s3.{current_app.config['AWS_S3_REGION']}.amazonaws.com/{s3_key}"

            return public_url

        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise

    @staticmethod
    def get_file_path(file_record):
        """Get file path based on storage provider"""
        if file_record.storage_provider == 'local':
            return file_record.file_path
        elif file_record.storage_provider == 's3':
            # For S3, download to temp file if needed
            return FileStorageService.download_from_s3(file_record)
        else:
            raise ValueError(f"Unsupported storage provider: {file_record.storage_provider}")

    @staticmethod
    def download_from_s3(file_record):
        """Download file from S3 to temporary location"""
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                region_name=current_app.config['AWS_S3_REGION']
            )

            bucket_name = current_app.config['AWS_S3_BUCKET']
            s3_key = f"files/{file_record.user_id}/{file_record.stored_filename}"

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=f".{file_record.stored_filename.split('.')[-1]}",
                delete=False
            )

            s3_client.download_file(bucket_name, s3_key, temp_file.name)

            return temp_file.name

        except Exception as e:
            logger.error(f"S3 download error: {str(e)}")
            raise

    @staticmethod
    def check_user_limits(user_id, file):
        """Check if user can upload file based on limits"""
        try:
            # Get user subscription info from user service
            user_service_url = current_app.config.get('USER_SERVICE_URL')
            if user_service_url:
                response = requests.get(f"{user_service_url}/api/users/subscription")
                if response.status_code == 200:
                    subscription = response.json().get('subscription')
                    if subscription:
                        # Check file count limit
                        current_files = FileRecord.query.filter_by(
                            user_id=user_id,
                            deleted_at=None
                        ).count()

                        if current_files >= subscription['monthly_file_limit']:
                            return {
                                'allowed': False,
                                'message': 'Monthly file upload limit exceeded'
                            }

                        # Check storage limit
                        file.seek(0, os.SEEK_END)
                        file_size_gb = file.tell() / (1024 * 1024 * 1024)
                        file.seek(0)

                        if subscription['storage_used_gb'] + file_size_gb > subscription['storage_limit_gb']:
                            return {
                                'allowed': False,
                                'message': 'Storage limit exceeded'
                            }

            return {'allowed': True}

        except Exception as e:
            logger.error(f"User limits check error: {str(e)}")
            # Allow upload if we can't check limits
            return {'allowed': True}

    @staticmethod
    def log_file_activity(file_record_id, user_id, activity_type, description, metadata=None, ip_address=None, user_agent=None):
        """Log file activity"""
        activity = FileActivity(
            file_record_id=file_record_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(activity)
        return activity

    @staticmethod
    def get_user_file_stats(user_id):
        """Get file statistics for user"""
        try:
            # Basic counts
            total_files = FileRecord.query.filter_by(
                user_id=user_id,
                deleted_at=None
            ).count()

            # File types distribution
            file_types = db.session.query(
                FileRecord.file_type,
                db.func.count(FileRecord.id)
            ).filter_by(
                user_id=user_id,
                deleted_at=None
            ).group_by(FileRecord.file_type).all()

            # Storage usage
            storage_usage = db.session.query(
                db.func.sum(FileRecord.file_size)
            ).filter_by(
                user_id=user_id,
                deleted_at=None
            ).scalar() or 0

            # Recent activity
            recent_uploads = FileRecord.query.filter(
                FileRecord.user_id == user_id,
                FileRecord.uploaded_at >= datetime.utcnow() - timedelta(days=7),
                FileRecord.deleted_at.is_(None)
            ).count()

            stats = {
                'total_files': total_files,
                'storage_usage_bytes': storage_usage,
                'storage_usage_gb': round(storage_usage / (1024 * 1024 * 1024), 2),
                'recent_uploads': recent_uploads,
                'file_types': {file_type.value: count for file_type, count in file_types}
            }

            return stats

        except Exception as e:
            logger.error(f"Get file stats error: {str(e)}")
            return {}

class FileValidationService:
    """File validation service"""

    ALLOWED_EXTENSIONS = {
        'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
        'xlsx', 'xls', 'csv', 'doc', 'docx', 'ppt', 'pptx', 'txt'
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def validate_file(file):
        """Validate uploaded file"""
        errors = []

        # Check filename
        if not file.filename:
            errors.append("No filename provided")
            return {'is_valid': False, 'errors': errors}

        # Check extension
        extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if extension not in FileValidationService.ALLOWED_EXTENSIONS:
            errors.append(f"File type '.{extension}' not supported")

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > FileValidationService.MAX_FILE_SIZE:
            errors.append(f"File size ({file_size} bytes) exceeds maximum allowed size")

        if file_size == 0:
            errors.append("File is empty")

        # Additional validation based on file type
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            validation_errors = FileValidationService.validate_image(file)
            errors.extend(validation_errors)

        elif extension == 'pdf':
            validation_errors = FileValidationService.validate_pdf(file)
            errors.extend(validation_errors)

        file.seek(0)  # Reset file pointer

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def validate_image(file):
        """Validate image file"""
        errors = []
        try:
            with Image.open(file) as img:
                # Check image dimensions
                if img.width > 10000 or img.height > 10000:
                    errors.append("Image dimensions too large")

                if img.width < 10 or img.height < 10:
                    errors.append("Image dimensions too small")

        except Exception as e:
            errors.append(f"Invalid image file: {str(e)}")

        return errors

    @staticmethod
    def validate_pdf(file):
        """Validate PDF file"""
        errors = []
        try:
            # Basic PDF header check
            file.seek(0)
            header = file.read(4)
            if header != b'%PDF':
                errors.append("Invalid PDF file")

        except Exception as e:
            errors.append(f"PDF validation error: {str(e)}")

        return errors

class OCRService:
    """OCR processing service"""

    @staticmethod
    def start_ocr_processing(file_record_id, provider='tesseract'):
        """Start OCR processing for a file"""
        try:
            file_record = FileRecord.query.get(file_record_id)
            if not file_record:
                raise ValueError("File not found")

            # Create OCR result record
            ocr_result = OCRResult(
                file_record_id=file_record_id,
                ocr_provider=provider,
                status=OCRStatus.PROCESSING
            )
            db.session.add(ocr_result)
            db.session.flush()

            # Update file status
            file_record.status = FileStatus.PROCESSING
            file_record.processing_started_at = datetime.utcnow()

            # Process based on provider
            if provider == 'tesseract':
                result = OCRService.process_with_tesseract(file_record)
            elif provider == 'google_vision':
                result = OCRService.process_with_google_vision(file_record)
            elif provider == 'aws_textract':
                result = OCRService.process_with_aws_textract(file_record)
            else:
                raise ValueError(f"Unsupported OCR provider: {provider}")

            # Update OCR result
            ocr_result.extracted_text = result.get('text', '')
            ocr_result.confidence_score = result.get('confidence')
            ocr_result.structured_data = result.get('structured_data')
            ocr_result.entities = result.get('entities')
            ocr_result.status = OCRStatus.COMPLETED
            ocr_result.completed_at = datetime.utcnow()

            # Update file status
            file_record.status = FileStatus.PROCESSED
            file_record.processing_completed_at = datetime.utcnow()

            return ocr_result.id

        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            # Update OCR result with error
            if 'ocr_result' in locals():
                ocr_result.status = OCRStatus.FAILED
                ocr_result.error_message = str(e)
                ocr_result.completed_at = datetime.utcnow()

            if 'file_record' in locals():
                file_record.status = FileStatus.ERROR

            raise

    @staticmethod
    def process_with_tesseract(file_record):
        """Process file with Tesseract OCR"""
        try:
            file_path = FileStorageService.get_file_path(file_record)

            if file_record.file_type == FileType.PDF:
                # For PDF, convert to images first
                extracted_text = OCRService.extract_text_from_pdf(file_path)
            else:
                # For images, use directly
                extracted_text = pytesseract.image_to_string(Image.open(file_path))

            return {
                'text': extracted_text,
                'confidence': None  # Tesseract doesn't provide confidence scores easily
            }

        except Exception as e:
            logger.error(f"Tesseract OCR error: {str(e)}")
            raise

    @staticmethod
    def process_with_google_vision(file_record):
        """Process file with Google Vision API"""
        try:
            if not current_app.config.get('GOOGLE_VISION_API_KEY'):
                raise ValueError("Google Vision API key not configured")

            client = vision.ImageAnnotatorClient()
            file_path = FileStorageService.get_file_path(file_record)

            with open(file_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations

            if texts:
                extracted_text = texts[0].description
                confidence = texts[0].confidence if hasattr(texts[0], 'confidence') else None
            else:
                extracted_text = ""
                confidence = None

            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")

            return {
                'text': extracted_text,
                'confidence': confidence
            }

        except Exception as e:
            logger.error(f"Google Vision OCR error: {str(e)}")
            raise

    @staticmethod
    def process_with_aws_textract(file_record):
        """Process file with AWS Textract"""
        try:
            textract_client = boto3.client(
                'textract',
                region_name=current_app.config.get('AWS_TEXTRACT_REGION', 'us-east-1')
            )

            file_path = FileStorageService.get_file_path(file_record)

            with open(file_path, 'rb') as document:
                response = textract_client.detect_document_text(
                    Document={'Bytes': document.read()}
                )

            # Extract text from response
            extracted_text = ""
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    extracted_text += block['Text'] + '\n'

            # Extract structured data
            structured_data = {
                'blocks': response['Blocks']
            }

            return {
                'text': extracted_text,
                'confidence': None,  # Could calculate average confidence from blocks
                'structured_data': structured_data
            }

        except Exception as e:
            logger.error(f"AWS Textract OCR error: {str(e)}")
            raise

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """Extract text from PDF using OCR"""
        try:
            import pdf2image

            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)

            extracted_text = ""
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                extracted_text += f"Page {i+1}:\n{text}\n\n"

            return extracted_text

        except Exception as e:
            logger.error(f"PDF OCR error: {str(e)}")
            raise

class FileAnalysisService:
    """File analysis service"""

    @staticmethod
    def request_analysis(file_record_id, user_id, analysis_type, parameters=None):
        """Request analysis for a file"""
        try:
            # Create analysis request
            analysis_request = FileAnalysisRequest(
                file_record_id=file_record_id,
                user_id=user_id,
                analysis_type=analysis_type,
                parameters=parameters or {},
                status='pending'
            )
            db.session.add(analysis_request)
            db.session.flush()

            # Send request to analysis service
            analysis_service_url = current_app.config.get('ANALYSIS_SERVICE_URL')
            if analysis_service_url:
                payload = {
                    'file_id': file_record_id,
                    'user_id': user_id,
                    'analysis_type': analysis_type,
                    'parameters': parameters
                }

                response = requests.post(
                    f"{analysis_service_url}/api/analysis/request",
                    json=payload
                )

                if response.status_code == 201:
                    result = response.json()
                    analysis_request.analysis_id = result.get('analysis_id')
                    analysis_request.status = 'submitted'

            return analysis_request

        except Exception as e:
            logger.error(f"Analysis request error: {str(e)}")
            raise

class FileShareService:
    """File sharing service"""

    @staticmethod
    def create_share(file_record_id, owner_user_id, permissions, expires_in_hours=None, max_downloads=None, is_public=False, shared_with_user_id=None):
        """Create a file share"""
        try:
            # Generate share token
            share_token = str(uuid.uuid4())

            # Calculate expiration
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

            # Create share
            file_share = FileShare(
                file_record_id=file_record_id,
                owner_user_id=owner_user_id,
                shared_with_user_id=shared_with_user_id,
                share_token=share_token,
                permissions=permissions,
                is_public=is_public,
                expires_at=expires_at,
                max_downloads=max_downloads
            )

            db.session.add(file_share)

            return file_share

        except Exception as e:
            logger.error(f"Create share error: {str(e)}")
            raise