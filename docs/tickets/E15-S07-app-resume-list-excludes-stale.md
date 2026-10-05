# E15-S07 — App: the resume list page counts only live matches

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions — do not repeat them here. These are app stories (only `app/` and `docs/`); the app never reads `scraper.db` and never edits `scraper/` or `resume-matcher/`: the single interface is the job markdown. Design of the whole epic: see the `GOAL` block of Epic 15 in `docs/todo.md`.

## Goal

On `/` (the main page) stale and hidden postings are never counted as matches: the `resume-match-data` JSON that drives match counts, "since new match" and the threshold slider contains only live matches.

## Context

- Needs E15-S06 (`jobs.job_stale_state`).
- `app/webapp/routes.py` `resume_list()`: for each resume `matches = db.get_matches(conn, resume["id"])` and `resume_match_data[resume["id"]] = [{"score": ..., "status": ..., "job_posted": ...} for m in matches]`, rendered into `<script type="application/json" id="resume-match-data">` by `app/webapp/templates/resumes.html` (its inline JS `computeResumeStats` counts `status === "New" && score >= threshold`). The template needs no change.
- A match row has `job_file` (absolute path of the markdown). Rows whose file is missing count as live (`job_stale_state` returns `'live'`).
- Decision: stale AND hidden are both excluded here (the main page shows only live matches); a stale posting that the user had marked Applied is excluded too (it was never counted as a match anyway, since only `New` counts).
- Tests: `app/tests/test_routes.py`, see `test_resume_list_with_matches_includes_match_data` (~line 625) for setup.

## Files to create/modify

- `app/webapp/routes.py`
- `app/tests/test_routes.py`

## Acceptance criteria

- In `resume_list`, a match is included in `resume_match_data` only if `jobs.job_stale_state(m["job_file"])[0] == "live"`.
- Test: one resume, four job markdown files in `tmp_path` written with `- Stale since:` dates computed from `date.today()`: none (live), today minus 1 day, today minus 2 days, today minus 3 days, each with a match row (status `New`, score 0.9). `GET /` returns 200 and the JSON parsed from the `id="resume-match-data"` script (regex `<script type="application/json" id="resume-match-data">(.*?)</script>`, `json.loads`) has exactly 1 entry for that resume. A second test: a match whose `job_file` does not exist is still counted (1 entry). Existing tests pass.

## Definition of done

- Run only `uv run pytest tests/test_routes.py -q` from `app/`.
- Committed in the JOB-HUNTER repo as `E15-S07: Resume list counts only live matches`.
- The orchestrator ticks `docs/todo.md`. `routes.py`/`test_routes.py` are also edited by E15-S08 and S09: run in order.
