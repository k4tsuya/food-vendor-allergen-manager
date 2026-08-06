"""Lightweight audit logging for admin write actions."""

import logging

from src.product_management.models import Admin

logger = logging.getLogger("audit")


def log_admin_action(admin: Admin, action: str, resource: str, resource_id: int | str) -> None:
    """Record an admin create/update/delete action for the audit trail.

    Logged under a separate "audit" logger (not the general app logger),
    so admin write actions can be reviewed independently of regular
    application logs.

    Args:
        admin: The admin who performed the action.
        action: What happened, e.g. "created", "updated", "deleted".
        resource: The type of resource affected, e.g. "item", "allergen".
        resource_id: Primary key of the affected resource. Accepts str
            for cases like the logo, which has no numeric id.
    """
    logger.info("Admin '%s' %s %s id=%s", admin.username, action, resource, resource_id)
