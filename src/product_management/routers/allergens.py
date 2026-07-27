"""Routes for allergens."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.core.database import get_db
from src.product_management.schemas import AllergenCreate, AllergenUpdate, AllergenResponse
from src.product_management.queries import list_allergens, create_allergen, update_allergen, delete_allergen
from src.product_management.core.audit import log_admin_action

router = APIRouter()


@router.get("/allergens")
def list_all_allergens(db: Session = Depends(get_db)):
    """Return all allergens."""
    return list_allergens(db)


@router.post("/allergens", response_model=AllergenResponse, status_code=status.HTTP_201_CREATED)
def create_new_allergen(
    data: AllergenCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new allergen. Requires authentication."""
    allergen = create_allergen(db, data)
    if allergen is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An allergen with code '{data.code}' already exists.",
        )

    log_admin_action(current_admin, "created", "item", allergen.id)
    return allergen


@router.put("/allergens/{allergen_id}", response_model=AllergenResponse)
def update_existing_allergen(
    allergen_id: int,
    data: AllergenUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update an existing allergen's descriptions. Requires authentication."""
    allergen = update_allergen(db, allergen_id, data)
    if allergen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allergen not found")
    
    log_admin_action(current_admin, "updated", "item", allergen.id)
    return allergen


@router.delete("/allergens/{allergen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_allergen(
    allergen_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete an allergen. Requires authentication."""
    deleted = delete_allergen(db, allergen_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allergen not found")
    
    log_admin_action(current_admin, "deleted", "item", allergen_id)