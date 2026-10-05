# E14-S08 — guru: click "Show more" before the element screenshot

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

guru screenshots show the whole description instead of a 783x180 box truncated at "... Show more".

## Context

- Needs E14-S01 (`screenshot_pre_actions` in `SiteAdapter` + `capture_element`), E14-S03 and E14-S04 (pipeline/backfill forward it).
- `scraper/job_scraper/sites/guru.py`: `screenshot_selector = "pre.jobDetails__description"` (class `GuruAdapter`, STATIC fetch). Test: `scraper/tests/test_guru.py` has `test_screenshot_selector_matches_description_element(fixture)` over `tests/fixtures/guru/detail_2101732.html`. The saved fixture contains the text "Show more" (find the exact element/button around it, e.g. `grep -o '.\{200\}Show more' scraper/tests/fixtures/guru/detail_2101732.html`).
- QA evidence: `docs/e13-qa-results.md` section 9 (`guru-1728117-market-research-india.png`: TRUNCATED, 783x180).
- E14-S01's test (in `scraper/tests/test_screenshots.py`) asserts `screenshot_pre_actions == ()` for all adapters; this story changes that assertion for guru.

## Files to create/modify

- `scraper/job_scraper/sites/guru.py`
- `scraper/tests/test_guru.py`
- `scraper/tests/test_screenshots.py` (only the default-tuple assertion from E14-S01)

## Acceptance criteria

- Run the probe protocol of Appendix C on ONE live guru URL: confirm the "Show more" control exists, that clicking it extends the element (print `bounding_box()` height before/after), and capture the exact stable selector of the control. If clicking does not expand the text (control absent or navigates away), record `BLOCKED: <why>` in the commit body and make no code change.
- `GuruAdapter.screenshot_pre_actions = ("<selector of the Show more control>",)`; selector valid for both Playwright and soupsieve, no hashed class names.
- Test in `tests/test_guru.py`: parses the fixture and asserts `len(BeautifulSoup(html, "html.parser").select(adapter.screenshot_pre_actions[0])) >= 1` (the control exists in the saved HTML) and that `adapter.screenshot_pre_actions` is a non-empty tuple; if the control is only in the live DOM, save the probe's rendered HTML as `tests/fixtures/guru/rendered_<id>.html` and assert against it.
- `tests/test_screenshots.py`: the registered-adapters default-tuple test now asserts `isinstance(..., tuple)` for all adapters and `== ()` for every adapter except `guru`.
- Commit body line: `guru: pre_action <selector>; probe height <before> -> <after>`.

## Definition of done

- Run only `uv run pytest tests/test_guru.py tests/test_screenshots.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S08: guru clicks Show more before screenshot`.
- The orchestrator ticks `docs/todo.md`.
