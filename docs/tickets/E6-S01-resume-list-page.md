# E6-S01 — Resume list page (GET /)

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

A landing page listing all registered resumes.

## Context

- Depends on E2-S01 (`base.html`, `style.css`) and E3-S02 (`db.py`'s `list_resumes`).
- `app/webapp/routes.py` already exists (from E1-S01/E2-S01) — add to it, don't replace `/health` or `/theme-preview`.
- The app needs a live `sqlite3.Connection` available to routes — add a `get_db()` helper in `routes.py` (or `db.py`) using Flask's `g` object and `current_app.config["DATABASE"]` for the db path, opening via `db.get_connection` + `db.init_db` on first use per request context. Keep this minimal — no connection pooling needed for a single-user local tool.
- `app/webapp/__init__.py`'s `create_app()` should set `app.config["DATABASE"]` to a path under the app's instance folder (e.g. `app.instance_path + "/matches.db"`) — create the instance folder if missing (`app.instance_path` handling is a standard Flask pattern; `os.makedirs(app.instance_path, exist_ok=True)`).

## Files to modify/create

- `app/webapp/__init__.py` (modify — add `DATABASE` config + instance folder creation)
- `app/webapp/routes.py` (modify — add the `get_db()` helper and the `/` route)
- `app/webapp/templates/resumes.html` (new, extends `base.html`)

## Acceptance criteria

- `GET /` returns HTTP 200 and renders `resumes.html`.
- The rendered page contains the literal text `"Resumes"` (a heading).
- When zero resumes are registered, the page contains the literal text `"No resumes registered yet"`.
- When one or more resumes are registered, each resume's `name` appears in the page body.
- `uv run pytest tests/ -q` (from `app/`) passes, including a new test using a `tmp_path`-based test DB (via `app.config["DATABASE"]` overridden in the test) checked both with zero resumes and with one resume registered via `db.register_resume`.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E6-S01: Add resume list page`.
- `docs/todo.md` item for E6-S01 checked off.
