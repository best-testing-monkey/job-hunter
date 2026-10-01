# E8-S02 — Track rematch-running state and expose a status endpoint

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

So the homepage's refresh icon can spin for the *actual* duration of a rematch (not a guess), track whether a rematch is currently running for a resume, and expose it via a small JSON endpoint the page can poll.

## Context

- Depends on E8-S01 (same `db.py` file — read its final state first, extend it, don't undo its changes).
- `app/webapp/routes.py` has `_run_rematch` (the background-thread function) and `rematch_resume` (`POST /resumes/<id>/rematch`, starts the thread then redirects) — read both in full before editing.
- Read `docs/DESIGN_DOC.md`'s "Data model changes" and the "Rematch status polling" part of the "Architecture change" subsection for the exact behavior.

## Files to modify

- `app/webapp/db.py`:
  - Add `rematch_running INTEGER NOT NULL DEFAULT 0` to the `resumes` table's `CREATE TABLE IF NOT EXISTS` statement.
  - Add `set_rematch_running(conn: sqlite3.Connection, resume_id: int, running: bool) -> None` — updates the column (`1`/`0`).
- `app/webapp/routes.py`:
  - In `rematch_resume`, call `db.set_rematch_running(conn, resume_id, True)` **before** `thread.start()`.
  - In `_run_rematch`, wrap the existing body in `try: ... finally: ` and call `db.set_rematch_running(<a fresh connection>, resume_id, False)` in the `finally` block — this must run even if `matcher.run_embed_match` or any upsert raises, so a crashed run doesn't leave the resume stuck showing "running" forever. (The function already opens its own connection for upserts; reuse it, don't open a second one, and make sure it's still open/valid in the `finally` block — open the connection at the top of the function, before the `try`.)
  - Add `GET /resumes/<int:resume_id>/rematch-status` returning `jsonify({"running": bool(resume["rematch_running"])})` (404 via `get_resume` if the resume doesn't exist, same pattern as every other per-resume route).
- `app/tests/test_db.py` / `app/tests/test_routes.py`: add tests (see below).

## Acceptance criteria

- `set_rematch_running(conn, id, True)` then `get_resume(conn, id)["rematch_running"]` is truthy; `set_rematch_running(conn, id, False)` then it's falsy.
- `GET /resumes/<id>/rematch-status` for an existing resume returns HTTP 200 and JSON `{"running": false}` before any rematch has run.
- A test simulates `_run_rematch` raising partway through (mock `matcher.run_embed_match` to raise an exception) and asserts `rematch_running` is back to `0`/false afterward — the `finally` block must actually fire. Mock out threading the same way E6-S04's existing rematch test does (join synchronously, or patch `threading.Thread`), don't let a real thread actually run in the test.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E8-S02: Track rematch-running state and expose a status endpoint`.
- `docs/todo.md` item for E8-S02 checked off.
