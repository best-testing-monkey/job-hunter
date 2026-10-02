# E13-S12 — Show rendered description on the job detail page

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here. Epic 13 app stories follow it unchanged (they only touch `app/`).

## Goal

The job detail page shows the description as formatted HTML (headings, lists, bold, paragraphs) styled for the app's dark theme instead of a `<pre>` block, and links to the posting's real Source URL.

## Context

- Depends on E13-S11 (`jobs.render_description_html`).
- `app/webapp/routes.py`, job detail route (`@bp.route("/jobs/<int:match_id>")`, function after `resume_detail`-related routes, around line 170-190): gets `match = db.get_match(...)`, `job_info = jobs.parse_job_file(match["job_file"])`, `description = jobs.get_job_description(match["job_file"])` and calls `render_template("job_detail.html", title=..., site=..., location=..., workplace=..., source=match["source_url"], description=description)`. `job_info["source"]` is the `- Source:` bullet from the Markdown file.
- `app/webapp/templates/job_detail.html` (extends `base.html`): renders the description with `<pre style="white-space: pre-wrap; ...">{{ description }}</pre>` and a `<a href="{{ source }}" class="btn-accent" target="_blank">View original posting</a>` link.
- `app/webapp/static/style.css`: CSS variables `--bg #08090a`, `--text-primary #fff`, `--text-secondary #9a9a9a`, `--text-muted #616161`, `--accent #feff7c`; a global reset `* { margin: 0; padding: 0 }` removes list indentation and paragraph spacing, so the new rules must restore them explicitly. `a` is accent-coloured.
- Existing test `test_job_detail_with_valid_match` in `app/tests/test_routes.py` (line ~757) builds a match whose `job_file` is a tmp `.md`; copy its setup for new tests. Blueprint name is `main`.
- This story also edits `routes.py` and the template, which E13-S33/S34 edit later — sequential.

## Files to create/modify

- `app/webapp/routes.py`
- `app/webapp/templates/job_detail.html`
- `app/webapp/static/style.css`
- `app/tests/test_routes.py`

## Acceptance criteria

- `GET /jobs/<match_id>` for a match whose job file has description `"### Duties\n\n- Write tests\n- Fix bugs\n\n**Must** know Python"` returns 200 and the body contains `<h3>Duties</h3>`, two `<li>` items (`<li>Write tests</li>`), `<strong>Must</strong>`, and the description is inside an element `<div class="job-description">`; the body no longer contains a `<pre` tag for the description.
- Scraped HTML in a description is escaped: a description `"<script>alert(1)</script>"` yields `&lt;script&gt;` in the body and no `<script>alert(1)</script>`.
- The `View original posting` link's `href` is the file's `- Source:` value (`jobs.parse_job_file(...)["source"]`), falling back to `match["source_url"]` only if the file has none. Test: match row `source_url="https://old.example/x"`, file `- Source: https://example.com/job1` -> body contains `href="https://example.com/job1"` and not `https://old.example/x`.
- `style.css` contains rules for `.job-description p` (margin-bottom, line-height >= 1.5), `.job-description h3` and `.job-description h4` (margin-top/bottom, `color: var(--text-primary)`), `.job-description ul` and `.job-description ol` (`padding-left: 1.5rem`, `margin-bottom`), `.job-description li` (margin-bottom), `.job-description strong` (`font-weight: 600`) and `max-width: 70ch` on `.job-description` (grep-able; no light-theme colours, only the existing variables).
- Existing tests, including `test_job_detail_with_valid_match` (still finds `This is a great job posting` and `View original posting`) and the 404 test, pass: `uv run pytest tests/ -q`.

## Definition of done

- Gates pass: `uv run pytest tests/ -q` from `app/` (zero failures, no fewer passing tests than before).
- Committed in the JOB-HUNTER repo as `E13-S12: Render job description as styled Markdown`.
- `docs/todo.md` item for E13-S12 checked off (same repo; may be a second commit `Mark E13-S12 as done in todo`).
