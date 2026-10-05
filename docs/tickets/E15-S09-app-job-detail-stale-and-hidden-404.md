# E15-S09 — App: job detail for stale postings, 404 for hidden ones everywhere

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions — do not repeat them here. These are app stories (only `app/` and `docs/`); the app never reads `scraper.db` and never edits `scraper/` or `resume-matcher/`: the single interface is the job markdown. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

A stale posting (0-2 days) still opens read-only with a "Delisted on <date>" notice; once hidden (3+ days) the job detail page, its screenshot and the status endpoint answer 404 through the existing styled 404 page.

## Context

- Needs E15-S06 (`jobs.job_stale_state`); after E15-S08 (same files).
- `app/webapp/routes.py`: `job_detail(match_id)` (loads the match, `abort(404)` if missing, renders `job_detail.html` with title/site/location/workplace/source/description_html/match_id/has_screenshot), `job_screenshot(match_id)` (404 if match or PNG missing, else `send_file`), `update_match_status_route(match_id)` (POST `/matches/<id>/status`: 404 if missing, 400 on invalid status, redirect to the resume detail). `webapp/__init__.py` registers `app.register_error_handler(404, ...)` rendering `404.html` (the styled 404, status 404).
- `app/webapp/templates/job_detail.html`: `<main>` with `<h1>{{ title }}</h1>`, a table, description, optional screenshot `<details>`, and the "View original posting" link.
- `app/webapp/static/style.css` already has `.job-description` and (after E15-S08) `.stale-row`/`.stale-badge`; add the new rule at the end of the file.
- Decisions: (1) stale job detail still opens (200) with a notice; it is already read-only (it has no editing controls) and keeps the original-posting link; (2) hidden -> `abort(404)` (styled 404); (3) the stale status endpoint answers 409 because stale rows are non-responsive (`abort(409)`); hidden answers 404; live behaves as today; (4) the screenshot route serves stale jobs (they still open) and 404s hidden ones; (5) persisted rows and statuses (e.g. Applied) are untouched — an Applied job follows the same 2-day rule as any other.
- Tests: `app/tests/test_routes.py` (`test_job_detail_with_valid_match` ~line 757, `test_job_detail_with_screenshot` ~1030 for setup incl. a PNG file).

## Files to create/modify

- `app/webapp/routes.py`
- `app/webapp/templates/job_detail.html`
- `app/webapp/static/style.css`
- `app/tests/test_routes.py`

## Acceptance criteria

- `job_detail`: after loading the match, `state, since = jobs.job_stale_state(match["job_file"])`; `hidden` -> `abort(404)`; passes `stale_since=since.isoformat() if state == "stale" else None` to the template.
- Template: when `stale_since` is set, directly after the `<h1>` render `<p class="stale-notice" role="note">Delisted on {{ stale_since }} — this posting is no longer listed on the original site.</p>`; absent otherwise.
- CSS: `.stale-notice { padding: 0.5rem 0.75rem; margin-bottom: 1rem; border: 1px solid var(--text-muted); background: #2a2a2a; color: var(--text-secondary); }`.
- `job_screenshot`: hidden -> 404 (before looking for the PNG); stale and live unchanged.
- `update_match_status_route`: hidden -> 404; stale -> `abort(409)` and the stored status stays unchanged; live unchanged (existing tests).
- Tests (dates from `date.today()`): stale 0/1/2-day jobs -> `GET /jobs/<id>` 200 and body contains `Delisted on <date>` and `class="stale-notice"`; live job (no bullet) -> 200 without `stale-notice`; 3-day job -> 404 and the body is the styled 404 page (contains `404 — Not Found`); `GET /jobs/<hidden id>/screenshot` is 404 even when the PNG exists, while the same for a stale job is 200 `image/png`; `POST /matches/<stale id>/status` with `status=Done` -> 409 and `db.get_match(...)["status"]` unchanged; hidden -> 404; live -> 302 as before; an `Applied` stale (1 day) job still opens (200). Existing tests pass.

## Definition of done

- Run only `uv run pytest tests/test_routes.py -q` from `app/`.
- Committed in the JOB-HUNTER repo as `E15-S09: Job detail notice for stale, 404 for hidden`.
- The orchestrator ticks `docs/todo.md`. This is the last Epic 15 code story: the full-suite gate runs after it.
