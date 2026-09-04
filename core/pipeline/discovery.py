# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import logging
import os
from typing import Callable, List, Optional

from core.domain.models import FileDTO
from core.storage.db_engine import DBEngine


class FileDiscovery:
    """Discovers files across target directories or reads cached records directly from SQLite."""

    def __init__(self, db_engine: DBEngine):
        self.db_engine = db_engine

    def collect_files(
        self,
        directories: List[str],
        enable_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[FileDTO]:
        self.db_engine.init_schema()

        if enable_cache:
            conn = self.db_engine.get_connection()
            cur = conn.cursor()
            try:
                row = cur.execute("SELECT COUNT(*) FROM files").fetchone()
                if row and row[0] > 0:
                    rows = cur.execute("SELECT path, size, mtime_ns, digest_partial, digest FROM files").fetchall()
                    file_dtos = [
                        FileDTO(
                            path=r[0],
                            size=r[1],
                            mtime_ns=r[2] if r[2] else 0,
                            digest_partial=r[3],
                            digest=r[4],
                        )
                        for r in rows
                    ]
                    if progress_callback:
                        progress_callback(
                            len(file_dtos), f"Loaded {len(file_dtos):,} cached file records from database."
                        )
                    return file_dtos
            except Exception as e:
                logging.warning(f"Cache check exception in FileDiscovery: {e}")

        # Crawl fresh directories
        file_dtos: List[FileDTO] = []
        batch_buf = []
        count = 0

        for target_dir in directories:
            if not os.path.exists(target_dir):
                continue

            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for fname in files:
                    if fname.startswith("."):
                        continue
                    full_path = os.path.join(root, fname)
                    try:
                        stat = os.stat(full_path)
                        f_dto = FileDTO(
                            path=full_path,
                            size=stat.st_size,
                            mtime_ns=stat.st_mtime_ns,
                        )
                        file_dtos.append(f_dto)
                        batch_buf.append((f_dto.path, f_dto.size, f_dto.mtime_ns))
                        count += 1

                        if len(batch_buf) >= 1000:
                            self._flush_batch(batch_buf)
                            batch_buf.clear()

                        if progress_callback and count % 2000 == 0:
                            progress_callback(count, f"Discovered {count:,} files across target directories...")
                    except OSError:
                        pass

        if batch_buf:
            self._flush_batch(batch_buf)
            batch_buf.clear()

        # Mark scanned directories
        with self.db_engine.transaction() as conn:
            for d in directories:
                conn.execute(
                    "INSERT INTO scanned_directories (path) VALUES (?) ON CONFLICT(path) DO NOTHING",
                    (d,),
                )

        if progress_callback:
            progress_callback(len(file_dtos), f"Discovered {len(file_dtos):,} total files.")
        return file_dtos

    def rescan_directories(
        self,
        directories: List[str],
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[FileDTO]:
        """Rescans target directories, purging deleted files and marking modified files for re-hashing."""
        self.db_engine.init_schema()
        conn = self.db_engine.get_connection()
        cur = conn.cursor()

        # Fetch existing cached files
        existing_rows = cur.execute("SELECT path, size, mtime_ns FROM files").fetchall()
        cached_map = {r[0]: (r[1], r[2] if r[2] else 0) for r in existing_rows}

        current_disk_paths = set()
        to_insert: List[tuple] = []
        to_update_modified: List[tuple] = []
        count = 0

        for target_dir in directories:
            if not os.path.exists(target_dir):
                continue

            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for fname in files:
                    if fname.startswith("."):
                        continue
                    full_path = os.path.join(root, fname)
                    current_disk_paths.add(full_path)
                    try:
                        stat = os.stat(full_path)
                        curr_size = stat.st_size
                        curr_mtime = stat.st_mtime_ns
                        count += 1

                        if full_path not in cached_map:
                            to_insert.append((full_path, curr_size, curr_mtime))
                        else:
                            cached_size, cached_mtime = cached_map[full_path]
                            if curr_size != cached_size or (curr_mtime > 0 and curr_mtime != cached_mtime):
                                to_update_modified.append((curr_size, curr_mtime, full_path))

                        if progress_callback and count % 2000 == 0:
                            progress_callback(count, f"Re-scanning disk files ({count:,} checked)...")
                    except OSError:
                        pass

        # Detect deleted files under scanned target directories
        deleted_paths = [
            p
            for p in cached_map.keys()
            if any(p.startswith(d + os.sep) or p == d for d in directories) and p not in current_disk_paths
        ]

        with self.db_engine.transaction() as conn_tx:
            if deleted_paths:
                for i in range(0, len(deleted_paths), 900):
                    chunk = deleted_paths[i : i + 900]
                    placeholders = ",".join("?" for _ in chunk)
                    conn_tx.execute(f"DELETE FROM files WHERE path IN ({placeholders})", chunk)

            if to_insert:
                conn_tx.executemany(
                    "INSERT INTO files (path, size, mtime_ns, entry_dt) "
                    "VALUES (?, ?, ?, datetime('now')) "
                    "ON CONFLICT(path) DO UPDATE SET "
                    "size=excluded.size, mtime_ns=excluded.mtime_ns, digest_partial=NULL, digest=NULL",
                    to_insert,
                )

            if to_update_modified:
                conn_tx.executemany(
                    "UPDATE files SET size = ?, mtime_ns = ?, digest_partial = NULL, digest = NULL WHERE path = ?",
                    to_update_modified,
                )

        if progress_callback:
            msg = (
                f"Rescan complete. New: {len(to_insert):,}, Modified: {len(to_update_modified):,}, "
                f"Deleted: {len(deleted_paths):,}."
            )
            progress_callback(count, msg)

        # Return updated file list from SQLite
        return self.collect_files(directories, enable_cache=True)

    def _flush_batch(self, batch: List[tuple]) -> None:
        with self.db_engine.transaction() as conn:
            conn.executemany(
                "INSERT INTO files (path, size, mtime_ns, entry_dt) "
                "VALUES (?, ?, ?, datetime('now')) "
                "ON CONFLICT(path) DO UPDATE SET "
                "size = CASE WHEN excluded.size > 0 THEN excluded.size ELSE files.size END, "
                "mtime_ns = CASE WHEN excluded.mtime_ns > 0 THEN excluded.mtime_ns ELSE files.mtime_ns END, "
                "entry_dt = datetime('now')",
                batch,
            )
