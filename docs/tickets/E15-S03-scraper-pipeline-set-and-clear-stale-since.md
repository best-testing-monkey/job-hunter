# E15-S03 — Pipeline: write the Stale since bullet when a posting goes stale, remove it when it returns

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` for conventions (Epic 15 scraper stories follow B exactly as Epic 13 did: `scraper/` is the owner's separate repo, commit there) — do not repeat them here. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

`run_site` detects postings that just went stale and writes `- Stale since: <today>` into their markdown (once: the date is never reset by later runs), and removes the bullet again when a stale posting is seen live.

## Context

- Needs E15-S01 (`set_stale_line`, `md_path_for`, `write(..., stale_since=)`) and E15-S02 (`list_newly_stale`, `mark_stale_not_seen_since(..., stale_on=)`).
- `scraper/job_scraper/pipeline.py` `run_site(adapter, repo, jobs_dir, run_started_at, raw_dir=None, screenshots_dir=None, counters=None)`: per posting: exclude -> `apply_dedup` -> `repo.upsert` -> duplicate branch / "rewrite" branch (`changed`, and after Epic 14 also "Source line differs", which captures a screenshot and calls `write(posting, jobs_dir, screenshot=screenshot)`) / otherwise nothing is written. After the loop: `stale_count = repo.mark_stale_not_seen_since(adapter.site_id, run_started_at)`; `counters["stale_marked"] = stale_count`.
- A posting whose content changed is rewritten from scratch by `write`, which emits no stale bullet: that is correct (`upsert` already cleared `is_stale`/`stale_since`).
- Date format: local date `YYYY-MM-DD` (`datetime.now().date().isoformat()`); the app compares with its own local date.
- Tests: `scraper/tests/test_pipeline.py` (`FakeAdapter`, `_run_shots` helper, real `JobRepository` on `tmp_path`).

## Files to create/modify

- `scraper/job_scraper/pipeline.py`
- `scraper/tests/test_pipeline.py`

## Acceptance criteria

- `run_site(..., today: str | None = None)`: `today` defaults to `datetime.now().date().isoformat()` and is injectable for tests.
- Before marking: `newly = repo.list_newly_stale(adapter.site_id, run_started_at)`; then `repo.mark_stale_not_seen_since(adapter.site_id, run_started_at, stale_on=today)`; then for each `(listing_id, title)` in `newly`: `set_stale_line(str(md_path_for(jobs_dir, adapter.site_id, listing_id, title)), today)` (a missing file is silently skipped by that helper). New counter `"newly_stale": len(newly)` (add to the counters dict and docstring); `stale_marked` keeps its meaning.
- In the loop, for a non-duplicate, non-excluded posting whose markdown is NOT rewritten (unchanged content and, if present, unchanged Source line): call `set_stale_line(<md path>, None)` so a posting that came back live loses its bullet. A rewritten posting needs no extra call.
- Never resets a date: running `run_site` twice with the posting still unlisted keeps the first date in the markdown and `newly_stale == 0` the second time.
- Tests (real repo + fake adapter whose `list_postings` yields a controllable list): (1) run 1 lists A and B, run 2 lists only A with `today="2026-10-05"` -> B's markdown contains exactly one `- Stale since: 2026-10-05`, A's has none, `newly_stale == 1`; (2) run 3 (still only A) with `today="2026-10-08"` -> B still says `2026-10-05`, `newly_stale == 0`; (3) run 4 lists A and B again (B unchanged) -> B's markdown has no `Stale since` line and the DB row has `is_stale == 0`; (4) B returns with changed content -> markdown rewritten without the bullet; (5) a duplicate-flagged posting never gets a bullet or a file. Existing pipeline tests pass (adjust any whole-dict counter equality for `newly_stale`).

## Definition of done

- Run only `uv run pytest tests/test_pipeline.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E15-S03: Pipeline marks and clears Stale since in markdown`.
- The orchestrator ticks `docs/todo.md`. `pipeline.py` was also edited by E14-S03/S06/S07 (finished earlier): never run two scraper stories at once.
