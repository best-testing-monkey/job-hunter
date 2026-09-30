# E5-S01 — Matching engine subprocess wrapper

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Provide a function that runs `resume-matcher/job_matcher.py --mode embed` as a subprocess against a given resume and the current job pool, returning parsed results.

## Context

- Depends on E1-S01 only — independent of E2/E3/E4, can be built in parallel with those.
- `resume-matcher/job_matcher.py` (sibling repo, **do not edit it**) CLI usage:
  `python job_matcher.py --resume <path> --jobs "<glob>" --mode embed --min-strong 0.0 --out <file>`
- It must run under the dedicated venv at `~/.venvs/resume-matcher/bin/python` (that venv has `torch`/`transformers`; this app's own venv does not and must not gain those dependencies — see Appendix A).
- It must run with **working directory set to `resume-matcher/`** — the jobs glob (`"../scraper/jobs/*.md"`) is relative to that directory, matching how it's invoked everywhere else in this project.
- Output (`--out` file) is JSONL, one line per (resume, job) pair, shape: `{"resume_file": "...", "job_file": "...", "probs": {"similarity": <float>}, "top": "similarity"}`.

## Files to create

- `app/webapp/matcher.py` (new)
- `app/tests/test_matcher.py` (new)

## Functions to add to `matcher.py`

- `run_embed_match(resume_path: str, jobs_glob: str = "../scraper/jobs/*.md") -> list[dict]`:
  - Resolves `resume_matcher_dir` relative to this file's location (same `parents[2]`-from-`app/webapp/` pattern as `jobs.py` in E4-S01, pointing at `resume-matcher/` instead).
  - Creates a temp file path for `--out` (use `tempfile`).
  - Runs `subprocess.run([os.path.expanduser("~/.venvs/resume-matcher/bin/python"), "job_matcher.py", "--resume", resume_path, "--jobs", jobs_glob, "--mode", "embed", "--min-strong", "0.0", "--out", <temp_path>], cwd=resume_matcher_dir, check=True)`.
  - Reads the temp file, parses each JSONL line, and returns a list of dicts shaped `{"job_file": <str>, "score": <float>}` (flattening `probs.similarity` into a top-level `score` key — callers shouldn't need to know the raw JSONL shape).
  - Deletes the temp file before returning (or on any exception — use `try/finally`).

## Acceptance criteria

- Test mocks `subprocess.run` (`unittest.mock.patch`) so it doesn't actually invoke the real ML pipeline — instead, the mock's side effect writes a small fake JSONL (2-3 lines matching the real shape above) to the `--out` path it was called with, so `run_embed_match` has something real to parse.
- Test asserts `run_embed_match` returns a list of dicts with `job_file` and `score` keys matching the fake JSONL's content.
- Test asserts the subprocess was invoked with `cwd` set to the `resume-matcher` directory and the interpreter path containing `.venvs/resume-matcher`.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E5-S01: Add matching engine subprocess wrapper`.
- `docs/todo.md` item for E5-S01 checked off.
