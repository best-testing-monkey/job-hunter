# E13-S11 — Render description Markdown to safe HTML

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here. Epic 13 app stories follow it unchanged (they only touch `app/`).

## Goal

Turn a job's Markdown description into safe HTML, and stop the description extractor from truncating at `###` sub-headings.

## Context

- Job descriptions will now be Markdown (paragraphs, `###` headings, `-` lists, `**bold**`) produced by the scraper's `html_to_markdown`. The text comes from scraped third-party sites, so it is untrusted.
- `app/webapp/jobs.py` has `get_job_description(job_file)`: it finds the line starting `## Description` and stops at the next line that `startswith('##')` — that would wrongly cut the description at the first `### Heading`. The stop condition must become: a line that starts with exactly `## ` (two hashes then a space), i.e. a level-2 heading; `###`/`####` lines stay inside the description.
- `app/webapp/templates/job_detail.html` currently renders the description in a `<pre>`; changing the template is E13-S12, NOT this story.
- `app/pyproject.toml` dependencies: only `flask` today. Add the pure-Python `markdown` package with `uv add markdown` run in `app/` (updates `pyproject.toml` and `uv.lock`). No other new dependency.
- Existing tests: `app/tests/test_jobs.py` (`test_get_job_description` uses a real `scraper/jobs/*.md`).

## Files to create/modify

- `app/pyproject.toml` (+ `app/uv.lock`, via `uv add markdown`)
- `app/webapp/jobs.py`
- `app/tests/test_jobs.py`

## Acceptance criteria

- `app/pyproject.toml` lists `markdown` in `dependencies`; `uv run python -c "import markdown"` works from `app/`.
- New `def render_description_html(markdown_text: str) -> str` in `webapp/jobs.py`: (1) escape `&`, `<`, `>` in the input with `html.escape(text, quote=False)` BEFORE Markdown conversion; (2) `markdown.markdown(escaped, extensions=["sane_lists"])`; (3) post-process the HTML result: replace any `href` whose value starts (case-insensitively, ignoring leading whitespace) with `javascript:`, `data:` or `vbscript:` by `href="#"`, and delete every `<img ...>` tag. Returns `""` for empty/whitespace input.
- Tests in `test_jobs.py` (each its own test): `"### Role\n\n- one\n- two\n\n**Bold** text"` yields `<h3>Role</h3>`, `<ul>`, two `<li>`, `<strong>Bold</strong>`; input `"<script>alert(1)</script>"` yields output containing `&lt;script&gt;` and NOT containing `<script>`; input `"[x](javascript:alert(1))"` yields no `href="javascript:`; input `"![a](http://evil.example/x.png)"` yields no `<img`; input `"1. a\n2. b"` yields `<ol>`; an ampersand (`"R&D"`) comes out as `R&amp;D`; `""` returns `""`.
- `get_job_description` change: a temp markdown file (via `tmp_path`) with `## Description`, text, `### Sub heading`, more text, then `## Scrape note`, note text returns a string containing `### Sub heading` and `more text` and NOT `Scrape note` / `note text`. The existing `test_get_job_description` still passes.
- `uv run pytest tests/ -q` passes.

## Definition of done

- Gates pass: `uv run pytest tests/ -q` from `app/` (zero failures, no fewer passing tests than before).
- Committed in the JOB-HUNTER repo as `E13-S11: Render job description markdown safely`.
- `docs/todo.md` item for E13-S11 checked off (same repo; may be a second commit `Mark E13-S11 as done in todo`).
