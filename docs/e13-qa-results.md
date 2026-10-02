# Epic 13 QA results (E13-S35)

Run date: 2026-10-02. Live run against the real sites, `--ignore-robots` never used. Wall clock 09:45 to 22:55, which includes a ~7 h pause: the owner froze the scrape (SIGSTOP) during system slowdown, the process died on resume (patchright launch timeout), and it was restarted site by site. Active work is roughly 1 h of scraping plus ~4.5 h of screenshot backfill (most of it 30 s selector timeouts on dead pages).

## 1. Preconditions

- `git -C scraper status --short`: empty.
- `browser_available()`: `True`.
- `df -h /media/baz/MonkeyWorks`: 10 GB free at start (98 % used); 41 GB free at end.
- pytest suites were NOT re-run in this story (orchestrator decision): the gate agents had just run them green (scraper 424 passed twice, app 94 passed).
- `pgrep`: only the owner's own snap Chromium was running, no ms-playwright processes.

## 2. Backup

`/media/baz/MonkeyWorks/backups/job-hunter-2026-10-02/` (1.1 GB): `scraper.db`, `jobs/`, `raw/`, plus (extra, for the step-10 rematch) `matches.db` and `resumes/` from `app/instance/`.

## 3. Offline sanity (`rebuild --site all`)

`errors == 0` for every rebuilt site. Skipped (not rebuildable): `working_nomads`, `tender_link` and also `stone_interim`.

| site | rebuilt | skipped_no_db | skipped_duplicate | excluded | errors |
|---|---|---|---|---|---|
| arc_dev | 1 | 0 | 0 | 0 | 0 |
| circle8 | 8 | 4 | 0 | 0 | 0 |
| djinni | 15 | 2 | 0 | 0 | 0 |
| flexvalue | 14 | 0 | 0 | 0 | 0 |
| freelancer_com | 27 | 0 | 1 | 0 | 0 |
| freelancermap | 21 | 0 | 1 | 0 | 0 |
| guru | 201 | 0 | 5 | 0 | 0 |
| harveynash | 23 | 2 | 0 | 0 | 0 |
| headfirst | 10 | 5 | 0 | 0 | 0 |
| hero | 49 | 0 | 0 | 0 | 0 |
| iamexpat | 275 | 3 | 2 | 0 | 0 |
| ictergezocht | 49 | 0 | 1 | 0 | 0 |
| planet_interim | 19 | 0 | 1 | 0 | 0 |
| pro_act | 10 | 1 | 0 | 0 | 0 |
| sevenstars | 12 | 0 | 0 | 0 | 0 |
| synprofs | 31 | 4 | 0 | 0 | 0 |
| wearedevelopers | 22 | 0 | 2 | 0 | 0 |

Spot-check (`grep -c '^## '`): `guru-1422412-...` 1, `iamexpat-18XLXN5Y2...` 1 (6 `###` headings, 25 bullets), `hero-04489d5d-...` 1. All pass.

## 4. Canary (`scrape --site pro_act`)

`{"seen": 12, "excluded": 0, "duplicates": 3, "written": 9, "stale_marked": 7, "screenshots_taken": 9, "screenshots_failed": 0}`. `screenshots/pro_act-*.png` exist and are non-empty (24 KB to 589 KB); markdown has `- Screenshot:` lines. Pass.

## 5. Full re-scrape

`scrape --site all` crashed in `headfirst` (curl 30 s timeout x3) after processing `arc_dev, circle8, djinni, flexvalue, freelancer_com, freelancermap, guru, harveynash`. The crash happened before the end-of-run counter summary, so those eight sites' counters were lost; their file counts are in the step-7 table instead. `headfirst` was rerun alone and passed. A second multi-site run for the other ten sites was frozen by the owner, then died on resume (browser launch timeout); the ten were then rerun one site per invocation (no retries were needed). Re-runs were idempotent: no screenshots or markdown disappeared (unchanged postings are counted as `duplicates`).

Per-site counters printed:

| site | seen | excluded | duplicates | written | stale_marked | shots_taken | shots_failed |
|---|---|---|---|---|---|---|---|
| pro_act (canary) | 12 | 0 | 3 | 9 | 7 | 9 | 0 |
| headfirst (rerun) | 10 | 0 | 4 | 6 | 10 | 0 | 0 |
| hero | 39 | 0 | 22 | 6 | 42 | 6 | 0 |
| iamexpat | 265 | 0 | 24 | 170 | 41 | 127 | 43 |
| ictergezocht | 50 | 0 | 22 | 28 | 29 | 0 | 28 |
| planet_interim | 20 | 0 | 2 | 18 | 18 | 0 | 0 |
| sevenstars | 13 | 0 | 2 | 11 | 10 | 0 | 11 |
| stone_interim | 19 | 0 | 5 | 14 | 7 | 0 | 0 |
| synprofs | 22 | 0 | 8 | 14 | 24 | 14 | 0 |
| tender_link | 250 | 16 | 100 | 134 | 118 | 134 | 0 |
| wearedevelopers | 24 | 0 | 20 | 2 | 2 | 0 | 2 |
| working_nomads | 59 | 0 | 51 | 8 | 1 | 6 | 2 |
| arc_dev, circle8, djinni, flexvalue, freelancer_com, freelancermap, guru, harveynash | counters lost (crash); live posting counts from the DB: 1, 3, 15, 13, 29, 22, 177, 34 | | | | | | |

Postings seen overall (DB, non-stale after the run): 1051 non-stale of 1505 rows (stale = delisted since earlier scrapes, kept).

No site was permanently failed. `ictergezocht` returned HTTP 403 (Cloudflare) for the detail pages: nothing was bypassed.

## 6. Backfill (`screenshots --site all --missing-only`)

| site | attempted | captured | failed | skipped_existing | skipped_no_selector |
|---|---|---|---|---|---|
| arc_dev | 1 | 1 | 0 | 1 | 0 |
| circle8 | 11 | 0 | 11 | 0 | 0 |
| djinni | 15 | 15 | 0 | 13 | 0 |
| flexvalue | 14 | 4 | 10 | 7 | 0 |
| freelancer_com | 27 | 26 | 1 | 21 | 0 |
| freelancermap | 21 | 21 | 0 | 21 | 0 |
| guru | 201 | 156 | 45 | 21 | 0 |
| harveynash | 23 | 23 | 0 | 29 | 0 |
| headfirst | 0 | 0 | 0 | 0 | 20 |
| hero | 49 | 12 | 37 | 31 | 0 |
| iamexpat | 153 | 94 | 59 | 152 | 0 |
| ictergezocht | 77 | 0 | 77 | 0 | 0 |
| planet_interim | 0 | 0 | 0 | 0 | 37 |
| pro_act | 10 | 2 | 8 | 9 | 0 |
| sevenstars | 23 | 0 | 23 | 0 | 0 |
| stone_interim | 0 | 0 | 0 | 0 | 26 |
| synprofs | 31 | 10 | 21 | 14 | 0 |
| tender_link | 214 | 97 | 117 | 134 | 0 |
| wearedevelopers | 24 | 0 | 24 | 0 | 0 |
| working_nomads | 54 | 4 | 50 | 6 | 0 |

Failure types in the backfill log: all but 20 are `Page.wait_for_selector: Timeout 30000ms exceeded` (selector never visible: delisted page, bot wall, consent overlay or selector drift); 20 on iamexpat are `Locator.screenshot: Element is not attached to the DOM`.

## 7. Count table (from disk after backfill)

"live" = postings the DB still marks non-stale; "stale" = delisted by the site since earlier scrapes, whose markdown is kept and whose pages are mostly gone (the main cause of selector timeouts for sites that look low overall).

| site | markdown | raw | PNG | PNG/md | live md | live PNG | live ratio |
|---|---|---|---|---|---|---|---|
| arc_dev | 2 | 2 | 2 | 1.00 | 1 | 1 | 1.00 |
| circle8 | 11 | 22 | 0 | 0.00 | 3 | 0 | 0.00 |
| djinni | 28 | 29 | 28 | 1.00 | 15 | 15 | 1.00 |
| flexvalue | 21 | 21 | 11 | 0.52 | 13 | 11 | 0.85 |
| freelancer_com | 48 | 48 | 47 | 0.98 | 30 | 30 | 1.00 |
| freelancermap | 42 | 44 | 42 | 1.00 | 21 | 21 | 1.00 |
| guru | 222 | 223 | 177 | 0.80 | 177 | 177 | 1.00 |
| harveynash | 52 | 55 | 52 | 1.00 | 33 | 33 | 1.00 |
| headfirst | 20 | 25 | 0 | n/a (no selector) | 10 | 0 | n/a |
| hero | 80 | 81 | 43 | 0.54 | 38 | 37 | 0.97 |
| iamexpat | 305 | 310 | 246 | 0.81 | 264 | 244 | 0.92 |
| ictergezocht | 77 | 79 | 0 | 0.00 | 49 | 0 | 0.00 |
| planet_interim | 37 | 38 | 0 | n/a (no selector) | 20 | 0 | n/a |
| pro_act | 19 | 19 | 11 | 0.58 | 12 | 11 | 0.92 |
| sevenstars | 23 | 23 | 0 | 0.00 | 13 | 0 | 0.00 |
| stone_interim | 26 | 26 | 0 | n/a (no selector, S29) | 19 | 0 | n/a |
| synprofs | 45 | 50 | 24 | 0.53 | 21 | 21 | 1.00 |
| tender_link | 348 | 370 | 231 | 0.66 | 231 | 231 | 1.00 |
| wearedevelopers | 24 | 26 | 0 | 0.00 | 22 | 0 | 0.00 |
| working_nomads | 60 | 60 | 10 | 0.17 | 59 | 10 | 0.17 |
| TOTAL | 1490 | 1550 | 924 | 0.62 | 1051 | 842 | 0.80 |

No zero-byte PNGs. `screenshots/` is 158 MB. Over sites that have a selector (excluding headfirst, planet_interim, stone_interim): 924/1407 = 0.66 overall, 842/1002 = 0.84 on live postings.

Sites below 0.9 and the likely cause:

- **circle8 (0/11)**: Cookiebot overlay (S30 flag) or page changed; selector `div.c-vacancy-paragraph__body-text` never became visible.
- **sevenstars (0/23)**: Cookiebot overlay (S30 flag); selector never visible.
- **ictergezocht (0/77)**: Cloudflare 403 challenge on detail pages (S32 flag; all raw pages are challenge pages) plus CookieYes banner. Not bypassed.
- **wearedevelopers (0/24)**: `section:has(> div.prose-base-content):not(...)` selector never visible (S32 flag, fragile `:has` selector or page changed/gated).
- **working_nomads (10/59 live)**: selector `div.jd-desktop div.jd-description` timed out; the failing URLs in the log are old `/job/go/<id>/` redirects because markdown for unchanged postings was never rewritten with the new `/jobs/` Source (see step 8), so the screenshot visits the wrong URL. Only the 10 rewritten files work.
- **flexvalue (11/21; live 11/13)**: 10 failures of `div.job-description`; the missed ones are delisted postings, 2 live misses unexplained.
- **hero (43/80; live 37/38)**: misses are delisted postings, where the page shows a gated teaser (S28 flag), `div.hero-requisition-body` not found; one live miss.
- **pro_act (11/19; live 11/12)**: misses are delisted postings and the `open-sollicitatie` form page (S18 note).
- **synprofs (24/45; live 21/21)** and **tender_link (231/348; live 231/231)** and **guru (177/222; live 177/177)**: all misses are delisted postings (their pages no longer exist); live coverage is 100 %.
- **iamexpat (246/305; live 244/264)**: 20 live misses with "Element is not attached to the DOM" (hashed class `div.BodyCenter_main__Sz_2E`, S30 flag; the page re-renders while the element shot is taken) plus delisted postings.
- **headfirst, planet_interim, stone_interim**: no selector by design (headfirst/planet_interim have no description scraped; stone_interim BLOCKED in S29 because the page is a client-rendered shell and no live selector was identified).

## 8. URL check

- `sqlite3 ... select site_id, count(*) ...` does NOT return zero rows: `freelancer_com|2`, `stone_interim|7`, `working_nomads|1`.
  - `freelancer_com` (2, fresh): false positives, the URL is `/projects/api/<slug>`, where "api" is the real freelancer.com project category, not an API endpoint.
  - `stone_interim` (7) and `working_nomads` (1): stale rows from the 2026-09-28 scrape (before the Epic 13 URL fixes), last seen 2026-09-28, `is_stale=1`.
- `grep -l '^- Source: .*\(/job/go/\|/api/\|/apply\)' scraper/jobs/*.md | wc -l` prints 66, not 0: 52 `working_nomads` (48 files dated 09-28 + 4 touched by the backfill adding `- Screenshot:`), 12 `stone_interim` (09-28), 2 `freelancer_com` (the false positives above).
- Every non-stale `working_nomads`/`stone_interim` DB row (and all fresh markdown I sampled) carries `/jobs/...` and `/opdrachten/id/...` URLs. Result: PASS for freshly scraped postings; FAIL for stale postings whose markdown was not rewritten (see follow-ups).

## 9. Visual check (PNGs opened with the Read tool)

| site | file | verdict |
|---|---|---|
| djinni | `djinni-841202-trainee-manual-qa-engineer.png` | CLEAN: description only, 670x1289, no nav/cookie/overlay. |
| freelancermap | `freelancermap-3049278-afra-11090-fullstack-developer-w-m-d.png` | CLEAN: description only, 820x1682. |
| harveynash | `harveynash-299093-project-assistent-jp3353.png` | Description plus the pink "Reageren" button at the bottom (S29 flag confirmed); text is washed out/faded (very low contrast) but legible. |
| guru | `guru-1728117-market-research-india.png` | TRUNCATED: only 783x180 showing the text cut at "... Show more" (S31 flag confirmed); full text is not captured. |
| iamexpat | `iamexpat-1dcPoN64gQiAhCsj2tDvhh-account-manager-dutch-amersfoort.png` | Description is on top but the shot also includes Apply/Bookmark/Share buttons, the yellow "Want more jobs like this?" alert signup, "More jobs from this employer", "Similar jobs" list and a floating ad box (S30 flag confirmed). |
| pro_act | `pro_act-8884-informatieanalist-ooapi.png` | Description visible but a grey dimmer plus a cookie consent dialog ("Accepteer alle cookies") covers the upper part of the page; the dimmer ends at the viewport height so the bottom half is un-dimmed. The contact form was hidden as designed. |
| hero | `hero-13f09263-functioneel-beheerder.png` | BAD: 640x65 strip of blurred text with "Log in om de volledige aanvraag te zien" (gated teaser, S28 flag confirmed). No description content. |
| synprofs | `synprofs-6912-ai-developer.png` | Description present but a sticky site header (logo + "Opdrachten / Leveranciers / ZZP-ers" nav) overlaps the top lines of the screenshot. |

Offending sites: guru (truncated), hero (gated teaser), pro_act (consent overlay), iamexpat (extra widgets), harveynash (button + faded), synprofs (nav bleed). Clean: djinni, freelancermap.

## 10. App check (own instance on port 5001; owner's app on 5000 untouched)

- Rematch: POST `/resumes/2/rematch` for resume 2 "Virtual assistant" only (model load ~45 s, finished within about a minute). Match rows for resume 2: before 1078, after 1490 (all markdown files, including stale ones). Resume 1 untouched (1078).
- Job with screenshot: match 1442 (Iamexpat): `/jobs/1442` 200, contains `class="job-description"`, 6 `<h3`, 19 `<li`; `curl -sI /jobs/1442/screenshot` returns `200 OK`, `Content-Type: image/png`.
- Job without screenshot: match 2287 (Ictergezocht): `/jobs/2287` 200, `class="job-description"` present, no screenshot block; `/jobs/2287/screenshot` returns `404 NOT FOUND`.
- "View original posting" href: working_nomads match 2347 -> `https://www.workingnomads.com/jobs/storyteller-freelance-...` (contains `/jobs/`, no `/job/go/`); stone_interim match 1817 -> `https://www.stone-interim.nl/opdrachten/id/4671/...` (contains `/opdrachten/`, no `/api/`). Pass.
- Caveat: after the rematch, `matches` has 52 rows with `/job/go/` and 14 with `/api/` source_url (stale postings' old markdown).
- App on port 5001 stopped. When checking at the end, nothing answered on port 5000 either; I only signalled processes matching `port 5001`.

## 11. Follow-ups

- working_nomads/stone_interim: markdown for postings whose content hash is unchanged is never rewritten, so old `/job/go/` and `/api/` Source lines persist (52 + 12 files); rewrite markdown when the source_url changes (or run a one-off refresh).
- working_nomads: backfill screenshots visit the stale `/job/go/` URL (50 failures); fix the Source URL first, then re-run `screenshots --site working_nomads --missing-only`.
- Scraper crash safety: one site's curl timeout killed `scrape --site all` and lost all earlier per-site counters; catch per-site exceptions and print counters incrementally.
- Scraper resilience: add a per-run retry or resume so a pause or stale browser (patchright `launch_persistent_context` 180 s timeout) does not kill a run.
- Screenshot backfill should skip or fast-fail postings already marked `is_stale=1` (hundreds of 30 s timeouts, ~4.5 h wall).
- circle8 and sevenstars: dismiss or hide the Cookiebot overlay before the element screenshot (0 PNGs).
- ictergezocht: Cloudflare 403 on detail pages; needs an owner decision (no bypass attempted); the CookieYes banner also needs hiding.
- wearedevelopers: `:has()` selector never matches in the live page, find a stable selector (0 PNGs).
- hero: gated/blurred teaser gives a 640x65 strip; detect the gate and skip the screenshot or record "gated" instead.
- guru: element is truncated at "... Show more"; click to expand before capturing.
- iamexpat: hashed class `BodyCenter_main__Sz_2E` yields 20 "not attached to the DOM" failures and captures alert signup/Similar jobs/Apply buttons; use `screenshot_hide_selectors` or a narrower wrapper.
- pro_act: dismiss the cookie consent dialog and dimmer (add it to `screenshot_hide_selectors`).
- synprofs: hide the sticky header before the element screenshot.
- harveynash: hide the "Reageren" button/share icons; text looks faded.
- stone_interim: client-rendered shell, find a live selector (still BLOCKED, 0 PNGs); headfirst and planet_interim still have no description or selector.
- URL check query: exclude the freelancer.com `/projects/api/` category false positive.
- headfirst: source_url is the shared `/vind-opdrachten` overview (open owner question from S17); pro_act `open-sollicitatie` is not a job ad (S18).
- App: rematch includes stale (delisted) markdown files (1078 -> 1490 matches); consider filtering `is_stale` postings.
