import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # A rematch writes from a background thread while the request thread (or
    # a page reload) may hold a read connection open on the same file —
    # without this, SQLite raises "database is locked" immediately instead
    # of waiting, which silently truncates an in-progress rematch's writes.
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            content TEXT,
            rematch_running INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            resume_id INTEGER NOT NULL REFERENCES resumes(id),
            job_file TEXT NOT NULL,
            title TEXT NOT NULL,
            site TEXT NOT NULL,
            location TEXT,
            workplace TEXT,
            source_url TEXT,
            score REAL NOT NULL,
            computed_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'New',
            job_posted TEXT,
            UNIQUE(resume_id, job_file)
        )
    """)
    conn.commit()


def get_resume(conn: sqlite3.Connection, resume_id: int) -> sqlite3.Row | None:
    cursor = conn.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    return cursor.fetchone()


def list_resumes(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    cursor = conn.execute("SELECT * FROM resumes")
    return cursor.fetchall()


def upsert_match(
    conn: sqlite3.Connection,
    resume_id: int,
    job_file: str,
    title: str,
    site: str,
    location: str | None,
    workplace: str | None,
    source_url: str | None,
    score: float,
    computed_at: str,
    job_posted: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO matches (resume_id, job_file, title, site, location, workplace, source_url, score, computed_at, job_posted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(resume_id, job_file) DO UPDATE SET
            title=excluded.title,
            site=excluded.site,
            location=excluded.location,
            workplace=excluded.workplace,
            source_url=excluded.source_url,
            score=excluded.score,
            computed_at=excluded.computed_at,
            job_posted=excluded.job_posted
        """,
        (resume_id, job_file, title, site, location, workplace, source_url, score, computed_at, job_posted),
    )
    conn.commit()


def get_matches(
    conn: sqlite3.Connection,
    resume_id: int,
    order_by: str = "score",
) -> list[sqlite3.Row]:
    allowed_columns = {"score", "title", "site"}
    if order_by not in allowed_columns:
        order_by = "score"

    query = f"SELECT * FROM matches WHERE resume_id = ? ORDER BY {order_by}"
    if order_by == "score":
        query += " DESC"

    cursor = conn.execute(query, (resume_id,))
    return cursor.fetchall()


def get_match(conn: sqlite3.Connection, match_id: int) -> sqlite3.Row | None:
    cursor = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    return cursor.fetchone()


def update_match_status(conn: sqlite3.Connection, match_id: int, status: str) -> None:
    valid_statuses = {"New", "Non-match", "Applied", "Done"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}")
    conn.execute(
        "UPDATE matches SET status = ? WHERE id = ?",
        (status, match_id),
    )
    conn.commit()


def create_resume(
    conn: sqlite3.Connection,
    resumes_dir: str,
    name: str,
    content: str,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO resumes (name, file_path, created_at, content) VALUES (?, ?, ?, ?)",
        (name, "", created_at, content),
    )
    conn.commit()
    resume_id = cursor.lastrowid

    Path(resumes_dir).mkdir(parents=True, exist_ok=True)
    file_path = str(Path(resumes_dir) / f"{resume_id}.md")
    Path(file_path).write_text(content)

    conn.execute(
        "UPDATE resumes SET file_path = ? WHERE id = ?",
        (file_path, resume_id),
    )
    conn.commit()

    return resume_id


def update_resume(
    conn: sqlite3.Connection,
    resume_id: int,
    name: str,
    content: str,
) -> None:
    conn.execute(
        "UPDATE resumes SET name = ?, content = ? WHERE id = ?",
        (name, content, resume_id),
    )
    conn.commit()

    cursor = conn.execute("SELECT file_path FROM resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    if row:
        file_path = row["file_path"]
        Path(file_path).write_text(content)


def delete_resume(
    conn: sqlite3.Connection,
    resume_id: int,
) -> None:
    cursor = conn.execute("SELECT file_path FROM resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    file_path = row["file_path"] if row else None

    conn.execute("DELETE FROM matches WHERE resume_id = ?", (resume_id,))
    conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    conn.commit()

    if file_path:
        Path(file_path).unlink(missing_ok=True)


def set_rematch_running(conn: sqlite3.Connection, resume_id: int, running: bool) -> None:
    value = 1 if running else 0
    conn.execute(
        "UPDATE resumes SET rematch_running = ? WHERE id = ?",
        (value, resume_id),
    )
    conn.commit()
