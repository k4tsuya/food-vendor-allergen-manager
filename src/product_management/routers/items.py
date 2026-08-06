"""Routes for items and PDF export."""

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_admin, limiter
from src.product_management.models import Admin
from src.product_management.pdf_generator import AllergenMatrixPDF
from src.product_management.queries import (
    create_item,
    delete_item,
    list_items,
    pdf_list_items,
    update_item,
)
from src.product_management.schemas import ItemCreate, ItemResponse, ItemUpdate, ItemWriteResponse

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)


@router.get("/items", response_model=list[ItemResponse])
def list_all_items(
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    exclude_allergens: list[str] | None = Query(default=None),
    categories: list[str] | None = Query(default=None),
    meat_types: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ItemResponse]:
    """
    Retrieve a paginated list of items, optionally filtered by various criteria.

    Args:
        limit (int): The maximum number of items to return. Defaults to 50.
        offset (int): The number of items to skip before starting to return results. Defaults to 0.
        search (str | None): A search query to filter items by name or description.
        exclude_allergens (list[str] | None): A list of allergens to exclude from the results.
        categories (list[str] | None): A list of categories to filter items by.
        meat_types (list[str] | None): A list of meat types to filter items by.
        db (Session): The database session to use for querying.

    Returns:
        list[ItemResponse]: A list of ItemResponse objects representing the filtered items.
    """
    return list_items(
        db,
        limit=limit,
        offset=offset,
        search=search,
        exclude_allergens=exclude_allergens,
        meat_types=meat_types,
        categories=categories,
    )


@router.get("/items/pdf", response_class=FileResponse)
def download_items_pdf(
    language: Literal["en", "nl"] = "nl", db: Session = Depends(get_db)
) -> FileResponse:
    """
    Generates and downloads a PDF of all items and their allergens.

    This function retrieves all items from the database, then generates a PDF containing
    an allergen matrix for these items. The PDF is saved to a temporary file and returned
    as a downloadable response.

    Args:
        language (Literal["en", "nl"]): The language for the PDF, defaulting to "nl".
        db (Session): The database session dependency.

    Returns:
        FileResponse: A response object containing the generated PDF file.
    """
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


@router.post("/items", response_model=ItemWriteResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_new_item(
    request: Request,
    data: ItemCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ItemWriteResponse:
    """
    Create a new item in the database. Requires admin authentication.

    This function processes the request data to create a new item record in the database.
    It logs the admin action and returns a response containing the created item and any warnings.

    Args:
        request (Request): The incoming HTTP request object.
        data (ItemCreate): Pydantic model containing the item creation data.
        current_admin (Admin): The authenticated admin user, injected via dependency.
        db (Session): The database session, injected via dependency.

    Returns:
        ItemWriteResponse: A response model containing the created item and any associated warnings.

    Raises:
        HTTPException: If the item creation fails due to validation errors or database constraints.
    """
    item, warnings = create_item(db, data)
    log_admin_action(current_admin, "created", "item", item.id)
    return ItemWriteResponse(item=item, warnings=warnings)  # type: ignore[arg-type]


@router.put("/items/{item_id}", response_model=ItemWriteResponse)
@limiter.limit("30/minute")
def update_existing_item(
    request: Request,
    item_id: int,
    data: ItemUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ItemWriteResponse:
    """Update an existing item. Requires authentication.

    This function updates an item in the database with the provided data. It
    checks for the existence of the item and logs the admin action. If the item
    is not found, it raises an HTTP 404 exception.

    Args:
        request: The incoming request object.
        item_id: The ID of the item to update.
        data: The update data for the item.
        current_admin: The current authenticated admin user. Defaults to Depends(get_current_admin).
        db: The database session. Defaults to Depends(get_db).

    Returns:
        The response containing the updated item and any warnings.

    Raises:
        HTTPException: If the item with the specified ID does not exist.
    """
    result = update_item(db, item_id, data)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    item, warnings = result
    log_admin_action(current_admin, "updated", "item", item.id)
    return ItemWriteResponse(item=item, warnings=warnings)  # type: ignore[arg-type]


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def delete_existing_item(
    request: Request,
    item_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    """Delete an item. Requires authentication.

    This function handles the deletion of an item by its ID. It requires an authenticated admin user
    and performs the deletion operation using the provided database session.
    If the item does not exist, it raises an HTTP 404 Not Found exception.
        After successful deletion, it logs the admin action.

    Args:
        request (Request): The incoming HTTP request object.
        item_id (int): The ID of the item to be deleted. Must be a positive integer.
        current_admin (Admin): The authenticated admin user performing the action.
            Retrieved via dependency injection.
        db (Session): The database session to interact with the database.
            Retrieved via dependency injection.

    Raises:
        HTTPException: Raised with status code 404
            if the item to be deleted does not exist in the database.
    """
    deleted = delete_item(db, item_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    log_admin_action(current_admin, "deleted", "item", item_id)
