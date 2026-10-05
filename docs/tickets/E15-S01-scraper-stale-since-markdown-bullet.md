# E15-S01 — Markdown: optional `- Stale since: YYYY-MM-DD` bullet

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` for conventions (Epic 15 scraper stories follow B exactly as Epic 13 did: `scraper/` is the owner's separate repo, commit there) — do not repeat them here. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

`markdown_export` can render, set, replace and remove an optional `- Stale since: YYYY-MM-DD` bullet, idempotently, exactly like `- Screenshot:`.

## Context

- `scraper/job_scraper/core/markdown_export.py`: `slugify`, `filename_for(posting)`, `stem_for`, `render(posting, screenshot=None)` (bullets in fixed order, then `- Screenshot:`, blank line, `## Description`), `write(posting, jobs_dir, screenshot=None) -> str`, and `set_screenshot_line(md_path, screenshot) -> bool` (replaces an existing line, else inserts after the last consecutive `- ` bullet before the blank line preceding `## Description`; returns False when unchanged or when the layout is not recognised). Copy its approach.
- The app parses bullets with `^- (\w[\w ]*):\s*(.+)$`; "Stale since" matches (letters and a space). Descriptions never start a line with `## `.
- Tests: `scraper/tests/test_markdown_export.py` (see the existing `set_screenshot_line` tests for fixtures/style).

## Files to create/modify

- `scraper/job_scraper/core/markdown_export.py`
- `scraper/tests/test_markdown_export.py`

## Acceptance criteria

- `render(posting, screenshot=None, stale_since: str | None = None)` and `write(posting, jobs_dir, screenshot=None, stale_since=None)`: when `stale_since` is a non-empty string the bullet `- Stale since: <value>` is rendered right after the `- Screenshot:` bullet (or after the last extra-field bullet if there is no screenshot); no bullet otherwise. Existing outputs are byte-identical when the argument is omitted.
- `md_path_for(jobs_dir: str, site_id: str, listing_id: str, title: str) -> Path`: `Path(jobs_dir) / f"{site_id}-{listing_id}-{slugify(title)}.md"` (same stem rule as `filename_for`).
- `set_stale_line(md_path: str, stale_since: str | None) -> bool`: file missing -> False. `stale_since` must match `^\d{4}-\d{2}-\d{2}$` or be None, else `ValueError`. A string: replace the existing `- Stale since:` line or insert one after the last consecutive header bullet (same rule as `set_screenshot_line`); `None`: remove the line if present. Returns True only if the file content changed; calling twice with the same arguments returns False the second time and leaves the file byte-identical. The description and everything after `## Description` are never touched, even if a description line itself looks like `- Stale since: 2020-01-01`.
- Tests: render with/without; write passes it through; `set_stale_line` insert, replace with a new date, remove, remove when absent (False), idempotent second call (False), missing file (False), bad format raises `ValueError`, description line lookalike untouched, file with both `- Screenshot:` and `- Stale since:` keeps both after a `set_screenshot_line` call and after a `set_stale_line` call, `md_path_for` equals `Path(jobs_dir)/filename_for(posting)` for a sample posting.

## Definition of done

- Run only `uv run pytest tests/test_markdown_export.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E15-S01: Add Stale since bullet to markdown export`.
- The orchestrator ticks `docs/todo.md` (do not edit it).
