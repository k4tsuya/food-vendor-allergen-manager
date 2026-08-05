"""Full data export/import — backup and restore for a vendor's business data.

Export produces a single JSON snapshot of everything except the admin
account (items, allergens, meat types, categories, settings). Import
does a full replace: it wipes existing business data and rebuilds it
from the imported file. This is deliberately simple (no merge/upsert
logic) — see README's Backup & Restore section for the reasoning.

The admin account is never touched by either operation, by design —
restoring a vendor's product data should never change who can log in.
"""

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
    """Returns a plain dict (not a Pydantic model instance) because this is
    handed directly to FastAPI's response_model=ExportData for validation
    and serialization — building the dict here keeps this function
    testable/usable independent of the HTTP layer.

    Args:
        db: Active database session.

    Returns:
        A dict matching the ExportData schema shape: exported_at,
        allergens, meat_types, categories, items, and settings.
    """
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
    """Deletion order matters and is NOT arbitrary:

    1. Association tables (item_allergen, item_meat_type) are cleared
       FIRST, explicitly, via raw table deletes. This is required because
       db.query(Item).delete() below is a *bulk* delete — it issues a
       direct DELETE FROM items at the database level and does NOT
       cascade to association tables the way deleting ORM objects
       one-by-one would. Skipping this step leaves orphaned association
       rows, which then collide once new items reuse old ids (this was
       a real bug caught during development).

    2. Item is deleted before Category/MeatType/Allergen, since items
       reference them — deleting a referenced row first would violate
       the relationship at the database level.

    3. New reference data (allergens, meat types, categories) is
       inserted and flushed (not committed) BEFORE new items are built,
       so they have real database-assigned ids to look up and link —
       without ending the transaction, so an error afterward can still
       roll back everything, including this step.

    The whole operation runs in a single transaction: nothing is
    committed until every step succeeds, and any error rolls back
    everything, so a failure partway through can never leave the
    database in a mixed old/new state.

    The admin account (Admin table) is never touched here.

    Args:
        db: Active database session.
        data: The full dataset to import, matching the ExportData schema
            (as produced by export_all_data, or a hand-built equivalent).

    Returns:
        None.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: Re-raised after rolling back the
            entire operation. The caller (routers/data.py) is responsible
            for translating this into an appropriate HTTP response.
    """
    try:
        db.execute(item_allergen.delete())
        db.execute(item_meat_type.delete())
        db.query(Item).delete()
        db.query(Category).delete()
        db.query(MeatType).delete()
        db.query(Allergen).delete()

        for a in data.allergens:
            db.add(
                Allergen(
                    code=a.code, description_en=a.description_en, description_nl=a.description_nl
                )
            )

        for m in data.meat_types:
            db.add(
                MeatType(
                    code=m.code, description_en=m.description_en, description_nl=m.description_nl
                )
            )

        for c in data.categories:
            db.add(
                Category(
                    code=c.code, description_en=c.description_en, description_nl=c.description_nl
                )
            )

        # flush (not commit) — assigns real ids to the new rows above so
        # they can be looked up below, without ending the transaction.
        db.flush()

        # Built once, outside the items loop below — looking up each
        # item's allergens/meat types one at a time here would
        # reintroduce the same N+1 pattern fixed in queries/items.py's
        # create_item/update_item.
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

        # get_settings() has its own internal commit, but only if no
        # settings row exists yet — in practice a row always already
        # exists by this point (created at app startup), so this call
        # is expected to just read, not commit, keeping it inside this
        # same transaction. Documented here since it's a real assumption,
        # not something enforced by the code itself.
        settings = get_settings(db)
        settings.meat_tracking_enabled = data.settings.meat_tracking_enabled
        settings.company_name = data.settings.company_name
        settings.site_title_en = data.settings.site_title_en
        settings.site_title_nl = data.settings.site_title_nl
        settings.default_language = data.settings.default_language

        db.commit()
    except Exception:
        db.rollback()
        raise
