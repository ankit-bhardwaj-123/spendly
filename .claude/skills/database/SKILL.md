---
name: database
description: Use when touching Spendly's SQLite data layer (database/db.py, tables, seed data, startup init) or writing any route that reads or writes users or expenses.
---

# Spendly database (SQLite)

Built in Step 1 (spec `.claude/spec/01-database-setup.md`, plan `.claude/plan/01-database-setup.md`).

## Key files
- `database/db.py`: the whole data layer.
  - `DB_PATH` (`database/db.py:10`): absolute `<project root>/expense_tracker.db`, so it doesn't depend on the working directory (the file is gitignored).
  - `CATEGORIES` (`database/db.py:12`): the fixed list Food, Transport, Bills, Health, Entertainment, Shopping, Other. Reuse it for dropdowns and validation.
  - `get_db()` (`database/db.py:15`): new connection with `sqlite3.Row` and `PRAGMA foreign_keys = ON`.
  - `init_db()` (`database/db.py:23`): `CREATE TABLE IF NOT EXISTS` for `users` and `expenses`.
  - `seed_db()` (`database/db.py:53`): demo user plus 8 expenses, skipped if any user exists.
- `main.py:9`: `from database.db import get_db, init_db, seed_db`.
- `main.py:13`: the `lifespan` handler runs `init_db()` then `seed_db()` before the first request. It replaces Flask's `app.app_context()`, which the spec mentions but FastAPI doesn't have.
- `database/__init__.py`: empty; makes `database` a package.

## Schema
- `users`: `id` PK autoincrement, `name` NOT NULL, `email` UNIQUE NOT NULL, `password_hash` NOT NULL, `created_at` default `datetime('now')`.
- `expenses`: `id` PK autoincrement, `user_id` NOT NULL → `users(id)`, `amount` REAL NOT NULL, `category` NOT NULL, `date` TEXT NOT NULL (`YYYY-MM-DD`), `description` nullable, `created_at` default `datetime('now')`.
- `created_at` is stored in UTC (SQLite `datetime('now')`), not local time.
- The schema doesn't check categories; validate against `CATEGORIES` in the route.

## Seed data
- Demo login: `demo@spendly.com` / `demo123`, hashed with `werkzeug.security.generate_password_hash`.
- 8 expenses covering all 7 categories (Food twice). Dates come from the inner `day()` helper (`database/db.py:68`): this month, capped at today, so none are in the future.
- Seeding only happens when `users` is empty, so it runs once. Once registration exists, the demo data won't come back while any user is left.

## Conventions (from the spec)
- Raw `sqlite3` only, no ORM. Always use `?` placeholders and never build SQL with f-strings or `%`.
- Open with `get_db()` and close in `finally` (or `with closing(get_db())`). `with conn:` alone commits but does **not** close.
- Call `conn.commit()` after writes; `sqlite3` doesn't autocommit.
- Hash passwords with werkzeug's `generate_password_hash` and check them with `check_password_hash` (for auth in later steps).
- Store `amount` as a float (REAL), never an integer.

## Gotchas
- `CREATE TABLE IF NOT EXISTS` never changes an existing table. After a schema change, delete `expense_tracker.db` and restart, or write an `ALTER TABLE`.
- Foreign keys are per connection in SQLite. Any connection opened without `get_db()` won't enforce them.
- `TestClient(main.app).get(...)` without `with` skips `lifespan`, so on a fresh checkout the DB isn't created. Use `with TestClient(main.app) as c:`.
- `python main.py` uses `reload=True`, so a running server re-runs `lifespan` and creates the DB as soon as `main.py` or `db.py` is saved.
- The JSON `/expenses` API in `main.py` is still in-memory (a dict plus `next_id`, with `title`, not `description`). It doesn't use these tables yet.
- werkzeug is a separate entry in `requirements.txt`. It used to come with Flask, so the spec wrongly calls it "already installed".

## Verify
```bash
python -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app); c.__enter__(); print(c.get('/terms').status_code)"
python -c "from database.db import get_db; c=get_db(); print([c.execute(q).fetchone()[0] for q in ('SELECT COUNT(*) FROM users','SELECT COUNT(*) FROM expenses','PRAGMA foreign_keys')])"
```
The second command should print `[1, 8, 1]` on a freshly seeded DB. Integrity checks: a duplicate email or an `expenses.user_id` that doesn't exist raises `sqlite3.IntegrityError`.
