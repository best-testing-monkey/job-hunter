# E3-S02 — Resume registration and match upsert queries

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Add query functions for registering a resume, listing resumes, upserting match rows (no duplicates on re-run), and reading a resume's matches.

## Context

- Depends on E3-S01 (extends the same `app/webapp/db.py` and `app/tests/test_db.py` files — read them first, add to them, don't replace them).
- `docs/DESIGN_DOC.md`'s Data model section: `matches` has `UNIQUE(resume_id, job_file)`; the "Matching flow" section describes upsert-not-duplicate semantics — a rematch run should update existing rows for the same `(resume_id, job_file)` pair, not insert new ones.

## Files to modify

- `app/webapp/db.py` (extend — add functions below to the existing file from E3-S01)
- `app/tests/test_db.py` (extend — add tests below to the existing file from E3-S01)

## Functions to add to `db.py`

- `register_resume(conn: sqlite3.Connection, name: str, file_path: str) -> int` — inserts into `resumes` with the current UTC timestamp (ISO format string) as `created_at`; returns the new row's `id`. If `file_path` already exists (the `UNIQUE` constraint), don't insert a duplicate — look up and return the existing row's `id` instead.
- `list_resumes(conn: sqlite3.Connection) -> list[sqlite3.Row]` — all rows from `resumes`, any order.
- `upsert_match(conn: sqlite3.Connection, resume_id: int, job_file: str, title: str, site: str, location: str | None, workplace: str | None, source_url: str | None, score: float, computed_at: str) -> None` — `INSERT ... ON CONFLICT(resume_id, job_file) DO UPDATE SET title=excluded.title, site=excluded.site, location=excluded.location, workplace=excluded.workplace, source_url=excluded.source_url, score=excluded.score, computed_at=excluded.computed_at`. Commit the transaction.
- `get_matches(conn: sqlite3.Connection, resume_id: int, order_by: str = "score") -> list[sqlite3.Row]` — all matches for the given `resume_id`. Only accept `order_by` values from a small allowlist (`"score"`, `"title"`, `"site"`) to avoid building a query string from unvalidated input; default `"score"` sorts descending (best match first).

## Acceptance criteria

- Calling `register_resume` twice with the same `file_path` (different or same `name`) returns the same `id` both times, and `list_resumes` shows exactly one row for that path.
- Calling `upsert_match` twice with the same `(resume_id, job_file)` but a different `score` the second time: `get_matches` returns exactly one row for that `job_file`, with the second call's `score`.
- `get_matches` with `order_by="score"` returns rows sorted highest score first.
- `uv run pytest tests/ -q` (from `app/`) passes, including new tests for all of the above.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E3-S02: Add resume registration and match upsert queries`.
- `docs/todo.md` item for E3-S02 checked off.
