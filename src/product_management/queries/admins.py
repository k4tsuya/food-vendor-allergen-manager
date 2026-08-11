"""Database query functions for admin accounts."""

from sqlalchemy.orm import Session

from src.product_management.core.security import hash_password
from src.product_management.models import Admin
from src.product_management.schemas import AdminCreate


def list_admins(db: Session) -> list[Admin]:
    """Retrieve all admin accounts.

    Args:
        db: Active database session.

    Returns:
        All Admin rows (owner and managers), in insertion order.
    """
    return db.query(Admin).all()


def create_admin(db: Session, data: "AdminCreate") -> Admin | None:
    """Create a new manager account, or None if the username is taken.

    Always creates the account with role="manager" — creating another
    owner isn't supported here, keeping a single, clear point of
    ownership for the business.

    Args:
        db: Active database session.
        data: Username and plaintext password for the new account.

    Returns:
        The created Admin, or None if the username already exists.
    """
    if db.query(Admin).filter_by(username=data.username).first():
        return None

    admin = Admin(
        username=data.username,
        hashed_password=hash_password(data.password),
        role="manager",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def delete_admin(db: Session, admin_id: int) -> tuple[bool, str | None]:
    """Delete a manager account by ID.

    The owner account can never be deleted through this — there must
    always be exactly one owner.

    Args:
        db: Active database session.
        admin_id: Primary key of the admin account to delete.

    Returns:
        A tuple of (success, error_reason). error_reason is None on
        success, "not_found" if no admin with that id exists, or
        "is_owner" if the target account is the owner.
    """
    admin = db.query(Admin).filter_by(id=admin_id).first()
    if admin is None:
        return False, "not_found"

    if admin.role == "owner":
        return False, "is_owner"

    db.delete(admin)
    db.commit()
    return True, None
