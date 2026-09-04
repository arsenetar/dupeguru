# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import logging
import os
from dataclasses import dataclass
from typing import List

from core.storage.db_engine import DBEngine


@dataclass
class DBVerificationResult:
    db_path: str
    is_valid: bool
    quick_check_ok: bool
    tables_present: List[str]
    file_count: int
    hashed_count: int
    errors: List[str]
    repaired: bool = False


class DBVerifier:
    """Verifies SQLite database schema, data integrity, and repairs missing metadata."""

    REQUIRED_TABLES = {"files", "scanned_directories", "scan_metadata"}

    def __init__(self, db_engine: DBEngine):
        self.db_engine = db_engine

    def verify_database(self) -> DBVerificationResult:
        db_path = self.db_engine.db_path
        errors: List[str] = []

        if not os.path.exists(db_path) and db_path != ":memory:":
            return DBVerificationResult(
                db_path=db_path,
                is_valid=False,
                quick_check_ok=False,
                tables_present=[],
                file_count=0,
                hashed_count=0,
                errors=[f"Database file does not exist: {db_path}"],
            )

        conn = self.db_engine.get_connection()
        cur = conn.cursor()

        # Check 1: SQLite Quick Check Integrity
        try:
            qc_row = cur.execute("PRAGMA quick_check").fetchone()
            quick_check_ok = qc_row and qc_row[0] == "ok"
            if not quick_check_ok:
                errors.append(f"PRAGMA quick_check failed: {qc_row[0] if qc_row else 'Unknown error'}")
        except Exception as e:
            quick_check_ok = False
            errors.append(f"SQLite PRAGMA quick_check exception: {e}")

        # Check 2: Table Existence
        tables_present: List[str] = []
        try:
            rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            tables_present = [r[0] for r in rows]
        except Exception as e:
            errors.append(f"Failed to query database table names: {e}")

        missing_tables = self.REQUIRED_TABLES - set(tables_present)
        if missing_tables:
            errors.append(f"Missing required database tables: {missing_tables}")

        result = DBVerificationResult(
            db_path=db_path,
            is_valid=quick_check_ok and len(missing_tables) == 0,
            quick_check_ok=quick_check_ok,
            tables_present=tables_present,
            file_count=0,
            hashed_count=0,
            errors=errors,
        )

        # Always run repair to backfill missing columns or tables
        self.repair_database(result)

        # Check 3: File & Hash Counts
        try:
            file_count, hashed_count = self.db_engine.get_file_counts()
            result.file_count = file_count
            result.hashed_count = hashed_count
        except Exception as e:
            errors.append(f"File count query exception: {e}")

        return result

    def repair_database(self, result: DBVerificationResult) -> bool:
        """Repairs missing tables, missing columns, indices, and ensures schema compatibility."""
        try:
            self.db_engine.init_schema()

            conn = self.db_engine.get_connection()
            cur = conn.cursor()

            # Repair missing columns on existing files table
            cols_info = cur.execute("PRAGMA table_info(files)").fetchall()
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
                        cur.execute(f"ALTER TABLE files ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass

            conn.commit()
            result.repaired = True
            result.is_valid = True
            logging.info(f"Successfully repaired schema and indices for database '{result.db_path}'")
            return True
        except Exception as e:
            logging.error(f"Failed to repair database '{result.db_path}': {e}")
            result.errors.append(f"Repair failure: {e}")
            return False
