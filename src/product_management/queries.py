"""Queries for the item management app."""
from src.product_management.schemas import ItemAllergenView, ItemCreate, ItemUpdate
from src.product_management.models import Item, Allergen, MeatType
from sqlalchemy.orm import Session


def list_items(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    exclude_allergens: list[str] | None = None,
    meat_types: list[str] | None = None,
    categories: list[str] | None = None,
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

    if categories:
        query = query.filter(Item.category_key.in_(categories))

    return (
        query.order_by(Item.category_key.asc().nulls_last(), Item.name.asc())
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


def get_item(db: Session, item_id: int) -> Item | None:
    """Query a single item by id."""
    return db.query(Item).filter_by(id=item_id).first()




def create_item(db: Session, data: "ItemCreate") -> tuple[Item, list[str]]:
    """Insert a new item, linking existing allergens and meat types by code."""
    item = Item(name=data.name, category_key=data.category_key)
    warnings: list[str] = []

    for code in data.allergen_codes:
        allergen = db.query(Allergen).filter_by(code=code).first()
        if allergen:
            item.allergens.append(allergen)
        else:
            warnings.append(f"Unknown allergen code '{code}' was skipped.")

    for code in data.meat_type_codes:
        meat_type = db.query(MeatType).filter_by(code=code).first()
        if meat_type:
            item.meat_types.append(meat_type)
        else:
            warnings.append(f"Unknown meat type code '{code}' was skipped.")

    db.add(item)
    db.commit()
    db.refresh(item)
    return item, warnings


def update_item(db: Session, item_id: int, data: "ItemUpdate") -> tuple[Item, list[str]] | None:
    """Update an existing item's fields, allergens, and meat types."""
    item = get_item(db, item_id)
    if item is None:
        return None

    item.name = data.name
    item.category_key = data.category_key

    warnings: list[str] = []
    resolved_allergens = []
    for code in data.allergen_codes:
        allergen = db.query(Allergen).filter_by(code=code).first()
        if allergen:
            resolved_allergens.append(allergen)
        else:
            warnings.append(f"Unknown allergen code '{code}' was skipped.")
    item.allergens = resolved_allergens

    resolved_meat_types = []
    for code in data.meat_type_codes:
        meat_type = db.query(MeatType).filter_by(code=code).first()
        if meat_type:
            resolved_meat_types.append(meat_type)
        else:
            warnings.append(f"Unknown meat type code '{code}' was skipped.")
    item.meat_types = resolved_meat_types

    db.commit()
    db.refresh(item)
    return item, warnings

def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item by id. Returns True if deleted, False if not found."""
    item = get_item(db, item_id)
    if item is None:
        return False

    db.delete(item)
    db.commit()
    return True