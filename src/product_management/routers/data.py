"""Routes for full data export/import (backup and restore)."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_admin, limiter
from src.product_management.models import Admin
from src.product_management.queries import export_all_data, import_all_data
from src.product_management.schemas import ExportData

router = APIRouter()


@router.get("/data/export", response_model=ExportData)
def export_data(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ExportData:
    """Export all business data (items, allergens, meat types, categories, settings) as JSON.

    Args:
        current_admin (Admin): The current logged-in admin user.
        db (Session): The database session.

    Returns:
        ExportData: A dictionary containing all exported business data.
    """
    return export_all_data(db)


@router.post("/data/import")
@limiter.limit("3/minute")
def import_data(
    request: Request,
    data: ExportData,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Replace all business data with the contents of an imported JSON file.

    Args:
        request: The incoming request object.
        data: The imported data to replace existing business data.
        current_admin: The admin user performing the import action.
        db: The database session for transactional operations.

    Returns:
        A dictionary with a single key 'detail' indicating the success of the import operation.
    """
    import_all_data(db, data)
    log_admin_action(current_admin, "imported", "full_dataset", "n/a")
    return {"detail": "Data imported successfully"}
