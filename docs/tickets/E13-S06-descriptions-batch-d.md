# E13-S06 — Migrate freelancer_com, freelancermap, hero descriptions to html_to_markdown

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Migrate 3 adapters (freelancer_com, freelancermap, hero) to the shared `html_to_markdown` helper so their descriptions keep paragraphs, headings and lists.

## Context

- Depends on E13-S02: use `from job_scraper.core.html_markdown import html_to_markdown` (spec: paragraphs, `###` headings, `-`/`1.` lists, `**bold**`, hard breaks; plain text accepted).
- Each adapter below lives at `scraper/job_scraper/sites/<site_id>.py` with tests at `scraper/tests/test_<site_id>.py` and fixtures in `scraper/tests/fixtures/<site>/` (see Appendix B).
- Adapters in this batch and where the description is built today:
  - `freelancer_com.py` `parse_detail` (~line 112): `soup.find("p", class_="Project-description")` then `get_text(strip=True)`. The element has the CSS class `whitespace-pre-line`, i.e. the page shows its newlines — the text inside likely contains literal `\n` and no child tags. Pass the element's inner text/HTML through `html_to_markdown` and confirm in the fixture (`tests/fixtures/freelancer_com/detail_40724221.html`) that line breaks survive.
  - `freelancermap.py` `parse_detail` (~line 122): `soup.select_one("div.project-body-description .ql-editor")` then `get_text(" ", strip=True)`. Quill output: `<p>`, `<ul>`, `<ol>`, `<strong>`.
  - `hero.py` `parse_detail` (~line 91): `div.hero-requisition-body` then ONLY its first `<p>` via `get_text(strip=True)` — this truncates the description to one paragraph. Convert the whole `div.hero-requisition-body` element instead; check the fixture (`tests/fixtures/hero/detail_e98187b8.html`) and make sure the description now contains more than the first paragraph (if the div really contains a single `<p>`, say so in your test's comment-free assertion by asserting the exact expected text).

## Files to create/modify

- `scraper/job_scraper/sites/freelancer_com.py`, `scraper/tests/test_freelancer_com.py`
- `scraper/job_scraper/sites/freelancermap.py`, `scraper/tests/test_freelancermap.py`
- `scraper/job_scraper/sites/hero.py`, `scraper/tests/test_hero.py`
- Fixtures: reuse the existing `tests/fixtures/<site>/detail_*.html|json`; add a new fixture only if none of the existing ones has a list or multiple paragraphs (copy a page from `scraper/raw/<site>/`, keep it).
- Do not touch any other adapter.

## Acceptance criteria

For EACH adapter in this batch (freelancer_com, freelancermap, hero):
- The `description` of the returned `JobPosting` is produced by `html_to_markdown(...)` of the original HTML (or text) — the old flattening code (`get_text(separator=" ")`, `get_text(strip=True)`, regex/HTMLParser stripping) is no longer used for the description (private helpers that become unused are deleted; helpers still used for other fields stay).
- Work only from the saved fixtures — the implementer inspects the fixture's description HTML first and confirms ALL of the description element is converted (not just the first `<p>`).
- A new test in `tests/test_<site_id>.py` parses an existing fixture via `adapter.parse_detail(stub, page)` and asserts on the real structure of that fixture, concretely: if the fixture description has several paragraphs, `"\n\n" in posting.description`; if it has a list, a line starting `"- "` or `"1. "` is present; if it has headings, a line starting `"### "` is present; if it has bold text, `"**"` is present. If the fixture is a single plain paragraph, assert the exact expected string instead.
- For every adapter: `not any(l.startswith("## ") for l in posting.description.splitlines())`, `"  \n"`-style hard breaks aside no line has trailing whitespace, and the description is non-empty.
- Existing assertions that compared the old flattened text are updated to the new Markdown; no existing test is deleted.
- Other fields (title, client, location, workplace, source_url, ...) are unchanged.
- `uv run pytest` from `scraper/` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S06: Migrate freelancer_com, freelancermap, hero descriptions to html_to_markdown`.
- `docs/todo.md` item for E13-S06 checked off, committed in the JOB-HUNTER repo (`Mark E13-S06 as done in todo`).
