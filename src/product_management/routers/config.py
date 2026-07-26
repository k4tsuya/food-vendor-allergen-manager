"""Routes for app-wide settings."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.schemas import SettingsResponse, SettingsUpdate
from src.product_management.queries import get_settings, update_settings

router = APIRouter()


@router.get("/config", response_model=SettingsResponse)
def get_config(db: Session = Depends(get_db)):
    """Return current app settings. Public — the frontend needs this without logging in."""
    return get_settings(db)


@router.put("/config", response_model=SettingsResponse)
def update_config(
    data: SettingsUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update app settings. Requires authentication."""
    return update_settings(db, data)