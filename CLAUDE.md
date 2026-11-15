# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Spendly", a teaching-style expense tracker. It started as a Flask template and was converted to **FastAPI + Jinja2**. Many features are stubs that are meant to be built step by step ("coming in Step N" placeholder routes, `static/js/main.js` is empty with instructions only). Step specs live in `.claude/spec/`, their implementation plans in `.claude/plan/`, and per-feature notes in `.claude/skills/` (check there before exploring; `database` is done). The product name in code and UI is **Spendly** (users sometimes write "Spendely").

## Commands

Dependencies are in `requirements.txt` (`fastapi[standard]`, `pytest`, `werkzeug` for password hashing); the virtualenv is `.venv/`.

```bash
pip install -r requirements.txt
python main.py                 # uvicorn with reload on http://localhost:5001 (port kept from the Flask app)
fastapi dev main.py            # alternative, port 8000
```

There are no tests yet. To smoke-test a route without starting a server:

```bash
python -c "from fastapi.testclient import TestClient; import main; print(TestClient(main.app).get('/terms').status_code)"
```

The startup hook (and so DB creation and seeding) runs only when `TestClient` is used as a context manager (`with TestClient(main.app) as c:`).

pytest is installed for when tests are added (`pytest path/to/test_file.py::test_name` for a single test).

## Architecture

- **`main.py` is the whole backend.** A `lifespan` handler runs `init_db()` and `seed_db()` on startup. It has three groups of routes:
  1. HTML pages (`/`, `/register`, `/login`, `/terms`, `/privacy`) rendered with `templates.TemplateResponse(request, "<name>.html")`.
  2. Placeholder `PlainTextResponse` routes for features not built yet (logout, profile, add/edit/delete expense pages).
  3. An in-memory JSON CRUD API on `/expenses` (a dict plus a `next_id` global, lost on restart).
- **Route order matters:** `/expenses/add` must stay declared before `/expenses/{expense_id}`, or "add" is parsed as an id.
- **Function names are route names.** Templates call `url_for('landing')`, `url_for('register')`, etc., so renaming a route function breaks links. Static files use `url_for('static', path='...')` (FastAPI's `path=`, not Flask's `filename=`).
- **Forms post to routes that don't exist yet.** `login.html` and `register.html` POST to `/login` and `/register`, and templates render an `{{ error }}` variable that no route passes yet.
- **Templates:** every page extends `templates/base.html`, which holds the navbar, the footer (including the Terms and Privacy links) and the blocks `title`, `head`, `content`, `scripts`. Footer changes go in `base.html`, not `landing.html`.
- **Styles:**
  - `static/css/style.css` is the global stylesheet. The theme lives in its `:root` variables (`--ink*`, `--paper*`, `--accent` green, `--accent-2` gold; fonts DM Serif Display and DM Sans, loaded from Google Fonts in `base.html`).
  - `static/css/landing.css` holds only the landing hero (`home-hero-*` classes). `landing.html` loads it through `{% block head %}`. The old `.hero`/`.mock-*` rules in `style.css` are now unused.
  - The Terms and Privacy pages share the `.terms-*` classes in `style.css`. Auth pages use `.auth-*`.
- **Database:** raw `sqlite3` in `database/db.py` (`get_db`, `init_db`, `seed_db`, `CATEGORIES`), file `expense_tracker.db` in the project root (gitignored).
  - Rules: no ORM, `?` placeholders only, close every connection.
  - Demo login: `demo@spendly.com` / `demo123`.
  - The `/expenses` JSON API is still in-memory and doesn't use the DB yet.
  - Schema, seed data and gotchas: `.claude/skills/database/SKILL.md`.

## Gotchas

- The git repository root is the user's home folder (`C:\Users\Vivek Rajotia`), not this project, so `CHANGELOG.md` lives there and `git status` shows unrelated files.
- No browser automation is installed. For a visual check, start the server and use headless Edge: `msedge --headless=new --window-size=1000,1000 --screenshot=<out.png> http://localhost:5001/`. Windows narrower than about 500px get cropped instead of shrunk, so mobile shots at 390px look cut off when they aren't.
