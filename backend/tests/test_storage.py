"""
Tests for Storage Service
"""
import pytest
from app.services.storage_service import StorageService


@pytest.mark.unit
class TestStorageService:
    """Test storage service operations"""

    @pytest.fixture
    def storage_service(self):
        """Create storage service instance"""
        # Note: This will use MinIO/S3 configured in .env
        # For testing, you may want to use a test bucket
        return StorageService()

    async def test_upload_file(self, storage_service):
        """Test file upload"""
        content = b"Test audio content"
        filename = "test_upload.wav"
        user_id = "test_user_123"

        file_key = await storage_service.upload_file(
            file_content=content,
            filename=filename,
            user_id=user_id
        )

        assert file_key is not None
        assert user_id in file_key
        assert filename in file_key

    async def test_download_file(self, storage_service):
        """Test file download"""
        # First upload a file
        content = b"Test audio content for download"
        filename = "test_download.wav"
        user_id = "test_user_456"

        file_key = await storage_service.upload_file(
            file_content=content,
            filename=filename,
            user_id=user_id
        )

        # Download it back
        downloaded = await storage_service.download_file(file_key)

        assert downloaded == content

    async def test_delete_file(self, storage_service):
        """Test file deletion"""
        # Upload a file
        content = b"Test audio content for deletion"
        filename = "test_delete.wav"
        user_id = "test_user_789"

        file_key = await storage_service.upload_file(
            file_content=content,
            filename=filename,
            user_id=user_id
        )

        # Delete it
        success = await storage_service.delete_file(file_key)
        assert success is True

    async def test_generate_presigned_url(self, storage_service):
        """Test presigned URL generation"""
        # Upload a file first
        content = b"Test audio content"
        filename = "test_presigned.wav"
        user_id = "test_user_101"

        file_key = await storage_service.upload_file(
            file_content=content,
            filename=filename,
            user_id=user_id
        )

        # Generate presigned URL
        url = storage_service.generate_presigned_url(file_key)

        assert url is not None
        assert "http" in url
        assert file_key in url


@pytest.mark.integration
class TestStorageIntegration:
    """Integration tests for storage"""

    async def test_upload_download_cycle(self):
        """Test complete upload-download cycle"""
        storage_service = StorageService()

        # Upload
        original_content = b"Original audio data " * 1000
        file_key = await storage_service.upload_file(
            file_content=original_content,
            filename="cycle_test.wav",
            user_id="cycle_user"
        )

        # Download
        downloaded_content = await storage_service.download_file(file_key)

        # Verify
        assert downloaded_content == original_content

        # Cleanup
        await storage_service.delete_file(file_key)
