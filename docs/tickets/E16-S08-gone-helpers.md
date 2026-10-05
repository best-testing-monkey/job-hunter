# E16-S08 — `core/gone.py`: pure delisted-page detection helpers

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

One pure, network-free module decides whether a fetched page means "this posting is gone": HTTP 404/410, a redirect to an unrelated page, or a soft-404 title. Both the detail fetch (E16-S09) and the screenshot capture (E16-S12) reuse it.

## Context

- Evidence (`docs/e14-qa-results.md`): delisted postings answer a 404 page (circle8, harveynash, working_nomads), redirect to the `/jobs` listing (working_nomads: the 17 misses and the 15 "could not verify human URL" lines), show "Job Not Found" (sevenstars) or HTTP 410 "Content Deleted" (guru).
- Scrapling responses (`scraper/.venv/lib/python3.13/site-packages/scrapling/engines/toolbelt/custom.py`, `convertor.py`): `Fetcher.get(url)` and `StealthyFetcher.fetch(url)` return a `Response` with `.status` (int), `.url` (the FINAL url after redirects: `response.url` for curl_cffi, `page.url` for the browser) and `.body` (bytes). A 404 does NOT raise; the 404 body is returned like any page. So status and final URL are readable at no extra cost.
- Real detail URLs (jobs `- Source:` lines): `https://www.synprofs.nl/opdracht/iam-specialist-5927/`, `https://www.sevenstars.nl/opdracht/devops-engineerinfra_7S-004944`, `https://hero.eu/interim-opdrachten/lead-developer-solution-architect-04489d5d`, `https://www.harveynash.nl/vacatures/299060-Commissioning-supervisor---WarmtelinQ-project-JP3351`, working_nomads detail fetch URL `https://www.workingnomads.com/job/go/1843253/` (serves the site's own page whose canonical is `/jobs/<slug-without-id>`).
- No scrapling or network import in this module (so tests stay trivial under `--disable-socket`).

## Files to create/modify

- `scraper/job_scraper/core/gone.py` (new)
- `scraper/tests/test_gone.py` (new)

## Acceptance criteria

- `@dataclass(frozen=True) class GoneCheck`: `listing_id: str = ""`, `listing_paths: tuple[str, ...] = ()`, `gone_markers: tuple[str, ...] = ()`.
- `is_unrelated_redirect(requested_url, final_url, listing_id="", listing_paths=()) -> bool` (pure). Normalise both URLs: lower-case host without a leading `www.`, scheme ignored, query and fragment ignored, path URL-decoded with trailing slashes stripped (empty path = `/`). Rules, in order: (1) same host+path -> False; (2) different host -> False (a redirect off-site is ambiguous, never treated as gone: FEASIBILITY NOTE, deliberate refinement); (3) `listing_id` non-empty and contained, case-insensitively, in the final path -> False; (4) final path is `/` -> True; (5) final path equals one of `listing_paths` or ends with it on a segment boundary (`/nl` + `/opdrachten`) -> True; (6) only when `listing_paths` is empty AND `listing_id` is non-empty: final path has strictly fewer non-empty segments than the requested path -> True; else False. (Rule 6 is restricted because on sites whose canonical URL has a shorter slug path than the fetch URL, e.g. working_nomads `/job/go/<id>/` -> `/jobs/<slug>`, a bare "shorter" rule would mark live postings gone.)
- `title_has_gone_marker(body: bytes | str, markers: Sequence[str]) -> str | None`: decodes bytes as UTF-8 with `errors="ignore"`, only the first 300000 characters, extracts the text of `<title>` and every `<h1>` with a regex (tags stripped, whitespace collapsed), returns the first marker found case-insensitively in any of them, else None; body text outside title/h1 is never searched; empty markers -> None.
- `gone_reason(status: int | None, requested_url: str, final_url: str | None, body: bytes | str | None, check: GoneCheck) -> str | None`: returns `"http 404"`/`"http 410"` for those statuses; `"redirect to <final path>"` when `final_url` is given and `is_unrelated_redirect(...)` is True using `check.listing_id`/`check.listing_paths`; `"marker '<m>'"` from `title_has_gone_marker` (only if `body` is not None); else None. Any other status (200, 403, 500, None) alone never counts as gone.
- Tests (pure, no network): table-driven `is_unrelated_redirect` cases from the real URLs above: `/opdracht/iam-specialist-5927/` -> `/opdrachten` True; same URL with trailing slash/`?utm=1`/`http://`/`www` differences False; working_nomads `https://www.workingnomads.com/job/go/1843253/` -> `https://www.workingnomads.com/jobs/some-short-slug` is False when `listing_paths=("/jobs",)` (final path is not `/jobs` itself) and True when `listing_paths=()` with `listing_id="1843253"` (3 segments -> 2): two separately named tests documenting why working_nomads must declare `listing_paths` (E16-S14); `/jobs` with `listing_paths=("/jobs",)` True; `/` True; off-site host False; final path containing id (case-insensitive) False; `/nl/opdrachten` with `("/opdrachten",)` True; `/opdrachten-extra` with `("/opdrachten",)` False. `title_has_gone_marker`: marker in `<title>`, in `<h1>`, only in body text -> None, bytes with invalid UTF-8, case-insensitivity. `gone_reason`: 404, 410, 200+clean -> None, 200+unrelated redirect, 403 -> None.

## Definition of done

- Run only `uv run pytest tests/test_gone.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S08: Add pure delisted-page detection helpers`.
- The orchestrator ticks `docs/todo.md`. Independent of S01-S07 (new files) but never run two scraper stories at once.
