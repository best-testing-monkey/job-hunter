# E6-S03 — Resume match list page (GET /resumes/<id>)

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Show one resume's persisted matches, sorted by score descending by default.

## Context

- Depends on E2-S01 (`base.html`) and E3-S02 (`db.py`'s `get_matches`).
- Use the same `get_db()` helper added in E6-S01.

## Files to modify/create

- `app/webapp/templates/resume_detail.html` (new, extends `base.html`)
- `app/webapp/routes.py` (extend — add the `GET /resumes/<int:resume_id>` route)
- `app/webapp/db.py` (extend — add `get_resume`, see below)
- `app/tests/test_db.py` (extend — add a test for `get_resume`)

## Implementation notes

- Add `get_resume(conn: sqlite3.Connection, resume_id: int) -> sqlite3.Row | None` to `db.py`, following the same style as the other query functions from E3-S02 (returns `None` if no row matches, doesn't raise). This will be reused by E6-S04 later — implement it generally, not tied to this page's specific needs.
- Route looks up the resume via `get_resume`. If not found, return a 404 (`abort(404)`).
- Otherwise calls `db.get_matches(get_db(), resume_id)` and renders `resume_detail.html` with the resume and its matches.
- Template renders a table: columns Score, Job title (linked to `source_url` if present), Site, Workplace, Location. One row per match.

## Acceptance criteria

- `GET /resumes/<id>` for a resume with matches returns HTTP 200; the response body contains each match's `title`.
- `GET /resumes/<id>` for a resume with zero matches returns HTTP 200 and contains the literal text `"No matches yet — run a rematch"`.
- `GET /resumes/999999` (an id that doesn't exist) returns HTTP 404.
- `uv run pytest tests/ -q` (from `app/`) passes, including new tests covering all three cases above (seed a temp DB directly via `db.register_resume` + `db.upsert_match` in the test setup).

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E6-S03: Add resume match list page`.
- `docs/todo.md` item for E6-S03 checked off.
