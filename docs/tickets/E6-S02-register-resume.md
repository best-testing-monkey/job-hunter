# E6-S02 — Register a resume (POST /resumes)

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

A minimal form on the resume list page to register a resume by name + file path (not full CRUD — see `docs/DESIGN_DOC.md`'s Non-goals section).

## Context

- Depends on E6-S01 (the list page the form lives on) and E3-S02 (`db.py`'s `register_resume`).
- Use the same `get_db()` helper added in E6-S01.

## Files to modify

- `app/webapp/templates/resumes.html` (extend — add the form)
- `app/webapp/routes.py` (extend — add the `POST /resumes` route)

## Implementation notes

- Form: `<form method="post" action="/resumes">` with a text input `name="name"`, a text input `name="file_path"`, and a submit button.
- Route: reads `request.form["name"]` and `request.form["file_path"]`, calls `db.register_resume(get_db(), name, file_path)`, then `redirect(url_for("main.resume_list"))` (HTTP 302) — adjust the endpoint name to whatever the `/` route is actually named in `routes.py`.

## Acceptance criteria

- `resumes.html` contains a `<form method="post" action="/resumes">` with inputs named `name` and `file_path`.
- `POST /resumes` with form data `{"name": "Test CV", "file_path": "/some/path.md"}` returns HTTP 302, and a subsequent `GET /` response body contains the text `"Test CV"`.
- `uv run pytest tests/ -q` (from `app/`) passes, including a new test covering the above using `app.test_client().post("/resumes", data={...})`.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E6-S02: Add resume registration form and route`.
- `docs/todo.md` item for E6-S02 checked off.
