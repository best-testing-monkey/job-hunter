# E13-S02 — Shared html_to_markdown helper

See `APPENDIX-A-standards.md` for code style, test, gate and commit conventions and `APPENDIX-B-scraper-standards.md` for the scraper-repo specifics (Epic 13 overrides Appendix A's "never edit scraper/" rule: the scraper repo is the owner's own and is edited here) — don't repeat them here.

## Goal

One bs4-based function that turns an HTML fragment (or plain text) into clean Markdown, so every adapter can stop flattening HTML itself.

## Context

- New module `scraper/job_scraper/core/html_markdown.py`. Look at `job_scraper/core/markdown_export.py` for module style (plain functions, type hints).
- Today adapters flatten HTML differently: `soup.get_text(separator=" ", strip=True)` (arc_dev, pro_act, synprofs, tender_link, working_nomads, harveynash, freelancermap), `get_text(strip=True)` which glues words together (flexvalue, freelancer_com, hero, iamexpat, ictergezocht, wearedevelopers), a regex tag stripper (stone_interim `_strip_html`), an `HTMLParser` stripper (sevenstars `strip_html_tags`), or JSON-LD `description` copied verbatim (djinni, circle8). All structure (paragraphs, lists, headings) is lost. `markdown_export.render` writes the description as-is under `## Description`.
- The Markdown goes into `scraper/jobs/*.md` under `## Description`, and the app extracts the description up to the next line starting with `## `, so the helper must never emit a line starting with `## ` (see Appendix B).

## Files to create/modify

- `scraper/job_scraper/core/html_markdown.py` (new): `def html_to_markdown(html: str | None) -> str`.
- `scraper/tests/test_html_markdown.py` (new).
- `scraper/tests/fixtures/html_markdown/sample.html` and `sample.md` (new): a realistic fragment (headings, paragraphs, a `<ul>`, an `<ol>`, `<strong>`, `<br>`, `&nbsp;`/`&eacute;` entities, a `<script>` tag) and the exact expected Markdown output (golden file).

## Acceptance criteria

Behavior of `html_to_markdown` (each bullet gets a test in `tests/test_html_markdown.py`):
- `None` or `""` or whitespace-only input returns `""`.
- Parse with `BeautifulSoup(html, "html.parser")`; drop `<script>`, `<style>`, comments.
- `<p>` and block-level `<div>`: each becomes one paragraph; paragraphs are separated by exactly ONE blank line (`"\n\n"`). Text sitting directly inside a `<div>` (not wrapped in `<p>`) is also a paragraph.
- Headings: `<h1>`, `<h2>`, `<h3>` become `### text`; `<h4>`..`<h6>` become `#### text`. (Never `#` or `##`.) A heading is its own block.
- `<ul>` becomes lines `- item`; `<ol>` becomes `1. item`, `2. item`, ... (real numbers). A list is one block (items on consecutive lines, no blank lines between items). Nested lists indent the child by 4 spaces. `<li>` containing `<p>` is flattened to one line.
- `<strong>`/`<b>` become `**text**`. Other inline tags (`<em>`, `<i>`, `<span>`, `<a>`, `<u>`) contribute only their text — links are NOT emitted as Markdown links (keep the link text only), images are dropped.
- `<br>` inside a paragraph becomes a Markdown hard line break (`"  \n"`: two spaces, newline).
- `<table>`: each `<tr>` becomes one line, cell texts joined with `" | "`; the table is one block.
- Entities are decoded; `\xa0` becomes a normal space; runs of whitespace inside a block collapse to one space; no trailing whitespace on a line except the two-space hard break.
- A text line that would start with `#` after conversion gets the `#` backslash-escaped (`\\#`) so it can never become a heading — in particular no output line ever starts with `## `.
- Input with NO `<` or `&` characters at all is treated as plain text: split on blank lines into paragraphs; single newlines inside a paragraph become hard breaks; the same `#` escaping and whitespace rules apply.
- Output never starts or ends with whitespace/newlines and never contains three consecutive newlines.
- `html_to_markdown(read(sample.html)) == read(sample.md)` exactly.
- `uv run pytest tests/test_html_markdown.py` passes.

## Definition of done

- Gates pass: `uv run pytest` from `scraper/` (zero failures, no fewer passing tests than before).
- Committed in the SCRAPER repo (`git -C scraper commit`) as `E13-S02: Add shared html_to_markdown helper`.
- `docs/todo.md` item for E13-S02 checked off, committed in the JOB-HUNTER repo (`Mark E13-S02 as done in todo`).
