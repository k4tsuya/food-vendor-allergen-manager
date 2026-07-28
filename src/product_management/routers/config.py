"""Routes for app-wide settings."""

import os
import shutil
import xml.etree.ElementTree as ET
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
from src.product_management.core.audit import log_admin_action
from src.product_management.core.database import get_db
from src.product_management.core.security import get_current_admin
from src.product_management.models import Admin
from src.product_management.schemas import SettingsResponse, SettingsUpdate
from src.product_management.queries import get_settings, update_settings

router = APIRouter()


MAGIC_NUMBERS = {
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
}


@router.get("/config", response_model=SettingsResponse)
def get_config(db: Session = Depends(get_db)):
    """Return current app settings. Public — the frontend needs this without logging in."""
    return get_settings(db)


@router.put("/config", response_model=SettingsResponse)
def update_config(
    data: SettingsUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update app settings. Requires authentication."""
    return update_settings(db, data)


LOGO_DIR = Path("src/product_management/static/logos")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/config/logo", response_model=SettingsResponse)
def upload_logo(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Upload a vendor logo, replacing any existing one."""
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

    settings.logo_path = filename
    db.commit()
    db.refresh(settings)

    log_admin_action(current_admin, "uploaded", "logo", filename)
    return settings


@router.delete("/config/logo", response_model=SettingsResponse)
def delete_logo(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Remove the current vendor logo, if any."""
    settings = get_settings(db)
    if settings.logo_path:
        old_file = LOGO_DIR / settings.logo_path
        if old_file.exists():
            old_file.unlink()
        settings.logo_path = None
        db.commit()
        db.refresh(settings)

    log_admin_action(current_admin, "removed", "logo", "n/a")
    return settings


def validate_file_content(extension: str, contents: bytes) -> None:
    """Verify the file's actual content matches its claimed extension."""
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