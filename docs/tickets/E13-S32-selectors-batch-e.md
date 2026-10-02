# E13-S32 — Screenshot selectors: ictergezocht, wearedevelopers, headfirst, planet_interim

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Determine and verify the description CSS selector for 4 adapters (ictergezocht, wearedevelopers, headfirst, planet_interim) so screenshots capture only the description.

## Context

- Depends on E13-S21 (`SiteAdapter.screenshot_selector`). Each adapter file is `scraper/job_scraper/sites/<site_id>.py`, tests `scraper/tests/test_<site_id>.py`, fixtures `scraper/tests/fixtures/<site>/`.
- The selector is used by Playwright on the live page (`capture_element`): it must match exactly ONE element that wraps just the job description (heading + body text of the ad) — not the site nav/header/footer, cookie banner, similar-jobs list, or apply form. Use stable ids/classes from the page; avoid `nth-child` chains and generated hashes (e.g. `css-1x2y3z`, `BodyCenter_main__Sz_2E`-style CSS-module names are acceptable only if no stable alternative exists, and say so in the commit message).
- It must be a plain CSS selector valid for both Playwright and `soupsieve` (bs4's `soup.select`): no `:contains()`, no Playwright-only `text=`/`:has-text()`.
- Verification here is offline against saved HTML (bs4). The saved HTML is what the server sent; client-rendered pages may differ in the live DOM — flag any adapter whose fixture description is JS-rendered, so the live QA (E13-S35) checks it.
- Adapter hints (the description selectors the adapters already use for scraping are a starting point):
  - ictergezocht: `div.vacancy-full-text-dom`. Fixture `detail_438712.html`. STEALTH site.
  - wearedevelopers: the `<div>` after the `<h2>` "Job description" (find a class/id for it). Fixtures `detail_1343363.html`, `detail_2203015.html`, `detail_2904764.html` (parametrize over all three). STEALTH site.
  - headfirst: scrapes no description (description is empty with a scrape note) and its `source_url` may be an overview page (see E13-S17) -> `screenshot_selector` stays `None`; the test asserts `HeadfirstAdapter.screenshot_selector is None`. (Skip the HTML-selector assertions for it.)
  - planet_interim: description requires a login and is not scraped -> `screenshot_selector` stays `None`; test asserts it.

## Files to create/modify

- `scraper/job_scraper/sites/ictergezocht.py`, `scraper/tests/test_ictergezocht.py`
- `scraper/job_scraper/sites/wearedevelopers.py`, `scraper/tests/test_wearedevelopers.py`
- `scraper/job_scraper/sites/headfirst.py`, `scraper/tests/test_headfirst.py`
- `scraper/job_scraper/sites/planet_interim.py`, `scraper/tests/test_planet_interim.py`

## Acceptance criteria

For EACH adapter (ictergezocht, wearedevelopers, headfirst, planet_interim):
- `screenshot_selector = "<css>"` is set as a class attribute (`None` only where this ticket says so).
- A new test `test_screenshot_selector_matches_description_element` in `tests/test_<site_id>.py` loads a saved detail HTML fixture (the human page; see hints for sites whose scrape-time fetch is JSON), runs `els = BeautifulSoup(html, "html.parser").select(adapter.screenshot_selector)` and asserts: `len(els) == 1`; `els[0].get_text()` contains a distinctive sentence copied from that fixture's description (at least 40 characters); `els[0].find(["nav", "header", "footer", "form"]) is None`; and `"cookie"` is not in `els[0].get_text().lower()`.
- Where more than one detail fixture exists, the test is parametrized over all of them (the selector must match exactly one element in each).
- If the fixture's HTML does not contain the description at all (client-rendered only), set `screenshot_selector` to the selector you can justify from the real page structure ONLY if a saved page in `scraper/raw/<site>/` contains it; otherwise leave it `None`, add a test asserting `None`, and record `BLOCKED: <why>` in the commit message body.
- The commit message body has one line per adapter: `<site_id>: <selector>` (or `BLOCKED`).
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S32: Screenshot selectors: ictergezocht, wearedevelopers, headfirst, planet_interim`.
- `docs/todo.md` item for E13-S32 checked off, committed in the JOB-HUNTER repo (`Mark E13-S32 as done in todo`).
