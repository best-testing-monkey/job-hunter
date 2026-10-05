# E14-S13 — iamexpat: narrower wrapper, extra widgets hidden, retry on detach

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

iamexpat screenshots show only the ad (no Apply/Bookmark/Share buttons, "Want more jobs like this?" signup, "More jobs from this employer", "Similar jobs", floating ad box) and no longer fail with "Element is not attached to the DOM".

## Context

- `scraper/job_scraper/sites/iamexpat.py`: `screenshot_selector = "div.BodyCenter_main__Sz_2E"` (hashed CSS-module class), no hide list. Test: `scraper/tests/test_iamexpat.py` `test_screenshot_selector_matches_description_element` (fixture `tests/fixtures/iamexpat/detail_tLJWUBCWY1P8MBXMScbwRE.html`).
- QA evidence: docs/e13-qa-results.md section 6 (20 failures `Locator.screenshot: Element is not attached to the DOM`), section 9 (png shows widgets), section 7 (iamexpat 246/305, live 244/264).
- `scraper/job_scraper/core/screenshots.py` `capture_element`: `page.locator(selector).first.screenshot(path=out_path)` right after `wait_for_selector`; the page re-renders (hydration) between those two calls, so the located element can detach. Test pattern: `scraper/tests/test_screenshots.py`.

## Files to create/modify

- `scraper/job_scraper/sites/iamexpat.py`
- `scraper/job_scraper/core/screenshots.py`
- `scraper/tests/test_iamexpat.py`
- `scraper/tests/test_screenshots.py`

## Acceptance criteria

- Shared retry (screenshots.py): the `wait_for_selector` + `locator.screenshot` pair is attempted up to 2 times; the second attempt only when the first raised an exception whose message contains `"not attached"` or `"detached"` (case-insensitive); before retrying call `page.wait_for_timeout(500)`. Other errors fail immediately as before; `capture_element` still never raises. Test (browser, `file://`, `enable_socket`, `needs_browser`): a page whose inline script replaces `#job` with a fresh clone 50 ms after load (`setTimeout`) and again never — capture returns True; a unit test with a stub `locator` whose first `screenshot` raises `Exception("Element is not attached to the DOM")` and second succeeds (use `unittest.mock` against a small extracted helper `_screenshot_with_retry(page, selector, out_path, timeout_ms)`) returns normally, while an `Exception("boom")` is raised after exactly one attempt.
- Probe protocol (Appendix C) on ONE live non-stale iamexpat posting (`launcher` per `fetch_strategy`): find the description wrapper that is NOT the hashed `BodyCenter_main__*` class (a stable semantic element/id/`data-*`/`itemprop`, e.g. one wrapping the "Job description" headings), print its count (must be 1) and bounding box, and list the widget elements to hide (Apply/Bookmark/Share bar, alert signup, "More jobs from this employer", "Similar jobs", floating ad) with stable selectors.
- `screenshot_selector` = the narrower stable wrapper if the probe finds one; otherwise keep the hashed class and say so in the commit body. `screenshot_hide_selectors` = tuple of the widget selectors (each valid for soupsieve and Playwright).
- Tests: fixture test asserts exactly one match of the new selector with a distinctive 40+ character sentence from the ad, no `nav/header/footer/form` inside; every hide selector is valid CSS; if the widgets exist in the saved fixture, they are matched by the hide selectors (assert `len(select(sel)) >= 1` for those that exist) and are NOT descendants of the screenshot element unless hidden by the list (assert via `el.select(hide)` for any that are inside).
- Commit body line: `iamexpat: <selector> | hide <list>`.

## Definition of done

- Run only `uv run pytest tests/test_iamexpat.py tests/test_screenshots.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S13: iamexpat narrower screenshot wrapper and retry on detach`.
- The orchestrator ticks `docs/todo.md`. `screenshots.py`/`test_screenshots.py` were edited in E14-S01/S02: run after them.
