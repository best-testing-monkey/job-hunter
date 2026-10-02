from pathlib import Path

from webapp.jobs import parse_job_file, site_name_for, get_job_description, render_description_html


def test_parse_job_file_and_site_name():
    repo_root = Path(__file__).resolve().parents[2]
    job_files = list(repo_root.glob("scraper/jobs/*.md"))
    assert job_files, "No job files found in scraper/jobs/"

    job_file = job_files[0]
    result = parse_job_file(job_file)

    assert isinstance(result, dict)
    assert "title" in result
    assert result["title"], "title should be non-empty"

    site_name = site_name_for(job_file.name)
    assert isinstance(site_name, str)
    assert site_name, "site_name should be non-empty"


def test_get_job_description():
    repo_root = Path(__file__).resolve().parents[2]
    job_files = list(repo_root.glob("scraper/jobs/*.md"))
    assert job_files, "No job files found in scraper/jobs/"

    job_file = job_files[0]
    description = get_job_description(job_file)

    assert isinstance(description, str)
    assert description, "description should be non-empty"
    assert "## Description" not in description, "description should not include the heading"


def test_get_job_description_excludes_scrape_note():
    repo_root = Path(__file__).resolve().parents[2]
    job_files = list(repo_root.glob("scraper/jobs/*.md"))

    job_file_with_scrape_note = None
    for job_file in job_files:
        content = job_file.read_text()
        if "## Scrape note" in content:
            job_file_with_scrape_note = job_file
            break

    if job_file_with_scrape_note:
        description = get_job_description(job_file_with_scrape_note)
        assert "## Scrape note" not in description, "description should not include scrape note section"


def test_get_job_description_not_found(tmp_path):
    job_file = tmp_path / "test.md"
    job_file.write_text("# Test Job\n\nSome content")

    description = get_job_description(job_file)
    assert description == "", "should return empty string when no description found"


def test_render_description_html_with_headings_and_lists():
    markdown_text = "### Role\n\n- one\n- two\n\n**Bold** text"
    html = render_description_html(markdown_text)
    assert "<h3>Role</h3>" in html
    assert "<ul>" in html
    assert "<li>one</li>" in html
    assert "<li>two</li>" in html
    assert "<strong>Bold</strong>" in html


def test_render_description_html_escapes_script_tags():
    markdown_text = "<script>alert(1)</script>"
    html = render_description_html(markdown_text)
    assert "&lt;script&gt;" in html
    assert "<script>" not in html


def test_render_description_html_removes_javascript_links():
    markdown_text = "[x](javascript:alert(1))"
    html = render_description_html(markdown_text)
    assert "javascript:" not in html.lower()
    assert 'href="#"' in html


def test_render_description_html_removes_images():
    markdown_text = "![a](http://evil.example/x.png)"
    html = render_description_html(markdown_text)
    assert "<img" not in html


def test_render_description_html_ordered_lists():
    markdown_text = "1. a\n2. b"
    html = render_description_html(markdown_text)
    assert "<ol>" in html


def test_render_description_html_escapes_ampersands():
    markdown_text = "R&D"
    html = render_description_html(markdown_text)
    assert "R&amp;D" in html


def test_render_description_html_empty_input():
    assert render_description_html("") == ""
    assert render_description_html("   ") == ""


def test_render_description_html_removes_data_urls():
    markdown_text = "[x](data:text/html,<script>alert(1)</script>)"
    html = render_description_html(markdown_text)
    assert "data:" not in html.lower()
    assert 'href="#"' in html


def test_render_description_html_removes_vbscript_urls():
    markdown_text = "[x](vbscript:alert(1))"
    html = render_description_html(markdown_text)
    assert "vbscript:" not in html.lower()
    assert 'href="#"' in html


def test_get_job_description_includes_subheadings(tmp_path):
    job_file = tmp_path / "test.md"
    content = "## Description\nDescription text\n### Sub heading\nmore text\n## Scrape note\nnote text"
    job_file.write_text(content)

    description = get_job_description(job_file)
    assert "### Sub heading" in description
    assert "more text" in description
    assert "Scrape note" not in description
    assert "note text" not in description
