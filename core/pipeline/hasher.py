# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import hashlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional, Tuple

from core.domain.models import FileDTO
from core.storage.db_engine import DBEngine

try:
    import xxhash

    HASHER_FUNC = xxhash.xxh128
except ImportError:
    HASHER_FUNC = hashlib.md5

PARTIAL_SIZE = 8192
PARTIAL_OFFSET = 16384


def calc_partial_hash(path: str) -> Optional[bytes]:
    try:
        size = os.path.getsize(path)
        if size <= PARTIAL_SIZE:
            return calc_full_hash(path)
        with open(path, "rb") as f:
            h = HASHER_FUNC()
            h.update(f.read(PARTIAL_SIZE))
            if size > (PARTIAL_OFFSET + PARTIAL_SIZE):
                f.seek(PARTIAL_OFFSET)
                h.update(f.read(PARTIAL_SIZE))
            return h.digest()
    except Exception:
        return None


def calc_full_hash(path: str) -> Optional[bytes]:
    try:
        with open(path, "rb") as f:
            h = HASHER_FUNC()
            while chunk := f.read(65536):
                h.update(chunk)
            return h.digest()
    except Exception:
        return None


class ContentHasher:
    """Multi-threaded content hasher that computes partial and full file digests."""

    def __init__(self, db_engine: DBEngine, max_workers: int = 8):
        self.db_engine = db_engine
        self.max_workers = max_workers

    def hash_candidate_files(
        self,
        candidate_dtos: List[FileDTO],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        stop_checker: Optional[Callable[[], bool]] = None,
    ) -> List[FileDTO]:
        if not candidate_dtos:
            return []

        total = len(candidate_dtos)
        processed = 0
        updated_dtos: List[FileDTO] = []
        batch_partial: List[Tuple[str, bytes]] = []
        batch_full: List[Tuple[str, bytes]] = []

        def _hash_worker(dto: FileDTO) -> Tuple[FileDTO, Optional[bytes], Optional[bytes]]:
            p_hash = dto.digest_partial if dto.digest_partial else calc_partial_hash(dto.path)
            f_hash = dto.digest if dto.digest else (calc_full_hash(dto.path) if p_hash else None)
            return (dto, p_hash, f_hash)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(_hash_worker, dto) for dto in candidate_dtos]
            for future in as_completed(futures):
                if stop_checker and stop_checker():
                    logging.info("ContentHasher cancelled by stop_checker.")
                    for f in futures:
                        f.cancel()
                    break
                processed += 1
                try:
                    orig_dto, p_hash, f_hash = future.result()
                    new_dto = FileDTO(
                        path=orig_dto.path,
                        size=orig_dto.size,
                        mtime_ns=orig_dto.mtime_ns,
                        digest_partial=p_hash,
                        digest=f_hash,
                        is_ref=orig_dto.is_ref,
                    )
                    updated_dtos.append(new_dto)

                    if p_hash and not orig_dto.digest_partial:
                        batch_partial.append((orig_dto.path, p_hash))
                    if f_hash and not orig_dto.digest:
                        batch_full.append((orig_dto.path, f_hash))

                    if len(batch_partial) >= 2000 or len(batch_full) >= 2000:
                        self._flush_hashes(batch_partial, batch_full)
                        batch_partial.clear()
                        batch_full.clear()

                    if progress_callback and (processed % 1000 == 0 or processed == total):
                        progress_callback(
                            processed,
                            total,
                            f"Hashing candidate files ({processed:,}/{total:,})...",
                        )
                except Exception as e:
                    logging.warning(f"Error hashing file: {e}")

        if batch_partial or batch_full:
            self._flush_hashes(batch_partial, batch_full)
            batch_partial.clear()
            batch_full.clear()

        if progress_callback:
            progress_callback(total, total, f"Completed hashing {total:,} candidate files.")

        return updated_dtos

    def _flush_hashes(
        self,
        batch_partial: List[Tuple[str, bytes]],
        batch_full: List[Tuple[str, bytes]],
    ) -> None:
        import time

        for attempt in range(5):
            try:
                with self.db_engine.transaction() as conn:
                    if batch_partial:
                        conn.executemany(
                            "UPDATE files SET digest_partial = ? WHERE path = ?",
                            [(p[1], p[0]) for p in batch_partial],
                        )
                    if batch_full:
                        conn.executemany(
                            "UPDATE files SET digest = ? WHERE path = ?",
                            [(f[1], f[0]) for f in batch_full],
                        )
                break
            except Exception as e:
                if attempt == 4:
                    logging.error(f"Failed flushing hashes to DB after 5 attempts: {e}")
                else:
                    time.sleep(0.1 * (attempt + 1))
