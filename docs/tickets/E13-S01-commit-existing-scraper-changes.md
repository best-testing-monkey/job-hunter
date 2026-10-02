# E13-S01 — Inspect and commit the uncommitted scraper work

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

Make sure the large pile of UNCOMMITTED work already sitting in `scraper/` is understood and safely committed before any Epic 13 story builds on it.

## Context

- Run `git -C scraper status --short` and `git -C scraper diff --stat`. At the time this epic was written there were 47 modified files plus untracked files; this is NOT a small diff. It is the previous session's work (see `scraper/docs/handoff-202609301625.md`, untracked):
  - a new `workplace` field (Fully Remote / Hybrid / On-site) on `JobPosting` (`job_scraper/core/models.py`, included in `content_hash`) and rendered by `core/markdown_export.py` as a `- Workplace:` bullet, with a shared classifier `job_scraper/core/workplace.py` (new, untracked) used by all 20 adapters in `job_scraper/sites/*.py`;
  - raw page storage: new `job_scraper/core/raw_export.py` (untracked), `raw_format` attribute on `sites/base.py`, `--raw-dir/--no-raw` flags in `cli.py`, `raw_dir` param in `pipeline.py` (`run_site`, `run`), `raw/` added to `.gitignore`;
  - new tests: `tests/test_raw_export.py`, `tests/test_workplace.py`, new fixtures `tests/fixtures/djinni/detail_850338.html`, `tests/fixtures/wearedevelopers/detail_1343363.html`, `detail_2203015.html`, plus edits to 20 adapter test files and `tests/test_pipeline.py`.
- Everything later in Epic 13 (rebuild-from-raw, source URLs, screenshots) depends on `raw/`, `raw_format` and `workplace` existing in the repo history.
- The scraper's last commit is `472c91b Add session handoff docs`.

## Files to create/modify

No source files are edited by this story — it only reads, tests and commits.
- Possibly `scraper/.gitignore` (already modified; leave as is).

## Acceptance criteria

- FIRST, inspect: run `git -C scraper diff` and read it (at minimum `cli.py`, `pipeline.py`, `core/markdown_export.py`, `core/models.py`, `sites/base.py`, `.gitignore`, and two or three adapter diffs). Do NOT run `git checkout`, `git restore`, `git stash`, `git reset` or `git clean` — nothing may be discarded.
- If anything in the diff looks unfinished, broken, or unrelated to workplace/raw storage (debug prints, stray files, secrets), STOP and ask the owner what to do. Do not discard it and do not silently commit it.
- `uv run pytest` from `scraper/` passes with zero failures on the working tree as it stands (if it fails, stop and report the failing tests; do not "fix" by reverting).
- After the owner-ok (or if nothing looked suspicious), commit everything in the scraper repo in two commits: (1) raw storage: `core/raw_export.py`, `tests/test_raw_export.py`, `.gitignore`, `sites/base.py`, `cli.py`, `pipeline.py`, `tests/test_pipeline.py`; message `E13-S01: Commit raw page storage`. (2) everything else (workplace field, classifier, adapter changes, fixtures, tests, `docs/handoff-202609301625.md`); message `E13-S01: Commit workplace classification across all adapters`. (If the two sets cannot be separated cleanly because `pipeline.py` etc. interleave, a single commit `E13-S01: Commit uncommitted workplace + raw-storage work` is acceptable.)
- Afterwards `git -C scraper status --short` prints nothing (clean tree; ignored dirs `jobs/`, `raw/`, `scraper.db` don't show).
- `git -C scraper log --oneline -3` shows the new commit(s) on top of `472c91b`.

## Definition of done

- Owner was asked/informed about the pre-existing uncommitted work; nothing was discarded.
- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S01: Commit uncommitted workplace + raw-storage work`.
- `docs/todo.md` item for E13-S01 checked off, committed in the JOB-HUNTER repo (`Mark E13-S01 as done in todo`).
