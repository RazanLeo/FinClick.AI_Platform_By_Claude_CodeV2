"""
AWS S3 Storage Service
Handles file storage and management for FinClick.AI platform
"""

import boto3
import asyncio
import logging
import json
import time
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, BinaryIO
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import io
from botocore.exceptions import ClientError, BotoCoreError
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

class StorageClass(Enum):
    STANDARD = "STANDARD"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"
    GLACIER = "GLACIER"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    GLACIER_IR = "GLACIER_IR"

class ServerSideEncryption(Enum):
    AES256 = "AES256"
    AWS_KMS = "aws:kms"

class ACL(Enum):
    PRIVATE = "private"
    PUBLIC_READ = "public-read"
    PUBLIC_READ_WRITE = "public-read-write"
    AUTHENTICATED_READ = "authenticated-read"

@dataclass
class S3UploadResult:
    success: bool
    key: Optional[str] = None
    url: Optional[str] = None
    etag: Optional[str] = None
    version_id: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class S3Object:
    key: str
    size: int
    last_modified: datetime
    etag: str
    storage_class: str
    url: Optional[str] = None

@dataclass
class S3PresignedUrl:
    url: str
    expires_at: datetime
    fields: Optional[Dict] = None  # For POST uploads

def retry_on_aws_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry AWS API calls on specific errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ClientError, BotoCoreError) as e:
                    last_exception = e
                    error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', 'Unknown')

                    # Retry on throttling and temporary errors
                    if error_code in ['Throttling', 'ServiceUnavailable', 'SlowDown', 'RequestTimeout']:
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)
                            logger.warning(f"AWS S3 error ({error_code}), retrying in {wait_time}s")
                            await asyncio.sleep(wait_time)
                        continue

                    # Don't retry on other errors
                    raise e
                except Exception as e:
                    # Don't retry on non-AWS exceptions
                    raise e

            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

class AWSS3Service:
    """Comprehensive AWS S3 storage service for FinClick.AI"""

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket_name: str,
        region_name: str = 'us-east-1',
        cloudfront_domain: str = None,
        default_storage_class: StorageClass = StorageClass.STANDARD,
        default_encryption: ServerSideEncryption = ServerSideEncryption.AES256
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.cloudfront_domain = cloudfront_domain
        self.default_storage_class = default_storage_class
        self.default_encryption = default_encryption

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        # Initialize S3 resource for high-level operations
        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        self.bucket = self.s3_resource.Bucket(bucket_name)

        # Rate limiting
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0

        logger.info(f"AWS S3 service initialized for bucket: {bucket_name}")

    async def _rate_limit_check(self):
        """Ensure we don't exceed AWS S3 rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename"""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'

    def _generate_key(self, filename: str, prefix: str = None, user_id: str = None) -> str:
        """Generate S3 key with proper structure"""
        parts = []

        if prefix:
            parts.append(prefix.strip('/'))

        if user_id:
            parts.append(f"users/{user_id}")

        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y/%m/%d')
        parts.append(timestamp)

        # Add filename
        parts.append(filename)

        return '/'.join(parts)

    def _get_public_url(self, key: str) -> str:
        """Get public URL for S3 object"""
        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{key}"
        else:
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{key}"

    @retry_on_aws_error()
    async def upload_file(
        self,
        file_content: BinaryIO,
        filename: str,
        prefix: str = None,
        user_id: str = None,
        content_type: str = None,
        storage_class: StorageClass = None,
        encryption: ServerSideEncryption = None,
        acl: ACL = ACL.PRIVATE,
        metadata: Dict[str, str] = None,
        tags: Dict[str, str] = None
    ) -> S3UploadResult:
        """Upload file to S3"""
        await self._rate_limit_check()

        try:
            # Generate key
            key = self._generate_key(filename, prefix, user_id)

            # Determine content type
            if not content_type:
                content_type = self._get_content_type(filename)

            # Prepare upload parameters
            upload_params = {
                'Key': key,
                'Body': file_content,
                'ContentType': content_type,
                'StorageClass': (storage_class or self.default_storage_class).value,
                'ServerSideEncryption': (encryption or self.default_encryption).value,
                'ACL': acl.value
            }

            # Add metadata
            if metadata:
                upload_params['Metadata'] = metadata

            # Add tags
            if tags:
                tag_string = '&'.join([f"{k}={v}" for k, v in tags.items()])
                upload_params['Tagging'] = tag_string

            # Upload file
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                **upload_params
            )

            # Get public URL if ACL allows
            url = None
            if acl in [ACL.PUBLIC_READ, ACL.PUBLIC_READ_WRITE]:
                url = self._get_public_url(key)

            logger.info(f"File uploaded successfully: {key}")
            return S3UploadResult(
                success=True,
                key=key,
                url=url,
                etag=response.get('ETag'),
                version_id=response.get('VersionId')
            )

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS S3 upload error {error_code}: {error_message}")

            return S3UploadResult(
                success=False,
                error_message=f"{error_code}: {error_message}"
            )

        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            return S3UploadResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_aws_error()
    async def upload_file_from_path(
        self,
        file_path: str,
        s3_key: str = None,
        prefix: str = None,
        user_id: str = None,
        **kwargs
    ) -> S3UploadResult:
        """Upload file from local path"""
        try:
            filename = file_path.split('/')[-1]

            with open(file_path, 'rb') as file:
                return await self.upload_file(
                    file_content=file,
                    filename=filename,
                    prefix=prefix,
                    user_id=user_id,
                    **kwargs
                )

        except FileNotFoundError:
            return S3UploadResult(
                success=False,
                error_message=f"File not found: {file_path}"
            )
        except Exception as e:
            logger.error(f"Failed to upload file from path: {str(e)}")
            return S3UploadResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_aws_error()
    async def download_file(self, key: str, download_path: str = None) -> bytes:
        """Download file from S3"""
        await self._rate_limit_check()

        try:
            if download_path:
                # Download to file
                self.s3_client.download_file(self.bucket_name, key, download_path)
                logger.info(f"File downloaded to: {download_path}")
                return None
            else:
                # Download to memory
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
                content = response['Body'].read()
                logger.info(f"File downloaded from S3: {key}")
                return content

        except ClientError as e:
            logger.error(f"Failed to download file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to download file: {str(e)}")
            raise

    @retry_on_aws_error()
    async def delete_file(self, key: str) -> bool:
        """Delete file from S3"""
        await self._rate_limit_check()

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"File deleted from S3: {key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False

    @retry_on_aws_error()
    async def delete_files(self, keys: List[str]) -> Dict[str, bool]:
        """Delete multiple files from S3"""
        await self._rate_limit_check()

        try:
            # Prepare delete request
            delete_objects = {
                'Objects': [{'Key': key} for key in keys]
            }

            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete=delete_objects
            )

            # Process results
            results = {}
            deleted = response.get('Deleted', [])
            errors = response.get('Errors', [])

            for item in deleted:
                results[item['Key']] = True

            for error in errors:
                results[error['Key']] = False
                logger.error(f"Failed to delete {error['Key']}: {error['Message']}")

            logger.info(f"Bulk delete completed: {len(deleted)} deleted, {len(errors)} errors")
            return results

        except ClientError as e:
            logger.error(f"Failed to delete files: {str(e)}")
            return {key: False for key in keys}

    @retry_on_aws_error()
    async def list_files(
        self,
        prefix: str = None,
        limit: int = 1000,
        continuation_token: str = None
    ) -> Dict[str, Any]:
        """List files in S3 bucket"""
        await self._rate_limit_check()

        try:
            params = {
                'Bucket': self.bucket_name,
                'MaxKeys': limit
            }

            if prefix:
                params['Prefix'] = prefix

            if continuation_token:
                params['ContinuationToken'] = continuation_token

            response = self.s3_client.list_objects_v2(**params)

            objects = []
            for obj in response.get('Contents', []):
                s3_object = S3Object(
                    key=obj['Key'],
                    size=obj['Size'],
                    last_modified=obj['LastModified'],
                    etag=obj['ETag'],
                    storage_class=obj.get('StorageClass', 'STANDARD'),
                    url=self._get_public_url(obj['Key'])
                )
                objects.append(s3_object)

            logger.info(f"Listed {len(objects)} files from S3")
            return {
                'objects': objects,
                'is_truncated': response.get('IsTruncated', False),
                'next_continuation_token': response.get('NextContinuationToken'),
                'count': len(objects)
            }

        except ClientError as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise

    @retry_on_aws_error()
    async def get_file_info(self, key: str) -> Dict[str, Any]:
        """Get file metadata and information"""
        await self._rate_limit_check()

        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)

            file_info = {
                'key': key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'etag': response['ETag'],
                'content_type': response.get('ContentType'),
                'storage_class': response.get('StorageClass', 'STANDARD'),
                'metadata': response.get('Metadata', {}),
                'url': self._get_public_url(key)
            }

            logger.info(f"Retrieved file info: {key}")
            return file_info

        except ClientError as e:
            logger.error(f"Failed to get file info: {str(e)}")
            raise

    @retry_on_aws_error()
    async def copy_file(
        self,
        source_key: str,
        destination_key: str,
        source_bucket: str = None,
        metadata: Dict[str, str] = None,
        storage_class: StorageClass = None
    ) -> bool:
        """Copy file within S3 or between buckets"""
        await self._rate_limit_check()

        try:
            copy_source = {
                'Bucket': source_bucket or self.bucket_name,
                'Key': source_key
            }

            copy_params = {
                'CopySource': copy_source,
                'Bucket': self.bucket_name,
                'Key': destination_key
            }

            if metadata:
                copy_params['Metadata'] = metadata
                copy_params['MetadataDirective'] = 'REPLACE'

            if storage_class:
                copy_params['StorageClass'] = storage_class.value

            self.s3_client.copy_object(**copy_params)

            logger.info(f"File copied: {source_key} -> {destination_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to copy file: {str(e)}")
            return False

    @retry_on_aws_error()
    async def generate_presigned_url(
        self,
        key: str,
        operation: str = 'get_object',
        expires_in: int = 3600,
        http_method: str = None
    ) -> S3PresignedUrl:
        """Generate presigned URL for S3 operations"""
        await self._rate_limit_check()

        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key
            }

            if http_method:
                params['HttpMethod'] = http_method

            url = self.s3_client.generate_presigned_url(
                operation,
                Params=params,
                ExpiresIn=expires_in
            )

            expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info(f"Generated presigned URL for {key}")
            return S3PresignedUrl(
                url=url,
                expires_at=expires_at
            )

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise

    @retry_on_aws_error()
    async def generate_presigned_post(
        self,
        key: str,
        expires_in: int = 3600,
        conditions: List = None,
        fields: Dict[str, str] = None
    ) -> S3PresignedUrl:
        """Generate presigned POST for direct browser uploads"""
        await self._rate_limit_check()

        try:
            post_data = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                ExpiresIn=expires_in,
                Conditions=conditions or [],
                Fields=fields or {}
            )

            expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info(f"Generated presigned POST for {key}")
            return S3PresignedUrl(
                url=post_data['url'],
                expires_at=expires_at,
                fields=post_data['fields']
            )

        except ClientError as e:
            logger.error(f"Failed to generate presigned POST: {str(e)}")
            raise

    @retry_on_aws_error()
    async def set_file_acl(self, key: str, acl: ACL) -> bool:
        """Set file ACL permissions"""
        await self._rate_limit_check()

        try:
            self.s3_client.put_object_acl(
                Bucket=self.bucket_name,
                Key=key,
                ACL=acl.value
            )

            logger.info(f"ACL updated for {key}: {acl.value}")
            return True

        except ClientError as e:
            logger.error(f"Failed to set ACL: {str(e)}")
            return False

    @retry_on_aws_error()
    async def add_file_tags(self, key: str, tags: Dict[str, str]) -> bool:
        """Add tags to S3 object"""
        await self._rate_limit_check()

        try:
            tag_set = [{'Key': k, 'Value': v} for k, v in tags.items()]

            self.s3_client.put_object_tagging(
                Bucket=self.bucket_name,
                Key=key,
                Tagging={'TagSet': tag_set}
            )

            logger.info(f"Tags added to {key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to add tags: {str(e)}")
            return False

    @retry_on_aws_error()
    async def get_file_tags(self, key: str) -> Dict[str, str]:
        """Get tags for S3 object"""
        await self._rate_limit_check()

        try:
            response = self.s3_client.get_object_tagging(
                Bucket=self.bucket_name,
                Key=key
            )

            tags = {}
            for tag in response.get('TagSet', []):
                tags[tag['Key']] = tag['Value']

            logger.info(f"Retrieved tags for {key}")
            return tags

        except ClientError as e:
            logger.error(f"Failed to get tags: {str(e)}")
            return {}

    @retry_on_aws_error()
    async def create_multipart_upload(
        self,
        key: str,
        content_type: str = None,
        metadata: Dict[str, str] = None,
        storage_class: StorageClass = None,
        encryption: ServerSideEncryption = None
    ) -> str:
        """Create multipart upload for large files"""
        await self._rate_limit_check()

        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key
            }

            if content_type:
                params['ContentType'] = content_type

            if metadata:
                params['Metadata'] = metadata

            if storage_class:
                params['StorageClass'] = storage_class.value

            if encryption:
                params['ServerSideEncryption'] = encryption.value

            response = self.s3_client.create_multipart_upload(**params)

            upload_id = response['UploadId']
            logger.info(f"Created multipart upload: {upload_id}")
            return upload_id

        except ClientError as e:
            logger.error(f"Failed to create multipart upload: {str(e)}")
            raise

    @retry_on_aws_error()
    async def upload_part(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes
    ) -> Dict[str, Any]:
        """Upload part for multipart upload"""
        await self._rate_limit_check()

        try:
            response = self.s3_client.upload_part(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=data
            )

            part_info = {
                'PartNumber': part_number,
                'ETag': response['ETag']
            }

            logger.info(f"Uploaded part {part_number} for {key}")
            return part_info

        except ClientError as e:
            logger.error(f"Failed to upload part: {str(e)}")
            raise

    @retry_on_aws_error()
    async def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: List[Dict[str, Any]]
    ) -> S3UploadResult:
        """Complete multipart upload"""
        await self._rate_limit_check()

        try:
            response = self.s3_client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )

            logger.info(f"Completed multipart upload: {key}")
            return S3UploadResult(
                success=True,
                key=key,
                url=self._get_public_url(key),
                etag=response.get('ETag')
            )

        except ClientError as e:
            logger.error(f"Failed to complete multipart upload: {str(e)}")
            return S3UploadResult(
                success=False,
                error_message=str(e)
            )

    @retry_on_aws_error()
    async def abort_multipart_upload(self, key: str, upload_id: str) -> bool:
        """Abort multipart upload"""
        await self._rate_limit_check()

        try:
            self.s3_client.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id
            )

            logger.info(f"Aborted multipart upload: {upload_id}")
            return True

        except ClientError as e:
            logger.error(f"Failed to abort multipart upload: {str(e)}")
            return False

    async def upload_large_file(
        self,
        file_content: BinaryIO,
        filename: str,
        prefix: str = None,
        user_id: str = None,
        chunk_size: int = 100 * 1024 * 1024,  # 100MB chunks
        **kwargs
    ) -> S3UploadResult:
        """Upload large file using multipart upload"""
        try:
            key = self._generate_key(filename, prefix, user_id)
            content_type = self._get_content_type(filename)

            # Create multipart upload
            upload_id = await self.create_multipart_upload(
                key=key,
                content_type=content_type,
                **kwargs
            )

            parts = []
            part_number = 1

            try:
                while True:
                    chunk = file_content.read(chunk_size)
                    if not chunk:
                        break

                    part_info = await self.upload_part(
                        key=key,
                        upload_id=upload_id,
                        part_number=part_number,
                        data=chunk
                    )

                    parts.append(part_info)
                    part_number += 1

                # Complete multipart upload
                return await self.complete_multipart_upload(key, upload_id, parts)

            except Exception as e:
                # Abort multipart upload on error
                await self.abort_multipart_upload(key, upload_id)
                raise e

        except Exception as e:
            logger.error(f"Failed to upload large file: {str(e)}")
            return S3UploadResult(
                success=False,
                error_message=str(e)
            )

    def calculate_file_hash(self, file_content: BinaryIO, algorithm: str = 'md5') -> str:
        """Calculate file hash"""
        hash_obj = hashlib.new(algorithm)
        file_content.seek(0)

        while chunk := file_content.read(8192):
            hash_obj.update(chunk)

        file_content.seek(0)
        return hash_obj.hexdigest()

    async def sync_directory(
        self,
        local_directory: str,
        s3_prefix: str,
        delete_extra: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Sync local directory with S3 prefix"""
        import os

        results = {
            'uploaded': [],
            'deleted': [],
            'skipped': [],
            'errors': []
        }

        try:
            # Get local files
            local_files = {}
            for root, dirs, files in os.walk(local_directory):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, local_directory)
                    s3_key = f"{s3_prefix.rstrip('/')}/{relative_path.replace(os.sep, '/')}"

                    local_files[s3_key] = {
                        'local_path': local_path,
                        'size': os.path.getsize(local_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(local_path))
                    }

            # Get S3 files
            s3_response = await self.list_files(prefix=s3_prefix)
            s3_files = {obj.key: obj for obj in s3_response['objects']}

            # Upload new/modified files
            for s3_key, local_info in local_files.items():
                should_upload = False

                if s3_key not in s3_files:
                    should_upload = True
                    reason = "new file"
                else:
                    s3_obj = s3_files[s3_key]
                    if local_info['size'] != s3_obj.size:
                        should_upload = True
                        reason = "size mismatch"
                    elif local_info['modified'] > s3_obj.last_modified.replace(tzinfo=None):
                        should_upload = True
                        reason = "modified"

                if should_upload:
                    if not dry_run:
                        try:
                            result = await self.upload_file_from_path(
                                file_path=local_info['local_path'],
                                s3_key=s3_key
                            )
                            if result.success:
                                results['uploaded'].append({'key': s3_key, 'reason': reason})
                            else:
                                results['errors'].append({'key': s3_key, 'error': result.error_message})
                        except Exception as e:
                            results['errors'].append({'key': s3_key, 'error': str(e)})
                    else:
                        results['uploaded'].append({'key': s3_key, 'reason': f"{reason} (dry run)"})
                else:
                    results['skipped'].append({'key': s3_key, 'reason': "up to date"})

            # Delete extra S3 files
            if delete_extra:
                for s3_key in s3_files:
                    if s3_key not in local_files:
                        if not dry_run:
                            success = await self.delete_file(s3_key)
                            if success:
                                results['deleted'].append({'key': s3_key, 'reason': "not in local"})
                            else:
                                results['errors'].append({'key': s3_key, 'error': "delete failed"})
                        else:
                            results['deleted'].append({'key': s3_key, 'reason': "not in local (dry run)"})

            logger.info(f"Directory sync completed: {len(results['uploaded'])} uploaded, "
                       f"{len(results['deleted'])} deleted, {len(results['skipped'])} skipped, "
                       f"{len(results['errors'])} errors")

            return results

        except Exception as e:
            logger.error(f"Directory sync failed: {str(e)}")
            results['errors'].append({'error': str(e)})
            return results

# Utility functions
async def create_aws_s3_service(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    bucket_name: str,
    region_name: str = 'us-east-1',
    cloudfront_domain: str = None,
    default_storage_class: StorageClass = StorageClass.STANDARD,
    default_encryption: ServerSideEncryption = ServerSideEncryption.AES256
) -> AWSS3Service:
    """Factory function to create AWSS3Service instance"""
    return AWSS3Service(
        aws_access_key_id,
        aws_secret_access_key,
        bucket_name,
        region_name,
        cloudfront_domain,
        default_storage_class,
        default_encryption
    )

def create_file_upload_conditions(
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    allowed_content_types: List[str] = None
) -> List[Dict]:
    """Create upload conditions for presigned POST"""
    conditions = [
        ["content-length-range", 0, max_file_size]
    ]

    if allowed_content_types:
        conditions.append(["in", "$content-type", allowed_content_types])

    return conditions

def extract_filename_from_url(url: str) -> str:
    """Extract filename from S3 URL"""
    parsed_url = urlparse(url)
    return parsed_url.path.split('/')[-1]

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_image_file(filename: str) -> bool:
    """Check if file is an image based on extension"""
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    return get_file_extension(filename) in image_extensions

def is_document_file(filename: str) -> bool:
    """Check if file is a document based on extension"""
    document_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv']
    return get_file_extension(filename) in document_extensions