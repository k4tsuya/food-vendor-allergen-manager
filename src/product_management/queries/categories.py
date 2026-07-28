"""Queries for categories."""

from sqlalchemy.orm import Session

from src.product_management.models import Category
from src.product_management.schemas import CategoryCreate, CategoryUpdate


def list_categories(db: Session) -> list[Category]:
    """Query all categories."""
    return db.query(Category).order_by(Category.description_en).all()


def get_category(db: Session, category_id: int) -> Category | None:
    """Query a single category by id."""
    return db.query(Category).filter_by(id=category_id).first()


def create_category(db: Session, data: "CategoryCreate") -> Category | None:
    """Insert a new category. Returns None if the code already exists."""
    if db.query(Category).filter_by(code=data.code).first():
        return None

    category = Category(
        code=data.code,
        description_en=data.description_en,
        description_nl=data.description_nl,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, data: "CategoryUpdate") -> Category | None:
    """Update an existing category's descriptions."""
    category = get_category(db, category_id)
    if category is None:
        return None

    category.description_en = data.description_en
    category.description_nl = data.description_nl
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category by id. Returns True if deleted, False if not found."""
    category = get_category(db, category_id)
    if category is None:
        return False

    db.delete(category)
    db.commit()
    return True
