# E14-S16 — harveynash: hide the "Reageren" button and share icons, check the faded text

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

harveynash screenshots contain only the ad text: no pink "Reageren" button, no share icons, and readable (not washed-out) text.

## Context

- `scraper/job_scraper/sites/harveynash.py`: `screenshot_selector = "div.post-content"`, `screenshot_hide_selectors = ("div.social-share",)`. Test: `scraper/tests/test_harveynash.py` (fixture `tests/fixtures/harveynash/detail_299204.html`). In the fixture the button is `<a href="#job-application" class="mb-3 me-0 primaryBtn" title="Reageren">` (it appears several times in the page, inside and outside `div.post-content`); the share block is `class="blog-style social-share styles_root__Lit7t card"`.
- QA evidence: docs/e13-qa-results.md section 9 (`harveynash-299093-project-assistent-jp3353.png`: description plus the Reageren button; text washed out/faded, very low contrast but legible).

## Files to create/modify

- `scraper/job_scraper/sites/harveynash.py`
- `scraper/tests/test_harveynash.py`

## Acceptance criteria

- Probe protocol (Appendix C) on ONE live non-stale harveynash posting: print `count()` of `div.post-content a.primaryBtn` and of `div.social-share` INSIDE `div.post-content`, take the element PNG with the proposed hide list applied and open it with the Read tool. Diagnose the fade: print the computed `opacity`, `color` and `filter` of `div.post-content` and of each ancestor up to `body` (loop over `parentElement`). If the fade comes from an unfinished fade-in transition, or from page chrome that the hide list can remove (e.g. a semi-transparent overlay), fix it only with a hide selector; otherwise record the computed values in the commit body and leave the text as is (document, do not hack `capture_element`).
- `screenshot_hide_selectors` = `("div.social-share", "div.post-content a.primaryBtn")` or the narrowest stable selectors the probe proves (each valid for soupsieve and Playwright; keep `div.social-share`).
- Tests: attribute asserted verbatim; each selector valid CSS; `select` on `detail_299204.html` shows `div.post-content a.primaryBtn` matches at least one element INSIDE the screenshot element (`el.select("a.primaryBtn")` non-empty) and the existing selector test stays green.
- Commit body lines: `harveynash: hide <list>` and `harveynash fade: <cause or "not reproduced"> (opacity <x>)`.

## Definition of done

- Run only `uv run pytest tests/test_harveynash.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S16: harveynash hides Reageren button`.
- The orchestrator ticks `docs/todo.md`.
