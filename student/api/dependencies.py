"""Use this to protect routes and get current user + role from JWT."""
import time
from collections import defaultdict
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.settings import settings

security = HTTPBearer()

# In-memory rate limit: key -> list of request timestamps (pruned to last 60s)
_rate_limit_store: dict = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds


def _get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def rate_limit_auth(request: Request) -> None:
    """Dependency: limit auth endpoints per IP per minute. Raises 429 if exceeded."""
    ip = _get_client_ip(request)
    key = f"auth:{ip}"
    now = time.time()
    # Prune old entries
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[key]) >= settings.RATE_LIMIT_AUTH_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many attempts. Try again in a minute.")
    _rate_limit_store[key].append(now)
    return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Decode JWT and return user payload (userid, email, role, username)."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        userid = payload.get("sub")
        role = payload.get("role")
        if not userid:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(allowed_roles: list[str]):
    """Dependency factory: restrict route to specific roles."""

    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Role '{user.get('role')}' not allowed")
        return user

    return role_checker
