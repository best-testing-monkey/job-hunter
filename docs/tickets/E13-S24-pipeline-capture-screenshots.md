# E13-S24 — Capture screenshots during the scrape

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

While scraping, take an element screenshot of each newly written/changed posting's description and record it in the Markdown, logging and continuing on any failure.

## Context

- Depends on E13-S21 (`adapter.screenshot_selector`), E13-S22 (`core/screenshots.py: capture_element`), E13-S23 (`markdown_export.write(posting, jobs_dir, screenshot=None)`, `stem_for`, `screenshot_relpath`).
- `scraper/job_scraper/pipeline.py`: `run_site(adapter, repo, jobs_dir, run_started_at, raw_dir=None) -> dict` loops over stubs: fetch page, `parse_detail`, optional `write_raw`, `is_excluded`, `apply_dedup`, `repo.upsert` (returns `changed`), duplicates counted, otherwise `if changed: write(posting, jobs_dir); counters["written"] += 1`. `run(site_ids, repo, jobs_dir, ignore_robots=False, raw_dir=None)` instantiates adapters and calls `run_site(..., raw_dir=raw_dir)`.
- `FetchStrategy.STEALTH` adapters (`adapter.fetch_strategy`) need `stealth=True`.
- Screenshots are taken from `posting.source_url` (the human ad page — Part 2 of this epic makes that URL trustworthy) — not from `stub.detail_url`.
- Tests: `scraper/tests/test_pipeline.py` has `FakeAdapter` and `test_run_site_basic` (patches `job_scraper.pipeline.fetch_page`); copy that style, patch `job_scraper.pipeline.capture_element`.
- If the markdown is unchanged (`changed` False) nothing is captured here; missing screenshots for unchanged jobs are filled by the `screenshots` backfill command (E13-S26/S27).

## Files to create/modify

- `scraper/job_scraper/pipeline.py`
- `scraper/tests/test_pipeline.py`

## Acceptance criteria

- `run_site(..., screenshots_dir: str | None = None)` and `run(..., screenshots_dir: str | None = None)` (passed through). Default `None` = no screenshots, so every existing call/test behaves as before.
- When `screenshots_dir` is set AND `adapter.screenshot_selector` is set AND the posting is being written (not duplicate, `changed`): call `capture_element(posting.source_url, adapter.screenshot_selector, <screenshots_dir>/<stem>.png, stealth=adapter.fetch_strategy == FetchStrategy.STEALTH)` BEFORE writing the markdown; pass `screenshot=screenshot_relpath(stem)` to `write(...)` iff the capture returned True OR the PNG already exists on disk (so a previously captured screenshot isn't dropped from a rewritten file); otherwise `screenshot=None`.
- Any exception raised by `capture_element` (it shouldn't, but mocks can) is caught, a warning is printed to stderr, and the scrape continues: the posting is still written and counted in `written`.
- Counters gain two keys, always present: `screenshots_taken` and `screenshots_failed` (ints, 0 when screenshots are off).
- Tests (all with `capture_element` patched; none launches a browser): (1) capture returns True -> `<tmp>/shots` path passed is `<screenshots_dir>/fake-site-job-1-python-developer.png`, the written markdown contains `- Screenshot: screenshots/fake-site-job-1-python-developer.png`, `screenshots_taken == 2`; (2) returns False -> markdown has no `- Screenshot:` line, `written == 2`, `screenshots_failed == 2`; (3) raises `RuntimeError` -> scrape completes, `written == 2`; (4) `screenshots_dir=None` -> `capture_element` never called; (5) adapter with `screenshot_selector = None` -> never called; (6) a stealth adapter (`fetch_strategy = FetchStrategy.STEALTH`) gets `stealth=True`; static gets `False`; (7) excluded and duplicate postings trigger no capture.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S24: Capture screenshots during scrape`.
- `docs/todo.md` item for E13-S24 checked off, committed in the JOB-HUNTER repo (`Mark E13-S24 as done in todo`).
