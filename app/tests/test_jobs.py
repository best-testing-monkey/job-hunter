from pathlib import Path

from webapp.jobs import parse_job_file, site_name_for, get_job_description


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
