# E16-S13 — pipeline and backfill pass a `GoneCheck` to `capture_element`

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

Both callers hand the adapter's gone settings to `capture_element`, so a delisted page met during a screenshot is a counted skip (`screenshots_skipped` / `skipped_blocked`) and never a 30 s timeout failure.

## Context

- `scraper/job_scraper/pipeline.py` `run_site`: the `capture_element(posting.source_url, adapter.screenshot_selector, ..., min_height=...)` call (E16-S04); `ok is None` -> `screenshots_skipped`.
- `scraper/job_scraper/core/screenshot_backfill.py` `backfill_screenshots`: `adapter = SITE_REGISTRY[site_id]` is a CLASS; `SiteAdapter.gone_check` is a classmethod (E16-S09), so `adapter.gone_check(listing_id)` works on the class. The backfill knows only the job stem, not the listing id (ids may contain hyphens, e.g. `7S-004979`), so it passes `adapter.gone_check()` with an empty listing id: the id test is skipped and only `/`, the adapter's `listing_paths` and `gone_markers` apply (rule 6 never applies without an id).
- `capture_element(..., gone_check=...)` exists after E16-S12.
- Tests: `scraper/tests/test_screenshot_backfill.py` (plain `FakeAdapter` class: add `listing_paths = ()`, `gone_markers = ()` and a `gone_check` classmethod returning `GoneCheck("", (), ())`, or make it subclass the right thing; keep its other attributes), `scraper/tests/test_pipeline.py`.

## Files to create/modify

- `scraper/job_scraper/pipeline.py`
- `scraper/job_scraper/core/screenshot_backfill.py`
- `scraper/tests/test_pipeline.py`
- `scraper/tests/test_screenshot_backfill.py`

## Acceptance criteria

- Pipeline: `gone_check=adapter.gone_check(posting.listing_id)`. Backfill: `gone_check=adapter.gone_check()`.
- Tests: pipeline — patched `capture_element` receives `gone_check == GoneCheck(listing_id, adapter.listing_paths, adapter.gone_markers)`; a None result increments `screenshots_skipped`. Backfill — receives `gone_check == GoneCheck("", (), ())` for the fake, and `GoneCheck("", ("/jobs",), ())` when the fake declares `listing_paths = ("/jobs",)`; a None result counts `skipped_blocked`.
- All existing tests in both files pass.

## Definition of done

- Run only `uv run pytest tests/test_pipeline.py tests/test_screenshot_backfill.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S13: Pass GoneCheck from pipeline and backfill to capture_element`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S11 and E16-S12 (`pipeline.py` chain S04 -> S11 -> S13; `screenshot_backfill.py` chain S03 -> S13).
