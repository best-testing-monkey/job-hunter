# E15-S06 — App: read `Stale since` from a job file, `stale_state` helper

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions — do not repeat them here. These are app stories (only `app/` and `docs/`); the app never reads `scraper.db` and never edits `scraper/` or `resume-matcher/`: the single interface is the job markdown. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

Pure helpers in `webapp/jobs.py` that turn a job markdown file into `('live' | 'stale' | 'hidden', stale_since)`, with an injectable `today`.

## Context

- `app/webapp/jobs.py`: `parse_job_file(path)` returns `build_report.parse_job(Path(path))` (a dict with `title, source, client, location, posted, workplace`); `build_report` lives in `resume-matcher/build_report.py` which this app must NOT edit, so the date is read here, in `jobs.py`, with its own regex. Other helpers there: `get_job_description`, `screenshot_path_for`.
- The scraper (E15-S01/S03) writes `- Stale since: YYYY-MM-DD` (local date) as a header bullet, between the `# Title` line and `## Description`.
- Tests: `app/tests/test_jobs.py` (existing `test_parse_job_file_and_site_name` reads real files under `scraper/jobs/`; keep it green; new tests use `tmp_path`).
- Boundary (defined precisely here, used by every later story): let `days = (today - stale_since).days`. `days <= 2` (including 0, 1, 2 and any future date) -> `'stale'`; `days >= 3` (strictly more than 2 full days) -> `'hidden'`; no date -> `'live'`.

## Files to create/modify

- `app/webapp/jobs.py`
- `app/tests/test_jobs.py`

## Acceptance criteria

- `STALE_VISIBLE_DAYS = 2` module constant.
- `read_stale_since(path: str | Path) -> date | None`: reads only the header (lines before the first line starting with `## `), finds the first line matching `^- Stale since:\s*(\d{4}-\d{2}-\d{2})\s*$`, returns `datetime.date`; returns None if there is no such line, the date is invalid (e.g. `2026-13-45`), or the file cannot be read (`OSError`). A matching line below `## Description` is ignored.
- `parse_job_file(path)` returns the same dict plus key `"stale_since"` (`date | None`, from `read_stale_since`). Existing keys unchanged.
- `stale_state(stale_since: date | None, today: date | None = None) -> str` per the boundary above; `today` defaults to `date.today()`.
- `job_stale_state(job_file: str | Path, today: date | None = None) -> tuple[str, date | None]`: `(stale_state(read_stale_since(job_file), today), read_stale_since(job_file))`; a missing/unreadable file gives `('live', None)` (existing matches with missing files must keep working).
- Tests: `stale_state` for `today = date(2026, 10, 10)` and since = 10-10 (0 days), 10-09, 10-08 -> `'stale'`; 10-07 (3 days) -> `'hidden'`; 10-01 -> `'hidden'`; 10-11 (future) -> `'stale'`; None -> `'live'`. `read_stale_since`: valid bullet, absent, invalid date, bullet after `## Description` ignored, missing file. `parse_job_file` on a tmp file has `stale_since == date(2026, 10, 8)` and still has `title`. `job_stale_state` on a missing path -> `('live', None)`.

## Definition of done

- Run only `uv run pytest tests/test_jobs.py -q` from `app/` (a separate gate agent runs the full suite).
- Committed in the JOB-HUNTER repo as `E15-S06: Read Stale since and add stale_state helper`.
- The orchestrator ticks `docs/todo.md`.
