# Appendix A — implementation standards

Applies to every story in this epic set. Don't repeat this content in
individual tickets — reference it.

## Environment

- `app/` is its own `uv`-managed project with its own `pyproject.toml` and
  `.venv`, separate from `resume-matcher`'s ML-heavy venv
  (`~/.venvs/resume-matcher`). Run everything from the `app/` directory via
  `uv run ...` (e.g. `uv run pytest tests/ -q`, `uv run flask --app webapp
  run`).
- Never add `torch`/`transformers`/ML dependencies to `app/pyproject.toml`.
  This app calls into `resume-matcher`'s dedicated venv via subprocess for
  anything ML-related (see `matcher.py`'s ticket) — it stays a plain Flask
  app otherwise.

## Code style

- Plain, dependency-light Python (3.10+), type hints on function signatures.
- No comments except where a non-obvious WHY needs explaining — never
  restate what the code already says. No docstrings unless a function's
  behavior genuinely isn't obvious from its name/signature.
- `sqlite3` directly (stdlib) — no ORM.
- Flask application-factory pattern: `create_app()` in `webapp/__init__.py`;
  routes registered via a Blueprint in `webapp/routes.py`.
- Don't add error handling, fallbacks, or input validation for scenarios
  that can't happen. Validate only at real boundaries (form input,
  subprocess failures, missing files).
- Don't introduce abstractions, config systems, or flexibility beyond what
  the ticket asks for.

## Tests

- `pytest`, one test file per module (`tests/test_<module>.py`).
- Use `tmp_path` for any test needing a real file/DB on disk — never touch
  the real `app/matches.db` (which doesn't exist yet in dev/test anyway) or
  real files under `scraper/`/`resume-matcher/` except where a ticket
  explicitly says to read one as read-only fixture data.
- Mock `subprocess.run` in tests that touch `matcher.py` — never actually
  invoke the real ML pipeline in a unit test (it takes minutes and needs a
  GPU). Same for anything spawning a background thread that calls into
  `matcher.py`: mock the matching call, and either patch out the
  `threading.Thread` or join it before asserting, so tests stay fast and
  deterministic.
- Flask routes: test via `app.test_client()`.

## Gates (must pass before a story is done)

From `app/`: `uv run pytest tests/ -q` — zero failures, no fewer passing
tests than before the story. No linter/type-checker is configured yet for
this project — don't add one unless a ticket says to.

## Commits

One commit per story. Message format: `E<n>-S<nn>: <short imperative
summary>` (e.g. `E3-S02: Add resume registration and match upsert
queries`). Imperative mood, explain why when it's not obvious from the
diff, not what (the diff already shows what). Match the style already used
in this repo's own commits and in the sibling `scraper`/`resume-matcher`
repos.

## Boundaries

- Never edit files under `scraper/` or `resume-matcher/` — this app reads
  from them (file paths, subprocess calls, a path-based Python import of
  `resume-matcher/build_report.py`) but never modifies their code.
- Stay inside the files your ticket's Context section lists. If you find
  you need to touch something not listed, stop and say so rather than
  expanding scope.
