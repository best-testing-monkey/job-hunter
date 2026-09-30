# E3-S01 — SQLite schema and connection helper

See `APPENDIX-A-standards.md` for code style, test, gate, and commit conventions — don't repeat them here.

## Goal

Create the SQLite schema (`resumes`, `matches` tables) and a `db.py` module providing a connection helper and schema initialization.

## Context

- Depends on E1-S01 (needs `app/webapp/` to exist as a package).
- `docs/DESIGN_DOC.md`'s "Data model" section has the exact `CREATE TABLE` statements for `resumes` and `matches` — use them verbatim, don't redesign the schema.
- Independent of E2-S01/E4-S01/E5-S01 — can be built in parallel with those.

## Files to create

- `app/webapp/db.py` (new)
- `app/tests/test_db.py` (new)

## Acceptance criteria

- `db.py` exposes:
  - `get_connection(db_path: str) -> sqlite3.Connection` — opens a connection with `conn.row_factory = sqlite3.Row` set.
  - `init_db(conn: sqlite3.Connection) -> None` — creates both tables via `CREATE TABLE IF NOT EXISTS`, exact schema from `docs/DESIGN_DOC.md`'s Data model section (column names, types, `UNIQUE` constraints, foreign key on `matches.resume_id`).
- Test (`tmp_path`-based, not a real file in the repo): call `get_connection` on a temp path, call `init_db`, then query `sqlite_master` (`SELECT name FROM sqlite_master WHERE type='table'`) and assert both `resumes` and `matches` are present.
- `uv run pytest tests/ -q` (from `app/`) passes.

## Definition of done

- Gates pass (see Appendix A).
- Committed as `E3-S01: Add SQLite schema and connection helper`.
- `docs/todo.md` item for E3-S01 checked off.
