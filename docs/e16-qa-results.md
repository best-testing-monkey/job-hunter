# Epic 16 QA results (E16-S16, live run 2026-10-05)

Run 16:37-16:47 (about 10 min wall; each scrape 20-60 s, load average stayed below 5). One heavy process at a time, each in the background with a log. Owner's app on port 5000: HTTP 200 before and after, untouched. No `--include-stale`, no `--ignore-robots`, no challenge solving. Pytest not run (GATE-6 just passed).

## 1. Preconditions

- `git -C scraper status --short`: empty. Scraper log shows E16-S01..S15: S01 a4d4220, S02 b50420c, S03 0fcbc3d, S04 0dc1f8d, S05 2fab981, S06 35a7a61, S07 c65fa31, S08 b1d7e72, S09 3bb6e9a, S10 204735b, S11 614f22c, S12 1998c08, S13 4edd2e9, S14 68fc23a, S15 21a6ce1.
- `browser_available()`: True. Port 5000: 200. Disk: 40 GB free (90 % used).

## 2. Backup

`/media/baz/MonkeyWorks/backups/job-hunter-2026-10-05-e16/` (`scraper.db`, `jobs/`, `screenshots/`, `moved-thin-pngs/`). Verified: `jobs/` 1490 = 1490 files, `screenshots/` 969 = 969 files, `diff -rq` empty for both, `cmp scraper.db` identical, `select count(*) from jobs` 1507 = 1507. **`raw/` is NOT backed up** (1.1 GB, skipped on instruction; the scrape only adds files there). The pre-Epic-14 backup `job-hunter-2026-10-05-pre-e14/` still holds `raw/`.

## 3. Baseline from disk (before any change)

Live = `is_stale = 0 and duplicate_of is null` (1039 rows). Note: Epic 14 counted `is_stale = 0` only (1058, includes 19 `duplicate_of` rows), so E14 totals are not directly comparable by 19 rows.

| site | markdown | PNG | live md | live PNG | live ratio | stale today |
|---|---|---|---|---|---|---|
| arc_dev | 2 | 2 | 1 | 1 | 1.00 | 1 |
| circle8 | 11 | 2 | 3 | 2 | 0.67 | 8 |
| djinni | 28 | 28 | 15 | 15 | 1.00 | 13 |
| flexvalue | 21 | 11 | 13 | 11 | 0.85 | 8 |
| freelancer_com | 48 | 47 | 29 | 29 | 1.00 | 18 |
| freelancermap | 42 | 42 | 21 | 21 | 1.00 | 21 |
| guru | 222 | 160 | 173 | 156 | 0.90 | 45 |
| harveynash | 52 | 33 | 33 | 33 | 1.00 | 19 |
| headfirst | 20 | 0 | 10 | 0 | 0.00 | 10 |
| hero | 80 | 43 | 38 | 37 | 0.97 | 42 |
| iamexpat | 305 | 253 | 262 | 251 | 0.96 | 41 |
| ictergezocht | 77 | 0 | 49 | 0 | 0.00 | 28 |
| planet_interim | 37 | 0 | 20 | 0 | 0.00 | 17 |
| pro_act | 19 | 10 | 12 | 10 | 0.83 | 7 |
| sevenstars | 23 | 10 | 13 | 10 | 0.77 | 10 |
| stone_interim | 26 | 19 | 19 | 19 | 1.00 | 7 |
| synprofs | 45 | 17 | 21 | 17 | 0.81 | 24 |
| tender_link | 348 | 231 | 231 | 231 | 1.00 | 117 |
| wearedevelopers | 24 | 22 | 22 | 22 | 1.00 | 2 |
| working_nomads | 60 | 39 | 54 | 39 | 0.72 | 6 |
| TOTAL | 1490 | 969 | 1039 | 904 | 0.87 | |

Thin PNGs (< 100 px), 20 in total: harveynash 9 (1116x30), hero 7 (640x65: 4, 640x97: 3), guru 3 (1566x52), freelancer_com 1 (744x25, `freelancer_com-saas-mefticaret-denetimi-...`).

## 4. Prune thin PNGs (all sites)

- Dry run: `{"scanned": 969, "small": 20, "moved": 0, "markdown_updated": 0, "unreadable": 0, "skipped_exists": 0}`
- Real: `{"scanned": 969, "small": 20, "moved": 20, "markdown_updated": 20, "unreadable": 0, "skipped_exists": 0}`
- Verified: 20 files in `backups/job-hunter-2026-10-05-e16/moved-thin-pngs/`; 0 PNGs below 100 px left in `screenshots/` (949 PNGs); all 20 matching markdown files exist and have no `- Screenshot:` line.

## 5. Delisted detection (one `scrape --site X` each, in order)

| site | time | seen | excluded | dups | written | gone | gone_suppressed | stale_marked | newly_stale | shots taken/failed/skipped |
|---|---|---|---|---|---|---|---|---|---|---|
| working_nomads | 16:38:50-16:40:20 | 56 | 0 | 2 | 0 | 0 | 0 | 6 | 0 | 0/0/0 |
| synprofs | 16:40:34-16:40:51 | 25 | 0 | 1 | 8 | 0 | 0 | 28 | 4 | 8/0/0 |
| pro_act | 16:41:00-16:41:06 | 11 | 0 | 0 | 2 | 0 | 0 | 9 | 2 | 2/0/0 |
| sevenstars | 16:41:10-16:42:07 | 14 | 0 | 0 | 6 | 0 | 0 | 15 | 5 | 6/0/0 |
| circle8 | 16:42:19-16:43:00 | 10 | 1 | 0 | 7 | 0 | 0 | 9 | 1 | 7/0/0 |
| hero | 16:43:08-16:44:12 | 52 | 0 | 3 | 15 | 0 | 0 | 46 | 4 | 14/0/1 |
| harveynash | 16:44:16-16:44:55 | 39 | 2 | 1 | 15 | 1 | 0 | 29 | 10 | 15/0/0 |

- `gone_suppressed` was 0 everywhere (safety valve never fired). All sites exit code 0.
- Only one detail-fetch detection: harveynash `299222` ("is gone (http 404)"), now `is_stale = 1`, `stale_since = 2026-10-05`, markdown has `- Stale since: 2026-10-05`.
- 26 rows turned stale in total (circle8 1, harveynash 10, hero 4, pro_act 2, sevenstars 5, synprofs 4), all `stale_since = 2026-10-05`; spot-check of 3 markdown files per site (2 for pro_act): all have `- Stale since: 2026-10-05`. No previously stale row changed (`comm` of id+stale_since before vs after: 0 lost). 5 older stale rows with NULL `stale_since` (freelancermap, guru, ictergezocht, planet_interim, tender_link) are untouched and pre-existing.
- working_nomads: 15 "could not verify human URL" lines (the posting page redirects to `/jobs`) but `gone` = 0 and `newly_stale` = 0: those 15 live postings are still not marked stale (see Unexpected).

## 6. Re-take captures (`--missing-only`, one invocation per site)

| site | attempted | captured | failed | skipped_existing | skipped_no_selector | skipped_blocked | skipped_stale |
|---|---|---|---|---|---|---|---|
| harveynash | 0 | 0 | 0 | 35 | 0 | 0 | 29 |
| hero | 8 | 0 | 1 | 41 | 0 | 7 | 46 |

- harveynash: nothing left to capture; the 15 captures happened during the scrape (screenshots_taken 15), all with the settle wait. All 9 previously blank (1116x30) postings are now stale (delisted), so they were never re-captured (`skipped_stale`); the blank strips were most likely captures of pages that had already disappeared.
- hero: 7 gated pages `skipped_blocked` (the old strips were not re-created), 1 `failed`.

## 7. Count table after the run

Live = `is_stale = 0 and duplicate_of is null` (1061 rows). "E14" is the E14 section 7 ratio.

| site | markdown | PNG | live md | live PNG | live ratio | live w/o PNG | E14 ratio | gone | newly_stale |
|---|---|---|---|---|---|---|---|---|---|
| arc_dev | 2 | 2 | 1 | 1 | 1.00 | 0 | 1.00 | - | - |
| circle8 | 18 | 9 | 9 | 9 | 1.00 | 0 | 0.67 | 0 | 1 |
| djinni | 28 | 28 | 15 | 15 | 1.00 | 0 | 1.00 | - | - |
| flexvalue | 21 | 11 | 13 | 11 | 0.85 | 2 | 0.85 | - | - |
| freelancer_com | 48 | 46 | 29 | 28 | 0.97 | 1 | 1.00 | - | - |
| freelancermap | 42 | 42 | 21 | 21 | 1.00 | 0 | 0.95 | - | - |
| guru | 222 | 157 | 173 | 155 | 0.90 | 18 | 0.90 | - | - |
| harveynash | 64 | 36 | 35 | 35 | 1.00 | 0 | 0.97 | 1 | 10 |
| headfirst | 20 | 0 | 10 | 0 | 0.00 | 10 | 0.00 | - | - |
| hero | 95 | 50 | 49 | 41 | 0.84 | 8 | 0.95 | 0 | 4 |
| iamexpat | 305 | 253 | 262 | 251 | 0.96 | 11 | 0.95 | - | - |
| ictergezocht | 77 | 0 | 49 | 0 | 0.00 | 49 | 0.00 | - | - |
| planet_interim | 37 | 0 | 20 | 0 | 0.00 | 20 | 0.00 | - | - |
| pro_act | 20 | 11 | 11 | 11 | 1.00 | 0 | 0.83 | 0 | 2 |
| sevenstars | 29 | 16 | 14 | 14 | 1.00 | 0 | 0.77 | 0 | 5 |
| stone_interim | 26 | 19 | 19 | 19 | 1.00 | 0 | 1.00 | - | - |
| synprofs | 52 | 24 | 24 | 24 | 1.00 | 0 | 0.77 | 0 | 4 |
| tender_link | 348 | 231 | 231 | 231 | 1.00 | 0 | 0.99 | - | - |
| wearedevelopers | 24 | 22 | 22 | 22 | 1.00 | 0 | 0.92 | - | - |
| working_nomads | 60 | 39 | 54 | 39 | 0.72 | 15 | 0.70 | 0 | 0 |
| TOTAL | 1538 | 996 | 1061 | 927 | 0.87 | 134 | 0.86 | 1 | 26 |

Total live ratio: baseline 904/1039 = 0.870 (E14 reported 909/1058 = 0.86 with the 19 duplicate rows), after prune 887/1039 = 0.854, now 927/1061 = 0.874. Stale rows 449 -> 475 (+26).

Sites whose ratio fell vs E14 (the E14 and baseline columns differ only by the duplicate filter and the prune):

- hero 0.95 -> 0.84 (41/49): live rows grew 38 -> 49 (new postings), and 8 live postings have no PNG: 7 gated teasers `skipped_blocked` (the 7 old strips, now removed rather than kept; 6 of them still live) plus 1 failure. This is the intended outcome (strips removed), not a regression.
- freelancer_com 1.00 -> 0.97: its one 744x25 PNG was moved by the prune (live, now without PNG).
- guru 0.90 -> 0.90 (155/173): 3 thin 1566x52 PNGs moved, 18 live without PNG.
- working_nomads 0.72: unchanged (15 live without PNG, see Unexpected). headfirst/planet_interim/ictergezocht 0.00 by design (no selector or blocked).

## 8. Thin PNGs after

- PNGs below 100 px over all `screenshots/`: **0** (996 PNGs; 0 zero-byte files).
- harveynash: 36 PNGs, none 1116x30, min height 1570 (761x1570, `harveynash-299279-digital-marketing-ux-expert.png`); the 15 re-taken today are 761 wide, 2198-3829 px high.
- hero: 50 PNGs, min height 129 (640x129), max 497. 44 of 50 are 497 px or lower (see Unexpected).
- circle8: 9 PNGs, min 4670 px high.

## 9. Visual check (Read tool)

| file | size | verdict |
|---|---|---|
| `harveynash-299322-juridisch-medewerker-privacydesk.png` (taken today) | 761x3035 | GOOD. Full legible black text on white (assignment, requirements, competencies, bullet lists, ZZP note); not washed out; no Reageren button. Fade-in fix works. The 9 old blank files could not be re-taken (their postings are stale). |
| `hero-3e56d138-assetmanager-water-en-riolering.png` (taken today) | 640x385 | BAD. Not the posting: a modal "Log in om de volledige aanvraag te zien" with a "Log in bij Hero" button over blurred text. It passes the 100 px threshold but is a login-gate teaser, not content. |
| `circle8-VNR-85412-senior-java-tester.png` (taken today) | 1524x4670 | GOOD. "Functieomschrijving" description, requirements, wishes, competencies; legible, no cookie banner or nav. |

## 10. URL check

The E14 section 4 query on `scraper.db` returned **no rows** (PASS).

## 11. Owner's app and flags

Port 5000: HTTP 200 before, 200 after. No `--include-stale`, no `--ignore-robots`. `git status --short` clean in job-hunter (before this file) and scraper; no stray `ms-playwright|chrome-headless|camoufox` processes.

## Unexpected

- `gone` fired only once in 7 sites (harveynash 299222, 404). The postings that E14 predicted as detail-fetch gone (circle8 VNR-85520, sevenstars 004985/86/87, synprofs 6934/6937/6944, pro_act 8721/8889, hero 2) were instead marked by the old end-of-run logic (`newly_stale`, absent from the listing). Detection from the detail fetch is thus only proven on one 404.
- working_nomads: its detail data comes from the API; the human posting page redirects to `/jobs` for 15 live postings, but that fetch is not covered by `gone_check`, so `gone` stays 0 and 15 live postings without PNG remain (0.72).
- harveynash: the 9 blank captures belong to postings that are now stale; blanks were not "re-taken".
- hero: most PNGs are gated login teasers 129-497 px high, only taller than the 100 px threshold (1 file opened and confirmed; the others of similar height are unverified).
- 5 old stale rows have `stale_since` NULL.

## Follow-ups

- hero: detect the login-gate modal (text "Log in om de volledige aanvraag te zien") and skip/prune these PNGs; 44 of 50 are below 500 px; raise `screenshot_min_height` for hero or check the DOM.
- working_nomads: pass `gone_check` to the human-URL verification (redirect to `/jobs`) so the 15 delisted postings get stale.
- Backfill `stale_since` for the 5 NULL stale rows.
- Check the remaining hero PNGs (`<= 500 px`) one by one before trusting them.
- guru 18 and iamexpat 11 live without PNG; flexvalue 2: re-run `screenshots --missing-only` later; ictergezocht 49 stays blocked on purpose.
- E14 counted duplicates in "live"; use the `duplicate_of is null` definition in future QA.

## Brain fog summary

- **Backup** done: db, jobs, screenshots; **raw/** not backed up.
- **Prune** moved 20 thin PNGs; 0 left under 100 px.
- **Scrapes**: 7 sites, `gone` only 1 (harveynash 404); 26 newly stale.
- **harveynash** now good, full text. Old blanks were stale postings.
- **hero** has login-gate PNGs that pass the height check. Needs a fix.
- **working_nomads** 15 delisted still live.
- **Live ratio** 0.870 before, 0.874 after.
- **URL check** clean. **Port 5000** 200 both times.
