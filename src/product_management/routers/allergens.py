"""Routes for allergens."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db
from src.product_management.queries import list_allergens

router = APIRouter()


@router.get("/allergens")
def list_all_allergens(db: Session = Depends(get_db)):
    """Return all allergens."""
    return list_allergens(db)