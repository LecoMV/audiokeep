"""
Tests for Security Functions
"""
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_token_pair
)


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_password_hashing(self):
        """Test password can be hashed"""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long

    def test_password_verification(self):
        """Test password verification"""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_same_password(self):
        """Test same password creates different hashes (salt)"""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 50

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_refresh_token(data)

        assert token is not None
        assert len(token) > 50

    def test_decode_valid_token(self):
        """Test decoding valid token"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)

        assert payload is None

    def test_token_pair_creation(self):
        """Test creating access and refresh token pair"""
        tokens = create_token_pair("user123", "test@example.com")

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

        # Verify both tokens
        access_payload = decode_token(tokens["access_token"])
        refresh_payload = decode_token(tokens["refresh_token"])

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
        assert access_payload["sub"] == "user123"
        assert refresh_payload["sub"] == "user123"

    def test_token_expiration_field(self):
        """Test tokens have expiration field"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        payload = decode_token(token)

        assert "exp" in payload
        assert payload["exp"] > 0
