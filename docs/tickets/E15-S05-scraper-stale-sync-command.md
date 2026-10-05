# E15-S05 — `stale-sync` command: backfill and repair Stale since bullets from scraper.db

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` for conventions (Epic 15 scraper stories follow B exactly as Epic 13 did: `scraper/` is the owner's separate repo, commit there) — do not repeat them here. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

A one-off (re-runnable) `python -m job_scraper stale-sync` command that brings every markdown file in line with `scraper.db`: stale rows get `- Stale since:`, live rows lose it.

## Context

- Needs E15-S01 (`set_stale_line`, `md_path_for`) and E15-S02 (`list_stale_state`, `set_stale_since`).
- `scraper.db` today holds about 450 rows with `is_stale = 1` but NO marking date (column added by E15-S02 is NULL for them). Decision (no date is stored anywhere; `last_seen_at` is only a lower bound and would hide old postings immediately): rows that are stale without a date are dated TODAY, so they stay visible in the app for the 2-day window and then disappear. That date is stored in the DB so later runs never move it.
- `scraper/job_scraper/cli.py`: subparsers `scrape`, `rebuild`, `screenshots`, `list-sites`; `main()` dispatches on `args.command`; `rebuild` has `--db` (default `scraper.db`) and `--jobs-dir` (default `jobs/`) — copy those option definitions. Test style: `scraper/tests/test_cli.py` (`temp_db` fixture, `monkeypatch.setattr(sys, "argv", ...)`, `capsys`).
- Duplicate rows (`duplicate_of` not null) have no markdown file and are excluded by `list_stale_state`.

## Files to create/modify

- `scraper/job_scraper/core/stale_sync.py` (new)
- `scraper/job_scraper/cli.py`
- `scraper/tests/test_stale_sync.py` (new)
- `scraper/tests/test_cli.py`
- `scraper/README.md`

## Acceptance criteria

- `sync_stale_markers(repo: JobRepository, jobs_dir: str, today: str) -> dict[str, int]`: for each row of `repo.list_stale_state()`: if `is_stale == 1` and `stale_since` is NULL -> `repo.set_stale_since(site_id, listing_id, today)` (counter `dated`); then for `is_stale == 1`: `set_stale_line(md, stale_since)` (counter `written` when it returns True); for `is_stale == 0`: `set_stale_line(md, None)` (counter `cleared` when True); if the markdown file does not exist: counter `missing_md` (nothing else). Returns `{"stale_rows", "dated", "written", "cleared", "missing_md"}` (all ints; `stale_rows` = rows with `is_stale == 1`). Idempotent: a second call with a different `today` returns `dated == 0`, `written == 0`, `cleared == 0` and keeps the first date.
- CLI: `stale-sync [--db scraper.db] [--jobs-dir jobs/]`; prints `json.dumps(counters)` (one line); uses `datetime.now().date().isoformat()` as `today`. Never touches the network, `raw/` or `screenshots/`.
- `scraper/README.md`: a short "Stale postings" paragraph (3-5 lines) under the CLI usage: the markdown bullet `- Stale since: YYYY-MM-DD` is written by `scrape` when a posting disappears and removed when it returns; `stale-sync` repairs/backfills it from `scraper.db`; undated stale rows are dated with the day the command runs; the app hides a stale posting 3 days after that date.
- Tests: `test_stale_sync.py` with a real `JobRepository` in `tmp_path` and markdown files written via `markdown_export.write`: stale undated row -> dated today and bullet written; stale dated row keeps its date; live row with a leftover bullet -> removed; missing md -> `missing_md`; duplicate row ignored; idempotence as above. `test_cli.py`: `stale-sync --db <tmp> --jobs-dir <tmp>` prints a JSON line whose keys equal the five counter names; `stale-sync --help` exits 0 and mentions `--db` and `--jobs-dir`.

## Definition of done

- Run only `uv run pytest tests/test_stale_sync.py tests/test_cli.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E15-S05: Add stale-sync command`.
- The orchestrator ticks `docs/todo.md`. `cli.py` was also edited by E14-S05/S06: never run two scraper stories at once. Do NOT run the command against the real `scraper.db` in this story.
