# E16-S16 — Live QA: detect delisted postings, settle wait, thin PNGs; record `docs/e16-qa-results.md`

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` (Safety rules for live runs) for conventions; do not repeat them here. This story writes ONLY `docs/e16-qa-results.md` (JOB-HUNTER repo); the generated data under `scraper/` is changed by the commands below, as in Epic 14's QA. Live network: the owner's OK is already given for this round, including "re-take the harveynash blanks". Starts only after the full-suite gate (GATE-6) is green.

## Goal

Prove on the real data that delisted postings are now marked stale from the detail fetch, that harveynash blanks and hero thin strips are gone, and record before/after counts against `docs/e14-qa-results.md`.

## Context

- Baseline numbers (live PNG ratio per site, 909/1058 = 0.86; working_nomads 39/56, synprofs 17/22, sevenstars 10/13, pro_act 10/12, circle8 2/3, hero 37/39, harveynash 33/34; 7 hero PNGs below 100 px, 9 harveynash 1116x30) are in `docs/e14-qa-results.md` sections 7 and 8; reuse its count script style (live = `is_stale = 0 and duplicate_of is null` in `scraper/scraper.db`, read-only `sqlite3 -readonly`).
- Commands (from `scraper/`; the module is run as `uv run python -m job_scraper ...`): `scrape --site X` (counters now include `gone`, `gone_suppressed`, `stale_marked`, `newly_stale`, `screenshots_taken/failed/skipped`), `screenshots --site X --missing-only`, `screenshots --prune-small --move-to DIR [--dry-run] [--min-height 100] [--site X]`.
- Real-data safety (same as Epics 14/15): never `--ignore-robots`, never `--include-stale`, owner's app on port 5000 untouched (record its HTTP code before and after, never stop it), own app on port 5001 only if you need it, no Cloudflare/bot-wall bypass. The drive is NTFS with known damage and slowed under heavy I/O before: ONE heavy process at a time, run each in the background with a log file in the session scratchpad, poll sparsely (every few minutes), and run `uptime` before each heavy step (continue only when the 1-minute load is below 8, otherwise wait). `~/.cache` lands on the crowded `/media/baz/MonkeyWorks` drive: check `df -h /media/baz/MonkeyWorks` first (need at least 5 GB free).
- Never run a second `scrape` while a first one is running. Expected total time 1-2 hours; if the first `scrape` shows more than 25 minutes for one site, stop and report instead of continuing.

## Files to create/modify

- `docs/e16-qa-results.md` (new)

## Acceptance criteria (steps)

1. Preconditions: `git -C scraper status --short` empty and `git -C scraper log --oneline | head -20` shows E16-S01..S15 (state the hashes); `uv run python -c "from job_scraper.core.screenshots import browser_available; print(browser_available())"` prints True; owner's app answers on port 5000; free disk space noted.
2. Backup (before any change): copy `scraper/scraper.db`, `scraper/jobs/`, `scraper/screenshots/` (and `scraper/raw/` if under 2 GB free-space budget) to `/media/baz/MonkeyWorks/backups/job-hunter-$(date +%F)-e16/` with `cp -a`, then verify with `diff -rq` on counts (file counts and `sqlite3 -readonly ... "select count(*) from jobs"`). Record paths and counts.
3. Baseline from disk (read-only): per-site markdown / PNG / live md / live PNG counts and the thin-PNG list (PNG heights from `struct.unpack(">II", data[16:24])` for hero and harveynash: count below 100 px).
4. Prune thin PNGs, all sites: first `screenshots --prune-small --dry-run` (record the counter line; expected about 7 hero + 9 harveynash + a few guru), then `screenshots --prune-small --move-to /media/baz/MonkeyWorks/backups/job-hunter-<date>-e16/moved-thin-pngs/` (record the counter line). Verify: no PNG below 100 px remains in `scraper/screenshots/`, the moved files exist in the backup folder, the matching markdown files have no `- Screenshot:` line.
5. Delisted detection, ONE `scrape --site X` invocation per site in this order: working_nomads, synprofs, pro_act, sevenstars, circle8, hero, harveynash (each in the background with a log; check `uptime` before each; wait for the site to finish before the next). Record per site the printed counters, in particular `seen, gone, gone_suppressed, written, newly_stale, stale_marked, screenshots_taken/failed/skipped`. Any `gone_suppressed > 0` means the safety valve fired: record it and do not rerun that site. Verify with read-only SQL that every `gone` detection ended `is_stale = 1` with `stale_since` = today and that the markdown has `- Stale since: <today>` (spot-check 3 files per site that had gone > 0), and that no previously stale row changed its `stale_since`.
6. Re-take captures: `screenshots --site harveynash --site hero --missing-only` (one invocation per site, background, log). Record counters. Expected: harveynash previously blank files are re-captured with real content; hero gated strips are skipped (`skipped_blocked`), never kept.
7. Count table and comparison: per site markdown, PNG, live md, live PNG, live ratio now vs `docs/e14-qa-results.md` section 7 (E14 ratio), and the `gone` count per site; total live ratio before 0.86. Explain every site whose ratio fell (stale rows leave the denominator: report both the ratio and the count of live postings without a PNG).
8. Thin PNGs after: count of PNGs below 100 px over all of `scraper/screenshots/` (must be 0) and the heights of the re-taken harveynash files (none at 1116x30; list min height).
9. Visual check with the Read tool on 3 PNGs: one re-taken harveynash file (expected full legible text, not washed out), one hero PNG (or state why none exist: all gated and skipped), one circle8 PNG. Verdict per file (size, what is visible).
10. URL check: re-run the Epic 14 URL-check query (`docs/e14-qa-results.md` section 4) against `scraper.db`; it must still return no rows.
11. Owner's app on port 5000 answered the same HTTP code before and after; no `--include-stale`, no `--ignore-robots`.
12. `docs/e16-qa-results.md` contains: run times, backup path, counters per command, the tables from steps 3, 4, 7, 8, the visual verdicts, "Unexpected" and "Follow-ups" sections (like Epic 14's), and a Brain fog summary. Anything that could not be verified is stated, not omitted.

## Definition of done

- The results file is complete per step 12; committed in the JOB-HUNTER repo as `E16-S16: Record Epic 16 QA results` (only `docs/e16-qa-results.md`).
- The orchestrator ticks `docs/todo.md`.
