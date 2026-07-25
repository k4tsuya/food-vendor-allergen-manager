from src.product_management.models import Item, Allergen


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