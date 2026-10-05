# E14-S03 — Pipeline: pass pre-actions/skip selectors, count skips

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

`run_site` forwards `screenshot_pre_actions` and `screenshot_skip_selectors` to `capture_element` and treats a `None` result as "skipped", not "failed".

## Context

- `scraper/job_scraper/pipeline.py` `run_site`: counters dict has `screenshots_taken` / `screenshots_failed`; inside the `elif changed:` branch it calls `capture_element(posting.source_url, adapter.screenshot_selector, str(out_path), stealth=..., hide_selectors=adapter.screenshot_hide_selectors)` in a try/except, then `if ok or out_path.exists(): screenshot = screenshot_relpath(stem)`.
- `capture_element` returns True / False / None (None = skipped on purpose; E14-S02). Attributes `screenshot_pre_actions` / `screenshot_skip_selectors` exist on `SiteAdapter` (E14-S01/S02).
- `scraper/tests/test_pipeline.py`: helper `_run_shots`, class `ShotAdapter`, tests `test_screenshot_*` (patch `job_scraper.pipeline.capture_element`).

## Files to create/modify

- `scraper/job_scraper/pipeline.py`
- `scraper/tests/test_pipeline.py`

## Acceptance criteria

- The call passes `pre_actions=adapter.screenshot_pre_actions` and `skip_selectors=adapter.screenshot_skip_selectors` in addition to the existing keywords.
- New counter `"screenshots_skipped": 0` in the counters dict (also update the docstring list of counters). If `ok is None`: increment `screenshots_skipped` only (not `screenshots_failed`, not `screenshots_taken`); no `- Screenshot:` bullet unless a PNG already exists at `out_path`; the markdown is still written and `written` still incremented.
- A `True` result still counts taken; `False` or an exception still counts failed.
- Tests: new `test_screenshot_none_counts_skipped` (`return_value=None`: `screenshots_skipped == 2`, `screenshots_failed == 0`, `screenshots_taken == 0`, no `- Screenshot:` in the markdown, `written == 2`); new `test_screenshot_pre_actions_and_skip_selectors_passed` (subclass with both attributes set; `cap.call_args_list[0].kwargs` equals them). Any existing test that compares the whole counters dict is updated for the new key; no test is deleted or weakened.

## Definition of done

- Run only `uv run pytest tests/test_pipeline.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S03: Pipeline passes pre-actions and skip selectors, counts skips`.
- The orchestrator ticks `docs/todo.md`. `pipeline.py` is also touched by E14-S06 and E14-S07: run them in order.
