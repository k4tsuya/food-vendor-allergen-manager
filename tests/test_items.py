def test_create_item_requires_auth(client):
    response = client.post("/items", json={"name": "Test", "allergen_codes": [], "meat_type_codes": []})

    assert response.status_code == 401


def test_create_item_succeeds_with_auth(client, auth_headers):
    response = client.post(
        "/items",
        json={"name": "Test Item", "category_key": "snacks", "allergen_codes": [], "meat_type_codes": []},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["item"]["name"] == "Test Item"


def test_create_item_warns_on_invalid_allergen_code(client, auth_headers):
    response = client.post(
        "/items",
        json={"name": "Test Item", "allergen_codes": ["not-real"], "meat_type_codes": []},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert "not-real" in response.json()["warnings"][0]


def test_update_item_replaces_fields(client, auth_headers):
    create_response = client.post(
        "/items",
        json={"name": "Original", "category_key": "snacks", "allergen_codes": [], "meat_type_codes": []},
        headers=auth_headers,
    )
    item_id = create_response.json()["item"]["id"]

    update_response = client.put(
        f"/items/{item_id}",
        json={"name": "Updated", "category_key": "bakery", "allergen_codes": [], "meat_type_codes": []},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["item"]["name"] == "Updated"
    assert update_response.json()["item"]["category_key"] == "bakery"


def test_update_nonexistent_item_returns_404(client, auth_headers):
    response = client.put(
        "/items/9999",
        json={"name": "Doesn't matter", "allergen_codes": [], "meat_type_codes": []},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_delete_item_succeeds(client, auth_headers):
    create_response = client.post(
        "/items",
        json={"name": "To Delete", "allergen_codes": [], "meat_type_codes": []},
        headers=auth_headers,
    )
    item_id = create_response.json()["item"]["id"]

    delete_response = client.delete(f"/items/{item_id}", headers=auth_headers)

    assert delete_response.status_code == 204


def test_delete_nonexistent_item_returns_404(client, auth_headers):
    response = client.delete("/items/9999", headers=auth_headers)

    assert response.status_code == 404


def test_delete_item_requires_auth(client):
    response = client.delete("/items/1")

    assert response.status_code == 401
    

