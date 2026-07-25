"""Routes for items, gluten-free filtering, and PDF export."""

from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db
from src.product_management.schemas import ItemResponse
from src.product_management.queries import list_items, get_gluten_free_items, pdf_list_items
from src.product_management.pdf_generator import AllergenMatrixPDF

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)


@router.get("/items", response_model=list[ItemResponse])
def list_all_items(db: Session = Depends(get_db)):
    """Return all items."""
    return list_items(db)


@router.get("/gluten-free", response_model=list[ItemResponse])
def list_gluten_free_items(db: Session = Depends(get_db)):
    """Return all gluten-free items."""
    return get_gluten_free_items(db)


@router.get("/items/pdf", response_class=FileResponse)
def download_items_pdf(language: str = "nl", db: Session = Depends(get_db)):
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