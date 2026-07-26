"""Queries for the item management app."""
from src.product_management.schemas import ItemAllergenView, ItemCreate, ItemUpdate
from src.product_management.models import Item, Allergen, MeatType, Category, AppSettings
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

def get_settings(db: Session) -> AppSettings:
    """Return the app's settings row, creating a default one if missing."""
    settings = db.query(AppSettings).first()
    if settings is None:
        settings = AppSettings(
            item_label_en="Item",
            item_label_nl="Item",
            meat_tracking_enabled=False,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, data: "SettingsUpdate") -> AppSettings:
    """Update the app's settings row."""
    settings = get_settings(db)
    settings.item_label_en = data.item_label_en
    settings.item_label_nl = data.item_label_nl
    settings.meat_tracking_enabled = data.meat_tracking_enabled
    db.commit()
    db.refresh(settings)
    return settings