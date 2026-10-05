# E16-S12 — `capture_element` skips pages that are gone (404/410, unrelated redirect, soft-404 title)

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

When the screenshot step itself lands on a delisted page, no PNG is written and the result is `None` (skipped on purpose, counted `skipped_blocked` by the callers) instead of a 30 s selector timeout counted as a failure.

## Context

- `scraper/job_scraper/core/screenshots.py`: plain path `capture_element` -> `page.goto(...)` returns `response` (`response.status`, `response.headers`; `page.url` is the final URL) -> `_capture_on_page(page, response, url, ...)`; stealth path `_capture_stealth` -> `StealthyFetcher.fetch(url, headless=True, timeout=..., page_action=cb)` returns a scrapling `Response` (`.status`, `.url`) AFTER the callback ran, and the callback calls `_capture_on_page(page, None, ...)`. `_is_challenge(response, title)` already uses status 403/503 + title. Because the stealth status is known only after the callback, the callback's check for status is impossible; the callback checks the redirected `page.url` and the title, and the post-fetch step checks `response.status`/`response.url` (same pattern as the challenge check, which deletes the file and returns None).
- `GoneCheck`, `gone_reason` from `scraper/job_scraper/core/gone.py` (E16-S08). `capture_element(..., min_height=100)` from E16-S02.
- Tests: `scraper/tests/test_screenshots.py` (stealth tests monkeypatch `scrapling.fetchers.StealthyFetcher.fetch`, see `test_stealth_challenge_returns_none`; unit tests with fake page/response objects).

## Files to create/modify

- `scraper/job_scraper/core/screenshots.py`
- `scraper/tests/test_screenshots.py`

## Acceptance criteria

- `capture_element(..., gone_check: GoneCheck | None = None)`; `_capture_on_page` and `_capture_stealth` get the same keyword (default None = no gone detection, old behaviour).
- In `_capture_on_page`, right after the existing challenge check and before any style/pre-action work: if `gone_check` is not None, compute `gone_reason(response.status if response is not None else None, url, page.url, f"<title>{title}</title>", gone_check)` (`title` is the already-read `page.title()`; only the title is checked for markers); when it returns a reason: log info `Skipping <url>: posting gone (<reason>)`, delete `out_path` (`unlink(missing_ok=True)`), return None.
- Stealth path: after the fetch returns (same place as the existing challenge check) call `gone_reason(response.status, url, response.url, None, gone_check)` when `gone_check` is not None; a reason deletes the file and returns None. A missing `.status`/`.url` attribute (fake) never triggers.
- Tests: plain path unit test with a fake `page` (`.url`, `.title()`) and fake `response` (`.status`=404, `.headers={}`): `_capture_on_page` returns None, `out_path` does not exist, and no `wait_for_selector`/screenshot call was made; same for status 410; for status 200 with `page.url` redirected to `https://s.test/jobs` and `GoneCheck("123", ("/jobs",))`; for a title `Job Not Found` with marker; with `gone_check=None` and status 404 the old flow continues (the fake page then records a `wait_for_selector` call); a normal 200 with the same URL continues; stealth: monkeypatched `StealthyFetcher.fetch` returning a fake with `status=404`, `url` unchanged -> `capture_element(..., stealth=True, gone_check=GoneCheck())` is None and the file was removed; a fake with `status=200`, `url` redirected to `/jobs` -> None; `status=200` and same URL -> True (existing success test shape).
- Existing tests still pass (the browser tests do not pass `gone_check`, so nothing triggers).

## Definition of done

- Run only `uv run pytest tests/test_screenshots.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S12: Skip screenshots of delisted pages`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S02 and E16-S08 (`screenshots.py` chain S01 -> S02 -> S12).
