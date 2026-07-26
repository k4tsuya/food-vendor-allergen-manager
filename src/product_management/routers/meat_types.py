"""Routes for meat types."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.core.database import get_db
from src.product_management.schemas import MeatTypeCreate, MeatTypeUpdate, MeatTypeResponse
from src.product_management.queries import list_meat_types, create_meat_type, update_meat_type, delete_meat_type


router = APIRouter()


@router.get("/meat-types")
def list_all_meat_types(db: Session = Depends(get_db)):
    """Return all meat types."""
    return list_meat_types(db)


@router.post("/meat-types", response_model=MeatTypeResponse, status_code=status.HTTP_201_CREATED)
def create_new_meat_type(
    data: MeatTypeCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new meat type. Requires authentication."""
    meat_type = create_meat_type(db, data)
    if meat_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A meat type with code '{data.code}' already exists.",
        )
    return meat_type


@router.put("/meat-types/{meat_type_id}", response_model=MeatTypeResponse)
def update_existing_meat_type(
    meat_type_id: int,
    data: MeatTypeUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update an existing meat type's descriptions. Requires authentication."""
    meat_type = update_meat_type(db, meat_type_id, data)
    if meat_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meat type not found")
    return meat_type


@router.delete("/meat-types/{meat_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_meat_type(
    meat_type_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete a meat type. Requires authentication."""
    deleted = delete_meat_type(db, meat_type_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meat type not found")