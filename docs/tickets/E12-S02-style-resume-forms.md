# E12-S02 — Style the New/Edit resume forms

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Fix usability QA finding #3: the New/Edit resume forms currently render as unstyled default browser widgets, and the content textarea is a 1-line box for pasting an entire CV into.

## Context

- Depends on E12-S01 (same two template files — read its final state first, since it added the error-message block; don't remove that, just style everything including it).
- `app/webapp/templates/resume_new.html` and `resume_edit.html` exist. `app/webapp/static/style.css` has the existing dark-theme tokens (`--bg`, `--text-primary`, `--text-secondary`, `--accent`, etc.) — reuse them, don't invent new colors.

## Files to modify

- `app/webapp/static/style.css` — add styles for form elements used by these two pages: `input[type="text"]`, `textarea`, `label` — dark background matching the theme (e.g. a step lighter than `--bg`, or just `--bg` with a `border: 1px solid var(--text-muted)`), `--text-primary` text color, monospace or readable font, reasonable padding. Specifically size the textarea generously: `textarea { min-height: 20rem; width: 100%; font-family: ui-monospace, "SF Mono", "Cascadia Code", "JetBrains Mono", monospace; }` (monospace suits resume markdown content) so a real multi-paragraph resume is actually editable without scrolling through a postage-stamp box.
- `app/webapp/templates/resume_new.html` / `resume_edit.html` — no structural changes needed beyond what CSS can reach (standard `<input>`/`<textarea>`/`<label>` elements already exist from earlier stories); only touch these files if the CSS selectors above need a class hook that isn't already there (prefer plain element selectors over adding classes if they work).

## Acceptance criteria

- Visual/manual check (headless-chrome screenshot of `/resumes/new` and `/resumes/<id>/edit`): the textarea is visibly tall (several lines of resume text visible without scrolling) and the input/textarea/button no longer look like unstyled default browser widgets — dark background, consistent with the rest of the app.
- `uv run pytest tests/ -q` (from `app/`) still passes (this is a CSS-only change — no Python/template-logic behavior should change, only appearance).

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E12-S02: Style the New/Edit resume forms and size the content textarea`.
- `docs/todo.md` item for E12-S02 checked off.
