import html
import re
import sys
from datetime import date
from pathlib import Path

import markdown

_RESUME_MATCHER_DIR = Path(__file__).resolve().parents[2] / "resume-matcher"
sys.path.insert(0, str(_RESUME_MATCHER_DIR))
import build_report  # noqa: E402

STALE_VISIBLE_DAYS = 2


def read_stale_since(path: str | Path) -> date | None:
    try:
        text = Path(path).read_text()
    except OSError:
        return None

    lines = text.split('\n')
    for line in lines:
        if line.startswith('## '):
            break
        if re.match(r'^- Stale since:\s*(\d{4}-\d{2}-\d{2})\s*$', line):
            match = re.match(r'^- Stale since:\s*(\d{4}-\d{2}-\d{2})\s*$', line)
            date_str = match.group(1)
            try:
                year, month, day = map(int, date_str.split('-'))
                return date(year, month, day)
            except ValueError:
                return None
    return None


def parse_job_file(path: str | Path) -> dict:
    result = build_report.parse_job(Path(path))
    result["stale_since"] = read_stale_since(path)
    return result


def stale_state(stale_since: date | None, today: date | None = None) -> str:
    if stale_since is None:
        return 'live'
    if today is None:
        today = date.today()
    days = (today - stale_since).days
    if days <= STALE_VISIBLE_DAYS:
        return 'stale'
    return 'hidden'


def job_stale_state(job_file: str | Path, today: date | None = None) -> tuple[str, date | None]:
    try:
        stale_since = read_stale_since(job_file)
    except (OSError, ValueError):
        return ('live', None)
    return (stale_state(stale_since, today), stale_since)


def site_name_for(job_file: str) -> str:
    return build_report.site_name(job_file)


def render_description_html(markdown_text: str) -> str:
    if not markdown_text or not markdown_text.strip():
        return ""

    escaped = html.escape(markdown_text, quote=False)
    html_output = markdown.markdown(escaped, extensions=["sane_lists"])

    def replace_dangerous_href(match):
        href_value = match.group(1)
        if re.match(r'\s*(javascript|data|vbscript):', href_value, re.IGNORECASE):
            return 'href="#"'
        return match.group(0)

    html_output = re.sub(r'href\s*=\s*"([^"]*)"', replace_dangerous_href, html_output)
    html_output = re.sub(r'<img[^>]*>', '', html_output)

    return html_output


def get_job_description(job_file: str | Path) -> str:
    text = Path(job_file).read_text()
    lines = text.split('\n')

    description_start = None
    next_section_start = None

    for i, line in enumerate(lines):
        if line.startswith('## Description'):
            description_start = i + 1
        elif description_start is not None and line.startswith('## '):
            next_section_start = i
            break

    if description_start is None:
        return ""

    if next_section_start is None:
        description_lines = lines[description_start:]
    else:
        description_lines = lines[description_start:next_section_start]

    return '\n'.join(description_lines).strip()


def screenshot_path_for(job_file: str | Path) -> Path | None:
    job = Path(job_file).resolve()
    screenshots_dir = (job.parent.parent / "screenshots").resolve()
    candidate = (screenshots_dir / f"{job.stem}.png").resolve()
    if candidate.parent != screenshots_dir or candidate.suffix != ".png" or not candidate.is_file():
        return None
    return candidate
