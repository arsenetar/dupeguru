import hashlib
import json
import logging
import os
import sqlite3
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional


class CrossDBMatcher:
    def __init__(self, db_paths: List[str], cache_dir: Optional[str] = None):
        self.db_paths = sorted([os.path.abspath(p) for p in db_paths if os.path.exists(p)])
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.local/share/de-dup")
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_db_path = os.path.join(cache_dir, "cross_scan_cache.db")
        self._init_cache_db()

    def _init_cache_db(self):
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cross_scan_cache (
                        set_key TEXT PRIMARY KEY,
                        fingerprint TEXT NOT NULL,
                        results_json TEXT NOT NULL,
                        total_groups INTEGER NOT NULL,
                        updated_at REAL NOT NULL
                    );
                    """)
        except Exception as e:
            logging.error(f"Failed to initialize cross_scan_cache.db: {e}")

    def compute_db_set_fingerprint(self) -> str:
        sig_parts = []
        for p in self.db_paths:
            try:
                st = os.stat(p)
                sig_parts.append(f"{p}:{st.st_mtime_ns}:{st.st_size}")
            except OSError:
                sig_parts.append(f"{p}:0:0")
        combined_sig = "|".join(sig_parts)
        return hashlib.sha256(combined_sig.encode("utf-8")).hexdigest()

    def _get_cached_results(self, set_key: str, current_fingerprint: str) -> Optional[List[Dict[str, Any]]]:
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                row = conn.execute(
                    "SELECT fingerprint, results_json FROM cross_scan_cache WHERE set_key = ?",
                    (set_key,),
                ).fetchone()
                if row and row[0] == current_fingerprint:
                    logging.info(f"Cross-DB cache HIT for DB set ({len(self.db_paths)} DBs).")
                    return json.loads(row[1])
        except Exception as e:
            logging.warning(f"Error reading cross-DB cache: {e}")
        return None

    def _save_cached_results(self, set_key: str, fingerprint: str, results: List[Dict[str, Any]]):
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                results_json = json.dumps(results)
                conn.execute(
                    """
                    INSERT INTO cross_scan_cache (set_key, fingerprint, results_json, total_groups, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(set_key) DO UPDATE SET
                        fingerprint=excluded.fingerprint,
                        results_json=excluded.results_json,
                        total_groups=excluded.total_groups,
                        updated_at=excluded.updated_at
                    """,
                    (set_key, fingerprint, results_json, len(results), time.time()),
                )
        except Exception as e:
            logging.error(f"Failed to save cross-DB cache: {e}")

    def find_cross_duplicates(self) -> List[Dict[str, Any]]:
        """Matches identical files across attached SQLite databases with persistent fingerprint caching."""
        if len(self.db_paths) < 2:
            return []

        set_key = "|".join(self.db_paths)
        fingerprint = self.compute_db_set_fingerprint()

        cached_res = self._get_cached_results(set_key, fingerprint)
        if cached_res is not None:
            return cached_res

        logging.info(f"Cross-DB cache MISS for DB set ({len(self.db_paths)} DBs). Computing cross-DB matches...")
        results = self._compute_cross_duplicates()
        self._save_cached_results(set_key, fingerprint, results)
        return results

    def _compute_cross_duplicates(self) -> List[Dict[str, Any]]:

        # Check if Rust acceleration is available
        try:
            from core import dupeguru_rust

            if hasattr(dupeguru_rust, "cross_db_compare"):
                rust_results = dupeguru_rust.cross_db_compare(self.db_paths)
                if rust_results:
                    return self._format_rust_results(rust_results)
        except Exception as e:
            logging.warning(f"Rust cross-db matcher fallback: {e}")

        # Python/SQLite ATTACH DATABASE Fallback
        conn = sqlite3.connect(":memory:")
        attached_aliases = []
        try:
            for idx, db_path in enumerate(self.db_paths):
                alias = f"db_{idx}"
                conn.execute(f"ATTACH DATABASE ? AS {alias}", (db_path,))
                attached_aliases.append((alias, db_path))

            union_queries = []
            for alias, db_path in attached_aliases:
                union_queries.append(
                    f"SELECT path, size, mtime_ns, hex(COALESCE(digest, digest_partial)) as checksum, "
                    f"'{alias}' as db_alias, '{db_path}' as db_path FROM {alias}.files "
                    f"WHERE size > 0 AND (digest IS NOT NULL OR digest_partial IS NOT NULL)"
                )

            union_sql = " UNION ALL ".join(union_queries)
            group_sql = (
                f"WITH all_files AS ({union_sql}) "
                f"SELECT path, size, mtime_ns, checksum, db_alias, db_path "
                f"FROM all_files WHERE checksum IS NOT NULL AND checksum != ''"
            )

            cursor = conn.execute(group_sql)
            checksum_groups = defaultdict(list)

            for row in cursor.fetchall():
                path, size, mtime_ns, checksum, db_alias, db_path = row
                checksum_groups[(size, checksum)].append(
                    {
                        "path": path,
                        "size": size,
                        "mtime_ns": mtime_ns,
                        "checksum": checksum,
                        "db_alias": db_alias,
                        "db_path": db_path,
                        "db_name": os.path.basename(db_path).replace(".db", ""),
                    }
                )

            dupe_groups = []
            group_id = 0
            for (size, checksum), files in checksum_groups.items():
                if len(files) > 1:
                    db_sources = {f["db_path"] for f in files}
                    group_id += 1
                    dupe_groups.append(
                        {
                            "group_id": group_id,
                            "size": size,
                            "checksum": checksum,
                            "match_count": len(files),
                            "db_count": len(db_sources),
                            "files": files,
                        }
                    )
            return dupe_groups
        finally:
            conn.close()

    def _format_rust_results(self, rust_results) -> List[Dict[str, Any]]:
        dupe_groups = []
        for g_idx, group_files in enumerate(rust_results):
            files = []
            group_size = 0
            group_checksum = ""
            for item in group_files:
                path, size, mtime_ns, checksum, db_path = item
                group_size = size
                group_checksum = checksum
                files.append(
                    {
                        "path": path,
                        "size": size,
                        "mtime_ns": mtime_ns,
                        "checksum": checksum,
                        "db_path": db_path,
                        "db_name": os.path.basename(db_path).replace(".db", ""),
                    }
                )
            if files:
                dupe_groups.append(
                    {
                        "group_id": g_idx + 1,
                        "size": group_size,
                        "checksum": group_checksum,
                        "match_count": len(files),
                        "db_count": len({f["db_path"] for f in files}),
                        "files": files,
                    }
                )
        return dupe_groups
