# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
import os
import sqlite3
from collections import defaultdict
from typing import Any, Dict, List


class CrossDBMatcher:
    def __init__(self, db_paths: List[str]):
        self.db_paths = [os.path.abspath(p) for p in db_paths if os.path.exists(p)]

    def find_cross_duplicates(self) -> List[Dict[str, Any]]:
        """Matches identical files across attached SQLite databases without re-reading disk files."""
        if len(self.db_paths) < 2:
            return []

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
