# job-hunter

A personal tool for matching resumes against scraped job postings and
tracking results over time.

## Layout

This repo (`job-hunter/`) holds the web app. Two sibling directories are
separate projects with their own git history and remotes — **not**
submodules of this repo yet (see `docs/DESIGN_DOC.md`'s Problem section):

- `scraper/` — scrapes job postings into `scraper/jobs/*.md`. Own repo,
  own README, own `uv`-managed venv.
- `resume-matcher/` — scores a resume against job postings (`job_matcher.py`).
  Own repo, own README, own **dedicated venv at `~/.venvs/resume-matcher`**
  (heavy ML dependencies: torch, transformers, llama-cpp-python — see
  `resume-matcher/README.md` for how that venv was set up).
- `app/` — this project's own code: a Flask app that reads job postings from
  `scraper/jobs/`, shells out to `resume-matcher/job_matcher.py` (via its
  dedicated venv) to compute matches, and persists results in SQLite so they
  survive across runs instead of one-off report files.

`app/` has its **own** lightweight `uv`-managed venv (Flask only — no ML
dependencies). It never imports torch/transformers directly; it calls
`resume-matcher`'s venv as a subprocess. See `docs/DESIGN_DOC.md` for the
full architecture.

## Prerequisites

1. `scraper/jobs/*.md` must already exist — run a scrape first if it
   doesn't (see `scraper/README.md`).
2. `resume-matcher`'s dedicated venv must exist at `~/.venvs/resume-matcher`
   with its dependencies installed (see `resume-matcher/README.md`'s
   Requirements section — GPU or CPU install, both work). `app/` calls this
   venv's interpreter directly by path; it is not managed by this repo.
3. [`uv`](https://docs.astral.sh/uv/) installed, for `app/`'s own venv.

## Running the app

```bash
cd app
uv sync                          # installs Flask into app/'s own venv
uv run flask --app webapp run    # http://127.0.0.1:5000
```

Then, in the browser:

1. Go to `/` and register a resume (a name + the path to an existing resume
   markdown file, e.g. `../resume-matcher/resumes/cv_1000.md`).
2. Open the resume's page and click **Rematch**. This runs in the
   background (via `resume-matcher`'s venv) — reload the page after it
   finishes (a full run against ~1000 postings takes a few minutes cold, or
   seconds if the embedding cache is warm) to see the scored match list.

## Tests

```bash
cd app
uv run pytest tests/ -q
```

## Project docs

- `docs/DESIGN_DOC.md` — architecture, data model, visual design tokens.
- `docs/todo.md` / `docs/tickets/` — the story breakdown this first slice
  was built from (`/breakdown` + `/run-stories`).
