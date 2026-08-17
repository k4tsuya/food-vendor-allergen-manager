"""Tests for the request body size limiting middleware."""

from src.product_management.core import body_limit


def test_request_under_limit_succeeds(client, monkeypatch):
    monkeypatch.setattr(body_limit, "MAX_BODY_SIZE", 1000)

    response = client.get("/health")

    assert response.status_code == 200


def test_request_over_limit_is_rejected(client, monkeypatch):
    monkeypatch.setattr(body_limit, "MAX_BODY_SIZE", 10)

    response = client.post(
        "/auth/login",
        json={"username": "irrelevant", "password": "irrelevant"},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body exceeds the maximum allowed size."
