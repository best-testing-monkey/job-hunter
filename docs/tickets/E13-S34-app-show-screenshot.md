# E13-S34 — Show the screenshot on the job detail page

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here. Epic 13 app stories follow it unchanged (they only touch `app/`).

## Goal

The job detail page shows the posting's screenshot in a collapsed `<details>` section below the description, and shows nothing when there is no screenshot.

## Context

- Depends on E13-S33 (`jobs.screenshot_path_for`, route endpoint `main.job_screenshot`) and E13-S12 (template/CSS state).
- `app/webapp/routes.py` job detail route renders `job_detail.html` with `title, site, location, workplace, source, description_html...` (as left by E13-S12); it must additionally pass `match_id=match_id` and `has_screenshot=jobs.screenshot_path_for(match["job_file"]) is not None`.
- `app/webapp/templates/job_detail.html`: has `<h2>Description</h2>` + `<div class="job-description">...</div>` then the `View original posting` link.
- `app/webapp/static/style.css`: dark theme variables (`--accent`, `--text-muted`, ...).
- Tests: `app/tests/test_routes.py` (copy the setup of `test_job_detail_with_valid_match`).

## Files to create/modify

- `app/webapp/routes.py`
- `app/webapp/templates/job_detail.html`
- `app/webapp/static/style.css`
- `app/tests/test_routes.py`

## Acceptance criteria

- When the match's job file has a sibling screenshot: `GET /jobs/<id>` is 200 and the body contains `<details class="job-screenshot">` (without an `open` attribute — collapsed by default), `<summary>Screenshot of original posting</summary>` and `<img src="/jobs/<id>/screenshot"` with `alt="Screenshot of the original job posting"` and `loading="lazy"`; the `<details>` appears AFTER the `job-description` div and BEFORE the `View original posting` link.
- When there is no screenshot: the body contains neither `job-screenshot` nor `/screenshot`; page still 200 with the description and link.
- `style.css` has `.job-screenshot summary` (`cursor: pointer`, `color: var(--accent)`) and `.job-screenshot img` (`max-width: 100%`, `border: 1px solid var(--text-muted)`, `margin-top: 1rem`).
- Existing job-detail tests (title, description text, link, 404) still pass; `uv run pytest tests/ -q` passes.

## Definition of done

- Gates pass: `uv run pytest tests/ -q` from `app/` (zero failures, no fewer passing tests than before).
- Committed in the JOB-HUNTER repo as `E13-S34: Show job screenshot on detail page`.
- `docs/todo.md` item for E13-S34 checked off (same repo; may be a second commit `Mark E13-S34 as done in todo`).
