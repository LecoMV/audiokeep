"""
Base SQLAlchemy Model
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime
import uuid

Base = declarative_base()


class TimestampMixin:
    """Mixin for timestamp columns"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())
