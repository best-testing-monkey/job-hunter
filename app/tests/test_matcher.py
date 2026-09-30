import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from webapp.matcher import run_embed_match


def mock_subprocess_run(cmd, **kwargs):
    out_path = None
    for i, arg in enumerate(cmd):
        if arg == "--out":
            out_path = cmd[i + 1]
            break

    if out_path:
        fake_jsonl = [
            {"resume_file": "test.pdf", "job_file": "job1.md", "probs": {"similarity": 0.85}, "top": "similarity"},
            {"resume_file": "test.pdf", "job_file": "job2.md", "probs": {"similarity": 0.72}, "top": "similarity"},
        ]
        with open(out_path, "w") as f:
            for entry in fake_jsonl:
                f.write(json.dumps(entry) + "\n")


def test_run_embed_match_returns_correct_structure():
    with patch("subprocess.run", side_effect=mock_subprocess_run) as mock_run:
        result = run_embed_match("test_resume.pdf")

        assert isinstance(result, list)
        assert len(result) == 2

        assert result[0]["job_file"] == "job1.md"
        assert result[0]["score"] == 0.85

        assert result[1]["job_file"] == "job2.md"
        assert result[1]["score"] == 0.72


def test_run_embed_match_subprocess_called_correctly():
    with patch("subprocess.run", side_effect=mock_subprocess_run) as mock_run:
        run_embed_match("test_resume.pdf", jobs_glob="../scraper/jobs/*.md")

        mock_run.assert_called_once()
        call_args, call_kwargs = mock_run.call_args

        cmd = call_args[0]
        assert ".venvs/resume-matcher" in cmd[0]
        assert "job_matcher.py" in cmd
        assert "--resume" in cmd
        assert "test_resume.pdf" in cmd
        assert "--jobs" in cmd
        assert "../scraper/jobs/*.md" in cmd
        assert "--mode" in cmd
        assert "embed" in cmd

        assert str(call_kwargs["cwd"]).endswith("resume-matcher")
        assert call_kwargs["check"] is True


def test_run_embed_match_cleans_temp_file():
    created_files = []
    original_mkstemp = __import__("tempfile").mkstemp

    def track_mkstemp(*args, **kwargs):
        fd, path = original_mkstemp(*args, **kwargs)
        created_files.append(path)
        return fd, path

    with patch("tempfile.mkstemp", side_effect=track_mkstemp):
        with patch("subprocess.run", side_effect=mock_subprocess_run):
            run_embed_match("test_resume.pdf")

    for temp_file in created_files:
        assert not os.path.exists(temp_file), f"Temp file {temp_file} was not cleaned up"


def test_run_embed_match_cleans_temp_file_on_exception():
    created_files = []
    original_mkstemp = __import__("tempfile").mkstemp

    def track_mkstemp(*args, **kwargs):
        fd, path = original_mkstemp(*args, **kwargs)
        created_files.append(path)
        return fd, path

    def failing_subprocess(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "test")

    with patch("tempfile.mkstemp", side_effect=track_mkstemp):
        with patch("subprocess.run", side_effect=failing_subprocess):
            try:
                run_embed_match("test_resume.pdf")
            except Exception:
                pass

    for temp_file in created_files:
        assert not os.path.exists(temp_file), f"Temp file {temp_file} was not cleaned up after exception"
