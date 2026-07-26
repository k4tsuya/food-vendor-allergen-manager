from src.product_management.models import Item, Allergen
from src.product_management.models import Admin
from src.product_management.core.security import hash_password

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


def test_gluten_free_endpoint_excludes_gluten_items(client, db_session):
    gluten = Allergen(code="gluten", description_en="Gluten", description_nl="Gluten")
    item_with_gluten = Item(name="Bread", allergens=[gluten])
    item_without_gluten = Item(name="Fishstick")

    db_session.add_all([item_with_gluten, item_without_gluten])
    db_session.commit()

    response = client.get("/gluten-free")

    names = [i["name"] for i in response.json()]
    assert names == ["Fishstick"]


def test_download_pdf_endpoint_returns_pdf_file(client, db_session):
    gluten = Allergen(code="gluten", description_en="Gluten", description_nl="Gluten")
    item = Item(name="Bread", allergens=[gluten])
    db_session.add(item)
    db_session.commit()

    response = client.get("/items/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"


def test_download_pdf_endpoint_rejects_invalid_language(client):
    response = client.get("/items/pdf?language=fr")

    assert response.status_code == 422
    
    

def get_auth_headers(client, db_session):
    db_session.add(Admin(username="testadmin", hashed_password=hash_password("testpass123")))
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_item_requires_auth(client):
    response = client.post("/items", json={"name": "Test", "allergen_codes": [], "meat_type_codes": []})

    assert response.status_code == 401


def test_create_item_succeeds_with_auth(client, db_session):
    headers = get_auth_headers(client, db_session)

    response = client.post(
        "/items",
        json={"name": "Test Item", "category_key": "snacks", "allergen_codes": [], "meat_type_codes": []},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["item"]["name"] == "Test Item"


def test_create_item_warns_on_invalid_allergen_code(client, db_session):
    headers = get_auth_headers(client, db_session)

    response = client.post(
        "/items",
        json={"name": "Test Item", "allergen_codes": ["not-real"], "meat_type_codes": []},
        headers=headers,
    )

    assert response.status_code == 201
    assert "not-real" in response.json()["warnings"][0]


def test_update_item_replaces_fields(client, db_session):
    headers = get_auth_headers(client, db_session)

    create_response = client.post(
        "/items",
        json={"name": "Original", "category_key": "snacks", "allergen_codes": [], "meat_type_codes": []},
        headers=headers,
    )
    item_id = create_response.json()["item"]["id"]

    update_response = client.put(
        f"/items/{item_id}",
        json={"name": "Updated", "category_key": "bakery", "allergen_codes": [], "meat_type_codes": []},
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["item"]["name"] == "Updated"
    assert update_response.json()["item"]["category_key"] == "bakery"


def test_update_nonexistent_item_returns_404(client, db_session):
    headers = get_auth_headers(client, db_session)

    response = client.put(
        "/items/9999",
        json={"name": "Doesn't matter", "allergen_codes": [], "meat_type_codes": []},
        headers=headers,
    )

    assert response.status_code == 404


def test_delete_item_succeeds(client, db_session):
    headers = get_auth_headers(client, db_session)

    create_response = client.post(
        "/items",
        json={"name": "To Delete", "allergen_codes": [], "meat_type_codes": []},
        headers=headers,
    )
    item_id = create_response.json()["item"]["id"]

    delete_response = client.delete(f"/items/{item_id}", headers=headers)

    assert delete_response.status_code == 204


def test_delete_nonexistent_item_returns_404(client, db_session):
    headers = get_auth_headers(client, db_session)

    response = client.delete("/items/9999", headers=headers)

    assert response.status_code == 404


def test_delete_item_requires_auth(client):
    response = client.delete("/items/1")

    assert response.status_code == 401