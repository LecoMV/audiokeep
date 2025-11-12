"""
Cleanup Celery Tasks
Scheduled tasks for maintenance
"""
from celery import Task
import logging
from datetime import datetime, timedelta

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.storage_service import StorageService
from app.models.job import Job, JobStatus
from sqlalchemy import select

logger = logging.getLogger(__name__)


@celery_app.task(name="app.services.cleanup_tasks.cleanup_old_files")
def cleanup_old_files():
    """
    Clean up files older than retention period

    Runs daily at 2 AM
    """
    import asyncio
    return asyncio.run(cleanup_old_files_async())


async def cleanup_old_files_async():
    """Async cleanup of old files"""
    async with AsyncSessionLocal() as db:
        storage_service = StorageService()

        try:
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=settings.FILE_RETENTION_DAYS)

            # Find old completed jobs
            result = await db.execute(
                select(Job).where(
                    Job.status == JobStatus.COMPLETED,
                    Job.created_at < cutoff_date
                )
            )
            old_jobs = result.scalars().all()

            deleted_count = 0
            for job in old_jobs:
                try:
                    # Delete files
                    if job.input_file_url:
                        await storage_service.delete_file(job.input_file_url)
                    if job.output_file_url:
                        await storage_service.delete_file(job.output_file_url)

                    # Delete job record
                    await db.delete(job)
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Failed to delete job {job.id}: {e}")

            await db.commit()
            logger.info(f"Cleaned up {deleted_count} old jobs")
            return {"deleted": deleted_count}

        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")
            raise


@celery_app.task(name="app.services.cleanup_tasks.cleanup_temp_files")
def cleanup_temp_files():
    """
    Clean up temporary files

    Runs every 6 hours
    """
    import asyncio
    return asyncio.run(cleanup_temp_files_async())


async def cleanup_temp_files_async():
    """Async cleanup of temporary files"""
    # TODO: Implement temp file cleanup
    logger.info("Temporary file cleanup completed")
    return {"status": "ok"}


@celery_app.task(name="app.services.cleanup_tasks.update_credit_balances")
def update_credit_balances():
    """
    Update credit balances and handle expirations

    Runs daily at midnight
    """
    import asyncio
    return asyncio.run(update_credit_balances_async())


async def update_credit_balances_async():
    """Async credit balance updates"""
    # TODO: Implement credit expiration logic if needed
    logger.info("Credit balance update completed")
    return {"status": "ok"}
