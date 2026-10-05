# E14-S11 — circle8 + sevenstars: find why Cookiebot still blocks, fix the hide list/waits

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

circle8 (0/11 PNGs) and sevenstars (0/23) produce screenshots: find the real cause with ONE live probe per site and fix selectors, hide list or waits.

## Context

- Both adapters already hide the dialog: `scraper/job_scraper/sites/circle8.py` (`screenshot_selector = "div.c-vacancy-paragraph__body-text"`, `screenshot_hide_selectors = ("#CybotCookiebotDialog",)`) and `sevenstars.py` (`screenshot_selector = "div.c-vacancy-paragraph__body-text.job-description"`, same hide). `capture_element` (`scraper/job_scraper/core/screenshots.py`) already hides `GENERIC_HIDE_SELECTORS` incl. `#CybotCookiebotDialog`, but the QA backfill (docs/e13-qa-results.md sections 6/7) still hit `wait_for_selector` 30 s timeouts on all of them — so the overlay is not the (only) cause. Candidates: the selector never matches the live DOM (classes differ from the saved HTML), content is client-rendered after `domcontentloaded`, the vacancy page redirects (delisted -> list), Cookiebot's wrapper has another id (e.g. `#CybotCookiebotDialogBodyUnderlay`), or the page is behind a bot check.
- Tests: `scraper/tests/test_circle8.py` (fixture `tests/fixtures/circle8/detail_VNR-85422.html`), `scraper/tests/test_sevenstars.py`. Both have `test_screenshot_selector_matches_description_element` and hide-selector tests from E13-S30/S36.

## Files to create/modify

- `scraper/job_scraper/sites/circle8.py`
- `scraper/job_scraper/sites/sevenstars.py`
- `scraper/tests/test_circle8.py`
- `scraper/tests/test_sevenstars.py`
- `scraper/tests/fixtures/circle8/rendered_<id>.html`, `scraper/tests/fixtures/sevenstars/rendered_<id>.html` (new, only if the live DOM differs from the saved HTML)

## Acceptance criteria

- Probe protocol (Appendix C), one run per site, on a NON-stale posting. In the commit body state per site the diagnosed cause in one line (e.g. `circle8: selector matched 0 elements live; real class is X`) with the printed evidence (count per candidate selector, status, final URL, fixed/sticky elements list).
- Fix per diagnosis: corrected `screenshot_selector` (stable class/id, valid for soupsieve and Playwright), and/or extended `screenshot_hide_selectors` (add every full-screen fixed element the probe listed, e.g. `#CybotCookiebotDialogBodyUnderlay`), and/or extra tuple entries. A wait/timing fix is allowed only inside the adapter via `screenshot_pre_actions` (E14-S01), e.g. clicking Cookiebot's "Allow all"/"Deny" button (`#CybottCookiebotDialogBodyButtonDecline` style id, take the real id from the probe) — never by editing `capture_element`.
- The probe's element PNG for each site, opened with the Read tool, shows only the job description; state yes/no in the commit body. If a site cannot be fixed (redirect/bot wall/delisted only), write `BLOCKED: <why>` for that site, change nothing but a test pinning the current attributes, and continue with the other site.
- Tests: for each fixed site the selector test runs against the fixture (or the new rendered fixture) and asserts exactly one match containing a distinctive 40+ character sentence from the ad; every hide selector is valid CSS (`select` raises nothing); the attribute values are asserted verbatim.
- Commit body lines: `circle8: <selector> | hide <list> | pre <list or ->` and the same for `sevenstars`.

## Definition of done

- Run only `uv run pytest tests/test_circle8.py tests/test_sevenstars.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S11: Fix circle8 and sevenstars screenshots (Cookiebot)`.
- The orchestrator ticks `docs/todo.md`.
