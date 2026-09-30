from pathlib import Path

from webapp.jobs import parse_job_file, site_name_for


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
