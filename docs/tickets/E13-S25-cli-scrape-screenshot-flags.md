# E13-S25 — CLI `scrape` screenshot flags and gitignore

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Turn screenshot capture on by default in `scrape`, configurable and skippable, and keep the generated PNGs out of git.

## Context

- Depends on E13-S24 (`run(..., screenshots_dir=...)`) and E13-S10 (creates `tests/test_cli.py`).
- `scraper/job_scraper/cli.py` `handle_scrape(args)` calls `run(site_ids, repo, args.jobs_dir, ignore_robots=args.ignore_robots, raw_dir=raw_dir)` with `raw_dir = None if args.no_raw else args.raw_dir`; the `scrape` parser already has `--raw-dir` (default `raw/`) and `--no-raw`. Mirror that pair.
- `scraper/.gitignore` has a `# Generated output` block listing `jobs/`, `raw/`, `scraper.db`.
- `cli.py` is also edited by E13-S10 and E13-S27 — sequential.

## Files to create/modify

- `scraper/job_scraper/cli.py`
- `scraper/.gitignore`
- `scraper/tests/test_cli.py`

## Acceptance criteria

- `scrape` accepts `--screenshots-dir` (default `screenshots/`) and `--no-screenshots` (flag, skips screenshots); `handle_scrape` passes `screenshots_dir=None if args.no_screenshots else args.screenshots_dir` to `run`.
- `.gitignore` contains the line `screenshots/` in the generated-output block; `git -C scraper check-ignore screenshots/x.png` prints the path.
- Tests (patch `job_scraper.cli.run`): `scrape --site pro_act` -> `run` called with `screenshots_dir="screenshots/"`; `scrape --site pro_act --screenshots-dir /tmp/s` -> `"/tmp/s"`; `scrape --site pro_act --no-screenshots` -> `None`. Existing `--raw-dir/--no-raw` behavior untouched.
- `uv run python -m job_scraper scrape --help` shows both new options.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S25: Add scrape screenshot flags and gitignore screenshots`.
- `docs/todo.md` item for E13-S25 checked off, committed in the JOB-HUNTER repo (`Mark E13-S25 as done in todo`).
