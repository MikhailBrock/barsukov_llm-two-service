from datetime import datetime, timezone

from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings


def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except JWTError:
        raise ValueError("Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise ValueError("Token missing 'sub' field")

    return payload
