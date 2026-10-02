# E13-S13 — working_nomads: store the human job-ad URL

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Make `source_url` for Working Nomads postings the page a human reads (`https://www.workingnomads.com/jobs/<slug>`), not `https://www.workingnomads.com/job/go/<id>/` which redirects to the employer's apply link.

## Context

- `scraper/job_scraper/sites/working_nomads.py`: `list_postings` fetches the API `https://www.workingnomads.com/api/exposed_jobs/` (JSON list) and yields `ListingStub(listing_id=<id from /job/go/<id>/>, detail_url=<the /job/go/<id>/ url>, title)`, caching each job dict in `self._job_cache[listing_id]` (keys: `url, title, description, company_name, category_name, tags, location, pub_date`). `parse_detail(stub, page)` reads only that cache and sets `source_url=stub.detail_url` (the redirect URL). The pipeline also downloads `stub.detail_url` as the "page" (raw capture) — which follows the redirect, so most raw pages are the EMPLOYER's site, not Working Nomads.
- Findings from `scraper/raw/working_nomads/` (52 files): only 4 raw pages are Working Nomads' own pages with `<link rel="canonical" href="https://www.workingnomads.com/jobs/<slug>">` and `og:url`, e.g. `working_nomads-1785901-face-deduplication-collection.html` (79 KB) with canonical `https://www.workingnomads.com/jobs/face-deduplication-collection-telus-digital` (job: title "Face Deduplication Collection", company "TELUS Digital"). The other 48 are employer pages without such a tag. So the human URL cannot generally be read from the page; the one observed slug pattern is `slugify(title) + "-" + slugify(company_name)`.
- The API listing fixture is `tests/fixtures/working_nomads/listing.json` (5 jobs, no slugs). `tests/test_working_nomads.py` has `load_fixture()` and patches `job_scraper.sites.working_nomads.fetch_page`.
- `parse_detail` cannot be rebuilt offline from raw (it needs the listing cache) — see E13-S09; a full re-scrape is what repairs existing jobs.
- This file is also edited by E13-S05 (description) and E13-S29 (screenshot selector); run in order.

## Files to create/modify

- `scraper/job_scraper/sites/working_nomads.py`
- `scraper/tests/test_working_nomads.py`
- `scraper/tests/fixtures/working_nomads/detail_1785901.html` (new): a copy of `scraper/raw/working_nomads/working_nomads-1785901-face-deduplication-collection.html` (also needed later by E13-S29).

## Acceptance criteria

- INVESTIGATE FIRST, offline: grep the four raw pages that carry a `rel="canonical"` Working Nomads URL (`grep -l 'rel="canonical" href="https://www.workingnomads.com/jobs/' raw/working_nomads/*.html`), and for each one find the matching job in the DB (`sqlite3 scraper.db "select title, client from jobs where site_id='working_nomads' and listing_id='<id>'"`, read-only). Check whether `slugify(title) + "-" + slugify(client)` (use `job_scraper.core.markdown_export.slugify`) reproduces each canonical slug exactly.
- If the rule reproduces ALL four canonical slugs: `parse_detail` sets `source_url` to `f"{base_url}/jobs/{slugify(title)}-{slugify(company_name)}"`; and if `page` is a Working Nomads page that has a canonical `https://www.workingnomads.com/jobs/...` link, that canonical value is used instead (it wins over the computed one). `stub.detail_url` stays the `/job/go/` URL (it is what the pipeline fetches for raw capture).
- If the rule fails for any of the four: STOP and report which ones failed and the real slugs — do not guess a different scheme.
- Tests in `tests/test_working_nomads.py`: (a) with the four known (title, company, canonical) triples as test data, the computed URL equals the canonical; (b) `parse_detail` given the `detail_1785901.html` fixture page returns `source_url == "https://www.workingnomads.com/jobs/face-deduplication-collection-telus-digital"` (seed `adapter._job_cache["1785901"]` with `{"title": "Face Deduplication Collection", "company_name": "TELUS Digital", ...}`); (c) for every job in `listing.json` the resulting `source_url` starts with `https://www.workingnomads.com/jobs/` and contains neither `/job/go/` nor `/api/`.
- Existing tests that asserted `source_url == ".../job/go/<id>/"` are updated to the new value (the `listing_id` and `detail_url` assertions stay).
- `uv run pytest` passes.

## Definition of done

- The commit message states the verification result (4/4 slugs reproduced).
- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S13: working_nomads: store human job-ad URL`.
- `docs/todo.md` item for E13-S13 checked off, committed in the JOB-HUNTER repo (`Mark E13-S13 as done in todo`).
