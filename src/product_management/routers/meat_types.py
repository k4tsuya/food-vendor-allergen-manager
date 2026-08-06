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


@router.get("/meat-types", response_model=list[MeatTypeResponse])
def list_all_meat_types(db: Session = Depends(get_db)) -> list[MeatTypeResponse]:
    """Retrieve all meat types.

    Exposes the meat-type list for frontend consumption (dropdowns,
    allergen matrix columns) via the public API.

    Args:
        db (Session): Database session, injected by FastAPI.

    Returns:
        list[MeatTypeResponse]: All meat types, converted from ORM
        objects to response schema.
    """
    meat_types = list_meat_types(db)
    return [MeatTypeResponse.model_validate(m) for m in meat_types]


@router.post("/meat-types", response_model=MeatTypeResponse, status_code=status.HTTP_201_CREATED)
def create_new_meat_type(
    data: MeatTypeCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MeatTypeResponse | None:
    """Create a new meat type.

    Rejects the request if a meat type with the same code already
    exists, since code must stay unique for lookups elsewhere.

    Args:
        data (MeatTypeCreate): Fields for the new meat type.
        current_admin (Admin): Admin performing the action, used for logging.
        db (Session): Database session, injected by FastAPI.

    Returns:
        MeatTypeResponse: The newly created meat type.

    Raises:
        HTTPException: 400 if a meat type with the given code already exists.
    """
    meat_type = create_meat_type(db, data)
    if meat_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A meat type with code '{data.code}' already exists.",
        )

    log_admin_action(current_admin, "created", "item", meat_type.id)
    return MeatTypeResponse.model_validate(meat_type)


@router.put("/meat-types/{meat_type_id}", response_model=MeatTypeResponse)
def update_existing_meat_type(
    meat_type_id: int,
    data: MeatTypeUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MeatTypeResponse | None:
    """Update an existing meat type.

    Returns a 404 instead of silently doing nothing, so the frontend
    knows the ID it tried to update doesn't exist.

    Args:
        meat_type_id (int): ID of the meat type to update.
        data (MeatTypeUpdate): Fields to update.
        current_admin (Admin): Admin performing the action, used for logging.
        db (Session): Database session, injected by FastAPI.

    Returns:
        MeatTypeResponse: The updated meat type.

    Raises:
        HTTPException: 404 if no meat type exists with the given ID.
    """
    meat_type = update_meat_type(db, meat_type_id, data)
    if meat_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meat type not found")

    log_admin_action(current_admin, "updated", "item", meat_type.id)
    return MeatTypeResponse.model_validate(meat_type)


@router.delete("/meat-types/{meat_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_meat_type(
    meat_type_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    """Delete an existing meat type.

    Returns a 404 instead of silently doing nothing, so the frontend
    knows the ID it tried to delete doesn't exist.

    Args:
        meat_type_id (int): ID of the meat type to delete.
        current_admin (Admin): Admin performing the action, used for logging.
        db (Session): Database session, injected by FastAPI.

    Raises:
        HTTPException: 404 if no meat type exists with the given ID.
    """
    deleted = delete_meat_type(db, meat_type_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meat type not found")

    log_admin_action(current_admin, "deleted", "item", meat_type_id)
