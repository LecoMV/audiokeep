"""
Credit Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.credit import CreditResponse, CreditTransactionResponse, CreditPurchase
from app.models.user import User
from app.api.dependencies import get_current_active_user
from app.services.credit_service import CreditService

router = APIRouter()


@router.get("/balance", response_model=CreditResponse)
async def get_credit_balance(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's credit balance
    """
    credit_service = CreditService(db)
    balance = await credit_service.get_user_credit_balance(current_user.id)

    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit balance not found"
        )

    return balance


@router.get("/history", response_model=List[CreditTransactionResponse])
async def get_credit_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get credit transaction history

    - **limit**: Maximum number of transactions to return (default: 50)
    - **offset**: Number of transactions to skip (default: 0)
    """
    credit_service = CreditService(db)
    transactions = await credit_service.get_transaction_history(
        current_user.id,
        limit=limit,
        offset=offset
    )

    return transactions


@router.post("/purchase", response_model=CreditResponse, status_code=status.HTTP_201_CREATED)
async def purchase_credits(
    purchase_data: CreditPurchase,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Purchase credit pack

    - **package**: Credit package ('starter', 'professional', 'studio', 'enterprise')
    - **payment_method_id**: Stripe payment method ID

    NOTE: This is a simplified version. In production, implement full Stripe integration.
    """
    from app.core.config import settings
    from app.models.credit import TransactionType
    from decimal import Decimal

    # Credit package mapping
    packages = {
        'starter': settings.CREDIT_PACK_STARTER,
        'professional': settings.CREDIT_PACK_PROFESSIONAL,
        'studio': settings.CREDIT_PACK_STUDIO,
        'enterprise': settings.CREDIT_PACK_ENTERPRISE,
    }

    credit_amount = packages.get(purchase_data.package)
    if not credit_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid package type"
        )

    # TODO: Implement Stripe payment processing here
    # For now, we'll simulate a successful payment

    credit_service = CreditService(db)
    try:
        balance = await credit_service.add_credits(
            user_id=current_user.id,
            amount=Decimal(credit_amount),
            transaction_type=TransactionType.PURCHASE,
            description=f"Purchased {purchase_data.package} credit pack",
            stripe_payment_id=purchase_data.payment_method_id  # In production, use actual payment ID
        )
        return balance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
