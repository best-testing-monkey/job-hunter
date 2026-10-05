# E16-S01 — Settle wait: let fade-in animations finish before the element screenshot

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

`capture_element` never photographs an element (or an ancestor) that is mid-fade or not yet faded in. Evidence: 9 of 33 harveynash PNGs are 1116x30 blank strips because an AOS fade-in (`data-aos="fade"` wrapper around `div.post-content`, opacity 0 -> 1) was captured at opacity about 0 (`docs/e14-qa-results.md` sections 8 and 9).

## Context

- `scraper/job_scraper/core/screenshots.py`: `_capture_on_page(page, response, url, selector, out_path, timeout_ms, hide_selectors, pre_actions, skip_selectors)` is shared by the plain-Playwright path (`capture_element`) and the stealth path (`_capture_stealth` -> `page_action`). It ends with `_screenshot_with_retry(page, selector, out_path, timeout_ms)`. The settle step goes right before that call, after the gate/skip check, so both launch paths get it.
- FEASIBILITY FINDING (design adjusted, report in the commit body): AOS only starts the fade when the element scrolls into view, and Playwright's `locator.screenshot` scrolls and shoots immediately, i.e. mid-transition. So the settle step must FIRST scroll the target into view (`page.locator(selector).first.scroll_into_view_if_needed(timeout=3000)`, errors ignored) and THEN wait.
- Tests: `scraper/tests/test_screenshots.py` (decorators `@pytest.mark.enable_socket` + `needs_browser`, `file://` pages under `tmp_path`, see `test_captures_only_element`).

## Files to create/modify

- `scraper/job_scraper/core/screenshots.py`
- `scraper/tests/test_screenshots.py`

## Acceptance criteria

- New helper `_settle(page, selector, max_ms=3000) -> None` called from `_capture_on_page` immediately before `_screenshot_with_retry`. It never raises: (1) scroll the first match into view (try/except), (2) `page.wait_for_function(SETTLE_JS, arg=selector, timeout=max_ms)` inside try/except (a timeout is swallowed and the capture proceeds), (3) `page.wait_for_timeout(100)`.
- `SETTLE_JS` (module constant) is true when the first element matching `selector` is missing, OR when every element from it up through all ancestors has `parseFloat(getComputedStyle(n).opacity) >= 0.99` AND no animation in `document.getAnimations()` has `playState === 'running'`, a target `t` that satisfies `t.contains(el)` (target is the element itself or an ancestor) and a finite iteration count (`effect.getComputedTiming().iterations !== Infinity`, so endless spinners never delay the capture). Descendant animations are deliberately ignored.
- Total settle time is bounded: at most `max_ms` + 100 ms + the scroll call; the capture is never failed or skipped by the settle step.
- Browser test 1 (`file://`): a page with a 3000 px spacer, then `<div id="job" style="background:#000;width:600px;height:300px;opacity:0;transition:opacity 600ms">`, plus a script that adds `style.opacity=1` to `#job` from an `IntersectionObserver` when it becomes visible (simulates AOS). `capture_element(page.as_uri(), "#job", out) is True`; the PNG is mostly black: decode it by loading it in a SECOND page as a `data:image/png;base64,...` image drawn on a canvas and reading the centre pixel via `page.evaluate` (data URLs do not taint the canvas); assert R, G and B are each below 30.
- Browser test 2 (ancestor fade): same idea but the opacity transition is on a PARENT wrapper (`#wrap`, 600 ms CSS `animation` from opacity 0 to 1 running at load); the centre pixel is black.
- Browser test 3 (no delay): the existing static `page_file` fixture page: `capture_element` finishes with settle overhead under 500 ms (measure `_settle(page, "#job")` directly with `time.perf_counter()` on a loaded page, assert below 0.5 s).
- Unit test: `_settle` with a stub page whose `wait_for_function` raises `Exception("timeout")` and whose `scroll_into_view_if_needed` raises still returns None and calls `wait_for_timeout(100)`.
- Existing tests in the file still pass.

## Definition of done

- Run only `uv run pytest tests/test_screenshots.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S01: Wait for fade-in animations to settle before the element screenshot`.
- The orchestrator ticks `docs/todo.md`. Same files as E16-S02 and E16-S12: run in order.
