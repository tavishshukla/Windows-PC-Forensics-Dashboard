import json
import sqlite3
import threading
from datetime import datetime

DB = "forensics_history.db"
_lock = threading.Lock()


def _connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with _lock, _connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            captured_at TEXT NOT NULL,
            cpu REAL, memory REAL, disk REAL,
            process_count INTEGER, connection_count INTEGER,
            risk_score INTEGER, risk_level TEXT
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            captured_at TEXT NOT NULL,
            severity TEXT NOT NULL,
            reason TEXT NOT NULL
        )""")


def record(snapshot, risk):
    captured = snapshot.get("time") or datetime.now().isoformat(timespec="seconds")
    with _lock, _connect() as con:
        con.execute(
            """INSERT INTO snapshots
            (captured_at,cpu,memory,disk,process_count,connection_count,risk_score,risk_level)
            VALUES (?,?,?,?,?,?,?,?)""",
            (captured, snapshot.get("cpu"), snapshot.get("memory"), snapshot.get("disk"),
             len(snapshot.get("processes", [])), len(snapshot.get("connections", [])),
             risk.get("score"), risk.get("level"))
        )
        for finding in risk.get("findings", []):
            con.execute(
                "INSERT INTO findings(captured_at,severity,reason) VALUES(?,?,?)",
                (captured, finding.get("severity", "info"), finding.get("reason", ""))
            )


def recent(limit=120):
    limit = max(1, min(int(limit), 500))
    with _lock, _connect() as con:
        return [dict(x) for x in con.execute(
            "SELECT * FROM snapshots ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()]


def findings(limit=100):
    limit = max(1, min(int(limit), 500))
    with _lock, _connect() as con:
        return [dict(x) for x in con.execute(
            "SELECT * FROM findings ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()]
