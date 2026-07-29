from src.product_management.models import Allergen, Item


def test_create_allergen_requires_auth(client):
    response = client.post(
        "/allergens",
        json={"code": "test", "description_en": "Test", "description_nl": "Test"},
    )

    assert response.status_code == 401


def test_create_allergen_succeeds_with_auth(client, auth_headers):
    response = client.post(
        "/allergens",
        json={"code": "test-allergen", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["code"] == "test-allergen"


def test_create_allergen_rejects_duplicate_code(client, auth_headers):
    client.post(
        "/allergens",
        json={"code": "dupe", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )
    response = client.post(
        "/allergens",
        json={"code": "dupe", "description_en": "Test again", "description_nl": "Test again"},
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_update_allergen_changes_descriptions(client, auth_headers):
    create_response = client.post(
        "/allergens",
        json={"code": "update-me", "description_en": "Original", "description_nl": "Origineel"},
        headers=auth_headers,
    )
    allergen_id = create_response.json()["id"]

    update_response = client.put(
        f"/allergens/{allergen_id}",
        json={"description_en": "Updated", "description_nl": "Bijgewerkt"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["description_en"] == "Updated"


def test_delete_allergen_succeeds(client, auth_headers):
    create_response = client.post(
        "/allergens",
        json={"code": "delete-me", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )
    allergen_id = create_response.json()["id"]

    delete_response = client.delete(f"/allergens/{allergen_id}", headers=auth_headers)

    assert delete_response.status_code == 204


def test_list_items_endpoint_returns_empty_list_when_no_items(client):
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == []


def test_list_items_endpoint_returns_seeded_item(client, db_session):
    db_session.add(Item(name="Frikandel"))
    db_session.commit()

    response = client.get("/items")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Frikandel"


def test_list_allergens_endpoint(client, db_session):
    db_session.add(Allergen(code="gluten", description_en="Gluten", description_nl="Gluten"))
    db_session.commit()

    response = client.get("/allergens")

    assert response.status_code == 200
    assert response.json()[0]["code"] == "gluten"
