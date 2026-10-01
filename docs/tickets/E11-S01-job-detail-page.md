# E11-S01 — Job detail page

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

A page showing a job posting's full details (including its description, which no existing code currently extracts), reached by clicking a job from a resume's match table.

## Context

- Depends on E8-S01 (`db.get_match`).
- Read `docs/DESIGN_DOC.md`'s "Job detail page (new)" subsection in full.
- `app/webapp/jobs.py` exists (`parse_job_file`, `site_name_for`, both delegating to `resume-matcher/build_report.py`) — read it first. `build_report.parse_job()` only extracts the metadata bullets (title/source/client/location/posted/workplace), **not** the description body — this story adds description extraction as NEW logic in `app/webapp/jobs.py` itself, it does NOT edit `resume-matcher/build_report.py` (that's a sibling project's file; per this project's standing rule, never edit `scraper/` or `resume-matcher/`).
- Look at a real scraped job file (e.g. `ls ../scraper/jobs/*.md | head -1`, then read it) to see the exact format: a `# Title` line, metadata bullets, then a `## Description` heading followed by the description text, optionally followed by a `## Scrape note` heading.

## Files to create/modify

- `app/webapp/jobs.py` — add `get_job_description(job_file: str | Path) -> str`: read the raw file text, find the `## Description` heading, return everything after it up to (but not including) the next `##` heading or end-of-file, stripped of leading/trailing whitespace. Return `""` if no `## Description` heading is found (don't raise).
- `app/webapp/routes.py` — add `GET /jobs/<int:match_id>`: looks up the match via `db.get_match` (404 if missing), calls `jobs.parse_job_file(match["job_file"])` for title/location/workplace/source and `jobs.get_job_description(match["job_file"])` for the description, renders a new `job_detail.html` template with all of it.
- `app/webapp/templates/job_detail.html` (new, extends `base.html`) — shows title (as `<h1>`), site, location, workplace, the full description text (preserve line breaks — wrap in `<pre>` or replace newlines with `<br>`, your call, `<pre>` is simplest and matches this app's low-ceremony style elsewhere), and a prominent "View original posting" link to `source`.

## Acceptance criteria

- `get_job_description` on a real file from `scraper/jobs/*.md` (glob for any one, same pattern as `test_jobs.py`'s existing test) returns non-empty text that doesn't include the `## Description` heading itself or anything from a following `## Scrape note` section (test against a file you've confirmed has both sections, if one exists in the current scrape — if none do, just confirm the returned text excludes the heading and matches what's between `## Description` and the next `##`/EOF).
- `GET /jobs/<match_id>` for a valid match returns HTTP 200 and the response contains the job's title and at least part of its description text.
- `GET /jobs/999999` returns HTTP 404.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E11-S01: Add job detail page`.
- `docs/todo.md` item for E11-S01 checked off.
