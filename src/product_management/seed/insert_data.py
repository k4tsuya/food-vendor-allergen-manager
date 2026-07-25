"""Module for inserting data into the database."""

from sqlalchemy.orm import Session

from src.product_management.core.config import ENABLE_MEAT_TRACKING
from src.product_management.models import Allergen, MeatType, Item
from src.product_management.seed.allergens import ALLERGENS
from src.product_management.seed.meat_types import MEAT_TYPES


SAMPLE_ITEMS = {
    "Frikandel": ["gluten", "soy", "mustard"],
    "Kroket": ["gluten", "milk"],
    "Bread": ["gluten"],
    "Fishstick": ["fish"],
}

SAMPLE_ITEM_MEAT_TYPES = {
    "Frikandel": ["pork", "beef"],
    "Kroket": ["beef"],
    "Bread": [],
    "Fishstick": ["fish"],
}

SAMPLE_ITEM_CATEGORIES = {
    "Frikandel": "Snacks",
    "Kroket": "Snacks",
    "Bread": "Bakery",
    "Fishstick": "Snacks",
}

def load_allergens(db: Session) -> None:
    """Insert allergens into the db if they don't exist."""
    for code, data in ALLERGENS.items():
        en = data["en"]
        nl = data["nl"]
        if db.query(Allergen).filter_by(code=code).first():
            continue

        db.add(
            Allergen(
                code=code,
                description_en=en,
                description_nl=nl,
            )
        )

    db.commit()


def load_meat_types(db: Session) -> None:
    """Insert meat types into the db if they don't exist."""
    for code, data in MEAT_TYPES.items():
        en = data["en"]
        nl = data["nl"]
        if db.query(MeatType).filter_by(code=code).first():
            continue

        db.add(
            MeatType(
                code=code,
                description_en=en,
                description_nl=nl,
            )
        )

    db.commit()


def load_items(db: Session) -> None:
    """Insert items into the db with the corresponding allergens."""

    data_source: dict = SAMPLE_ITEMS
    meat_data_source: dict = SAMPLE_ITEM_MEAT_TYPES
    category_data_source: dict = SAMPLE_ITEM_CATEGORIES

    allergens_by_code = {
        allergen.code: allergen
        for allergen in db.query(Allergen).all()
    }

    meat_types_by_code = {}
    if ENABLE_MEAT_TRACKING:
        meat_types_by_code = {
            meat_type.code: meat_type
            for meat_type in db.query(MeatType).all()
        }

    # To use real data, create items.py in the same directory of this module
    # and create a JSON structure like SAMPLE_ITEMS.
    try:
        from src.product_management.seed.items import items
        data_source = items
    except ImportError:
        print("Real data not found. Loading sample data...")

    # To use real meat type data, create item_meat.py in the same
    # directory as this module, with the same structure as SAMPLE_ITEM_MEAT_TYPES.
    try:
        from src.product_management.seed.item_meat import item_meat
        meat_data_source = item_meat
    except ImportError:
        pass

    try:
        from src.product_management.seed.item_categories import item_categories
        category_data_source = item_categories
    except ImportError:
        pass

    for name, allergen_codes in data_source.items():
        if db.query(Item).filter_by(name=name).first():
            continue

        item = Item(name=name)

        for code in allergen_codes:
            item.allergens.append(allergens_by_code[code])

        if ENABLE_MEAT_TRACKING:
            meat_codes = meat_data_source.get(name, [])
            for code in meat_codes:
                item.meat_types.append(meat_types_by_code[code])

        db.add(item)

    db.commit()