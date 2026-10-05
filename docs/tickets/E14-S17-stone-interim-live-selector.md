# E14-S17 — stone_interim: find a live selector or document BLOCKED

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

stone_interim (0 PNGs, no selector) gets a screenshot selector found on the LIVE client-rendered page, or a documented `BLOCKED`.

## Context

- `scraper/job_scraper/sites/stone_interim.py`: `screenshot_selector = None  # BLOCKED: saved human page has no description (client-rendered)`. Test: `scraper/tests/test_stone_interim.py` (fixtures in `scraper/tests/fixtures/stone_interim/`: `detail_4893.html` = client-rendered shell, `detail_4893_api_GetVacancy.json`). The human ad URL form is `https://www.stone-interim.nl/opdrachten/id/<id>/<slug>` (E13-S14).
- Not rebuildable from raw (`core/rebuild.py` `NOT_REBUILDABLE`); markdown comes from the API.
- QA evidence: docs/e13-qa-results.md sections 6/7/11 (stone_interim 26 files, "skipped_no_selector 26", live postings 19).
- The existing test asserts `screenshot_selector is None`; this story replaces it when a selector is found.

## Files to create/modify

- `scraper/job_scraper/sites/stone_interim.py`
- `scraper/tests/test_stone_interim.py`
- `scraper/tests/fixtures/stone_interim/rendered_<id>.html` (new, the trimmed rendered DOM from the probe)

## Acceptance criteria

- Probe protocol (Appendix C) on ONE live non-stale stone_interim URL (from `scraper.db`, `source_url like '%/opdrachten/id/%'`): wait up to 10 s for network idle (`page.wait_for_load_state("networkidle", timeout=10000)`, probe only — it is not a change to `capture_element`), print the visible text length of `body` and `count()` of candidate wrappers (a stable id/class/`data-*`/semantic element wrapping the vacancy description), save `page.content()`, take the element PNG, open it with the Read tool.
- If a stable single wrapper exists live: set `screenshot_selector` (plain CSS, no hashed class names, valid for soupsieve and Playwright), save the trimmed rendered HTML as `tests/fixtures/stone_interim/rendered_<id>.html` (under 50 KB, no personal data, scripts stripped), replace the `is None` test by the standard selector test against that fixture (exactly one match; contains a distinctive 40+ character sentence; no `nav/header/footer/form`; no "cookie" in text). If `capture_element` would need the client-rendered content to settle first, that works already because `wait_for_selector` waits up to 30 s for the element.
- If the live page also has no usable wrapper, or the description only arrives after interaction, or the site blocks the headless probe: keep `None`, update the comment to `BLOCKED: <specific finding from the probe>`, keep the `is None` test, record `BLOCKED: <why>` in the commit body.
- Commit body line: `stone_interim: <selector or BLOCKED: why>`.

## Definition of done

- Run only `uv run pytest tests/test_stone_interim.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S17: stone_interim live screenshot selector`.
- The orchestrator ticks `docs/todo.md`.
