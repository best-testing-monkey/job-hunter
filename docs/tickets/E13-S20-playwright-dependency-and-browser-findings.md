# E13-S20 — Declare playwright as a direct dependency; record browser findings

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Make the screenshot library an explicit dependency of the scraper without triggering a second browser download, and write down which browser the project uses.

## Context

- `scraper/pyproject.toml` dependencies: `scrapling[fetchers]`, `pytest`, `beautifulsoup4`. `scrapling[fetchers]` 0.4.15 already requires `playwright>=1.62.0` and `patchright>=1.62.1` (see `scraper/uv.lock`: playwright 1.63.0, patchright 1.63.0 are locked), so Playwright is only a TRANSITIVE dependency today.
- Browsers on disk (found while writing this ticket): `~/.cache/ms-playwright/` has `chromium-1208`, `-1223`, `-1234`, `-1243`, matching `chromium_headless_shell-*`, `firefox-1509`, `webkit-2248`, `ffmpeg-1011`; `~/.cache/camoufox/` exists. Machine quirk: `~/.cache/*` physically lands on the crowded `/media/baz/MonkeyWorks` drive.
- `job_scraper/sites/base.py` `fetch_page` uses scrapling `Fetcher` (HTTP, no browser) for `FetchStrategy.STATIC` and `StealthyFetcher.fetch(url, headless=True)` for `STEALTH` (which browser that launches — patchright Chromium or Camoufox — must be determined from the installed scrapling source: `scraper/.venv/lib/python3.13/site-packages/scrapling/engines/`).
- Plan used by later stories: screenshots are taken with plain `playwright` Chromium for STATIC adapters and with `patchright` (drop-in, anti-detection patched Chromium) for STEALTH adapters; both resolve their browser from `~/.cache/ms-playwright`.

## Files to create/modify

- `scraper/pyproject.toml` (+ `scraper/uv.lock`)
- `scraper/tests/test_browser_dependency.py` (new)
- `scraper/README.md` — new section `## Screenshots (browser requirements)` with the findings.

## Acceptance criteria

- Run from `scraper/`: `uv add playwright patchright`. The resulting `uv.lock` diff must NOT change the locked versions (still playwright 1.63.x, patchright 1.63.x) and must not add other packages; `pyproject.toml` `dependencies` now lists `playwright` and `patchright` explicitly.
- Do NOT run `playwright install`, `patchright install` or `camoufox fetch`: they download hundreds of MB into `~/.cache` on the crowded drive. If a needed browser build is missing, stop and ask the owner.
- Determine and record in the README section (each as one sentence): (1) which Chromium revision playwright 1.63 expects and the full path of its executable (`uv run python -c "from playwright.sync_api import sync_playwright as s; p=s().start(); print(p.chromium.executable_path); p.stop()"`) and whether that file exists; (2) the same for patchright; (3) which browser scrapling's `StealthyFetcher` uses (read the scrapling source) and whether it shares the `~/.cache/ms-playwright` install, i.e. whether the screenshot feature needs a second browser download (answer yes/no); (4) the install command to run if a browser is missing (`uv run playwright install chromium`) and the warning about the drive.
- Test `tests/test_browser_dependency.py`: `import playwright.sync_api`, `import patchright.sync_api` succeed, and `tomllib.load` of `pyproject.toml` has `playwright` and `patchright` entries (any version spec) under `project.dependencies`. (Launching a browser is tested in E13-S22, not here.)
- `uv run pytest` passes (no network, no browser launched).

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S20: Declare playwright/patchright deps and document browser findings`.
- `docs/todo.md` item for E13-S20 checked off, committed in the JOB-HUNTER repo (`Mark E13-S20 as done in todo`).
