"""
Celery Application Configuration
Distributed task queue for audio processing
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "audiokeep",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.audio_processing",
        "app.services.cleanup_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.PROCESSING_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.PROCESSING_TIMEOUT_SECONDS - 60,
    worker_prefetch_multiplier=1,  # Important for GPU tasks
    worker_max_tasks_per_child=10,  # Prevent memory leaks
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # 1 hour
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-files": {
        "task": "app.services.cleanup_tasks.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    "cleanup-temp-files": {
        "task": "app.services.cleanup_tasks.cleanup_temp_files",
        "schedule": crontab(hour="*/6", minute=0),  # Run every 6 hours
    },
    "update-credit-balances": {
        "task": "app.services.cleanup_tasks.update_credit_balances",
        "schedule": crontab(hour=0, minute=0),  # Run daily at midnight
    },
}


if __name__ == "__main__":
    celery_app.start()
