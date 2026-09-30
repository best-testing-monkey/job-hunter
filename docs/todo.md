# job-hunter app — todo

Per-resume match tracking, first slice. See `docs/DESIGN_DOC.md` and
`docs/tickets/`. Implementation standards: `docs/tickets/APPENDIX-A-standards.md`.

Independent stories (same "depends on E1 only" set) may run in parallel:
E3-S01, E4-S01, E5-S01 are mutually independent once E1-S01 is done.
E2-S01 is also independent of those three but gates E6-S01/E6-S03 (need the
base template). Keep parallel subagent batches to 2 at a time.

## Epic 1 — Scaffolding

- [x] E1-S01 Scaffold the Flask app project (docs/tickets/E1-S01-scaffold-flask-app.md)

## Epic 2 — Visual shell

- [x] E2-S01 Dark-only base template and stylesheet (docs/tickets/E2-S01-base-template-and-theme.md)

## Epic 3 — Data layer

- [x] E3-S01 SQLite schema and connection helper (docs/tickets/E3-S01-sqlite-schema.md)
- [x] E3-S02 Resume registration and match upsert queries (docs/tickets/E3-S02-resume-and-match-queries.md)

## Epic 4 — Job metadata reuse

- [x] E4-S01 Job metadata wrapper reusing build_report.py (docs/tickets/E4-S01-job-metadata-wrapper.md)

## Epic 5 — Matching engine

- [x] E5-S01 Matcher subprocess wrapper (docs/tickets/E5-S01-matcher-subprocess-wrapper.md)

## Epic 6 — Routes

- [x] E6-S01 Resume list page (docs/tickets/E6-S01-resume-list-page.md)
- [x] E6-S02 Register a resume (docs/tickets/E6-S02-register-resume.md)
- [x] E6-S03 Resume match list page (docs/tickets/E6-S03-resume-match-list-page.md)
- [x] E6-S04 Trigger a rematch (docs/tickets/E6-S04-trigger-rematch.md)
