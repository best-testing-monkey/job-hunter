# E15-S08 — App: stale matches as dark-gray, non-responsive rows on the resume detail page

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions — do not repeat them here. These are app stories (only `app/` and `docs/`); the app never reads `scraper.db` and never edits `scraper/` or `resume-matcher/`: the single interface is the job markdown. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

`/resumes/<id>` shows live matches as today, shows stale matches (0-2 days after the `Stale since` date) as dark-gray, visibly marked, non-interactive rows below them, and omits hidden ones completely.

## Context

- Needs E15-S06 (`jobs.job_stale_state`).
- `app/webapp/routes.py` `resume_detail(resume_id)`: `matches = db.get_matches(conn, resume_id)` rendered by `app/webapp/templates/resume_detail.html`: table `#matches-table` with `<thead>` (sortable headers `data-sort-key`) and ONE `<tbody>` of rows `<tr data-score="...">` (score cell, title cell with `<a href="/jobs/{{ id }}">`, site, location, status cell with a `<form method="post" action="/matches/{{ id }}/status">` containing a `<select name="status" onchange="this.form.submit()">`). Empty state: `{% if matches %}...{% else %}<p>No matches yet — run a rematch</p>`.
- `app/webapp/static/app.js` `makeSortable(table)` reorders only `tableEl.querySelector("tbody")` (the FIRST tbody); the template's inline script filters `table.querySelectorAll("tbody tr")` by `data-score` against the threshold slider. Therefore, with no JS change: rows placed in a SECOND `<tbody class="stale-rows">` are never reordered by sorting (always last) and are still filtered by the threshold like every other row. Decision: threshold applies to stale rows too; sorting never moves them; the first `<tbody>` must always be rendered, even when it has no rows.
- Theme variables in `app/webapp/static/style.css`: `--bg #08090a`, `--text-secondary #9a9a9a`, `--text-muted #616161`, `--accent #feff7c`.
- A stale match keeps its user status (`New`, `Applied`, `Non-match`, `Done`); the status is shown as plain text. Persisted `matches` rows are never modified by this story.
- Tests: `app/tests/test_routes.py` (see `test_resume_detail_with_matches` ~line 165 and `test_resume_detail_with_no_matches`).

## Files to create/modify

- `app/webapp/routes.py`
- `app/webapp/templates/resume_detail.html`
- `app/webapp/static/style.css`
- `app/tests/test_routes.py`

## Acceptance criteria

- `resume_detail` computes for each match `state, since = jobs.job_stale_state(m["job_file"])`: `live` -> `live_matches` (existing sort order), `stale` -> `stale_matches` (list of dicts `{"match": row, "since": since.isoformat()}`), `hidden` -> omitted. Passes `live_matches` and `stale_matches` to the template (keep passing `matches` = live + stale rows for the emptiness check, or switch the check to `live_matches or stale_matches`).
- Template: the table (and threshold slider) is rendered when there is at least one live OR stale match; first `<tbody>` holds the live rows exactly as today; a second `<tbody class="stale-rows">` follows it with one row per stale match: `<tr class="stale-row" aria-disabled="true" data-score="{{ score }}">` containing: score cell (`data-sort-value` as in live rows); title cell with `<span class="stale-title">{{ title }}</span>` followed by `<span class="stale-badge">stale since {{ since }}</span>` and NO `<a>` element; site and location cells as in live rows; status cell with `<span class="stale-status">{{ status }}</span>` and NO `<form>`, `<select>` or `<button>`.
- CSS (`style.css`): `.stale-row td { background: #2a2a2a; color: var(--text-muted); pointer-events: none; cursor: not-allowed; user-select: none; }`, `.stale-badge { margin-left: 0.5rem; padding: 0 0.4rem; border: 1px solid var(--text-muted); border-radius: 3px; font-size: 0.75rem; text-transform: uppercase; }`.
- No change to `app.js` or the inline script (verify by reading: both already handle the second tbody as described).
- Tests: resume with matches whose files carry dates today, today-1, today-2, today-3 and one with no bullet (+ one stale match with status `Applied`): response 200; the live match title appears inside an `<a href="/jobs/<id>">`; the stale (1-day, 2-day, Applied) titles appear in `<span class="stale-title">` with no `/jobs/<id>` href for their ids; exactly 3 occurrences of `class="stale-row"`; each stale row contains `aria-disabled="true"` and `stale since <date>`; the stale rows contain no `<select`; the 3-day match's title (use a unique title) does not appear anywhere in the response; the `<tbody class="stale-rows">` marker appears after the first `</tbody>`; the Applied stale row shows `Applied` as text. A resume whose only matches are hidden shows the `No matches yet` paragraph. Existing resume-detail tests pass.

## Definition of done

- Run only `uv run pytest tests/test_routes.py -q` from `app/`.
- Committed in the JOB-HUNTER repo as `E15-S08: Show stale matches as disabled rows on resume detail`.
- The orchestrator ticks `docs/todo.md`. Same files as E15-S07 and S09 (`routes.py`, `test_routes.py`): run in order.
