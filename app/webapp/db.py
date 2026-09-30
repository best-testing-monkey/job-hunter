import sqlite3
from datetime import datetime, timezone


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
            created_at TEXT NOT NULL
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
            UNIQUE(resume_id, job_file)
        )
    """)
    conn.commit()


def register_resume(conn: sqlite3.Connection, name: str, file_path: str) -> int:
    try:
        created_at = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "INSERT INTO resumes (name, file_path, created_at) VALUES (?, ?, ?)",
            (name, file_path, created_at),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor = conn.execute(
            "SELECT id FROM resumes WHERE file_path = ?",
            (file_path,),
        )
        row = cursor.fetchone()
        return row[0]


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
) -> None:
    conn.execute(
        """
        INSERT INTO matches (resume_id, job_file, title, site, location, workplace, source_url, score, computed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(resume_id, job_file) DO UPDATE SET
            title=excluded.title,
            site=excluded.site,
            location=excluded.location,
            workplace=excluded.workplace,
            source_url=excluded.source_url,
            score=excluded.score,
            computed_at=excluded.computed_at
        """,
        (resume_id, job_file, title, site, location, workplace, source_url, score, computed_at),
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
