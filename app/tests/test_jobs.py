from datetime import date
from pathlib import Path

from webapp.jobs import (
    parse_job_file,
    site_name_for,
    get_job_description,
    render_description_html,
    screenshot_path_for,
    read_stale_since,
    stale_state,
    job_stale_state,
)


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


def _job_layout(tmp_path):
    (tmp_path / "jobs").mkdir()
    job = tmp_path / "jobs" / "a-1-x.md"
    job.write_text("# x")
    return job


def test_screenshot_path_for_returns_existing_png(tmp_path):
    job = _job_layout(tmp_path)
    (tmp_path / "screenshots").mkdir()
    png = tmp_path / "screenshots" / "a-1-x.png"
    png.write_bytes(b"x")
    assert screenshot_path_for(job) == png.resolve()


def test_screenshot_path_for_none_when_png_absent(tmp_path):
    job = _job_layout(tmp_path)
    (tmp_path / "screenshots").mkdir()
    assert screenshot_path_for(job) is None


def test_screenshot_path_for_none_when_screenshots_dir_absent(tmp_path):
    job = _job_layout(tmp_path)
    assert screenshot_path_for(job) is None


def test_screenshot_path_for_none_when_symlink_escapes(tmp_path):
    job = _job_layout(tmp_path)
    (tmp_path / "screenshots").mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"x")
    (tmp_path / "screenshots" / "a-1-x.png").symlink_to(outside)
    assert screenshot_path_for(job) is None


def test_stale_state_0_days():
    today = date(2026, 10, 10)
    since = date(2026, 10, 10)
    assert stale_state(since, today) == 'stale'


def test_stale_state_1_day():
    today = date(2026, 10, 10)
    since = date(2026, 10, 9)
    assert stale_state(since, today) == 'stale'


def test_stale_state_2_days():
    today = date(2026, 10, 10)
    since = date(2026, 10, 8)
    assert stale_state(since, today) == 'stale'


def test_stale_state_3_days():
    today = date(2026, 10, 10)
    since = date(2026, 10, 7)
    assert stale_state(since, today) == 'hidden'


def test_stale_state_many_days():
    today = date(2026, 10, 10)
    since = date(2026, 10, 1)
    assert stale_state(since, today) == 'hidden'


def test_stale_state_future_date():
    today = date(2026, 10, 10)
    since = date(2026, 10, 11)
    assert stale_state(since, today) == 'stale'


def test_stale_state_none():
    today = date(2026, 10, 10)
    assert stale_state(None, today) == 'live'


def test_read_stale_since_valid_bullet(tmp_path):
    job_file = tmp_path / "test.md"
    job_file.write_text("# Test Job\n- Stale since: 2026-10-08\n\n## Description\nContent")
    assert read_stale_since(job_file) == date(2026, 10, 8)


def test_read_stale_since_absent(tmp_path):
    job_file = tmp_path / "test.md"
    job_file.write_text("# Test Job\n\n## Description\nContent")
    assert read_stale_since(job_file) is None


def test_read_stale_since_invalid_date(tmp_path):
    job_file = tmp_path / "test.md"
    job_file.write_text("# Test Job\n- Stale since: 2026-13-45\n\n## Description\nContent")
    assert read_stale_since(job_file) is None


def test_read_stale_since_bullet_after_description_ignored(tmp_path):
    job_file = tmp_path / "test.md"
    job_file.write_text("# Test Job\n\n## Description\nContent\n- Stale since: 2026-10-08")
    assert read_stale_since(job_file) is None


def test_read_stale_since_missing_file():
    assert read_stale_since("/nonexistent/path/file.md") is None


def test_parse_job_file_includes_stale_since(tmp_path):
    job_file = tmp_path / "test.md"
    job_file.write_text("# Test Job Title\n- Stale since: 2026-10-08\n\n## Description\nTest description")
    result = parse_job_file(job_file)
    assert "stale_since" in result
    assert result["stale_since"] == date(2026, 10, 8)
    assert "title" in result




def test_job_stale_state_missing_file():
    today = date(2026, 10, 10)
    state, returned_date = job_stale_state("/nonexistent/path/file.md", today)
    assert state == 'live'
    assert returned_date is None


def test_job_stale_state_with_valid_file(tmp_path):
    job_file = tmp_path / "test.md"
    job_file.write_text("# Test Job\n- Stale since: 2026-10-08\n\n## Description\nContent")
    today = date(2026, 10, 10)
    state, returned_date = job_stale_state(job_file, today)
    assert state == 'stale'
    assert returned_date == date(2026, 10, 8)
