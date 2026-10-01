# E12-S01 — Server-side validation on resume create/edit; create redirects to the new resume

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Fix usability QA findings #1/#2 (blank or whitespace-only resume name/content silently saved, producing unrecoverable "ghost" entries) and #8 (create redirects to the list, edit redirects to the detail page — inconsistent) in one pass, since both touch the same create/edit route handlers.

## Context

- Independent of Epics 8–11 — only touches the create/edit routes and their templates.
- `app/webapp/routes.py` has `register_resume_route` (`POST /resumes`), `edit_resume_get`/`edit_resume_post` (`GET`/`POST /resumes/<id>/edit`) — read all of them first.
- `app/webapp/templates/resume_new.html` and `resume_edit.html` exist — read both first.

## Files to modify

- `app/webapp/routes.py`:
  - In `register_resume_route`: if `name.strip()` or `content.strip()` is empty, re-render `resume_new.html` with an error message and the originally-entered (unstripped) `name`/`content` values pre-filled (so the user doesn't lose what they typed), instead of creating the resume. On success, redirect to `main.resume_detail` for the new resume's id (not `main.resume_list` — this is the QA #8 fix).
  - In `edit_resume_post`: same blank/whitespace check: if invalid, re-render `resume_edit.html` with an error and the submitted (not the old DB) values, don't call `update_resume`. On success, redirect behavior is unchanged (already goes to `main.resume_detail`).
- `app/webapp/templates/resume_new.html` / `resume_edit.html`: add a conditional error block (e.g. `{% if error %}<p class="error">{{ error }}</p>{% endif %}`) above the form, and make the `name`/`content` fields' values come from a passed-in `name`/`content` variable (defaulting to empty for new, to the resume's current values for edit) so a failed submission re-shows what the user typed rather than resetting the form.
- `app/webapp/static/style.css`: add a small `.error` style (e.g. `color: #e34948;` — reuse the dataviz-validated "critical" red if you want a hex, or any clearly-error-reading color that still has decent contrast on `var(--bg)` — don't need to re-derive/validate a new color for one error message, just don't use pure saturated red-on-black without checking it's at least legible).

## Acceptance criteria

- `POST /resumes` with `name=""` (or `name="   "`) does NOT create a row in `resumes` (verify via `db.list_resumes`), returns the form page (not a redirect) with an error message visible, and the user's originally-typed content (if non-blank) is still in the textarea.
- `POST /resumes` with valid `name`/`content` still creates the resume and now redirects (302) to `/resumes/<new-id>` (not `/`).
- `POST /resumes/<id>/edit` with a blank/whitespace name or content does NOT change the existing row (verify via `db.get_resume`), returns the edit form with an error, doesn't lose the submitted values.
- `uv run pytest tests/ -q` (from `app/`) passes — update the existing create/edit tests' happy-path redirect assertions if they checked the old `main.resume_list` target for create, and add new tests for the blank/whitespace rejection cases.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E12-S01: Reject blank/whitespace resume name or content; create redirects to the new resume`.
- `docs/todo.md` item for E12-S01 checked off.
