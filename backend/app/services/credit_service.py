"""
Credit Service
Business logic for credit management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from typing import Optional, List
import logging

from app.models.credit import Credit, CreditTransaction, TransactionType
from app.models.user import User

logger = logging.getLogger(__name__)


class CreditService:
    """Service for credit operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_credit_balance(self, user_id: str) -> Optional[Credit]:
        """Get user's credit balance"""
        result = await self.db.execute(
            select(Credit).where(Credit.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def add_credits(
        self,
        user_id: str,
        amount: Decimal,
        transaction_type: TransactionType,
        description: Optional[str] = None,
        stripe_payment_id: Optional[str] = None
    ) -> Credit:
        """Add credits to user account"""
        # Get or create credit record
        credit = await self.get_user_credit_balance(user_id)

        if not credit:
            credit = Credit(user_id=user_id, balance=Decimal(0))
            self.db.add(credit)
            await self.db.flush()

        # Update balance
        credit.balance += amount

        # Create transaction record
        transaction = CreditTransaction(
            user_id=user_id,
            amount=amount,
            balance_after=credit.balance,
            type=transaction_type,
            description=description,
            stripe_payment_id=stripe_payment_id
        )
        self.db.add(transaction)

        await self.db.commit()
        await self.db.refresh(credit)

        logger.info(f"Added {amount} credits to user {user_id}. New balance: {credit.balance}")
        return credit

    async def deduct_credits(
        self,
        user_id: str,
        amount: Decimal,
        job_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Credit:
        """Deduct credits from user account"""
        credit = await self.get_user_credit_balance(user_id)

        if not credit:
            raise ValueError("Credit account not found")

        if credit.balance < amount:
            raise ValueError(f"Insufficient credits. Balance: {credit.balance}, Required: {amount}")

        # Update balance
        credit.balance -= amount

        # Create transaction record
        transaction = CreditTransaction(
            user_id=user_id,
            amount=-amount,  # Negative for deduction
            balance_after=credit.balance,
            type=TransactionType.USAGE,
            description=description,
            job_id=job_id
        )
        self.db.add(transaction)

        await self.db.commit()
        await self.db.refresh(credit)

        logger.info(f"Deducted {amount} credits from user {user_id}. New balance: {credit.balance}")
        return credit

    async def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[CreditTransaction]:
        """Get user's credit transaction history"""
        result = await self.db.execute(
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def check_sufficient_credits(self, user_id: str, amount: Decimal) -> bool:
        """Check if user has sufficient credits"""
        credit = await self.get_user_credit_balance(user_id)
        if not credit:
            return False
        return credit.balance >= amount

    def calculate_credit_cost(
        self,
        duration_seconds: float,
        quality_tier: str,
        settings: dict
    ) -> Decimal:
        """Calculate credit cost for a job"""
        # Base cost: 1 credit per minute
        base_cost = Decimal(duration_seconds) / Decimal(60)

        # Quality multipliers
        quality_multipliers = {
            'standard': Decimal('1.0'),
            'high': Decimal('2.0'),
            'ultra': Decimal('4.0'),
            'forensic': Decimal('6.0')
        }
        quality_mult = quality_multipliers.get(quality_tier, Decimal('1.0'))

        # Feature multipliers (additive)
        features_mult = Decimal('1.0')
        if settings.get('noise_reduction'):
            features_mult += Decimal('0.3')
        if settings.get('speech_enhancement'):
            features_mult += Decimal('0.4')
        if settings.get('voice_isolation'):
            features_mult += Decimal('0.8')
        if settings.get('spectral_repair'):
            features_mult += Decimal('0.6')
        if settings.get('forensic_analysis'):
            features_mult += Decimal('1.5')

        total_cost = base_cost * quality_mult * features_mult

        # Round up to 2 decimal places
        return total_cost.quantize(Decimal('0.01'))
