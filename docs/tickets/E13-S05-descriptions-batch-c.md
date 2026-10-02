# E13-S05 — Migrate harveynash, tender_link, stone_interim, working_nomads descriptions to html_to_markdown

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Migrate 4 adapters (harveynash, tender_link, stone_interim, working_nomads) to the shared `html_to_markdown` helper so their descriptions keep paragraphs, headings and lists.

## Context

- Depends on E13-S02: use `from job_scraper.core.html_markdown import html_to_markdown` (spec: paragraphs, `###` headings, `-`/`1.` lists, `**bold**`, hard breaks; plain text accepted).
- Each adapter below lives at `scraper/job_scraper/sites/<site_id>.py` with tests at `scraper/tests/test_<site_id>.py` and fixtures in `scraper/tests/fixtures/<site>/` (see Appendix B).
- Adapters in this batch and where the description is built today:
  - `harveynash.py` `_strip_html` (`get_text(separator=" ")` + whitespace collapse) applied to `page_data["description"]` (HTML inside the page's `__NEXT_DATA__` JSON). Leave `_extract_workplace_signal` alone.
  - `tender_link.py` `_extract_description`: six JSON fields (`introInformation`, `companyInformation`, `vacancyInformation`, `offerInformation`, `requirementsInformation`, `functionContactInformation`), each HTML, flattened and joined with spaces. Convert each separately; join non-empty parts with `"\n\n"`. Its fixture is `tests/fixtures/tender_link/listing.json` (the vacancy dicts) — `parse_detail` reads from the adapter's `_vacancy_cache` filled by `list_postings`, so tests call `list_postings` with `fetch_page` patched first.
  - `stone_interim.py` `_extract_description` + `_strip_html`: five HTML fields (`IntroInformation`, `VacancyInformation`, `OfferInformation`, `Requirements`, `CompanyInformation`) joined with spaces, regex tag removal plus a hand-written entity table. Convert each field separately, join with `"\n\n"`, delete `_strip_html` (bs4 decodes entities). Fixture: `tests/fixtures/stone_interim/detail_4893_api_GetVacancy.json`.
  - `working_nomads.py` `_strip_html_tags` (`get_text(separator=" ")`) on `job["description"]` from the listing JSON, via `_job_cache` filled by `list_postings`; fixture `tests/fixtures/working_nomads/listing.json`.
  - NOTE: `stone_interim.py` and `working_nomads.py` are touched again by E13-S13 / E13-S14 (source URL fixes) — those run after this story, never in parallel with it.

## Files to create/modify

- `scraper/job_scraper/sites/harveynash.py`, `scraper/tests/test_harveynash.py`
- `scraper/job_scraper/sites/tender_link.py`, `scraper/tests/test_tender_link.py`
- `scraper/job_scraper/sites/stone_interim.py`, `scraper/tests/test_stone_interim.py`
- `scraper/job_scraper/sites/working_nomads.py`, `scraper/tests/test_working_nomads.py`
- Fixtures: reuse the existing `tests/fixtures/<site>/detail_*.html|json`; add a new fixture only if none of the existing ones has a list or multiple paragraphs (copy a page from `scraper/raw/<site>/`, keep it).
- Do not touch any other adapter.

## Acceptance criteria

For EACH adapter in this batch (harveynash, tender_link, stone_interim, working_nomads):
- The `description` of the returned `JobPosting` is produced by `html_to_markdown(...)` of the original HTML (or text) — the old flattening code (`get_text(separator=" ")`, `get_text(strip=True)`, regex/HTMLParser stripping) is no longer used for the description (private helpers that become unused are deleted; helpers still used for other fields stay).
- Work only from the saved fixtures — the implementer inspects the fixture's description HTML first and confirms ALL of the description element is converted (not just the first `<p>`).
- A new test in `tests/test_<site_id>.py` parses an existing fixture via `adapter.parse_detail(stub, page)` and asserts on the real structure of that fixture, concretely: if the fixture description has several paragraphs, `"\n\n" in posting.description`; if it has a list, a line starting `"- "` or `"1. "` is present; if it has headings, a line starting `"### "` is present; if it has bold text, `"**"` is present. If the fixture is a single plain paragraph, assert the exact expected string instead.
- For every adapter: `not any(l.startswith("## ") for l in posting.description.splitlines())`, `"  \n"`-style hard breaks aside no line has trailing whitespace, and the description is non-empty.
- Existing assertions that compared the old flattened text are updated to the new Markdown; no existing test is deleted.
- Other fields (title, client, location, workplace, source_url, ...) are unchanged.
- `uv run pytest` from `scraper/` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S05: Migrate harveynash, tender_link, stone_interim, working_nomads descriptions to html_to_markdown`.
- `docs/todo.md` item for E13-S05 checked off, committed in the JOB-HUNTER repo (`Mark E13-S05 as done in todo`).
