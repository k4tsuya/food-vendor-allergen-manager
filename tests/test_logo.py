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
    real_png_header = b"\x89PNG\r\n\x1a\n" + b"rest of fake but valid-looking png data"
    response = client.post(
        "/config/logo",
        files={"file": ("logo.png", io.BytesIO(real_png_header), "image/png")},
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


def test_upload_logo_rejects_fake_png(client, auth_headers):
    response = client.post(
        "/config/logo",
        files={"file": ("logo.png", io.BytesIO(b"not a real image"), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_upload_logo_rejects_svg_with_script(client, auth_headers):
    malicious_svg = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
    response = client.post(
        "/config/logo",
        files={"file": ("logo.svg", io.BytesIO(malicious_svg), "image/svg+xml")},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_upload_logo_accepts_valid_svg(client, auth_headers):
    valid_svg = b'<svg xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="5" r="4"/></svg>'
    response = client.post(
        "/config/logo",
        files={"file": ("logo.svg", io.BytesIO(valid_svg), "image/svg+xml")},
        headers=auth_headers,
    )
    assert response.status_code == 200
