# E2-S01 — Dark-only base template and stylesheet

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Build the base HTML shell and CSS implementing the dark-only design tokens from the design doc, with a debug/preview page to verify it renders correctly. No real app pages yet.

## Context

- Depends on E1-S01 (needs `app/webapp/__init__.py`, `routes.py` to exist).
- Read `docs/DESIGN_DOC.md`'s "Visual design tokens" table — use those exact hex values, don't invent different ones. There is **no light mode**: no `@media (prefers-color-scheme)` block, no light-theme CSS variables at all.
- `app/webapp/routes.py` (from E1-S01) — add a new route here, don't remove `/health`.

## Files to create/modify

- `app/webapp/static/style.css` (new) — `:root` custom properties: `--bg: #08090a`, `--text-primary: #ffffff`, `--text-secondary: #9a9a9a`, `--text-muted: #616161`, `--accent: #feff7c`, `--text-on-accent: #000000`. Font stacks: monospace (`ui-monospace, "SF Mono", "Cascadia Code", "JetBrains Mono", monospace`) for nav/labels/buttons; system sans (`system-ui, -apple-system, "Segoe UI", sans-serif`) for headings/body. A `.btn-accent` class: `background: var(--accent); color: var(--text-on-accent);` with sharp/minimally-rounded corners (e.g. `border-radius: 4px`), no drop shadows.
- `app/webapp/templates/base.html` (new) — HTML shell: `<head>` links `static/style.css`; `<body style="background: var(--bg); color: var(--text-primary)">` (or via a body rule in the CSS, either is fine); a `<nav>` with the site name "job-hunter"; `{% block content %}{% endblock %}`.
- `app/webapp/templates/theme_preview.html` (new) — extends `base.html`; content block contains an `<h1>` with text "Theme preview", a `<p>` with some placeholder secondary-styled text (`class="text-secondary"`, styled via `color: var(--text-secondary)` in the CSS), and a `<button class="btn-accent">Sample button</button>`.
- `app/webapp/routes.py` (modify) — add `GET /theme-preview` rendering `theme_preview.html`. Leave this as a permanent debug page (useful for future visual QA), not something to delete later.

## Acceptance criteria

- `style.css` defines exactly the six custom properties listed above on `:root`, and contains no `@media (prefers-color-scheme)` rule and no other color variables.
- `GET /theme-preview` returns HTTP 200 and the response body contains the literal text "Theme preview" and a `<button class="btn-accent">` containing the text "Sample button".
- `uv run pytest tests/ -q` passes, including a new test asserting the above on `/theme-preview`.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E2-S01: Add dark-only base template and stylesheet`.
- `docs/todo.md` item for E2-S01 checked off.