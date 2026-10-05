# E15-S03b — Stop postings being flagged as duplicates of themselves; repair existing rows

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` for conventions. (Added during the Epic 15 run: E15-S03 found that a re-seen posting matched its own row in `find_duplicate`; a read-only query of the owner's real `scraper/scraper.db` shows 725 rows with `duplicate_of IS NOT NULL`, of which 703 have `duplicate_of = id` — self-duplicates. Duplicates are skipped by the pipeline, so those postings never had their markdown/URL/screenshot refreshed on re-scrapes. Only ~22 are real cross-site duplicates.)

## Goal

`find_duplicate` must never return the posting's own row, and existing self-referencing rows must be repaired automatically.

## Context

- `scraper/job_scraper/core/db.py`: `JobRepository` (migrations run in `__init__`, see how E15-S02 added `stale_since`, commit fdd1134), `find_duplicate(...)`, `upsert(...)`, `duplicate_of` column (`INTEGER REFERENCES jobs(id)`), `UNIQUE(site_id, listing_id)`.
- `scraper/job_scraper/pipeline.py` `run_site`: E15-S03 (commit 8d411cf) added a guard that ignores a duplicate match against the posting's own row — read that diff; it becomes redundant once the root cause is fixed.
- Tests: `scraper/tests/test_db.py`, `scraper/tests/test_pipeline.py`.
- Real data (git-ignored, NEVER write to it): `scraper/scraper.db`. Prove the repair on a COPY made in the session scratchpad.

## Files to create/modify

- `scraper/job_scraper/core/db.py`
- `scraper/job_scraper/pipeline.py` (remove the E15-S03 guard only if it is now redundant and tests still prove the behavior)
- `scraper/tests/test_db.py`, `scraper/tests/test_pipeline.py`

## Acceptance criteria

- `find_duplicate(posting)` excludes the row with the same `(site_id, listing_id)` as the posting: test — upsert posting A; `find_duplicate(A)` returns None; upsert a different posting B (other site, same title/client/description key as A) -> `find_duplicate(B)` returns A's id.
- Migration in `JobRepository.__init__`: `UPDATE jobs SET duplicate_of = NULL WHERE duplicate_of = id`, idempotent (running twice changes nothing the second time). Test on a `tmp_path` DB seeded via raw SQL: 3 self-referencing rows and 1 legitimate duplicate row (points to a different id) -> after opening with `JobRepository`, the 3 self rows have `duplicate_of IS NULL` and the legitimate one is unchanged; reopening changes nothing.
- A re-seen posting is not skipped as a duplicate of itself: pipeline test — run `run_site` twice with the same mocked adapter results; the second run's `duplicates` counter is 0 and `written`/`unchanged` counters behave as before.
- Copy-migration proof (report in the commit body): copy `scraper/scraper.db` to the scratchpad, open the copy with `JobRepository`, report counts before/after of rows with `duplicate_of IS NOT NULL` (expected 725 -> ~22) and total rows unchanged; the real DB's mtime is unchanged (`stat -c %Y scraper/scraper.db` before/after).
- Only the touched test files were run.

## Definition of done

- Committed in the SCRAPER repo as `E15-S03b: Fix self-duplicate detection and repair existing rows`.
- `docs/todo.md` ticked by the orchestrator.
