"""
User Service
Business logic for user management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging

from app.models.user import User, SubscriptionTier
from app.models.credit import Credit
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.config import settings

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        # Check if user exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            subscription_tier=SubscriptionTier.FREE,
        )
        self.db.add(user)
        await self.db.flush()

        # Create initial credit balance with free credits
        credit = Credit(
            user_id=user.id,
            balance=settings.FREE_TIER_CREDITS
        )
        self.db.add(credit)

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Created new user: {user.email} with {settings.FREE_TIER_CREDITS} free credits")
        return user

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.email is not None:
            # Check if email is already taken
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already in use")
            user.email = user_data.email
            user.email_verified = False  # Require re-verification

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        logger.info(f"Deleted user: {user.email}")
        return True
