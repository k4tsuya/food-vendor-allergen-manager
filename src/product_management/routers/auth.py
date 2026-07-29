"""Authentication routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import (
    create_access_token,
    get_current_admin,
    hash_password,
    limiter,
    verify_password,
)
from src.product_management.models import Admin
from src.product_management.schemas import LoginRequest, PasswordChangeRequest, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an admin and return a JWT access token."""
    admin = db.query(Admin).filter_by(username=credentials.username).first()

    client_host = request.client.host if request.client else "unknown"

    if not admin or not verify_password(credentials.password, admin.hashed_password):
        logger.warning(
            "Failed login attempt for username '%s' from %s",
            credentials.username,
            client_host,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    logger.info("Successful login for '%s' from %s", admin.username, client_host)
    token = create_access_token(admin.username)
    return TokenResponse(access_token=token)


@router.get("/auth/me")
def get_me(current_admin: Admin = Depends(get_current_admin)):
    """Return the currently authenticated admin's username. Used to verify a token is valid."""
    return {"username": current_admin.username}


@router.put("/auth/password")
@limiter.limit("5/minute")
def change_password(
    request: Request,
    data: PasswordChangeRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Change the current admin's password. Requires the current password to be correct."""

    client_host = request.client.host if request.client else "unknown"

    if not verify_password(data.current_password, current_admin.hashed_password):
        logger.warning(
            "Failed login attempt for username '%s' from %s", current_admin.username, client_host
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    current_admin.hashed_password = hash_password(data.new_password)
    db.commit()

    log_admin_action(current_admin, "changed", "password", current_admin.username)
    logger.info("Password changed for '%s'", current_admin.username)

    return {"detail": "Password changed successfully"}
