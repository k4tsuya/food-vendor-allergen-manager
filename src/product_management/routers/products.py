"""Routes for products, gluten-free filtering, and PDF export."""

from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db
from src.product_management.schemas import ProductResponse
from src.product_management.queries import list_products, get_gluten_free_products, pdf_list_products
from src.product_management.pdf_generator import AllergenMatrixPDF

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)


@router.get("/products", response_model=list[ProductResponse])
def list_all_products(db: Session = Depends(get_db)):
    """Return all products."""
    return list_products(db)


@router.get("/gluten-free", response_model=list[ProductResponse])
def list_gluten_free_products(db: Session = Depends(get_db)):
    """Return all gluten-free products."""
    return get_gluten_free_products(db)


@router.get("/products/pdf", response_class=FileResponse)
def download_products_pdf(language: str = "nl", db: Session = Depends(get_db)):
    """Save a PDF of all products and their allergens."""
    products = pdf_list_products(db)
    file_path = OUTPUT_DIR / "product_allergens.pdf"

    pdf = AllergenMatrixPDF(orientation="L")
    pdf.set_language(language)
    pdf.generate_allergen_matrix_pdf(
        data=products,
        output_path=str(file_path),
        language=language,
    )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="products_allergens.pdf",
    )