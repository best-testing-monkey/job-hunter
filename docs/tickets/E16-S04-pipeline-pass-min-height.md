# E16-S04 — pipeline passes `screenshot_min_height` to `capture_element`

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

`scrape` honours the same minimum height as the backfill: a too-small capture counts as `screenshots_skipped`, leaves no PNG and gets no `- Screenshot:` line.

## Context

- `scraper/job_scraper/pipeline.py` `run_site(...)`: inside the `elif changed or source_line_differs(...)` branch the `capture_element(posting.source_url, adapter.screenshot_selector, str(out_path), stealth=..., hide_selectors=..., pre_actions=..., skip_selectors=...)` call; `ok is None` -> `counters["screenshots_skipped"] += 1` and `screenshot` stays None when no file exists.
- `SiteAdapter.screenshot_min_height` exists after E16-S03; `FakeAdapter` in `scraper/tests/test_pipeline.py` subclasses `SiteAdapter` so it inherits it.
- Test pattern: see the existing screenshot tests in `scraper/tests/test_pipeline.py` (they patch `job_scraper.pipeline.capture_element`).

## Files to create/modify

- `scraper/job_scraper/pipeline.py`
- `scraper/tests/test_pipeline.py`

## Acceptance criteria

- The `capture_element` call gets `min_height=adapter.screenshot_min_height`.
- Test: patched `capture_element` called with `min_height=100` for the default adapter and with 150 when the test adapter overrides it; when the patched call returns None the counter `screenshots_skipped` is 1, the markdown has no `- Screenshot:` line and the posting is still written (`written == 1`).
- Existing pipeline tests unchanged and passing.

## Definition of done

- Run only `uv run pytest tests/test_pipeline.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S04: Pass screenshot_min_height from the pipeline`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S03. `pipeline.py` chain: S04 -> S11 -> S13.
