# E13-S26 — Screenshot backfill function

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

A function that walks one site's existing Markdown job files, captures each one's screenshot from its `- Source:` URL, and records the `- Screenshot:` line — skipping already-captured ones on request.

## Context

- Depends on E13-S21, S22, S23. The URL to open comes from the file itself (`- Source: <url>`), so no DB is needed.
- `scraper/jobs/<stem>.md` -> `scraper/screenshots/<stem>.png`; `SITE_REGISTRY[site_id].screenshot_selector` / `.fetch_strategy` give the selector and stealth flag (class attributes, no instantiation needed).
- `markdown_export.set_screenshot_line(md_path, rel)`, `screenshot_relpath(stem)`; `screenshots.capture_element(url, selector, out_path, *, stealth)`.
- Every job file of a site is named `<site_id>-<listing_id>-<slug>.md`, so `Path(jobs_dir).glob(f"{site_id}-*.md")` selects them (no site id is a prefix of another).

## Files to create/modify

- `scraper/job_scraper/core/screenshot_backfill.py` (new): `def backfill_screenshots(site_id: str, jobs_dir: str, screenshots_dir: str, missing_only: bool = False) -> dict[str, int]`
- `scraper/tests/test_screenshot_backfill.py` (new)

## Acceptance criteria

- Raises `ValueError` for an unknown `site_id`.
- Returns a dict with exactly the keys `attempted`, `captured`, `failed`, `skipped_existing`, `skipped_no_selector` (ints).
- If the adapter's `screenshot_selector` is `None`: every job file of the site counts in `skipped_no_selector`, nothing is attempted.
- Per job file (sorted order): read the first `^- Source:\s*(.+)$` line (no Source line -> `failed`). If `missing_only` and `<screenshots_dir>/<stem>.png` exists -> `skipped_existing` (but still call `set_screenshot_line` so a PNG without the markdown line gets the line). Otherwise `attempted += 1`, call `capture_element(source, selector, <png path>, stealth=adapter.fetch_strategy == FetchStrategy.STEALTH)`: True -> `captured += 1` and `set_screenshot_line(md, screenshot_relpath(stem))`; False -> `failed += 1`. An exception from `capture_element` counts as `failed` (printed to stderr) and never stops the loop.
- Tests with `capture_element` patched and fake adapters registered by monkeypatching `SITE_REGISTRY` entries (or by using a real adapter class and `monkeypatch.setattr(Adapter, "screenshot_selector", "div.x")`), using `tmp_path` job files: all-success counts; failure counts; `missing_only=True` skips an existing PNG (and capture is not called for it) yet adds the markdown line; a file without `- Source:` is `failed`; `screenshot_selector=None` -> `skipped_no_selector`; the md files get exactly one `- Screenshot:` line after two runs.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S26: Add screenshot backfill function`.
- `docs/todo.md` item for E13-S26 checked off, committed in the JOB-HUNTER repo (`Mark E13-S26 as done in todo`).
