"""Routes for app-wide settings."""

import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_owner
from src.product_management.models import Admin
from src.product_management.queries import get_settings, update_settings
from src.product_management.schemas import SettingsResponse, SettingsUpdate

router = APIRouter()


MAGIC_NUMBERS = {
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
}


@router.get("/config", response_model=SettingsResponse)
def get_config(db: Session = Depends(get_db)) -> SettingsResponse:
    """Return current app settings. Public — the frontend needs this without logging in.

    Args:
        db (Session): Database session.

    Returns:
        SettingsResponse: The current application settings.
    """
    settings = get_settings(db)
    return SettingsResponse.model_validate(settings)


@router.put("/config", response_model=SettingsResponse)
def update_config(
    data: SettingsUpdate,
    current_admin: Admin = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """Update app settings. Requires authentication.

    Args:
        data: The settings data to update.
        current_admin: The current authenticated admin user.
        db: The database session.

    Returns:
        SettingsResponse: The updated settings response.
    """
    updated_settings = update_settings(db, data)
    return SettingsResponse.model_validate(updated_settings)


LOGO_DIR = Path("src/product_management/static/logos")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/config/logo", response_model=SettingsResponse)
def upload_logo(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """Upload a vendor logo, replacing any existing one.

    Args:
        file: The uploaded file containing the vendor logo.
        current_admin: The current admin user performing the action.
        db: The database session.

    Returns:
        SettingsResponse: The updated settings with the new logo path.

    Raises:
        HTTPException: If no filename is provided, if the file type is unsupported,
            or if the file size exceeds the maximum allowed size.
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_LOGO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logo file is too large (max 2MB).",
        )

    contents = file.file.read()
    validate_file_content(extension, contents)
    file.file.seek(0)

    settings = get_settings(db)
    if settings.logo_path:
        old_file = LOGO_DIR / settings.logo_path
        if old_file.exists():
            old_file.unlink()

    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"logo{extension}"
    destination = LOGO_DIR / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    settings.logo_path = filename  # type: ignore[assignment]
    db.commit()
    db.refresh(settings)

    log_admin_action(current_admin, "uploaded", "logo", filename)
    return SettingsResponse.model_validate(settings)


@router.delete("/config/logo", response_model=SettingsResponse)
def delete_logo(
    current_admin: Admin = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """Remove the current vendor logo, if any.

    Args:
        current_admin: The current logged-in admin.
        db: Database session.

    Returns:
        SettingsResponse: The updated settings after removing the logo.

    Raises:
        HTTPException: If the admin does not have permission to perform the action.
    """
    settings = get_settings(db)
    if settings.logo_path:
        old_file = LOGO_DIR / settings.logo_path
        if old_file.exists():
            old_file.unlink()
        settings.logo_path = None  # type: ignore[assignment]
        db.commit()
        db.refresh(settings)

    log_admin_action(current_admin, "removed", "logo", "n/a")
    return SettingsResponse.model_validate(settings)


def validate_file_content(extension: str, contents: bytes) -> None:
    """Verify that the file's actual content matches its claimed extension.

    Args:
        extension (str): The file extension to validate against.
        contents (bytes): The raw bytes of the file content to validate.
    """
    if extension in MAGIC_NUMBERS:
        signature = MAGIC_NUMBERS[extension]
        if not contents.startswith(signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match a valid image for this extension.",
            )

    elif extension == ".svg":
        try:
            root = ET.fromstring(contents)
        except ET.ParseError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is not valid SVG/XML.",
            )

        if not root.tag.endswith("svg"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is not a valid SVG (missing <svg> root element).",
            )

        if b"<script" in contents.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SVG files containing <script> tags are not allowed.",
            )
