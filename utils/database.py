"""
SQLite persistence for trip history and analytics.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "travel_planner.db"


def get_connection():
    """Return SQLite connection with row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they do not exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            num_days INTEGER NOT NULL,
            budget REAL NOT NULL,
            style TEXT NOT NULL,
            interests TEXT NOT NULL,
            persona TEXT,
            predicted_cost REAL,
            trip_score REAL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_trip(city, num_days, budget, style, interests, persona, predicted_cost, trip_score):
    """Insert a trip record."""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO trips (city, num_days, budget, style, interests, persona,
                           predicted_cost, trip_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            city,
            num_days,
            budget,
            style,
            ",".join(interests),
            persona,
            predicted_cost,
            trip_score,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_trip_stats():
    """Aggregate stats for dashboard charts."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as c FROM trips").fetchone()["c"]
    personas = conn.execute(
        "SELECT persona, COUNT(*) as c FROM trips GROUP BY persona"
    ).fetchall()
    conn.close()
    return {
        "total_trips": total,
        "personas": {r["persona"]: r["c"] for r in personas if r["persona"]},
    }
