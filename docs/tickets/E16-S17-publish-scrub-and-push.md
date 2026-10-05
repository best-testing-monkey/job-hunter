# E16-S17 — Publish runbook: scrub personal data, commit source files, push scraper and resume-matcher

See `APPENDIX-A-standards.md` and `APPENDIX-B-scraper-standards.md` (git rules: never checkout/restore/stash/reset/clean, never `git add -A` in a repo with someone else's uncommitted files). No code is written in this story. It is the LAST story, after E16-S16 (QA), and the only story after GATE-6 allowed one full scraper suite run (once, at step A6). Owner request: "commit and push all changes".

## Goal

Everything unpushed in `scraper/` and `resume-matcher/` reaches GitHub without third-party personal data or secrets; `job-hunter` (no remote) is committed locally.

## Context

- `scraper/` is PUBLIC (`git@github.com:best-testing-monkey/job-scraper.git`). About 63 commits are unpushed (`git -C scraper log origin/main..HEAD --oneline | wc -l`; origin/main HEAD was `472c91b` when this ticket was written: confirm with `git -C scraper ls-remote origin HEAD` and `git -C scraper rev-parse origin/main`, use whatever it prints as BASE). Test fixtures contain real recruiter personal data. Known hits (`git grep` in `tests/fixtures`): a named recruiter address at telusdigital.com (`working_nomads/detail_1785901.html`), a named recruiter address at stone-technology.nl (`stone_interim/detail_4893_api_GetVacancy.json`, `stone_interim/rendered_3783.html`), a Dutch mobile number in those stone_interim files (find it with `git grep -nE '\+31 ?6'`), and name-based recruiter emails in circle8 and sevenstars fixtures (first-name.last-name@circle8.nl, first-name@sevenstars.nl, first-name.last-name@synprofs.nl; the full set comes from the scan). Generic company mailboxes (`info@`, `hello@`, `advertising@`, `tech@`, `contact@`, `support@`) are NOT personal and are kept. Phone numbers also appear as `tel:`/`+31`/`0031`/`06` patterns in circle8, sevenstars, stone_interim, freelancermap, headfirst, freelancer_com, pro_act, hero, synprofs, tender_link, freelance_nl and iamexpat fixtures; plain numeric IDs are not phone numbers (a loose digit regex gives hundreds of false hits: judge each hit family by context).
- `resume-matcher/` is PUBLIC (`github.com/best-testing-monkey/resume-matcher`), 2 unpushed commits from another session, plus uncommitted: modified `AGENTS.md`, `job_matcher.py`, untracked `CLAUDE.md`, `build_report.py` (the job-hunter app imports `build_report.parse_job`), and generated data (`embeddings_cpu.sqlite`, `embeddings_gpu.sqlite`, `results_*.jsonl`, `jobs_by_embed_score.txt`, `reports/`).
- `job-hunter/` (the repo this file lives in) has NO remote: do not create a repository and do not add a remote; report that to the owner.
- A sibling session may have added commits or uncommitted files meanwhile: re-check `git status` and `git log` in each repo first; include sibling work only if it is already committed.

## Files to create/modify

- `scraper/tests/fixtures/**` (scrubbed through history rewrite, then a final working-tree check)
- `resume-matcher/.gitignore`, `resume-matcher/AGENTS.md`, `job_matcher.py`, `CLAUDE.md`, `build_report.py` (commit only)
- `docs/todo.md`, `docs/tickets/*`, `docs/e16-qa-results.md` and any other changed docs in job-hunter (commit only)
- a throwaway script `scrub.py` in the SESSION SCRATCHPAD (never in a repo)

## Part A — scraper (scrub first, then push)

1. `git -C scraper status --short` must be empty (otherwise stop and report). `git -C scraper branch backup-before-scrub` (local only; never pushed). Confirm BASE as above.
2. Scan everything that would be pushed: `git -C scraper diff BASE..HEAD` plus the added files, for: emails (`[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`), phone patterns (`\+31`, `0031`, `\b06[ -]?\d`, `tel:`), `Tim Jansen`, `gmail`, and secret patterns (`api[_-]?key`, `secret`, `token`, `password`, `BEGIN .* PRIVATE KEY`, `.env`, `Bearer `). Produce the list of distinct emails with counts and the phone hit families; classify each as generic (keep) or personal (scrub). `Tim Jansen`/`gmail` hits in scraper files must be listed for the owner (his own name/email in docs is the owner's call: report, do not scrub unless inside a fixture).
3. Before changing anything, `grep` the scraper tests (`tests/*.py`) for every personal local part and phone you will replace; any assertion on them must be updated in the same rewrite (use fixtures-only replacements of equal meaning, e.g. a recruiter email asserted in a test becomes `recruiter@example.com` in test and fixture).
4. Write `scrub.py` in the scratchpad: walks `tests/fixtures` (text files only, `errors="surrogateescape"` round trip, no change to files without hits), replaces every personal email with `recruiter@example.com` (company-owned names in a `jobs@` style role mailbox -> `jobs@example.com`), phone numbers with `+31 6 00000000` (spaced form) or `+31600000000` (compact form, `tel:` links), keeping the surrounding markup/JSON valid. Run it once on a COPY of one history commit's fixtures to check the result parses (`python -m json.tool` for the json files).
5. Rewrite ONLY the unpushed range: `git -C scraper filter-branch --tree-filter 'python3 <abs path>/scrub.py' -- BASE..HEAD`. (filter-branch touches many commits on a slow NTFS drive: run it in the background with a log, one heavy process at a time.) Pushed history before BASE stays untouched. Do not use `--force` on any push. Do not delete `refs/original/` until A6 passes.
6. Verify: (a) `git -C scraper diff backup-before-scrub HEAD --stat` lists ONLY files under `tests/fixtures/` (and any test `.py` assertions updated in step 3); (b) re-run the step-2 scan over `BASE..HEAD` (`git log -p BASE..HEAD`), personal hits must be 0 in every commit, not just HEAD; (c) the same `git log -p origin-pushed-range` was not rewritten: `git -C scraper merge-base --is-ancestor BASE HEAD` succeeds and `git -C scraper rev-parse BASE` unchanged; (d) the full scraper suite passes once: `cd scraper && uv run pytest -q` (the one allowed full run in this story; if tests fail because of the scrub, fix the fixtures/tests with a new commit and re-scan, then repeat only the failing files).
7. Only after A6 is green: `git -C scraper push origin main` (plain push, never `--force`, never `--no-verify`). If it is rejected (non-fast-forward, hook, permission), do not force and do not retry with other flags: report the exact error and stop Part A.

## Part B — resume-matcher

1. `git -C resume-matcher status --short` and `git log origin/main..HEAD --oneline`; the 2 unpushed commits (city travel-time module, intercity overrides) must be scanned like step A2 (`git diff origin/main..HEAD`) for personal data and secrets.
2. Add `embeddings_*.sqlite` to `resume-matcher/.gitignore` (append one line if absent).
3. `git add .gitignore AGENTS.md job_matcher.py CLAUDE.md build_report.py` (explicit paths only, never `-A`), scan the staged diff (`git diff --cached`) with the same regexes (a CV, real name or phone in `AGENTS.md`/`CLAUDE.md` is reported to the owner and NOT committed until he decides), then commit `Add build_report, agent notes and ignore embedding databases`. The generated data (`embeddings_*.sqlite`, `results_*.jsonl`, `jobs_by_embed_score.txt`, `reports/`) is never staged; list what stays untracked.
4. `git -C resume-matcher push origin main` (plain). On rejection report and stop; never force.

## Part C — job-hunter (local commit only)

1. `git status --short`; `git log --oneline -5`. Include the sibling session's work only if it is already committed (its two commits are). Stage explicit paths of this epic's docs (`docs/todo.md`, `docs/tickets/E16-*`, `docs/e16-qa-results.md`, other changed docs) and commit `E16-S17: Record Epic 16 breakdown, QA results and publish run`. Never `git add -A`; leave unrelated uncommitted files of other sessions alone and list them.
2. Do NOT create a repository or add a remote: report "job-hunter has no remote configured; nothing pushed" to the owner.

## Acceptance criteria

- Scraper: personal-data scan over `BASE..HEAD` finds 0 personal emails/phones in every commit; `git diff backup-before-scrub HEAD --stat` shows only fixture (and necessary test-assertion) changes; full suite passes; the push is accepted without force, or the exact rejection is reported with nothing forced.
- resume-matcher: commit contains exactly the five named files; the generated data is untracked/ignored; push accepted or reported.
- job-hunter: committed locally; no remote was added; the final message lists every repo's HEAD hash, push status, the personal-data hit families found (counts only, no real values copied into docs), the `backup-before-scrub` branch name, and anything left for the owner (own name in docs, untracked generated data, no remote).
- No real recruiter personal data (emails, phones, names) is written into any doc or commit message in this story.

## Definition of done

- Part A to C done as above; the three repos committed as named (scraper rewrite keeps the original commit messages; the new commits use `E16-S17: ...`).
- The orchestrator ticks `docs/todo.md`.
