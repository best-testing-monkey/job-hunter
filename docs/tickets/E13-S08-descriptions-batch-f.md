# E13-S08 — Migrate flexvalue and guru descriptions to html_to_markdown

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Migrate 2 adapters (flexvalue, guru) to the shared `html_to_markdown` helper so their descriptions keep paragraphs, headings and lists.

## Context

- Depends on E13-S02: use `from job_scraper.core.html_markdown import html_to_markdown` (spec: paragraphs, `###` headings, `-`/`1.` lists, `**bold**`, hard breaks; plain text accepted).
- Each adapter below lives at `scraper/job_scraper/sites/<site_id>.py` with tests at `scraper/tests/test_<site_id>.py` and fixtures in `scraper/tests/fixtures/<site>/` (see Appendix B).
- Adapters in this batch and where the description is built today:
  - `flexvalue.py` `_extract_description(job_description)`: iterates the children of `main#job div.job-description`, skips the leading metadata `<table>`, and joins `get_text(strip=True)` of the other children. Replace the join with `html_to_markdown` applied to the HTML of all children except that table (the table is parsed into `extra_fields` elsewhere). Fixture `tests/fixtures/flexvalue/detail_1065407.html`. `_extract_client` must keep working.
  - `guru.py` `parse_detail` (~line 128): the description is in `<pre class="jobDetails__description">` — already PLAIN text with newlines; today it is cut at `" ... "` and stripped. Route the final string through `html_to_markdown` (plain-text mode) so it gets the same paragraph/hard-break normalization, keeping the `" ... "` cut. Fixture `tests/fixtures/guru/detail_2101732.html`. (guru is stealth-only in practice; do not fetch anything.)
  - Not migrated (no description is scraped, nothing to do): `headfirst`, `planet_interim`.

## Files to create/modify

- `scraper/job_scraper/sites/flexvalue.py`, `scraper/tests/test_flexvalue.py`
- `scraper/job_scraper/sites/guru.py`, `scraper/tests/test_guru.py`
- Fixtures: reuse the existing `tests/fixtures/<site>/detail_*.html|json`; add a new fixture only if none of the existing ones has a list or multiple paragraphs (copy a page from `scraper/raw/<site>/`, keep it).
- Do not touch any other adapter.

## Acceptance criteria

For EACH adapter in this batch (flexvalue, guru):
- The `description` of the returned `JobPosting` is produced by `html_to_markdown(...)` of the original HTML (or text) — the old flattening code (`get_text(separator=" ")`, `get_text(strip=True)`, regex/HTMLParser stripping) is no longer used for the description (private helpers that become unused are deleted; helpers still used for other fields stay).
- Work only from the saved fixtures — the implementer inspects the fixture's description HTML first and confirms ALL of the description element is converted (not just the first `<p>`).
- A new test in `tests/test_<site_id>.py` parses an existing fixture via `adapter.parse_detail(stub, page)` and asserts on the real structure of that fixture, concretely: if the fixture description has several paragraphs, `"\n\n" in posting.description`; if it has a list, a line starting `"- "` or `"1. "` is present; if it has headings, a line starting `"### "` is present; if it has bold text, `"**"` is present. If the fixture is a single plain paragraph, assert the exact expected string instead.
- For every adapter: `not any(l.startswith("## ") for l in posting.description.splitlines())`, `"  \n"`-style hard breaks aside no line has trailing whitespace, and the description is non-empty.
- Existing assertions that compared the old flattened text are updated to the new Markdown; no existing test is deleted.
- Other fields (title, client, location, workplace, source_url, ...) are unchanged.
- `uv run pytest` from `scraper/` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S08: Migrate flexvalue and guru descriptions to html_to_markdown`.
- `docs/todo.md` item for E13-S08 checked off, committed in the JOB-HUNTER repo (`Mark E13-S08 as done in todo`).
