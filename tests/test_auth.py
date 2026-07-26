from src.product_management.models import Admin
from src.product_management.core.security import hash_password


def test_login_succeeds_with_correct_credentials(client, db_session):
    db_session.add(Admin(username="testadmin", hashed_password=hash_password("testpass123")))
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_fails_with_wrong_password(client, db_session):
    db_session.add(Admin(username="testadmin", hashed_password=hash_password("testpass123")))
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"username": "testadmin", "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_login_fails_with_unknown_username(client, db_session):
    response = client.post(
        "/auth/login",
        json={"username": "doesnotexist", "password": "whatever"},
    )

    assert response.status_code == 401


def test_protected_route_rejects_missing_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_protected_route_accepts_valid_token(client, db_session):
    db_session.add(Admin(username="testadmin", hashed_password=hash_password("testpass123")))
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["username"] == "testadmin"


def test_protected_route_rejects_garbage_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not.a.real.token"})

    assert response.status_code == 401
    

def test_login_rate_limits_after_five_attempts(client, db_session):
    db_session.add(Admin(username="testadmin", hashed_password=hash_password("testpass123")))
    db_session.commit()

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={"username": "testadmin", "password": "wrong"},
        )
        assert response.status_code == 401

    sixth_response = client.post(
        "/auth/login",
        json={"username": "testadmin", "password": "wrong"},
    )
    assert sixth_response.status_code == 429