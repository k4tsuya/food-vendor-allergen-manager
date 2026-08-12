"""Health check route."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.product_management.core.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Report whether the API and database are reachable.

    Used by uptime monitors and deployment checks to confirm the service
    is running and can actually talk to the database, not just that the
    process is alive.

    Only catches OperationalError — the exception SQLAlchemy raises for
    actual connectivity failures (e.g. the database file is missing, or
    a network-based database is unreachable). Deliberately not a bare
    except Exception, so a bug unrelated to database connectivity
    (e.g. in the query itself) surfaces as a real 500 instead of being
    silently reported as "database unreachable."

    Args:
        db (Session): Database session, injected by FastAPI.

    Returns:
        dict[str, str]: `status` is always "ok" if this endpoint responds
        at all. `database` is "ok" if the test query succeeded, or
        "unreachable" if a database connectivity error occurred.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except OperationalError:
        db_status = "unreachable"

    return {"status": "ok", "database": db_status}
