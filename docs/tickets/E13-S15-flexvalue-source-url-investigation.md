# E13-S15 — flexvalue: verify the stored URL is the human ad page

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Decide, from saved evidence, whether `https://aanvragen.flexvalue.nl/careers/6605/jobs/<id>-<Title>` is a human-readable job ad (not the application portal/form) and encode the decision in a test.

## Context

- `scraper/job_scraper/sites/flexvalue.py`: `base_url = "https://aanvragen.flexvalue.nl"` (the host name says "aanvragen" = "apply"), `LISTING_URL = ".../careers/6605"`; `list_postings` builds `detail_url = base_url + href` for each `a.table-row` and `parse_detail` stores `source_url=stub.detail_url`. Stored example: `https://aanvragen.flexvalue.nl/careers/6605/jobs/1065407-Java-Devops-Engineer`.
- Evidence already seen in `scraper/raw/flexvalue/flexvalue-1065407-java-devops-engineer.html` and the fixture `tests/fixtures/flexvalue/detail_1065407.html`: the page is a CATS (catsone.com) careers-portal page (assets from `cp.static.catsone.com`), has `<div class="job-description">` with the full ad, `og:url` is `http://aanvragen.flexvalue.nl/careers/6605/jobs/1065407-Java-Devops-Engineer` (http, no `/apply`), and the apply flow is a separate path `/careers/6605/jobs/1065407-Java-Devops-Engineer/apply`. So the stored URL looks like the public ad page, hosted on the vendor's portal.
- Tests: `tests/test_flexvalue.py`.
- This file is also edited by E13-S08 (description) and E13-S28 (selector).

## Files to create/modify

- `scraper/job_scraper/sites/flexvalue.py` (only if a change is warranted)
- `scraper/tests/test_flexvalue.py`
- `scraper/README.md` — one sentence under the `flexvalue` bullet: "job URLs point at the public careers-portal ad page; the apply form lives under `/apply`".

## Acceptance criteria

- Inspect the fixture and decide: (1) does the stored URL load a page that contains the full job description (yes per the evidence; confirm via the fixture: `div.job-description` non-empty)? (2) Does the page's own apply link point to a different path (`.../apply`)? (3) Is there a link to a per-job page on a different, more public host (e.g. flexvalue.nl) anywhere in the fixture/listing (`grep -o 'https\?://[^"]*flexvalue[^"]*' tests/fixtures/flexvalue/*.html | sort -u`)? If a more public per-job URL exists in the page data, switch `source_url` to it; otherwise keep the portal URL.
- Normalize the scheme: `source_url` always starts with `https://`.
- Test (`test_flexvalue.py`): `parse_detail` on the fixture gives a `source_url` matching `^https://aanvragen\.flexvalue\.nl/careers/\d+/jobs/\d+-[^/]+$` (no trailing `/apply`, no query string); and the description is non-empty.
- The commit message records the conclusion in one sentence (kept portal URL because ... / switched to ... because ...), including any residual uncertainty because no live check is possible offline.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S15: flexvalue: verify and pin source URL shape`.
- `docs/todo.md` item for E13-S15 checked off, committed in the JOB-HUNTER repo (`Mark E13-S15 as done in todo`).
