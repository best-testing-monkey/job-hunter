from webapp import create_app


def test_health():
    app = create_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_theme_preview():
    app = create_app()
    client = app.test_client()
    response = client.get("/theme-preview")
    assert response.status_code == 200
    assert b"Theme preview" in response.data
    assert b'<button class="btn-accent">Sample button</button>' in response.data
