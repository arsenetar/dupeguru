# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional, Tuple

from core.domain.models import DuplicateGroupDTO
from core.storage.db_engine import DBEngine


def default_file_remover(path: str) -> bool:
    """Safely remove a file from disk."""
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


class FileDeletionService:
    """Service handling multi-threaded physical file deletion, progress reporting,
    and database synchronization across single or multiple task databases.
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        file_remover: Callable[[str], bool] = default_file_remover,
    ):
        self._max_workers = max_workers
        self._file_remover = file_remover

    def delete_files(
        self,
        target_paths: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        db_engines: Optional[List[DBEngine]] = None,
        active_duplicate_groups: Optional[List[DuplicateGroupDTO]] = None,
    ) -> Tuple[int, List[str], List[DuplicateGroupDTO]]:
        """Deletes files concurrently, updates progress, purges from DBEngines,
        and filters in-memory DuplicateGroupDTOs.

        Returns:
            (deleted_physical_count, successful_paths, updated_duplicate_groups)
        """
        if not target_paths:
            return (0, [], active_duplicate_groups or [])

        total_len = len(target_paths)
        workers = self._max_workers or min(64, max(4, total_len // 100))
        step = max(1, min(100, total_len // 50))

        if progress_callback:
            progress_callback(0, total_len, f"Deleting 0 / {total_len:,} duplicate files...")

        def _worker(p: str) -> Tuple[bool, str, bool]:
            try:
                existed = os.path.exists(p)
                if existed:
                    removed = self._file_remover(p)
                    return (True, p, removed)
                return (True, p, False)
            except OSError as e:
                logging.error(f"Failed to delete file {p}: {e}")
                return (False, p, False)
            except Exception as e:
                logging.error(f"Unexpected error deleting file {p}: {e}")
                return (False, p, False)

        successful_paths: List[str] = []
        deleted_count = 0

        with ThreadPoolExecutor(max_workers=workers) as executor:
            for idx, (ok, p, physical) in enumerate(executor.map(_worker, target_paths), start=1):
                if ok:
                    successful_paths.append(p)
                    if physical:
                        deleted_count += 1
                if progress_callback and (idx % step == 0 or idx == total_len):
                    pct = int((idx / total_len) * 100)
                    progress_callback(
                        idx,
                        total_len,
                        f"Deleting {idx:,} / {total_len:,} duplicate files ({pct}%)...",
                    )

        # Purge from DBEngines if provided
        if db_engines and successful_paths:
            for engine in db_engines:
                try:
                    engine.delete_files_by_paths(successful_paths)
                except Exception as e:
                    logging.error(f"Failed to purge deleted files from DB '{engine.db_path}': {e}")

        # Filter in-memory duplicate groups if provided
        filtered_groups: List[DuplicateGroupDTO] = []
        if active_duplicate_groups:
            succ_set = set(successful_paths)
            for g in active_duplicate_groups:
                rem_dupes = [d for d in g.duplicates if d.path not in succ_set]
                if rem_dupes:
                    new_saved = sum(d.size for d in rem_dupes)
                    filtered_groups.append(
                        DuplicateGroupDTO(
                            group_id=g.group_id,
                            pivot=g.pivot,
                            duplicates=rem_dupes,
                            saved_bytes=new_saved,
                        )
                    )

        return (deleted_count, successful_paths, filtered_groups)
