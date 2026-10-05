import sqlite3
from webapp import create_app, db

OLD_SCHEMA = """
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, file_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL, content TEXT, rematch_running INTEGER NOT NULL DEFAULT 0
)"""


def test_migration_from_old_schema(tmp_path):
    path = str(tmp_path / "old.db")
    raw = sqlite3.connect(path)
    raw.execute(OLD_SCHEMA)
    raw.execute("INSERT INTO resumes (name, file_path, created_at) VALUES ('r', 'f', 't')")
    raw.commit()
    raw.close()
    conn = db.get_connection(path)
    db.init_db(conn)
    db.init_db(conn)  # idempotent
    s = db.get_travel_settings(conn, 1)
    assert s == {"home_city": None, "max_travel_minutes": None, "travel_mode": "car"}
    db.set_travel_settings(conn, 1, "Almere", 90, "transit")
    assert db.get_travel_settings(conn, 1)["travel_mode"] == "transit"


def _setup(tmp_path, home="Almere", max_min=90):
    app = create_app()
    app.config["DATABASE"] = str(tmp_path / "t.db")
    app.config["RESUMES_DIR"] = str(tmp_path / "resumes")
    conn = db.get_connection(app.config["DATABASE"])
    db.init_db(conn)
    rid = db.create_resume(conn, app.config["RESUMES_DIR"], "R", "content")
    if home:
        db.set_travel_settings(conn, rid, home, max_min, "car")
    for title, loc, wp in [
        ("SpainJob", "Barcelona, Spain", "On-site"),
        ("NearJob", "Amsterdam", "On-site"),
        ("RemoteJob", "Madrid, Spain", "Fully Remote"),
        ("MysteryJob", None, None),
    ]:
        db.upsert_match(conn, rid, f"/nonexistent/{title}.md", title, "site", loc, wp, None, 0.9, "t")
    conn.close()
    return app.test_client(), rid


def _page(client, rid, q=""):
    r = client.get(f"/resumes/{rid}{q}")
    assert r.status_code == 200
    return r.data.decode()


def test_filter_excludes_far_keeps_remote_and_unknown(tmp_path):
    client, rid = _setup(tmp_path)
    html = _page(client, rid)
    assert "SpainJob" not in html
    assert "NearJob" in html and "RemoteJob" in html and "MysteryJob" in html
    assert "Remote</span>" in html
    assert "Unknown location" in html
    assert " min</span>" in html
    assert "1 job hidden by travel limit" in html


def test_toggle_off_shows_all(tmp_path):
    client, rid = _setup(tmp_path)
    html = _page(client, rid, "?travel_filter=0")
    assert "SpainJob" in html and "NearJob" in html


def test_no_settings_no_filtering(tmp_path):
    client, rid = _setup(tmp_path, home=None)
    html = _page(client, rid)
    assert "SpainJob" in html and "hidden by travel limit" not in html


def test_unresolvable_home_city_warns_no_crash(tmp_path):
    client, rid = _setup(tmp_path, home="Qwertyville Nowhere")
    html = _page(client, rid)
    assert "could not be resolved" in html
    assert "SpainJob" in html


def test_save_settings_and_validation(tmp_path):
    client, rid = _setup(tmp_path, home=None)
    url = f"/resumes/{rid}/travel"
    for bad in [
        {"home_city": "Almere", "max_travel_minutes": "abc", "travel_mode": "car"},
        {"home_city": "Almere", "max_travel_minutes": "0", "travel_mode": "car"},
        {"home_city": "Almere", "max_travel_minutes": "", "travel_mode": "car"},
        {"home_city": "Zzzzzz", "max_travel_minutes": "60", "travel_mode": "car"},
        {"home_city": "Almere", "max_travel_minutes": "60", "travel_mode": "plane"},
    ]:
        assert client.post(url, data=bad).status_code == 400
    r = client.post(url, data={"home_city": "Almere", "max_travel_minutes": "90", "travel_mode": "car"})
    assert r.status_code == 302
    assert "SpainJob" not in _page(client, rid)
    r = client.post(url, data={"home_city": "", "max_travel_minutes": "", "travel_mode": "car"})
    assert r.status_code == 302
    assert "SpainJob" in _page(client, rid)
    assert client.post("/resumes/999/travel", data={}).status_code == 404
