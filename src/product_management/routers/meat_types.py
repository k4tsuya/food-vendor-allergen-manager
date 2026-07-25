"""Routes for meat types."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db
from src.product_management.queries import list_meat_types

router = APIRouter()


@router.get("/meat-types")
def list_all_meat_types(db: Session = Depends(get_db)):
    """Return all meat types."""
    return list_meat_types(db)