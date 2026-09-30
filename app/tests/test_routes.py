from unittest.mock import patch, MagicMock
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
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    response = client.get("/")
    assert response.status_code == 200
    assert b"Resumes" in response.data
    assert b"My Resume" in response.data
    assert b"No resumes registered yet" not in response.data


def test_register_resume_post(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    content = "# My Resume\nExperienced developer"
    response = client.post("/resumes", data={"name": "Test CV", "content": content})
    assert response.status_code == 302

    response = client.get("/")
    assert response.status_code == 200
    assert b"Test CV" in response.data

    from pathlib import Path
    resume_file = Path(app.config["RESUMES_DIR"]) / "1.md"
    assert resume_file.exists()
    assert resume_file.read_text() == content


def test_resume_detail_with_matches(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job1.txt",
        title="Software Engineer",
        site="TechCorp",
        location="San Francisco",
        workplace="remote",
        source_url="https://example.com/job1",
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job2.txt",
        title="Senior Engineer",
        site="TechCorp",
        location="New York",
        workplace="hybrid",
        source_url="https://example.com/job2",
        score=0.85,
        computed_at="2024-01-01T00:00:00",
    )
    conn.close()

    response = client.get(f"/resumes/{resume_id}")
    assert response.status_code == 200
    assert b"Software Engineer" in response.data
    assert b"Senior Engineer" in response.data


def test_resume_detail_with_no_matches(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    response = client.get(f"/resumes/{resume_id}")
    assert response.status_code == 200
    assert "No matches yet — run a rematch" in response.get_data(as_text=True)


def test_resume_detail_not_found(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    conn.close()

    response = client.get("/resumes/999999")
    assert response.status_code == 404


def test_rematch_resume(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    mock_results = [
        {"job_file": "jobs/job1.md", "score": 0.95},
        {"job_file": "jobs/job2.md", "score": 0.85},
    ]

    def mock_parse_job_file(path):
        if "job1" in str(path):
            return {
                "title": "Software Engineer",
                "location": "San Francisco",
                "workplace": "remote",
                "source": "https://example.com/job1",
            }
        else:
            return {
                "title": "Senior Engineer",
                "location": "New York",
                "workplace": "hybrid",
                "source": "https://example.com/job2",
            }

    def mock_site_name_for(job_file):
        return "TechCorp"

    class SyncThread:
        def __init__(self, *args, **kwargs):
            self.target = kwargs.get("target")
            self.args = kwargs.get("args", ())

        def start(self):
            self.target(*self.args)

    with patch("webapp.matcher.run_embed_match", return_value=mock_results):
        with patch("webapp.jobs.parse_job_file", side_effect=mock_parse_job_file):
            with patch("webapp.jobs.site_name_for", side_effect=mock_site_name_for):
                with patch("threading.Thread", SyncThread):
                    response = client.post(f"/resumes/{resume_id}/rematch")

    assert response.status_code == 302
    assert response.location.endswith(f"/resumes/{resume_id}")

    conn = db.get_connection(app.config["DATABASE"])
    matches = db.get_matches(conn, resume_id)
    conn.close()

    assert len(matches) == 2
    assert matches[0]["title"] == "Software Engineer"
    assert matches[0]["score"] == 0.95
    assert matches[0]["site"] == "TechCorp"
    assert matches[1]["title"] == "Senior Engineer"
    assert matches[1]["score"] == 0.85


def test_edit_resume_get(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume\nExperienced developer")
    conn.close()

    response = client.get(f"/resumes/{resume_id}/edit")
    assert response.status_code == 200
    assert b"My Resume" in response.data
    assert b"# My Resume\nExperienced developer" in response.data


def test_edit_resume_get_not_found(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    conn.close()

    response = client.get("/resumes/999999/edit")
    assert response.status_code == 404


def test_edit_resume_post(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    new_name = "Updated Resume"
    new_content = "# Updated Resume\nSenior developer with 10 years experience"

    response = client.post(f"/resumes/{resume_id}/edit", data={"name": new_name, "content": new_content})
    assert response.status_code == 302
    assert response.location.endswith(f"/resumes/{resume_id}")

    conn = db.get_connection(app.config["DATABASE"])
    resume = db.get_resume(conn, resume_id)
    conn.close()

    assert resume["name"] == new_name
    assert resume["content"] == new_content

    from pathlib import Path
    resume_file = Path(app.config["RESUMES_DIR"]) / f"{resume_id}.md"
    assert resume_file.read_text() == new_content


def test_edit_resume_post_not_found(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    conn.close()

    response = client.post("/resumes/999999/edit", data={"name": "Test", "content": "Test"})
    assert response.status_code == 404


def test_delete_resume_with_matches(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job1.txt",
        title="Software Engineer",
        site="TechCorp",
        location="San Francisco",
        workplace="remote",
        source_url="https://example.com/job1",
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    resume = db.get_resume(conn, resume_id)
    file_path = resume["file_path"]
    conn.close()

    from pathlib import Path
    assert Path(file_path).exists()

    response = client.post(f"/resumes/{resume_id}/delete")
    assert response.status_code == 302
    assert response.location.endswith("/")

    response = client.get(f"/resumes/{resume_id}")
    assert response.status_code == 404

    conn = db.get_connection(app.config["DATABASE"])
    matches = db.get_matches(conn, resume_id)
    conn.close()

    assert len(matches) == 0

    assert not Path(file_path).exists()


def test_delete_resume_not_found(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    conn.close()

    response = client.post("/resumes/999999/delete")
    assert response.status_code == 404
