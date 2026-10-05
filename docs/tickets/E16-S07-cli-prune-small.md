# E16-S07 — CLI: `screenshots --prune-small`

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

`python -m job_scraper screenshots --prune-small [--min-height 100] [--site X ...] [--move-to DIR] [--dry-run]` runs the prune module and prints one JSON counter line; it needs no browser.

## Context

- `scraper/job_scraper/cli.py`: the `screenshots` subparser (`--site` dest `sites`, `--missing-only`, `--jobs-dir`, `--screenshots-dir`, `--db`, `--include-stale`); `handle_screenshots(args)` first checks `browser_available()` and then requires `--site`. The prune mode must come BEFORE both checks.
- `prune_small_screenshots(screenshots_dir, jobs_dir, *, min_height, sites, move_to, dry_run)` from E16-S06 (`scraper/job_scraper/core/screenshot_prune.py`).
- Tests: `scraper/tests/test_cli.py` (`test_screenshots_*` patch names in the cli module; copy that style; `main()` reads `sys.argv`, see how existing tests invoke it).

## Files to create/modify

- `scraper/job_scraper/cli.py`
- `scraper/tests/test_cli.py`

## Acceptance criteria

- New `screenshots` options: `--prune-small` (store_true), `--min-height` (int, default 100), `--move-to` (path, default None), `--dry-run` (store_true). Help text of `--move-to`: "folder PNGs are moved into (required unless --dry-run); files are never deleted".
- `handle_screenshots`: when `args.prune_small`: do not call `browser_available`; `--site` is optional (none or `all` means every site, otherwise the given list); if not `--dry-run` and no `--move-to` print "Error: --move-to is required unless --dry-run" to stderr and `sys.exit(1)`; else call `prune_small_screenshots(args.screenshots_dir, args.jobs_dir, min_height=args.min_height, sites=<list or None>, move_to=args.move_to, dry_run=args.dry_run)` and `print(json.dumps(counters))`. Without `--prune-small` the behaviour is unchanged (also `--min-height`/`--move-to`/`--dry-run` are ignored then).
- Tests (patch `prune_small_screenshots` and `browser_available` in the cli module): prune mode with `--dry-run` and no site calls it with `sites=None, dry_run=True, move_to=None`, `browser_available` is not called, stdout is one JSON line; `--site hero --site harveynash --move-to /x --min-height 120` passes `sites=["hero","harveynash"], min_height=120, move_to="/x"`; no `--move-to` and no `--dry-run` exits 1 with the error on stderr and the module is not called; the existing screenshots tests still pass.

## Definition of done

- Run only `uv run pytest tests/test_cli.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S07: Add screenshots --prune-small command`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S06. `cli.py` is not edited by later Epic 16 code stories.
