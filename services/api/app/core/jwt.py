import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from app.core.config import settings

ISSUER = "fluentmeet-api"
AUDIENCE = "fluentmeet-client"

def generate_opaque_token(nbytes: int = 32) -> str:
    """Generate a cryptographically secure URL-safe random string."""
    return secrets.token_urlsafe(nbytes)

def hash_token(raw_token: str) -> str:
    """Hash an opaque token using SHA-256 before database persistence."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

def create_access_token(
    user_id: str,
    session_id: str,
    email: str,
    platform_role: str = "individual",
    expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "sid": session_id,
        "email": email,
        "role": platform_role,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.PyJWTError:
        return None

