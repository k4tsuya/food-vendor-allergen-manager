"""Routes for categories."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.queries import (
    create_category,
    delete_category,
    list_categories,
    update_category,
)
from src.product_management.schemas import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter()


@router.get("/categories", response_model=list[CategoryResponse])
def list_all_categories(db: Session = Depends(get_db)):
    """Return all categories."""
    return list_categories(db)


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(
    data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new category. Requires authentication."""
    category = create_category(db, data)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A category with code '{data.code}' already exists.",
        )

    log_admin_action(current_admin, "created", "item", category.id)
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int,
    data: CategoryUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update an existing category's descriptions. Requires authentication."""
    category = update_category(db, category_id, data)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    log_admin_action(current_admin, "updated", "item", category.id)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_category(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete a category. Requires authentication."""
    deleted = delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    log_admin_action(current_admin, "deleted", "item", category_id)
