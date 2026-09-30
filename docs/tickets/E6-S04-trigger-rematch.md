# E6-S04 — Trigger a rematch (POST /resumes/<id>/rematch)

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Wire a "Rematch" button on the resume detail page to actually run the matching engine and persist results.

## Context

- Depends on E6-S03 (the page the button lives on, and its `db.py`'s `get_resume`), E4-S01 (`jobs.py`'s `parse_job_file`), E5-S01 (`matcher.py`'s `run_embed_match`), E3-S02 (`db.py`'s `upsert_match`).
- Per `docs/DESIGN_DOC.md`'s Matching flow: v1 has no live progress indicator — the request kicks off a background thread and redirects immediately; the user reloads the page later to see results.

## Files to modify

- `app/webapp/templates/resume_detail.html` (extend — add the "Rematch" form/button)
- `app/webapp/routes.py` (extend — add the `POST /resumes/<int:resume_id>/rematch` route)
- `app/webapp/db.py` (read-only reference — reuse `get_resume` from E6-S03, no changes needed here)

## Implementation notes

- Template: `<form method="post" action="/resumes/<id>/rematch">` with a submit button labeled `"Rematch"`.
- Route: looks up the resume's `file_path` via `db.get_resume` (404 if the resume doesn't exist, same as E6-S03), then starts a `threading.Thread` running a function that:
  1. calls `matcher.run_embed_match(resume_file_path)`
  2. for each result, calls `jobs.parse_job_file(result["job_file"])` and `jobs.site_name_for(result["job_file"])` to get title/site/location/workplace/source
  3. calls `db.upsert_match(...)` with those fields plus `result["score"]` and the current UTC timestamp as `computed_at`
  - The thread needs its **own** database connection (`sqlite3.Connection` objects aren't safe to share across threads) — open a fresh one inside the thread function via `db.get_connection(app.config["DATABASE"])`, not the request-scoped `get_db()`.
  - The route itself does not wait for the thread; it redirects (302) back to `/resumes/<id>` immediately.

## Acceptance criteria

- `resume_detail.html` contains a `<form method="post" action="/resumes/<id>/rematch">` with a button containing the text `"Rematch"`.
- Test mocks `webapp.matcher.run_embed_match` to return a small fixed list of `{"job_file": ..., "score": ...}` dicts synchronously, and mocks/stubs `webapp.jobs.parse_job_file`/`site_name_for` to return fixed metadata (don't rely on real files from `scraper/jobs/` for this test — keep it fast and independent of that data existing).
- Test triggers `POST /resumes/<id>/rematch`, **joins the background thread before asserting** (e.g. by capturing the `Thread` object and calling `.join()` in the test, or by making the route testable with threading patched to run synchronously — either approach is fine as long as the test doesn't finish before the thread does), then asserts `db.get_matches(conn, resume_id)` reflects the mocked results.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E6-S04: Wire up rematch trigger`.
- `docs/todo.md` item for E6-S04 checked off.
