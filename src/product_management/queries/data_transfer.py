"""Queries for full data export/import (backup and restore)."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.product_management.models import (
    Allergen,
    Category,
    Item,
    MeatType,
    item_allergen,
    item_meat_type,
)
from src.product_management.queries.settings import get_settings
from src.product_management.schemas import ExportData


def export_all_data(db: Session) -> dict:
    """Build a full export of all business data, excluding the admin account."""
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "allergens": [
            {"code": a.code, "description_en": a.description_en, "description_nl": a.description_nl}
            for a in db.query(Allergen).all()
        ],
        "meat_types": [
            {"code": m.code, "description_en": m.description_en, "description_nl": m.description_nl}
            for m in db.query(MeatType).all()
        ],
        "categories": [
            {"code": c.code, "description_en": c.description_en, "description_nl": c.description_nl}
            for c in db.query(Category).all()
        ],
        "items": [
            {
                "name": i.name,
                "category_key": i.category_key,
                "allergen_codes": [a.code for a in i.allergens],
                "meat_type_codes": [m.code for m in i.meat_types],
            }
            for i in db.query(Item).all()
        ],
        "settings": {
            "meat_tracking_enabled": get_settings(db).meat_tracking_enabled,
            "company_name": get_settings(db).company_name,
            "site_title_en": get_settings(db).site_title_en,
            "site_title_nl": get_settings(db).site_title_nl,
            "default_language": get_settings(db).default_language,
        },
    }


def import_all_data(db: Session, data: "ExportData") -> None:
    """Wipe all business data and replace it with the imported data."""
    db.execute(item_allergen.delete())
    db.execute(item_meat_type.delete())
    db.query(Item).delete()
    db.query(Category).delete()
    db.query(MeatType).delete()
    db.query(Allergen).delete()
    db.commit()

    for a in data.allergens:
        db.add(
            Allergen(code=a.code, description_en=a.description_en, description_nl=a.description_nl)
        )

    for m in data.meat_types:
        db.add(
            MeatType(code=m.code, description_en=m.description_en, description_nl=m.description_nl)
        )

    for c in data.categories:
        db.add(
            Category(code=c.code, description_en=c.description_en, description_nl=c.description_nl)
        )

    db.commit()

    allergens_by_code = {a.code: a for a in db.query(Allergen).all()}
    meat_types_by_code = {m.code: m for m in db.query(MeatType).all()}

    for item_data in data.items:
        item = Item(name=item_data.name, category_key=item_data.category_key)
        for code in item_data.allergen_codes:
            if code in allergens_by_code:
                item.allergens.append(allergens_by_code[code])
        for code in item_data.meat_type_codes:
            if code in meat_types_by_code:
                item.meat_types.append(meat_types_by_code[code])
        db.add(item)

    settings = get_settings(db)
    settings.meat_tracking_enabled = data.settings.meat_tracking_enabled
    settings.company_name = data.settings.company_name
    settings.site_title_en = data.settings.site_title_en
    settings.site_title_nl = data.settings.site_title_nl
    settings.default_language = data.settings.default_language

    db.commit()
