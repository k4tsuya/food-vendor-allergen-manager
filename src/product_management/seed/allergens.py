"""Module for the allergen data."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ICON_DIR = BASE_DIR / "static" / "icons" / "allergens"

ALLERGENS = {
    "gluten": {"en": "Gluten", "nl": "Gluten", "icon": ICON_DIR / "gluten.png"},
    "crustaceans": {"en": "Crustaceans", "nl": "Schaaldier", "icon": ICON_DIR / "crustaceans.png"},
    "eggs": {"en": "Eggs", "nl": "Ei", "icon": ICON_DIR / "eggs.png"},
    "fish": {"en": "Fish", "nl": "Vis", "icon": ICON_DIR / "fish.png"},
    "peanuts": {"en": "Peanuts", "nl": "Pinda's", "icon": ICON_DIR / "peanuts.png"},
    "soy": {"en": "Soybeans", "nl": "Soja", "icon": ICON_DIR / "soy.png"},
    "milk": {"en": "Milk", "nl": "Melk", "icon": ICON_DIR / "milk.png"},
    "nuts": {"en": "Nuts", "nl": "Noten", "icon": ICON_DIR / "nuts.png"},
    "celery": {"en": "Celery", "nl": "Selderij", "icon": ICON_DIR / "celery.png"},
    "mustard": {"en": "Mustard", "nl": "Mosterd", "icon": ICON_DIR / "mustard.png"},
    "sesame": {"en": "Sesame", "nl": "Sesam", "icon": ICON_DIR / "sesame.png"},
    "sulphites": {"en": "Sulphites", "nl": "Sulfieten", "icon": ICON_DIR / "sulphites.png"},
    "lupin": {"en": "Lupin", "nl": "Lupine", "icon": ICON_DIR / "lupin.png"},
    "molluscs": {"en": "Molluscs", "nl": "Weekdier", "icon": ICON_DIR / "molluscs.png"},
}