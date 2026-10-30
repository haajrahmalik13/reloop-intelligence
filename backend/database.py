
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "reloop.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                condition TEXT NOT NULL,
                uniform_models INTEGER NOT NULL,
                pickup_cost REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_donation(donation):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO donations (
                company_name, device_type, quantity,
                condition, uniform_models, pickup_cost
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            donation.company_name,
            donation.device_type,
            donation.quantity,
            donation.condition,
            int(donation.uniform_models),
            donation.pickup_cost
        ))

        return cursor.lastrowid


def get_all_donations():
    with get_connection() as connection:
        rows = connection.execute("""
        SELECT * FROM donations
        ORDER BY id DESC
        """).fetchall()

        donations = []

        for row in rows:
            item = dict(row)
            item["uniform_models"] = bool(item["uniform_models"])
            donations.append(item)

        return donations


def update_donation_status(donation_id, status):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE donations
            SET status = ?
            WHERE id = ?
        """, (status, donation_id))

        return cursor.rowcount > 0
