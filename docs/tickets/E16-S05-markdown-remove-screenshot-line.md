# E16-S05 — `remove_screenshot_line` in markdown_export

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

A helper that removes the `- Screenshot:` bullet from a job markdown file (needed by the prune command, E16-S06); `set_screenshot_line` cannot remove.

## Context

- `scraper/job_scraper/core/markdown_export.py`: `set_screenshot_line(md_path, screenshot) -> bool` (replace/insert, idempotent, False when the file lacks `## Description`); `set_stale_line(md_path, None)` removes a stale bullet and is the model to copy: only the header block before `## Description` is searched, a missing file returns False.
- Tests: `scraper/tests/test_markdown_export.py` (see the `set_screenshot_line` / `set_stale_line` tests for the fixture style, `tmp_path`).

## Files to create/modify

- `scraper/job_scraper/core/markdown_export.py`
- `scraper/tests/test_markdown_export.py`

## Acceptance criteria

- `remove_screenshot_line(md_path: str) -> bool`: removes the first line starting with `- Screenshot:` found in the header block (lines before `## Description`); returns True if the file changed, False if the file does not exist, has no `## Description`, or has no such line. Nothing at or after `## Description` is ever touched (a description line starting with `- Screenshot:` survives). Idempotent: a second call returns False.
- Tests: file with the bullet -> True and the bullet gone, all other lines byte-identical; second call False; missing file False; file without the bullet False; a body line `- Screenshot: x` under `## Description` is kept; round trip `set_screenshot_line` then `remove_screenshot_line` restores the original text exactly.

## Definition of done

- Run only `uv run pytest tests/test_markdown_export.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S05: Add remove_screenshot_line markdown helper`.
- The orchestrator ticks `docs/todo.md`. Independent of S01-S04 but never run two scraper stories at once.
