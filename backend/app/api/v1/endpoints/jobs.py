"""
Audio Processing Job Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.db.session import get_db
from app.schemas.job import JobCreate, JobResponse, JobSettings
from app.models.user import User
from app.api.dependencies import get_current_active_user
from app.services.job_service import JobService
from app.services.credit_service import CreditService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio_file(
    file: UploadFile = File(...),
    settings: str = None,  # JSON string of JobSettings
    quality_tier: str = "standard",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload audio file for processing

    - **file**: Audio file (WAV, MP3, FLAC, M4A, OGG, etc.)
    - **settings**: JSON string of processing settings
    - **quality_tier**: Quality tier ('standard', 'high', 'ultra', 'forensic')

    Returns job information with estimated credit cost
    """
    from app.core.config import settings as app_settings
    import json

    # Validate file size
    file_size = 0
    contents = await file.read()
    file_size = len(contents)

    max_size = app_settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {app_settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    # Validate file format
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in app_settings.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported formats: {', '.join(app_settings.SUPPORTED_FORMATS)}"
        )

    # Parse settings
    try:
        if settings:
            settings_dict = json.loads(settings)
            job_settings = JobSettings(**settings_dict)
        else:
            job_settings = JobSettings()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid settings: {str(e)}"
        )

    # Create job
    job_service = JobService(db)
    try:
        job = await job_service.create_job(
            user_id=current_user.id,
            filename=file.filename,
            file_content=contents,
            settings=job_settings.model_dump(),
            quality_tier=quality_tier
        )
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{job_id}/process", response_model=JobResponse)
async def start_processing(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start processing an uploaded job

    Checks credit balance and initiates processing
    """
    job_service = JobService(db)
    credit_service = CreditService(db)

    # Get job
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Verify ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process this job"
        )

    # Check credits
    has_credits = await credit_service.check_sufficient_credits(
        current_user.id,
        job.credits_estimated
    )
    if not has_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits"
        )

    # Start processing
    try:
        updated_job = await job_service.start_processing(job_id)
        return updated_job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get job information
    """
    job_service = JobService(db)
    job = await job_service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )

    return job


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's jobs

    - **limit**: Maximum number of jobs to return (default: 50)
    - **offset**: Number of jobs to skip (default: 0)
    """
    job_service = JobService(db)
    jobs = await job_service.list_user_jobs(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return jobs


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a job
    """
    job_service = JobService(db)
    job = await job_service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job"
        )

    await job_service.delete_job(job_id)
    return None
