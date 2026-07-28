"""Queries for meat types."""

from sqlalchemy.orm import Session

from src.product_management.models import MeatType
from src.product_management.schemas import MeatTypeCreate, MeatTypeUpdate


def list_meat_types(db: Session) -> list[MeatType]:
    """Query all meat types."""
    return db.query(MeatType).order_by(MeatType.description_en).all()


def get_meat_type(db: Session, meat_type_id: int) -> MeatType | None:
    """Query a single meat type by id."""
    return db.query(MeatType).filter_by(id=meat_type_id).first()


def create_meat_type(db: Session, data: "MeatTypeCreate") -> MeatType | None:
    """Insert a new meat type. Returns None if the code already exists."""
    if db.query(MeatType).filter_by(code=data.code).first():
        return None

    meat_type = MeatType(
        code=data.code,
        description_en=data.description_en,
        description_nl=data.description_nl,
    )
    db.add(meat_type)
    db.commit()
    db.refresh(meat_type)
    return meat_type


def update_meat_type(db: Session, meat_type_id: int, data: "MeatTypeUpdate") -> MeatType | None:
    """Update an existing meat type's descriptions."""
    meat_type = get_meat_type(db, meat_type_id)
    if meat_type is None:
        return None

    meat_type.description_en = data.description_en
    meat_type.description_nl = data.description_nl
    db.commit()
    db.refresh(meat_type)
    return meat_type


def delete_meat_type(db: Session, meat_type_id: int) -> bool:
    """Delete a meat type by id. Returns True if deleted, False if not found."""
    meat_type = get_meat_type(db, meat_type_id)
    if meat_type is None:
        return False

    db.delete(meat_type)
    db.commit()
    return True
