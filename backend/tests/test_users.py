"""
Tests for User Endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.unit
class TestUsers:
    """Test user management endpoints"""

    async def test_get_current_user(self, authenticated_client):
        """Test get current user info"""
        client, _ = authenticated_client

        response = await client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "subscription_tier" in data

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test get current user without authentication"""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 403  # No Authorization header

    async def test_update_user(self, authenticated_client):
        """Test update user info"""
        client, _ = authenticated_client

        update_data = {"full_name": "Updated Name"}
        response = await client.patch("/api/v1/users/me", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    async def test_delete_user(self, authenticated_client, test_user_data):
        """Test delete user account"""
        client, _ = authenticated_client

        response = await client.delete("/api/v1/users/me")

        assert response.status_code == 204

        # Verify user can't login anymore
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert login_response.status_code == 401
