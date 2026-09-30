from webapp import create_app
from webapp import db


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


def test_resume_list_empty(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Resumes" in response.data
    assert b"No resumes registered yet" in response.data


def test_resume_list_with_one_resume(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    db.register_resume(conn, "My Resume", "/path/to/resume.pdf")
    conn.close()

    response = client.get("/")
    assert response.status_code == 200
    assert b"Resumes" in response.data
    assert b"My Resume" in response.data
    assert b"No resumes registered yet" not in response.data
