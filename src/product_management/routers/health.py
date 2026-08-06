"""Health check route."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Report whether the API and database are reachable.

    Args:
        db: Database session.

    Returns:
        A dictionary with the API and database status.
        - status: Always returns "ok".
        - database: "ok" if the database is reachable, otherwise "unreachable".
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unreachable"

    return {"status": "ok", "database": db_status}
