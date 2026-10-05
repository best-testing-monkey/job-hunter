# E14-S19 — Capture screenshots inside the scraper's own anti-detect browser (StealthyFetcher)

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md`. (Added on the owner's decision of 2026-10-05: "screenshots should use the same anti-detect browser the scraper already uses". Background: E14-S11/S12 found circle8, sevenstars and wearedevelopers answer HTTP 403 to `capture_element(stealth=True)`, which launches bare `patchright chromium.launch(headless=True)`, although the scraper fetches the same sites fine with scrapling's `StealthyFetcher` (`FetchStrategy.STEALTH`, `job_scraper/sites/base.py` `fetch_page`).)

## Goal

For adapters whose `fetch_strategy` is `FetchStrategy.STEALTH`, `capture_element` runs the page load and the element screenshot inside `scrapling.fetchers.StealthyFetcher.fetch(url, headless=True, page_action=...)` — the same browser configuration the scraper uses for that site — instead of bare patchright. Non-stealth adapters keep the current plain-Playwright path unchanged.

## Context

- `scraper/job_scraper/core/screenshots.py` `capture_element(url, selector, out_path, *, stealth=False, timeout_ms=30000, hide_selectors=(), pre_actions=(), skip_selectors=())` returns `True` saved / `False` failed / `None` skipped on purpose, never raises; its body (viewport, `page.goto`, `_is_challenge`, hide style tag, pre-actions, `wait_for_selector`, skip check, retry on detach if E14-S13 has landed, `locator.first.screenshot`) must keep its behaviour and test coverage.
- `scraper/job_scraper/sites/base.py` `fetch_page(strategy, url, **kwargs)`: `StealthyFetcher.fetch(url, headless=True, **kwargs)`; extra kwargs pass through (some adapters may pass e.g. `network_idle=True`; grep `fetch_page(` in `scraper/job_scraper/sites/*.py` to see what each STEALTH adapter passes: circle8, sevenstars, wearedevelopers, ictergezocht, guru, freelancermap, planet_interim).
- Callers: `scraper/job_scraper/pipeline.py` (`stealth=adapter.fetch_strategy == FetchStrategy.STEALTH`) and `scraper/job_scraper/core/screenshot_backfill.py` (same expression) — keep their call signature; do not change them unless a new keyword is needed.
- scrapling is installed in `scraper/.venv` (read its source: `.venv/lib/python3.13/site-packages/scrapling/fetchers/` — find `StealthyFetcher.fetch`'s signature, how `page_action` is called (it receives the Playwright `Page` and must return it), what the returned `Response` offers (`.status`, `.headers`), and which timeout units it uses (ms vs s)). The page_action runs AFTER the page loaded.
- Tests: `scraper/tests/test_screenshots.py` (real-browser tests use `file://`/`set_content`, `@pytest.mark.enable_socket`, `needs_browser`).

## Files to create/modify

- `scraper/job_scraper/core/screenshots.py`
- `scraper/tests/test_screenshots.py`
- `scraper/README.md` (2-3 lines in the Screenshots section: stealth sites are captured inside the scraper's StealthyFetcher browser; the scraper does not try to solve or bypass challenges beyond what its own fetch does)

## Acceptance criteria

- Refactor so the per-page work (hide style, pre-actions, wait for selector, skip check, challenge check, element screenshot) lives in ONE function `_capture_on_page(page, ...) -> bool | None` used by both launch paths (plain Playwright and StealthyFetcher `page_action`), so behaviour cannot drift. Existing tests keep passing unchanged.
- `stealth=True` path: `StealthyFetcher.fetch(url, headless=True, page_action=cb)` where `cb(page)` runs `_capture_on_page` and stores its result in a closure variable and returns `page`; the viewport/timeouts match the plain path as closely as the fetcher allows (document differences in a comment). The challenge check uses the `Response` status/headers returned by `fetch` (and `page.title()` inside `cb`): when the response is a challenge (`_is_challenge`-style: `cf-mitigated: challenge`, or status 403/503 with a Cloudflare title such as "Just a moment..." / "Attention Required! | Cloudflare") return `None` WITHOUT taking a screenshot. Do not pass `solve_cloudflare` or any other challenge-solving option; only pass what is needed to take the screenshot (the scraper's own `fetch_page` calls for that adapter may use extra kwargs — do NOT copy challenge-solving kwargs).
- Any exception inside the stealth path returns `False` (logged), never raises; the partial PNG is removed on failure/skip; the stealth browser is always closed (the fetcher handles it — verify no leaked processes in tests: `pgrep -fa camoufox|chrome-headless|ms-playwright` after the test run shows none).
- Tests: (1) no browser: with `StealthyFetcher.fetch` monkeypatched to a fake that calls the `page_action` with a fake page object and returns a `SimpleNamespace(status=200, headers={})`, `capture_element(..., stealth=True)` returns True when the fake page's locator screenshot succeeds, False when it raises, None when the fake response is a 403 + "Just a moment..." title; assert `solve_cloudflare` is NOT in the kwargs passed to `fetch`. (2) one real-browser test for the stealth path on a `file://` page IF scrapling's StealthyFetcher can load `file://` URLs headlessly in this environment; otherwise skip it with a clear reason and rely on the monkeypatch tests plus the QA story. (3) plain path tests unchanged.
- Verification of the real effect on ONE site, at most 2 live loads: run `capture_element` with `stealth=True` for one non-stale circle8 posting (non-stale via READ-ONLY `sqlite3 "file:scraper/scraper.db?mode=ro"`, `- Source:` from `scraper/jobs/circle8-*.md`), selector `div.c-vacancy-paragraph__body-text`; record status/result in the commit body (True/False/None) and, if a PNG was produced, open it with the Read tool and state whether it shows only the ad. If it is still 403 through the real StealthyFetcher path, say so (BLOCKED for those sites; nothing more is attempted) — the commit still lands with the tests.

## Definition of done

- Run only `uv run pytest tests/test_screenshots.py -q` from `scraper/` (plus any other test file you touched).
- Committed in the SCRAPER repo as `E14-S19: Capture stealth-site screenshots inside StealthyFetcher`.
- The orchestrator ticks `docs/todo.md`.
