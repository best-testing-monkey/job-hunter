# E15-S04 — `rebuild` keeps the stale state and bullet

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` for conventions (Epic 15 scraper stories follow B exactly as Epic 13 did: `scraper/` is the owner's separate repo, commit there) — do not repeat them here. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

`rebuild --site X` (offline regeneration from raw/) must not un-stale postings or drop their `- Stale since:` bullet.

## Context

- Needs E15-S01/S02. Problem found while verifying feasibility: `scraper/job_scraper/core/rebuild.py` `rebuild_site` calls `repo.upsert(posting, seen_at=last_seen_at)`, and `upsert` sets `is_stale = 0` (both update paths; plus `stale_since = NULL` after E15-S02); then `markdown_export.write(posting, jobs_dir)` renders without any stale bullet. So today a rebuild silently revives delisted postings in the DB and the bullet would vanish.
- `rebuild_site` reads rows via `SELECT listing_id, title, source_url, last_seen_at, duplicate_of FROM jobs WHERE site_id = ?` and iterates `raw_dir/<site>/*.html|json`.
- DB helpers from E15-S02: `set_stale_state(site_id, listing_id, is_stale, stale_since)`.
- Tests: `scraper/tests/test_rebuild.py` (see how it builds a repo + raw dir + registers a fake/real adapter).

## Files to create/modify

- `scraper/job_scraper/core/rebuild.py`
- `scraper/tests/test_rebuild.py`

## Acceptance criteria

- The row query also selects `is_stale, stale_since` (carry them through the existing tuple handling). For each rebuilt posting: remember them before `repo.upsert`, and after it call `repo.set_stale_state(site_id, listing_id, is_stale, stale_since)` with the remembered values; then `markdown_export.write(posting, jobs_dir, stale_since=stale_since if is_stale and stale_since else None)`.
- Counters and behaviour for non-stale rows are unchanged.
- Tests: a stale row (`is_stale=1`, `stale_since="2026-10-03"`) rebuilt from raw: DB row still `is_stale == 1` and `stale_since == "2026-10-03"`, markdown contains exactly one `- Stale since: 2026-10-03`; a non-stale row: markdown has no such line and `is_stale == 0`; a stale row with `stale_since IS NULL` (pre-migration data): stays stale, no bullet written, no error. Existing tests pass.

## Definition of done

- Run only `uv run pytest tests/test_rebuild.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E15-S04: Rebuild preserves stale state`.
- The orchestrator ticks `docs/todo.md`.
