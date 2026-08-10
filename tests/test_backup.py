"""Tests for the automated backup."""

import os
from datetime import datetime, timedelta, timezone

from src.product_management.core import backup


def test_run_scheduled_backup_creates_file(db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(backup, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(backup, "BACKUP_DIR", tmp_path)

    backup.run_scheduled_backup()

    backup_files = list(tmp_path.glob("backup_*.json"))
    assert len(backup_files) == 1


def test_delete_old_backups_removes_stale_files(tmp_path, monkeypatch):
    monkeypatch.setattr(backup, "BACKUP_DIR", tmp_path)

    old_file = tmp_path / "backup_old.json"
    old_file.write_text("{}")
    old_time = (datetime.now(timezone.utc) - timedelta(days=20)).timestamp()
    os.utime(old_file, (old_time, old_time))

    recent_file = tmp_path / "backup_recent.json"
    recent_file.write_text("{}")

    backup._delete_old_backups()

    assert not old_file.exists()
    assert recent_file.exists()
