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

## Epic 7 — Resume CRUD

All four stories touch `app/webapp/routes.py` and/or the same templates —
run sequentially, not in parallel (E7-S01 is the exception: it only touches
`db.py`/`__init__.py`, so it could in principle pair with something else,
but there's nothing else pending right now).

- [x] E7-S01 Add content column and resume CRUD db functions (docs/tickets/E7-S01-resume-crud-db-functions.md)
- [x] E7-S02 Switch resume creation to content-based, remove register_resume (docs/tickets/E7-S02-content-based-create.md)
- [x] E7-S03 Edit a resume (docs/tickets/E7-S03-edit-resume.md)
- [x] E7-S04 Delete a resume (docs/tickets/E7-S04-delete-resume.md)

## Epic 8 — Match status, job_posted, rematch-running state

Sequential (both touch `db.py`; E8-S02 also touches `routes.py`). Can start
in parallel with Epic 9's first story (disjoint files).

- [ ] E8-S01 Add match status, job_posted column, and match lookup functions (docs/tickets/E8-S01-match-status-and-posted-date.md)
- [ ] E8-S02 Track rematch-running state and expose a status endpoint (docs/tickets/E8-S02-rematch-running-state.md)

## Epic 9 — Homepage dashboard

E9-S01 is new files only (`app.js`, `base.html`, `style.css`) — can run in
parallel with E8-S01. E9-S02 depends on both E8-S01/E8-S02 and E9-S01, and
touches `routes.py` — sequential after those.

- [ ] E9-S01 Add app.js foundation (threshold slider, table sort, rematch polling) (docs/tickets/E9-S01-app-js-foundation.md)
- [ ] E9-S02 Rebuild homepage as a sortable dashboard with threshold filtering (docs/tickets/E9-S02-homepage-dashboard.md)

## Epic 10 — Resume detail page redesign

E10-S01 only touches `resume_detail.html` — can run in parallel with
Epic 8/9 work. E10-S02 depends on E8-S01, E9-S01, and E10-S01, and touches
`routes.py` — sequential after those.

- [ ] E10-S01 Style the resume metadata section on the detail page (docs/tickets/E10-S01-resume-metadata-table.md)
- [ ] E10-S02 Add sortable, threshold-filtered match table with status workflow (docs/tickets/E10-S02-sortable-matches-with-status.md)

## Epic 11 — Job detail page

Depends on E8-S01, touches `routes.py` — sequential relative to the other
`routes.py`-touching stories above.

- [ ] E11-S01 Add job detail page (docs/tickets/E11-S01-job-detail-page.md)

## Epic 12 — Remaining usability QA fixes

E12-S01 and E12-S02 are sequential (same templates). E12-S03 only touches
`__init__.py` and a new template — can run in parallel with anything that
doesn't also touch `__init__.py` (nothing else in this batch does).

- [ ] E12-S01 Reject blank/whitespace resume name or content; create redirects to the new resume (docs/tickets/E12-S01-resume-form-validation.md)
- [ ] E12-S02 Style the New/Edit resume forms and size the content textarea (docs/tickets/E12-S02-style-resume-forms.md)
- [ ] E12-S03 Add a dark-themed 404 error page (docs/tickets/E12-S03-styled-404-page.md)
