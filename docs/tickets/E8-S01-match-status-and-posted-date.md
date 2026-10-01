# E8-S01 — Add match status, job_posted column, and match lookup functions

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Add a `status` and `job_posted` column to `matches`, and the `get_match`/`update_match_status` functions the later detail-page and job-detail-page stories depend on — without a rematch ever resetting an already-triaged match's status.

## Context

- Epics 1–7 are done and committed. `app/webapp/db.py` has `get_connection`, `init_db`, `create_resume`, `update_resume`, `delete_resume`, `list_resumes`, `get_resume`, `upsert_match`, `get_matches`. Read the whole file first.
- Read `docs/DESIGN_DOC.md`'s "Data model changes" subsection (under "Dashboard, match workflow, and job detail (third slice)") for the exact schema.
- Do NOT touch `routes.py` or any template in this story — purely additive to `db.py`.

## Files to modify

- `app/webapp/db.py`:
  - Add `status TEXT NOT NULL DEFAULT 'New'` and `job_posted TEXT` to the `matches` table's `CREATE TABLE IF NOT EXISTS` statement.
  - Change `upsert_match`'s signature to accept a new `job_posted: str | None` parameter, and update its `INSERT ... ON CONFLICT ... DO UPDATE` so the `ON CONFLICT` clause sets `job_posted=excluded.job_posted` alongside the existing fields — but does **NOT** include `status` in that `DO UPDATE SET` list at all, so an existing row's `status` is never touched by a later upsert. New rows still get `status`'s table-level default (`'New'`).
  - Add `get_match(conn: sqlite3.Connection, match_id: int) -> sqlite3.Row | None` — look up a single match by its own `id` primary key (not by resume_id).
  - Add `update_match_status(conn: sqlite3.Connection, match_id: int, status: str) -> None` — update the `status` column for one match by id. Validate `status` is one of `{"New", "Non-match", "Applied", "Done"}` (raise `ValueError` if not — this is a real boundary, not a "can't happen" case, since it'll be driven by a web form later).
- `app/tests/test_db.py`: add tests (see below).

## Acceptance criteria

- A fresh `upsert_match` call (new `resume_id`+`job_file` pair) creates a row with `status == "New"`.
- Calling `update_match_status` to change a row's status to `"Applied"`, then calling `upsert_match` again for that same `(resume_id, job_file)` with a different `score`/`job_posted`: the row's `score`/`job_posted` reflect the new values, but `status` is still `"Applied"` (not reset to `"New"`).
- `update_match_status` with an invalid status string (e.g. `"Bogus"`) raises `ValueError` and does not change the row.
- `get_match` returns the correct row for a valid id, `None` for a nonexistent id.
- `uv run pytest tests/ -q` (from `app/`) passes — all existing tests (update any existing `upsert_match`/`get_matches` call sites in tests that need the new `job_posted` argument) plus new ones.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E8-S01: Add match status, job_posted column, and match lookup functions`.
- `docs/todo.md` item for E8-S01 checked off.
