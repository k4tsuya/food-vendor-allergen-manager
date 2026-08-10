import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from src.product_management.core.database import SessionLocal
from src.product_management.queries import export_all_data

logger = logging.getLogger("backup")

BACKUP_DIR = Path("backups")
RETENTION_DAYS = 14  # Number of days to keep backups.


def run_scheduled_backup() -> None:
    """Export all business data to a timestamped JSON file.

    Runs on a daily schedule via start_backup_scheduler. Creates its
    own database session rather than using the get_db dependency,
    since this runs outside any HTTP request. After writing the new
    backup, deletes any backups older than RETENTION_DAYS.
    """
    BACKUP_DIR.mkdir(exist_ok=True)

    db = SessionLocal()
    try:
        data = export_all_data(db)
    finally:
        db.close()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    file_path = BACKUP_DIR / f"backup_{timestamp}.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("Automated backup written to %s", file_path)
    _delete_old_backups()


def _delete_old_backups() -> None:
    """Delete backup files older than RETENTION_DAYS.

    Keeps backups/ from growing indefinitely once older files are
    past the point of being useful for recovery.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    for file in BACKUP_DIR.glob("backup_*.json"):
        file_mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
        if file_mtime < cutoff:
            file.unlink()
            logger.info("Deleted old backup %s", file.name)


def start_backup_scheduler() -> BackgroundScheduler:
    """Start the daily automated backup job.

    Called once at app startup. Runs run_scheduled_backup every day
    at 03:00 UTC, a low-traffic time for a snackbar business.

    Returns:
        BackgroundScheduler: The running scheduler, so it can be shut
        down cleanly on app shutdown if needed.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scheduled_backup, "cron", hour=9, minute=21)
    scheduler.start()
    logger.info("Backup scheduler started (daily at 03:00 UTC)")
    return scheduler
