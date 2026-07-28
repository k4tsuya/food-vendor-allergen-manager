import io


def test_upload_logo_requires_auth(client):
    response = client.post(
        "/config/logo",
        files={"file": ("logo.png", io.BytesIO(b"fake image data"), "image/png")},
    )
    assert response.status_code == 401


def test_upload_logo_rejects_bad_extension(client, auth_headers):
    response = client.post(
        "/config/logo",
        files={"file": ("logo.txt", io.BytesIO(b"not an image"), "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_upload_logo_succeeds_and_sets_logo_path(client, auth_headers):
    response = client.post(
        "/config/logo",
        files={"file": ("logo.png", io.BytesIO(b"fake image data"), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["logo_path"] == "logo.png"


def test_delete_logo_clears_logo_path(client, auth_headers):
    client.post(
        "/config/logo",
        files={"file": ("logo.png", io.BytesIO(b"fake image data"), "image/png")},
        headers=auth_headers,
    )

    response = client.delete("/config/logo", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["logo_path"] is None