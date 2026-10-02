# Appendix B — scraper-repo standards (Epic 13)

Applies to every Epic 13 story that touches `scraper/`. Read together with
`APPENDIX-A-standards.md`; where they differ, this file wins for `scraper/`
work.

## Two repos

- `scraper/` is a SEPARATE git repository with its own history. It is the
  owner's own code and Epic 13 edits it freely. Commit scraper changes with
  `git -C scraper add ... && git -C scraper commit ...` (or `cd scraper`).
- `docs/` and `app/` belong to the job-hunter repo (the parent). Ticking a
  story off in `docs/todo.md` is committed there, never in the scraper repo.
- Appendix A's boundary "never edit files under `scraper/`" does NOT apply to
  Epic 13 scraper stories. It still applies in reverse: scraper stories never
  edit `app/` or `resume-matcher/`, and app stories never edit `scraper/`.
- Generated, git-ignored outputs (`scraper/jobs/`, `scraper/raw/`,
  `scraper/scraper.db`, later `scraper/screenshots/`) are never edited by
  hand and never touched by a story except E13-S35 (the QA runbook).

## Environment and tests

- Run from `scraper/`: `uv run pytest` (pytest is configured with
  `--disable-socket`, so any test that touches the network fails — this is
  deliberate). Never run `python -m job_scraper scrape` inside a story
  except E13-S35.
- One test file per adapter: `tests/test_<site_id>.py`; fixtures live in
  `tests/fixtures/<site>/`. Existing tests patch the adapter module's
  `fetch_page` (e.g. `patch("job_scraper.sites.working_nomads.fetch_page",
  return_value=fixture_bytes)`) and call `adapter.parse_detail(stub, page)`
  with a `ListingStub` built by hand — copy that pattern.
- When a story intentionally changes output (description format, URL),
  update the existing assertions that encoded the old value. Do not delete a
  test or weaken it to `assert True`.
- Adapters are plain classes subclassing `job_scraper.sites.base.SiteAdapter`
  (`site_id`, `base_url`, `fetch_strategy`, `list_postings()`,
  `parse_detail()`), registered in `job_scraper/sites/registry.py`.
- Parsing uses `beautifulsoup4` (`BeautifulSoup(page, "html.parser")`)
  only. Do not add `markdownify`, `html2text`, `lxml` or other converters.

## Markdown job files (`scraper/jobs/<stem>.md`)

- `<stem>` = `job_scraper.core.markdown_export.filename_for(posting)` minus
  `.md`, i.e. `<site_id>-<listing_id>-<slugified title>`. Raw pages
  (`raw/<site>/<stem>.html|json`) and, from this epic on, screenshots
  (`screenshots/<stem>.png`) use the same stem.
- Layout: `# Title`, blank line, `- Key: value` bullets (the first is
  `- Source: <url>`), blank line, `## Description`, blank line, body,
  optional `## Scrape note`. The app parses the bullets with the regex
  `^- (\w[\w ]*):\s*(.+)$` and extracts the description as everything between
  `## Description` and the next level-2 heading.
- Because of that, description bodies must NEVER contain a line that starts
  with `## ` (exactly two hashes). Headings inside a description use `###` or
  deeper.

## Commits

`E13-S<nn>: <imperative summary>` as in Appendix A, in the repo the story
names.
