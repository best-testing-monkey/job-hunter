# E13-S33 — Serve job screenshots through a Flask route

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here. Epic 13 app stories follow it unchanged (they only touch `app/`).

## Goal

Let the browser load `scraper/screenshots/<stem>.png` for a match, with no way to request an arbitrary file.

## Context

- Screenshot files: `scraper/screenshots/<stem>.png`, where `<stem>` is the stem of the match's job file (`scraper/jobs/<stem>.md`). A match row (`db.get_match(conn, match_id)`) has `job_file` = absolute path of that `.md`. Therefore `screenshot path = Path(job_file).resolve().parent.parent / "screenshots" / f"{Path(job_file).stem}.png"`.
- `app/webapp/jobs.py` holds job-file helpers (`parse_job_file`, `site_name_for`, `get_job_description`); `app/webapp/routes.py` has the blueprint `bp = Blueprint("main", __name__)` and the job detail route `/jobs/<int:match_id>` (uses `abort(404)` when the match is missing; imports from flask include `abort`).
- Path safety: the URL carries only the integer match id (`<int:...>` converter); the file path is derived from the DB's `job_file`, never from user input. Still verify the resolved PNG path's parent is exactly the sibling `screenshots` dir and the file is a regular `.png` file.
- Test setup to copy: `test_job_detail_with_valid_match` in `app/tests/test_routes.py` (~line 757): `create_app()`, `app.config["DATABASE"]`, `db.upsert_match(conn, ..., job_file=str(job_file), ...)`, `db.get_matches`.

## Files to create/modify

- `app/webapp/jobs.py`
- `app/webapp/routes.py`
- `app/tests/test_jobs.py`
- `app/tests/test_routes.py`

## Acceptance criteria

- `jobs.screenshot_path_for(job_file: str | Path) -> Path | None`: returns the path described above if it exists as a file, else `None`.
- Route `@bp.route("/jobs/<int:match_id>/screenshot")`, function name `job_screenshot`: 404 if the match does not exist; 404 if `screenshot_path_for(match["job_file"])` is `None`; otherwise `send_file(path, mimetype="image/png")` (HTTP 200).
- Tests in `test_jobs.py` (using `tmp_path/"jobs"/"a-1-x.md"` and `tmp_path/"screenshots"/"a-1-x.png"`): returns the PNG path when it exists; `None` when the PNG is absent; `None` when the screenshots dir is absent.
- Tests in `test_routes.py`: (1) match whose job file has a sibling screenshot (write minimal PNG bytes `b"\x89PNG\r\n\x1a\n" + b"0"*16`) -> `GET /jobs/<id>/screenshot` is 200, `Content-Type` is `image/png`, body equals the bytes; (2) match without screenshot -> 404; (3) unknown id `999999` -> 404; (4) `GET /jobs/abc/screenshot` -> 404; (5) `GET /jobs/1/screenshot/../../etc/passwd` and `GET /jobs/%2e%2e%2f/screenshot` -> 404; (6) a match whose `job_file` stem would resolve outside the screenshots dir (e.g. `job_file="/tmp/x/../jobs/a.md"` with a PNG only reachable via `..`) never serves a file outside `<parent>/screenshots`.
- `uv run pytest tests/ -q` passes.

## Definition of done

- Gates pass: `uv run pytest tests/ -q` from `app/` (zero failures, no fewer passing tests than before).
- Committed in the JOB-HUNTER repo as `E13-S33: Serve job screenshots via Flask route`.
- `docs/todo.md` item for E13-S33 checked off (same repo; may be a second commit `Mark E13-S33 as done in todo`).
