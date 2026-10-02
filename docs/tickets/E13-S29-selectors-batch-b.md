# E13-S29 — Screenshot selectors: stone_interim, tender_link, harveynash, working_nomads

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Determine and verify the description CSS selector for 4 adapters (stone_interim, tender_link, harveynash, working_nomads) so screenshots capture only the description.

## Context

- Depends on E13-S21 (`SiteAdapter.screenshot_selector`). Each adapter file is `scraper/job_scraper/sites/<site_id>.py`, tests `scraper/tests/test_<site_id>.py`, fixtures `scraper/tests/fixtures/<site>/`.
- The selector is used by Playwright on the live page (`capture_element`): it must match exactly ONE element that wraps just the job description (heading + body text of the ad) — not the site nav/header/footer, cookie banner, similar-jobs list, or apply form. Use stable ids/classes from the page; avoid `nth-child` chains and generated hashes (e.g. `css-1x2y3z`, `BodyCenter_main__Sz_2E`-style CSS-module names are acceptable only if no stable alternative exists, and say so in the commit message).
- It must be a plain CSS selector valid for both Playwright and `soupsieve` (bs4's `soup.select`): no `:contains()`, no Playwright-only `text=`/`:has-text()`.
- Verification here is offline against saved HTML (bs4). The saved HTML is what the server sent; client-rendered pages may differ in the live DOM — flag any adapter whose fixture description is JS-rendered, so the live QA (E13-S35) checks it.
- Adapter hints (the description selectors the adapters already use for scraping are a starting point):
  - These four fetch JSON/API data at scrape time, but the screenshot opens `source_url`, the HUMAN page, so the selector is tested against the human-page HTML fixture:
    - stone_interim: `tests/fixtures/stone_interim/detail_4893.html` (human page for id 4893).
    - tender_link: `tests/fixtures/tender_link/detail_33345.html`.
    - harveynash: `tests/fixtures/harveynash/detail_299204.html` (Next.js page; the description is in `__NEXT_DATA__` JSON — confirm the server-rendered HTML also contains the description inside an element, otherwise follow the BLOCKED rule).
    - working_nomads: `tests/fixtures/working_nomads/detail_1785901.html` (added by E13-S13; a Working Nomads page, Angular app — check the description is present in the saved HTML).
  - For these four the existing tests build postings from JSON/listing fixtures; the new selector test only needs the HTML fixture and does not call `parse_detail`.

## Files to create/modify

- `scraper/job_scraper/sites/stone_interim.py`, `scraper/tests/test_stone_interim.py`
- `scraper/job_scraper/sites/tender_link.py`, `scraper/tests/test_tender_link.py`
- `scraper/job_scraper/sites/harveynash.py`, `scraper/tests/test_harveynash.py`
- `scraper/job_scraper/sites/working_nomads.py`, `scraper/tests/test_working_nomads.py`

## Acceptance criteria

For EACH adapter (stone_interim, tender_link, harveynash, working_nomads):
- `screenshot_selector = "<css>"` is set as a class attribute (`None` only where this ticket says so).
- A new test `test_screenshot_selector_matches_description_element` in `tests/test_<site_id>.py` loads a saved detail HTML fixture (the human page; see hints for sites whose scrape-time fetch is JSON), runs `els = BeautifulSoup(html, "html.parser").select(adapter.screenshot_selector)` and asserts: `len(els) == 1`; `els[0].get_text()` contains a distinctive sentence copied from that fixture's description (at least 40 characters); `els[0].find(["nav", "header", "footer", "form"]) is None`; and `"cookie"` is not in `els[0].get_text().lower()`.
- Where more than one detail fixture exists, the test is parametrized over all of them (the selector must match exactly one element in each).
- If the fixture's HTML does not contain the description at all (client-rendered only), set `screenshot_selector` to the selector you can justify from the real page structure ONLY if a saved page in `scraper/raw/<site>/` contains it; otherwise leave it `None`, add a test asserting `None`, and record `BLOCKED: <why>` in the commit message body.
- The commit message body has one line per adapter: `<site_id>: <selector>` (or `BLOCKED`).
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S29: Screenshot selectors: stone_interim, tender_link, harveynash, working_nomads`.
- `docs/todo.md` item for E13-S29 checked off, committed in the JOB-HUNTER repo (`Mark E13-S29 as done in todo`).
