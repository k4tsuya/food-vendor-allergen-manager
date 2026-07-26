"""Routes for items, gluten-free filtering, and PDF export."""

from pathlib import Path
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Literal


from src.product_management.core.database import get_db
from src.product_management.core.config import CATEGORY_LABELS
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.schemas import ItemResponse, ItemCreate, ItemUpdate, ItemWriteResponse
from src.product_management.queries import (
    list_items, get_gluten_free_items, pdf_list_items, create_item, update_item, delete_item)
from src.product_management.pdf_generator import AllergenMatrixPDF

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)


from fastapi import Query

@router.get("/items", response_model=list[ItemResponse])
def list_all_items(
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    exclude_allergens: list[str] | None = Query(default=None),
    categories: list[str] | None = Query(default=None),
    meat_types: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return items, paginated and optionally filtered."""
    return list_items(
        db,
        limit=limit,
        offset=offset,
        search=search,
        exclude_allergens=exclude_allergens,
        meat_types=meat_types,
        categories=categories,
    )


@router.get("/gluten-free", response_model=list[ItemResponse])
def list_gluten_free_items(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    """Return all gluten-free items."""
    return get_gluten_free_items(db, limit, offset)


@router.get("/items/pdf", response_class=FileResponse)
def download_items_pdf(language: Literal["en", "nl"] = "nl", db: Session = Depends(get_db)):
    """Save a PDF of all items and their allergens."""
    items = pdf_list_items(db)
    file_path = OUTPUT_DIR / "item_allergens.pdf"

    pdf = AllergenMatrixPDF(orientation="L")
    pdf.set_language(language)
    pdf.generate_allergen_matrix_pdf(
        data=items,
        output_path=str(file_path),
        language=language,
    )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="item_allergens.pdf",
    )
@router.get("/categories")
def list_all_categories(db: Session = Depends(get_db)):
    """Return all distinct item categories currently in use."""
    return list(CATEGORY_LABELS.keys())



@router.post("/items", response_model=ItemWriteResponse, status_code=status.HTTP_201_CREATED)
def create_new_item(
    data: ItemCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new item. Requires authentication."""
    item, warnings = create_item(db, data)
    return ItemWriteResponse(item=item, warnings=warnings)


@router.put("/items/{item_id}", response_model=ItemWriteResponse)
def update_existing_item(
    item_id: int,
    data: ItemUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update an existing item. Requires authentication."""
    result = update_item(db, item_id, data)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    item, warnings = result
    return ItemWriteResponse(item=item, warnings=warnings)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_item(
    item_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete an item. Requires authentication."""
    deleted = delete_item(db, item_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")