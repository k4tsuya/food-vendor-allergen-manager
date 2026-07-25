"""Queries for the item management app."""
from src.product_management.schemas import ItemAllergenView
from src.product_management.models import Item, Allergen, MeatType
from sqlalchemy.orm import Session


def list_items(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    exclude_allergens: list[str] | None = None,
    meat_types: list[str] | None = None,
) -> list[Item]:
    """Query items, paginated and optionally filtered."""
    query = db.query(Item)

    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))

    if exclude_allergens:
        for code in exclude_allergens:
            query = query.filter(~Item.allergens.any(Allergen.code == code))

    if meat_types:
        query = query.filter(Item.meat_types.any(MeatType.code.in_(meat_types)))

    return (
        query.order_by(Item.category.asc().nulls_last(), Item.name.asc())
        .limit(limit)
        .offset(offset)
        .all()
    )

def list_allergens(db: Session) -> list[Allergen]:
    """Query all allergens."""
    return db.query(Allergen).order_by(Allergen.description_en).all()

def get_gluten_free_items(db: Session, limit: int = 50, offset: int = 0) -> list[Item]:
    """Query all gluten-free items."""
    return (db.query(Item).filter(~Item.allergens.any(Allergen.code == "gluten")).limit(limit).offset(offset).all())


def list_meat_types(db: Session) -> list[MeatType]:
    """Query all meat types."""
    return db.query(MeatType).order_by(MeatType.description_en).all()

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