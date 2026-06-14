import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_hash_not_equal_plain():
    hashed = hash_password("secret123")
    assert hashed != "secret123"


def test_verify_correct_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("secret123")
    assert verify_password("wrongpass", hashed) is False


def test_create_and_decode_token():
    token = create_access_token(sub="42", role="user")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload


def test_invalid_token_raises():
    from app.core.exceptions import InvalidTokenError
    with pytest.raises(InvalidTokenError):
        decode_token("not.a.valid.token")
