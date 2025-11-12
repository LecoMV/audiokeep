"""
Credit and Credit Transaction Models
"""
from sqlalchemy import Column, String, Numeric, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base, TimestampMixin, generate_uuid


class TransactionType(str, enum.Enum):
    """Credit transaction type"""
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"
    BONUS = "bonus"
    REFUND = "refund"
    USAGE = "usage"
    EXPIRATION = "expiration"


class Credit(Base):
    """User credit balance"""
    __tablename__ = "credits"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    balance = Column(Numeric(10, 2), default=0.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credits")

    def __repr__(self):
        return f"<Credit user_id={self.user_id} balance={self.balance}>"


class CreditTransaction(Base, TimestampMixin):
    """Credit transaction history"""
    __tablename__ = "credit_transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # Positive for add, negative for deduct
    balance_after = Column(Numeric(10, 2), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    description = Column(String(500), nullable=True)

    # Related entities
    job_id = Column(String, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    stripe_payment_id = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="credit_transactions")
    job = relationship("Job", back_populates="credit_transaction")

    def __repr__(self):
        return f"<CreditTransaction user_id={self.user_id} amount={self.amount} type={self.type}>"
