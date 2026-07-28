"""Queries for app-wide settings."""

from sqlalchemy.orm import Session

from src.product_management.models import AppSettings
from src.product_management.schemas import SettingsUpdate


def get_settings(db: Session) -> AppSettings:
    """Return the app's settings row, creating a default one if missing."""
    settings = db.query(AppSettings).first()
    if settings is None:
        settings = AppSettings(
            meat_tracking_enabled=False,
            company_name="Your Company Name",
            site_title_en="Allergen Check",
            site_title_nl="Allergenen Check",
            default_language="nl",
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, data: "SettingsUpdate") -> AppSettings:
    """Update the app's settings row."""
    settings = get_settings(db)
    settings.meat_tracking_enabled = data.meat_tracking_enabled
    settings.company_name = data.company_name
    settings.site_title_en = data.site_title_en
    settings.site_title_nl = data.site_title_nl
    settings.default_language = data.default_language
    db.commit()
    db.refresh(settings)
    return settings
