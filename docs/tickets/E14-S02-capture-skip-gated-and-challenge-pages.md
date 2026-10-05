# E14-S02 — `capture_element` skips gated and bot-challenge pages cleanly

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

Distinguish "deliberately skipped" (gated teaser, Cloudflare challenge page) from "failed": `capture_element` returns `None` for a skip, records nothing, and takes no screenshot.

## Context

- `scraper/job_scraper/core/screenshots.py` `capture_element(...)` currently returns `bool` (True saved / False failed, never raises). `page.goto(...)` returns a Playwright `Response | None`.
- QA findings (`docs/e13-qa-results.md` sections 6, 9, 11): hero shows a gated blurred teaser ("Log in om de volledige aanvraag te zien", a 640x65 strip) for delisted postings; ictergezocht detail pages answer HTTP 403 from Cloudflare. Owner rule: NO bypass of bot walls; detect and skip.
- `scraper/job_scraper/sites/base.py`: `SiteAdapter.screenshot_hide_selectors` is the style to copy for the new attribute.
- Tests live in `scraper/tests/test_screenshots.py` (same helpers as E14-S01).
- Callers (pipeline/backfill) are changed in E14-S03/S04, not here. Until then `None` is falsy, so they count it as failed — acceptable for the interim.

## Files to create/modify

- `scraper/job_scraper/sites/base.py`
- `scraper/job_scraper/core/screenshots.py`
- `scraper/tests/test_screenshots.py`

## Acceptance criteria

- `SiteAdapter.screenshot_skip_selectors: ClassVar[tuple[str, ...]] = ()` + docstring ("if any of these matches after load, the page is a gate/teaser: skip the screenshot").
- `capture_element(..., skip_selectors: Sequence[str] = ()) -> bool | None`. Return contract in the docstring: True saved, False failed, None skipped on purpose. Still never raises.
- Challenge detection: module-level pure function `_is_challenge(response, title: str) -> bool` returning True when `response` is not None and (`response.headers.get("cf-mitigated") == "challenge"` or (`response.status in (403, 503)` and `"just a moment"` in `title.lower()`)). `capture_element` calls it right after `page.goto` with `page.title()`; if True: log at info level, remove any partial file, return None.
- Gate detection: after the hide style/pre-actions, wait for `", ".join([selector, *skip_selectors])` (so a gate that renders instead of the ad is noticed quickly), then if `skip_selectors` is non-empty and any `page.locator(s).count() > 0`: return None (no PNG written). With empty `skip_selectors` behaviour is unchanged.
- Tests: (1) no browser: `_is_challenge` with `types.SimpleNamespace` fakes for four cases (header challenge -> True; 403 + "Just a moment..." -> True; 403 + "Forbidden" -> False; `None` response -> False). (2) browser (`file://`, `enable_socket`, `needs_browser`): page with `<div class="gate">log in</div><div id="job">text</div>` and `skip_selectors=("div.gate",)` -> result `is None` and the output PNG does not exist; same page without skip_selectors -> True. (3) default tuple check for `screenshot_skip_selectors` over all registered adapters (same style as the pre-actions test from E14-S01). (4) existing "missing selector returns False" test still returns exactly `False` (not None).

## Definition of done

- Run only `uv run pytest tests/test_screenshots.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S02: Skip gated and bot-challenge pages in capture_element`.
- The orchestrator ticks `docs/todo.md`. Touches the same files as E14-S01: run after it.
