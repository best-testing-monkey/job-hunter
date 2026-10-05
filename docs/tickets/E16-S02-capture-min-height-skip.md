# E16-S02 — `capture_element` skips captures shorter than `min_height`

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

A screenshot shorter than about 100 px (hero gated-teaser strips 640x65, unrecovered harveynash 1116x30 blanks) is never kept: no file is left and the result is `None` (skipped on purpose), not a failure.

## Context

- `scraper/job_scraper/core/screenshots.py`: `capture_element(url, selector, out_path, *, stealth, timeout_ms, hide_selectors, pre_actions, skip_selectors)` returns True / False / None (None = skipped on purpose, no file; E14-S02). `_capture_on_page(...)` does the per-page work for both launch paths (plain Playwright and `_capture_stealth`), `_screenshot_with_retry` writes the PNG; E16-S01 added `_settle` before it.
- Evidence: `docs/e14-qa-results.md` section 8 (7 hero PNGs below 100 px: 640x65 x5, 640x97 x2; 9 harveynash 1116x30).
- Tests: `scraper/tests/test_screenshots.py` (existing browser tests use elements of 300 px; check every existing test that captures an element shorter than 100 px and pass `min_height=0` there).

## Files to create/modify

- `scraper/job_scraper/core/screenshots.py`
- `scraper/tests/test_screenshots.py`

## Acceptance criteria

- `capture_element(..., min_height: int = 100)`; `_capture_stealth(...)` and `_capture_on_page(...)` get the same parameter and pass it through unchanged.
- In `_capture_on_page`, after `_settle` and before shooting: `box = page.locator(selector).first.bounding_box()`; if `box` is not None and `box["height"] < min_height` then log info `Skipping <url>: element only <h>px high`, `Path(out_path).unlink(missing_ok=True)`, return None (no PNG written).
- Module helper `_png_height(path) -> int | None` reads the IHDR height with `struct.unpack(">II", data[16:24])[1]` (None when the file is missing, shorter than 24 bytes or lacks the PNG magic). After the shot is written, if `_png_height(out_path)` is below `min_height` the file is deleted and the result is None. `min_height=0` disables both checks.
- `capture_element` returns None for the skip (the existing `except` still turns real exceptions into False).
- Browser tests (`file://`): a 60 px high element with default settings returns None and leaves no file; the same page with `min_height=0` returns True and a PNG of about 60 px; a 300 px element still returns True. Unit test of `_png_height` with hand-built bytes (valid header height 65 -> 65; garbage -> None; missing file -> None).
- Stealth path: a test with the existing `StealthyFetcher` monkeypatch pattern (see `test_stealth_saves_via_stealthy_fetcher`) where the fake page's `locator(...).first.bounding_box()` returns `{"height": 40}` expects None and no file.

## Definition of done

- Run only `uv run pytest tests/test_screenshots.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S02: Skip screenshots shorter than min_height`.
- The orchestrator ticks `docs/todo.md`. After E16-S01 (same files); E16-S12 follows.
