# E14-S09 — hero: detect the gated teaser and skip the screenshot

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

For hero postings that show a login-gated, blurred teaser, record no screenshot (counted as skipped) instead of saving a 640x65 strip.

## Context

- Needs E14-S02 (`screenshot_skip_selectors`, `capture_element` returns None for a skip) and E14-S03/S04 (pipeline/backfill honour it).
- `scraper/job_scraper/sites/hero.py`: `screenshot_selector = "div.hero-requisition-body"`. Test: `scraper/tests/test_hero.py`, fixture `scraper/tests/fixtures/hero/detail_e98187b8.html`.
- QA evidence: `docs/e13-qa-results.md` section 9 (`hero-13f09263-functioneel-beheerder.png`: 640x65 strip of blurred text with "Log in om de volledige aanvraag te zien") and section 7 (hero 43/80 PNG, live 37/38; the misses are delisted/gated postings).

## Files to create/modify

- `scraper/job_scraper/sites/hero.py`
- `scraper/tests/test_hero.py`
- `scraper/tests/fixtures/hero/gated_teaser.html` (new, only if the live probe gives a gated page)

## Acceptance criteria

- Probe protocol (Appendix C) on ONE live hero page. Use a URL of a posting known to be gated: find one with `grep -l "Log in om de volledige" scraper/raw/hero/*.html | head -1` and take the matching `- Source:` from `scraper/jobs/<stem>.md` (do not scan many pages). Record: the element that carries the gate text/blur (a stable selector, e.g. an id/`data-*`/semantic class; not a Tailwind utility chain), and `count()` of it on a normal (non-gated) page of the saved fixture to prove it does not appear there.
- `HeroAdapter.screenshot_skip_selectors = ("<gate selector>",)`.
- Test 1: the gate selector, run with `BeautifulSoup(...).select`, matches the saved gated page (`tests/fixtures/hero/gated_teaser.html`, trimmed from the probe's `page.content()` or from the raw page, under 50 KB) and matches NOTHING in `detail_e98187b8.html` (the ungated page).
- Test 2: the selector is valid CSS (no exception on `select`) and `screenshot_skip_selectors` is a non-empty tuple.
- If no stable gate selector exists, record `BLOCKED: <why>` in the commit body, add a test pinning `screenshot_skip_selectors == ()`, and change nothing else.
- Commit body line: `hero: skip <selector>`.

## Definition of done

- Run only `uv run pytest tests/test_hero.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S09: hero skips gated teaser screenshots`.
- The orchestrator ticks `docs/todo.md`.
