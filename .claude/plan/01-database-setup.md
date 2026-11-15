# Plan: Step 1 — Database Setup (Spendly)

> On approval, the first action is to save this plan to
> `Desktop/expense_tracker/.claude/plan/01-database-setup.md` (folder already exists).

## Context

`database/db.py` is an empty stub. Spec `.claude/spec/01-database-setup.md` asks for a working
SQLite data layer (`get_db`, `init_db`, `seed_db`) with `users` and `expenses` tables, a demo user
and 8 sample expenses, so later steps (auth, profile, expenses) have real storage.

The spec was written for the Flask app, so three things are adapted to this repo:

| Spec says | Reality | Plan |
| --- | --- | --- |
| `app.py` | The backend is `main.py` (FastAPI) | Edit `main.py` |
| `app.app_context()` on startup | FastAPI has no app context | Use a FastAPI `lifespan` handler |
| werkzeug "already installed" | Not in `.venv` or `requirements.txt` | Add `werkzeug` to `requirements.txt` and install it (user chose this) |

DB file: `expense_tracker.db` in the project root (already in `.gitignore`).

## Changes

### 1. `requirements.txt`
Add a line `werkzeug`, then `pip install -r requirements.txt` in `.venv`.

### 2. `database/db.py` (replace stub)
- `DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"` — absolute, so it
  does not depend on the working directory uvicorn is started from.
- `CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]`
  (exported so later steps can reuse it for dropdowns/validation).
- `get_db()`: `sqlite3.connect(DB_PATH)`, `row_factory = sqlite3.Row`,
  `execute("PRAGMA foreign_keys = ON")`, return the connection.
- `init_db()`: one `executescript` with two `CREATE TABLE IF NOT EXISTS` statements exactly per
  spec section 4:
  - `users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')))`
  - `expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id),
    amount REAL NOT NULL, category TEXT NOT NULL, date TEXT NOT NULL, description TEXT,
    created_at TEXT DEFAULT (datetime('now')))`
  - Close the connection in `finally`.
- `seed_db()`:
  - `SELECT COUNT(*) FROM users`; if > 0, return early.
  - Insert Demo User / `demo@spendly.com` / `generate_password_hash("demo123")` with `?` params;
    take `cursor.lastrowid` as `user_id`.
  - Build 8 expenses covering all 7 categories (Food twice), dates in the current month built with
    `date.today().replace(day=d).isoformat()` using days 1–28 capped at today's day so none are in
    the future and all stay `YYYY-MM-DD`.
  - `executemany` with `?` placeholders, `commit()`, close in `finally`.
- No string formatting in any SQL; no ORM.

### 3. `main.py`
- `from contextlib import asynccontextmanager` and `from database.db import get_db, init_db, seed_db`
  (`get_db` imported per spec for later steps).
- Add:
  ```python
  @asynccontextmanager
  async def lifespan(app):
      init_db()
      seed_db()
      yield
  ```
  and change to `app = FastAPI(title="Spendly", lifespan=lifespan)`.
- No route changes; the in-memory `/expenses` JSON API stays as is (spec: routes unchanged).

### 4. Housekeeping (per global CLAUDE.md)
- `C:\Users\Vivek Rajotia\CHANGELOG.md` → `## [Unreleased]` / Added: 2026-11-14 SQLite data layer
  (`database/db.py`, `main.py`, `requirements.txt`).
- Update project `CLAUDE.md`: Database section (now implemented, lifespan startup, file path) and
  Commands (werkzeug in requirements).
- Skill file `.claude/skills/...` only after the user confirms the feature is done.

## Verification

1. `python -c "from fastapi.testclient import TestClient; import main; c=TestClient(main.app).__enter__(); print(c.get('/terms').status_code)"`
   → 200, and `expense_tracker.db` exists (the `with`/`__enter__` runs the lifespan).
2. Script check (scratchpad), using `get_db()`:
   - `SELECT COUNT(*)` → users = 1, expenses = 8; distinct categories = 7; all dates match
     `^\d{4}-\d{2}-\d{2}$` and are in the current month.
   - `check_password_hash(row["password_hash"], "demo123")` → True.
   - Run `init_db(); seed_db()` again → counts unchanged.
   - Insert duplicate `demo@spendly.com` → `sqlite3.IntegrityError` (UNIQUE).
   - Insert expense with `user_id=999` → `sqlite3.IntegrityError` (FOREIGN KEY).
3. `python main.py` starts without errors on :5001.
