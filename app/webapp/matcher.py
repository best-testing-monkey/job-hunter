import json
import os
import subprocess
import tempfile
from pathlib import Path


def run_embed_match(resume_path: str, jobs_glob: str = "../scraper/jobs/*.md") -> list[dict]:
    resume_matcher_dir = Path(__file__).parent.parent.parent / "resume-matcher"

    temp_fd, temp_path = tempfile.mkstemp(suffix=".jsonl", text=True)
    os.close(temp_fd)

    try:
        subprocess.run(
            [
                os.path.expanduser("~/.venvs/resume-matcher/bin/python"),
                "job_matcher.py",
                "--resume",
                resume_path,
                "--jobs",
                jobs_glob,
                "--mode",
                "embed",
                "--min-strong",
                "0.0",
                "--out",
                temp_path,
            ],
            cwd=str(resume_matcher_dir),
            check=True,
        )

        results = []
        with open(temp_path, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    results.append({
                        "job_file": entry["job_file"],
                        "score": entry["probs"]["similarity"],
                    })

        return results
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
