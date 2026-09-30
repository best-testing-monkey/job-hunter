import sqlite3


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
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
