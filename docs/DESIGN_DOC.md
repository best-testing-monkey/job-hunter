# job-hunter app — design doc

## Problem

Matching a resume against scraped jobs today is a manual CLI workflow:
`resume-matcher/job_matcher.py --mode embed` scores a resume against
`scraper/jobs/*.md`, and `resume-matcher/build_report.py` turns the JSONL
output into a static markdown/HTML report. This works as a one-off POC, but
every run overwrites the last one — there's no persistent record of past
matches, no way to track more than one resume, and "check today's shortlist"
means re-opening a generated file rather than a live view.

The longer-term vision (from design conversation, not yet built) is a small
personal tool: CRUD of resumes, resume metadata, curated lists of
transferable skills, and a per-resume list of matches. This doc scopes only
the first slice — **per-resume match tracking as a local web app** — and
defers the rest (see Non-goals).

This app is a **new, separate project** at the `job-hunter` repo root
(sibling to `scraper/` and `resume-matcher/`, not nested inside either).
`scraper/` and `resume-matcher/` remain independent git repos with their own
remotes (`job-scraper`, `resume-matcher` on GitHub) — this project reads
their output/tooling but does not vendor or duplicate their code.
Converting them into formal git submodules of this repo is a separate,
not-yet-decided step (`scraper` currently has substantial uncommitted work)
and is out of scope for this build.

## Goals

- **Persistent match history**: a resume's match results live in a local
  SQLite database, not a throwaway JSONL/HTML file — re-running a match
  updates the record, it doesn't replace a file.
- **Reuse, don't duplicate, the existing scoring engine**:
  `resume-matcher/job_matcher.py`'s `--mode embed` path (the `Embedder`
  class) is the scoring engine. This app shells out to it as a subprocess
  (via its own dedicated venv, `~/.venvs/resume-matcher`) rather than
  importing torch/transformers into a plain web app's dependencies.
- **Reuse the existing job-metadata parsing**: `resume-matcher/build_report.py`
  already parses `scraper/jobs/*.md` into structured fields (title, source,
  client, location, workplace, site). Import and reuse `parse_job()` and
  `site_name()` from that module rather than re-implementing markdown
  parsing.
- **Read jobs from the existing source of truth**: `scraper/jobs/*.md` is
  read directly, live, at match time — no copying job data into this app's
  own storage.
- **A local web UI**, dark-only, matching a specific reference aesthetic
  (see Visual design tokens below) — this app is for one person (or a small
  team), run locally, no deployment/hosting concerns.

## Non-goals (this phase)

- **Resume CRUD** (add/edit/delete resume *content*, rich metadata beyond
  name+file path) — deferred to a later slice. This phase's minimal seam:
  a resume is "registered" with a name and a path to an existing markdown
  file (e.g. `resume-matcher/resumes/cv_1000.md`); no resume content editing.
  **Now in scope — see "Resume CRUD (second slice)" below.**
- **Transferable-skills curation/tagging** — deferred to a later slice.
- **Multi-user / auth** — single-user local tool.
- **Converting `scraper`/`resume-matcher` into git submodules** — separate
  decision, not part of this build.
- **Logit-read modes** (classify/category/rank/criteria) — v1 uses embed
  mode only (fast, cheap, already proven at this dataset's scale — see
  `resume-matcher/README.md`'s benchmarks). A "deep read" mode can be added
  later the same way it was hand-rolled once already in `build_report.py`'s
  history.
- **Job scraping itself** — entirely out of scope; `scraper/` is untouched
  by this work.

## Architecture

New project at `job-hunter/app/` — Python, `uv`-managed venv, **own**
lightweight dependencies (Flask, Jinja2 — no ML libraries):

```
app/
  pyproject.toml
  app/
    __init__.py          # Flask app factory
    db.py                 # sqlite3 connection + schema init
    routes.py              # Flask routes (or blueprints if it grows)
    matcher.py             # subprocess wrapper around job_matcher.py
    jobs.py                # thin wrapper importing resume-matcher's
                            #   build_report.parse_job / site_name
    templates/
      base.html             # shell: nav, dark theme, monospace chrome
      resumes.html           # resume list (route: /)
      resume_detail.html      # one resume's match list (route: /resumes/<id>)
    static/
      style.css               # design tokens as CSS custom properties
  tests/
    test_db.py
    test_matcher.py
    test_routes.py
```

### Data model (SQLite, `app/matches.db`, gitignored — local generated data)

```sql
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(id),
    job_file TEXT NOT NULL,
    title TEXT NOT NULL,
    site TEXT NOT NULL,
    location TEXT,
    workplace TEXT,          -- Fully Remote / Hybrid / On-site / NULL
    source_url TEXT,
    score REAL NOT NULL,
    computed_at TEXT NOT NULL,
    UNIQUE(resume_id, job_file)
);
```

A rematch run **upserts** rows (`ON CONFLICT (resume_id, job_file) DO
UPDATE`) keyed on `(resume_id, job_file)`, so re-running doesn't duplicate
rows and the `score`/`computed_at` simply reflect the latest run.

### Matching flow

1. User clicks "Rematch" on a resume's page (`POST /resumes/<id>/rematch`).
2. Flask spawns a background thread that shells out to:
   `~/.venvs/resume-matcher/bin/python resume-matcher/job_matcher.py
   --resume <file_path> --jobs "scraper/jobs/*.md" --mode embed
   --min-strong 0.0 --out <tmp-file>`
3. On completion, parse the JSONL output, look up each `job_file`'s metadata
   via `build_report.parse_job()`, and upsert into `matches`.
4. The resume's page shows a "last run: <time>, running: <bool>" status;
   simplest v1 implementation is a DB flag + a manual page refresh (no
   websockets/polling needed for a single-user local tool).

### Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | List registered resumes (name, match count, last run time) |
| POST | `/resumes` | Register a resume (name + file path only — not full CRUD) |
| GET | `/resumes/<id>` | One resume's match list: sortable by score, filterable by site/workplace, paginated |
| POST | `/resumes/<id>/rematch` | Trigger a fresh embed-mode match run (background thread) |

## Resume CRUD (second slice)

The first slice's "register a resume" is create-only and points at a file
the user must already have on disk somewhere else — not real CRUD. This
slice makes the app **own** resume content: create, edit, and delete a
resume's actual text from inside the tool, instead of just pointing at an
external path.

### What doesn't change

The matching flow (`matcher.run_embed_match`, `_run_rematch`, the whole
`POST /resumes/<id>/rematch` route from the first slice) is untouched.
`job_matcher.py` still needs a real file path to read, so `resumes.file_path`
stays in the schema and stays the thing the matcher subprocess is pointed
at — it just becomes **app-managed** instead of user-typed: the app writes
it under `app/instance/resumes/<id>.md` whenever content is created or
edited, and removes it on delete.

### Data model change

Add one column to the existing `resumes` table (additive — no existing
persisted rows to migrate, this app has no real users yet):

```sql
ALTER TABLE resumes ADD COLUMN content TEXT;
```

(`content` is the resume's markdown text, edited in the app. `file_path`
remains `NOT NULL UNIQUE`, computed by the app as
`<instance_path>/resumes/<id>.md` — never user-supplied going forward.)

### `db.py` changes

- `create_resume(conn, resumes_dir: str, name: str, content: str) -> int` —
  replaces `register_resume` (remove it; update its one call site in
  `routes.py` — don't leave both functions around). Inserts the row first
  (empty `file_path` placeholder) to get an autoincrement `id`, computes
  `Path(resumes_dir) / f"{id}.md"`, writes `content` to it, then `UPDATE`s
  the row's `file_path` to that path. Returns the `id`.
- `update_resume(conn, resume_id: int, name: str, content: str) -> None` —
  updates `name`/`content` in the DB, then rewrites the existing
  `file_path`'s file with the new `content` (the path itself doesn't
  change).
- `delete_resume(conn, resume_id: int) -> None` — deletes all rows in
  `matches` for this `resume_id`, deletes the `resumes` row, then removes
  the resume's file at its `file_path` (`Path(file_path).unlink(missing_ok=True)`
  — the file might already be gone; that's fine, not an error).

`resumes_dir` is a new Flask config value, `app.config["RESUMES_DIR"]`, set
in `create_app()` alongside the existing `DATABASE` config —
`os.path.join(app.instance_path, "resumes")`, created via
`os.makedirs(..., exist_ok=True)` the same way the instance folder already
is.

### Routes

| Method | Path | Purpose |
|---|---|---|
| POST | `/resumes` | **Changed**: now takes `name` + `content` (a textarea), not `file_path`. Calls `create_resume`. |
| GET | `/resumes/<id>/edit` | New — a form pre-filled with the resume's current `name`/`content`. |
| POST | `/resumes/<id>/edit` | New — calls `update_resume`, redirects to `/resumes/<id>`. |
| POST | `/resumes/<id>/delete` | New — calls `delete_resume`, redirects to `/`. Destructive — the delete button/form should have a client-side `confirm()` before submitting. |

### Verification

- `uv run pytest tests/ -q` — extend `test_db.py` for `create_resume`
  (writes a real file, sets `file_path` correctly), `update_resume`
  (rewrites content, same `file_path`), `delete_resume` (removes matches +
  resume row + file, tolerates an already-missing file).
- Manual: create a resume with real content through the UI, confirm the
  file exists on disk at the expected path with matching content; edit it
  and confirm the file's content changed; trigger a rematch and confirm it
  still works unmodified; delete it and confirm the file, DB row, and any
  matches are gone.

## Visual design tokens

Dark-only theme (no light mode, no toggle), modeled on a reference site
(`https://nexus-gr8r.framer.website/`) the user specifically liked: pure
near-black background, one vivid pale-yellow accent used sparingly
(buttons, highlight dots — never as body text color), monospace type for
UI chrome, clean sans for actual reading content. Colors extracted by pixel
sampling the reference and contrast-checked (WCAG), not eyeballed:

| Role | Hex | Contrast on bg | Notes |
|---|---|---|---|
| Background | `#08090a` | — | Near-black, not pure `#000` |
| Primary text | `#ffffff` | 19.9:1 | Headings, primary values |
| Secondary text | `#9a9a9a` | 7.1:1 | Table/body copy that must be read — clears AA/AAA |
| Muted/label text | `#616161` | 3.2:1 | Nav items, decorative captions only — not for content |
| Accent | `#feff7c` | 18.8:1 | Buttons, highlight dots, active states — never large blocks of body text |
| Text on accent fill | `#000000` | 19.8:1 | e.g. button label on a `#feff7c` fill |

Typography: monospace stack (`ui-monospace, "SF Mono", "Cascadia Code",
"JetBrains Mono", monospace`) for nav, table headers, stat captions,
buttons, labels. System sans (`system-ui, -apple-system, "Segoe UI",
sans-serif`) for headings and body/table content — full-monospace
throughout (as the reference site does for its marketing copy) hurts
readability for a data-heavy tool, so this app diverges from the reference
there. Sharp/minimally-rounded buttons; thin hairline dividers between
sections (no card-shadow-heavy look).

Decorative motifs from the reference (dotted-grid texture framing the page,
corner-bracket accents) are optional polish, not required for v1 — easy to
layer on via CSS once the functional pages exist.

## Verification

- `uv run pytest tests/ -q` from `app/` — unit tests for `db.py` (schema,
  upsert dedup logic) and `jobs.py` (reuses `build_report`'s parsing;
  test against a couple of real files from `scraper/jobs/`).
- Manual end-to-end: `uv run flask --app app run`, register
  `resume-matcher/resumes/cv_1000.md`, trigger a rematch, confirm the match
  list renders sorted by score with the same top results the existing
  `resume-matcher/reports/poc_cv1000_vs_scraper.html` shows (cross-check
  against that known-good report).
- Visual: confirm the page matches the token table above (background,
  accent, contrast) — no light-mode CSS should exist to check.
