# E14-S15 — synprofs: hide the sticky site header

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

synprofs screenshots no longer have the sticky header (logo + "Opdrachten / Leveranciers / ZZP-ers" nav) overlapping the top lines.

## Context

- `scraper/job_scraper/sites/synprofs.py`: `screenshot_selector = "div.sd-sdcx-components-vacancies-parts-publication-text"`, no hide list. Test: `scraper/tests/test_synprofs.py` (fixture `tests/fixtures/synprofs/detail_6930.html`). The fixture contains `<header id="masthead" class="site-header fixed" role="banner">`.
- QA evidence: docs/e13-qa-results.md section 9 (`synprofs-6912-ai-developer.png`: header overlaps the first lines); tender_link shares the same screenshot selector but is a different site with 231/231 live coverage — do NOT touch it.

## Files to create/modify

- `scraper/job_scraper/sites/synprofs.py`
- `scraper/tests/test_synprofs.py`

## Acceptance criteria

- Probe protocol (Appendix C) on ONE live non-stale synprofs posting: confirm `header#masthead` is fixed/sticky and overlaps the element, take the element PNG with `header#masthead { display:none }` applied, open it with the Read tool and confirm the top lines are clean. Also list any other fixed element (chat widget, cookie bar) and add it if it overlaps.
- `screenshot_hide_selectors = ("header#masthead",)` plus any extra selector the probe proved necessary.
- Tests: attribute asserted verbatim; every hide selector valid CSS; `header#masthead` matches exactly one element in `detail_6930.html` and is not a descendant of the screenshot element (`el.select_one("header#masthead") is None`); the existing selector test stays green.
- Commit body line: `synprofs: hide <list>`.

## Definition of done

- Run only `uv run pytest tests/test_synprofs.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S15: synprofs hides sticky header`.
- The orchestrator ticks `docs/todo.md`.
