# E13-S36 — Hide cookie overlays / apply forms before the element screenshot

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` for conventions. (Added during the run after S28-S32 found Cookiebot/CookieYes overlays on several sites and an apply form inside pro_act's description wrapper.)

## Goal

Screenshots must show only the job ad: let each adapter declare CSS selectors of elements to hide (cookie banners, consent dialogs, apply forms, share bars) and make `capture_element` hide them before screenshotting.

## Context

- `scraper/job_scraper/sites/base.py` `SiteAdapter` has `screenshot_selector: ClassVar[str | None]` (E13-S21).
- `scraper/job_scraper/core/screenshots.py`: `capture_element(url, selector, out_path, *, stealth=False, timeout_ms=30000) -> bool` (E13-S22; never raises; real-browser tests use `file://` + `page.set_content` and are marked `@pytest.mark.enable_socket`).
- Callers: `scraper/job_scraper/pipeline.py` `run_site` (E13-S24) and `scraper/job_scraper/core/screenshot_backfill.py` `backfill_screenshots` (E13-S26) — both call `capture_element` with `adapter.screenshot_selector`; their tests mock `capture_element`.
- Known overlays/obstructions from the selector stories (see todo.md "LIVE-QA FLAGS"): sevenstars + circle8 `#CybotCookiebotDialog` (Cookiebot); ictergezocht `#cookieyes-banner`; pro_act application form `div.contact-info` sits INSIDE `div.content-wrapper` (so pro_act currently has `screenshot_selector = None`, BLOCKED); harveynash has a "Reageren" button and share icons inside `div.post-content`.

## Files to create/modify

- `scraper/job_scraper/sites/base.py`: add `screenshot_hide_selectors: ClassVar[tuple[str, ...]] = ()` next to `screenshot_selector`, same docstring style.
- `scraper/job_scraper/core/screenshots.py`: `GENERIC_HIDE_SELECTORS` constant (tuple) + new keyword-only parameter `hide_selectors: Sequence[str] = ()` on `capture_element`.
- `scraper/job_scraper/pipeline.py` and `scraper/job_scraper/core/screenshot_backfill.py`: pass `hide_selectors=adapter.screenshot_hide_selectors` to `capture_element`.
- `scraper/job_scraper/sites/{sevenstars,circle8,ictergezocht,pro_act}.py` (+ harveynash if a clean selector for its button/share icons exists in the saved HTML): set `screenshot_hide_selectors`; for pro_act also set `screenshot_selector` to the wrapper that contains the ad text (`section.section-content div.content-wrapper`, verify it matches exactly one element on the fixture and several `raw/pro_act` pages) and hide `div.contact-info`.
- Tests: `scraper/tests/test_screenshots.py`, `test_adapter_base.py`, `test_pipeline.py`, `test_screenshot_backfill.py`, and the four/five adapter test files.

## Acceptance criteria

- `capture_element(..., hide_selectors=...)`: after `page.goto` and before the element screenshot, injects a `<style>` with `selector { display: none !important; }` for every selector in `GENERIC_HIDE_SELECTORS + hide_selectors` (join with commas; skip empty), and also sets `html, body { overflow: auto !important; }` (consent dialogs often lock scrolling). `GENERIC_HIDE_SELECTORS` contains at least `#CybotCookiebotDialog`, `#cookieyes-banner`, `#onetrust-banner-sdk`, `.cookie-banner`, `[id*="cookie-consent" i]`, `[class*="cookie-consent" i]` (all valid Playwright CSS). Failures still return False, never raise.
- Real-browser test (file:// + set_content, `enable_socket` marker as the existing ones): a page with `<div id="CybotCookiebotDialog" style="position:fixed;inset:0;background:red">` overlay over a `div#job` and a `div.contact-info` inside `div#job`; with `hide_selectors=("div.contact-info",)` the PNG height equals the height of `#job` WITHOUT the contact-info block (assert ±2px against a second capture of a page without those elements), and a pixel sample inside the PNG is not red.
- `SiteAdapter.screenshot_hide_selectors` defaults to `()`; test that it is a tuple for all registered adapters.
- pipeline and backfill tests (mocked `capture_element`) assert the call receives `hide_selectors` equal to the adapter's attribute.
- sevenstars and circle8 hide `#CybotCookiebotDialog`; ictergezocht hides `#cookieyes-banner`; each adapter test asserts the attribute AND that every hide selector, when run via `BeautifulSoup(fixture).select(...)`, is valid CSS (no exception; matching is not required because overlays are injected by JS).
- pro_act: `screenshot_selector` is now the wrapper, a test asserts it matches exactly one element on `tests/fixtures/pro_act/detail_8887.html`, that `div.contact-info` is inside it AND is listed in `screenshot_hide_selectors`; the old test asserting `screenshot_selector is None` is replaced.
- Existing tests keep passing (only run the touched test files).

## Definition of done

- Run only the touched test files (a separate gate agent runs full suites).
- Committed in the SCRAPER repo as `E13-S36: Hide overlays and forms before element screenshots`.
- `docs/todo.md` item ticked by the orchestrator.
