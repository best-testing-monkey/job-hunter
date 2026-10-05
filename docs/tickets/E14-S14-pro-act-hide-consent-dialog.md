# E14-S14 — pro_act: hide the cookie consent dialog and dimmer

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 14 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

pro_act screenshots show no consent dialog and no grey dimmer over the ad.

## Context

- `scraper/job_scraper/sites/pro_act.py`: `screenshot_selector = "section.section-content div.content-wrapper"`, `screenshot_hide_selectors = ("div.contact-info",)`. Test: `scraper/tests/test_pro_act.py` (fixture `tests/fixtures/pro_act/detail_8887.html`; has tests for the selector and the hide list from E13-S36).
- QA evidence: docs/e13-qa-results.md section 9 (`pro_act-8884-informatieanalist-ooapi.png`: grey dimmer plus consent dialog "Accepteer alle cookies" over the upper part).
- The saved fixture shows the site uses the "cookie-law-info" plugin; ids present in the HTML include `#cookie-law-info-bar`, `#cookie-law-info-again`, `#cookie_hdr_showagain`, `#cliSettingsPopup`. The dimmer/backdrop class (likely `.cli-modal-backdrop`) is injected by JS, so it is only visible live.

## Files to create/modify

- `scraper/job_scraper/sites/pro_act.py`
- `scraper/tests/test_pro_act.py`

## Acceptance criteria

- Probe protocol (Appendix C) on ONE live non-stale pro_act posting: list the visible fixed/sticky elements (dialog, dimmer, "show again" tab) and take the element PNG with the proposed hide list applied; open it with the Read tool and confirm no dialog and no dimmer.
- `screenshot_hide_selectors` extended (keep `div.contact-info`) with the real selectors from the probe, expected: `#cookie-law-info-bar`, `#cookie-law-info-again`, `#cliSettingsPopup`, `.cli-modal-backdrop`, `.cli-modal-dialog` (drop any the probe shows are absent AND not in the fixture; add any other full-screen fixed element listed).
- Tests: attribute asserted verbatim; each hide selector valid CSS (`select` raises nothing); the ids that exist in `detail_8887.html` (`#cookie-law-info-bar`) are matched by the hide list (`len(select(...)) >= 1`) and are NOT inside the screenshot element (`el.select_one(sel) is None`); `div.contact-info` is still inside the element and still hidden (existing test stays green).
- Commit body line: `pro_act: hide <list>`.

## Definition of done

- Run only `uv run pytest tests/test_pro_act.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E14-S14: pro_act hides consent dialog and dimmer`.
- The orchestrator ticks `docs/todo.md`.
