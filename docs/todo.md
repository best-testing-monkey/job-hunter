# job-hunter app — todo

Per-resume match tracking, first slice. See `docs/DESIGN_DOC.md` and
`docs/tickets/`. Implementation standards: `docs/tickets/APPENDIX-A-standards.md`.

Independent stories (same "depends on E1 only" set) may run in parallel:
E3-S01, E4-S01, E5-S01 are mutually independent once E1-S01 is done.
E2-S01 is also independent of those three but gates E6-S01/E6-S03 (need the
base template). Keep parallel subagent batches to 2 at a time.

## Epic 1 — Scaffolding

- [x] E1-S01 Scaffold the Flask app project (docs/tickets/E1-S01-scaffold-flask-app.md)

## Epic 2 — Visual shell

- [x] E2-S01 Dark-only base template and stylesheet (docs/tickets/E2-S01-base-template-and-theme.md)

## Epic 3 — Data layer

- [x] E3-S01 SQLite schema and connection helper (docs/tickets/E3-S01-sqlite-schema.md)
- [x] E3-S02 Resume registration and match upsert queries (docs/tickets/E3-S02-resume-and-match-queries.md)

## Epic 4 — Job metadata reuse

- [x] E4-S01 Job metadata wrapper reusing build_report.py (docs/tickets/E4-S01-job-metadata-wrapper.md)

## Epic 5 — Matching engine

- [x] E5-S01 Matcher subprocess wrapper (docs/tickets/E5-S01-matcher-subprocess-wrapper.md)

## Epic 6 — Routes

- [x] E6-S01 Resume list page (docs/tickets/E6-S01-resume-list-page.md)
- [x] E6-S02 Register a resume (docs/tickets/E6-S02-register-resume.md)
- [x] E6-S03 Resume match list page (docs/tickets/E6-S03-resume-match-list-page.md)
- [x] E6-S04 Trigger a rematch (docs/tickets/E6-S04-trigger-rematch.md)

## Epic 7 — Resume CRUD

All four stories touch `app/webapp/routes.py` and/or the same templates —
run sequentially, not in parallel (E7-S01 is the exception: it only touches
`db.py`/`__init__.py`, so it could in principle pair with something else,
but there's nothing else pending right now).

- [x] E7-S01 Add content column and resume CRUD db functions (docs/tickets/E7-S01-resume-crud-db-functions.md)
- [x] E7-S02 Switch resume creation to content-based, remove register_resume (docs/tickets/E7-S02-content-based-create.md)
- [x] E7-S03 Edit a resume (docs/tickets/E7-S03-edit-resume.md)
- [x] E7-S04 Delete a resume (docs/tickets/E7-S04-delete-resume.md)

## Epic 8 — Match status, job_posted, rematch-running state

Sequential (both touch `db.py`; E8-S02 also touches `routes.py`). Can start
in parallel with Epic 9's first story (disjoint files).

- [x] E8-S01 Add match status, job_posted column, and match lookup functions (docs/tickets/E8-S01-match-status-and-posted-date.md)
- [x] E8-S02 Track rematch-running state and expose a status endpoint (docs/tickets/E8-S02-rematch-running-state.md)

## Epic 9 — Homepage dashboard

E9-S01 is new files only (`app.js`, `base.html`, `style.css`) — can run in
parallel with E8-S01. E9-S02 depends on both E8-S01/E8-S02 and E9-S01, and
touches `routes.py` — sequential after those.

- [x] E9-S01 Add app.js foundation (threshold slider, table sort, rematch polling) (docs/tickets/E9-S01-app-js-foundation.md)
- [x] E9-S02 Rebuild homepage as a sortable dashboard with threshold filtering (docs/tickets/E9-S02-homepage-dashboard.md)

## Epic 10 — Resume detail page redesign

E10-S01 only touches `resume_detail.html` — can run in parallel with
Epic 8/9 work. E10-S02 depends on E8-S01, E9-S01, and E10-S01, and touches
`routes.py` — sequential after those.

- [x] E10-S01 Style the resume metadata section on the detail page (docs/tickets/E10-S01-resume-metadata-table.md)
- [x] E10-S02 Add sortable, threshold-filtered match table with status workflow (docs/tickets/E10-S02-sortable-matches-with-status.md)

## Epic 11 — Job detail page

Depends on E8-S01, touches `routes.py` — sequential relative to the other
`routes.py`-touching stories above.

- [x] E11-S01 Add job detail page (docs/tickets/E11-S01-job-detail-page.md)

## Epic 12 — Remaining usability QA fixes

E12-S01 and E12-S02 are sequential (same templates). E12-S03 only touches
`__init__.py` and a new template — can run in parallel with anything that
doesn't also touch `__init__.py` (nothing else in this batch does).

- [x] E12-S01 Reject blank/whitespace resume name or content; create redirects to the new resume (docs/tickets/E12-S01-resume-form-validation.md)
- [x] E12-S02 Style the New/Edit resume forms and size the content textarea (docs/tickets/E12-S02-style-resume-forms.md)
- [x] E12-S03 Add a dark-themed 404 error page (docs/tickets/E12-S03-styled-404-page.md)

## Epic 13 — Scraper quality: readable descriptions, correct links, screenshots

**GOAL (set 2026-10-02):** complete E13-S02..S35 via `/run-stories` with cheap subagents, one story at a time.
Rules: story agents run ONLY the tests applicable to their change (never the full suite).
Full-suite gates run by a SEPARATE fix-it subagent after S12, after S19 and after S34 (scraper: `uv run pytest` in scraper/; app: `uv run pytest tests/ -q` in app/), fixing failures and committing in the right repo.
Follow-up (cleanup, after S12 gate): freelancer_com.py uses a `\x00AMP\x00` placeholder hack because `html_to_markdown` treats any `&` as HTML; replace with a `plain=True` option on the helper.
DECIDED (owner, closed): headfirst keeps the shared `/vind-opdrachten` overview as `source_url`; the external striive.com brokerUrl stays only as `apply_url`. No code change (E13-S17's test already pins the overview URL). Found in S17.
NOTE (S18): pro_act posting `pro_act-8681-open-sollicitatie-2026` is an open-application form, not a job ad — probably should be excluded by the scrape filters; not fixed.
NOTE (S19): tender_link stored URL is a human ad page that 301-redirects to a longer SEO-slug canonical; works for users, left as is.
FOLLOW-UP (S28): pro_act has NO screenshot_selector (BLOCKED: apply form `div.contact-info` is a sibling of the ad text inside `div.content-wrapper`); hero is a gated/blurred teaser (live QA in S35). Idea: add an optional `screenshot_hide_selectors` adapter attribute (elements hidden via JS before the element screenshot) to unblock pro_act and clean up cookie banners/forms generally.
LIVE-QA FLAGS (S29, check in S35): stone_interim selector BLOCKED (saved page is a client-rendered shell; find selector on the live page); harveynash `div.post-content` also holds a "Reageren" button + share icons; working_nomads uses `div.jd-desktop div.jd-description` (page renders description twice; viewport is 1280px wide in capture_element so desktop copy is visible).
LIVE-QA FLAGS (S30): iamexpat selector is a hashed CSS-module class `div.BodyCenter_main__Sz_2E` (no stable wrapper; also captures alert signup/Similar jobs/Apply buttons; may break on site rebuild); sevenstars + circle8 show a Cookiebot overlay that must be dismissed/hidden before the element shot.
LIVE-QA FLAGS (S31): guru element is truncated in saved HTML ("... Show more") — full text may need a live click/expand; arc_dev check tab visibility live; no overlays seen in saved HTML for arc_dev/freelancer_com/freelancermap/guru.
LIVE-QA FLAGS (S32): ictergezocht fixture has CookieYes overlay `#cookieyes-banner`; all 50 raw ictergezocht pages are Cloudflare challenge pages (only 1 fixture verifiable); wearedevelopers selector uses `:has()` (needs Chromium>=105, fine); headfirst + planet_interim intentionally None (no description scraped).
STORY ADDED: E13-S36 (overlay/form hiding) runs after S32, before gate 3 + S33/S34.
Gates done: GATE-1 (after S12), GATE-2 (after S19), GATE-3 (after S34, scraper 424x2 / app 94). Only S35 (live re-scrape) remains.
Status log: tick each story here as it lands; gates done so far: (none)

Scraper stories follow `docs/tickets/APPENDIX-A-standards.md` plus `docs/tickets/APPENDIX-B-scraper-standards.md`; app stories follow Appendix A only. The scraper stories touch the same adapter files several times (description, source URL, selector): run them one at a time, in the order listed. Keep any parallel subagent batch to 2 at a time, and only across scraper/app (never two scraper stories together).

### Part 0 — Preserve existing scraper work

E13-S01 must run first and needs the owner's attention: `scraper/` has a large UNCOMMITTED diff (47 modified files) that every later story builds on. Inspect it, ask if anything looks off, never discard.

- [x] E13-S01 Inspect and commit/preserve the uncommitted scraper changes first (scraper repo) (docs/tickets/E13-S01-commit-existing-scraper-changes.md)

### Part 1 — Readable descriptions (scraper)

S02 first; S03-S08 each touch different adapter files (+ their test files) but all touch the same adapters again in Parts 2 and 3 — run the whole epic's scraper stories sequentially, never two at once. S09 -> S10 (both end up editing `cli.py`, as do S25 and S27).

- [x] E13-S02 Add the shared `html_to_markdown` helper (core, unit-tested with fixtures) (docs/tickets/E13-S02-html-to-markdown-helper.md)
- [x] E13-S03 Migrate arc_dev, pro_act, synprofs descriptions to html_to_markdown (docs/tickets/E13-S03-descriptions-batch-a.md)
- [x] E13-S04 Migrate djinni, circle8, sevenstars descriptions to html_to_markdown (docs/tickets/E13-S04-descriptions-batch-b.md)
- [x] E13-S05 Migrate harveynash, tender_link, stone_interim, working_nomads descriptions to html_to_markdown (docs/tickets/E13-S05-descriptions-batch-c.md)
- [x] E13-S06 Migrate freelancer_com, freelancermap, hero descriptions to html_to_markdown (docs/tickets/E13-S06-descriptions-batch-d.md)
- [x] E13-S07 Migrate iamexpat, ictergezocht, wearedevelopers descriptions to html_to_markdown (docs/tickets/E13-S07-descriptions-batch-e.md)
- [x] E13-S08 Migrate flexvalue and guru descriptions to html_to_markdown (docs/tickets/E13-S08-descriptions-batch-f.md)
- [x] E13-S09 Add `core/rebuild.py`: regenerate jobs/*.md and DB rows from raw/ without network (docs/tickets/E13-S09-rebuild-from-raw-module.md)
- [x] E13-S10 Add the `rebuild --site X` CLI subcommand (regenerate markdown from raw/, no network) (docs/tickets/E13-S10-rebuild-cli.md)

### Part 1 — Readable descriptions (app)

Independent of the scraper stories (touches only `app/`, can run any time), but S11 -> S12 are sequential (`routes.py`/template are touched again by S33/S34).

- [x] E13-S11 App: add `markdown` dependency and `render_description_html` (escaped, sanitized); fix description extraction for `###` headings (docs/tickets/E13-S11-app-render-description-markdown.md)
- [x] E13-S12 App: render the description as styled Markdown on the job detail page (dark theme) (docs/tickets/E13-S12-app-job-detail-markdown-view.md)

### Part 2 — Correct source URLs

S13 and S14 re-edit `working_nomads.py` / `stone_interim.py` (also touched by S05 and S29): run after S05. S16-S19 re-edit adapters touched by S03-S08.

- [x] E13-S13 working_nomads: store the human ad URL, not the /job/go/<id>/ redirect (docs/tickets/E13-S13-working-nomads-source-url.md)
- [x] E13-S14 stone_interim: store the human ad URL, not the GetVacancy API endpoint (docs/tickets/E13-S14-stone-interim-source-url.md)
- [x] E13-S15 flexvalue: investigate whether aanvragen.flexvalue.nl job URLs are application pages; fix or lock in (docs/tickets/E13-S15-flexvalue-source-url-investigation.md)
- [x] E13-S16 Audit source URLs: arc_dev, circle8, djinni, freelancer_com (docs/tickets/E13-S16-source-url-audit-a.md)
- [x] E13-S17 Audit source URLs: freelancermap, guru, harveynash, headfirst (docs/tickets/E13-S17-source-url-audit-b.md)
- [x] E13-S18 Audit source URLs: hero, iamexpat, ictergezocht, planet_interim, pro_act (docs/tickets/E13-S18-source-url-audit-c.md)
- [x] E13-S19 Audit source URLs: sevenstars, synprofs, tender_link, wearedevelopers (docs/tickets/E13-S19-source-url-audit-d.md)

### Part 3 — Screenshots (scraper)

S20 -> S22 -> S23 -> S24 -> S25 -> S26 -> S27 are a chain (S21 is independent of S20-S23 but must precede S24 and S28+). Selector batches S28-S32 need S21 only but should run after the URL stories (they also edit the same adapters). `pipeline.py`: S24; `markdown_export.py`: S23; `cli.py`: S25/S27 (after S10).

- [x] E13-S20 Declare `playwright` (and `patchright`) as direct deps; verify a browser is available; document findings (docs/tickets/E13-S20-playwright-dependency-and-browser-findings.md)
- [x] E13-S21 Add optional `screenshot_selector` ClassVar to `SiteAdapter` (docs/tickets/E13-S21-adapter-screenshot-selector-attribute.md)
- [x] E13-S22 Add `core/screenshots.py`: `capture_element` (element-only PNG, never raises) and `browser_available` (docs/tickets/E13-S22-capture-element-screenshot.md)
- [x] E13-S23 markdown_export: optional `- Screenshot:` bullet and `set_screenshot_line` helper (docs/tickets/E13-S23-markdown-screenshot-line.md)
- [x] E13-S24 pipeline: capture a screenshot for each newly written job (failures never fail the scrape) (docs/tickets/E13-S24-pipeline-capture-screenshots.md)
- [x] E13-S25 CLI: `--screenshots-dir` / `--no-screenshots` on `scrape`; git-ignore `screenshots/` (docs/tickets/E13-S25-cli-scrape-screenshot-flags.md)
- [x] E13-S26 Add `core/screenshot_backfill.py`: capture screenshots for existing jobs/*.md (docs/tickets/E13-S26-screenshot-backfill-module.md)
- [x] E13-S27 CLI: `screenshots --site X [--missing-only]` backfill command (docs/tickets/E13-S27-screenshots-cli.md)
- [x] E13-S28 Screenshot selectors: pro_act, hero, flexvalue, synprofs (docs/tickets/E13-S28-selectors-batch-a.md)
- [x] E13-S29 Screenshot selectors: stone_interim, tender_link, harveynash, working_nomads (docs/tickets/E13-S29-selectors-batch-b.md)
- [x] E13-S30 Screenshot selectors: sevenstars, circle8, iamexpat, djinni (docs/tickets/E13-S30-selectors-batch-c.md)
- [x] E13-S31 Screenshot selectors: arc_dev, freelancer_com, freelancermap, guru (docs/tickets/E13-S31-selectors-batch-d.md)
- [x] E13-S32 Screenshot selectors: ictergezocht, wearedevelopers, headfirst, planet_interim (docs/tickets/E13-S32-selectors-batch-e.md)
- [x] E13-S36 Hide cookie overlays/apply forms before element screenshots (`screenshot_hide_selectors`); unblocks pro_act (docs/tickets/E13-S36-hide-overlays-before-screenshot.md)

### Part 3 — Screenshots (app)

S33 -> S34, after S12 (same `routes.py`/template/CSS). Independent of the scraper stories (they only read `scraper/screenshots/*.png` if present).

- [x] E13-S33 App: `GET /jobs/<id>/screenshot` serves the job's PNG safely (404 if missing) (docs/tickets/E13-S33-app-serve-screenshots.md)
- [x] E13-S34 App: collapsible screenshot section on job_detail.html (hidden when missing) (docs/tickets/E13-S34-app-show-screenshot.md)

### Part 4 — Full re-scrape and QA

Last. Live network, long-running; the only story that writes `scraper/jobs/`, `raw/`, `scraper.db`, `screenshots/`.

- [x] E13-S35 Full re-scrape + `screenshots --missing-only` backfill + verification runbook (live network) (docs/tickets/E13-S35-full-rescrape-and-qa-runbook.md)

### Scraper repo note

`scraper/` is a separate git repository with its own history. Epic 13 tickets that change code, tests, fixtures or `scraper/README.md` are committed in the SCRAPER repo (`git -C scraper commit`, message `E13-S<nn>: ...`). Tickets that change `app/` and everything under `docs/` (including ticking items in this file) are committed in the JOB-HUNTER repo. Generated outputs in `scraper/` (`jobs/`, `raw/`, `scraper.db`, `screenshots/`) are git-ignored and never committed. Story E13-S01 first commits the large pre-existing uncommitted scraper work; E13-S35 is the only one that writes the generated directories.

## Epic 14 — Screenshot quality fixes (follow-up round after the Epic 13 QA)

**GOAL (set 2026-10-05):** complete E14-S01..S18 via `/run-stories` with cheap subagents, one story at a time. Derived only from the Follow-ups in `docs/e13-qa-results.md`; owner decision: "do a follow-up round, with 15 or so small per-site fixes".
Rules: story agents run ONLY the tests applicable to their change (never the full suite). Standards: `docs/tickets/APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and the new `APPENDIX-C-screenshot-fix-standards.md` (probe protocol: ONE headless live probe per site from the session scratchpad, then the fix, then a fixture-based unit test; browser tests are `enable_socket` + `file://` only; no Cloudflare/bot-wall bypass, `--ignore-robots` never).
GATE-4 (full suites by a SEPARATE fix-it subagent: `uv run pytest` in `scraper/`, `uv run pytest tests/ -q` in `app/`; fix failures, commit in the right repo): after E14-S17 (the last code story).
E14-S18 is a live-network QA story: it already has the owner's OK in the Epic 13 style, but ask before running if it will take more than 1 hour or is heavy (13 GB RAM machine); follow Appendix C safety rules (backup first, one heavy process at a time, polite delays, owner's app on port 5000 untouched, own app on 5001).
Same-file chains (strictly sequential, and never two scraper stories at once): `screenshots.py` S01 -> S02 -> S13; `pipeline.py` S03 -> S06 -> S07 (and Epic 15 S03 later); `screenshot_backfill.py` S04 -> S05; `cli.py` S05 -> S06; `test_screenshots.py` S01, S02, S08, S13; `base.py` S01 -> S02; `markdown_export.py` S07.
Decisions: backfill skips stale postings by reading `scraper.db` (`is_stale = 1`) read-only in E14-S05 (no dependency on Epic 15); `capture_element` returns True/False/None where None = skipped on purpose (gated teaser or Cloudflare challenge, counted as `skipped_blocked`/`screenshots_skipped`, never as failure); the URL-check false-positive (`freelancer.com /projects/api/`) is handled in the improved query in E14-S18.
Scraper repo note: every story except S18 commits in the SCRAPER repo (`git -C scraper commit`, message `E14-S<nn>: ...`); S18 writes only `docs/` (JOB-HUNTER repo).

### Part 1 — Shared mechanisms

- [ ] E14-S01 Add optional `screenshot_pre_actions` (click selectors before capture) to `SiteAdapter` and `capture_element` (docs/tickets/E14-S01-screenshot-pre-actions-mechanism.md)
- [ ] E14-S02 `capture_element` returns None for gated teasers and Cloudflare challenge pages (`screenshot_skip_selectors`, `_is_challenge`) (docs/tickets/E14-S02-capture-skip-gated-and-challenge-pages.md)
- [ ] E14-S03 pipeline: pass pre-actions/skip selectors, count `screenshots_skipped` (docs/tickets/E14-S03-pipeline-pass-new-capture-options.md)
- [ ] E14-S04 backfill: pass pre-actions/skip selectors, count `skipped_blocked` (docs/tickets/E14-S04-backfill-pass-new-capture-options.md)
- [ ] E14-S05 backfill skips postings marked `is_stale = 1` in scraper.db (`--db`, `--include-stale`) (docs/tickets/E14-S05-backfill-skip-stale-postings.md)
- [ ] E14-S06 scrape crash safety: per-site exceptions caught, counters printed incrementally (docs/tickets/E14-S06-scrape-crash-safety.md)
- [ ] E14-S07 pipeline rewrites the markdown when the Source URL changed although the content hash did not (docs/tickets/E14-S07-rewrite-markdown-when-source-url-changes.md)

### Part 2 — Per-site fixes

Each story needs the shared stories it names. Each edits only its own adapter + test file (plus fixtures), except S08 (also `test_screenshots.py`) and S13 (also `screenshots.py`/`test_screenshots.py`).

- [ ] E14-S08 guru: click "Show more" before capture (needs S01, S03, S04) (docs/tickets/E14-S08-guru-expand-show-more.md)
- [ ] E14-S09 hero: detect the gated teaser and skip (needs S02-S04) (docs/tickets/E14-S09-hero-skip-gated-teaser.md)
- [ ] E14-S10 ictergezocht: skip Cloudflare challenge pages cleanly, no bypass; README note (needs S02-S04) (docs/tickets/E14-S10-ictergezocht-skip-cloudflare-challenge.md)
- [ ] E14-S11 circle8 + sevenstars: diagnose why Cookiebot still blocks (live probe), fix selector/hide list (docs/tickets/E14-S11-cookiebot-circle8-sevenstars.md)
- [ ] E14-S12 wearedevelopers: replace the `:has()` selector with a stable one (docs/tickets/E14-S12-wearedevelopers-stable-selector.md)
- [ ] E14-S13 iamexpat: narrower wrapper, hide extra widgets, retry on "not attached" (after S01/S02: same `screenshots.py`) (docs/tickets/E14-S13-iamexpat-narrow-wrapper-and-retry.md)
- [ ] E14-S14 pro_act: hide the cookie consent dialog and dimmer (docs/tickets/E14-S14-pro-act-hide-consent-dialog.md)
- [ ] E14-S15 synprofs: hide the sticky header (docs/tickets/E14-S15-synprofs-hide-sticky-header.md)
- [ ] E14-S16 harveynash: hide the Reageren button, check the faded text (docs/tickets/E14-S16-harveynash-hide-reageren-button.md)
- [ ] E14-S17 stone_interim: find a live selector with a probe or document BLOCKED (docs/tickets/E14-S17-stone-interim-live-selector.md)
- [ ] GATE-4 full-suite gate agent (scraper + app) after E14-S17

### Part 3 — QA

- [ ] E14-S18 Re-run screenshots for the fixed sites, visual check of 8 PNGs, counts, record `docs/e14-qa-results.md` (live network) (docs/tickets/E14-S18-rerun-qa-and-record-results.md)

## Epic 15 — Stale (delisted) postings

**GOAL (set 2026-10-05):** complete E15-S01..S10 via `/run-stories` with cheap subagents, one story at a time. Owner decision: "Delisted postings: give those status 'stale'. Stale does not count for the main page as a match and shows in the resume detail page as a dark gray non-responsive row for 2 days. After 2 stale days the job is completely hidden."
Rules: story agents run ONLY the tests applicable to their change (never the full suite). Scraper stories follow Appendix A + B; app stories follow Appendix A only.
GATE-5 (full suites by a SEPARATE fix-it subagent, `scraper/` and `app/`): after E15-S09 (the last code story). E15-S10 is offline QA (no network); it only uses scratchpad copies and an own app instance on port 5001 with a scratch DB (never `app/instance/matches.db`, never the owner's port 5000).

Design (verified against the code; every story encodes it):
- Single interface stays the job markdown. The scraper already marks delisted postings `jobs.is_stale = 1` in `scraper.db`, but stores NO date, and `mark_stale_not_seen_since` re-marks stale rows on every run. E15-S02 adds `stale_since TEXT` (set once with COALESCE, cleared on upsert); the pipeline (S03) writes the bullet `- Stale since: YYYY-MM-DD` (local date) into the markdown when a posting newly goes stale, never resets it, and removes it when the posting is seen live again. `rebuild` (S04) keeps it (a rebuild used to silently un-stale rows via `upsert`); `stale-sync` (S05) backfills/repairs from `scraper.db` and dates undated stale rows with the day it runs (no real marking date exists).
- The app never reads `scraper.db`. `webapp/jobs.py` reads the bullet itself (`resume-matcher/build_report.py` must not be edited): `read_stale_since`, `parse_job_file` gains `stale_since`, `stale_state(stale_since, today=None)`: days = today - since; 0..2 -> `stale` (inclusive of day 2; future dates also stale), 3 or more (strictly more than 2 full days) -> `hidden`, no date -> `live`; a missing job file counts as `live`.
- Main page `/` (S07): only `live` matches in `resume-match-data` (stale and hidden excluded from counts, stats, threshold data).
- Resume detail (S08): live rows as before; `stale` rows in a second `<tbody class="stale-rows">` (always sorted last, since `makeSortable` only reorders the first tbody; the threshold slider still filters them), dark gray `.stale-row`, `aria-disabled="true"`, no link, no status form/select, badge "stale since <date>", user status (e.g. Applied) shown as plain text; `hidden` omitted. No `app.js` change.
- Hidden jobs (S09): omitted everywhere; job detail, its screenshot and the status endpoint return 404 via the existing styled 404. Stale jobs (0-2 days): job detail still opens (200, read-only) with a "Delisted on <date>" notice; screenshot route serves; status POST returns 409. A stale job the user marked Applied follows the same 2-day rule; persisted match rows are never modified.
- No blocker found. Ambiguities resolved: undated stale rows get today's date at first `stale-sync`; `rebuild` revival bug fixed in S04; rematch still stores matches for stale/hidden files (state is evaluated at read time).
Same-file chains (strictly sequential): scraper `pipeline.py` (Epic 14 S03/S06/S07, then E15-S03), `cli.py` (E14-S05/S06, then E15-S05), `markdown_export.py` (E14-S07, then E15-S01), `db.py` (E15-S02); app `routes.py` and `test_routes.py` S07 -> S08 -> S09; `style.css` S08 -> S09; `jobs.py`/`test_jobs.py` S06. Never run two scraper stories at once; one scraper and one app story may run in parallel when they share no files. Epic 15 starts after Epic 14's last code story (shared scraper files); the app stories S06-S09 may run earlier.
Scraper repo note: S01-S05 commit in the SCRAPER repo (`E15-S<nn>: ...`); S06-S10 and `docs/` commit in the JOB-HUNTER repo.

### Part 1 — Scraper (writes and keeps the bullet)

- [x] E15-S01 markdown_export: optional `- Stale since:` bullet, `set_stale_line`, `md_path_for` (docs/tickets/E15-S01-scraper-stale-since-markdown-bullet.md)
- [x] E15-S02 scraper.db: `stale_since` column + migration, `list_newly_stale`, stale-state helpers (docs/tickets/E15-S02-scraper-db-stale-since-column.md)
- [x] E15-S03 pipeline: set the bullet when a posting goes stale (once), clear it when seen live again (docs/tickets/E15-S03-scraper-pipeline-set-and-clear-stale-since.md)
- [x] E15-S03b Fix `find_duplicate` self-matches and repair 703 self-duplicate rows in scraper.db (docs/tickets/E15-S03b-fix-self-duplicates.md) — found during S03; explains why re-scrapes skipped most postings
- [x] E15-S04 rebuild keeps stale state and bullet (docs/tickets/E15-S04-scraper-rebuild-keeps-stale-state.md)
- [x] E15-S05 `stale-sync` command to backfill/repair bullets from scraper.db (docs/tickets/E15-S05-scraper-stale-sync-command.md)

### Part 2 — App

- [x] E15-S06 app: read `stale_since`, `stale_state` helper (docs/tickets/E15-S06-app-parse-stale-since-and-stale-state.md)
- [x] E15-S07 app: resume list page counts only live matches (docs/tickets/E15-S07-app-resume-list-excludes-stale.md)
- [x] E15-S08 app: resume detail shows stale matches as dark-gray non-responsive rows, hides expired ones (docs/tickets/E15-S08-app-resume-detail-stale-rows.md)
- [ ] E15-S09 app: job detail notice for stale, 404 for hidden (detail, screenshot, status) (docs/tickets/E15-S09-app-job-detail-stale-and-hidden-404.md)
- [ ] GATE-5 full-suite gate agent (scraper + app) after E15-S09

### Part 3 — QA

- [ ] E15-S10 Drive the real app on port 5001 with stale fixtures (0/1/2/3 days), `stale-sync` on copies, record `docs/e15-qa-results.md` (docs/tickets/E15-S10-qa-and-record-results.md)
