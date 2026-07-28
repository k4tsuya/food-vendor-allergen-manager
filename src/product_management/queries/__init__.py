"""Queries package.

Split into one module per resource. Everything is re-exported here so
existing code doing `from src.product_management.queries import X`
keeps working without changes.
"""

from src.product_management.queries.items import (
    list_items,
    pdf_list_items,
    get_item,
    create_item,
    update_item,
    delete_item,
)
from src.product_management.queries.allergens import (
    list_allergens,
    get_allergen,
    create_allergen,
    update_allergen,
    delete_allergen,
)
from src.product_management.queries.meat_types import (
    list_meat_types,
    get_meat_type,
    create_meat_type,
    update_meat_type,
    delete_meat_type,
)
from src.product_management.queries.categories import (
    list_categories,
    get_category,
    create_category,
    update_category,
    delete_category,
)
from src.product_management.queries.settings import (
    get_settings,
    update_settings,
)
from src.product_management.queries.data_transfer import (
    export_all_data,
    import_all_data,
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
