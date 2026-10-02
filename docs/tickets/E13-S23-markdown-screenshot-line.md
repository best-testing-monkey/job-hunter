# E13-S23 — Markdown `- Screenshot:` line support

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Let job Markdown files record their screenshot as `- Screenshot: screenshots/<stem>.png`, both at write time and when added afterwards by a backfill.

## Context

- `scraper/job_scraper/core/markdown_export.py`: `slugify`, `filename_for(posting)` (`<site_id>-<listing_id>-<slug>.md`), `render(posting) -> str` (layout: `# title`, blank, bullets in fixed order then one bullet per `extra_fields` entry, blank, `## Description`, blank, description, optional `## Scrape note`), `write(posting, jobs_dir) -> str`.
- The app's parser (`resume-matcher/build_report.py`, `JOB_FIELD_RE = r"^- (\w[\w ]*):\s*(.+)$"`) reads every `- Key: value` bullet into a dict and only uses `source/client/location/posted/workplace`, so an extra `- Screenshot: ...` bullet is harmless. The app finds screenshots by file stem, not by this line (E13-S33); the line is informational for humans and for other tools.
- Screenshot files live in `scraper/screenshots/<stem>.png`, `<stem>` = `filename_for(posting)` minus `.md`; the path in the bullet is relative to `scraper/` (`screenshots/<stem>.png`), like `jobs/` and `raw/`.
- Tests: `scraper/tests/test_markdown_export.py`.
- Screenshot data is NOT part of `JobPosting` or `content_hash` (so re-scrapes don't churn).

## Files to create/modify

- `scraper/job_scraper/core/markdown_export.py`
- `scraper/tests/test_markdown_export.py`

## Acceptance criteria

- `def stem_for(posting: JobPosting) -> str` returns `filename_for(posting)` without `.md`; `def screenshot_relpath(stem: str) -> str` returns `f"screenshots/{stem}.png"`.
- `render(posting, screenshot: str | None = None)`: when `screenshot` is a non-empty string, a bullet `- Screenshot: <screenshot>` is added AFTER the `extra_fields` bullets and before the blank line preceding `## Description`; with `None` the output is byte-identical to today's (existing tests unchanged). `write(posting, jobs_dir, screenshot=None)` passes it through.
- `def set_screenshot_line(md_path: str, screenshot: str) -> bool`: if the file already has a `- Screenshot:` line, replace its value; otherwise insert the bullet after the last consecutive `- ` bullet of the header block (the lines between the `# title` line and the blank line before `## Description`). Returns `True` if the file content changed, `False` if it already had exactly that line. Idempotent.
- Tests: render with/without `screenshot`; bullet position (after an extra field, before `## Description`); `set_screenshot_line` on a rendered file inserts once, returns True then False on the second call, and replaces a different old value; text after the header (description, scrape note) is untouched; the app regex `^- (\w[\w ]*):\s*(.+)$` matches `- Screenshot: screenshots/x.png` (copy the regex literally into the test).
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S23: Add Screenshot bullet support to markdown export`.
- `docs/todo.md` item for E13-S23 checked off, committed in the JOB-HUNTER repo (`Mark E13-S23 as done in todo`).
