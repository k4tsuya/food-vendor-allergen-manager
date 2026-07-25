"""Queries for the item management app."""
from src.product_management.schemas import ItemAllergenView
from src.product_management.models import Item, Allergen
from sqlalchemy.orm import Session


def list_items(db: Session, limit: int = 50, offset: int = 0) -> list[Item]:
    """Query all items."""
    return db.query(Item).limit(limit).offset(offset).all()

def list_allergens(db: Session) -> list[Allergen]:
    """Query all allergens."""
    return db.query(Allergen).order_by(Allergen.description_en).all()

def get_gluten_free_items(db: Session, limit: int = 50, offset: int = 0) -> list[Item]:
    """Query all gluten-free items."""
    return (db.query(Item).filter(~Item.allergens.any(Allergen.code == "gluten")).limit(limit).offset(offset).all())

def pdf_list_items(db: Session) -> list[ItemAllergenView]:
    """List all items with their allergens."""
    items = list_items(db)

    return [
        ItemAllergenView(
            name=i.name,
            allergens=[a.code for a in i.allergens],
        )
        for i in items
    ]