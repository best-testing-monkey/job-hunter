# E14-S18 — Re-run screenshots for the fixed sites, visual check, record results (live network)

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (the safety rules for live runs in Appendix C apply in full). Commit goes to the JOB-HUNTER repo.

## Goal

Measure whether the Epic 14 fixes work on the real sites and record the numbers.

## Context

- Last Epic 14 story; needs E14-S01..S17 done and the full-suite gate after S17 green. Mirrors `docs/tickets/E13-S35-full-rescrape-and-qa-runbook.md` (read its steps) and compares against `docs/e13-qa-results.md` sections 6-9 (per-site counts, visual verdicts).
- Commands (from `scraper/`): `uv run python -m job_scraper scrape --site <id>` (repeatable), `uv run python -m job_scraper screenshots --site <id> [--missing-only]` (stale postings are skipped since E14-S05; `--include-stale` is never used here), counters are printed per site (`skipped_blocked`, `skipped_stale` are new).
- Live network, can be slow: ask the owner before starting any step expected to take more than 1 hour or to be heavy (steps 5-6 together are about 500 captures plus 30 s timeouts on failures). One heavy process at a time, polite delays, never `--ignore-robots`, the owner's app on port 5000 untouched, own app (only if needed) on 5001.
- Machine notes: 13 GB RAM, repo and `~/.cache` on the crowded `/media/baz/MonkeyWorks` drive.
- The only file written to git is `docs/e14-qa-results.md`. Bugs found become follow-up lines, not fixes.

## Files to create/modify

- `docs/e14-qa-results.md` (new)

## Acceptance criteria

Do the steps in order; record the output of each in its own section of `docs/e14-qa-results.md` with numbers filled in (no placeholders):
1. Preconditions: `git -C scraper status --short` empty; `uv run python -c "from job_scraper.core.screenshots import browser_available as b; print(b())"` prints `True`; `df -h /media/baz/MonkeyWorks` at least 2 GB free (else stop and ask); `pgrep -fa ms-playwright` shows nothing.
2. Backup: `scraper.db`, `jobs/`, `raw/`, `screenshots/` copied to `/media/baz/MonkeyWorks/backups/job-hunter-<date>-e14/`; path recorded.
3. URL refresh (E14-S07): `scrape --site working_nomads --site stone_interim` (one invocation; counters printed incrementally per E14-S06; if a site errors the other must still print). Then verify with a scratchpad script: for every `scraper.db` row with `is_stale = 0` and `duplicate_of is null` of those two sites, the markdown `- Source:` equals the DB `source_url`; record mismatches (expected 0). Record the number of remaining old-URL files that belong to stale rows (expected non-zero, handled by Epic 15).
4. Improved URL-check query (record it): `sqlite3 -readonly scraper/scraper.db "select site_id, count(*) from jobs where is_stale=0 and (source_url like '%/job/go/%' or source_url like '%/apply%' or source_url like '%/wp-json/%' or (source_url like '%/api/%' and source_url not like '%/projects/api/%')) group by site_id"` returns no rows (the freelancer.com `/projects/api/<slug>` category is a documented false positive).
5. New-site screenshots, missing only: `screenshots --site circle8 --site sevenstars --site wearedevelopers --site hero --site working_nomads --site stone_interim --site ictergezocht --missing-only` (ictergezocht must print `skipped_blocked` and `failed: 0`; hero gated pages must be `skipped_blocked`, not `failed`; stone_interim only if E14-S17 found a selector, else it must print `skipped_no_selector`).
6. Re-capture of the sites whose existing PNGs were wrong (guru truncated, iamexpat widgets, pro_act overlay, synprofs header, harveynash button): move their old PNGs into the backup folder first (`screenshots/<site>-*.png` for those five sites only), then `screenshots --site guru --site iamexpat --site pro_act --site synprofs --site harveynash --missing-only`. Record counters per site.
7. Count table (same columns as `docs/e13-qa-results.md` section 7: markdown, raw, PNG, PNG/md, live md, live PNG, live ratio) for every site, plus a column "E13 live ratio" copied from that file. Targets: live ratio >= 0.9 for every site with a selector; list each site below 0.9 with the likely cause, and every `skipped_blocked` count (hero gated, ictergezocht challenge) as "skipped on purpose".
8. Visual check: open (Read tool) one PNG each for guru, iamexpat, pro_act, synprofs, harveynash, circle8, sevenstars, wearedevelopers (8 PNGs; for any site with 0 PNGs say so instead). Per PNG: dimensions and verdict (only the ad? no header/consent dialog/dimmer/Apply buttons/Reageren button? guru not truncated?). Also check that no hero PNG is smaller than 100 px high: `python3 -c` over the files with `struct.unpack(">II", d[16:24])`.
9. Results file ends with "Follow-ups" (one line each) and a "Compared with E13" table (per-site live ratio before/after).
- `docs/e14-qa-results.md` exists, every step has real numbers, committed.

## Definition of done

- `git -C scraper status --short` is still empty afterwards (generated dirs are ignored).
- Committed in the JOB-HUNTER repo as `E14-S18: Record Epic 14 QA results`.
- The orchestrator ticks `docs/todo.md`.
