"""
Subscription Model
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base, TimestampMixin, generate_uuid


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIALING = "trialing"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier"""
    PRO = "pro"
    STUDIO = "studio"
    FORENSIC = "forensic"


class Subscription(Base, TimestampMixin):
    """User subscription"""
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Stripe
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_price_id = Column(String(255), nullable=False)

    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False)

    # Billing period
    current_period_start = Column(String, nullable=False)  # ISO timestamp
    current_period_end = Column(String, nullable=False)  # ISO timestamp

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(String, nullable=True)  # ISO timestamp

    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription user_id={self.user_id} tier={self.tier} status={self.status}>"
