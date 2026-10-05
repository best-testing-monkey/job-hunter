# Epic 14 QA results (E14-S18, live run 2026-10-05)

Run 13:52-15:04 (about 1 h 12 min wall). One heavy process at a time, one `--site` per invocation for screenshots, load average stayed below 6. Owner's app on port 5000 untouched (200 before and after). No `--include-stale`, no `--ignore-robots`, no challenge solving.

## State before step 3 (already done by the owner)

- Real `stale-sync` already run (439 stale postings dated 2026-10-05); `scraper.db` already migrated (`stale_since` column; 703 self-duplicate rows repaired, `duplicate_of` rows 725 -> 22). Not re-run.
- Before step 3: 444 stale rows in total, working_nomads 59 live / 1 stale, stone_interim 19 live / 7 stale, 22 `duplicate_of` rows, 924 PNGs, 1490 markdown files.

## 1. Preconditions

- `git -C scraper status --short`: empty. `browser_available()`: `True`. `df -h /media/baz/MonkeyWorks`: 40 GB free (90 % used). No `ms-playwright` process. Owner's app answered 200 on port 5000.

## 2. Backup

Satisfied by the owner's verified backup `/media/baz/MonkeyWorks/backups/job-hunter-2026-10-05-pre-e14/` (`scraper.db`, `jobs/`, `raw/`, `screenshots/`, `app-instance`). Old wrong PNGs from step 6 are in its subfolder `moved-old-pngs/` (510 files).

## 3. URL refresh (`scrape --site working_nomads --site stone_interim`, one invocation, 14:00-14:05)

| site | seen | excluded | duplicates | written | stale_marked | newly_stale | shots_taken | shots_failed | shots_skipped |
|---|---|---|---|---|---|---|---|---|---|
| working_nomads | 56 | 0 | 2 | 46 | 6 | 5 | 33 | 13 | 0 |
| stone_interim | 19 | 0 | 0 | 5 | 7 | 0 | 4 | 1 | 0 |

- Counters printed incrementally, no site errored. The log shows 15 "could not verify human URL" lines for working_nomads (the posting page redirects to the `/jobs` listing); 13 working_nomads shots failed with a 30 s selector timeout and one stone_interim shot failed with `Page.goto` timeout.
- Verification script (every row of both sites with `is_stale = 0` and `duplicate_of is null`, markdown `- Source:` vs DB `source_url`): 73 checked, **0 mismatches**, 0 missing files.
- Old-URL (`/job/go/`, `/api/`, `/apply`) markdown files remaining: 13, all belonging to stale rows (0 belong to non-stale rows). Left for Epic 15.

## 4. URL-check query (improved)

`sqlite3 -readonly scraper/scraper.db "select site_id, count(*) from jobs where is_stale=0 and (source_url like '%/job/go/%' or source_url like '%/apply%' or source_url like '%/wp-json/%' or (source_url like '%/api/%' and source_url not like '%/projects/api/%')) group by site_id"` returned **no rows**. PASS. (freelancer_com `/projects/api/<slug>`: 2 rows, documented false positive.)

## 5. New-site screenshots (`--missing-only`, one invocation per site)

| site | attempted | captured | failed | skipped_existing | skipped_no_selector | skipped_blocked | skipped_stale |
|---|---|---|---|---|---|---|---|
| circle8 | 3 | 2 | 1 | 0 | 0 | 0 | 8 |
| sevenstars | 13 | 10 | 3 | 0 | 0 | 0 | 10 |
| wearedevelopers | 22 | 22 | 0 | 0 | 0 | 0 | 2 |
| hero | 1 | 0 | 1 | 37 | 0 | 0 | 42 |
| working_nomads | 15 | 0 | 15 | 39 | 0 | 0 | 6 |
| stone_interim | 15 | 15 | 0 | 4 | 0 | 0 | 7 |
| ictergezocht | 49 | 0 | 0 | 0 | 0 | 49 | 28 |

- ictergezocht: `skipped_blocked` 49, `failed` 0: as required (Cloudflare challenge, skipped on purpose).
- stone_interim: selector exists (E14-S17), 19 live PNGs.
- hero: `skipped_blocked` is 0 (the gate cannot be selector-skipped, E14-S09); the one live miss `hero-675068ef` failed with a selector timeout, so it was counted `failed`, not `skipped_blocked`.
- working_nomads: all 15 attempts failed (selector timeout). These are the postings whose page redirects to the `/jobs` listing (the "could not verify human URL" ones): delisted, but `scraper.db` still says `is_stale=0`.
- Failures in circle8 (1), sevenstars (3): selector timeouts on 404-style pages of delisted postings that are not yet marked stale (see follow-ups).

## 6. Re-capture of the five previously wrong sites

Old PNGs moved first: guru 177, iamexpat 246, pro_act 11, synprofs 24, harveynash 52 (510 files) into `moved-old-pngs/` of the backup folder. Then one invocation per site, `--missing-only`:

| site | attempted | captured | failed | skipped_existing | skipped_no_selector | skipped_blocked | skipped_stale |
|---|---|---|---|---|---|---|---|
| synprofs | 21 | 17 | 4 | 0 | 0 | 0 | 24 |
| pro_act | 12 | 10 | 2 | 0 | 0 | 0 | 7 |
| harveynash | 33 | 33 | 0 | 0 | 0 | 0 | 19 |
| iamexpat | 264 | 253 | 11 | 0 | 0 | 0 | 41 |
| guru | 177 | 160 | 17 | 0 | 0 | 0 | 45 |

All 34 failures are `Page.wait_for_selector: Timeout 30000ms exceeded` (iamexpat 20 "not attached to the DOM" failures of E13 are gone; guru 17, iamexpat 11, synprofs 4, pro_act 2).

## 7. Count table (from disk after the run)

"live" = non-stale in `scraper.db` (stale-sync dated 2026-10-05, 449 stale rows now).

| site | markdown | raw | PNG | PNG/md | live md | live PNG | live ratio | E13 live ratio |
|---|---|---|---|---|---|---|---|---|
| arc_dev | 2 | 2 | 2 | 1.00 | 1 | 1 | 1.00 | 1.00 |
| circle8 | 11 | 22 | 2 | 0.18 | 3 | 2 | 0.67 | 0.00 |
| djinni | 28 | 29 | 28 | 1.00 | 15 | 15 | 1.00 | 1.00 |
| flexvalue | 21 | 21 | 11 | 0.52 | 13 | 11 | 0.85 | 0.85 |
| freelancer_com | 48 | 48 | 47 | 0.98 | 29 | 29 | 1.00 | 1.00 |
| freelancermap | 42 | 44 | 42 | 1.00 | 22 | 21 | 0.95 | 1.00 |
| guru | 222 | 223 | 160 | 0.72 | 177 | 160 | 0.90 | 1.00 |
| harveynash | 52 | 55 | 33 | 0.63 | 34 | 33 | 0.97 | 1.00 |
| headfirst | 20 | 25 | 0 | 0.00 | 10 | 0 | 0.00 | n/a |
| hero | 80 | 81 | 43 | 0.54 | 39 | 37 | 0.95 | 0.97 |
| iamexpat | 305 | 310 | 253 | 0.83 | 265 | 252 | 0.95 | 0.92 |
| ictergezocht | 77 | 79 | 0 | 0.00 | 50 | 0 | 0.00 | 0.00 |
| planet_interim | 37 | 38 | 0 | 0.00 | 20 | 0 | 0.00 | n/a |
| pro_act | 19 | 19 | 10 | 0.53 | 12 | 10 | 0.83 | 0.92 |
| sevenstars | 23 | 23 | 10 | 0.43 | 13 | 10 | 0.77 | 0.00 |
| stone_interim | 26 | 26 | 19 | 0.73 | 19 | 19 | 1.00 | n/a |
| synprofs | 45 | 50 | 17 | 0.38 | 22 | 17 | 0.77 | 1.00 |
| tender_link | 348 | 370 | 231 | 0.66 | 234 | 231 | 0.99 | 1.00 |
| wearedevelopers | 24 | 26 | 22 | 0.92 | 24 | 22 | 0.92 | 0.00 |
| working_nomads | 60 | 62 | 39 | 0.65 | 56 | 39 | 0.70 | 0.17 |
| TOTAL | 1490 | 1553 | 969 | 0.65 | 1058 | 909 | 0.86 | 0.80 |

No zero-byte PNGs. `screenshots/` is 200 MB. Over all sites with a selector, live PNG ratio is 909/1028 = 0.88 (headfirst 0/10 and planet_interim 0/20 have no selector by design and are excluded; including them the total is 909/1058 = 0.86).

Sites below 0.9 live and likely cause:

- **headfirst, planet_interim**: no description and no selector, by design (not counted).
- **circle8 0.67 (2/3)**: the one miss is `VNR-85520`, a delisted posting returning a 404 page while `is_stale=0`. Up from 0.00.
- **sevenstars 0.77 (10/13)**: 3 misses (`7S-004985/86/87`), selector timeout, probably delisted pages not yet marked stale. Up from 0.00.
- **synprofs 0.77 (17/22)**: 5 misses (6934, 6937, 6942, 6944, 6949), selector timeout, likely delisted not yet stale (not checked per page). Down from 1.00; E13 had 21/21 with a header that overlapped the text.
- **working_nomads 0.70 (39/56)**: 17 misses, all redirect to the `/jobs` listing (delisted, not yet stale). Up from 0.17.
- **pro_act 0.83 (10/12)**: misses 8721 and 8889, selector timeout; the open-application form page `8681` does have a 850x144 PNG (not a job ad, known).
- **flexvalue 0.85 (11/13)**: unchanged, not touched in this story.
- **ictergezocht 0.00 (0/50)**: `skipped_blocked` 49, skipped on purpose (Cloudflare challenge).
- guru 0.90 (160/177), hero 0.95 (37/39) are at or above target. hero: 2 live misses (`675068ef`, `bd6e26b6`).

`skipped_blocked` on purpose: ictergezocht 49. hero: 0 (gate cannot be selector-skipped).

## 8. URL check and sizes

Hero PNG heights (struct over `screenshots/hero-*.png`): 43 files, **7 are below 100 px high** (640x65: 5 files, 640x97: 2 files, e.g. `hero-13f09263-functioneel-beheerder.png`). These are the old gated-teaser strips from E13 (hero was not re-captured; `--missing-only` skipped 37 existing). No `screenshot_min_height` skip exists yet (E14-S09 idea).

Other small captures: harveynash has 9 PNGs 1116x30 (blank white strip), guru 3 below 100 px (min 52 px, `guru-2120996-digital-ads-management.png`, short teasers) and 15 below 200 px.

## 9. Visual check (PNGs opened with the Read tool)

| site | file | size | verdict |
|---|---|---|---|
| guru | `guru-1728117-market-research-india.png` | 1566x256 (new) | Description text only, no page chrome. Still ends with "... Show more": truncated by design (login link, E14-S08). Known caveat, not a regression. |
| iamexpat | `iamexpat-1dcPoN64gQiAhCsj2tDvhh-account-manager-dutch-amersfoort.png` | 807x1401 | CLEAN. Only "About this role" text. No Apply/Bookmark buttons, no alert signup, no similar jobs, no ad box. FIXED vs E13. |
| pro_act | `pro_act-8884-informatieanalist-ooapi.png` | 850x2032 | CLEAN. Only the ad text; no dimmer, no cookie dialog, no contact form. FIXED vs E13. |
| synprofs | `synprofs-6912-ai-developer.png` | 554x3100 | CLEAN. Ad text only, no sticky header or nav overlapping. FIXED vs E13. |
| harveynash | `harveynash-299093-project-assistent-jp3353.png` | 1116x30 | BAD: a blank white strip with only the ghost of faint text (AOS fade-in captured at opacity ~0). A second file `harveynash-299272-tekenaar-hoogbouw-kolham-16393.png` (761x3487) is CLEAN: full text, legible, no Reageren button, not faded. 9 of 33 harveynash PNGs are 1116x30 blanks. The button fix works; the fade-in is a real problem for about 27 % of captures. |
| circle8 | `circle8-VNR-85579-senior-mobile-qa-test-automation-engineer.png` | 1524x12450 | Description text only, no cookie banner or nav. Very tall (12450 px; the other file is 18488 px) because the description is long and the capture is one tall element. Faint "Sluit overmorgen" pill shadow not noticeable. 2 PNGs total. |
| sevenstars | `sevenstars-7S-004979-projectleider-doorontwikkeling-dwh.png` | 1544x2418 | CLEAN. Description only, no Cookiebot overlay. FIXED vs E13 (0 PNGs before). |
| wearedevelopers | `wearedevelopers-1343363-qa-engineer-manual-automation.png` | 1612x3010 | CLEAN. "Job description" heading plus text, uniform dark navy background (the site's dark theme), light text legible, no consent dialog or tint overlay visible. TrustArc pre-action looks verified for this file (the dark background is not a dimmer: no lighter/darker split). Selector is positional (fragile, see follow-ups). Min height of the 22 files is 304 px, so some short/odd captures exist but none under 100 px. |
| hero | (hero-13f09263-functioneel-beheerder.png, by struct only) | 640x65 | Not opened again; the 7 sub-100 px files are the E13 gated strips (see section 8). |

All required sites have PNGs; none has 0 PNGs. (ictergezocht has 0 PNGs: skipped_blocked.)

## Compared with E13

| site | E13 live ratio | E14 live ratio | change |
|---|---|---|---|
| circle8 | 0.00 | 0.67 | up |
| sevenstars | 0.00 | 0.77 | up |
| wearedevelopers | 0.00 | 0.92 | up |
| working_nomads | 0.17 | 0.70 | up |
| stone_interim | n/a | 1.00 | new |
| iamexpat | 0.92 | 0.95 | up, widgets gone |
| guru | 1.00 | 0.90 | down (17 selector timeouts; old PNGs were moved, so pages that failed now have no PNG) |
| harveynash | 1.00 | 0.97 | down 1 file; 9 captures blank |
| pro_act | 0.92 | 0.83 | down |
| synprofs | 1.00 | 0.77 | down |
| hero | 0.97 | 0.95 | roughly equal |
| freelancermap | 1.00 | 0.95 | 1 new live posting without PNG (3055134) |
| ictergezocht | 0.00 | 0.00 | skipped on purpose |
| flexvalue | 0.85 | 0.85 | unchanged |
| arc_dev, djinni, freelancer_com, tender_link | 1.00 | 1.00, 1.00, 1.00, 0.99 | unchanged (tender_link 231/234, 3 newly live rows without PNG) |

Overall live ratio: E13 842/1051 = 0.80, E14 909/1058 = 0.86.

## Unexpected

- Live ratios for guru, synprofs and pro_act fell because the old PNGs were moved and the fresh capture cannot reach some pages that were captured in E13 (probably delisted since, still `is_stale=0`).
- hero produced one `failed` instead of any `skipped_blocked`; hero tiny gated PNGs from E13 remain.
- Stale count rose from 444 to 449 during the run (working_nomads `newly_stale` 5).

## Follow-ups

- harveynash: 9 of 33 PNGs are 1116x30 blank strips (AOS fade-in captured at opacity 0); add a settle/wait-for-opacity step and re-capture them.
- hero: 7 PNGs below 100 px high remain (gated teasers); add `screenshot_min_height` skip (E14-S09 idea) and remove or re-evaluate those files.
- Detect delisted postings from the detail fetch (404 or redirect to the listing) and mark them stale: causes the circle8 (1), sevenstars (3), working_nomads (17), synprofs (5), pro_act (2), hero (2) misses and the "could not verify human URL" lines.
- guru: 17 new selector timeouts and a few 52 px teasers; "Show more" stays truncated by design (login link).
- circle8: PNGs are 12450 and 18488 px high; consider a max height or accept; 3 live rows only.
- wearedevelopers: selector `section:nth-of-type(3)` is positional; confirm on more PNGs (min 304 px height) and re-check if the layout changes.
- freelancermap `3055134` and tender_link (3 rows): newly live rows without PNG, run `screenshots --missing-only` for them.
- 13 old-URL markdown files remain for stale working_nomads/stone_interim rows (Epic 15).
- working_nomads: 13 screenshot failures during the scrape plus 15 more in the backfill are the same delisted postings.
