# E12-S03 — Dark-themed 404 error page

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Fix usability QA finding #4: every 404 (bad resume id, bad edit/delete/rematch link) currently shows Flask/Werkzeug's raw default error page — plain white, totally disconnected from the app's all-dark visual identity.

## Context

- Independent of every other epic in this slice — only touches `__init__.py` and adds one new template.
- `app/webapp/__init__.py`'s `create_app()` exists — read it first, extend it, don't replace it.
- `app/webapp/templates/base.html` exists and already carries the dark theme — the new 404 template should extend it, same as every other page.

## Files to create/modify

- `app/webapp/templates/404.html` (new, extends `base.html`) — a simple page: heading ("404 — Not Found" or similar), a short sentence, and a link back to `/`.
- `app/webapp/__init__.py` — register a Flask error handler: `app.register_error_handler(404, lambda e: (render_template("404.html"), 404))` (or an equivalent named function — either is fine) inside `create_app()`, after the blueprint is registered.

## Acceptance criteria

- `GET` of any nonexistent-resource URL that currently 404s (e.g. `/resumes/999999`) still returns HTTP 404, but the response body now contains content from `404.html` (e.g. assert the "404" or "Not Found" text appears) rather than Werkzeug's default page, and renders within the same dark-theme `base.html` shell (e.g. assert the response contains whatever marker `base.html` always includes, like the nav).
- `uv run pytest tests/ -q` (from `app/`) passes — existing 404 tests (resume detail, edit, delete, rematch, status, job detail if built by then) should still see HTTP 404; extend at least one to also assert the new page's content appears.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E12-S03: Add a dark-themed 404 error page`.
- `docs/todo.md` item for E12-S03 checked off.
