from webapp.db import (
    get_connection,
    init_db,
    list_resumes,
    upsert_match,
    get_matches,
    get_match,
    update_match_status,
    get_resume,
    create_resume,
    update_resume,
    delete_resume,
    set_rematch_running,
)


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


def test_list_resumes_empty(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resumes = list_resumes(conn)
    assert len(resumes) == 0

    conn.close()


def test_list_resumes_multiple(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    create_resume(conn, str(resumes_dir), "Resume 1", "# Resume 1")
    create_resume(conn, str(resumes_dir), "Resume 2", "# Resume 2")
    create_resume(conn, str(resumes_dir), "Resume 3", "# Resume 3")

    resumes = list_resumes(conn)
    assert len(resumes) == 3

    conn.close()


def test_upsert_match_insert(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

    matches = get_matches(conn, resume_id)
    assert len(matches) == 0

    conn.close()


def test_get_matches_order_by_score_descending(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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


def test_get_resume_exists(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")
    resume = get_resume(conn, resume_id)

    assert resume is not None
    assert resume["id"] == resume_id
    assert resume["name"] == "My Resume"
    assert resume["file_path"] != ""

    conn.close()


def test_get_resume_not_found(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume = get_resume(conn, 999999)

    assert resume is None

    conn.close()


def test_create_resume(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    content = "# My Resume\n\nExperienced developer"
    resume_id = create_resume(conn, str(resumes_dir), "My Resume", content)

    assert isinstance(resume_id, int)
    assert resume_id > 0

    resume = get_resume(conn, resume_id)
    assert resume is not None
    assert resume["name"] == "My Resume"
    assert resume["content"] == content
    assert resume["file_path"] != ""

    file_path = resume["file_path"]
    assert (tmp_path / "resumes" / f"{resume_id}.md").exists()
    import pathlib
    assert pathlib.Path(file_path).read_text() == content

    conn.close()


def test_update_resume(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    content = "# Original Resume"
    resume_id = create_resume(conn, str(resumes_dir), "Original Name", content)

    original_resume = get_resume(conn, resume_id)
    original_file_path = original_resume["file_path"]

    new_content = "# Updated Resume\n\nNew content here"
    update_resume(conn, resume_id, "Updated Name", new_content)

    updated_resume = get_resume(conn, resume_id)
    assert updated_resume["name"] == "Updated Name"
    assert updated_resume["content"] == new_content
    assert updated_resume["file_path"] == original_file_path

    import pathlib
    assert pathlib.Path(original_file_path).read_text() == new_content

    conn.close()


def test_delete_resume(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    content = "# My Resume"
    resume_id = create_resume(conn, str(resumes_dir), "My Resume", content)

    resume = get_resume(conn, resume_id)
    file_path = resume["file_path"]

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

    matches_before = get_matches(conn, resume_id)
    assert len(matches_before) == 1

    delete_resume(conn, resume_id)

    resume_after = get_resume(conn, resume_id)
    assert resume_after is None

    matches_after = get_matches(conn, resume_id)
    assert len(matches_after) == 0

    import pathlib
    assert not pathlib.Path(file_path).exists()

    conn.close()


def test_delete_resume_missing_file(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    content = "# My Resume"
    resume_id = create_resume(conn, str(resumes_dir), "My Resume", content)

    resume = get_resume(conn, resume_id)
    file_path = resume["file_path"]

    import pathlib
    pathlib.Path(file_path).unlink()

    delete_resume(conn, resume_id)

    resume_after = get_resume(conn, resume_id)
    assert resume_after is None

    conn.close()


def test_delete_resume_twice(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    content = "# My Resume"
    resume_id = create_resume(conn, str(resumes_dir), "My Resume", content)

    delete_resume(conn, resume_id)

    delete_resume(conn, resume_id)

    resume = get_resume(conn, resume_id)
    assert resume is None

    conn.close()


def test_upsert_match_creates_with_new_status(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    assert matches[0]["status"] == "New"

    conn.close()


def test_get_match_returns_row(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    match_id = matches[0]["id"]
    match = get_match(conn, match_id)

    assert match is not None
    assert match["id"] == match_id
    assert match["title"] == "Software Engineer"
    assert match["status"] == "New"

    conn.close()


def test_get_match_returns_none_for_nonexistent_id(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_connection(str(db_path))
    init_db(conn)

    match = get_match(conn, 999999)
    assert match is None

    conn.close()


def test_update_match_status_changes_status(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    match_id = matches[0]["id"]

    update_match_status(conn, match_id, "Applied")

    match = get_match(conn, match_id)
    assert match["status"] == "Applied"

    conn.close()


def test_update_match_status_invalid_status_raises_error(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    match_id = matches[0]["id"]

    try:
        update_match_status(conn, match_id, "Bogus")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    match = get_match(conn, match_id)
    assert match["status"] == "New"

    conn.close()


def test_upsert_match_preserves_status_on_conflict(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
    match_id = matches[0]["id"]

    update_match_status(conn, match_id, "Applied")

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
        job_posted="2024-01-02",
    )

    match = get_match(conn, match_id)
    assert match["status"] == "Applied"
    assert match["score"] == 0.87
    assert match["title"] == "Senior Software Engineer"
    assert match["job_posted"] == "2024-01-02"

    conn.close()


def test_upsert_match_with_job_posted(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

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
        job_posted="2024-01-01",
    )

    matches = get_matches(conn, resume_id)
    assert len(matches) == 1
    assert matches[0]["job_posted"] == "2024-01-01"

    conn.close()


def test_set_rematch_running_true(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

    set_rematch_running(conn, resume_id, True)

    resume = get_resume(conn, resume_id)
    assert resume["rematch_running"] == 1

    conn.close()


def test_set_rematch_running_false(tmp_path):
    db_path = tmp_path / "test.db"
    resumes_dir = tmp_path / "resumes"
    conn = get_connection(str(db_path))
    init_db(conn)

    resume_id = create_resume(conn, str(resumes_dir), "My Resume", "# My Resume")

    set_rematch_running(conn, resume_id, True)
    resume = get_resume(conn, resume_id)
    assert resume["rematch_running"] == 1

    set_rematch_running(conn, resume_id, False)
    resume = get_resume(conn, resume_id)
    assert resume["rematch_running"] == 0

    conn.close()
