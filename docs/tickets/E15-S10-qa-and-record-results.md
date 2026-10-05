# E15-S10 — Epic 15 QA: drive the real app with stale fixtures, record results

See `APPENDIX-A-standards.md` (app) and `APPENDIX-C-screenshot-fix-standards.md` (live-run safety rules apply to anything touching real data). No network is used. Commit goes to the JOB-HUNTER repo.

## Goal

Prove end to end that stale and hidden postings behave as designed in the running app and that the scraper side writes and repairs the markdown bullet.

## Context

- Needs E15-S01..S09 done and the full-suite gate after S09 green.
- The app factory `webapp.create_app()` stores its DB in `app/instance/matches.db` (the OWNER'S data) — never use that file. Instead start an own instance on port 5001 from `app/` with `uv run python -c "from webapp import create_app; a = create_app(); a.config['DATABASE'] = '<scratchpad>/qa/matches.db'; a.config['RESUMES_DIR'] = '<scratchpad>/qa/resumes'; a.run(port=5001)"` (run in background, stop it at the end; the owner's app on port 5000 stays untouched; only signal processes matching `port=5001`/your own PID).
- Everything is created under the session scratchpad directory (given in the system prompt), never in the repo: fixture job files `qa/jobs/*.md`, a `qa/screenshots/<stem>.png` for two of them, the QA database. Build the database with the app's own functions: `webapp.db.get_connection`, `init_db`, `create_resume`, `upsert_match` (see `app/webapp/db.py`).
- Boundary reminder (defined in E15-S06): days = today - Stale since; 0, 1, 2 -> stale; 3 or more -> hidden.

## Files to create/modify

- `docs/e15-qa-results.md` (new)

## Acceptance criteria

Record each step's command and output in `docs/e15-qa-results.md` (real numbers/status codes, no placeholders):
1. Fixtures: five job markdown files with `- Stale since:` = none, today-0, today-1, today-2, today-3 (distinct unique titles `QA live`, `QA stale0`, `QA stale1`, `QA stale2`, `QA hidden3`), one resume, five `New` matches (score 0.9), plus a sixth job `QA applied1` stale 1 day with status `Applied`. State the exact dates used.
2. Start the app on 5001; `curl -s localhost:5001/health` returns `{"status":"ok"}`.
3. Main page: `curl -s localhost:5001/` — the `resume-match-data` JSON has exactly 1 entry for the resume (the live one).
4. Resume detail: `curl -s localhost:5001/resumes/<id>` — `QA live` is inside an `<a href="/jobs/N">`; `QA stale0`, `QA stale1`, `QA stale2`, `QA applied1` appear only inside `class="stale-title"` spans, rows have `aria-disabled="true"`, and contain `stale since <date>`; `QA hidden3` does not appear (`grep -c` prints 0); the stale rows contain no `<select`.
5. Job detail: `curl -s -o /dev/null -w "%{http_code}"` for each match: live 200, stale0/1/2 200 (body contains `Delisted on <date>`), applied1 200, hidden3 404 (body contains `404`). Screenshot route: hidden3 404, stale with PNG 200 `image/png` (`curl -sI`), live with PNG 200.
6. Status endpoint: `curl -s -o /dev/null -w "%{http_code}" -X POST -d status=Done localhost:5001/matches/N/status` -> live 302, stale 409, hidden 404.
7. Boundary: re-run steps 4-5 after changing nothing but verify with a python one-liner that `stale_state(today-2) == 'stale'` and `stale_state(today-3) == 'hidden'` (from `webapp.jobs`), and note whether the dates used were crossing midnight.
8. Scraper side, on COPIES only: copy `scraper/scraper.db` and `scraper/jobs/` into the scratchpad, run `uv run python -m job_scraper stale-sync --db <copy>/scraper.db --jobs-dir <copy>/jobs` from `scraper/`, record the printed counters; then verify `grep -l '^- Stale since: ' <copy>/jobs/*.md | wc -l` equals `stale_rows - missing_md`, and run the command a second time: `dated`, `written`, `cleared` are all 0. The real `scraper/scraper.db` and `scraper/jobs/` are NOT modified (record `git -C scraper status --short` empty and file mtimes unchanged).
9. App stopped (nothing listening on 5001; 5000 untouched).
10. The file ends with "Follow-ups" (one line each), e.g. "run `stale-sync` on the real data after the owner OKs it", "first live `scrape` after Epic 15 will date newly delisted postings".
- `docs/e15-qa-results.md` exists, every step has a filled-in result, committed.

## Definition of done

- No file outside `docs/` is changed in the repo (scratchpad files are not committed).
- Committed in the JOB-HUNTER repo as `E15-S10: Record Epic 15 QA results`.
- The orchestrator ticks `docs/todo.md`.
