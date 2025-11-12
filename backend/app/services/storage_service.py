"""
Storage Service
S3/MinIO file storage operations
"""
import boto3
from botocore.client import Config
from typing import Optional
import logging
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for file storage operations"""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created S3 bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to create bucket: {e}")

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        folder: str = "uploads"
    ) -> str:
        """Upload file to S3"""
        try:
            key = f"{folder}/{user_id}/{filename}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content
            )
            logger.info(f"Uploaded file to S3: {key}")
            return key
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    async def download_file(self, file_key: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise

    async def delete_file(self, file_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"Deleted file from S3: {file_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 604800  # 7 days
    ) -> str:
        """Generate presigned URL for file download"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
