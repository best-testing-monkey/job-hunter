# Epic 15 QA results (E15-S10)

Run 2026-10-05 around 12:53 CEST (far from midnight; no midnight crossing). All fixtures live in the session scratchpad (`.../scratchpad/e15qa/qa/`), never in the repo. Real data untouched: `stat -c '%Y %n'` before and after both gave `1790957433 scraper/scraper.db` and `1791196171 app/instance/matches.db` (unchanged).

## 1. Fixtures — PASS
Today = 2026-10-05. Jobs (`qa/jobs/*.md`), built with `webapp.db.create_resume` / `upsert_match` into `qa/matches.db`, one resume (id 1), score 0.9:

| match id | title | Stale since | status |
|---|---|---|---|
| 1 | QA live | none | New |
| 2 | QA stale0 | 2026-10-05 | New |
| 3 | QA stale1 | 2026-10-04 | New |
| 4 | QA stale2 | 2026-10-03 | New |
| 5 | QA hidden3 | 2026-10-02 | New |
| 6 | QA applied1 | 2026-10-04 | Applied |

PNGs in `qa/screenshots/` for `qa_live`, `qa_stale1`, `qa_hidden3`.

## 2. Health — PASS
App started on port 5001 (pid 3393288, own DB/RESUMES_DIR in scratchpad). `curl -s localhost:5001/health` -> `{"status":"ok"}`.

## 3. Main page — PASS
`curl -s localhost:5001/` -> `resume-match-data` = `{"1": [{"job_posted": null, "score": 0.9, "status": "New"}]}` (exactly 1 entry, the live one).

## 4. Resume detail — PASS
`curl -s localhost:5001/resumes/1`:
- `QA live` inside `<a href="/jobs/1">`.
- `QA stale0/1/2` and `QA applied1` only in `<span class="stale-title">`, rows `aria-disabled="true"`, badges `stale since 2026-10-05`, `2026-10-04`, `2026-10-03`, `2026-10-04`.
- `grep -c 'QA hidden3'` -> 0.
- `<select` count in whole page 1 (live row only); 0 within stale rows.

## 5. Job detail and screenshot — PASS
| match | /jobs/N | body |
|---|---|---|
| 1 live | 200 | no notice |
| 2 stale0 | 200 | `Delisted on 2026-10-05` |
| 3 stale1 | 200 | `Delisted on 2026-10-04` |
| 4 stale2 | 200 | `Delisted on 2026-10-03` |
| 5 hidden3 | 404 | contains `404` |
| 6 applied1 | 200 | `Delisted on 2026-10-04` |

Screenshot route (`curl -sI`): hidden3 (5) 404; stale1 (3, has PNG) 200 `image/png`; live (1) 200 `image/png`; stale0 (2, no PNG) 404 (extra check).

## 6. Status endpoint — PASS
`POST status=Done`: live (1) 302, stale (3) 409, hidden (5) 404.

## 7. Boundary — PASS
`stale_state(today-2, today)` = `stale`, `stale_state(today-3, today)` = `hidden` (also today -> `stale`, None -> `live`). Dates did not cross midnight during the run (steps 4-7 all within the same minute, 2026-10-05).

## 8. Scraper stale-sync on copies — PASS
Copied `scraper/scraper.db` and `scraper/jobs/` (1490 files) to `.../e15qa/sc/`; ran from `scraper/` with `--db`/`--jobs-dir` pointing at the copies.
- First run: `{"stale_rows": 439, "dated": 439, "written": 439, "cleared": 0, "missing_md": 0}`
- `grep -l '^- Stale since: ' <copy>/jobs/*.md | wc -l` -> 439 = 439 - 0.
- Second run: `{"stale_rows": 439, "dated": 0, "written": 0, "cleared": 0, "missing_md": 0}` (idempotent).
- `git -C scraper status --short` empty; real `scraper.db` mtime unchanged (1790957433).

## 9. App stopped — PASS
Only pid 3393288 was signalled. `curl localhost:5001/health` -> `000` (nothing listening). Owner's app on 5000 still returns 200 (pids 835716/835720 untouched).

## Follow-ups
- Run `stale-sync` on the real `scraper/scraper.db` and `scraper/jobs/` after the owner OKs it (would date 439 rows and write 439 bullets today).
- First live `scrape` after Epic 15 will date newly delisted postings.
- Owner's running app on port 5000 predates Epic 15 code; restart it (owner decision) to see stale behaviour.
