from webapp.db import get_connection, init_db, register_resume, list_resumes, upsert_match, get_matches


def test_db_schema(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]

    assert "matches" in tables
    assert "resumes" in tables
    conn.close()


def test_register_resume_first_call(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")
    assert isinstance(resume_id, int)
    assert resume_id > 0

    resumes = list_resumes(conn)
    assert len(resumes) == 1
    assert resumes[0]["name"] == "My Resume"
    assert resumes[0]["file_path"] == "/path/to/resume.pdf"
    assert resumes[0]["id"] == resume_id

    conn.close()


def test_register_resume_duplicate_file_path(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id1 = register_resume(conn, "My Resume", "/path/to/resume.pdf")
    resume_id2 = register_resume(conn, "Updated Resume Name", "/path/to/resume.pdf")

    assert resume_id1 == resume_id2

    resumes = list_resumes(conn)
    assert len(resumes) == 1

    conn.close()


def test_list_resumes_empty(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resumes = list_resumes(conn)
    assert len(resumes) == 0

    conn.close()


def test_list_resumes_multiple(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    register_resume(conn, "Resume 1", "/path/to/resume1.pdf")
    register_resume(conn, "Resume 2", "/path/to/resume2.pdf")
    register_resume(conn, "Resume 3", "/path/to/resume3.pdf")

    resumes = list_resumes(conn)
    assert len(resumes) == 3

    conn.close()


def test_upsert_match_insert(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")

    upsert_match(
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

    matches = get_matches(conn, resume_id)
    assert len(matches) == 1
    assert matches[0]["title"] == "Software Engineer"
    assert matches[0]["score"] == 0.95

    conn.close()


def test_upsert_match_update_on_conflict(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")

    upsert_match(
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

    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job1.txt",
        title="Senior Software Engineer",
        site="TechCorp",
        location="New York",
        workplace="hybrid",
        source_url="https://example.com/job1",
        score=0.87,
        computed_at="2024-01-02T00:00:00",
    )

    matches = get_matches(conn, resume_id)
    assert len(matches) == 1
    assert matches[0]["score"] == 0.87
    assert matches[0]["title"] == "Senior Software Engineer"
    assert matches[0]["location"] == "New York"

    conn.close()


def test_get_matches_empty(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")

    matches = get_matches(conn, resume_id)
    assert len(matches) == 0

    conn.close()


def test_get_matches_order_by_score_descending(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")

    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job1.txt",
        title="Job 1",
        site="Site1",
        location=None,
        workplace=None,
        source_url=None,
        score=0.75,
        computed_at="2024-01-01T00:00:00",
    )
    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job2.txt",
        title="Job 2",
        site="Site2",
        location=None,
        workplace=None,
        source_url=None,
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )
    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job3.txt",
        title="Job 3",
        site="Site3",
        location=None,
        workplace=None,
        source_url=None,
        score=0.85,
        computed_at="2024-01-01T00:00:00",
    )

    matches = get_matches(conn, resume_id, order_by="score")
    assert len(matches) == 3
    assert matches[0]["score"] == 0.95
    assert matches[1]["score"] == 0.85
    assert matches[2]["score"] == 0.75

    conn.close()


def test_get_matches_order_by_title(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")

    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job1.txt",
        title="Zebra Engineer",
        site="Site1",
        location=None,
        workplace=None,
        source_url=None,
        score=0.75,
        computed_at="2024-01-01T00:00:00",
    )
    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job2.txt",
        title="Apple Engineer",
        site="Site2",
        location=None,
        workplace=None,
        source_url=None,
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )

    matches = get_matches(conn, resume_id, order_by="title")
    assert len(matches) == 2
    assert matches[0]["title"] == "Apple Engineer"
    assert matches[1]["title"] == "Zebra Engineer"

    conn.close()


def test_get_matches_order_by_site(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")

    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job1.txt",
        title="Job 1",
        site="ZebraCorp",
        location=None,
        workplace=None,
        source_url=None,
        score=0.75,
        computed_at="2024-01-01T00:00:00",
    )
    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job2.txt",
        title="Job 2",
        site="AppleCorp",
        location=None,
        workplace=None,
        source_url=None,
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )

    matches = get_matches(conn, resume_id, order_by="site")
    assert len(matches) == 2
    assert matches[0]["site"] == "AppleCorp"
    assert matches[1]["site"] == "ZebraCorp"

    conn.close()


def test_get_matches_invalid_order_by_defaults_to_score(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = register_resume(conn, "My Resume", "/path/to/resume.pdf")

    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job1.txt",
        title="Job 1",
        site="Site1",
        location=None,
        workplace=None,
        source_url=None,
        score=0.75,
        computed_at="2024-01-01T00:00:00",
    )
    upsert_match(
        conn,
        resume_id=resume_id,
        job_file="job2.txt",
        title="Job 2",
        site="Site2",
        location=None,
        workplace=None,
        source_url=None,
        score=0.95,
        computed_at="2024-01-01T00:00:00",
    )

    matches = get_matches(conn, resume_id, order_by="invalid_column")
    assert len(matches) == 2
    assert matches[0]["score"] == 0.95

    conn.close()
