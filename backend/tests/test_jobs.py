"""
Tests for Job Endpoints and Processing
"""
import pytest
from httpx import AsyncClient
import io
from decimal import Decimal

from app.services.job_service import JobService
from app.services.credit_service import CreditService
from app.models.job import JobStatus, QualityTier


@pytest.mark.unit
class TestJobEndpoints:
    """Test job management endpoints"""

    async def test_upload_audio_file(self, authenticated_client):
        """Test audio file upload"""
        client, _ = authenticated_client

        # Create a small fake WAV file
        import wave
        import numpy as np

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(48000)
            audio_data = (np.random.randn(48000) * 32767).astype(np.int16)
            wav_file.writeframes(audio_data.tobytes())

        buffer.seek(0)

        # Upload file
        files = {'file': ('test_audio.wav', buffer, 'audio/wav')}
        data = {
            'quality_tier': 'standard'
        }

        response = await client.post(
            "/api/v1/jobs/upload",
            files=files,
            data=data
        )

        assert response.status_code == 201
        job = response.json()
        assert job['original_filename'] == 'test_audio.wav'
        assert job['status'] == 'pending'
        assert 'credits_estimated' in job
        assert Decimal(str(job['credits_estimated'])) > 0

    async def test_upload_file_too_large(self, authenticated_client):
        """Test upload with file too large"""
        client, _ = authenticated_client

        # This test would need to create a very large file
        # Skipping actual implementation for now
        pass

    async def test_upload_unsupported_format(self, authenticated_client):
        """Test upload with unsupported file format"""
        client, _ = authenticated_client

        # Create a text file
        buffer = io.BytesIO(b"This is not audio")
        files = {'file': ('test.txt', buffer, 'text/plain')}

        response = await client.post(
            "/api/v1/jobs/upload",
            files=files
        )

        assert response.status_code == 400

    async def test_list_user_jobs(self, authenticated_client):
        """Test listing user's jobs"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/jobs/")

        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)

    async def test_get_job_unauthorized(self, client: AsyncClient):
        """Test getting job without authentication"""
        response = await client.get("/api/v1/jobs/fake-job-id")
        assert response.status_code == 403


@pytest.mark.unit
class TestJobService:
    """Test job service layer"""

    async def test_create_job(self, db_session, test_user_data):
        """Test job creation"""
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate
        import wave
        import numpy as np

        # Create user
        user_service = UserService(db_session)
        user = await user_service.create_user(UserCreate(**test_user_data))

        # Create audio data
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(48000)
            audio_data = (np.random.randn(48000) * 32767).astype(np.int16)
            wav_file.writeframes(audio_data.tobytes())

        buffer.seek(0)
        audio_content = buffer.read()

        # Create job
        job_service = JobService(db_session)
        job = await job_service.create_job(
            user_id=user.id,
            filename="test.wav",
            file_content=audio_content,
            settings={"noise_reduction": True},
            quality_tier="standard"
        )

        assert job.user_id == user.id
        assert job.original_filename == "test.wav"
        assert job.status == JobStatus.PENDING
        assert job.credits_estimated > 0

    async def test_credit_cost_calculation(self, db_session):
        """Test credit cost calculation for different scenarios"""
        credit_service = CreditService(db_session)

        # Standard quality, 60 seconds, noise reduction only
        cost1 = credit_service.calculate_credit_cost(
            duration_seconds=60,
            quality_tier="standard",
            settings={"noise_reduction": True}
        )
        assert cost1 == Decimal("1.30")  # 1 min * 1.0 * 1.3

        # High quality, 120 seconds, multiple features
        cost2 = credit_service.calculate_credit_cost(
            duration_seconds=120,
            quality_tier="high",
            settings={
                "noise_reduction": True,
                "speech_enhancement": True,
                "voice_isolation": True
            }
        )
        # 2 min * 2.0 * (1.0 + 0.3 + 0.4 + 0.8) = 2 * 2.0 * 2.5 = 10.0
        assert cost2 == Decimal("10.00")

        # Forensic quality with analysis
        cost3 = credit_service.calculate_credit_cost(
            duration_seconds=60,
            quality_tier="forensic",
            settings={
                "noise_reduction": True,
                "forensic_analysis": True
            }
        )
        # 1 min * 6.0 * (1.0 + 0.3 + 1.5) = 6.0 * 2.8 = 16.8
        assert cost3 == Decimal("16.80")

    async def test_insufficient_credits_check(self, db_session, test_user_data):
        """Test insufficient credits prevention"""
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate

        # Create user
        user_service = UserService(db_session)
        user = await user_service.create_user(UserCreate(**test_user_data))

        # Check if user can afford expensive job
        credit_service = CreditService(db_session)

        # User has 50 credits, try to check for 100
        has_credits = await credit_service.check_sufficient_credits(
            user.id,
            Decimal("100")
        )

        assert has_credits is False

        # Check for 30 credits (should have enough)
        has_credits = await credit_service.check_sufficient_credits(
            user.id,
            Decimal("30")
        )

        assert has_credits is True


@pytest.mark.integration
class TestJobProcessing:
    """Test job processing workflow"""

    async def test_job_lifecycle(self, db_session, test_user_data):
        """Test complete job lifecycle"""
        from app.services.user_service import UserService
        from app.services.job_service import JobService
        from app.schemas.user import UserCreate
        import wave
        import numpy as np

        # Create user
        user_service = UserService(db_session)
        user = await user_service.create_user(UserCreate(**test_user_data))

        # Create audio
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(48000)
            audio_data = (np.random.randn(48000) * 32767).astype(np.int16)
            wav_file.writeframes(audio_data.tobytes())

        buffer.seek(0)
        audio_content = buffer.read()

        # Create job
        job_service = JobService(db_session)
        job = await job_service.create_job(
            user_id=user.id,
            filename="test.wav",
            file_content=audio_content,
            settings={"noise_reduction": True},
            quality_tier="standard"
        )

        assert job.status == JobStatus.PENDING

        # Update to processing
        updated_job = await job_service.update_job_status(
            job.id,
            JobStatus.PROCESSING
        )
        assert updated_job.status == JobStatus.PROCESSING
        assert updated_job.started_at is not None

        # Complete job (simulate)
        # Note: This would normally be done by Celery worker
        # For testing, we'll just verify the service method works
        quality_metrics = {
            "snr_db": 25.5,
            "dynamic_range_db": 18.2,
            "peak_amplitude": 0.95
        }

        completed_job = await job_service.update_job_status(
            job.id,
            JobStatus.COMPLETED
        )

        assert completed_job.status == JobStatus.COMPLETED
        assert completed_job.completed_at is not None
