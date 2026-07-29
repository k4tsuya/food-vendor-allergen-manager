"""Lightweight audit logging for admin write actions."""

import logging

from src.product_management.models import Admin

logger = logging.getLogger("audit")


def log_admin_action(admin: Admin, action: str, resource: str, resource_id: int | str) -> None:
    """Record an admin create/update/delete action."""
    logger.info("Admin '%s' %s %s id=%s", admin.username, action, resource, resource_id)
