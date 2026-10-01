# E9-S02 — Homepage dashboard: threshold slider, sortable resume table, icon actions

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Rebuild the homepage as the dashboard described in `docs/DESIGN_DOC.md`'s "Homepage (`/`)" subsection: a confidence-threshold slider, a sortable resume table with client-side-computed Match Count / since-new-match columns, and icon-based actions (delete, rematch-with-live-spinner).

## Context

- Depends on E8-S01, E8-S02 (needs `status`/`job_posted` on matches, `rematch_running` on resumes, the `/rematch-status` endpoint) and E9-S01 (needs `app.js`'s three helpers and the CSS it added). Read the final state of `app/webapp/db.py`, `routes.py`, and `app/webapp/static/app.js` before starting.
- Read `docs/DESIGN_DOC.md`'s "Homepage (`/`)" subsection in full — it specifies exactly what's computed client-side vs. server-side, and why (the threshold lives in `localStorage`, not on the server, so Match Count/since-new-match must be recomputable in JS without a round-trip).
- `app/webapp/templates/resumes.html` and the `resume_list` route in `routes.py` exist — read both first.

## Files to modify

- `app/webapp/routes.py` — in `resume_list`, for each resume also fetch its matches (`db.get_matches`) and build a per-resume list of `{"score": ..., "status": ..., "job_posted": ...}` dicts; pass this to the template (e.g. as a dict keyed by resume id, or attached per-resume — your call, whatever's cleanest to serialize) so it can be embedded as JSON.
- `app/webapp/templates/resumes.html`:
  - Add the threshold slider (`<input type="range" min="0" max="100" value="65" id="threshold-slider">` + a `<span id="threshold-readout">`) positioned above the table, with the "+ New Resume" link beside it (reuse the existing `.btn-accent` link, just reposition).
  - Embed the per-resume match data as JSON: `<script type="application/json" id="resume-match-data">{{ resume_match_data | tojson }}</script>` (or similar — Flask/Jinja's `tojson` filter handles this).
  - The resume table: `<th data-sort-key="name">Name</th>`, `<th data-sort-key="match-count">Match count</th>`, `<th data-sort-key="since-new-match">since new match</th>`, `<th>Actions</th>` (Actions not sortable, no `data-sort-key`). Each resume's `<tr>` has `<td data-sort-value="...">` cells for the three sortable columns, computed/updated by JS (initial render can show `0`/`—` server-side; JS fills in real values on page load via the threshold callback).
  - Actions column: a delete icon (keep the existing `onsubmit="return confirm(...)"` form, just restyle as an icon — a simple inline SVG or a unicode `✕` styled red via CSS is fine, no icon library needed) and a rematch icon (unicode `↻` or a simple inline SVG, wrapped in the existing rematch `<form>`) with an `id` JS can target to call `pollRematchStatus` on page load if that resume's `rematch_running` is already true (e.g. render a `data-rematch-running="true/false"` attribute server-side so JS knows whether to start polling immediately on page load, in case the user reloaded mid-run).
  - Inline `<script>` (or a small addition to `app.js` — your call) that: parses the embedded JSON, calls `initThresholdSlider` with a callback that recomputes each resume's Match Count (`status === "New" && score >= threshold ? count++`) and since-new-match (max `job_posted` among entries with `score >= threshold`, formatted as a relative time string — a simple hand-rolled "X days/hours ago" formatter is fine, no date library needed), writes the results into each row's `data-sort-value`/visible text, then calls `makeSortable` on the table once.
- Remove the old plain `<ul>` resume list markup entirely — it's replaced by the table.

## Acceptance criteria

- `GET /` renders the slider, the table with the four columns, and (if resumes exist) a row per resume with working delete and rematch icons (same underlying `POST` endpoints as before — this story restyles and adds client-side computation, it doesn't change what `POST /resumes/<id>/delete` or `/rematch` do).
- With a resume that has matches at varying scores and statuses, moving the slider (simulate via a direct `fetch`/manual test, or trust visual/manual verification — there's no JS test runner in this project, see E9-S01's note) changes the displayed Match Count correctly in a live browser check.
- `uv run pytest tests/ -q` (from `app/`) passes — update/extend `test_routes.py`'s homepage tests to check the new table structure (e.g. assert `data-sort-key="name"` appears, assert the JSON script tag is present) rather than the old `<ul>` structure.
- Do a real manual check (start the app, open `/` in a browser or headless-chrome screenshot) to confirm the slider and table actually render sensibly — this is enough new template/JS surface that a passing test suite alone isn't sufficient confidence.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E9-S02: Rebuild homepage as a sortable dashboard with threshold filtering`.
- `docs/todo.md` item for E9-S02 checked off.
