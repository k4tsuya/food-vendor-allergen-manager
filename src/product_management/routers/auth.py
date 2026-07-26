"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db
from src.product_management.core.security import verify_password, create_access_token, get_current_admin, limiter
from src.product_management.models import Admin
from src.product_management.schemas import LoginRequest, TokenResponse
from fastapi import Request



router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an admin and return a JWT access token."""
    admin = db.query(Admin).filter_by(username=credentials.username).first()

    if not admin or not verify_password(credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(admin.username)
    return TokenResponse(access_token=token)


@router.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an admin and return a JWT access token."""
    admin = db.query(Admin).filter_by(username=credentials.username).first()

    if not admin or not verify_password(credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(admin.username)
    return TokenResponse(access_token=token)

@router.get("/auth/me")
def get_me(current_admin: Admin = Depends(get_current_admin)):
    """Return the currently authenticated admin's username. Used to verify a token is valid."""
    return {"username": current_admin.username}