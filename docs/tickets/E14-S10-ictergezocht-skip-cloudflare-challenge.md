# E14-S10 — ictergezocht: skip Cloudflare challenge pages cleanly (no bypass)

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

ictergezocht detail pages answer with a Cloudflare challenge (HTTP 403). Per the owner's rule nothing is bypassed: the screenshot step must detect the challenge, skip cleanly (not a failure, no 30 s timeout) and the situation is documented.

## Context

- Needs E14-S02 (`_is_challenge` + `capture_element` returning None for a challenge page) and E14-S03/S04 (callers count it as skipped).
- `scraper/job_scraper/sites/ictergezocht.py`: `screenshot_selector = "div.vacancy-full-text-dom"`, `screenshot_hide_selectors = ("#cookieyes-banner",)` — the CookieYes hide stays untouched. Test: `scraper/tests/test_ictergezocht.py`, fixture `scraper/tests/fixtures/ictergezocht/detail_438712.html`.
- QA evidence: `docs/e13-qa-results.md` sections 5, 6, 7, 11 (0/77 PNGs; all 79 raw pages are Cloudflare challenge pages; backfill ran 77 x 30 s timeouts).
- `scraper/README.md` has a "Screenshots" section (grep `-n -i screenshot scraper/README.md`) where site limitations are noted.

## Files to create/modify

- `scraper/job_scraper/sites/ictergezocht.py`
- `scraper/tests/test_ictergezocht.py`
- `scraper/README.md`

## Acceptance criteria

- ONE probe (Appendix C) against one live ictergezocht detail URL, headless, no stealth tricks, no challenge solving: print HTTP status, `cf-mitigated` response header and `page.title()`. Record the three values in the commit body.
- If the probe shows a challenge (403 and/or `cf-mitigated: challenge` or title "Just a moment..."): add a class attribute `screenshot_skip_selectors = ("#challenge-form", "#cf-challenge-running", "div.cf-browser-verification")` ONLY as a belt-and-braces addition (these ids/classes are Cloudflare's documented challenge markup); the primary detection is the generic `_is_challenge` from E14-S02. If the probe unexpectedly returns the real page (no challenge), keep the code as is, record that in the commit body and README, and do not add skip selectors.
- Test: parametrized `BeautifulSoup(...).select` validity check of every skip selector (no exception); a test pinning `screenshot_hide_selectors == ("#cookieyes-banner",)` (unchanged); a test reading a tiny inline challenge HTML string (`<form id="challenge-form"></form>`) and asserting the skip selectors match it and do NOT match `tests/fixtures/ictergezocht/detail_438712.html`.
- `scraper/README.md`: 2-4 lines under the Screenshots section: "ictergezocht: detail pages are behind a Cloudflare challenge; no screenshots are taken (skipped, not counted as failures). The scraper never bypasses bot walls."
- Commit body line: `ictergezocht: challenge detected (status/header/title) -> skipped`.

## Definition of done

- Run only `uv run pytest tests/test_ictergezocht.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S10: ictergezocht skips Cloudflare challenge pages`.
- The orchestrator ticks `docs/todo.md`.
