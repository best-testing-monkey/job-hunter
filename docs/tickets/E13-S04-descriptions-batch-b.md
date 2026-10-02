# E13-S04 — Migrate djinni, circle8, sevenstars descriptions to html_to_markdown

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Migrate 3 adapters (djinni, circle8, sevenstars) to the shared `html_to_markdown` helper so their descriptions keep paragraphs, headings and lists.

## Context

- Depends on E13-S02: use `from job_scraper.core.html_markdown import html_to_markdown` (spec: paragraphs, `###` headings, `-`/`1.` lists, `**bold**`, hard breaks; plain text accepted).
- Each adapter below lives at `scraper/job_scraper/sites/<site_id>.py` with tests at `scraper/tests/test_<site_id>.py` and fixtures in `scraper/tests/fixtures/<site>/` (see Appendix B).
- Adapters in this batch and where the description is built today:
  - `djinni.py` `parse_detail` (`description = ld_json.get("description", "")`, ~line 103): JSON-LD description copied verbatim. Inspect `tests/fixtures/djinni/detail_848723.html` / `detail_850338.html`: the string may be HTML (with tags/entities) or plain text with `\n`; `html_to_markdown` handles both.
  - `circle8.py` `parse_detail` (JSON-LD `data.get("description", "")`, ~line 68): same treatment. Note `circle8.py` builds a `JobPosting` in two places (~lines 48 and 88); both must end up with a converted description.
  - `sevenstars.py` `parse_detail` (~line 138): `strip_html_tags(raw_description)` (module-level `MLStripper` HTMLParser). Replace with `html_to_markdown`; keep `strip_html_tags` only if something else still calls it (grep), otherwise delete it and `MLStripper`. The workplace detection `_extract_workplace_from_description` still receives the converted description text — it must keep working (existing test).

## Files to create/modify

- `scraper/job_scraper/sites/djinni.py`, `scraper/tests/test_djinni.py`
- `scraper/job_scraper/sites/circle8.py`, `scraper/tests/test_circle8.py`
- `scraper/job_scraper/sites/sevenstars.py`, `scraper/tests/test_sevenstars.py`
- Fixtures: reuse the existing `tests/fixtures/<site>/detail_*.html|json`; add a new fixture only if none of the existing ones has a list or multiple paragraphs (copy a page from `scraper/raw/<site>/`, keep it).
- Do not touch any other adapter.

## Acceptance criteria

For EACH adapter in this batch (djinni, circle8, sevenstars):
- The `description` of the returned `JobPosting` is produced by `html_to_markdown(...)` of the original HTML (or text) — the old flattening code (`get_text(separator=" ")`, `get_text(strip=True)`, regex/HTMLParser stripping) is no longer used for the description (private helpers that become unused are deleted; helpers still used for other fields stay).
- Work only from the saved fixtures — the implementer inspects the fixture's description HTML first and confirms ALL of the description element is converted (not just the first `<p>`).
- A new test in `tests/test_<site_id>.py` parses an existing fixture via `adapter.parse_detail(stub, page)` and asserts on the real structure of that fixture, concretely: if the fixture description has several paragraphs, `"\n\n" in posting.description`; if it has a list, a line starting `"- "` or `"1. "` is present; if it has headings, a line starting `"### "` is present; if it has bold text, `"**"` is present. If the fixture is a single plain paragraph, assert the exact expected string instead.
- For every adapter: `not any(l.startswith("## ") for l in posting.description.splitlines())`, `"  \n"`-style hard breaks aside no line has trailing whitespace, and the description is non-empty.
- Existing assertions that compared the old flattened text are updated to the new Markdown; no existing test is deleted.
- Other fields (title, client, location, workplace, source_url, ...) are unchanged.
- `uv run pytest` from `scraper/` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S04: Migrate djinni, circle8, sevenstars descriptions to html_to_markdown`.
- `docs/todo.md` item for E13-S04 checked off, committed in the JOB-HUNTER repo (`Mark E13-S04 as done in todo`).
