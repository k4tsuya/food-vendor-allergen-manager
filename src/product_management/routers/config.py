"""Route exposing app-wide configuration to the frontend."""

from fastapi import APIRouter

from src.product_management.core.config import ITEM_LABEL, ENABLE_MEAT_TRACKING
from src.product_management.schemas import ConfigResponse

router = APIRouter()


@router.get("/config", response_model=ConfigResponse)
def get_config():
    """Return frontend-relevant configuration values."""
    return ConfigResponse(
        item_label_en=ITEM_LABEL["en"],
        item_label_nl=ITEM_LABEL["nl"],
        meat_tracking_enabled=ENABLE_MEAT_TRACKING,
    )