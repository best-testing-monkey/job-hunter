# E13-S21 — Add `screenshot_selector` to the base adapter

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Give every adapter a place to declare the CSS selector of its job-description element (default: none).

## Context

- `scraper/job_scraper/sites/base.py`: `class SiteAdapter(ABC)` has ClassVars `site_id`, `base_url`, `fetch_strategy` (default `FetchStrategy.STATIC`), `raw_format` (default `"html"`, documented by a docstring-style string right below it). Add the new attribute in the same style.
- Existing tests: `scraper/tests/test_adapter_base.py`.

## Files to create/modify

- `scraper/job_scraper/sites/base.py`
- `scraper/tests/test_adapter_base.py`

## Acceptance criteria

- `SiteAdapter.screenshot_selector: ClassVar[str | None] = None`, followed by a short docstring-style string: CSS selector (valid for both Playwright and soupsieve/bs4 — no `:contains()`) matching exactly ONE element that wraps only the job description; `None` means no screenshots for this site.
- Test: a minimal concrete subclass (implementing the two abstract methods) has `screenshot_selector is None`; a subclass overriding it with `"div.desc"` reports `"div.desc"`.
- Test: for every adapter class in `SITE_REGISTRY` (`job_scraper.sites.registry`), `screenshot_selector` is either `None` or a non-empty string.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S21: Add screenshot_selector to SiteAdapter`.
- `docs/todo.md` item for E13-S21 checked off, committed in the JOB-HUNTER repo (`Mark E13-S21 as done in todo`).
