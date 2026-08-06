"""Database query functions for meat types.

Meat types are optional reference data (see core/config.py and the
AppSettings.meat_tracking_enabled flag) — this table always exists, but
stays empty and unused when the feature is disabled. Same code +
description shape and CRUD pattern as allergens; the admin UI reuses the
same component (CodeLabelAdmin) for both.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.product_management.models import MeatType
from src.product_management.schemas import MeatTypeCreate, MeatTypeUpdate


def list_meat_types(db: Session) -> list[MeatType]:
    """Retrieve all meat types, sorted by English description.

    Sorted for the same reason as list_allergens: a predictable order
    for both the matrix's meat-type columns and the admin table.

    Args:
        db: Active database session.

    Returns:
        All MeatType rows, ordered by description_en ascending.
    """
    return db.query(MeatType).order_by(MeatType.description_en).all()


def get_meat_type(db: Session, meat_type_id: int) -> MeatType | None:
    """Args:
        db: Active database session.
        meat_type_id: Primary key of the meat type to fetch.

    Returns:
        The matching MeatType, or None if no meat type has this id.
    """
    return db.query(MeatType).filter_by(id=meat_type_id).first()


def create_meat_type(db: Session, data: "MeatTypeCreate") -> MeatType | None:
    """Create a new meat type, or None if the code already exists.

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
        data: The new meat type's code and English/Dutch descriptions.

    Returns:
        The created MeatType, or None if the code already exists
        (whether caught by the initial check or the race-condition
        fallback).
    """
    if db.query(MeatType).filter_by(code=data.code).first():
        return None

    meat_type = MeatType(
        code=data.code,
        description_en=data.description_en,
        description_nl=data.description_nl,
    )
    db.add(meat_type)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    db.refresh(meat_type)
    return meat_type


def update_meat_type(db: Session, meat_type_id: int, data: "MeatTypeUpdate") -> MeatType | None:
    """Update a meat type's descriptions, or None if it doesn't exist.

    `code` is intentionally not updatable here (see the MeatTypeUpdate
    schema — it has no code field). Code is used as a stable identifier
    for filtering (?meat_types=pork) and for looking up the matching
    icon file (static/icons/meat/pork.png); changing it after creation
    would silently break both. Renaming a code is a delete-and-recreate,
    not an update.

    Args:
        db: Active database session.
        meat_type_id: Primary key of the meat type to update.
        data: New English/Dutch descriptions to apply.

    Returns:
        The updated MeatType, or None if no meat type with this id exists.
    """
    meat_type = get_meat_type(db, meat_type_id)
    if meat_type is None:
        return None

    meat_type.description_en = data.description_en
    meat_type.description_nl = data.description_nl
    db.commit()
    db.refresh(meat_type)
    return meat_type


def delete_meat_type(db: Session, meat_type_id: int) -> bool:
    """Delete a meat type, returning whether it existed.

    Deleting this removes the corresponding rows from the item_meat_type
    association table automatically — SQLAlchemy cascades this for
    single-object deletes, unlike the bulk-delete case handled explicitly
    in queries/data_transfer.py's import_all_data.

    Args:
        db: Active database session.
        meat_type_id: Primary key of the meat type to delete.

    Returns:
        True if a meat type was found and deleted, False otherwise.
    """
    meat_type = get_meat_type(db, meat_type_id)
    if meat_type is None:
        return False

    db.delete(meat_type)
    db.commit()
    return True
