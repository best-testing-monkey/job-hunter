# E1-S01 — Scaffold the Flask app project

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Set up `app/` at the `job-hunter` repo root as a uv-managed Flask project with a minimal working app factory and a health-check route.

## Context

- Repo root: `/media/baz/MonkeyWorks/PycharmProjects/job-hunter/`. The `app/` directory already exists (currently empty) — this story populates it.
- Read `docs/DESIGN_DOC.md`'s "Architecture" section for the target directory layout: `app/pyproject.toml`, `app/webapp/` (the Python package, not to be confused with the outer `app/` project directory), `app/tests/`.
- No existing code to reuse for this story — it's the initial scaffold everything else builds on.

## Files to create

- `app/pyproject.toml` — project name `job-hunter-app`, `requires-python = ">=3.10"`, one dependency: `flask`.
- `app/webapp/__init__.py` — `create_app() -> Flask` that creates a Flask app, registers the Blueprint from `webapp/routes.py`, and returns it.
- `app/webapp/routes.py` — a Blueprint (e.g. `bp = Blueprint("main", __name__)`) with one route: `GET /health` returning JSON `{"status": "ok"}`.
- `app/tests/test_routes.py` — tests the health route via Flask's test client.

## Acceptance criteria

- `app/pyproject.toml` exists and declares `flask` as a dependency.
- `uv sync` (run from `app/`) succeeds.
- `uv run python -c "from webapp import create_app; create_app()"` (run from `app/`) exits without error.
- A test using `app.test_client().get("/health")` asserts HTTP 200 and JSON body `{"status": "ok"}`.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E1-S01: Scaffold Flask app project`.
- `docs/todo.md` item for E1-S01 checked off.
