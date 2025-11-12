"""
Job Service
Business logic for audio processing jobs
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from decimal import Decimal
import logging
import librosa
import io

from app.models.job import Job, JobStatus, QualityTier
from app.services.credit_service import CreditService
from app.services.storage_service import StorageService
from app.core.config import settings

logger = logging.getLogger(__name__)


class JobService:
    """Service for job operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.credit_service = CreditService(db)
        self.storage_service = StorageService()

    async def create_job(
        self,
        user_id: str,
        filename: str,
        file_content: bytes,
        settings: dict,
        quality_tier: str
    ) -> Job:
        """Create a new processing job"""
        # Extract audio metadata
        try:
            audio_data, sample_rate = librosa.load(io.BytesIO(file_content), sr=None)
            duration = len(audio_data) / sample_rate

            # Validate duration
            if duration > settings.MAX_AUDIO_DURATION_SECONDS:
                raise ValueError(f"Audio too long. Maximum duration: {settings.MAX_AUDIO_DURATION_SECONDS/3600} hours")

        except Exception as e:
            logger.error(f"Failed to load audio file: {e}")
            raise ValueError(f"Invalid audio file: {str(e)}")

        # Calculate estimated credits
        estimated_credits = self.credit_service.calculate_credit_cost(
            duration_seconds=duration,
            quality_tier=quality_tier,
            settings=settings
        )

        # Upload file to storage
        try:
            file_url = await self.storage_service.upload_file(
                file_content=file_content,
                filename=filename,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise ValueError(f"Failed to upload file: {str(e)}")

        # Create job
        job = Job(
            user_id=user_id,
            original_filename=filename,
            file_size=len(file_content),
            duration_seconds=Decimal(str(duration)),
            original_sample_rate=sample_rate,
            original_channels=1 if len(audio_data.shape) == 1 else audio_data.shape[0],
            original_format=filename.split('.')[-1].lower(),
            status=JobStatus.PENDING,
            settings=settings,
            quality_tier=QualityTier(quality_tier),
            credits_estimated=estimated_credits,
            input_file_url=file_url
        )

        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        logger.info(f"Created job {job.id} for user {user_id}. Estimated credits: {estimated_credits}")
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_user_jobs(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Job]:
        """List user's jobs"""
        result = await self.db.execute(
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def start_processing(self, job_id: str) -> Job:
        """Start processing a job"""
        from app.services.audio_processing import process_audio_task

        job = await self.get_job(job_id)
        if not job:
            raise ValueError("Job not found")

        if job.status != JobStatus.PENDING:
            raise ValueError(f"Job already {job.status}")

        # Update status to queued
        job.status = JobStatus.QUEUED
        await self.db.commit()

        # Dispatch Celery task
        task = process_audio_task.delay(job_id)
        job.celery_task_id = task.id

        await self.db.commit()
        await self.db.refresh(job)

        logger.info(f"Started processing job {job_id} with task {task.id}")
        return job

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        error_message: Optional[str] = None
    ) -> Job:
        """Update job status"""
        job = await self.get_job(job_id)
        if not job:
            raise ValueError("Job not found")

        job.status = status
        if error_message:
            job.error_message = error_message

        if status == JobStatus.PROCESSING:
            from datetime import datetime
            job.started_at = datetime.utcnow().isoformat()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            from datetime import datetime
            job.completed_at = datetime.utcnow().isoformat()

        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def complete_job(
        self,
        job_id: str,
        output_file_url: str,
        quality_metrics: dict,
        credits_used: Decimal
    ) -> Job:
        """Mark job as completed"""
        from app.models.credit import TransactionType

        job = await self.get_job(job_id)
        if not job:
            raise ValueError("Job not found")

        job.status = JobStatus.COMPLETED
        job.output_file_url = output_file_url
        job.quality_metrics = quality_metrics
        job.credits_used = credits_used

        from datetime import datetime
        job.completed_at = datetime.utcnow().isoformat()

        # Deduct credits
        await self.credit_service.deduct_credits(
            user_id=job.user_id,
            amount=credits_used,
            job_id=job_id,
            description=f"Audio processing: {job.original_filename}"
        )

        await self.db.commit()
        await self.db.refresh(job)

        logger.info(f"Completed job {job_id}. Credits used: {credits_used}")
        return job

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        job = await self.get_job(job_id)
        if not job:
            return False

        # Delete files from storage
        if job.input_file_url:
            await self.storage_service.delete_file(job.input_file_url)
        if job.output_file_url:
            await self.storage_service.delete_file(job.output_file_url)

        await self.db.delete(job)
        await self.db.commit()

        logger.info(f"Deleted job {job_id}")
        return True
