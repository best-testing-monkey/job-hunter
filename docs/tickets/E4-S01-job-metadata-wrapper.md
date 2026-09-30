# E4-S01 — Job metadata wrapper reusing build_report.py

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Provide a thin wrapper that imports and reuses `resume-matcher/build_report.py`'s existing job-parsing functions, so this app never re-implements scraped-job markdown parsing.

## Context

- Depends on E1-S01 only — independent of E2/E3/E5, can be built in parallel with those.
- `resume-matcher/build_report.py` (sibling repo, **do not edit it**) defines:
  - `parse_job(path: Path) -> dict` — returns a dict with keys `title`, `source`, `client`, `location`, `posted`, `workplace` (workplace is one of `"Fully Remote"`/`"Hybrid"`/`"On-site"`/`""`).
  - `site_name(job_file: str) -> str` — derives a readable site name from the job file's slug prefix (e.g. `"djinni-850338-....md"` → `"Djinni"`).
- `resume-matcher` is a sibling directory to `app/`, not an installed Python package — import it via a `sys.path` insertion, not `pip install -e`.
- Real job files to test against already exist at `scraper/jobs/*.md` (1000+ files) — glob for any one of them in the test, don't hardcode a specific filename that might get deleted/renamed by a future scrape.

## Files to create

- `app/webapp/jobs.py` (new)
- `app/tests/test_jobs.py` (new)

## Implementation notes

In `jobs.py`, resolve the path to `resume-matcher/` relative to this file's own location and insert it into `sys.path` before importing:

```python
import sys
from pathlib import Path

_RESUME_MATCHER_DIR = Path(__file__).resolve().parents[2] / "resume-matcher"
sys.path.insert(0, str(_RESUME_MATCHER_DIR))
import build_report  # noqa: E402
```

(`parents[2]` from `app/webapp/jobs.py` is the `job-hunter` repo root — verify this resolves correctly; if the nesting doesn't match, fix the index, don't hardcode an absolute path.)

## Functions to add to `jobs.py`

- `parse_job_file(path: str | Path) -> dict` — delegates to `build_report.parse_job(Path(path))`.
- `site_name_for(job_file: str) -> str` — delegates to `build_report.site_name(job_file)`.

## Acceptance criteria

- Test globs `scraper/jobs/*.md` (path relative to the repo root — resolve via the same `parents[2]` pattern), takes the first match, calls `parse_job_file` on it, and asserts the returned dict has a non-empty `title` key.
- Test calls `site_name_for` on that same file's name and asserts the result is a non-empty string.
- `uv run pytest tests/ -q` (from `app/`) passes.
- No parsing logic from `build_report.py` is copied or reimplemented in `jobs.py` — it only imports and delegates.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E4-S01: Add job metadata wrapper reusing build_report.py`.
- `docs/todo.md` item for E4-S01 checked off.
