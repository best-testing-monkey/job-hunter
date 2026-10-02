# E13-S14 — stone_interim: store the human job-ad URL

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Make `source_url` for Stone Interim postings the human page `https://www.stone-interim.nl/opdrachten/id/<id>/<Title+With+Plus>/<ContractType>/` instead of the JSON API endpoint `.../api/v1/WordPress/GetVacancy/<id>`.

## Context

- `scraper/job_scraper/sites/stone_interim.py`: `list_postings` POSTs to the overview API and for each item in `data["Items"]` has `item["Title"]` and `item["LinkUrl"]` (e.g. `/opdrachten/id/4893/Interim+Supply+Chain+Manager/Interim/`, the human page) — it extracts the id with `re.search(r"/id/(\d+)/", link_url)` but then throws `LinkUrl` away and builds `detail_url = ".../api/v1/WordPress/GetVacancy/{id}"`, which is also what `parse_detail` stores as `source_url`. The pipeline downloads `detail_url` (JSON, `raw_format = "json"`) — keep that fetch.
- `parse_detail(stub, page)` gets the vacancy JSON: `TitleInformation` (note: may have a trailing space, e.g. `"Finance Consultant "`), `ToVacancy.CRVacancy.ToContractTypeNode.CRDataNode.Value` (contract type, e.g. `"Interim"`).
- Fixtures: `tests/fixtures/stone_interim/` has `listing_api_GetOverviewItems.json` (overview API response with `LinkUrl`s), `detail_4893_api_GetVacancy.json` (detail JSON for id 4893), `detail_4893.html` (the human page), `vacancies_sitemap.xml` (contains `https://www.stone-interim.nl/opdrachten/id/4893/Interim+Supply+Chain+Manager/Interim/`). Tests in `tests/test_stone_interim.py`.
- Offline rebuild (E13-S09) calls `parse_detail` with only the saved JSON and a stub whose `detail_url` is the old API URL, so `parse_detail` must be able to compute the human URL from the JSON alone; `list_postings` can additionally remember the authoritative `LinkUrl`.
- This file is also edited by E13-S05 (description) and E13-S29 (selector); run in order.

## Files to create/modify

- `scraper/job_scraper/sites/stone_interim.py`
- `scraper/tests/test_stone_interim.py`

## Acceptance criteria

- Add a pure helper (module-level or method) `human_url(listing_id: str, title: str, contract_type: str | None) -> str` returning `f"{base_url}/opdrachten/id/{listing_id}/{urllib.parse.quote_plus(title.strip())}/{contract_type}/"` (contract-type segment omitted if unknown). VERIFY it against the data first: for every item in `listing_api_GetOverviewItems.json`, `human_url(id, item["Title"], item["ContractType"]) == base_url + item["LinkUrl"]` — put this as a test. If it does not hold for every item, adjust the rule (e.g. which fields feed the title/contract segments) until it does; if you cannot find a rule that holds for all items, STOP and report.
- Also verify it with `detail_4893_api_GetVacancy.json` (title from `TitleInformation`, contract type from `ToContractTypeNode`) giving exactly `https://www.stone-interim.nl/opdrachten/id/4893/Interim+Supply+Chain+Manager/Interim/` (the sitemap URL) — a test.
- `list_postings` stores `self._link_cache[listing_id] = base_url + LinkUrl`; `parse_detail` uses the cached value when present, otherwise `human_url(...)` computed from the JSON. `stub.detail_url` is unchanged (still the GetVacancy API URL, used for fetching).
- Test: `parse_detail` on `detail_4893_api_GetVacancy.json` returns `source_url == "https://www.stone-interim.nl/opdrachten/id/4893/Interim+Supply+Chain+Manager/Interim/"` and `"/api/" not in source_url`; test: `list_postings` (with the overview POST patched as existing tests do) still yields stubs whose `detail_url` contains `/api/v1/WordPress/GetVacancy/`.
- Optional sanity (not a test): run `human_url` over all `raw/stone_interim/*.json` and confirm none raises.
- `uv run pytest` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S14: stone_interim: store human job-ad URL`.
- `docs/todo.md` item for E13-S14 checked off, committed in the JOB-HUNTER repo (`Mark E13-S14 as done in todo`).
