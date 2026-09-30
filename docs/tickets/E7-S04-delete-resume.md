# E7-S04 — Delete a resume (POST /resumes/<id>/delete)

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

A button on a resume's detail page to delete it (and its matches and backing file) entirely.

## Context

- Depends on E7-S01 (`db.py`'s `delete_resume`) and E7-S03 (the page this button lives on — implement after it, don't run concurrently with it since both touch `resume_detail.html` and `routes.py`).
- Destructive action — needs a client-side confirmation before submitting (a plain `onsubmit="return confirm('...')"` on the form is sufficient, no JS library needed).

## Files to modify

- `app/webapp/templates/resume_detail.html` — add a `<form method="post" action="/resumes/<id>/delete" onsubmit="return confirm('Delete this resume and all its matches?')">` with a submit button labeled `"Delete"`.
- `app/webapp/routes.py` — add `POST /resumes/<int:resume_id>/delete`: looks up the resume via `get_resume` (404 if missing), calls `db.delete_resume(get_db(), resume_id)`, redirects (302) to `main.resume_list`.
- `app/tests/test_routes.py` — add tests (see below).

## Acceptance criteria

- `resume_detail.html` contains a `<form method="post" action="/resumes/<id>/delete">` with a button containing the text `"Delete"`, and the form has an `onsubmit` attribute calling `confirm(...)`.
- `POST /resumes/<id>/delete` for an existing resume (with at least one match) returns HTTP 302 to `/`; a subsequent `GET /resumes/<id>` returns HTTP 404; `db.get_matches` for that id returns an empty list; the resume's backing file no longer exists on disk.
- `POST /resumes/999999/delete` (nonexistent id) returns HTTP 404.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E7-S04: Add resume delete route and button`.
- `docs/todo.md` item for E7-S04 checked off — this is the last story in Epic 7.
