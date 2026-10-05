# E14-S01 — Optional `screenshot_pre_actions` (click before capture)

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

Let an adapter list CSS selectors that `capture_element` clicks (e.g. a "Show more" button) after the page loads and before the element screenshot.

## Context

- `scraper/job_scraper/sites/base.py`: `SiteAdapter` already has `screenshot_selector` and `screenshot_hide_selectors: ClassVar[tuple[str, ...]] = ()` (E13-S21/S36), each followed by a docstring.
- `scraper/job_scraper/core/screenshots.py`: `capture_element(url, selector, out_path, *, stealth=False, timeout_ms=30000, hide_selectors=())`. Order inside: `page.goto`, `page.add_style_tag(css)`, `page.wait_for_selector(selector)`, `page.locator(selector).first.screenshot(path=out_path)`. It must never raise (returns False on any failure).
- `scraper/tests/test_screenshots.py` has the browser-test pattern (`@pytest.mark.enable_socket`, `needs_browser`, `page_file` fixture, PNG height via `struct.unpack(">II", data[16:24])`).
- This story only adds the mechanism; pipeline/backfill wiring is E14-S03/S04, guru uses it in E14-S08.

## Files to create/modify

- `scraper/job_scraper/sites/base.py`
- `scraper/job_scraper/core/screenshots.py`
- `scraper/tests/test_screenshots.py`

## Acceptance criteria

- `SiteAdapter.screenshot_pre_actions: ClassVar[tuple[str, ...]] = ()` with a docstring in the same style (CSS selectors, valid for Playwright; each clicked once, in order, before the element screenshot).
- `capture_element(..., pre_actions: Sequence[str] = ())` (keyword-only, after `hide_selectors`): after the style tag is added and before `wait_for_selector(selector)`, for each selector in `pre_actions`: take `page.locator(sel).first`; if `count() > 0` and `is_visible()`, `click(timeout=3000)` then `page.wait_for_timeout(300)`. A missing or unclickable pre-action selector is logged at debug level and skipped; it never makes the capture fail by itself.
- Browser test A (`file://`): page with `<div id="job"><p>short</p><button id="more" onclick="document.getElementById('full').style.display='block';this.remove()">Show more</button><div id="full" style="display:none;height:400px">full text</div></div>`. With `pre_actions=("button#more",)` the PNG height is at least 400 px greater than a capture of the same page without `pre_actions` (compare the two heights).
- Browser test B: `pre_actions=("button#does-not-exist",)` still returns True and the PNG exists.
- Test C (no browser): for every class in `SITE_REGISTRY.values()`, `isinstance(cls.screenshot_pre_actions, tuple)` and `cls.screenshot_pre_actions == ()` for all adapters at this point in the epic (guru changes it in E14-S08, which updates this assertion to a tuple check only).
- Existing tests in `tests/test_screenshots.py` still pass.

## Definition of done

- Run only `uv run pytest tests/test_screenshots.py -q` from `scraper/` (a separate gate agent runs full suites).
- Committed in the SCRAPER repo as `E14-S01: Add screenshot_pre_actions (click before capture)`.
- The orchestrator ticks `docs/todo.md` (do not edit it).
