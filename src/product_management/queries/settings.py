"""Database query functions for app-wide settings.

Settings are stored as a single row (not one-per-key) since there's only
ever one active configuration for the whole app — see AppSettings in
models.py. get_settings() doubles as the seeding mechanism: the first
call after a fresh database creates sensible defaults, rather than
relying on a separate seed function that has to run in exactly the
right order at startup.
"""

from sqlalchemy.orm import Session

from src.product_management.models import AppSettings
from src.product_management.schemas import SettingsUpdate


def get_settings(db: Session) -> AppSettings:
    """Return the app's settings row, creating a default one if missing.

    Always returns a real row — callers never need to handle a None case
    the way they do for get_item/get_allergen/etc., since "settings don't
    exist yet" isn't a valid state for this app to be in.

    Args:
        db: Active database session.

    Returns:
        The app's AppSettings row, creating a default one first if none exists.
    """
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
    """Overwrite all settings fields with the given values.

    Always a full replacement (matches how the admin settings form
    submits every field together, not a partial update).

    Args:
        db: Active database session.
        data: New values for every settings field.

    Returns:
        The updated AppSettings row.
    """
    settings = get_settings(db)
    settings.meat_tracking_enabled = data.meat_tracking_enabled
    settings.company_name = data.company_name
    settings.site_title_en = data.site_title_en
    settings.site_title_nl = data.site_title_nl
    settings.default_language = data.default_language
    db.commit()
    db.refresh(settings)
    return settings
