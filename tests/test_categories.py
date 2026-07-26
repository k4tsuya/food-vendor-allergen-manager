def test_list_categories_is_public(client, db_session):
    from src.product_management.models import Category

    db_session.add(Category(code="snacks", description_en="Snacks", description_nl="Snacks"))
    db_session.commit()

    response = client.get("/categories")

    assert response.status_code == 200
    assert response.json()[0]["code"] == "snacks"


def test_create_category_requires_auth(client):
    response = client.post(
        "/categories",
        json={"code": "drinks", "description_en": "Drinks", "description_nl": "Dranken"},
    )

    assert response.status_code == 401


def test_create_category_succeeds_with_auth(client, auth_headers):
    response = client.post(
        "/categories",
        json={"code": "drinks", "description_en": "Drinks", "description_nl": "Dranken"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["code"] == "drinks"


def test_create_category_rejects_duplicate_code(client, auth_headers):
    client.post(
        "/categories",
        json={"code": "dupe-cat", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )
    response = client.post(
        "/categories",
        json={"code": "dupe-cat", "description_en": "Test again", "description_nl": "Test again"},
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_update_category_changes_descriptions(client, auth_headers):
    create_response = client.post(
        "/categories",
        json={"code": "update-cat", "description_en": "Original", "description_nl": "Origineel"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]

    update_response = client.put(
        f"/categories/{category_id}",
        json={"description_en": "Updated", "description_nl": "Bijgewerkt"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["description_en"] == "Updated"


def test_delete_category_succeeds(client, auth_headers):
    create_response = client.post(
        "/categories",
        json={"code": "delete-cat", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )
    category_id = create_response.json()["id"]

    delete_response = client.delete(f"/categories/{category_id}", headers=auth_headers)

    assert delete_response.status_code == 204