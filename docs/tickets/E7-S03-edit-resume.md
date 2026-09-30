# E7-S03 — Edit a resume (GET/POST /resumes/<id>/edit)

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

A form to edit an existing resume's name and content.

## Context

- Depends on E7-S01 (`db.py`'s `update_resume`, `get_resume`) and E7-S02 (the content-based create flow this mirrors).
- `app/webapp/routes.py` already has `GET /resumes/<int:resume_id>` (E6-S03) using `get_resume` + `abort(404)` if missing — follow the same 404 pattern here.
- `app/webapp/templates/base.html` exists — extend it, same as every other template.

## Files to modify/create

- `app/webapp/templates/resume_edit.html` (new, extends `base.html`) — a form with `method="post" action="/resumes/<id>/edit"`, a text input `name="name"` pre-filled with `{{ resume['name'] }}`, a `<textarea name="content">{{ resume['content'] }}</textarea>` pre-filled with the current content, and a submit button labeled `"Save"`.
- `app/webapp/routes.py`:
  - `GET /resumes/<int:resume_id>/edit` — looks up the resume via `get_resume` (404 if missing), renders `resume_edit.html`.
  - `POST /resumes/<int:resume_id>/edit` — looks up the resume (404 if missing), reads `request.form["name"]`/`request.form["content"]`, calls `db.update_resume(get_db(), resume_id, name, content)`, redirects (302) to `main.resume_detail` for that id.
- `app/webapp/templates/resume_detail.html` — add a link/button to `/resumes/<id>/edit` labeled `"Edit"` (a plain `<a>` is fine, doesn't need to be a form).
- `app/tests/test_routes.py` — add tests (see below).

## Acceptance criteria

- `GET /resumes/<id>/edit` for an existing resume returns HTTP 200 and the response body contains the resume's current `name` and `content` (e.g. as pre-filled form field values).
- `GET /resumes/999999/edit` returns HTTP 404.
- `POST /resumes/<id>/edit` with new `name`/`content` returns HTTP 302 to `/resumes/<id>`, and a subsequent `GET /resumes/<id>` (or `db.get_resume` directly) shows the updated values; the resume's file on disk (same `file_path` as before) now contains the new content.
- `resume_detail.html` contains a link to `/resumes/<id>/edit` with the text `"Edit"`.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E7-S03: Add resume edit form and route`.
- `docs/todo.md` item for E7-S03 checked off.
