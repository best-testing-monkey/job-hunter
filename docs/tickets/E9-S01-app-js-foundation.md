# E9-S01 — app.js foundation: threshold slider, table sort, rematch polling

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Add the first client-side JavaScript this project has: a reusable threshold-slider helper, a reusable table-sort helper, and a rematch-status polling helper — plus the global accent-colored-link CSS rule and spinner animation, used by later stories in this epic and Epic 10.

## Context

- Independent of Epic 8 — can run in parallel with it (disjoint files).
- Read `docs/DESIGN_DOC.md`'s "Architecture change: this slice introduces real client-side JavaScript" subsection in full — it specifies the exact behavior of all three pieces.
- `app/webapp/templates/base.html` and `app/webapp/static/style.css` exist — read both first, extend them, don't replace them.
- This story does not wire these helpers into any specific page yet (no resumes.html/resume_detail.html changes) — later stories (E9-S02, E10-S02) call into what you build here. Write the functions generally, not tied to one page's specific markup.

## Files to create/modify

- `app/webapp/static/app.js` (new):
  - `initThresholdSlider(sliderEl, readoutEl, onChange)` — reads `localStorage.getItem("confidenceThreshold")` (default `"65"` if unset) on load, sets `sliderEl.value` and `readoutEl.textContent` (as `"<value>%"`) to it, and calls `onChange(value)` once immediately. On the slider's `input` event: writes the new value to `localStorage`, updates the readout, and calls `onChange(value)` again. `onChange` is a callback the calling page supplies (e.g. "recompute these numbers" or "show/hide these rows") — this function doesn't know what a page does with the value.
  - `makeSortable(tableEl)` — for every `<th data-sort-key="...">` in `tableEl`'s header row: on click, cycles that column through unsorted → ascending (add a `▼` to the header text, sort rows by comparing each row's matching `<td data-sort-value="...">` — compare numerically if the value parses as a number, otherwise as a string) → descending (`▲`, reverse order) → unsorted (remove the arrow, restore original row order — cache the original `<tr>` order on first sort so "unsorted" can actually restore it). Clicking a different column resets any other column's arrow/sort state first (only one column sorted at a time).
  - `pollRematchStatus(resumeId, iconEl, intervalMs = 2000)` — adds a `spinning` CSS class to `iconEl`, then every `intervalMs` calls `fetch(`/resumes/${resumeId}/rematch-status`)`, parses the JSON; if `running` is false, removes the `spinning` class and stops polling (clear the interval).
- `app/webapp/templates/base.html` — add `<script src="/static/app.js" defer></script>` before `</body>`.
- `app/webapp/static/style.css`:
  - Add a global `a { color: var(--accent); }` rule (fixes the default-browser-blue-link nitpick from the QA report — this app has no other place that rule belongs).
  - Add a `.spinning` class with a CSS `@keyframes` rotation (`animation: spin 1s linear infinite;` + the `@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }` rule).
  - Add a small `th[data-sort-key]` style (`cursor: pointer; user-select: none;`) so sortable headers look clickable.

## Acceptance criteria

- There's no existing JS test tooling in this project — don't add one. Instead, add a `GET /theme-preview`-style manual check isn't required either; verification for this story is a quick manual check (open `/theme-preview` or any page with a `<script>` tag, confirm `app.js` loads with no console errors via `curl -s http://127.0.0.1:5000/static/app.js` returning the file, and run the existing test suite to confirm nothing broke).
- `app/webapp/static/app.js` defines exactly the three functions above (`initThresholdSlider`, `makeSortable`, `pollRematchStatus`), each independently callable.
- `base.html` includes the `<script>` tag.
- `style.css` has the global `a` rule, `.spinning`/`@keyframes spin`, and the `th[data-sort-key]` cursor rule.
- `uv run pytest tests/ -q` (from `app/`) still passes (this story shouldn't change any Python behavior, just add static assets).

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E9-S01: Add app.js foundation (threshold slider, table sort, rematch polling)`.
- `docs/todo.md` item for E9-S01 checked off.
