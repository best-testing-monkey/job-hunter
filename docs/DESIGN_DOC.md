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

## Dashboard, match workflow, and job detail (third slice)

Driven by two inputs: a user-authored flow describing a richer homepage and
detail page, and an independent usability QA pass (`docs/usability-qa-report.md`,
11 findings) run against the first two slices. This section specifies the
new flow in full and states explicitly, finding by finding, which QA items
it resolves as a side effect and which still need a standalone fix.

### Architecture change: this slice introduces real client-side JavaScript

Everything built so far is pure server-rendered HTML with one inline
`onsubmit="return confirm(...)"`. Three new behaviors can't be done that
way:

- The confidence-threshold slider persists in the browser
  (`localStorage`), not the server, and must re-filter/re-sort visible
  rows **instantly** as it's dragged — a server round-trip per drag tick
  is wrong.
- Table columns sort client-side, in-place, with a 3-state cycle.
- The rematch "spinning while running" icon reflects live server state
  the page must poll for without a full reload.

New file: `app/webapp/static/app.js` — plain vanilla JS, no framework, no
build step (consistent with this project's dependency-light style). Three
independent pieces, each usable without the others:

1. **Threshold slider** (`initThresholdSlider()`): reads/writes a single
   shared `localStorage` key (`confidenceThreshold`, default `65`) used by
   *both* the homepage and the resume detail page — moving it on either
   page updates the same stored value. On `input`, re-runs whatever
   filter/recompute callback the current page registered (homepage
   recomputes Match Count/since-new-match from embedded JSON; detail page
   shows/hides match rows by comparing each row's `data-score` attribute).
2. **Table sort** (`makeSortable(table)`): attached to each sortable
   `<th>`. Click cycle: unsorted → ascending (▼ next to the label) →
   descending (▲) → unsorted (no arrow), removing any arrow from other
   columns when a new one is clicked (only one column sorted at a time).
   Sorts by reading each row's `data-sort-value` attribute (so numeric/date
   columns sort correctly, not as strings) and re-appending `<tr>`s in the
   new order — no server round-trip, since the full dataset is already in
   the DOM. Sort state is **not** persisted across reloads.
3. **Rematch status polling** (`pollRematchStatus(resumeId, iconEl)`):
   while a rematch is running for a resume, `fetch`es
   `GET /resumes/<id>/rematch-status` every ~2s and toggles a `.spinning`
   CSS class (a simple `@keyframes` rotation) on that resume's refresh
   icon; stops polling once the response says it's no longer running.

### Data model changes

```sql
ALTER TABLE matches ADD COLUMN status TEXT NOT NULL DEFAULT 'New';
ALTER TABLE matches ADD COLUMN job_posted TEXT;
ALTER TABLE resumes ADD COLUMN rematch_running INTEGER NOT NULL DEFAULT 0;
```

- `matches.status` — one of `New` / `Non-match` / `Applied` / `Done`
  (validate in app code, no DB-level CHECK needed for a single-user tool).
  Defaults to `New` for every newly-upserted match; **a rematch upsert
  must NOT reset an already-triaged match's status back to `New`** — only
  `score`/`title`/`site`/`location`/`workplace`/`source_url`/`job_posted`/
  `computed_at` get overwritten on conflict, `status` is left alone unless
  the row is brand new.
- `matches.job_posted` — the job's `Posted:` date (from
  `jobs.parse_job_file()`'s existing `posted` field), stored at match-write
  time so "since new match" doesn't need to re-read every job file on
  every homepage load. Populate it in `_run_rematch`'s existing call to
  `jobs.parse_job_file()` (already fetches this field, just wasn't being
  passed through to `upsert_match`).
- `resumes.rematch_running` — `1` while `_run_rematch` is executing for
  that resume, `0` otherwise. Set to `1` right before the background
  thread starts (in `rematch_resume`, before `thread.start()`), reset to
  `0` in a `try/finally` inside `_run_rematch` so a crashed matcher run
  still clears the flag (don't leave a resume stuck "forever spinning").

### Homepage (`/`)

- **Confidence slider**: `<input type="range" min="0" max="100" value="65">`
  with a live `%` readout, positioned above the table, `localStorage`-backed
  per the Architecture section above.
- **"+ New Resume"**: unchanged destination (`/resumes/new`), just
  repositioned to sit beside the slider rather than below the list.
- **Resume table**, columns `Name` / `Match count` / `since new match` /
  `Actions`, one `<tr>` per resume:
  - Sortable on all but `Actions` (3-state cycle, see Architecture).
  - `Match count` and `since new match` are **computed client-side** from
    a per-resume JSON blob the server embeds in the page (each resume's
    full `[{score, status, job_posted}, ...]` match list — modest data
    volume for a single-user local tool, no pagination API needed). JS
    recomputes both whenever the slider moves:
    - Match count = number of entries where `status == "New" && score >=
      threshold`.
    - since new match = `now - max(job_posted where score >= threshold)`,
      rendered as a relative delta ("3 hours ago", "2 days ago"); `"—"` if
      no match clears the threshold.
  - `Actions`: red-X delete icon (existing confirm dialog, just
    re-skinned as an icon instead of a text button) and a circular-arrow
    rematch icon that POSTs to the existing `/resumes/<id>/rematch` and
    immediately starts polling (see Architecture) so it spins for the
    actual duration of the run, not a guess.

### Resume detail page (`/resumes/<id>`)

- Resume name/content/metadata (file path, created date) in a **styled
  table**, replacing the current plain heading + paragraph.
- The same confidence slider (shared `localStorage` key) sits above the
  matches table and filters (hides/shows, client-side) rows by
  `data-score`.
- Matches table, sortable (same mechanism), **default sort: score,
  descending**. Columns as today (Score, Job, Site, Location) plus:
  - **Status** — a `<select>` per row (`New`/`Non-match`/`Applied`/`Done`),
    styled to match the rest of the table rather than a bare browser
    widget (still a real `<select>`, just CSS-skinned — no custom JS
    dropdown needed). On `change`, `POST`s to
    `/matches/<match_id>/status` (new route) to persist immediately —
    no separate "Save" step.
  - **Job** (title) now links to the new job detail page (see below)
    instead of linking straight out to `source_url`.

### Job detail page (new)

- `GET /jobs/<int:match_id>` — looks up the match row (for its
  `job_file`), re-reads that file fresh from disk via a new
  `jobs.get_job_description(job_file) -> str` helper (reads the raw
  markdown, returns everything between the `## Description` heading and
  the next `##` heading or end-of-file — this is new logic in `app/`,
  *not* an edit to `resume-matcher/build_report.py`, since that function
  deliberately only parses the metadata bullets today). Renders title,
  site, location, workplace, full description text, and a "View original
  posting" link to `source_url`.
- 404s if the `match_id` doesn't exist.

### Mapping to the usability QA findings

| # | Finding | Resolution |
|---|---|---|
| 1, 2 | Blank/whitespace resume name or content silently saved | **Not fixed by the above — needs its own story**: reject blank/whitespace `name`/`content` server-side on both create and edit, re-render the form with the entered values and an error instead of redirecting. |
| 3 | New/Edit forms unstyled, 1-line textarea | **Not fixed by the above — needs its own story**: style both forms consistently with the rest of the app, size the textarea for real resume content (`rows`, monospace, sensible width). |
| 4 | 404 page is raw unstyled Werkzeug output | **Not fixed by the above — needs its own story**: a Flask error handler rendering a dark-themed 404 page. |
| 5 | No feedback after clicking Rematch | **Fixed** by the spinning-icon + polling mechanism above. |
| 6 | Match scores shown at 16 decimal places | **Fixed in passing** while building the new sortable match tables — render as a rounded 2-decimal value (`data-sort-value` keeps the raw float for correct sorting; displayed text is rounded). |
| 7 | 1,079 unfiltered matches, no floor | **Fixed** by the confidence threshold slider filtering what's shown. |
| 8 | Create redirects to list, Edit redirects to detail (inconsistent) | **Not fixed by the above — needs its own story**: make `POST /resumes` (create) redirect straight to the new resume's detail page, matching edit's behavior. |
| 9 | Links render browser-default blue, not the accent color | **Fixed in passing** while restyling the tables this slice touches — style `a` globally in `style.css` to use the accent color. |
| 10 | Raw filesystem path shown on resume detail page | **Fixed in passing** — the new styled metadata table gives it a proper labeled cell instead of a raw sentence. |
| 11 | Match table overflows on a 390px mobile viewport | **Deferred, explicitly out of scope** — this is a localhost desktop tool; mobile layout isn't a goal right now. |

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
