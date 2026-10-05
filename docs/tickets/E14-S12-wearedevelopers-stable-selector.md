# E14-S12 — wearedevelopers: replace the `:has()` selector with a stable one

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

wearedevelopers (0/24 PNGs) gets a screenshot selector that actually matches the live page.

## Context

- `scraper/job_scraper/sites/wearedevelopers.py` (STEALTH fetch, so probe with patchright): `screenshot_selector` is `section:has(> div.prose-base-content):not(section:has(> div.prose-base-content) ~ section)`; the QA backfill found it never visible live (docs/e13-qa-results.md sections 6/7/11). Tests: `scraper/tests/test_wearedevelopers.py`, `test_screenshot_selector_matches_description_element(fixture, snippet)` parametrized over `tests/fixtures/wearedevelopers/detail_1343363.html`, `detail_2203015.html`, `detail_2904764.html`.
- Possible causes: `:has()`/`:not(... ~ section)` evaluates differently live, the page is client-rendered (the saved HTML is what STEALTH fetch returned, the live DOM may differ), the page is gated or a redirect.

## Files to create/modify

- `scraper/job_scraper/sites/wearedevelopers.py`
- `scraper/tests/test_wearedevelopers.py`
- `scraper/tests/fixtures/wearedevelopers/rendered_<id>.html` (new, only if the live DOM differs from the saved HTML)

## Acceptance criteria

- Probe protocol (Appendix C) on ONE live non-stale posting: print `count()` for the old selector and for 3 candidate plain-CSS selectors (e.g. `div.prose-base-content`, or a wrapper built from a stable `id`/`data-*`/semantic class), plus the element PNG of the best candidate; open it with the Read tool.
- New `screenshot_selector`: plain CSS, no `:has()`, no `:not(... ~ ...)`, no `nth-child` chains, no hashed/utility-only classes; matches exactly ONE element live (probe count == 1) containing the job description but not nav/header/footer/cookie banner. If the only stable option is the first `div.prose-base-content`, use `div.prose-base-content` and make `capture_element`'s `.first` pick it (it already uses `.first`; state this in the commit body) — then the test must accept `len(els) >= 1` and assert `els[0]` holds the description.
- Tests: the parametrized selector test passes on all three saved fixtures (adjust the assertions to the new selector: first match contains the existing `snippet`; no `nav/header/footer/form` inside; `"cookie"` not in its text), and a new test asserts `":has(" not in adapter.screenshot_selector`.
- If the live probe shows the page is gated, blocked or still not matching anything stable: `BLOCKED: <why>` in the commit body, no selector change.
- Commit body line: `wearedevelopers: <selector>; live count <n>`.

## Definition of done

- Run only `uv run pytest tests/test_wearedevelopers.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S12: wearedevelopers stable screenshot selector`.
- The orchestrator ticks `docs/todo.md`.
