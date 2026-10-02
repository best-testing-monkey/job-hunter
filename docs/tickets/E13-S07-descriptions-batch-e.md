# E13-S07 — Migrate iamexpat, ictergezocht, wearedevelopers descriptions to html_to_markdown

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Migrate 3 adapters (iamexpat, ictergezocht, wearedevelopers) to the shared `html_to_markdown` helper so their descriptions keep paragraphs, headings and lists.

## Context

- Depends on E13-S02: use `from job_scraper.core.html_markdown import html_to_markdown` (spec: paragraphs, `###` headings, `-`/`1.` lists, `**bold**`, hard breaks; plain text accepted).
- Each adapter below lives at `scraper/job_scraper/sites/<site_id>.py` with tests at `scraper/tests/test_<site_id>.py` and fixtures in `scraper/tests/fixtures/<site>/` (see Appendix B).
- Adapters in this batch and where the description is built today:
  - `iamexpat.py` `parse_detail` (~line 113): `.BodyCenter_main__Sz_2E` element, `get_text(strip=True)` (words from adjacent tags are glued together). Fixture `tests/fixtures/iamexpat/detail_tLJWUBCWY1P8MBXMScbwRE.html`.
  - `ictergezocht.py` `_extract_description`: `div.vacancy-full-text-dom`, `get_text(strip=True)`. Fixture `tests/fixtures/ictergezocht/detail_438712.html`.
  - `wearedevelopers.py` `_extract_description`: finds the `<h2>` whose text is "Job description" and takes the NEXT `<div>`'s `get_text(strip=True)`. Fixtures `tests/fixtures/wearedevelopers/detail_*.html` (three of them: use at least two in tests).

## Files to create/modify

- `scraper/job_scraper/sites/iamexpat.py`, `scraper/tests/test_iamexpat.py`
- `scraper/job_scraper/sites/ictergezocht.py`, `scraper/tests/test_ictergezocht.py`
- `scraper/job_scraper/sites/wearedevelopers.py`, `scraper/tests/test_wearedevelopers.py`
- Fixtures: reuse the existing `tests/fixtures/<site>/detail_*.html|json`; add a new fixture only if none of the existing ones has a list or multiple paragraphs (copy a page from `scraper/raw/<site>/`, keep it).
- Do not touch any other adapter.

## Acceptance criteria

For EACH adapter in this batch (iamexpat, ictergezocht, wearedevelopers):
- The `description` of the returned `JobPosting` is produced by `html_to_markdown(...)` of the original HTML (or text) — the old flattening code (`get_text(separator=" ")`, `get_text(strip=True)`, regex/HTMLParser stripping) is no longer used for the description (private helpers that become unused are deleted; helpers still used for other fields stay).
- Work only from the saved fixtures — the implementer inspects the fixture's description HTML first and confirms ALL of the description element is converted (not just the first `<p>`).
- A new test in `tests/test_<site_id>.py` parses an existing fixture via `adapter.parse_detail(stub, page)` and asserts on the real structure of that fixture, concretely: if the fixture description has several paragraphs, `"\n\n" in posting.description`; if it has a list, a line starting `"- "` or `"1. "` is present; if it has headings, a line starting `"### "` is present; if it has bold text, `"**"` is present. If the fixture is a single plain paragraph, assert the exact expected string instead.
- For every adapter: `not any(l.startswith("## ") for l in posting.description.splitlines())`, `"  \n"`-style hard breaks aside no line has trailing whitespace, and the description is non-empty.
- Existing assertions that compared the old flattened text are updated to the new Markdown; no existing test is deleted.
- Other fields (title, client, location, workplace, source_url, ...) are unchanged.
- `uv run pytest` from `scraper/` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S07: Migrate iamexpat, ictergezocht, wearedevelopers descriptions to html_to_markdown`.
- `docs/todo.md` item for E13-S07 checked off, committed in the JOB-HUNTER repo (`Mark E13-S07 as done in todo`).
