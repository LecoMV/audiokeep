#!/usr/bin/env python3
"""
Initialize Database with Alembic Migrations
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.base import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """Initialize database"""
    logger.info("Creating database tables...")

    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

    logger.info("✓ Database tables created successfully")


async def create_superuser():
    """Create initial superuser"""
    from app.db.session import AsyncSessionLocal
    from app.services.user_service import UserService
    from app.schemas.user import UserCreate

    logger.info("Creating superuser...")

    async with AsyncSessionLocal() as db:
        user_service = UserService(db)

        # Check if superuser exists
        existing = await user_service.get_user_by_email("admin@audiokeep.io")
        if existing:
            logger.info("Superuser already exists")
            return

        # Create superuser
        user_data = UserCreate(
            email="admin@audiokeep.io",
            password="AdminPassword123!",
            full_name="AudioKeep Admin"
        )

        user = await user_service.create_user(user_data)
        user.is_superuser = True
        await db.commit()

        logger.info(f"✓ Superuser created: {user.email}")
        logger.info("  Password: AdminPassword123!")
        logger.info("  PLEASE CHANGE THIS PASSWORD IMMEDIATELY!")


async def main():
    """Main entry point"""
    try:
        await init_db()
        await create_superuser()
        logger.info("\n✓ Database initialization complete!")
        return 0
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
