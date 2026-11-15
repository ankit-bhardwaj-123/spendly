"""SQLite data layer for Spendly: connection helper, schema and demo seed data."""

import sqlite3
from datetime import date
from pathlib import Path

from werkzeug.security import generate_password_hash

# Absolute path so the DB lands in the project root whatever folder uvicorn starts from.
DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db() -> sqlite3.Connection:
    """Open a connection with dict-like rows and foreign keys enforced."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create all tables. Safe to call on every startup."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db() -> None:
    """Insert a demo user and 8 sample expenses, only if no users exist yet."""
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        today = date.today()

        def day(d: int) -> str:
            # Keep every date in the current month and never after today.
            return today.replace(day=min(d, today.day)).isoformat()

        sample = [
            (12.50, "Food", day(1), "Lunch at the cafe"),
            (45.00, "Transport", day(3), "Monthly bus pass top-up"),
            (120.00, "Bills", day(5), "Electricity bill"),
            (30.00, "Health", day(8), "Pharmacy"),
            (18.99, "Entertainment", day(10), "Movie tickets"),
            (64.25, "Shopping", day(12), "New shoes"),
            (9.75, "Other", day(14), "Stationery"),
            (38.40, "Food", day(15), "Groceries"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            [(user_id, *row) for row in sample],
        )
        conn.commit()
    finally:
        conn.close()
