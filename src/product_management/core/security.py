"""Password hashing and JWT token utilities."""

import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db
from src.product_management.models import Admin

logger = logging.getLogger("security")

limiter = Limiter(key_func=get_remote_address)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in .env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage.

    Args:
        plain_password: The password to hash, in plaintext.

    Returns:
        The bcrypt hash, safe to store in the database.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored hash.

    Args:
        plain_password: The password to verify, in plaintext.
        hashed_password: The stored bcrypt hash to check against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str) -> str:
    """Create a signed JWT containing the given username, with an expiry.

    Args:
        username: The admin username to embed in the token's "sub" claim.

    Returns:
        The signed JWT as a string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Decode a JWT and return the username, or None if invalid/expired.

    Logs whether a failure was due to expiry or an invalid/tampered
    token, since that distinction is useful for security monitoring
    even though callers always just get None either way — an attacker
    probing with garbage tokens looks different in the logs than a
    normal user whose session simply timed out.

    Args:
        token: The JWT to decode and verify.

    Returns:
        The username from the token's "sub" claim, or None if the
        token is invalid, tampered with, or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except ExpiredSignatureError:
        logger.info("Token expired")
        return None
    except JWTError:
        logger.warning("Invalid or tampered token received")
        return None


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    """Verify the JWT and return the current admin, or reject the request.

    Used as a FastAPI dependency on every protected route, so a route
    only needs to declare `current_admin: Admin = Depends(get_current_admin)`
    to require a valid, currently-existing admin.

    Args:
        token: The bearer token from the Authorization header, injected
            by FastAPI via oauth2_scheme.
        db: Database session, injected by FastAPI.

    Returns:
        Admin: The authenticated admin matching the token's username.

    Raises:
        HTTPException: 401 if the token is missing, invalid, or expired,
            or if the username it contains no longer matches an admin
            (e.g. deleted after the token was issued).
    """
    username = decode_access_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = db.query(Admin).filter_by(username=username).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
        )

    return admin
