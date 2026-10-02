# E13-S35 — Full re-scrape, screenshot backfill and QA runbook

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Run the whole improved pipeline once for real, then verify descriptions, URLs, screenshots and the app page, recording the results.

## Context

- This is the ONLY Epic 13 story that uses the network and writes to the generated, git-ignored directories `scraper/jobs/`, `scraper/raw/`, `scraper/scraper.db`, `scraper/screenshots/`. Needs E13-S01..S34 done.
- Commands (from `scraper/`): `uv run python -m job_scraper scrape --site <id|all>` (writes jobs, raw, and now screenshots by default), `uv run python -m job_scraper rebuild --site all`, `uv run python -m job_scraper screenshots --site all --missing-only`. Flags: `--ignore-robots` (never use without asking the owner), `--no-screenshots`.
- The app (`app/`): `uv run flask --app webapp run` (port 5000); job pages `/jobs/<match_id>`, screenshots `/jobs/<match_id>/screenshot`. The app's `matches` table (`source_url`, `title`, `job_file`) is filled by a rematch; match rows made before this epic keep their OLD `source_url` until a rematch, but the job detail page prefers the Markdown file's `- Source:` (E13-S12).
- Expect the scrape to take a long time (≈1100 postings, plus one browser launch per screenshot) and some sites to fail screenshots (selector drift, bot walls); the point is to measure that, not to make it perfect.
- Machine notes: `~/.cache/*` and the repo live on the crowded `/media/baz/MonkeyWorks` drive. ~1100 PNGs may take ~100-500 MB.

## Files to create/modify

- `docs/e13-qa-results.md` (new) — the only file written to git. Commit it in the JOB-HUNTER repo. Nothing in `scraper/` is committed by this story (generated dirs are ignored); if you find bugs, write them down as follow-up items in the results file instead of fixing them here.

## Acceptance criteria

Do the steps in order; record the output of each in `docs/e13-qa-results.md` (a section per step, numbers filled in, no placeholders):
1. Preconditions: `git -C scraper status --short` is empty; `uv run pytest` passes in `scraper/` and `uv run pytest tests/ -q` in `app/`; `uv run python -c "from job_scraper.core.screenshots import browser_available as b; print(b())"` prints `True`; `df -h /media/baz/MonkeyWorks` shows at least 2 GB free (otherwise stop and ask the owner).
2. Backup: copy `scraper/scraper.db`, `scraper/jobs/`, `scraper/raw/` to a dated folder outside the repo (state its path in the results file).
3. Offline sanity: `rebuild --site all`; all counters printed, `errors == 0` for every rebuilt site; list `working_nomads` and `tender_link` as skipped. Spot-check three rebuilt `jobs/*.md`: the description has `### `/`- ` structure and no line starts with `## ` except `## Description`/`## Scrape note`: `grep -c '^## ' <file>` is 1 or 2.
4. Canary scrape: `scrape --site pro_act` first; confirm `scraper/screenshots/pro_act-*.png` exist and are non-empty and the markdown has `- Screenshot:` lines. If the canary shows `screenshots_failed` equal to everything, stop and report (probable selector or browser problem).
5. Full re-scrape: `scrape --site all` (one invocation; if a site crashes the run, rerun that site alone; record which sites failed and why).
6. Backfill: `screenshots --site all --missing-only`; record per-site counters.
7. Count table (put it in the results file): per site — markdown files, raw files, PNG files, PNGs/markdown ratio. For sites with a selector the ratio should be >= 0.9; list every site below 0.9 with the likely cause.
8. URL check: `sqlite3 scraper/scraper.db "select site_id, count(*) from jobs where source_url like '%/job/go/%' or source_url like '%/api/%' or source_url like '%/apply%' or source_url like '%/wp-json/%' group by site_id"` returns no rows; also run it on the markdown: `grep -l '^- Source: .*\(/job/go/\|/api/\|/apply\)' scraper/jobs/*.md | wc -l` prints 0.
9. Visual check: open (Read tool) at least six PNGs from six different sites; for each say whether it shows only the description (no nav/menu/cookie banner) — attach the verdicts to the results file; list offending sites.
10. App check: start the app (`cd app && uv run flask --app webapp run`), do a rematch for one resume (via the app's rematch button/route), pick one match with a screenshot and one without. `curl -s localhost:5000/jobs/<id>` contains `class="job-description"` and `<h3`/`<li>` (for a job with structure); `curl -sI localhost:5000/jobs/<id>/screenshot` returns `200` and `Content-Type: image/png` for the first and `404` for the second; the "View original posting" `href` for a working_nomads and a stone_interim job contains `/jobs/` and `/opdrachten/` respectively and neither `/job/go/` nor `/api/`. Stop the app.
11. The results file ends with a "Follow-ups" list (selector fixes, failing sites, adapters needing work) — each item one line.
- `docs/e13-qa-results.md` exists, every step above has a filled-in result, and it is committed.

## Definition of done

- No scraper-repo commit needed; `git -C scraper status --short` is still clean afterwards (generated dirs are ignored).
- Committed in the JOB-HUNTER repo as `E13-S35: Record Epic 13 QA results`.
- `docs/todo.md` item for E13-S35 checked off in the same commit.
