# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.domain.models import ScanTaskDTO, TaskStatus
from core.storage.db_engine import DBEngine


class TaskRepository:
    """Repository for loading, persisting, and querying ScanTaskDTO instances."""

    def __init__(self, scans_dir: str):
        self.scans_dir = scans_dir
        if not os.path.exists(scans_dir):
            os.makedirs(scans_dir, exist_ok=True)
        self._tasks: Dict[str, ScanTaskDTO] = {}
        self._mtime_cache: Dict[str, Tuple[float, ScanTaskDTO]] = {}

    def refresh(self) -> List[ScanTaskDTO]:
        """Scans the storage directory for .db files and updates task state."""
        candidate_dirs = [self.scans_dir]
        home = os.path.expanduser("~")
        fallback_dir = os.path.join(home, ".local/share", "de-dup", "scans")
        if "de-dup" in self.scans_dir and os.path.exists(fallback_dir) and fallback_dir not in candidate_dirs:
            candidate_dirs.append(fallback_dir)

        tasks: Dict[str, ScanTaskDTO] = {}
        for s_dir in candidate_dirs:
            if not os.path.exists(s_dir):
                continue
            for fname in sorted(os.listdir(s_dir)):
                if fname.endswith(".db"):
                    db_path = os.path.join(s_dir, fname)
                    task_id = fname.replace(".db", "")

                    try:
                        mtime = os.path.getmtime(db_path)
                    except Exception:
                        mtime = 0

                    if db_path in self._mtime_cache:
                        cached_mtime, cached_task = self._mtime_cache[db_path]
                        if cached_mtime == mtime or (
                            cached_task
                            and cached_task.status
                            in [
                                TaskStatus.DISCOVERING,
                                TaskStatus.HASHING,
                                TaskStatus.SCANNING,
                            ]
                        ):
                            tasks[task_id] = cached_task
                            continue

                    name = task_id.rsplit("_", 1)[0] if "_" in task_id else task_id
                    file_count, hashed_count = 0, 0
                    meta = {}
                    dirs = []

                    try:
                        db_engine = DBEngine(db_path)
                        file_count, hashed_count = db_engine.get_file_counts()
                        meta = db_engine.get_metadata()

                        if "directories" in meta and meta["directories"]:
                            try:
                                parsed = json.loads(meta["directories"])
                                if isinstance(parsed, list):
                                    dirs = parsed
                            except Exception:
                                pass

                        if not dirs:
                            try:
                                conn = db_engine.get_connection()
                                cur = conn.cursor()
                                rows = cur.execute("SELECT path FROM scanned_directories").fetchall()
                                dirs = [r[0] for r in rows]
                            except Exception:
                                dirs = []
                    except Exception as e:
                        logging.warning(f"Error reading database task metadata for {db_path}: {e}")

                    match_count = int(meta.get("match_count", 0)) if meta.get("match_count") else 0
                    dupe_count = int(meta.get("dupe_count", 0)) if meta.get("dupe_count") else 0

                    status = (
                        TaskStatus.COMPLETED
                        if match_count > 0 or meta.get("status") == "completed"
                        else (TaskStatus.NEEDS_HASHING if file_count > 0 and hashed_count == 0 else TaskStatus.IDLE)
                    )

                    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0

                    task = ScanTaskDTO(
                        task_id=task_id,
                        name=name,
                        db_path=db_path,
                        directories=dirs,
                        status=status,
                        file_count=file_count,
                        hashed_count=hashed_count,
                        match_count=match_count,
                        dupe_count=dupe_count,
                        db_size_bytes=db_size,
                    )
                    self._mtime_cache[db_path] = (mtime, task)
                    tasks[task_id] = task

        # Preserve any in-memory created tasks whose database files are not yet created on disk
        for tid, t in self._tasks.items():
            if tid not in tasks and not os.path.exists(t.db_path):
                tasks[tid] = t

        self._tasks = tasks
        return list(self._tasks.values())

    def get_task(self, task_id: str) -> Optional[ScanTaskDTO]:
        if task_id not in self._tasks:
            self.refresh()
        return self._tasks.get(task_id)

    def save_task_metadata(self, task: ScanTaskDTO) -> None:
        if not os.path.exists(task.db_path):
            return
        db_engine = DBEngine(task.db_path)
        db_engine.set_metadata("directories", json.dumps(task.directories))
        db_engine.set_metadata("match_count", str(task.match_count))
        db_engine.set_metadata("dupe_count", str(task.dupe_count))
        db_engine.set_metadata("status", task.status.value if isinstance(task.status, TaskStatus) else str(task.status))
        self._tasks[task.task_id] = task

    def delete_task(self, task_id: str) -> bool:
        if not task_id or "/" in task_id or "\\" in task_id or ".." in task_id or "\0" in task_id:
            return False
        task = self.get_task(task_id)
        if not task:
            return False

        if task_id in self._tasks:
            del self._tasks[task_id]

        try:
            resolved_db = Path(task.db_path).resolve(strict=True)
            if resolved_db.is_file():
                os.remove(str(resolved_db))
                for ext in ["-wal", "-shm"]:
                    extra = str(resolved_db) + ext
                    if os.path.exists(extra):
                        os.remove(extra)
                return True
        except (OSError, ValueError):
            return False
        return True

    def create_task(
        self,
        name: str,
        directories: List[str],
        db_filename: Optional[str] = None,
        overwrite: bool = False,
    ) -> ScanTaskDTO:
        """Create and register a new ScanTaskDTO instance."""
        existing = self.get_task(name)
        if existing and not overwrite:
            return existing

        safe_name = name.strip().replace(" ", "_").replace("/", "_").replace("\\", "_").replace("..", "_")
        task_id = existing.task_id if (existing and overwrite) else f"{safe_name}_{uuid.uuid4().hex[:8]}"

        scans_dir_path = Path(self.scans_dir).resolve()
        if not db_filename:
            db_path = existing.db_path if (existing and overwrite) else str(scans_dir_path / f"{task_id}.db")
        else:
            safe_filename = os.path.basename(db_filename.strip().replace("/", "_").replace("\\", "_"))
            if not safe_filename.endswith(".db"):
                safe_filename += ".db"
            db_path = str(scans_dir_path / safe_filename)

        if overwrite:
            try:
                resolved_db = Path(db_path).resolve()
                resolved_db.relative_to(scans_dir_path)
                if resolved_db.exists():
                    os.remove(str(resolved_db))
                    for ext in ["-wal", "-shm"]:
                        extra = str(resolved_db) + ext
                        if os.path.exists(extra):
                            os.remove(extra)
            except (OSError, ValueError):
                pass

        normalized_dirs = [os.path.normpath(d.strip().strip("'\"")) for d in directories if d and d.strip()]
        task_dto = ScanTaskDTO(
            task_id=task_id,
            name=name,
            db_path=db_path,
            directories=normalized_dirs,
            status=TaskStatus.IDLE,
        )
        self.save_task_metadata(task_dto)
        self._tasks[task_id] = task_dto
        return task_dto
