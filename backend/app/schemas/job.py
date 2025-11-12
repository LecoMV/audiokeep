"""
Job Pydantic Schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class JobSettings(BaseModel):
    """Audio processing settings"""
    # Restoration features
    noise_reduction: bool = False
    noise_reduction_strength: float = 0.5  # 0.0 to 1.0
    speech_enhancement: bool = False
    click_removal: bool = False
    spectral_repair: bool = False
    declipping: bool = False
    dehum: bool = False

    # Enhancement features
    voice_isolation: bool = False
    bandwidth_extension: bool = False
    dynamic_range_enhancement: bool = False

    # Quality settings
    target_sample_rate: int = 48000  # 48000, 96000, 192000
    output_format: str = "wav"  # wav, flac, mp3

    # Forensic features (requires forensic tier)
    forensic_analysis: bool = False
    generate_report: bool = False

    @validator("target_sample_rate")
    def validate_sample_rate(cls, v):
        if v not in [48000, 96000, 192000]:
            raise ValueError("Sample rate must be 48000, 96000, or 192000")
        return v

    @validator("output_format")
    def validate_format(cls, v):
        if v not in ["wav", "flac", "mp3"]:
            raise ValueError("Format must be wav, flac, or mp3")
        return v

    @validator("noise_reduction_strength")
    def validate_strength(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Strength must be between 0.0 and 1.0")
        return v


class JobCreate(BaseModel):
    """Schema for creating a job"""
    settings: JobSettings
    quality_tier: str = "standard"  # standard, high, ultra, forensic

    @validator("quality_tier")
    def validate_quality_tier(cls, v):
        if v not in ["standard", "high", "ultra", "forensic"]:
            raise ValueError("Quality tier must be standard, high, ultra, or forensic")
        return v


class JobResponse(BaseModel):
    """Job response schema"""
    id: str
    user_id: str
    original_filename: str
    file_size: int
    duration_seconds: Optional[Decimal] = None
    status: str
    created_at: datetime
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    settings: Dict[str, Any]
    quality_tier: str
    credits_estimated: Decimal
    credits_used: Optional[Decimal] = None
    output_file_url: Optional[str] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class ProcessingStatus(BaseModel):
    """Processing status update"""
    job_id: str
    status: str
    progress: float  # 0.0 to 1.0
    message: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds
