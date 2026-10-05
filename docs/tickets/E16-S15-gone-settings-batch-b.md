# E16-S15 — Per-adapter gone settings: sevenstars, synprofs, pro_act, stone_interim

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

Same as E16-S14 for the second batch of adapters with known delisted misses (sevenstars 3, synprofs 5, pro_act 2).

## Context

- Mechanism: see E16-S14 Context. Evidence rule: markers only from saved pages or the owner's recorded QA text; no probes.
- Evidence: grep of `scraper/raw/<site>/` and `scraper/tests/fixtures/<site>/` found no 404/not-found page for synprofs, pro_act, stone_interim, sevenstars. The only evidence is the QA text "Job Not Found" for sevenstars (`docs/todo.md` Epic 14 lines, `docs/e14-qa-results.md`): a marker that cannot fire wrongly, because it is matched against `<title>`/`<h1>` only, so `sevenstars.gone_markers = ("job not found",)` is safe even if the real wording differs (then it simply never matches; note this in the commit body: "marker from owner QA, no saved page").
- Listing paths from the code and fixtures: sevenstars `LISTING_URL = "https://www.sevenstars.nl/opdrachten"` (detail `/opdracht/<slug>_7S-<id>`); synprofs detail `https://www.synprofs.nl/opdracht/<slug>-<id>/` and the landing page canonical `https://www.synprofs.nl/opdrachten/` (fixture `tests/fixtures/synprofs/opdrachten_landing_page_no_listing.html`, title "Toegang tot mooie opdrachten | SynProfs"); pro_act `LISTING_URL = "https://pro-act.nl/vacatures"` (detail `/vacatures/<slug>-<id>/`); stone_interim's detail fetch is the JSON API `https://www.stone-interim.nl/api/v1/WordPress/GetVacancy/<id>` (a delisted vacancy there is an HTTP status/JSON matter, no saved evidence): keep `listing_paths` EMPTY and `gone_markers` EMPTY for stone_interim (generic HTTP rule only) — with an empty `listing_paths` and a listing id inside the API URL, rule 6 of `is_unrelated_redirect` would apply to a redirect with fewer path segments; that is acceptable here and must be pinned by a test.
- Tests: `scraper/tests/test_sevenstars.py`, `test_synprofs.py`, `test_pro_act.py`, `test_stone_interim.py`; add tests at the end of each.

## Files to create/modify

- `scraper/job_scraper/sites/sevenstars.py`, `synprofs.py`, `pro_act.py` (stone_interim.py only if a test needs nothing: it is NOT modified)
- `scraper/tests/test_sevenstars.py`, `test_synprofs.py`, `test_pro_act.py`, `test_stone_interim.py`

## Acceptance criteria

- `sevenstars.listing_paths = ("/opdrachten",)`, `sevenstars.gone_markers = ("job not found",)`; `synprofs.listing_paths = ("/opdrachten",)`; `pro_act.listing_paths = ("/vacatures",)`; stone_interim unchanged (both tuples empty).
- Tests: sevenstars `https://www.sevenstars.nl/opdracht/devops-engineerinfra_7S-004944` -> `https://www.sevenstars.nl/opdrachten` True (id `7S-004944`) and -> same URL lower-case False; `title_has_gone_marker(b"<html><title>Job Not Found | Seven Stars</title></html>", SevenStars.gone_markers)` is not None, and a saved real page (`tests/fixtures/sevenstars/detail_7S-004982.html`) gives None; synprofs `https://www.synprofs.nl/opdracht/iam-specialist-5927/` -> `https://www.synprofs.nl/opdrachten/` True (id `5927`) and the saved detail fixture `detail_6930.html` gives `title_has_gone_marker(..., adapter.gone_markers)` None; pro_act `https://pro-act.nl/vacatures/open-solicitatie-2026-8681/` -> `https://pro-act.nl/vacatures` True; stone_interim: `SiteAdapter` defaults (`listing_paths == ()`, `gone_markers == ()`) are pinned, and `is_unrelated_redirect("https://www.stone-interim.nl/api/v1/WordPress/GetVacancy/4893", "https://www.stone-interim.nl/", "4893", ())` is True while the same request redirecting to `.../GetVacancy/4893/` is False.
- Existing tests in all four files pass unchanged.

## Definition of done

- Run only `uv run pytest tests/test_sevenstars.py tests/test_synprofs.py tests/test_pro_act.py tests/test_stone_interim.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S15: Add gone settings for sevenstars, synprofs, pro_act`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S14 (same pattern; the last code story before the gate).
