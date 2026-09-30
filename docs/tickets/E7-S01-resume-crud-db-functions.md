# E7-S01 — Add content column and resume CRUD db functions

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Add a `content` column to the `resumes` table and the `create_resume`/`update_resume`/`delete_resume` functions that make the app own a resume's text (write/rewrite/remove its backing file), per `docs/DESIGN_DOC.md`'s "Resume CRUD (second slice)" section.

## Context

- Everything from the first slice (E1–E6) is done and committed. `app/webapp/db.py` currently has `get_connection`, `init_db`, `register_resume`, `list_resumes`, `upsert_match`, `get_matches`, `get_resume`. Read the whole file first.
- Read `docs/DESIGN_DOC.md`'s "Resume CRUD (second slice)" section in full — it specifies the exact schema change and function signatures.
- Do NOT remove `register_resume` yet or touch `routes.py`/templates in this story — a later story (E7-S02) switches the route over and removes it then. This story is purely additive to `db.py`/`__init__.py`.
- There is no real persisted data yet (`app/instance/matches.db` is gitignored, local-only, and safe to delete if a stale copy with the old schema exists on your machine — just delete the file, don't write a migration).

## Files to modify

- `app/webapp/db.py`:
  - Change the `resumes` table's `CREATE TABLE IF NOT EXISTS` statement to add `content TEXT` as a column (nullable). Keep `file_path TEXT NOT NULL UNIQUE` as-is.
  - Add `create_resume(conn: sqlite3.Connection, resumes_dir: str, name: str, content: str) -> int`: insert a row with `file_path=""` as a placeholder to get an autoincrement id, compute `file_path = str(Path(resumes_dir) / f"{id}.md")`, write `content` to that path (create `resumes_dir` first via `Path(resumes_dir).mkdir(parents=True, exist_ok=True)` if it doesn't exist), then `UPDATE resumes SET file_path = ? WHERE id = ?`. Return the id.
  - Add `update_resume(conn: sqlite3.Connection, resume_id: int, name: str, content: str) -> None`: update the row's `name` and `content`, then look up its `file_path` and overwrite that file with the new `content`.
  - Add `delete_resume(conn: sqlite3.Connection, resume_id: int) -> None`: delete all `matches` rows for this `resume_id`, delete the `resumes` row, then `Path(file_path).unlink(missing_ok=True)` (look up `file_path` before deleting the row).
- `app/webapp/__init__.py`: add `app.config["RESUMES_DIR"] = os.path.join(app.instance_path, "resumes")`, next to the existing `DATABASE` config line.
- `app/tests/test_db.py`: add tests (see below).

## Acceptance criteria

- `create_resume` with a `tmp_path`-based `resumes_dir`: the returned id's row has a non-empty `file_path` under that directory, and the file at that path exists with the exact `content` passed in.
- `update_resume`: after calling it, `get_resume`'s row shows the new `name`/`content`, the `file_path` is unchanged from before the update, and the file at that path now contains the new content.
- `delete_resume`: after calling it on a resume that has matches, `get_resume` returns `None`, `get_matches` for that id returns an empty list, and the file at its former `file_path` no longer exists. Also test that calling `delete_resume` a second time (or on an id whose file is already gone) doesn't raise.
- `uv run pytest tests/ -q` (from `app/`) passes — all existing tests plus these new ones.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E7-S01: Add content column and resume CRUD db functions`.
- `docs/todo.md` item for E7-S01 checked off.
