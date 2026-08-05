"""Routes for meat types."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.queries import (
    create_meat_type,
    delete_meat_type,
    list_meat_types,
    update_meat_type,
)
from src.product_management.schemas import MeatTypeCreate, MeatTypeResponse, MeatTypeUpdate

router = APIRouter()


@router.get("/meat-types")
def list_all_meat_types(db: Session = Depends(get_db)):
    """
    Retrieve a list of all meat types.

    Args:
        db (Session): A database session.

    Returns:
        list[MeatTypeResponse]: A list of meat types.
    """
    return list_meat_types(db)


@router.post("/meat-types", response_model=MeatTypeResponse, status_code=status.HTTP_201_CREATED)
def create_new_meat_type(
    data: MeatTypeCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new meat type.

    Args:
        data (MeatTypeCreate): The data for creating a new meat type.
        current_admin (Admin): The current admin user.
        db (Session): A database session.

    Returns:
        MeatTypeResponse: The created meat type.

    Raises:
        HTTPException: If a meat type with the given code already exists.
    """
    meat_type = create_meat_type(db, data)
    if meat_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A meat type with code '{data.code}' already exists.",
        )

    log_admin_action(current_admin, "created", "item", meat_type.id)
    return meat_type


@router.put("/meat-types/{meat_type_id}", response_model=MeatTypeResponse)
def update_existing_meat_type(
    meat_type_id: int,
    data: MeatTypeUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update an existing meat type.

    Args:
        meat_type_id (int): The ID of the meat type to update.
        data (MeatTypeUpdate): The updated data for the meat type.
        current_admin (Admin): The current admin user.
        db (Session): A database session.

    Returns:
        MeatTypeResponse: The updated meat type.

    Raises:
        HTTPException: If the meat type is not found.
    """
    meat_type = update_meat_type(db, meat_type_id, data)
    if meat_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meat type not found")

    log_admin_action(current_admin, "updated", "item", meat_type.id)

    return meat_type


@router.delete("/meat-types/{meat_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_meat_type(
    meat_type_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Delete an existing meat type.

    Args:
        meat_type_id (int): The ID of the meat type to delete.
        current_admin (Admin): The current admin user.
        db (Session): A database session.

    Raises:
        HTTPException: If the meat type is not found.
    """
    deleted = delete_meat_type(db, meat_type_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meat type not found")

    log_admin_action(current_admin, "deleted", "item", meat_type_id)
