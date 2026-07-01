"""
database.history
-----------------
Lightweight SQLite history store. Runs on the main thread's connection but
all write operations are cheap (single-row inserts), so this doesn't need
its own worker thread — heavy work (the actual math) happens in
core.math_engine and is what gets offloaded to a background thread in the
UI layer (see app/ui/screens/calculator_screen.py).
"""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HistoryEntry:
    id: int
    expression: str
    result: str
    timestamp: float
    favorite: bool = False


class HistoryStore:
    def __init__(self, db_path: str | Path = "calc_history.db"):
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT NOT NULL,
                timestamp REAL NOT NULL,
                favorite INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self._conn.commit()

    def add(self, expression: str, result: str) -> HistoryEntry:
        ts = time.time()
        cur = self._conn.execute(
            "INSERT INTO history (expression, result, timestamp, favorite) VALUES (?, ?, ?, 0)",
            (expression, result, ts),
        )
        self._conn.commit()
        return HistoryEntry(id=cur.lastrowid, expression=expression, result=result, timestamp=ts)

    def recent(self, limit: int = 100) -> list[HistoryEntry]:
        rows = self._conn.execute(
            "SELECT id, expression, result, timestamp, favorite FROM history "
            "ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [HistoryEntry(id=r[0], expression=r[1], result=r[2], timestamp=r[3], favorite=bool(r[4])) for r in rows]

    def toggle_favorite(self, entry_id: int) -> None:
        self._conn.execute(
            "UPDATE history SET favorite = 1 - favorite WHERE id = ?", (entry_id,)
        )
        self._conn.commit()

    def favorites(self) -> list[HistoryEntry]:
        rows = self._conn.execute(
            "SELECT id, expression, result, timestamp, favorite FROM history "
            "WHERE favorite = 1 ORDER BY timestamp DESC"
        ).fetchall()
        return [HistoryEntry(id=r[0], expression=r[1], result=r[2], timestamp=r[3], favorite=bool(r[4])) for r in rows]

    def clear(self) -> None:
        self._conn.execute("DELETE FROM history")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
