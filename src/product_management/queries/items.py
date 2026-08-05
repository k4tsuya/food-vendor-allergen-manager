"""Database query functions for items.

Items are the central resource in this app — each item has a name, an
optional category, and many-to-many relationships to Allergen and MeatType.
Functions here handle both read access (with filtering/pagination for the
public matrix and admin table) and the CRUD operations exposed by the
authenticated admin endpoints.
"""

from sqlalchemy.orm import Session, selectinload

from src.product_management.models import Allergen, Item, MeatType
from src.product_management.schemas import ItemAllergenView, ItemCreate, ItemResponse, ItemUpdate


def list_items(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    exclude_allergens: list[str] | None = None,
    meat_types: list[str] | None = None,
    categories: list[str] | None = None,
) -> list[ItemResponse]:
    """Filters are combined with AND logic across categories (search AND
    exclude_allergens AND meat_types AND categories), but within a single
    filter, matching is OR-based — e.g. meat_types=["pork","beef"] returns
    items containing pork OR beef, not both.

    Uses selectinload for `allergens` and `meat_types` to avoid the N+1
    query problem: without it, SQLAlchemy would lazily fire one extra
    query per item per relationship when the response is serialized
    (e.g. 50 items would mean ~101 queries instead of 3).

    Args:
        db: Active database session.
        limit: Max number of items to return (pagination).
        offset: Number of items to skip (pagination).
        search: Case-insensitive substring match on item name, if given.
        exclude_allergens: Allergen codes to exclude; an item is excluded
            if it contains ANY of these.
        meat_types: Meat type codes to filter by; an item matches if it
            contains ANY of these.
        categories: Category keys to filter by (OR match).

    Returns:
        A list of Item objects, ordered by category (nulls last), then name.
    """
    query = db.query(Item).options(
        selectinload(Item.allergens),
        selectinload(Item.meat_types),
    )

    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))

    if exclude_allergens:
        for code in exclude_allergens:
            query = query.filter(~Item.allergens.any(Allergen.code == code))

    if meat_types:
        query = query.filter(Item.meat_types.any(MeatType.code.in_(meat_types)))

    if categories:
        query = query.filter(Item.category_key.in_(categories))

    items = (
        query.order_by(
            Item.category_key.asc().nulls_last(),
            Item.name.asc(),
        )
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [ItemResponse.model_validate(item) for item in items]


def pdf_list_items(db: Session) -> list[ItemAllergenView]:
    """Deliberately calls list_items(db) with no filters/pagination arguments,
    so the PDF always includes the full item list regardless of whatever
    filters happen to be active on the public matrix page at the time.

    Args:
        db: Active database session.

    Returns:
        One ItemAllergenView per item, in the same order list_items returns.
    """
    items = list_items(db)

    return [
        ItemAllergenView(
            name=i.name,
            allergens=[a.code for a in i.allergens],
        )
        for i in items
    ]


def get_item(db: Session, item_id: int) -> Item | None:
    """Args:
        db: Active database session.
        item_id: Primary key of the item to fetch.

    Returns:
        The matching Item (allergens/meat_types eager-loaded), or None if
        not found — callers (update_item, delete_item) turn None into a 404.
    """
    return (
        db.query(Item)
        .options(selectinload(Item.allergens), selectinload(Item.meat_types))
        .filter_by(id=item_id)
        .first()
    )


def _resolve_allergens(db: Session, codes: list[str]) -> tuple[list[Allergen], list[str]]:
    """Exists to avoid an N+1 pattern: looking up each code with its own
    db.query(...).filter_by(code=code).first() inside a loop would issue
    one query per code (e.g. 5 allergens = 5 queries). Instead, this fetches
    every matching row in one query using `IN (...)`, then does the
    code -> Allergen matching in memory.

    Args:
        db: Active database session.
        codes: Allergen codes to resolve. May be empty.

    Returns:
        A tuple of (matched Allergen objects; warning strings for any
        codes that didn't match an existing Allergen).
    """
    if not codes:
        return [], []

    found = db.query(Allergen).filter(Allergen.code.in_(codes)).all()
    found_by_code = {a.code: a for a in found}

    resolved = []
    warnings = []
    for code in codes:
        if code in found_by_code:
            resolved.append(found_by_code[code])
        else:
            warnings.append(f"Unknown allergen code '{code}' was skipped.")

    return resolved, warnings


def _resolve_meat_types(db: Session, codes: list[str]) -> tuple[list[MeatType], list[str]]:
    """Same N+1-avoidance reasoning as _resolve_allergens — see that
    function's docstring for the full explanation.

    Args:
        db: Active database session.
        codes: Meat type codes to resolve. May be empty.

    Returns:
        A tuple of (matched MeatType objects, warning strings for any
        codes that didn't match an existing MeatType).
    """
    if not codes:
        return [], []

    found = db.query(MeatType).filter(MeatType.code.in_(codes)).all()
    found_by_code = {m.code: m for m in found}

    resolved = []
    warnings = []
    for code in codes:
        if code in found_by_code:
            resolved.append(found_by_code[code])
        else:
            warnings.append(f"Unknown meat type code '{code}' was skipped.")

    return resolved, warnings


def create_item(db: Session, data: "ItemCreate") -> tuple[Item, list[str]]:
    """Unknown allergen/meat type codes are silently skipped rather than
    rejecting the whole request — a deliberate design choice: the admin
    UI only offers valid codes via checkboxes, so this path only matters
    for direct API access, where a typo'd code shouldn't block creating
    an otherwise-valid item. Skipped codes are collected into a warnings
    list so the caller can inform the user rather than failing silently.

    Args:
        db: Active database session.
        data: New item's name, optional category_key, and allergen/meat
            type codes to link.

    Returns:
        A tuple of (the created Item, a list of warning strings for any
        codes that didn't match an existing Allergen/MeatType).
    """
    allergens, allergen_warnings = _resolve_allergens(db, data.allergen_codes)
    meat_types, meat_warnings = _resolve_meat_types(db, data.meat_type_codes)

    item = Item(name=data.name, category_key=data.category_key)
    item.allergens = allergens
    item.meat_types = meat_types

    db.add(item)
    db.commit()
    db.refresh(item)
    return item, allergen_warnings + meat_warnings


def update_item(db: Session, item_id: int, data: "ItemUpdate") -> tuple[Item, list[str]] | None:
    """This is a full replacement, not a merge: whatever allergen/meat codes
    are submitted become the item's complete set, replacing whatever it
    had before (matching how the admin edit form works — it always
    submits the full current selection, not a diff).

    Args:
        db: Active database session.
        item_id: Primary key of the item to update.
        data: New name, category_key, and full allergen/meat type code
            lists to replace the item's current ones with.

    Returns:
        None if the item doesn't exist (caller should respond 404).
        Otherwise a tuple of (updated Item, warnings for unknown codes),
        same shape as create_item.
    """
    item = get_item(db, item_id)
    if item is None:
        return None

    item.name = data.name
    item.category_key = data.category_key  # type: ignore[assignment]

    allergens, allergen_warnings = _resolve_allergens(db, data.allergen_codes)
    meat_types, meat_warnings = _resolve_meat_types(db, data.meat_type_codes)

    item.allergens = allergens
    item.meat_types = meat_types

    db.commit()
    db.refresh(item)
    return item, allergen_warnings + meat_warnings


def delete_item(db: Session, item_id: int) -> bool:
    """Args:
        db: Active database session.
        item_id: Primary key of the item to delete.

    Returns:
        True if an item was found and deleted, False if no item with
        that id existed (caller should respond 404, not treat this as
        a server error).
    """
    item = get_item(db, item_id)
    if item is None:
        return False

    db.delete(item)
    db.commit()
    return True
