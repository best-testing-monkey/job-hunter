# E16-S06 — `core/screenshot_prune.py`: move thin PNGs aside, drop their markdown line

See `APPENDIX-A-standards.md`, `APPENDIX-B-scraper-standards.md` and `APPENDIX-C-screenshot-fix-standards.md` for conventions (Epic 16 edits the owner's `scraper/` repo; commits go to the SCRAPER repo) — do not repeat them here.

## Goal

Existing PNGs that are shorter than a threshold (7 hero strips below 100 px, 9 harveynash 1116x30 blanks) can be moved out of `screenshots/` in one safe step; the matching job markdown loses its `- Screenshot:` bullet. Never deletes anything.

## Context

- PNG header height: `struct.unpack(">II", data[16:24])[1]` (IHDR width, height) after the 8-byte magic `\x89PNG\r\n\x1a\n`; `_png_height` exists in `scraper/job_scraper/core/screenshots.py` after E16-S02 and may be imported (it returns None for unreadable files).
- File naming: `screenshots/<stem>.png` and `jobs/<stem>.md` share the stem `<site_id>-<listing_id>-<slug>` (Appendix B). Site restriction = filename prefix `f"{site_id}-"`.
- `remove_screenshot_line` exists in `scraper/job_scraper/core/markdown_export.py` after E16-S05.
- Real data under `scraper/screenshots/` and `scraper/jobs/` is never touched by a story or test; tests use `tmp_path` only. The drive is NTFS: use `shutil.move`.

## Files to create/modify

- `scraper/job_scraper/core/screenshot_prune.py` (new)
- `scraper/tests/test_screenshot_prune.py` (new)

## Acceptance criteria

- `prune_small_screenshots(screenshots_dir: str, jobs_dir: str, *, min_height: int = 100, sites: Sequence[str] | None = None, move_to: str | None = None, dry_run: bool = False) -> dict[str, int]`. Scans `sorted(Path(screenshots_dir).glob("*.png"))`, restricted to files starting with `f"{site}-"` for any `site` in `sites` (None or empty = all).
- Returns exactly the keys `scanned, small, moved, markdown_updated, unreadable, skipped_exists`. `unreadable` = PNG whose height cannot be read (left in place, never moved).
- `dry_run=True`: counts `small` but moves/edits nothing (`moved` = 0, `markdown_updated` = 0). `dry_run=False` with `move_to is None` raises `ValueError("move_to is required unless dry_run")` before touching anything.
- For each PNG with height < `min_height`: create `move_to` (mkdir parents), move the file there (if a file of that name already exists in `move_to`, leave the PNG in place and count `skipped_exists`), then call `remove_screenshot_line(str(Path(jobs_dir)/f"{stem}.md"))` and count `markdown_updated` when it returns True. Running again changes nothing (idempotent: the PNG is gone, the line is gone).
- Tests (tmp_path only; build PNGs with the stdlib only, e.g. a helper `make_png(path, width, height)` that writes the magic, an IHDR chunk with `zlib.crc32` and a minimal valid IDAT/IEND — or only magic + IHDR if that is all `_png_height` needs; keep the helper in the test file): heights 65, 99, 100, 300 with threshold 100 move exactly 65 and 99; their markdown loses the bullet while the others keep it; `sites=["hero"]` leaves `harveynash-*` thin files alone; dry run changes nothing and reports `small`; missing `move_to` without dry_run raises ValueError and moves nothing; a garbage file named `x.png` counts `unreadable` and stays; a pre-existing target name counts `skipped_exists`; second run reports `moved == 0`; a PNG with no markdown file still moves (`markdown_updated` 0).

## Definition of done

- Run only `uv run pytest tests/test_screenshot_prune.py -q` from `scraper/`.
- Committed in the SCRAPER repo as `E16-S06: Add screenshot prune module`.
- The orchestrator ticks `docs/todo.md`. Needs E16-S02 and E16-S05.
