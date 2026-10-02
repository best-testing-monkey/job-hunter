# E13-S16 — Audit source URLs: arc_dev, circle8, djinni, freelancer_com

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Audit 4 adapters (arc_dev, circle8, djinni, freelancer_com) so that `source_url` is a human-readable job-ad page, fixing and testing each.

## Context

- Rule: `source_url` (rendered as `- Source:` in the Markdown and shown to the user as "View original posting") must be the page a human opens in a browser to READ the job ad. It must NOT be an apply form (`/apply`, `/solliciteer`, `/sollicit`), a redirect or tracker (`/go/`, `/out/`, `/redirect`, `?utm_`), an API/JSON endpoint (`/api/`, `/wp-json/`, `.json`), or an overview/listing page shared by many jobs.
- How `source_url` is set: every adapter in `scraper/job_scraper/sites/<site_id>.py` does `source_url=stub.detail_url` (a few build it from other data); `stub.detail_url` is created in that adapter's `list_postings` (listing page link, sitemap `<loc>`, or API field).
- Evidence sources, all offline: the adapter code, `tests/fixtures/<site>/` (listing + detail pages: check each detail page's `<link rel="canonical">`, `og:url`, JSON-LD `url`), and read-only examples of stored values: `sqlite3 scraper/scraper.db "select source_url from jobs where site_id='<site_id>' limit 5"`.
- Fixed in other stories (do not touch): working_nomads (E13-S13), stone_interim (E13-S14), flexvalue (E13-S15).
- If a fix needs a URL that only the listing page carries, cache it in `list_postings` (see how E13-S14 does `_link_cache`) AND, when the detail page itself carries the true URL (canonical/og:url/JSON-LD), prefer deriving it in `parse_detail` so the offline `rebuild` command (E13-S09/S10) repairs existing jobs.
- Adapter-specific leads (verify, don't assume):
  - arc_dev: `urljoin(base_url, href)`; stored `https://arc.dev/remote-jobs/j/<slug>-<id>` — likely fine.
  - circle8: stored `https://www.circle8.nl/opdracht/<slug>_<VNR-id>` with `%2C`/`%26` escapes; `parse_detail` builds a `JobPosting` in two places with `source_url` set from `stub.detail_url` (and once `source_url=""` then patched) — check both paths end with the real URL.
  - djinni: stored `https://djinni.co/jobs/<id>-<slug>/`; check JSON-LD `url` / canonical in `tests/fixtures/djinni/detail_*.html`.
  - freelancer_com: stored `https://www.freelancer.com/projects/<category>/<slug>`; check canonical in the detail fixture.

## Files to create/modify

- `scraper/job_scraper/sites/arc_dev.py` (only if a fix is needed), `scraper/tests/test_arc_dev.py`
- `scraper/job_scraper/sites/circle8.py` (only if a fix is needed), `scraper/tests/test_circle8.py`
- `scraper/job_scraper/sites/djinni.py` (only if a fix is needed), `scraper/tests/test_djinni.py`
- `scraper/job_scraper/sites/freelancer_com.py` (only if a fix is needed), `scraper/tests/test_freelancer_com.py`

## Acceptance criteria

For EACH adapter (arc_dev, circle8, djinni, freelancer_com):
- The implementer has inspected the adapter and its fixtures and recorded one line per adapter in the commit message body: `<site_id>: OK (<evidence>)` or `<site_id>: FIXED (<old pattern> -> <new pattern>)` or `<site_id>: LIMITATION (<why no per-ad URL exists>)`.
- If the stored URL was not a human ad page it is fixed in the adapter, and the existing fixture-based tests are updated to the new value.
- A new test named `test_source_url_is_human_ad_page` in `tests/test_<site_id>.py` runs `parse_detail` on an existing detail fixture and asserts the exact expected `source_url` shape with a regex for that site (e.g. `^https://www\.example\.nl/vacature/[a-z0-9-]+/$`) AND that it contains none of: `/apply`, `/go/`, `/api/`, `/wp-json/`, `.json`, `?utm_`, `/redirect`.
- Where `listing.html`/`listing.*` fixtures exist, a second assertion checks every `list_postings()` stub's `detail_url` has the same shape (skip for sites whose `list_postings` needs several pages).
- Nothing in the audited adapters other than URL handling changes.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S16: Audit source URLs: arc_dev, circle8, djinni, freelancer_com`.
- `docs/todo.md` item for E13-S16 checked off, committed in the JOB-HUNTER repo (`Mark E13-S16 as done in todo`).
