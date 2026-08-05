"""Database query functions for categories.

Categories group items for display (e.g. "Snacks", "Bakery"). An item
references a category by `code`, stored as Item.category_key — not by a
foreign key to Category.id. This is a deliberate looser coupling (see
delete_category's docstring for what that means in practice).
"""

from sqlalchemy.orm import Session

from src.product_management.models import Category
from src.product_management.schemas import CategoryCreate, CategoryUpdate


def list_categories(db: Session) -> list[Category]:
    """Args:
        db: Active database session.

    Returns:
        All Category rows, ordered by description_en ascending.
    """
    return db.query(Category).order_by(Category.description_en).all()


def get_category(db: Session, category_id: int) -> Category | None:
    """Args:
        db: Active database session.
        category_id: Primary key of the category to fetch.

    Returns:
        The matching Category, or None if no category has this id.
    """
    return db.query(Category).filter_by(id=category_id).first()


def create_category(db: Session, data: "CategoryCreate") -> Category | None:
    """`code` has a unique constraint at the database level, so this checks
    for an existing match first and returns None rather than letting the
    insert fail with a raw IntegrityError — the router turns that None
    into a clean 400 response instead of a 500.

    Args:
        db: Active database session.
        data: The new category's code and English/Dutch descriptions.

    Returns:
        The created Category, or None if the code already exists.

    Raises:
        sqlalchemy.exc.IntegrityError: In a rare race condition where a
            different request inserts the same code between this
            function's existence check and its own commit.
    """
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
    """`code` is intentionally not updatable here (see the CategoryUpdate
    schema — it has no code field). Code is what items store on
    Item.category_key, so changing it after creation would silently
    break the link for every item already using it. Renaming a code is
    a delete-and-recreate, not an update.

    Args:
        db: Active database session.
        category_id: Primary key of the category to update.
        data: New English/Dutch descriptions to apply.

    Returns:
        The updated Category, or None if no category with this id exists.
    """
    category = get_category(db, category_id)
    if category is None:
        return None

    category.description_en = data.description_en
    category.description_nl = data.description_nl
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Unlike allergens/meat types, this does NOT cascade to items: since
    Item.category_key is a plain string matching Category.code (not a
    foreign key to Category.id), deleting a Category leaves any items
    that referenced it with a category_key pointing at nothing. This is
    why the frontend always resolves category_key against the current
    live category list and falls back to "Uncategorized" for anything
    that doesn't match, rather than assuming every category_key resolves.

    Args:
        db: Active database session.
        category_id: Primary key of the category to delete.

    Returns:
        True if a category was found and deleted, False otherwise.
    """
    category = get_category(db, category_id)
    if category is None:
        return False

    db.delete(category)
    db.commit()
    return True
