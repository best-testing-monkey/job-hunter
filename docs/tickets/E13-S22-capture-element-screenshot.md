# E13-S22 — `capture_element` Playwright helper

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

A single function that opens a URL in headless Chromium and saves a PNG of ONLY the element matching a CSS selector, returning False (never raising) on any failure.

## Context

- Depends on E13-S20 (playwright/patchright dependencies and the browser findings in `README.md`).
- API: `from playwright.sync_api import sync_playwright`; for stealth use `from patchright.sync_api import sync_playwright as sync_patchright` (same API). Element screenshot: `page.locator(selector).first.screenshot(path=out_path)` captures only that element's box.
- No browser launch exists anywhere in the repo yet; `job_scraper/sites/base.py` `fetch_page` is HTTP/scrapling only.
- pytest runs with `--disable-socket` (pytest-socket). Browser tests may hit `SocketBlockedError` from the Playwright driver/asyncio internals; if so mark those tests `@pytest.mark.enable_socket` (pytest-socket marker) — they must still only use `file://` URLs and `page.set_content`, never the network.
- Logging: use `logging.getLogger(__name__)`; the CLI prints warnings via the default handler.

## Files to create/modify

- `scraper/job_scraper/core/screenshots.py` (new)
- `scraper/tests/test_screenshots.py` (new)

## Acceptance criteria

- `def capture_element(url: str, selector: str, out_path: str, *, stealth: bool = False, timeout_ms: int = 30000) -> bool`: launches headless Chromium (patchright when `stealth=True`), viewport 1280x1600, `page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)`, `page.wait_for_selector(selector, timeout=timeout_ms)`, screenshots the first match to `out_path` (parent directories created), returns `True`. The browser is always closed (`try/finally`).
- ANY exception (timeout, selector not found, navigation error, browser missing) is caught: a warning containing the URL and the exception text is logged, a partially written `out_path` is removed, and `False` is returned. The function never raises.
- `def browser_available() -> bool`: True iff plain-playwright Chromium's `executable_path` exists on disk (no launch, no network).
- Tests (skipped with `pytest.mark.skipif(not browser_available(), ...)` when no browser): write `tmp_path/page.html` with `<nav style="height:500px">NAV</nav><div id="job" style="height:300px;width:600px">Job text</div>`; `capture_element(page.as_uri(), "#job", str(tmp_path/"out.png"))` returns `True`; the file starts with the PNG magic bytes `b"\x89PNG\r\n\x1a\n"`; the PNG's height (big-endian uint32 at byte offset 20) is 300 (+-2) and width 600 (+-2) — proving only the element was captured, not the 500px nav.
- Test: selector `"#nope"` with `timeout_ms=500` returns `False` and creates no file. Test: URL `(tmp_path/"missing.html").as_uri()` returns `False` and creates no file.
- Test (no browser needed): `capture_element` with `sync_playwright` patched to raise `RuntimeError` returns `False` (never raises); `browser_available()` returns a `bool`.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S22: Add capture_element screenshot helper`.
- `docs/todo.md` item for E13-S22 checked off, committed in the JOB-HUNTER repo (`Mark E13-S22 as done in todo`).
