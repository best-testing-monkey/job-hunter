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
    assert b'id="threshold-slider"' in response.data


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
    assert b'id="threshold-slider"' in response.data
    assert b'data-sort-key="name"' in response.data
    assert b'data-sort-key="match-count"' in response.data
    assert b'data-sort-key="since-new-match"' in response.data
    assert b'id="resume-match-data"' in response.data


def test_register_resume_post(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    content = "# My Resume\nExperienced developer"
    response = client.post("/resumes", data={"name": "Test CV", "content": content})
    assert response.status_code == 302
    assert response.location.endswith("/resumes/1")

    response = client.get("/")
    assert response.status_code == 200
    assert b"Test CV" in response.data

    from pathlib import Path
    resume_file = Path(app.config["RESUMES_DIR"]) / "1.md"
    assert resume_file.exists()
    assert resume_file.read_text() == content


def test_register_resume_post_blank_name(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    content = "# My Resume\nExperienced developer"
    response = client.post("/resumes", data={"name": "", "content": content})
    assert response.status_code == 200
    assert b"error" in response.data.lower()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resumes = db.list_resumes(conn)
    conn.close()

    assert len(resumes) == 0


def test_register_resume_post_whitespace_name(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    content = "# My Resume\nExperienced developer"
    response = client.post("/resumes", data={"name": "   ", "content": content})
    assert response.status_code == 200
    assert b"error" in response.data.lower()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resumes = db.list_resumes(conn)
    conn.close()

    assert len(resumes) == 0


def test_register_resume_post_blank_content(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    response = client.post("/resumes", data={"name": "Test CV", "content": ""})
    assert response.status_code == 200
    assert b"error" in response.data.lower()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resumes = db.list_resumes(conn)
    conn.close()

    assert len(resumes) == 0


def test_register_resume_post_whitespace_content(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    response = client.post("/resumes", data={"name": "Test CV", "content": "   \n  \t  "})
    assert response.status_code == 200
    assert b"error" in response.data.lower()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resumes = db.list_resumes(conn)
    conn.close()

    assert len(resumes) == 0


def test_register_resume_post_blank_name_preserves_content(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    content = "# My Resume\nExperienced developer"
    response = client.post("/resumes", data={"name": "", "content": content})
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert content in response_text


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
    assert b"404" in response.data
    assert b"Not Found" in response.data
    assert b"job-hunter" in response.data


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


def test_edit_resume_post_blank_name(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    original_name = "My Resume"
    new_name = ""
    new_content = "# Updated Resume\nSenior developer"

    response = client.post(f"/resumes/{resume_id}/edit", data={"name": new_name, "content": new_content})
    assert response.status_code == 200
    assert b"error" in response.data.lower()

    conn = db.get_connection(app.config["DATABASE"])
    resume = db.get_resume(conn, resume_id)
    conn.close()

    assert resume["name"] == original_name


def test_edit_resume_post_whitespace_name(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    original_name = "My Resume"
    new_name = "   "
    new_content = "# Updated Resume\nSenior developer"

    response = client.post(f"/resumes/{resume_id}/edit", data={"name": new_name, "content": new_content})
    assert response.status_code == 200
    assert b"error" in response.data.lower()

    conn = db.get_connection(app.config["DATABASE"])
    resume = db.get_resume(conn, resume_id)
    conn.close()

    assert resume["name"] == original_name


def test_edit_resume_post_blank_content(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    original_content = "# My Resume"
    new_name = "Updated Resume"
    new_content = ""

    response = client.post(f"/resumes/{resume_id}/edit", data={"name": new_name, "content": new_content})
    assert response.status_code == 200
    assert b"error" in response.data.lower()

    conn = db.get_connection(app.config["DATABASE"])
    resume = db.get_resume(conn, resume_id)
    conn.close()

    assert resume["content"] == original_content


def test_edit_resume_post_blank_name_preserves_submitted_values(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    new_name = ""
    new_content = "# Updated Resume\nSenior developer"

    response = client.post(f"/resumes/{resume_id}/edit", data={"name": new_name, "content": new_content})
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert new_content in response_text


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


def test_rematch_status_not_running(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    response = client.get(f"/resumes/{resume_id}/rematch-status")
    assert response.status_code == 200
    assert response.get_json() == {"running": False}


def test_rematch_status_not_found(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    conn.close()

    response = client.get("/resumes/999999/rematch-status")
    assert response.status_code == 404


def test_rematch_status_running_flag_set(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.set_rematch_running(conn, resume_id, True)
    conn.close()

    response = client.get(f"/resumes/{resume_id}/rematch-status")
    assert response.status_code == 200
    assert response.get_json() == {"running": True}


def test_rematch_exception_clears_running_flag(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    conn.close()

    def mock_parse_job_file(path):
        return {
            "title": "Software Engineer",
            "location": "San Francisco",
            "workplace": "remote",
            "source": "https://example.com/job1",
        }

    def mock_site_name_for(job_file):
        return "TechCorp"

    class SyncThread:
        def __init__(self, *args, **kwargs):
            self.target = kwargs.get("target")
            self.args = kwargs.get("args", ())

        def start(self):
            self.target(*self.args)

    def mock_run_embed_match_raises(path):
        raise Exception("Matcher failed")

    with patch("webapp.matcher.run_embed_match", side_effect=mock_run_embed_match_raises):
        with patch("webapp.jobs.parse_job_file", side_effect=mock_parse_job_file):
            with patch("webapp.jobs.site_name_for", side_effect=mock_site_name_for):
                with patch("threading.Thread", SyncThread):
                    try:
                        response = client.post(f"/resumes/{resume_id}/rematch")
                    except Exception:
                        pass

    conn = db.get_connection(app.config["DATABASE"])
    resume = db.get_resume(conn, resume_id)
    conn.close()

    assert resume["rematch_running"] == 0


def test_resume_list_with_matches_includes_match_data(tmp_path):
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
        job_posted="2026-09-25T10:00:00Z",
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
        score=0.75,
        computed_at="2024-01-01T00:00:00",
        job_posted="2026-09-20T10:00:00Z",
    )
    conn.close()

    response = client.get("/")
    assert response.status_code == 200
    assert b"My Resume" in response.data
    assert b'id="resume-match-data"' in response.data
    response_text = response.get_data(as_text=True)
    assert '"score": 0.95' in response_text
    assert '"score": 0.75' in response_text
    assert '"status": "New"' in response_text
    assert f'data-resume-id="{resume_id}"' in response_text


def test_update_match_status_valid(tmp_path):
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
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.post(f"/matches/{match_id}/status", data={"status": "Applied"})
    assert response.status_code == 302
    assert response.location.endswith(f"/resumes/{resume_id}")

    conn = db.get_connection(app.config["DATABASE"])
    match = db.get_match(conn, match_id)
    conn.close()

    assert match["status"] == "Applied"


def test_update_match_status_invalid_status(tmp_path):
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
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.post(f"/matches/{match_id}/status", data={"status": "InvalidStatus"})
    assert response.status_code == 400

    conn = db.get_connection(app.config["DATABASE"])
    match = db.get_match(conn, match_id)
    conn.close()

    assert match["status"] == "New"


def test_update_match_status_not_found(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    conn.close()

    response = client.post("/matches/999999/status", data={"status": "Applied"})
    assert response.status_code == 404


def test_job_detail_with_valid_match(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    job_file = tmp_path / "job1.md"
    job_file.write_text("""# Software Engineer

- Source: https://example.com/job1
- Client: TechCorp
- Location: San Francisco
- Workplace: remote

## Description

This is a great job posting. You will work on exciting projects.
""")

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file=str(job_file),
        title="Software Engineer",
        site="TechCorp",
        location="San Francisco",
        workplace="remote",
        source_url="https://example.com/job1",
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.get(f"/jobs/{match_id}")
    assert response.status_code == 200
    assert b"Software Engineer" in response.data
    assert b"This is a great job posting" in response.data
    assert b"San Francisco" in response.data
    assert b"remote" in response.data
    assert b"View original posting" in response.data


def test_job_detail_not_found(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    client = app.test_client()

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    conn.close()

    response = client.get("/jobs/999999")
    assert response.status_code == 404


def test_job_detail_renders_markdown(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    job_file = tmp_path / "job1.md"
    job_file.write_text("""# Software Engineer

- Source: https://example.com/job1
- Client: TechCorp
- Location: San Francisco
- Workplace: remote

## Description

### Duties

- Write tests
- Fix bugs

**Must** know Python
""")

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file=str(job_file),
        title="Software Engineer",
        site="TechCorp",
        location="San Francisco",
        workplace="remote",
        source_url="https://old.example/x",
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.get(f"/jobs/{match_id}")
    assert response.status_code == 200
    assert b"<h3>Duties</h3>" in response.data
    assert b"<li>Write tests</li>" in response.data
    assert b"<li>Fix bugs</li>" in response.data
    assert b"<strong>Must</strong>" in response.data
    assert b'<div class="job-description">' in response.data
    assert b"<pre" not in response.data


def test_job_detail_escapes_html(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    job_file = tmp_path / "job1.md"
    job_file.write_text("""# Software Engineer

- Source: https://example.com/job1
- Client: TechCorp
- Location: San Francisco
- Workplace: remote

## Description

<script>alert(1)</script>
""")

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file=str(job_file),
        title="Software Engineer",
        site="TechCorp",
        location="San Francisco",
        workplace="remote",
        source_url="https://example.com/job1",
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.get(f"/jobs/{match_id}")
    assert response.status_code == 200
    assert b"&lt;script&gt;" in response.data
    assert b"<script>alert(1)</script>" not in response.data


def test_job_detail_uses_source_from_job_file(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    job_file = tmp_path / "job1.md"
    job_file.write_text("""# Software Engineer

- Source: https://example.com/job1
- Client: TechCorp
- Location: San Francisco
- Workplace: remote

## Description

This is a great job posting.
""")

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file=str(job_file),
        title="Software Engineer",
        site="TechCorp",
        location="San Francisco",
        workplace="remote",
        source_url="https://old.example/x",
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.get(f"/jobs/{match_id}")
    assert response.status_code == 200
    assert b'href="https://example.com/job1"' in response.data
    assert b"https://old.example/x" not in response.data


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 16


def _screenshot_client(tmp_path, job_file_str=None, with_png=True):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    (tmp_path / "jobs").mkdir(exist_ok=True)
    job_file = tmp_path / "jobs" / "a-1-x.md"
    job_file.write_text("# x")
    if with_png:
        (tmp_path / "screenshots").mkdir(exist_ok=True)
        (tmp_path / "screenshots" / "a-1-x.png").write_bytes(PNG_BYTES)
    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "R", "# R")
    db.upsert_match(
        conn, resume_id=resume_id, job_file=job_file_str or str(job_file), title="x",
        site="s", location="l", workplace="remote", source_url="https://e.com/1",
        score=0.5, computed_at="2024-01-01T00:00:00",
    )
    match_id = db.get_matches(conn, resume_id)[0]["id"]
    conn.close()
    return app.test_client(), match_id


def test_job_screenshot_served(tmp_path):
    client, match_id = _screenshot_client(tmp_path)
    response = client.get(f"/jobs/{match_id}/screenshot")
    assert response.status_code == 200
    assert response.content_type == "image/png"
    assert response.data == PNG_BYTES


def test_job_screenshot_missing_png_404(tmp_path):
    client, match_id = _screenshot_client(tmp_path, with_png=False)
    assert client.get(f"/jobs/{match_id}/screenshot").status_code == 404


def test_job_screenshot_unknown_id_404(tmp_path):
    client, _ = _screenshot_client(tmp_path)
    assert client.get("/jobs/999999/screenshot").status_code == 404


def test_job_screenshot_non_int_id_404(tmp_path):
    client, _ = _screenshot_client(tmp_path)
    assert client.get("/jobs/abc/screenshot").status_code == 404


def test_job_screenshot_traversal_urls_404(tmp_path):
    client, _ = _screenshot_client(tmp_path)
    assert client.get("/jobs/1/screenshot/../../etc/passwd").status_code == 404
    assert client.get("/jobs/%2e%2e%2f/screenshot").status_code == 404


def test_job_screenshot_dotdot_job_file_never_serves_outside(tmp_path):
    (tmp_path / "jobs").mkdir()
    (tmp_path / "jobs" / "a-1-x.png").write_bytes(PNG_BYTES)
    dotdot = f"{tmp_path}/jobs/../jobs/a-1-x.md"
    client, match_id = _screenshot_client(tmp_path, job_file_str=dotdot, with_png=False)
    assert client.get(f"/jobs/{match_id}/screenshot").status_code == 404


def test_job_screenshot_symlink_escape_404(tmp_path):
    client, match_id = _screenshot_client(tmp_path, with_png=False)
    (tmp_path / "screenshots").mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(PNG_BYTES)
    (tmp_path / "screenshots" / "a-1-x.png").symlink_to(outside)
    assert client.get(f"/jobs/{match_id}/screenshot").status_code == 404


def test_job_detail_with_screenshot(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    (tmp_path / "jobs").mkdir(exist_ok=True)
    job_file = tmp_path / "jobs" / "a-1-x.md"
    job_file.write_text("""# Software Engineer

- Source: https://example.com/job1
- Client: TechCorp
- Location: San Francisco
- Workplace: remote

## Description

This is a great job posting. You will work on exciting projects.
""")

    (tmp_path / "screenshots").mkdir(exist_ok=True)
    (tmp_path / "screenshots" / "a-1-x.png").write_bytes(PNG_BYTES)

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file=str(job_file),
        title="Software Engineer",
        site="TechCorp",
        location="San Francisco",
        workplace="remote",
        source_url="https://example.com/job1",
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.get(f"/jobs/{match_id}")
    assert response.status_code == 200
    assert b'<details class="job-screenshot">' in response.data
    assert b"<summary>Screenshot of original posting</summary>" in response.data
    assert b'<img src="/jobs/' in response.data
    assert b'/screenshot" alt="Screenshot of the original job posting" loading="lazy">' in response.data
    assert b"View original posting" in response.data


def test_job_detail_without_screenshot(tmp_path):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "test.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    client = app.test_client()

    (tmp_path / "jobs").mkdir(exist_ok=True)
    job_file = tmp_path / "jobs" / "b-2-y.md"
    job_file.write_text("""# Product Manager

- Source: https://example.com/job2
- Client: StartupCorp
- Location: Remote
- Workplace: remote

## Description

Lead our product strategy.
""")

    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    resume_id = db.create_resume(conn, app.config["RESUMES_DIR"], "My Resume", "# My Resume")
    db.upsert_match(
        conn,
        resume_id=resume_id,
        job_file=str(job_file),
        title="Product Manager",
        site="StartupCorp",
        location="Remote",
        workplace="remote",
        source_url="https://example.com/job2",
        score=0.88,
        computed_at="2024-01-01T00:00:00",
    )
    matches = db.get_matches(conn, resume_id)
    match_id = matches[0]["id"]
    conn.close()

    response = client.get(f"/jobs/{match_id}")
    assert response.status_code == 200
    assert b"job-screenshot" not in response.data
    assert b"/screenshot" not in response.data
    assert b"Product Manager" in response.data
    assert b"Lead our product strategy" in response.data
    assert b"View original posting" in response.data
