def test_create_meat_type_requires_auth(client):
    response = client.post(
        "/meat-types",
        json={"code": "test", "description_en": "Test", "description_nl": "Test"},
    )

    assert response.status_code == 401


def test_create_meat_type_succeeds_with_auth(client, auth_headers):
    response = client.post(
        "/meat-types",
        json={"code": "test-meat", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["code"] == "test-meat"


def test_create_meat_type_rejects_duplicate_code(client, auth_headers):
    client.post(
        "/meat-types",
        json={"code": "dupe-meat", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )
    response = client.post(
        "/meat-types",
        json={"code": "dupe-meat", "description_en": "Test again", "description_nl": "Test again"},
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_update_meat_type_changes_descriptions(client, auth_headers):
    create_response = client.post(
        "/meat-types",
        json={"code": "update-meat", "description_en": "Original", "description_nl": "Origineel"},
        headers=auth_headers,
    )
    meat_type_id = create_response.json()["id"]

    update_response = client.put(
        f"/meat-types/{meat_type_id}",
        json={"description_en": "Updated", "description_nl": "Bijgewerkt"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["description_en"] == "Updated"


def test_delete_meat_type_succeeds(client, auth_headers):
    create_response = client.post(
        "/meat-types",
        json={"code": "delete-meat", "description_en": "Test", "description_nl": "Test"},
        headers=auth_headers,
    )
    meat_type_id = create_response.json()["id"]

    delete_response = client.delete(f"/meat-types/{meat_type_id}", headers=auth_headers)

    assert delete_response.status_code == 204
