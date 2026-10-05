# E14-S04 — Backfill: pass pre-actions/skip selectors, count skips

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

`backfill_screenshots` forwards `screenshot_pre_actions` and `screenshot_skip_selectors` and counts a `None` capture result as `skipped_blocked`.

## Context

- `scraper/job_scraper/core/screenshot_backfill.py` `backfill_screenshots(site_id, jobs_dir, screenshots_dir, missing_only=False, delay=1.0)`: counts keys `attempted, captured, failed, skipped_existing, skipped_no_selector`; calls `capture_element(match.group(1).strip(), selector, str(png), stealth=stealth, hide_selectors=adapter.screenshot_hide_selectors)`.
- `capture_element` returns True / False / None (None = skipped on purpose; E14-S02).
- `scraper/tests/test_screenshot_backfill.py`: `FakeAdapter` is a plain class (attributes `screenshot_selector`, `screenshot_hide_selectors`, `fetch_strategy`), `run(env, **kw)`, tests patch `sb.capture_element`; `test_all_success` compares the counts dict with `==`.
- `scraper/job_scraper/cli.py` `handle_screenshots` just prints `json.dumps(counters)`; no change needed there.

## Files to create/modify

- `scraper/job_scraper/core/screenshot_backfill.py`
- `scraper/tests/test_screenshot_backfill.py`

## Acceptance criteria

- The capture call additionally passes `pre_actions=adapter.screenshot_pre_actions` and `skip_selectors=adapter.screenshot_skip_selectors`.
- New counts key `"skipped_blocked": 0` (present in every returned dict, including the `skipped_no_selector` early return). A `None` result increments `skipped_blocked` only: not `failed`, not `captured`, no `set_screenshot_line` call, the markdown file is untouched. `attempted` still counts the attempt.
- Tests: `FakeAdapter` gains `screenshot_pre_actions = ()` and `screenshot_skip_selectors = ()`; every existing equality assertion on the counts dict gains `"skipped_blocked": 0`; new test with `return_value=None` asserts `skipped_blocked == 2`, `failed == 0`, `captured == 0` and that the md files are byte-identical to before; new test asserts the two kwargs are forwarded (set non-empty tuples on a `FakeAdapter` subclass registered via `monkeypatch.setitem(SITE_REGISTRY, ...)`).

## Definition of done

- Run only `uv run pytest tests/test_screenshot_backfill.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S04: Backfill passes pre-actions and skip selectors, counts skips`.
- The orchestrator ticks `docs/todo.md`. `screenshot_backfill.py` is also touched by E14-S05: run it after this one.
