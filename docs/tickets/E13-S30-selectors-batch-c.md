# E13-S30 — Screenshot selectors: sevenstars, circle8, iamexpat, djinni

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Determine and verify the description CSS selector for 4 adapters (sevenstars, circle8, iamexpat, djinni) so screenshots capture only the description.

## Context

- Depends on E13-S21 (`SiteAdapter.screenshot_selector`). Each adapter file is `scraper/job_scraper/sites/<site_id>.py`, tests `scraper/tests/test_<site_id>.py`, fixtures `scraper/tests/fixtures/<site>/`.
- The selector is used by Playwright on the live page (`capture_element`): it must match exactly ONE element that wraps just the job description (heading + body text of the ad) — not the site nav/header/footer, cookie banner, similar-jobs list, or apply form. Use stable ids/classes from the page; avoid `nth-child` chains and generated hashes (e.g. `css-1x2y3z`, `BodyCenter_main__Sz_2E`-style CSS-module names are acceptable only if no stable alternative exists, and say so in the commit message).
- It must be a plain CSS selector valid for both Playwright and `soupsieve` (bs4's `soup.select`): no `:contains()`, no Playwright-only `text=`/`:has-text()`.
- Verification here is offline against saved HTML (bs4). The saved HTML is what the server sent; client-rendered pages may differ in the live DOM — flag any adapter whose fixture description is JS-rendered, so the live QA (E13-S35) checks it.
- Adapter hints (the description selectors the adapters already use for scraping are a starting point):
  - sevenstars: description comes from JSON-LD in the page; find the visible element holding the same text. Fixture `detail_7S-004982.html`. STEALTH site.
  - circle8: JSON-LD description; find the visible element. Fixture `detail_VNR-85422.html`. STEALTH site.
  - iamexpat: `.BodyCenter_main__Sz_2E` is the current scraping selector (CSS-module hashed name — look for a more stable parent/child class). Fixture `detail_tLJWUBCWY1P8MBXMScbwRE.html`; the element must not include the page sidebar/related jobs.
  - djinni: JSON-LD description; the visible element is the job-description block of the page. Fixtures `detail_848723.html` and `detail_850338.html` (parametrize over both).

## Files to create/modify

- `scraper/job_scraper/sites/sevenstars.py`, `scraper/tests/test_sevenstars.py`
- `scraper/job_scraper/sites/circle8.py`, `scraper/tests/test_circle8.py`
- `scraper/job_scraper/sites/iamexpat.py`, `scraper/tests/test_iamexpat.py`
- `scraper/job_scraper/sites/djinni.py`, `scraper/tests/test_djinni.py`

## Acceptance criteria

For EACH adapter (sevenstars, circle8, iamexpat, djinni):
- `screenshot_selector = "<css>"` is set as a class attribute (`None` only where this ticket says so).
- A new test `test_screenshot_selector_matches_description_element` in `tests/test_<site_id>.py` loads a saved detail HTML fixture (the human page; see hints for sites whose scrape-time fetch is JSON), runs `els = BeautifulSoup(html, "html.parser").select(adapter.screenshot_selector)` and asserts: `len(els) == 1`; `els[0].get_text()` contains a distinctive sentence copied from that fixture's description (at least 40 characters); `els[0].find(["nav", "header", "footer", "form"]) is None`; and `"cookie"` is not in `els[0].get_text().lower()`.
- Where more than one detail fixture exists, the test is parametrized over all of them (the selector must match exactly one element in each).
- If the fixture's HTML does not contain the description at all (client-rendered only), set `screenshot_selector` to the selector you can justify from the real page structure ONLY if a saved page in `scraper/raw/<site>/` contains it; otherwise leave it `None`, add a test asserting `None`, and record `BLOCKED: <why>` in the commit message body.
- The commit message body has one line per adapter: `<site_id>: <selector>` (or `BLOCKED`).
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S30: Screenshot selectors: sevenstars, circle8, iamexpat, djinni`.
- `docs/todo.md` item for E13-S30 checked off, committed in the JOB-HUNTER repo (`Mark E13-S30 as done in todo`).
