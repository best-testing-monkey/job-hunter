# E14-S06 — Scrape crash safety: per-site exceptions, incremental counters

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

One site's exception (e.g. headfirst's curl timeout) must not kill `scrape --site all` or lose the counters of the sites already done; each site's counters are printed as soon as the site finishes.

## Context

- QA evidence: `docs/e13-qa-results.md` section 5 and 11 ("one site's curl timeout killed `scrape --site all` and lost all earlier per-site counters").
- `scraper/job_scraper/pipeline.py`: `run_site(adapter, repo, jobs_dir, run_started_at, raw_dir=None, screenshots_dir=None) -> dict` builds a local `counters` dict; `run(site_ids, repo, jobs_dir, ignore_robots=False, raw_dir=None, screenshots_dir=None) -> dict[str, dict]` loops over sites and calls `run_site`.
- `scraper/job_scraper/cli.py` `handle_scrape` calls `run(...)` and only afterwards prints `f"{site_id}: {json.dumps(counters)}"` per site.
- `scraper/tests/test_pipeline.py` (class `FakeAdapter`, `test_run_with_registry_entry` shows how to register a fake adapter), `scraper/tests/test_cli.py` (`test_scrape_*` patch `run` in the cli module with fakes that return a dict).

## Files to create/modify

- `scraper/job_scraper/pipeline.py`
- `scraper/job_scraper/cli.py`
- `scraper/tests/test_pipeline.py`
- `scraper/tests/test_cli.py`

## Acceptance criteria

- `run_site(..., counters: dict | None = None)`: when a dict is passed it is used (filled in place) instead of a fresh one, so the caller still has the partial counts after an exception. Default behaviour and return value unchanged.
- `run(..., on_site_done: Callable[[str, dict], None] | None = None)`: each site's `run_site` call is wrapped in `try/except Exception as exc` (NOT `BaseException`: Ctrl-C still stops the run). On exception: print `Error: site <id> failed: <ExceptionType>: <msg>` to stderr and store `results[site_id] = {**partial_counters, "error": "<ExceptionType>: <msg>"}`; the loop continues with the next site. After every site (success or error) call `on_site_done(site_id, results[site_id])` if given. Robots-skipped and unknown sites behave as before.
- `handle_scrape`: passes `on_site_done` that prints `f"{site_id}: {json.dumps(counters)}"` with `flush=True` immediately; after `run` returns it prints any site in `results` that was not printed yet (keeps tests that patch `run` passing); exits with status 1 (`sys.exit(1)`) if any result has an `"error"` key, 0 otherwise.
- Tests: pipeline — two registered fake adapters, the first raises `RuntimeError("boom")` inside `list_postings`; `run([...])` returns both keys, the first has `"error"` starting with `RuntimeError: boom`, the second has normal counters, and the callback was called twice in order; a partially-processed site keeps its `seen` count in the error dict (adapter yields one stub, then raises on the second fetch). cli — patch `run` to call the callback itself for two sites and assert both lines are in captured stdout in order, once each; a result containing `"error"` makes `main()` raise `SystemExit` with code 1. Existing tests pass unchanged except where they asserted exact output of a patched `run` (adjust only if needed).

## Definition of done

- Run only `uv run pytest tests/test_pipeline.py tests/test_cli.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S06: Scrape survives per-site errors and prints counters incrementally`.
- The orchestrator ticks `docs/todo.md`. Same files as E14-S03/S05: run after them. This is the last story touching `pipeline.py` for this behaviour; E14-S07 edits it again.
