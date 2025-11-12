"""
Credit Pydantic Schemas
"""
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional


class CreditResponse(BaseModel):
    """Credit balance response"""
    user_id: str
    balance: Decimal
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditTransactionResponse(BaseModel):
    """Credit transaction response"""
    id: str
    user_id: str
    amount: Decimal
    balance_after: Decimal
    type: str
    description: Optional[str] = None
    created_at: datetime
    stripe_payment_id: Optional[str] = None

    class Config:
        from_attributes = True


class CreditPurchase(BaseModel):
    """Schema for purchasing credits"""
    package: str  # 'starter', 'professional', 'studio', 'enterprise'
    payment_method_id: str  # Stripe payment method ID
