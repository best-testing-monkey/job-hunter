# E16-S03 — `SiteAdapter.screenshot_min_height` and the backfill passes it

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

The per-site minimum screenshot height lives on the adapter (default 100) and `screenshots --site X` hands it to `capture_element`; a skipped-small capture counts as `skipped_blocked` like other on-purpose skips.

## Context

- `scraper/job_scraper/sites/base.py`: `SiteAdapter` ClassVars `screenshot_selector`, `screenshot_hide_selectors`, `screenshot_pre_actions`, `screenshot_skip_selectors` (each followed by a docstring-style string).
- `scraper/job_scraper/core/screenshot_backfill.py`: `backfill_screenshots(...)`; `adapter = SITE_REGISTRY[site_id]` is the CLASS (not an instance); the `capture_element(...)` call passes hide/pre-action/skip selectors; `None` results go to `counts["skipped_blocked"]`. `capture_element(..., min_height=100)` exists after E16-S02.
- Tests: `scraper/tests/test_screenshot_backfill.py` has a plain `FakeAdapter` class (no base class) with the screenshot attributes and a helper `run(env, **kw)`; the existing tests patch `capture_element` in `sb` (read the file to copy the pattern).

## Files to create/modify

- `scraper/job_scraper/sites/base.py`
- `scraper/job_scraper/core/screenshot_backfill.py`
- `scraper/tests/test_screenshot_backfill.py`

## Acceptance criteria

- `SiteAdapter.screenshot_min_height: ClassVar[int] = 100` with a one-line explanatory docstring-string like its neighbours (captures with a shorter element are skipped on purpose).
- `backfill_screenshots` calls `capture_element(..., min_height=adapter.screenshot_min_height)` (plain attribute access; add the attribute to the test `FakeAdapter` instead of using getattr).
- Tests: `FakeAdapter.screenshot_min_height = 100`; a test asserts the patched `capture_element` receives `min_height=100`, and with `monkeypatch.setattr(FakeAdapter, "screenshot_min_height", 150)` receives 150; a test where the patched capture returns None counts `skipped_blocked == 1` and writes no `- Screenshot:` line. A test asserts every class in `SITE_REGISTRY` has `screenshot_min_height == 100` unless explicitly overridden (assert it is an int > 0).
- Existing assertions in the file still pass.

## Definition of done

- Run only `uv run pytest tests/test_screenshot_backfill.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S03: Add screenshot_min_height to adapters and pass it from the backfill`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S02. `base.py` is edited again in E16-S09 and `screenshot_backfill.py` in E16-S13: run in order.
