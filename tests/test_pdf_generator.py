from src.product_management.models import Allergen, Item


def test_download_pdf_endpoint_returns_pdf_file(client, db_session):
    gluten = Allergen(code="gluten", description_en="Gluten", description_nl="Gluten")
    item = Item(name="Bread", allergens=[gluten])
    db_session.add(item)
    db_session.commit()

    response = client.get("/items/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_download_pdf_endpoint_rejects_invalid_language(client):
    response = client.get("/items/pdf?language=fr")

    assert response.status_code == 422
