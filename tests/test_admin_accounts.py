"""Tests for admin account management and owner/manager role restrictions."""


def test_manager_cannot_access_settings(client, manager_auth_headers):
    response = client.put(
        "/config",
        json={
            "meat_tracking_enabled": False,
            "company_name": "Test Co",
            "site_title_en": "Test",
            "site_title_nl": "Test",
            "default_language": "nl",
        },
        headers=manager_auth_headers,
    )

    assert response.status_code == 403


def test_owner_can_access_settings(client, auth_headers):
    response = client.put(
        "/config",
        json={
            "meat_tracking_enabled": False,
            "company_name": "Test Co",
            "site_title_en": "Test",
            "site_title_nl": "Test",
            "default_language": "nl",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_manager_cannot_create_admin(client, manager_auth_headers):
    response = client.post(
        "/admins",
        json={"username": "newmanager", "password": "testpass123"},
        headers=manager_auth_headers,
    )

    assert response.status_code == 403


def test_owner_can_create_manager(client, auth_headers):
    response = client.post(
        "/admins",
        json={"username": "newmanager", "password": "testpass123"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["role"] == "manager"


def test_owner_cannot_delete_own_owner_account(client, auth_headers, db_session):
    from src.product_management.models import Admin

    owner = db_session.query(Admin).filter_by(username="testadmin").first()

    response = client.delete(f"/admins/{owner.id}", headers=auth_headers)

    assert response.status_code == 400
