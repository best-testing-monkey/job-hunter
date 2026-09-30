import sys
from pathlib import Path

_RESUME_MATCHER_DIR = Path(__file__).resolve().parents[2] / "resume-matcher"
sys.path.insert(0, str(_RESUME_MATCHER_DIR))
import build_report  # noqa: E402


def parse_job_file(path: str | Path) -> dict:
    return build_report.parse_job(Path(path))


def site_name_for(job_file: str) -> str:
    return build_report.site_name(job_file)
