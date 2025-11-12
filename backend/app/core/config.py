"""
Application Configuration
Load and validate environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import secrets


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    APP_NAME: str = "AudioKeep"
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    API_VERSION: str = Field(default="v1", env="API_VERSION")
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))

    # Server
    BACKEND_HOST: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    BACKEND_PORT: int = Field(default=8000, env="BACKEND_PORT")
    FRONTEND_URL: str = Field(default="http://localhost:5173", env="FRONTEND_URL")
    BACKEND_URL: str = Field(default="http://localhost:8000", env="BACKEND_URL")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://audiokeep:audiokeep_password@localhost:5432/audiokeep",
        env="DATABASE_URL"
    )

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1", env="CELERY_RESULT_BACKEND")

    # S3/MinIO
    S3_ENDPOINT: str = Field(default="http://localhost:9000", env="S3_ENDPOINT")
    S3_ACCESS_KEY: str = Field(default="minioadmin", env="S3_ACCESS_KEY")
    S3_SECRET_KEY: str = Field(default="minioadmin", env="S3_SECRET_KEY")
    S3_BUCKET_NAME: str = Field(default="audiokeep", env="S3_BUCKET_NAME")
    S3_REGION: str = Field(default="us-east-1", env="S3_REGION")
    USE_S3: bool = Field(default=True, env="USE_S3")

    # Authentication
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Email
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_FROM: str = Field(default="noreply@audiokeep.io", env="SMTP_FROM")
    SMTP_FROM_NAME: str = Field(default="AudioKeep", env="SMTP_FROM_NAME")

    # Stripe
    STRIPE_SECRET_KEY: str = Field(default="", env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: str = Field(default="", env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")

    # AI Models
    MODEL_CACHE_DIR: str = Field(default="/app/models", env="MODEL_CACHE_DIR")
    TORCH_HOME: str = Field(default="/app/torch_cache", env="TORCH_HOME")
    HF_HOME: str = Field(default="/app/hf_cache", env="HF_HOME")
    TORCH_DEVICE: str = Field(default="cuda", env="TORCH_DEVICE")

    # Processing Configuration
    MAX_UPLOAD_SIZE_MB: int = Field(default=2048, env="MAX_UPLOAD_SIZE_MB")
    MAX_AUDIO_DURATION_SECONDS: int = Field(default=28800, env="MAX_AUDIO_DURATION_SECONDS")
    DEFAULT_SAMPLE_RATE: int = Field(default=48000, env="DEFAULT_SAMPLE_RATE")
    SUPPORTED_FORMATS: str = Field(default="wav,mp3,flac,m4a,ogg,aac,wma", env="SUPPORTED_FORMATS")
    MAX_BATCH_SIZE: int = Field(default=10, env="MAX_BATCH_SIZE")
    PROCESSING_TIMEOUT_SECONDS: int = Field(default=3600, env="PROCESSING_TIMEOUT_SECONDS")

    @validator("SUPPORTED_FORMATS")
    def parse_supported_formats(cls, v):
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(",")]
        return v

    # Credits
    FREE_TIER_CREDITS: int = Field(default=50, env="FREE_TIER_CREDITS")
    CREDIT_PACK_STARTER: int = Field(default=100, env="CREDIT_PACK_STARTER")
    CREDIT_PACK_PROFESSIONAL: int = Field(default=500, env="CREDIT_PACK_PROFESSIONAL")
    CREDIT_PACK_STUDIO: int = Field(default=1500, env="CREDIT_PACK_STUDIO")
    CREDIT_PACK_ENTERPRISE: int = Field(default=5000, env="CREDIT_PACK_ENTERPRISE")

    # File Retention
    FILE_RETENTION_DAYS: int = Field(default=30, env="FILE_RETENTION_DAYS")
    TEMP_FILE_CLEANUP_HOURS: int = Field(default=24, env="TEMP_FILE_CLEANUP_HOURS")

    # Monitoring
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Feature Flags
    ENABLE_FORENSIC_FEATURES: bool = Field(default=True, env="ENABLE_FORENSIC_FEATURES")
    ENABLE_BATCH_PROCESSING: bool = Field(default=True, env="ENABLE_BATCH_PROCESSING")
    ENABLE_API_ACCESS: bool = Field(default=True, env="ENABLE_API_ACCESS")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_UPLOAD_PER_HOUR: int = Field(default=100, env="RATE_LIMIT_UPLOAD_PER_HOUR")

    # GPU Configuration
    GPU_MEMORY_FRACTION: float = Field(default=0.9, env="GPU_MEMORY_FRACTION")
    ENABLE_MIXED_PRECISION: bool = Field(default=True, env="ENABLE_MIXED_PRECISION")
    BATCH_INFERENCE_SIZE: int = Field(default=4, env="BATCH_INFERENCE_SIZE")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
