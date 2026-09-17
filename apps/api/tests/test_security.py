import pytest
from app.core.security import (
    UserRole,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.exceptions import AuthenticationError


def test_password_hashing():
    """Test bcrypt hashing and verification."""
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_flow():
    """Test JWT access and refresh token generation and decoding."""
    user_id = "test-user-uuid-1234"
    token = create_access_token(subject=user_id, role=UserRole.STUDENT)
    decoded = decode_token(token)
    assert decoded["sub"] == user_id
    assert decoded["role"] == UserRole.STUDENT
    assert decoded["type"] == "access"

    refresh_token, jti, expire = create_refresh_token(subject=user_id)
    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh["sub"] == user_id
    assert decoded_refresh["type"] == "refresh"
    assert decoded_refresh["jti"] == jti


def test_invalid_jwt_token():
    """Test decoding an invalid token raises AuthenticationError."""
    with pytest.raises(AuthenticationError):
        decode_token("invalid.token.signature")
