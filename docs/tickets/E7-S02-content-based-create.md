# E7-S02 — Switch resume creation to content-based, remove register_resume

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Change `POST /resumes` to create a resume from a name + pasted content (using E7-S01's `create_resume`) instead of a name + external file path, and remove the now-unused `register_resume`.

## Context

- Depends on E7-S01 (`db.py`'s `create_resume`, `app.config["RESUMES_DIR"]`).
- `app/webapp/routes.py`'s current `register_resume_route` (`POST /resumes`) reads `request.form["name"]` and `request.form["file_path"]`, calls `db.register_resume`. Read the whole file first — this is the only call site of `register_resume`, and the route/function names may need updating to reflect the new form fields.
- `app/webapp/templates/resumes.html` currently has a form with `name` and `file_path` text inputs. Read it first.

## Files to modify

- `app/webapp/routes.py`: change the `POST /resumes` handler to read `request.form["name"]` and `request.form["content"]`, call `db.create_resume(get_db(), current_app.config["RESUMES_DIR"], name, content)`, redirect to `main.resume_list` as before.
- `app/webapp/templates/resumes.html`: change the form's second field from `<input name="file_path">` to `<textarea name="content"></textarea>` (keep the `name` input as-is).
- `app/webapp/db.py`: remove `register_resume` entirely — it has no remaining callers after this change.
- `app/tests/test_routes.py`: update the existing register/create test to POST `{"name": ..., "content": ...}` instead of `{"name": ..., "file_path": ...}`, and additionally assert that a file now exists on disk under the test's `RESUMES_DIR` containing that content (you'll need to set `app.config["RESUMES_DIR"]` to a `tmp_path` subdirectory in the test, the same way `app.config["DATABASE"]` is already overridden for tests).
- `app/tests/test_db.py`: remove any test that exercises `register_resume` (superseded by E7-S01's `create_resume` tests).

## Acceptance criteria

- `resumes.html`'s form has inputs named `name` and `content` (content as a `<textarea>`), no `file_path` field.
- `POST /resumes` with `{"name": "Test CV", "content": "# My resume\n..."}` returns HTTP 302, a subsequent `GET /` contains `"Test CV"`, and a file exists on disk (under the configured `RESUMES_DIR`) containing that content.
- `db.py` no longer defines `register_resume`, and nothing in `app/webapp/` or `app/tests/` still calls it (`grep -r register_resume app/` returns nothing).
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E7-S02: Switch resume creation to content-based, remove register_resume`.
- `docs/todo.md` item for E7-S02 checked off.
