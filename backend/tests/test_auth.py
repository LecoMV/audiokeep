"""
Tests for Authentication Endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.unit
class TestAuthentication:
    """Test authentication endpoints"""

    async def test_register_user(self, client: AsyncClient, test_user_data):
        """Test user registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert data["subscription_tier"] == "free"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register again
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient, test_user_data):
        """Test successful login"""
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user_data):
        """Test login with wrong password"""
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123"
            }
        )

        assert response.status_code == 401

    async def test_refresh_token(self, client: AsyncClient, test_user_data):
        """Test token refresh"""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        tokens = login_response.json()

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": tokens["refresh_token"]}
        )

        assert response.status_code == 200
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
