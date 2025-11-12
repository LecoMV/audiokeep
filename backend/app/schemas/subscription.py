"""
Subscription Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionCreate(BaseModel):
    """Schema for creating subscription"""
    tier: str  # 'pro', 'studio', 'forensic'
    payment_method_id: str  # Stripe payment method ID


class SubscriptionResponse(BaseModel):
    """Subscription response schema"""
    id: str
    user_id: str
    tier: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
    cancelled_at: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription"""
    tier: Optional[str] = None  # Upgrade/downgrade
    cancel_at_period_end: Optional[bool] = None
