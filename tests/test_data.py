from src.product_management.models import Item, Allergen, MeatType, Category


def test_export_requires_auth(client):
    response = client.get("/data/export")
    assert response.status_code == 401


def test_import_requires_auth(client):
    response = client.post("/data/import", json={})
    assert response.status_code == 401


def test_export_includes_all_sections(client, db_session, auth_headers):
    db_session.add(Allergen(code="gluten", description_en="Gluten", description_nl="Gluten"))
    db_session.add(Item(name="Bread"))
    db_session.commit()

    response = client.get("/data/export", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "allergens" in data
    assert "meat_types" in data
    assert "categories" in data
    assert "items" in data
    assert "settings" in data
    assert data["allergens"][0]["code"] == "gluten"


def test_import_replaces_existing_data(client, db_session, auth_headers):
    db_session.add(Item(name="Old Item"))
    db_session.commit()

    import_payload = {
        "exported_at": "2026-01-01T00:00:00",
        "allergens": [{"code": "milk", "description_en": "Milk", "description_nl": "Melk"}],
        "meat_types": [],
        "categories": [],
        "items": [
            {
                "name": "New Item",
                "category_key": None,
                "allergen_codes": ["milk"],
                "meat_type_codes": [],
            }
        ],
        "settings": {
            "meat_tracking_enabled": False,
            "company_name": "Test Co",
            "site_title_en": "Test",
            "site_title_nl": "Test",
            "default_language": "en",
        },
    }

    response = client.post("/data/import", json=import_payload, headers=auth_headers)
