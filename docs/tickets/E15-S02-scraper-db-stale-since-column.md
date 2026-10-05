# E15-S02 — scraper.db: `stale_since` column and stale-transition queries

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` for conventions (Epic 15 scraper stories follow B exactly as Epic 13 did: `scraper/` is the owner's separate repo, commit there) — do not repeat them here. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

The scraper DB remembers WHEN a posting first went stale (a date), clears it when the posting is seen live again, and can list rows that are newly stale.

## Context

- `scraper/job_scraper/core/db.py` `JobRepository`: table `jobs` has `is_stale INTEGER NOT NULL DEFAULT 0` but NO date (verified: nothing stores the marking date; `last_seen_at` is only a lower bound). `upsert(posting, seen_at)` has two UPDATE statements (hash changed: sets `is_stale = 0`; unchanged: `UPDATE jobs SET last_seen_at = ?, is_stale = 0 WHERE id = ?`). `mark_stale_not_seen_since(site_id, run_started_at) -> int` sets `is_stale = 1` for every row of the site with `last_seen_at < run_started_at` (re-marks already-stale rows every run, returns that rowcount — keep that return semantic, a pipeline counter and existing tests depend on it).
- Existing databases (`scraper/scraper.db`) were created without the column, so the constructor must migrate: `CREATE TABLE IF NOT EXISTS` alone is not enough.
- Test file: `scraper/tests/test_db.py`.

## Files to create/modify

- `scraper/job_scraper/core/db.py`
- `scraper/tests/test_db.py`

## Acceptance criteria

- New column `stale_since TEXT` (ISO date string or NULL) in the `CREATE TABLE` statement AND an idempotent migration run in `__init__` (`PRAGMA table_info(jobs)`; if `stale_since` is missing, `ALTER TABLE jobs ADD COLUMN stale_since TEXT`). Test: create a DB with the OLD schema (raw sqlite3, no column, one row), open it with `JobRepository`, assert the column exists and the row is intact; opening twice does not fail.
- Both `upsert` UPDATE paths also set `stale_since = NULL` (they already set `is_stale = 0`). Test: stale row (`is_stale=1`, `stale_since='2026-10-01'`) is upserted again with identical content -> `is_stale == 0` and `stale_since IS NULL`; same with changed content.
- `mark_stale_not_seen_since(site_id, run_started_at, stale_on: str | None = None) -> int`: unchanged return value; when `stale_on` is given it also sets `stale_since = COALESCE(stale_since, stale_on)` on the rows it marks (an existing date is NEVER overwritten, so repeated runs keep the original date). Tests: first call dates the row, second call with a later `stale_on` keeps the first date, `stale_on=None` leaves `stale_since` NULL.
- `list_newly_stale(site_id, run_started_at) -> list[tuple[str, str]]`: `(listing_id, title)` of rows of that site with `is_stale = 0`, `last_seen_at < run_started_at` and `duplicate_of IS NULL`. Test: a live-seen row, an already-stale row and a duplicate row are NOT returned; an unseen live row is.
- `list_stale_state() -> list[tuple[str, str, str, int, str | None]]`: `(site_id, listing_id, title, is_stale, stale_since)` for every row with `duplicate_of IS NULL`, ordered by `site_id, listing_id`.
- `set_stale_state(site_id, listing_id, is_stale: int, stale_since: str | None) -> None` and `set_stale_since(site_id, listing_id, stale_since: str | None) -> None` (plain UPDATEs + commit). Test each once.
- All existing tests in `tests/test_db.py` pass.

## Definition of done

- Run only `uv run pytest tests/test_db.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E15-S02: Track stale_since in scraper.db`.
- The orchestrator ticks `docs/todo.md`.
