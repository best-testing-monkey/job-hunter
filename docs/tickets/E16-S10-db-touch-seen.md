# E16-S10 — `JobRepository.touch_seen` (safety valve for suspicious "gone" waves)

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

A repository method that refreshes `last_seen_at` for given postings without changing anything else, so the pipeline can refuse to stale a mass of postings when a site starts answering 404 to everything (outage, block page).

## Context

- `scraper/job_scraper/core/db.py`: `JobRepository` (`self.conn`), `upsert` sets `last_seen_at`, `mark_stale_not_seen_since(site_id, run_started_at, stale_on)` marks rows whose `last_seen_at < run_started_at`, `list_newly_stale`, `set_stale_state`.
- Design (verified): a posting whose detail fetch raises `PostingGone` is simply NOT upserted this run, so the existing end-of-run `list_newly_stale` + `mark_stale_not_seen_since(..., stale_on=today)` + `set_stale_line` machinery (E15-S03) marks it stale with today's date and never changes an existing `stale_since`. No new stale-marking code is needed; only the safety valve below.
- Tests: `scraper/tests/test_db.py` (build a repo on `tmp_path / "t.db"`; see how existing tests upsert a `JobPosting`).

## Files to create/modify

- `scraper/job_scraper/core/db.py`
- `scraper/tests/test_db.py`

## Acceptance criteria

- `touch_seen(self, site_id: str, listing_ids: Sequence[str], seen_at: str) -> int`: `UPDATE jobs SET last_seen_at = ? WHERE site_id = ? AND listing_id = ?` for each id (executemany, one commit), returns the number of rows updated; it never changes `is_stale`, `stale_since` or any content column; an empty list returns 0 without touching the DB.
- Tests: two upserted rows, `touch_seen` for one with a later timestamp updates only that row's `last_seen_at`; an already-stale row stays stale with its `stale_since`; unknown ids give 0; empty list gives 0; after `touch_seen` with a timestamp >= run start, `list_newly_stale` no longer lists that row.

## Definition of done

- Run only `uv run pytest tests/test_db.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S10: Add JobRepository.touch_seen`.
- The orchestrator ticks `docs/todo.md`. Independent of S08/S09; E16-S11 needs it.
