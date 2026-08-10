# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Tuple


class DBEngine:
    """Thread-safe, connection-isolated SQLite database engine."""

    SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY,
        size INTEGER,
        mtime_ns INTEGER,
        entry_dt TEXT,
        digest BLOB,
        digest_partial BLOB,
        digest_samples BLOB
    );
    CREATE TABLE IF NOT EXISTS scanned_directories (
        path TEXT PRIMARY KEY
    );
    CREATE TABLE IF NOT EXISTS scan_metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_files_size ON files(size);
    CREATE INDEX IF NOT EXISTS idx_files_digest ON files(digest);
    CREATE INDEX IF NOT EXISTS idx_files_digest_partial ON files(digest_partial);
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            if self.db_path != ":memory:":
                db_dir = os.path.dirname(self.db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
            self._local.conn = sqlite3.connect(self.db_path, timeout=60.0)
            self._local.conn.row_factory = sqlite3.Row
            if self.db_path != ":memory:":
                try:
                    self._local.conn.execute("PRAGMA journal_mode=WAL;")
                    self._local.conn.execute("PRAGMA synchronous=NORMAL;")
                    self._local.conn.execute("PRAGMA busy_timeout=60000;")
                except Exception:
                    pass
        return self._local.conn

    def init_schema(self) -> None:
        with self.transaction() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    path TEXT PRIMARY KEY,
                    size INTEGER,
                    mtime_ns INTEGER,
                    entry_dt TEXT,
                    digest BLOB,
                    digest_partial BLOB,
                    digest_samples BLOB
                );
                """)
            conn.execute("CREATE TABLE IF NOT EXISTS scanned_directories (path TEXT PRIMARY KEY);")
            conn.execute("CREATE TABLE IF NOT EXISTS scan_metadata (key TEXT PRIMARY KEY, value TEXT);")

            # Check and backfill missing columns on pre-existing files tables
            cols_info = conn.execute("PRAGMA table_info(files)").fetchall()
            existing_cols = {c[1] for c in cols_info}
            required_cols = {
                "mtime_ns": "INTEGER",
                "entry_dt": "TEXT",
                "digest": "BLOB",
                "digest_partial": "BLOB",
                "digest_samples": "BLOB",
            }
            for col_name, col_type in required_cols.items():
                if col_name not in existing_cols:
                    try:
                        conn.execute(f"ALTER TABLE files ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass

            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files(size);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_digest_partial ON files(digest_partial);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_digest ON files(digest);")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_groups (
                    group_id INTEGER PRIMARY KEY,
                    pivot_path TEXT,
                    saved_bytes INTEGER
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_entries (
                    group_id INTEGER,
                    file_path TEXT,
                    is_pivot INTEGER,
                    FOREIGN KEY(group_id) REFERENCES duplicate_groups(group_id)
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dupe_entries_group ON duplicate_entries(group_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dupe_entries_file ON duplicate_entries(file_path);")

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn is not None:
            try:
                self._local.conn.close()
            except Exception:
                pass
            self._local.conn = None

    # Helper Queries
    def get_file_counts(self) -> Tuple[int, int]:
        """Returns (total_file_count, hashed_file_count)."""
        conn = self.get_connection()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT COUNT(*), COUNT(CASE WHEN digest IS NOT NULL OR digest_partial IS NOT NULL THEN 1 END) FROM files"
        ).fetchone()
        if not row:
            return 0, 0
        return int(row[0]), int(row[1])

    def get_candidate_sizes(self) -> List[int]:
        conn = self.get_connection()
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT DISTINCT size FROM files WHERE size > 0 GROUP BY size HAVING COUNT(*) > 1 ORDER BY size DESC"
        ).fetchall()
        return [r[0] for r in rows]

    def get_files_by_sizes(self, sizes: List[int]) -> List[Dict[str, Any]]:
        if not sizes:
            return []
        conn = self.get_connection()
        cur = conn.cursor()
        placeholders = ",".join("?" for _ in sizes)
        query = f"SELECT path, size, mtime_ns, digest, digest_partial FROM files WHERE size IN ({placeholders})"
        rows = cur.execute(query, sizes).fetchall()
        return [dict(r) for r in rows]

    def set_metadata(self, key: str, value: str) -> None:
        with self.transaction() as conn:
            conn.execute(
                "INSERT INTO scan_metadata (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value)),
            )

    def get_metadata(self) -> Dict[str, str]:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            rows = cur.execute("SELECT key, value FROM scan_metadata").fetchall()
            return {r[0]: r[1] for r in rows}
        except Exception:
            return {}

    def save_duplicate_groups(self, groups) -> None:
        group_rows = []
        entry_rows = []
        for g in groups:
            group_rows.append((g.group_id, g.pivot.path, g.saved_bytes))
            entry_rows.append((g.group_id, g.pivot.path, 1))
            for d in g.duplicates:
                entry_rows.append((g.group_id, d.path, 0))

        with self.transaction() as conn:
            conn.execute("DELETE FROM duplicate_entries;")
            conn.execute("DELETE FROM duplicate_groups;")
            conn.executemany(
                "INSERT INTO duplicate_groups (group_id, pivot_path, saved_bytes) VALUES (?, ?, ?)",
                group_rows,
            )
            conn.executemany(
                "INSERT INTO duplicate_entries (group_id, file_path, is_pivot) VALUES (?, ?, ?)",
                entry_rows,
            )

    def has_saved_duplicate_groups(self) -> bool:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            table_check = cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='duplicate_groups'"
            ).fetchone()
            if not table_check:
                return False

            status_val = self.get_metadata("status")
            if status_val == "completed":
                return True

            row = cur.execute("SELECT COUNT(*) FROM duplicate_groups").fetchone()
            return bool(row and row[0] > 0)
        except Exception:
            return False

    def delete_files_by_paths(self, paths: List[str]) -> int:
        if not paths:
            return 0
        with self.transaction() as conn:
            conn.executemany("DELETE FROM duplicate_entries WHERE file_path = ?", [(p,) for p in paths])
            conn.executemany("DELETE FROM files WHERE path = ?", [(p,) for p in paths])
            conn.execute(
                "DELETE FROM duplicate_groups WHERE group_id NOT IN ("
                "SELECT group_id FROM duplicate_entries WHERE is_pivot = 0"
                ")"
            )
            conn.execute(
                "DELETE FROM duplicate_entries WHERE group_id NOT IN (" "SELECT group_id FROM duplicate_groups" ")"
            )
            rem_dupes = conn.execute("SELECT COUNT(*) FROM duplicate_entries WHERE is_pivot = 0").fetchone()[0]
            rem_matches = conn.execute("SELECT COUNT(*) FROM duplicate_groups").fetchone()[0]
            conn.execute(
                "INSERT INTO scan_metadata (key, value) VALUES ('dupe_count', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(rem_dupes),),
            )
            conn.execute(
                "INSERT INTO scan_metadata (key, value) VALUES ('match_count', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(rem_matches),),
            )
        return len(paths)

    def get_candidate_duplicate_files(self):
        from core.domain.models import FileDTO

        query = """
        WITH candidate_sizes AS (
            SELECT size FROM files WHERE size > 0 GROUP BY size HAVING COUNT(*) > 1
        )
        SELECT f.path, f.size, f.mtime_ns, f.digest_partial, f.digest
        FROM files f
        JOIN candidate_sizes cs ON f.size = cs.size
        ORDER BY f.size DESC, f.path ASC
        """
        conn = self.get_connection()
        cur = conn.cursor()
        rows = cur.execute(query).fetchall()
        return [
            FileDTO(
                path=r["path"],
                size=r["size"],
                mtime_ns=r["mtime_ns"] if r["mtime_ns"] else 0,
                digest_partial=r["digest_partial"],
                digest=r["digest"],
            )
            for r in rows
        ]

    def load_duplicate_groups(self):
        from core.domain.models import DuplicateGroupDTO, FileDTO

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            g_rows = cur.execute(
                "SELECT group_id, pivot_path, saved_bytes FROM duplicate_groups ORDER BY group_id ASC"
            ).fetchall()
            if not g_rows:
                return []

            query = """
            SELECT de.group_id, de.is_pivot, f.path, f.size, f.mtime_ns, f.digest_partial, f.digest
            FROM duplicate_entries de
            JOIN files f ON de.file_path = f.path
            ORDER BY de.group_id ASC, de.is_pivot DESC
            """
            e_rows = cur.execute(query).fetchall()

            groups_map = {}
            for r in g_rows:
                groups_map[r["group_id"]] = {
                    "group_id": r["group_id"],
                    "saved_bytes": r["saved_bytes"],
                    "pivot": None,
                    "duplicates": [],
                }

            for r in e_rows:
                g_id = r["group_id"]
                if g_id in groups_map:
                    dto = FileDTO(
                        path=r["path"],
                        size=r["size"],
                        mtime_ns=r["mtime_ns"] if r["mtime_ns"] else 0,
                        digest_partial=r["digest_partial"],
                        digest=r["digest"],
                    )
                    if r["is_pivot"] == 1:
                        groups_map[g_id]["pivot"] = dto
                    else:
                        groups_map[g_id]["duplicates"].append(dto)

            result = []
            for g_id, gdata in groups_map.items():
                if gdata["pivot"]:
                    result.append(
                        DuplicateGroupDTO(
                            group_id=gdata["group_id"],
                            pivot=gdata["pivot"],
                            duplicates=gdata["duplicates"],
                            saved_bytes=gdata["saved_bytes"],
                        )
                    )
            return result
        except Exception:
            return []
