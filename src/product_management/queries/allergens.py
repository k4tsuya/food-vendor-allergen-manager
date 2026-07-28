"""Queries for allergens."""

from sqlalchemy.orm import Session

from src.product_management.models import Allergen
from src.product_management.schemas import AllergenCreate, AllergenUpdate


def list_allergens(db: Session) -> list[Allergen]:
    """Query all allergens."""
    return db.query(Allergen).order_by(Allergen.description_en).all()


def get_allergen(db: Session, allergen_id: int) -> Allergen | None:
    """Query a single allergen by id."""
    return db.query(Allergen).filter_by(id=allergen_id).first()


def create_allergen(db: Session, data: "AllergenCreate") -> Allergen | None:
    """Insert a new allergen. Returns None if the code already exists."""
    if db.query(Allergen).filter_by(code=data.code).first():
        return None

    allergen = Allergen(
        code=data.code,
        description_en=data.description_en,
        description_nl=data.description_nl,
    )
    db.add(allergen)
    db.commit()
    db.refresh(allergen)
    return allergen


def update_allergen(db: Session, allergen_id: int, data: "AllergenUpdate") -> Allergen | None:
    """Update an existing allergen's descriptions."""
    allergen = get_allergen(db, allergen_id)
    if allergen is None:
        return None

    allergen.description_en = data.description_en
    allergen.description_nl = data.description_nl
    db.commit()
    db.refresh(allergen)
    return allergen


def delete_allergen(db: Session, allergen_id: int) -> bool:
    """Delete an allergen by id. Returns True if deleted, False if not found."""
    allergen = get_allergen(db, allergen_id)
    if allergen is None:
        return False

    db.delete(allergen)
    db.commit()
    return True
