# E14-S07 — Rewrite the markdown when `source_url` changed (hash unchanged)

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

A live posting whose content hash is unchanged but whose `- Source:` line in `jobs/<stem>.md` differs from the freshly parsed `source_url` is rewritten (and re-screenshotted), so old `/job/go/` (working_nomads) and `/api/` (stone_interim) Source lines disappear after a normal rescrape.

## Context

- Root cause: `JobPosting.content_hash()` (`scraper/job_scraper/core/models.py`) does not include `source_url`; `JobRepository.upsert` therefore returns `False` for such a posting and `run_site` (`scraper/job_scraper/pipeline.py`, branch `elif changed:`) never rewrites the file. The DB row may already carry the new URL, so the check must compare against the MARKDOWN file, not the DB.
- QA evidence: `docs/e13-qa-results.md` sections 8, 10, 11: 52 working_nomads + 12 stone_interim files still carry old Source lines; backfill screenshots for working_nomads visit the stale `/job/go/` URL (50 failures).
- `scraper/job_scraper/core/markdown_export.py`: `filename_for(posting)`, `stem_for`, `set_screenshot_line` (style reference for small file helpers), `render`, `write`.
- Not rebuildable from raw (`core/rebuild.py` `NOT_REBUILDABLE`: working_nomads, tender_link, stone_interim), so the refresh is a normal live rescrape of those sites: `uv run python -m job_scraper scrape --site working_nomads --site stone_interim` (run by E14-S18, not here). Stale (delisted) files keep their old Source line; Epic 15 hides them after 2 days.
- Tests: `scraper/tests/test_markdown_export.py`, `scraper/tests/test_pipeline.py` (helper `_run_shots`, `FakeAdapter`).

## Files to create/modify

- `scraper/job_scraper/core/markdown_export.py`
- `scraper/job_scraper/pipeline.py`
- `scraper/tests/test_markdown_export.py`
- `scraper/tests/test_pipeline.py`

## Acceptance criteria

- `markdown_export.source_line_differs(md_path: str, source_url: str) -> bool`: True if the file does not exist, has no `- Source:` line, or its value (after `.strip()`) != `source_url`; False when equal.
- `run_site`: for a posting that is not a duplicate, not excluded and NOT `changed`, if `source_line_differs(Path(jobs_dir) / filename_for(posting), posting.source_url)` is True it takes exactly the same path as `changed` (screenshot capture when configured, `write(...)`, `counters["written"] += 1`). If the Source line is equal, nothing is written (idempotent: a second identical run writes 0 files).
- Tests: `source_line_differs` four cases (missing file, no Source line, different URL, same URL incl. surrounding whitespace); pipeline test: pre-write a markdown file with `- Source: https://old.example/job/go/1`, upsert the same posting into the repo first so the hash is unchanged, run `run_site`, assert the file now contains the new `- Source:` line and `written == 1`; a second `run_site` call yields `written == 0` and `duplicates` unchanged. Existing tests pass.

## Definition of done

- Run only `uv run pytest tests/test_markdown_export.py tests/test_pipeline.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S07: Rewrite markdown when the Source URL changed`.
- The orchestrator ticks `docs/todo.md`. `pipeline.py`/`test_pipeline.py` were edited by E14-S03 and S06: run after them.
