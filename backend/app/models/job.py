"""
Audio Processing Job Model
"""
from sqlalchemy import Column, String, BigInteger, Numeric, ForeignKey, Enum as SQLEnum, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base, TimestampMixin, generate_uuid


class JobStatus(str, enum.Enum):
    """Job processing status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QualityTier(str, enum.Enum):
    """Audio quality tier"""
    STANDARD = "standard"  # 48kHz, basic processing
    HIGH = "high"  # 96kHz, advanced processing
    ULTRA = "ultra"  # 192kHz, maximum quality
    FORENSIC = "forensic"  # Forensic analysis + reporting


class Job(Base, TimestampMixin):
    """Audio processing job"""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # File information
    original_filename = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # bytes
    duration_seconds = Column(Numeric(10, 2), nullable=True)
    original_sample_rate = Column(BigInteger, nullable=True)
    original_channels = Column(BigInteger, nullable=True)
    original_format = Column(String(50), nullable=True)

    # Processing status
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    started_at = Column(String, nullable=True)  # ISO timestamp
    completed_at = Column(String, nullable=True)  # ISO timestamp
    error_message = Column(Text, nullable=True)

    # Processing settings
    settings = Column(JSON, nullable=False)
    quality_tier = Column(SQLEnum(QualityTier), default=QualityTier.STANDARD, nullable=False)

    # Credits
    credits_estimated = Column(Numeric(10, 2), nullable=False)
    credits_used = Column(Numeric(10, 2), nullable=True)

    # File URLs
    input_file_url = Column(String(1000), nullable=True)
    output_file_url = Column(String(1000), nullable=True)

    # Processing results
    quality_metrics = Column(JSON, nullable=True)
    processing_logs = Column(Text, nullable=True)

    # Celery task
    celery_task_id = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="jobs")
    credit_transaction = relationship("CreditTransaction", back_populates="job", uselist=False)

    def __repr__(self):
        return f"<Job {self.id} status={self.status}>"
