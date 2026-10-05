# E16-S11 — pipeline: a delisted detail page marks the posting stale, with a safety valve

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

`run_site` fetches detail pages with the gone check on; a posting that raises `PostingGone` is not parsed, written or screenshotted, is counted in a new `gone` counter, and ends the run marked stale (today's date, bullet in the markdown) through the existing end-of-run logic. The run continues. Already-stale postings keep their date.

## Context

- `scraper/job_scraper/pipeline.py` `run_site(adapter, repo, jobs_dir, run_started_at, raw_dir, screenshots_dir, today, counters)`: the loop starts with `counters["seen"] += 1; page = fetch_page(adapter.fetch_strategy, stub.detail_url)`. After the loop: `newly = repo.list_newly_stale(...)`, `stale_count = repo.mark_stale_not_seen_since(..., stale_on=today)`, `set_stale_line(md_path_for(...), today)` for each newly stale (only rows with `is_stale = 0`, so an existing `stale_since` is never overwritten), `counters["stale_marked"]`, `counters["newly_stale"]`. `PostingGone` and `SiteAdapter.gone_check(listing_id)` come from E16-S09; `JobRepository.touch_seen` from E16-S10.
- Why no new marking code: a stub that is skipped is not upserted, its `last_seen_at` stays older than `run_started_at`, so the existing code marks it. (A posting not yet in the DB is simply not recorded.)
- Existing tests patch `job_scraper.pipeline.fetch_page` and use a `FakeAdapter(SiteAdapter)`; check `scraper/tests/test_pipeline.py`, `test_integration.py`, `test_cli.py` for assertions that compare the whole counters dict and add the two new keys there (only touched files are run: grep, then run `test_pipeline.py`; if `test_integration.py`/`test_cli.py` compare counters, update them and run them too).

## Files to create/modify

- `scraper/job_scraper/pipeline.py`
- `scraper/tests/test_pipeline.py`

## Acceptance criteria

- The detail fetch becomes `fetch_page(adapter.fetch_strategy, stub.detail_url, gone_check=adapter.gone_check(stub.listing_id))` inside `try/except PostingGone as exc`: on catch increment `counters["gone"]`, remember `stub.listing_id` in a local list `gone_ids`, print `Notice: <site_id> <listing_id> is gone (<exc.reason>)` to stderr and `continue` (no raw write, no parse, no upsert, no markdown, no screenshot). Any other exception behaves as before.
- Counters initialised in `run_site`: `"gone": 0`, `"gone_suppressed": 0`.
- Safety valve, evaluated after the loop and BEFORE `list_newly_stale`: if `len(gone_ids) >= 10` and `len(gone_ids) * 2 > counters["seen"]` (a site-wide 404/redirect wave is far more likely an outage or a block than 10+ real delistings) then print a Warning to stderr, call `repo.touch_seen(adapter.site_id, gone_ids, run_started_at)` so they are NOT staled, and set `counters["gone_suppressed"] = len(gone_ids)`. `counters["gone"]` keeps the detection count either way.
- Tests with a `FakeAdapter` yielding stubs and a patched `fetch_page` whose side effect raises `PostingGone` for chosen URLs and returns bytes for others: (a) a live-in-DB posting that raises PostingGone ends with `is_stale == 1`, `stale_since == today`, the markdown contains `- Stale since: <today>`, `counters["gone"] == 1`, `newly_stale == 1`, and `written` counts only the other postings; the gone posting is not re-written and its `parse_detail` is never called (count calls); (b) a posting already stale since an older date that raises PostingGone keeps that older date in DB and markdown and is not in `newly_stale`; (c) a PostingGone posting not in the DB creates no row; (d) the fetch is called with a `gone_check` that equals `GoneCheck(stub.listing_id, FakeAdapter.listing_paths, FakeAdapter.gone_markers)`; (e) valve: 10 stubs all gone -> `gone == 10`, `gone_suppressed == 10`, no row stale; 3 of 10 gone -> normal marking, `gone_suppressed == 0`; (f) a normal run's counters contain `gone == 0` and unchanged other values.

## Definition of done

- Run only `uv run pytest tests/test_pipeline.py -q` from `scraper/` (plus `tests/test_integration.py tests/test_cli.py` only if you had to update them).
- Committed in the SCRAPER repo as `E16-S11: Mark delisted postings stale from the detail fetch`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S04, E16-S09, E16-S10 (`pipeline.py` chain S04 -> S11 -> S13).
