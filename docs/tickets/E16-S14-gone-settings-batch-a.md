# E16-S14 — Per-adapter gone settings: working_nomads, circle8, hero, harveynash

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

Each adapter declares the listing/landing paths a delisted posting redirects to, and soft-404 markers only where saved evidence exists; every other detection relies on the generic HTTP 404/410 rule (E16-S09).

## Context

- Mechanism: `SiteAdapter.listing_paths` and `gone_markers` (E16-S09), `is_unrelated_redirect` rules in `scraper/job_scraper/core/gone.py` (E16-S08): a final path of `/` or one of `listing_paths` (segment-boundary suffix) after a redirect on the same host means "gone".
- Evidence (offline only, no probes; `pytest` runs with `--disable-socket`): the grep of every saved page in `scraper/raw/<site>/` and `scraper/tests/fixtures/<site>/` for 404/not-found/niet-gevonden titles or `<h1>` found NONE for these four sites (the scraper only keeps pages it parsed), so `gone_markers` stay EMPTY for all four; only the owner's QA observations (`docs/e14-qa-results.md` sections 3, 5 and Follow-ups) show the behaviour: working_nomads redirects to the `/jobs` listing, circle8 and harveynash answer 404 pages (generic rule). Say "no saved evidence; generic HTTP rule only" in the commit body for circle8 and harveynash.
- Listing URLs read from the code: `working_nomads.py` human URLs are `https://www.workingnomads.com/jobs/<slug>` (index `/jobs`; detail fetch URL is `/job/go/<id>/`, which serves the site's own page, so the canonical `/jobs/<slug>` is NOT a gone redirect); `circle8.py` `LISTING_URL = "https://www.circle8.nl/opdrachten"` (detail `/opdracht/<slug>_VNR-<id>`); `hero.py` `LISTING_URL = "https://hero.eu/interim-opdrachten"` (detail `/interim-opdrachten/<slug>-<id>`, the id is inside the URL); `harveynash.py` detail `https://www.harveynash.nl/vacatures/<id>-<slug>` (index `/vacatures`; the listing source is a sitemap).
- Tests: one existing file per adapter (`scraper/tests/test_working_nomads.py`, `test_circle8.py`, `test_hero.py`, `test_harveynash.py`); add the new tests at the end of each, no fixture changes.

## Files to create/modify

- `scraper/job_scraper/sites/working_nomads.py`, `circle8.py`, `hero.py`, `harveynash.py`
- `scraper/tests/test_working_nomads.py`, `test_circle8.py`, `test_hero.py`, `test_harveynash.py`

## Acceptance criteria

- `working_nomads.listing_paths = ("/jobs",)`; `circle8.listing_paths = ("/opdrachten",)`; `hero.listing_paths = ("/interim-opdrachten",)`; `harveynash.listing_paths = ("/vacatures",)`; `gone_markers` untouched (empty) in all four.
- Per adapter, one test using `is_unrelated_redirect` with the adapter's own attributes and a real URL pair: working_nomads `https://www.workingnomads.com/job/go/1843253/` -> `https://www.workingnomads.com/jobs` True, -> `https://www.workingnomads.com/jobs/senior-python-developer-acme` False; circle8 `https://www.circle8.nl/opdracht/backstage-engineers-(medior%2C-senior-%26-technical-lead)_VNR-85376` -> `https://www.circle8.nl/opdrachten` True, -> the same URL with a trailing slash False; hero `https://hero.eu/interim-opdrachten/lead-developer-solution-architect-04489d5d` -> `https://hero.eu/interim-opdrachten` True and -> `https://hero.eu/` True; harveynash `https://www.harveynash.nl/vacatures/299060-Commissioning-supervisor---WarmtelinQ-project-JP3351` -> `https://www.harveynash.nl/vacatures` True and -> `.../vacatures/299060-commissioning-supervisor-warmtelinq-project-jp3351` False. Use the listing ids `1843253`, `VNR-85376`, `04489d5d`, `299060` as `listing_id`.
- Each adapter's existing tests still pass unchanged.

## Definition of done

- Run only `uv run pytest tests/test_working_nomads.py tests/test_circle8.py tests/test_hero.py tests/test_harveynash.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S14: Add gone settings for working_nomads, circle8, hero, harveynash` with the body lines `working_nomads: listing_paths /jobs` etc. and the no-evidence note.
- The orchestrator ticks `docs/todo.md`. Needs E16-S09; never in parallel with another scraper story.
