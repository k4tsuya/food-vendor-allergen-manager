"""Tests for the /health endpoint."""

from sqlalchemy.exc import OperationalError


def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"


def test_health_check_reports_ok_when_database_is_reachable(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_check_reports_unreachable_on_database_error(client, monkeypatch):
    def broken_execute(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("simulated connection failure"))

    monkeypatch.setattr("sqlalchemy.orm.Session.execute", broken_execute)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "unreachable"}
