# Appendix C — screenshot-fix standards (Epic 14)

Applies to every Epic 14 story. Read together with `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` (B wins for `scraper/` work). Do not repeat this content in tickets — reference it.

## Repos and commits

- Stories that change `scraper/` code, tests or fixtures commit in the SCRAPER repo: `git -C scraper add <files> && git -C scraper commit -m "E14-S<nn>: <imperative summary>"`.
- The QA story (E14-S18) writes only `docs/` and commits in the JOB-HUNTER repo.
- Commit-message body for every site story has one line `<site_id>: <selector / hide list / pre-action / BLOCKED: reason>`.
- Never edit `docs/todo.md` (the orchestrator ticks it). Never use git checkout/restore/stash/reset/clean.

## Tests

- Run ONLY the test files the ticket touches (`cd scraper && uv run pytest tests/test_x.py -q`). A separate gate agent runs the full suites.
- pytest runs with `--disable-socket`. Any test that starts a real browser must be marked `@pytest.mark.enable_socket` AND `needs_browser` (copy the decorator pattern from `scraper/tests/test_screenshots.py`) AND load only `file://` pages (write an HTML file under `tmp_path`, pass `page.as_uri()`). Tests never touch a real site.
- Adapter selector tests parse saved fixtures with `BeautifulSoup(html, "html.parser").select(...)` (soupsieve): the selector must stay valid for both soupsieve and Playwright (no `:contains()`, `:has-text()`, `text=`).
- When the live DOM differs from the saved fixture (client-rendered pages), save the probe's rendered HTML as a new, trimmed fixture `scraper/tests/fixtures/<site>/rendered_<id>.html` (under 50 KB, no personal data, scripts removed) and test against that.

## Probe protocol (selector / overlay stories)

The saved fixtures are what the server sent, not what Chromium renders, so every selector or hide-list change is first checked once against the live page:

1. Pick ONE live URL: `sqlite3 -readonly scraper/scraper.db "select source_url from jobs where site_id='<id>' and is_stale=0 and duplicate_of is null limit 1"` (read-only; never write to `scraper.db`, `jobs/`, `raw/`, `screenshots/`). If no non-stale row exists, use the `- Source:` of a recent `scraper/jobs/<id>-*.md` and say so in the commit body.
2. Write a throwaway script in the SESSION SCRATCHPAD directory (given in your system prompt), never in the repo. Use `patchright.sync_api` when the adapter's `fetch_strategy` is `STEALTH`, else `playwright.sync_api`; `headless=True`; viewport `{"width": 1280, "height": 1600}` (same as `capture_element`); `wait_until="domcontentloaded"`; ONE page load; a hard 45 s timeout; close the browser in `finally`.
3. The script prints: HTTP status, final URL, `page.title()`, `page.locator(<candidate>).count()` for each candidate selector, and the visible fixed/sticky elements via
   `page.evaluate("[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e);return (s.position==='fixed'||s.position==='sticky')&&e.offsetHeight>0}).map(e=>e.tagName+'#'+e.id+'.'+String(e.className).slice(0,60)+' '+JSON.stringify(e.getBoundingClientRect()))")`;
   it also saves `page.content()` to a scratchpad `.html` and one PNG of the candidate element (apply the proposed hide CSS first), then you open the PNG with the Read tool and say in the commit body whether it shows only the job ad.
4. Politeness: one run per site per story (a second run only if the first was inconclusive), no loops, no crawling, `--ignore-robots` never, and Cloudflare/bot walls are NEVER bypassed (no solving, no stealth tricks beyond what `fetch_strategy` already is). If the probe is blocked or the browser is unavailable (`browser_available()` False), record `BLOCKED: <why>` in the commit body, change nothing for that site except a test pinning the current state, and stop.
5. Then make the code change, then add the fixture-based unit test (and, for shared mechanisms, the `file://` browser test).

## Safety rules for live runs (E14-S18 and any probe)

Back up first (`scraper/scraper.db`, `jobs/`, `raw/`, `screenshots/` into a dated folder under `/media/baz/MonkeyWorks/backups/`), one heavy process at a time, polite delays (default `--delay` of the backfill, never lowered), `--ignore-robots` never, the owner's app on port 5000 untouched (own app on port 5001 only). Ask the owner before starting any run expected to take more than 1 hour or to be heavy on the machine (13 GB RAM; `~/.cache` lands on the crowded `/media/baz/MonkeyWorks` drive).
