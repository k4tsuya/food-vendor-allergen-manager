"""Queries package.

Split into one module per resource. Everything is re-exported here so
existing code doing `from src.product_management.queries import X`
keeps working without changes.
"""

from src.product_management.queries.allergens import (
    create_allergen,
    delete_allergen,
    get_allergen,
    list_allergens,
    update_allergen,
)
from src.product_management.queries.categories import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)
from src.product_management.queries.data_transfer import (
    export_all_data,
    import_all_data,
)
from src.product_management.queries.items import (
    create_item,
    delete_item,
    get_item,
    list_items,
    pdf_list_items,
    update_item,
)
from src.product_management.queries.meat_types import (
    create_meat_type,
    delete_meat_type,
    get_meat_type,
    list_meat_types,
    update_meat_type,
)
from src.product_management.queries.settings import (
    get_settings,
    update_settings,
)

__all__ = [
    "list_items",
    "get_gluten_free_items",
    "pdf_list_items",
    "get_item",
    "create_item",
    "update_item",
    "delete_item",
    "list_allergens",
    "get_allergen",
    "create_allergen",
    "update_allergen",
    "delete_allergen",
    "list_meat_types",
    "get_meat_type",
    "create_meat_type",
    "update_meat_type",
    "delete_meat_type",
    "list_categories",
    "get_category",
    "create_category",
    "update_category",
    "delete_category",
    "get_settings",
    "update_settings",
    "export_all_data",
    "import_all_data",
]
