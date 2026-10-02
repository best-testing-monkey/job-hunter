import html
import re
import sys
from pathlib import Path

import markdown

_RESUME_MATCHER_DIR = Path(__file__).resolve().parents[2] / "resume-matcher"
sys.path.insert(0, str(_RESUME_MATCHER_DIR))
import build_report  # noqa: E402


def parse_job_file(path: str | Path) -> dict:
    return build_report.parse_job(Path(path))


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
