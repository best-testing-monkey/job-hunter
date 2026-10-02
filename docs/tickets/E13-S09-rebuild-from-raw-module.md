# E13-S09 — Rebuild job markdown from saved raw pages (no network)

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

A function that re-runs each adapter's `parse_detail` over the raw pages already saved in `scraper/raw/<site>/` and rewrites the matching `scraper/jobs/<stem>.md` (and the `scraper.db` row), so description/URL changes apply to existing jobs without a re-scrape.

## Context

- Raw pages: `raw/<site_id>/<stem>.html|json`, written during scrapes by `job_scraper/core/raw_export.py` (`filename_for(posting, ext)`; `<stem>` = `<site_id>-<listing_id>-<slugify(title)>`, identical to the markdown filename stem from `core/markdown_export.py`). 20 sites, ~1078 files currently.
- `adapter.parse_detail(stub, page)` needs a `ListingStub(listing_id, detail_url, title)`; rebuild reconstructs it from the `jobs` table in `scraper.db`: columns `site_id, listing_id, source_url, title, last_seen_at, duplicate_of` (`job_scraper/core/db.py`, `JobRepository.conn` is a plain `sqlite3` connection; `JobRepository.upsert(posting, seen_at)` returns bool).
- Sites that CANNOT be rebuilt from raw because `parse_detail` reads a dict cached by `list_postings` from the listing API response (which is not saved in raw/): `working_nomads` (`_job_cache`) and `tender_link` (`_vacancy_cache`). They need a re-scrape (E13-S35 covers it). `rebuild` must refuse them with a clear message.
- Pipeline rules to mirror (see `job_scraper/pipeline.py` `run_site` and `job_scraper/core/filters.py` `is_excluded`): excluded postings get no markdown; duplicates (`duplicate_of` not null) get no markdown.
- URL note: most adapters set `source_url=stub.detail_url`, so rebuild reproduces the URL stored in the DB. Stories E13-S13..S19 make `parse_detail` derive the true human URL from the page itself where the page carries it, which is what lets rebuild repair URLs offline.

## Files to create/modify

- `scraper/job_scraper/core/rebuild.py` (new): `NOT_REBUILDABLE: dict[str, str]` (site_id -> reason, keys `working_nomads`, `tender_link`) and `def rebuild_site(site_id: str, repo: JobRepository, jobs_dir: str, raw_dir: str) -> dict[str, int]`.
- `scraper/tests/test_rebuild.py` (new).

## Acceptance criteria

`rebuild_site(...)` behavior (each bullet has a test, using `tmp_path` DB/jobs/raw dirs and the `pro_act` adapter with fixture `tests/fixtures/pro_act/detail_8887.html`; never the network):
- Raises `ValueError` (message mentions the reason) for a site in `NOT_REBUILDABLE`, and for a `site_id` not in `SITE_REGISTRY`.
- For every file in `raw_dir/site_id/` (`.html` or `.json`): look up the DB row whose `f"{site_id}-{listing_id}-{slugify(title)}"` equals the file's stem; no row -> count `skipped_no_db`.
- Build `ListingStub(listing_id=row.listing_id, detail_url=row.source_url, title=row.title)`, call `adapter.parse_detail(stub, path.read_bytes())`. An exception from `parse_detail` is caught, printed to stderr with the file name, counted in `errors`, and does not stop the run.
- If `is_excluded(posting)` -> count `excluded`, write nothing. If the row has `duplicate_of` not null -> count `skipped_duplicate`, write nothing.
- Otherwise `repo.upsert(posting, seen_at=row.last_seen_at)` (keep the original last-seen time) and `markdown_export.write(posting, jobs_dir)` (overwrites the existing file), count `rebuilt`.
- Returns a dict with exactly the keys `rebuilt`, `skipped_no_db`, `skipped_duplicate`, `excluded`, `errors` (all ints).
- Test: seed DB + old markdown with description `"OLD"`, write the fixture bytes as the raw file with the right stem, run `rebuild_site`: `rebuilt == 1`, the markdown now contains the fixture's real description text and not `"OLD"`, and the DB row's `description` matches too.
- `uv run pytest tests/test_rebuild.py` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S09: Add rebuild-from-raw module`.
- `docs/todo.md` item for E13-S09 checked off, committed in the JOB-HUNTER repo (`Mark E13-S09 as done in todo`).
