# E10-S01 — Styled resume metadata table on the detail page

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Replace the resume detail page's plain heading + "File: ..." paragraph with a proper styled metadata table, fixing the QA report's "raw filesystem path" nitpick along the way.

## Context

- Independent of Epic 8/9 — can run in parallel with them (only touches `resume_detail.html`, nothing else). Do NOT touch `routes.py` in this story — `get_resume` already returns everything needed (`name`, `content`, `file_path`, `created_at`).
- `app/webapp/templates/resume_detail.html` exists — read it first. This story only touches the top section (resume info) — leave the matches table, Edit link, Delete form, and Rematch form exactly as they are; a later story (E10-S02) handles the matches table.

## Files to modify

- `app/webapp/templates/resume_detail.html` — replace the current `<h1>{{ resume['name'] }}</h1><p>File: {{ resume['file_path'] }}</p>` with a small `<table>` (or definition list, your call — a `<table>` is more consistent with the rest of the app) showing rows for Name, Created, and File path (each as a labeled row, not a raw sentence). Content is likely too long for a table row — keep it out of this table and show it in a `<details>`/`<pre>` block below the table (collapsed by default via `<details><summary>Content</summary><pre>...</pre></details>` is a reasonable, dependency-free way to do this) so a long resume doesn't push the matches table far down the page.

## Acceptance criteria

- `GET /resumes/<id>` still returns HTTP 200 and contains the resume's `name`, `created_at`, and `file_path` — same data as before, just restyled (don't drop any existing information).
- The raw sentence `"File: <path>"` no longer appears as unstyled running text — it's a labeled table cell or equivalent.
- `uv run pytest tests/ -q` (from `app/`) passes — existing tests that check for specific text on this page should still find what they're looking for (adjust test assertions if the exact markup they check against needs it, but the underlying data shown must not change).

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E10-S01: Style the resume metadata section on the detail page`.
- `docs/todo.md` item for E10-S01 checked off.
