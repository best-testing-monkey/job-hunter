# E14-S05 — Backfill skips postings the scraper already marked stale

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

`screenshots --site X` must not spend 30 s timeouts on delisted postings: skip every job whose `scraper.db` row has `is_stale = 1`.

## Context

- Design choice (made here, no dependency on Epic 15): read `scraper/scraper.db` directly (read-only) instead of waiting for Epic 15's `- Stale since:` bullet. The DB is authoritative and exists today; `jobs.is_stale INTEGER` is set by `JobRepository.mark_stale_not_seen_since` (`scraper/job_scraper/core/db.py`).
- QA evidence: `docs/e13-qa-results.md` section 6/11 — hundreds of 30 s timeouts, about 4.5 h wall, almost all on delisted pages.
- `scraper/job_scraper/core/screenshot_backfill.py` `backfill_screenshots(site_id, jobs_dir, screenshots_dir, missing_only=False, delay=1.0)` iterates `sorted(Path(jobs_dir).glob(f"{site_id}-*.md"))`; stem = `md.stem` = `<site_id>-<listing_id>-<slugify(title)>` (`job_scraper.core.markdown_export.slugify`). Counts keys: `attempted, captured, failed, skipped_existing, skipped_no_selector, skipped_blocked` (E14-S04).
- `scraper/job_scraper/cli.py`: the `screenshots` subparser has `--site`, `--missing-only`, `--jobs-dir`, `--screenshots-dir`; `handle_screenshots` calls `backfill_screenshots(site_id, args.jobs_dir, args.screenshots_dir, missing_only=args.missing_only)`. `scrape`/`rebuild` already use `--db` (default `scraper.db`).
- Tests: `scraper/tests/test_screenshot_backfill.py` (fixture `env`, helper `run`), `scraper/tests/test_cli.py` (`test_screenshots_*` patch `backfill_screenshots` in the cli module).

## Files to create/modify

- `scraper/job_scraper/core/screenshot_backfill.py`
- `scraper/job_scraper/cli.py`
- `scraper/tests/test_screenshot_backfill.py`
- `scraper/tests/test_cli.py`

## Acceptance criteria

- `backfill_screenshots(..., db_path: str | None = None, include_stale: bool = False)`: when `db_path` is given, exists as a file and `include_stale` is False, open it read-only (`sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)`), `SELECT listing_id, title FROM jobs WHERE site_id = ? AND is_stale = 1`, and build the set of stems `f"{site_id}-{listing_id}-{slugify(title)}"`. A job file whose stem is in the set is skipped BEFORE any delay/capture/PNG check: counts key `"skipped_stale"` += 1 (new key, present in every returned dict), the md file is untouched. A missing DB file means nothing is skipped (no error).
- `cli.py`: `screenshots` gets `--db` (default `scraper.db`) and `--include-stale` (store_true, help: "also try postings the scraper marked stale"); `handle_screenshots` passes `db_path=args.db, include_stale=args.include_stale`.
- Tests: update every equality assertion on the counts dict with `"skipped_stale": 0`; new test builds a real sqlite file in `tmp_path` via `JobRepository(str(tmp_path/"s.db"))` + `upsert` + `mark_stale_not_seen_since` (one live row, one stale row whose stem matches an md file), asserts the stale md gets no capture call (`cap.call_count == 1`) and `skipped_stale == 1`; test `include_stale=True` captures both; test missing DB path captures both; cli tests: adjust any `assert_called_with` on `backfill_screenshots` for the two new kwargs and add one test that `--db x.db --include-stale` reaches the call.

## Definition of done

- Run only `uv run pytest tests/test_screenshot_backfill.py tests/test_cli.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S05: Backfill skips postings marked stale in scraper.db`.
- The orchestrator ticks `docs/todo.md`. Same files as E14-S04 (and `cli.py` again in E14-S06): run in order.
