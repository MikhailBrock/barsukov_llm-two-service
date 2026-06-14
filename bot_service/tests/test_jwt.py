import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt

from app.core.jwt import decode_and_validate
from app.core.config import settings


def make_token(sub: str = "1", role: str = "user", expired: bool = False) -> str:
    now = datetime.now(timezone.utc)
    exp = now - timedelta(seconds=1) if expired else now + timedelta(hours=1)
    payload = {"sub": sub, "role": role, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def test_valid_token_decoded():
    token = make_token(sub="42", role="user")
    payload = decode_and_validate(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "user"


def test_garbage_token_raises():
    with pytest.raises(ValueError):
        decode_and_validate("garbage.not.a.token")


def test_expired_token_raises():
    token = make_token(expired=True)
    with pytest.raises(ValueError, match="expired"):
        decode_and_validate(token)
