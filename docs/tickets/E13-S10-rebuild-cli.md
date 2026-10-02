# E13-S10 — `rebuild` CLI subcommand

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Expose `rebuild_site` as `uv run python -m job_scraper rebuild --site <id|all>`.

## Context

- Depends on E13-S09 (`job_scraper/core/rebuild.py`: `rebuild_site`, `NOT_REBUILDABLE`).
- `scraper/job_scraper/cli.py` has `main()` (argparse subparsers `scrape`, `list-sites`), `handle_scrape`, `handle_list_sites`; the `scrape` parser has `--site` (repeatable, `all` means every site via `sorted(SITE_REGISTRY.keys())`), `--db` (default `scraper.db`), `--jobs-dir` (default `jobs/`), `--raw-dir` (default `raw/`). Mirror those option names/defaults for `rebuild`.
- No `tests/test_cli.py` exists yet; this story creates it (call `main()` with `monkeypatch.setattr(sys, "argv", [...])` and patch `job_scraper.cli.rebuild_site`).
- `cli.py` is also edited by E13-S25 and E13-S27 — never in parallel with them.

## Files to create/modify

- `scraper/job_scraper/cli.py`
- `scraper/tests/test_cli.py` (new)
- `scraper/README.md` — add a short "Rebuild markdown from raw pages" usage block under `## Usage`, and a one-line note that `working_nomads` and `tender_link` cannot be rebuilt (re-scrape instead).

## Acceptance criteria

- `uv run python -m job_scraper rebuild --help` (no network) lists `--site`, `--db`, `--jobs-dir`, `--raw-dir`.
- Test: `rebuild --site pro_act` calls `rebuild_site("pro_act", <JobRepository>, "jobs/", "raw/")` once and prints one line `pro_act: {"rebuilt": ..., ...}` (JSON, same style as `handle_scrape`).
- Test: `rebuild --site all` calls `rebuild_site` once per site in `sorted(SITE_REGISTRY)` EXCEPT those in `NOT_REBUILDABLE`, which are skipped with a line on stderr (`Skipping working_nomads: <reason>`); the exit code is 0.
- Test: `rebuild --site working_nomads` explicitly: prints the reason to stderr and exits with code 1.
- Test: `rebuild` without `--site` prints an error to stderr and exits 1 (same behavior as `scrape`).
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S10: Add rebuild CLI subcommand`.
- `docs/todo.md` item for E13-S10 checked off, committed in the JOB-HUNTER repo (`Mark E13-S10 as done in todo`).
