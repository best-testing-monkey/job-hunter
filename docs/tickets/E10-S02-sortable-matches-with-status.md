# E10-S02 — Sortable match table with status workflow and threshold filtering

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Make the resume detail page's match table sortable, filterable by the shared confidence threshold, show rounded scores, add a per-match Status selectbox that saves immediately, and link each job to the new job detail page.

## Context

- Depends on E8-S01 (`status`/`job_posted` columns, `get_match`/`update_match_status`), E9-S01 (`app.js`'s `initThresholdSlider`/`makeSortable`), and E10-S01 (same template — read its final state first, build on it, don't undo its metadata-table change).
- Read `docs/DESIGN_DOC.md`'s "Resume detail page" subsection in full.
- The job detail page (`GET /jobs/<match_id>`) doesn't exist yet (built in E11-S01, which may run after this story) — link to `/jobs/{{ match['id'] }}` anyway; it's fine for that link to 404 until E11-S01 lands, this story's own tests shouldn't depend on that route existing.

## Files to modify

- `app/webapp/routes.py` — add a new route `POST /matches/<int:match_id>/status`: reads `request.form["status"]`, calls `match = db.get_match(conn, match_id)` (404 if `None`), then `db.update_match_status(conn, match_id, status)` (if the value isn't one of the four valid strings, it raises `ValueError` — catch it and return HTTP 400, don't let it 500), redirects to `main.resume_detail` using `match["resume_id"]` (the match row's own foreign key back to its resume).
- `app/webapp/templates/resume_detail.html`:
  - Add the threshold slider above the matches table (same markup pattern as the homepage from E9-S02 — `<input type="range">` + readout), wired via `initThresholdSlider` to hide/show `<tr>`s by comparing each row's `data-score` attribute against the threshold (don't recompute aggregates here, just toggle row visibility).
  - Matches table headers get `data-sort-key` attributes (Score, Job, Site, Location — Status is not sortable, skip it), each row's cells get matching `data-sort-value`; call `makeSortable` on page load. Score's `data-sort-value` is the raw float (for correct numeric sort); displayed text is rounded to 2 decimals.
  - Job (title) cell: link to `/jobs/{{ match['id'] }}` instead of `source_url` directly (drop the old `source_url` link on this page — it'll be reachable from the new job detail page instead).
  - Status cell: a `<select name="status">` with the four options, current value selected, inside a small `<form method="post" action="/matches/{{ match['id'] }}/status">` that auto-submits on `change` (`onchange="this.form.submit()"` — no separate Save button needed).
- `app/tests/test_routes.py`: add tests (see below).

## Acceptance criteria

- `POST /matches/<id>/status` with a valid status updates the DB (verify via `db.get_match`) and redirects (302) back to the resume's detail page.
- `POST /matches/<id>/status` with an invalid status string returns HTTP 400, doesn't change the row.
- `POST /matches/999999/status` (nonexistent match) returns HTTP 404.
- `GET /resumes/<id>` (with at least one match) shows the match's score rounded to 2 decimals in the visible text, a `<select>` with the correct current status selected, and a link to `/jobs/<match_id>`.
- `uv run pytest tests/ -q` (from `app/`) passes.
- Manual/visual check: load the page in a browser or headless-chrome screenshot, confirm the slider actually hides/shows rows and clicking a column header sorts it — the same caveat as E9-S02 about no JS test runner applies.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E10-S02: Add sortable, threshold-filtered match table with status workflow`.
- `docs/todo.md` item for E10-S02 checked off.
