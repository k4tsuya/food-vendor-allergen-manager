"""Tests for password strength validation on account creation and password change."""


def test_create_admin_rejects_short_password(client, auth_headers):
    response = client.post(
        "/admins",
        json={"username": "shortpw", "password": "abc123"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_admin_rejects_password_with_no_number(client, auth_headers):
    response = client.post(
        "/admins",
        json={"username": "nonumber", "password": "onlyletters"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_admin_rejects_password_with_no_letter(client, auth_headers):
    response = client.post(
        "/admins",
        json={"username": "noletter", "password": "12345678"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_admin_accepts_strong_password(client, auth_headers):
    response = client.post(
        "/admins",
        json={"username": "stronguser", "password": "validpass123"},
        headers=auth_headers,
    )

    assert response.status_code == 201


def test_change_password_rejects_weak_new_password(client, auth_headers):
    response = client.put(
        "/auth/password",
        json={"current_password": "testpass123", "new_password": "weak"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_change_password_accepts_strong_new_password(client, auth_headers):
    response = client.put(
        "/auth/password",
        json={"current_password": "testpass123", "new_password": "newvalidpass456"},
        headers=auth_headers,
    )

    assert response.status_code == 200
