# E16-S09 — `PostingGone`, adapter gone attributes, opt-in detail check in `fetch_page`

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

A DETAIL fetch can raise `PostingGone` when the page says the posting is gone; listing fetches and every existing caller of `fetch_page` behave exactly as before.

## Context

- Design choice (least invasive): an optional keyword `gone_check: GoneCheck | None = None` on the existing `fetch_page`; with None the function is byte-for-byte the old behaviour (returns `.body`; the fetcher is called with exactly the old arguments; `gone_check` is never forwarded to scrapling). Existing tests that patch `job_scraper.pipeline.fetch_page` or `job_scraper.sites.<x>.fetch_page` and `test_fetch_page_static/stealth` (`FakeResponse` with only `.body`, `assert_called_once_with("https://example.com")`) keep working.
- `scraper/job_scraper/sites/base.py`: `fetch_page(strategy, url, **kwargs)` returns `Fetcher.get(url, **kwargs).body` or `StealthyFetcher.fetch(url, headless=True, **kwargs).body`; `SiteAdapter` ClassVars. `GoneCheck` and `gone_reason` from `scraper/job_scraper/core/gone.py` (E16-S08).
- Response fields: `.status`, `.url` (final URL), `.body` (see E16-S08 Context). Read them with `getattr(resp, "status", None)` / `getattr(resp, "url", None)` so fakes without those attributes simply never trigger.
- Tests: `scraper/tests/test_adapter_base.py` (add the new tests here; patch `job_scraper.sites.base.Fetcher.get` / `StealthyFetcher.fetch` like `test_pipeline.py` does for `test_fetch_page_static`).

## Files to create/modify

- `scraper/job_scraper/sites/base.py`
- `scraper/tests/test_adapter_base.py`

## Acceptance criteria

- `class PostingGone(Exception)` in `base.py` with attributes `url: str` and `reason: str` (message `"<url>: <reason>"`).
- `fetch_page(strategy, url, *, gone_check: GoneCheck | None = None, **kwargs)`: after fetching, if `gone_check` is not None compute `reason = gone_reason(status, url, final_url, body, gone_check)` and raise `PostingGone(url, reason)` when not None; otherwise return the body. The `DYNAMIC` strategy still raises `NotImplementedError`.
- `SiteAdapter` gets `listing_paths: ClassVar[tuple[str, ...]] = ()` ("URL paths of the site's listing/landing pages; a detail fetch that redirects to one means the posting is gone") and `gone_markers: ClassVar[tuple[str, ...]] = ()` ("case-insensitive texts of a soft-404 page, matched against <title>/<h1> only"), plus `@classmethod def gone_check(cls, listing_id: str = "") -> GoneCheck` returning `GoneCheck(listing_id, cls.listing_paths, cls.gone_markers)`.
- Tests: no `gone_check` -> body returned for a 404 fake (old behaviour); `gone_check` + status 404 raises `PostingGone` with reason `"http 404"` (static) and with a stealth fake; status 410 raises; status 200 with `url` equal to the request returns the body; 200 whose `.url` is `https://s.test/jobs` while requesting `https://s.test/job/abc-123` with `GoneCheck("123", ("/jobs",))` raises with a reason starting `"redirect to /jobs"`; a 200 page whose `<title>` is `Job Not Found` with marker `("job not found",)` raises; the same text only in a `<p>` returns the body; a `FakeResponse` with only `.body` plus `gone_check` returns the body; `gone_check` is not forwarded to the fetcher (`assert_called_once_with(url)`); every `SITE_REGISTRY` adapter has tuple-typed `listing_paths`/`gone_markers` and `SiteAdapter.gone_check("x")` equals `GoneCheck("x", (), ())` for a bare subclass.
- Existing `fetch_page` tests in `test_pipeline.py` still pass (run that file too).

## Definition of done

- Run only `uv run pytest tests/test_adapter_base.py tests/test_pipeline.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S09: Raise PostingGone from opt-in detail fetches`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S08 and E16-S03 (same file `base.py`).
