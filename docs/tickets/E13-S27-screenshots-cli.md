# E13-S27 — `screenshots` CLI subcommand

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Expose the backfill as `uv run python -m job_scraper screenshots --site <id|all> [--missing-only]`.

## Context

- Depends on E13-S26 (`backfill_screenshots`), E13-S22 (`browser_available`), E13-S25.
- `scraper/job_scraper/cli.py`: subparsers `scrape`, `list-sites`, `rebuild` (E13-S10); options named `--site` (repeatable, `all` = `sorted(SITE_REGISTRY.keys())`), `--jobs-dir` (default `jobs/`), `--screenshots-dir` (default `screenshots/`, from S25). `tests/test_cli.py` exists (S10/S25).
- `cli.py` is also edited by E13-S10 and E13-S25 — sequential.

## Files to create/modify

- `scraper/job_scraper/cli.py`
- `scraper/tests/test_cli.py`
- `scraper/README.md` — usage block for `screenshots` and one line: screenshots are taken at scrape time by default; this command back-fills existing jobs (`--missing-only` skips ones that already have a PNG).

## Acceptance criteria

- `screenshots --site pro_act --missing-only` calls `backfill_screenshots("pro_act", "jobs/", "screenshots/", missing_only=True)` and prints `pro_act: {"attempted": ..., ...}` (JSON, same style as `scrape`); without `--missing-only` it passes `missing_only=False`.
- `screenshots --site all` runs every site in sorted order (sites without a selector just report `skipped_no_selector`).
- `screenshots` without `--site` prints an error to stderr and exits 1; an unknown site id prints the `ValueError` message to stderr and exits 1.
- If `browser_available()` is False, prints `No Playwright Chromium found; see README "Screenshots (browser requirements)"` to stderr and exits 1 without calling `backfill_screenshots`.
- Tests patch `job_scraper.cli.backfill_screenshots` and `job_scraper.cli.browser_available` (cover each bullet above).
- `uv run python -m job_scraper screenshots --help` lists `--site`, `--missing-only`, `--jobs-dir`, `--screenshots-dir`.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S27: Add screenshots backfill CLI command`.
- `docs/todo.md` item for E13-S27 checked off, committed in the JOB-HUNTER repo (`Mark E13-S27 as done in todo`).
