"""Routes for allergens."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.queries import (
    create_allergen,
    delete_allergen,
    list_allergens,
    update_allergen,
)
from src.product_management.schemas import AllergenCreate, AllergenResponse, AllergenUpdate

router = APIRouter()


@router.get("/allergens")
def list_all_allergens(db: Session = Depends(get_db)) -> list[AllergenResponse]:
    """Retrieve all allergens.

    Exposes the allergen list for frontend consumption (filters,
    allergen matrix columns, admin dropdowns) via the public API.

    Args:
        db (Session): Database session, injected by FastAPI.

    Returns:
        list[AllergenResponse]: All allergens, converted from ORM
        objects to response schema.
    """
    allergens = list_allergens(db)
    return [AllergenResponse.model_validate(a) for a in allergens]


@router.post("/allergens", response_model=AllergenResponse, status_code=status.HTTP_201_CREATED)
def create_new_allergen(
    data: AllergenCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AllergenResponse:
    """Create a new allergen.

    Rejects the request if an allergen with the same code already
    exists, since code must stay unique for lookups elsewhere.

    Args:
        data (AllergenCreate): Fields for the new allergen.
        current_admin (Admin): Admin performing the action, used for logging.
        db (Session): Database session, injected by FastAPI.

    Returns:
        AllergenResponse: The newly created allergen.

    Raises:
        HTTPException: 400 if an allergen with the given code already exists.
    """
    allergen = create_allergen(db, data)
    if allergen is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An allergen with code '{data.code}' already exists.",
        )

    log_admin_action(current_admin, "created", "item", allergen.id)
    return AllergenResponse.model_validate(allergen)


@router.put("/allergens/{allergen_id}", response_model=AllergenResponse)
def update_existing_allergen(
    allergen_id: int,
    data: AllergenUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AllergenResponse:
    """Update an existing allergen.

    Returns a 404 instead of silently doing nothing, so the frontend
    knows the ID it tried to update doesn't exist.

    Args:
        allergen_id (int): ID of the allergen to update.
        data (AllergenUpdate): Fields to update.
        current_admin (Admin): Admin performing the action, used for logging.
        db (Session): Database session, injected by FastAPI.

    Returns:
        AllergenResponse: The updated allergen.

    Raises:
        HTTPException: 404 if no allergen exists with the given ID.
    """
    allergen = update_allergen(db, allergen_id, data)
    if allergen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allergen not found")

    log_admin_action(current_admin, "updated", "item", allergen.id)
    return AllergenResponse.model_validate(allergen)


@router.delete("/allergens/{allergen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_allergen(
    allergen_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    """Delete an existing allergen.

    Returns a 404 instead of silently doing nothing, so the frontend
    knows the ID it tried to delete doesn't exist.

    Args:
        allergen_id (int): ID of the allergen to delete.
        current_admin (Admin): Admin performing the action, used for logging.
        db (Session): Database session, injected by FastAPI.

    Raises:
        HTTPException: 404 if no allergen exists with the given ID.
    """
    deleted = delete_allergen(db, allergen_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allergen not found")

    log_admin_action(current_admin, "deleted", "item", allergen_id)
