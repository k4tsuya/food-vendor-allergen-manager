"""Database query functions for allergens.

Allergens are reference data — the fixed EU/NVWA-regulated list, managed
through the admin area rather than defined in code. Items link to allergens
via a many-to-many relationship (see models.py: item_allergen table).
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.product_management.models import Allergen
from src.product_management.schemas import AllergenCreate, AllergenUpdate


def list_allergens(db: Session) -> list[Allergen]:
    """Retrieve all allergens, sorted by English description.

    Sorted (not just returned in insertion order) so both the public
    matrix's allergen key and the admin table show a predictable order.

    Args:
        db: Active database session.

    Returns:
        All Allergen rows, ordered by description_en ascending.
    """
    return db.query(Allergen).order_by(Allergen.description_en).all()


def get_allergen(db: Session, allergen_id: int) -> Allergen | None:
    """Retrieve a single allergen by ID.

    Args:
        db: Active database session.
        allergen_id: Primary key of the allergen to fetch.

    Returns:
        The matching Allergen, or None if no allergen has this id.
    """
    return db.query(Allergen).filter_by(id=allergen_id).first()


def create_allergen(db: Session, data: "AllergenCreate") -> Allergen | None:
    """Create a new allergen, or None if the code already exists.

    `code` has a unique constraint at the database level, so this checks
    for an existing match first and returns None rather than letting the
    insert fail with a raw IntegrityError. It also catches the rare race
    condition where a duplicate code is inserted by another request
    between this function's existence check and its own commit — the
    database's unique constraint blocks that insert regardless; this
    just makes sure the failure is handled cleanly instead of crashing.
    The router turns None into a clean 400 response either way.

    Args:
        db: Active database session.
        data: The new allergen's code and English/Dutch descriptions.

    Returns:
        The created Allergen, or None if the code already exists
        (whether caught by the initial check or the race-condition
        fallback).
    """
    if db.query(Allergen).filter_by(code=data.code).first():
        return None

    allergen = Allergen(
        code=data.code,
        description_en=data.description_en,
        description_nl=data.description_nl,
    )
    db.add(allergen)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    db.refresh(allergen)
    return allergen


def update_allergen(db: Session, allergen_id: int, data: "AllergenUpdate") -> Allergen | None:
    """Update an allergen's descriptions, or None if it doesn't exist.

    `code` is intentionally not updatable here (see the AllergenUpdate
    schema — it has no code field). Code is used as a stable identifier
    for filtering (?exclude_allergens=gluten) and for looking up the
    matching icon file (static/icons/allergens/gluten.png); changing it
    after creation would silently break both. Renaming a code is a
    delete-and-recreate, not an update.

    Args:
        db: Active database session.
        allergen_id: Primary key of the allergen to update.
        data: New English/Dutch descriptions to apply.

    Returns:
        The updated Allergen, or None if no allergen with this id exists.
    """
    allergen = get_allergen(db, allergen_id)
    if allergen is None:
        return None

    allergen.description_en = data.description_en
    allergen.description_nl = data.description_nl
    db.commit()
    db.refresh(allergen)
    return allergen


def delete_allergen(db: Session, allergen_id: int) -> bool:
    """Delete an allergen, returning whether it existed.

    Deleting this removes the corresponding rows from the item_allergen
    association table automatically — SQLAlchemy cascades this for
    single-object deletes, unlike the bulk-delete case handled explicitly
    in queries/data_transfer.py's import_all_data.

    Args:
        db: Active database session.
        allergen_id: Primary key of the allergen to delete.

    Returns:
        True if an allergen was found and deleted, False otherwise.
    """
    allergen = get_allergen(db, allergen_id)
    if allergen is None:
        return False

    db.delete(allergen)
    db.commit()
    return True
