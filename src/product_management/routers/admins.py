"""Routes for managing admin accounts. Owner-only."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_owner
from src.product_management.models import Admin
from src.product_management.queries import create_admin, delete_admin, list_admins
from src.product_management.schemas import AdminCreate, AdminResponse

router = APIRouter()


@router.get("/admins", response_model=list[AdminResponse])
def list_all_admins(
    current_owner: Admin = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> list[AdminResponse]:
    """List all admin accounts. Owner-only.

    Args:
        current_owner (Admin): The authenticated owner making the request.
        db (Session): Database session, injected by FastAPI.

    Returns:
        list[AdminResponse]: All admin accounts (username, role — no passwords).
    """
    admins = list_admins(db)
    return [AdminResponse.model_validate(a) for a in admins]


@router.post("/admins", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def create_new_admin(
    data: AdminCreate,
    current_owner: Admin = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> AdminResponse:
    """Create a new manager account. Owner-only.

    Args:
        data (AdminCreate): Username and password for the new account.
        current_owner (Admin): The authenticated owner creating the account.
        db (Session): Database session, injected by FastAPI.

    Returns:
        AdminResponse: The newly created manager account.

    Raises:
        HTTPException: 400 if the username is already taken.
    """
    admin = create_admin(db, data)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{data.username}' is already taken.",
        )

    log_admin_action(current_owner, "created", "admin", admin.id)
    return AdminResponse.model_validate(admin)


@router.delete("/admins/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_admin(
    admin_id: int,
    current_owner: Admin = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> None:
    """Delete a manager account. Owner-only.

    Args:
        admin_id (int): ID of the admin account to delete.
        current_owner (Admin): The authenticated owner performing the action.
        db (Session): Database session, injected by FastAPI.

    Raises:
        HTTPException: 404 if no admin exists with the given ID.
        HTTPException: 400 if attempting to delete the owner account.
    """
    success, error = delete_admin(db, admin_id)

    if not success:
        if error == "not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The owner account cannot be deleted.",
        )

    log_admin_action(current_owner, "deleted", "admin", admin_id)
