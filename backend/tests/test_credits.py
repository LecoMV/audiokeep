"""
Tests for Credit System
"""
import pytest
from httpx import AsyncClient
from decimal import Decimal

from app.services.credit_service import CreditService
from app.models.credit import TransactionType


@pytest.mark.unit
class TestCredits:
    """Test credit management"""

    async def test_get_initial_credit_balance(self, authenticated_client):
        """Test user gets free credits on signup"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/credits/balance")

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["balance"])) == Decimal("50")  # FREE_TIER_CREDITS

    async def test_get_credit_history(self, authenticated_client):
        """Test get credit transaction history"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/credits/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_calculate_credit_cost(self, db_session):
        """Test credit cost calculation"""
        credit_service = CreditService(db_session)

        # Test standard quality, 60 seconds, basic features
        cost = credit_service.calculate_credit_cost(
            duration_seconds=60,
            quality_tier="standard",
            settings={"noise_reduction": True}
        )

        # 1 minute * 1.0 (standard) * 1.3 (noise reduction) = 1.3 credits
        assert cost == Decimal("1.30")

    async def test_calculate_credit_cost_high_quality(self, db_session):
        """Test credit cost for high quality"""
        credit_service = CreditService(db_session)

        cost = credit_service.calculate_credit_cost(
            duration_seconds=120,  # 2 minutes
            quality_tier="high",
            settings={"noise_reduction": True, "speech_enhancement": True}
        )

        # 2 minutes * 2.0 (high) * 1.7 (features) = 6.8 credits
        assert cost == Decimal("6.80")

    async def test_add_credits(self, db_session, test_user_data):
        """Test adding credits to account"""
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate

        # Create user
        user_service = UserService(db_session)
        user = await user_service.create_user(UserCreate(**test_user_data))

        # Add credits
        credit_service = CreditService(db_session)
        balance = await credit_service.add_credits(
            user_id=user.id,
            amount=Decimal("100"),
            transaction_type=TransactionType.PURCHASE,
            description="Test purchase"
        )

        assert balance.balance == Decimal("150")  # 50 initial + 100 purchased

    async def test_deduct_credits(self, db_session, test_user_data):
        """Test deducting credits"""
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate

        # Create user
        user_service = UserService(db_session)
        user = await user_service.create_user(UserCreate(**test_user_data))

        # Deduct credits
        credit_service = CreditService(db_session)
        balance = await credit_service.deduct_credits(
            user_id=user.id,
            amount=Decimal("10"),
            description="Test usage"
        )

        assert balance.balance == Decimal("40")  # 50 - 10

    async def test_deduct_insufficient_credits(self, db_session, test_user_data):
        """Test deducting more credits than available"""
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate

        # Create user
        user_service = UserService(db_session)
        user = await user_service.create_user(UserCreate(**test_user_data))

        # Try to deduct more than available
        credit_service = CreditService(db_session)

        with pytest.raises(ValueError, match="Insufficient credits"):
            await credit_service.deduct_credits(
                user_id=user.id,
                amount=Decimal("100"),  # More than 50 initial credits
                description="Test usage"
            )
