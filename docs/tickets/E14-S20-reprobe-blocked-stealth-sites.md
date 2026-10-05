# E14-S20 — Re-probe the stealth sites that were blocked (circle8, sevenstars, wearedevelopers) and fix their screenshots

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md`. Depends on E14-S19 (capture inside StealthyFetcher). Replaces the BLOCKED results of E14-S11 (circle8, sevenstars) and E14-S12 (wearedevelopers).

## Goal

With the new stealth capture path, each of circle8, sevenstars and wearedevelopers produces a screenshot of only the job ad, or is documented as still blocked.

## Context

- Previous results: `git -C scraper show ad88890 ed41ece 147f19e` (pinning tests only; circle8 selector `div.c-vacancy-paragraph__body-text` + hide `#CybotCookiebotDialog`; sevenstars `div.c-vacancy-paragraph__body-text.job-description` + same hide; wearedevelopers `section:has(> div.prose-base-content):not(section:has(> div.prose-base-content) ~ section)`, which E13 flagged as never matching live).
- Adapter files `scraper/job_scraper/sites/{circle8,sevenstars,wearedevelopers}.py`, tests `scraper/tests/test_{circle8,sevenstars,wearedevelopers}.py`, fixtures `scraper/tests/fixtures/<site>/`.
- `capture_element(..., stealth=True)` now runs inside `StealthyFetcher` (E14-S19). Probe through `capture_element` itself and, for diagnosis, a `StealthyFetcher.fetch(url, headless=True, page_action=cb)` script that prints candidate selector counts and fixed/sticky full-screen elements; owner rule: no challenge solving, no bypass beyond the scraper's own fetch.

## Files to create/modify

- `scraper/job_scraper/sites/circle8.py`, `sevenstars.py`, `wearedevelopers.py` (only if a fix is needed)
- `scraper/tests/test_circle8.py`, `test_sevenstars.py`, `test_wearedevelopers.py`
- `scraper/tests/fixtures/<site>/rendered_<id>.html` (new, only if the live DOM differs from the saved HTML)

## Acceptance criteria

- One site at a time, at most 2 live loads per site, each on a NON-stale posting (READ-ONLY `sqlite3 "file:scraper/scraper.db?mode=ro"`; `- Source:` from `scraper/jobs/<site>-*.md`). Record per site: result of `capture_element` (True/False/None), status/title if blocked, candidate-selector counts, fixed/sticky overlay list.
- If the page loads: fix per diagnosis exactly as E14-S11's acceptance describes (stable selector valid for soupsieve and Playwright, hide list incl. full-screen overlays like `#CybotCookiebotDialogBodyUnderlay`, optional `screenshot_pre_actions` such as Cookiebot decline). For wearedevelopers replace the `:has()`/`~` selector by a plain-CSS one with live count 1 (see E14-S12's criteria). Open each PNG with the Read tool and state in the commit body whether only the ad is visible.
- If a site is still 403/challenge via the stealth path: `BLOCKED: <why>`, keep the pinning test, change nothing else for that site.
- Tests per fixed site: selector matches exactly one element in the fixture (or the new rendered fixture) containing a distinctive 40+ character sentence, every hide selector is valid CSS, attribute values asserted verbatim.
- Commit body lines per site: `<site>: <selector> | hide <list> | pre <list or -> | live count <n>` or `BLOCKED`.

## Definition of done

- Run only `uv run pytest tests/test_circle8.py tests/test_sevenstars.py tests/test_wearedevelopers.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S20: Fix circle8, sevenstars and wearedevelopers screenshots via stealth capture`.
- The orchestrator ticks `docs/todo.md`.
