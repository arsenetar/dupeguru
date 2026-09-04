# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

from collections import defaultdict
from typing import Callable, List, Optional

from core.domain.models import DuplicateGroupDTO, FileDTO
from core.pipeline.hasher import ContentHasher
from core.storage.db_engine import DBEngine


class DuplicateMatcher:
    """Finds duplicate file groups by matching file sizes and digest hashes."""

    def __init__(self, db_engine: DBEngine, batch_size: int = 500):
        self.db_engine = db_engine
        self.batch_size = batch_size
        self.hasher = ContentHasher(db_engine)

    def find_duplicates(
        self,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[DuplicateGroupDTO]:
        conn = self.db_engine.get_connection()
        cur = conn.cursor()

        query = """
        WITH candidate_sizes AS (
            SELECT size FROM files WHERE size > 0 GROUP BY size HAVING COUNT(*) > 1
        )
        SELECT f.path, f.size, f.mtime_ns, f.digest_partial, f.digest
        FROM files f
        JOIN candidate_sizes cs ON f.size = cs.size
        ORDER BY f.size DESC, f.path ASC
        """
        try:
            file_rows = cur.execute(query).fetchall()
        except Exception:
            file_rows = []

        if not file_rows:
            if progress_callback:
                progress_callback(0, 0, "No duplicate candidate files found.")
            return []

        dtos = [
            FileDTO(
                path=r["path"],
                size=r["size"],
                mtime_ns=r["mtime_ns"] if r["mtime_ns"] else 0,
                digest_partial=r["digest_partial"],
                digest=r["digest"],
            )
            for r in file_rows
        ]

        size_groups = defaultdict(list)
        for f in dtos:
            size_groups[f.size].append(f)

        duplicate_groups: List[DuplicateGroupDTO] = []
        group_counter = 0
        total_sizes = len(size_groups)

        for processed_count, (size, files_in_size) in enumerate(size_groups.items(), 1):
            if len(files_in_size) < 2:
                continue

            hash_groups = defaultdict(list)
            for f in files_in_size:
                d = f.digest_partial
                dig = f.digest
                key = (d, dig) if (d and dig) else (d if d else dig)
                if key:
                    hash_groups[key].append(f)

            for key, matched_files in hash_groups.items():
                if len(matched_files) > 1:
                    group_counter += 1
                    pivot = matched_files[0]
                    duplicates = matched_files[1:]
                    saved_bytes = pivot.size * len(duplicates)

                    dup_group = DuplicateGroupDTO(
                        group_id=group_counter,
                        pivot=pivot,
                        duplicates=duplicates,
                        saved_bytes=saved_bytes,
                    )
                    duplicate_groups.append(dup_group)

            if progress_callback and processed_count % 500 == 0:
                progress_callback(
                    processed_count,
                    total_sizes,
                    f"Comparing candidate duplicates ({processed_count:,}/{total_sizes:,} "
                    f"size groups, {len(duplicate_groups):,} groups found)...",
                )

        if progress_callback:
            progress_callback(
                total_sizes,
                total_sizes,
                f"Scan complete. Found {len(duplicate_groups):,} duplicate groups.",
            )

        if duplicate_groups:
            self.db_engine.save_duplicate_groups(duplicate_groups)

        return duplicate_groups

    def load_or_find_duplicates(
        self,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[DuplicateGroupDTO]:
        if self.db_engine.has_saved_duplicate_groups():
            groups = self.db_engine.load_duplicate_groups()
            if groups:
                return groups
        return self.find_duplicates(progress_callback=progress_callback)
