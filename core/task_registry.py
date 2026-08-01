# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import threading
import time
import uuid
from typing import Any, Dict, List, Optional


class ScanTaskStatus:
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


def minimize_directories(dirs: List[str]) -> List[str]:
    if not dirs:
        return []
    sorted_dirs = sorted(dirs, key=lambda p: (len(p), p))
    minimized = []
    for d in sorted_dirs:
        if not any(d == root or d.startswith(root + os.sep) for root in minimized):
            minimized.append(d)
    return minimized


class ScanTask:
    def __init__(self, task_id: str, name: str, db_path: str, directories: List[str]):
        self.task_id = task_id
        self.name = name
        self.db_path = db_path
        self.directories = directories
        self.status = ScanTaskStatus.IDLE
        self.progress_percentage = 0
        self.progress_message = ""
        self.error_message = None
        self.created_at = time.time()
        self.completed_at = None
        self.file_count = 0
        self.match_count = 0
        self.dupe_count = 0
        self.app_instance = None
        self._thread = None

    def save_metadata(self) -> None:
        try:
            from core import fs

            if fs.filesdb and fs.filesdb.engine and getattr(fs.filesdb.engine, "db_path", None) == self.db_path:
                status_str = self.status.value if isinstance(self.status, ScanTaskStatus) else str(self.status)
                fs.filesdb.set_metadata("match_count", self.match_count)
                fs.filesdb.set_metadata("dupe_count", self.dupe_count)
                fs.filesdb.set_metadata("status", status_str)
                return
        except Exception:
            pass

        if os.path.exists(self.db_path):
            try:
                import sqlite3

                conn = sqlite3.connect(self.db_path, timeout=10.0)
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS scan_metadata (key TEXT PRIMARY KEY, value TEXT)")
                cur.execute("INSERT OR REPLACE INTO scan_metadata VALUES ('match_count', ?)", (str(self.match_count),))
                cur.execute("INSERT OR REPLACE INTO scan_metadata VALUES ('dupe_count', ?)", (str(self.dupe_count),))
                status_str = self.status.value if isinstance(self.status, ScanTaskStatus) else str(self.status)
                cur.execute("INSERT OR REPLACE INTO scan_metadata VALUES ('status', ?)", (status_str,))
                conn.commit()
                conn.close()
            except Exception:
                pass

    def to_dict(self) -> Dict[str, Any]:
        db_size = 0
        hashed_count = 0
        total_files = self.file_count
        if os.path.exists(self.db_path):
            try:
                db_size = os.path.getsize(self.db_path)
                import sqlite3

                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                row_files = cur.execute("SELECT COUNT(*) FROM files").fetchone()
                if row_files and row_files[0] > 0:
                    total_files = row_files[0]
                    self.file_count = total_files
                row_hashed = cur.execute(
                    "SELECT COUNT(*) FROM files WHERE (digest IS NOT NULL AND length(digest) > 0) "
                    "OR (digest_partial IS NOT NULL AND length(digest_partial) > 0)"
                ).fetchone()
                if row_hashed:
                    hashed_count = row_hashed[0]
                conn.close()
            except Exception:
                pass

        status_str = self.status.value if isinstance(self.status, ScanTaskStatus) else str(self.status)
        if self.match_count > 0 or getattr(self, "is_loaded", False) or status_str == "completed":
            if total_files > 0 and hashed_count < total_files:
                hashed_count = total_files
            status_str = "completed"
        elif total_files > 0 and hashed_count < total_files:
            status_str = "needs_hashing"

        return {
            "task_id": self.task_id,
            "name": self.name,
            "db_path": self.db_path,
            "directories": self.directories,
            "status": status_str,
            "progress_percentage": self.progress_percentage,
            "progress_message": self.progress_message,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "file_count": total_files,
            "hashed_count": hashed_count,
            "match_count": self.match_count,
            "dupe_count": self.dupe_count,
            "db_size_bytes": db_size,
        }


class ScanTaskRegistry:
    def __init__(self, scans_dir: str):
        self.scans_dir = os.path.abspath(scans_dir)
        os.makedirs(self.scans_dir, exist_ok=True)
        self.tasks: Dict[str, ScanTask] = {}
        self._lock = threading.RLock()
        self._scan_storage_refresh()

    def get_task_by_name(self, name: str) -> Optional[ScanTask]:
        self._scan_storage_refresh()
        safe_name = name.strip().replace(" ", "_").replace("/", "_").lower()
        with self._lock:
            for task in self.tasks.values():
                if task.name.strip().replace(" ", "_").replace("/", "_").lower() == safe_name:
                    return task
            return None

    def create_task(
        self,
        name: str,
        directories: List[str],
        db_filename: Optional[str] = None,
        overwrite: bool = False,
    ) -> ScanTask:
        with self._lock:
            existing = self.get_task_by_name(name)
            if existing and not overwrite:
                return existing

            task_id = existing.task_id if (existing and overwrite) else str(uuid.uuid4())[:8]
            safe_name = name.replace(" ", "_").replace("/", "_")
            if not db_filename:
                db_filename = (
                    existing.db_path
                    if (existing and overwrite)
                    else os.path.join(self.scans_dir, f"{safe_name}_{task_id}.db")
                )
            else:
                if not db_filename.endswith(".db"):
                    db_filename += ".db"
                db_filename = os.path.join(self.scans_dir, db_filename)

            db_path = db_filename
            if overwrite and os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    if os.path.exists(db_path + "-wal"):
                        os.remove(db_path + "-wal")
                    if os.path.exists(db_path + "-shm"):
                        os.remove(db_path + "-shm")
                except OSError:
                    pass

            task = ScanTask(task_id=task_id, name=name, db_path=db_path, directories=directories)
            self.tasks[task_id] = task
            return task

    def get_task(self, task_id: str) -> Optional[ScanTask]:
        with self._lock:
            return self.tasks.get(task_id)

    def list_tasks(self) -> List[Dict[str, Any]]:
        self._scan_storage_refresh()
        with self._lock:
            return [task.to_dict() for task in self.tasks.values()]

    def delete_task(self, task_id: str, delete_db_file: bool = True) -> bool:
        with self._lock:
            task = self.tasks.pop(task_id, None)
            if not task:
                return False
            if task.status == ScanTaskStatus.RUNNING and task.app_instance:
                try:
                    task.app_instance.cancel_job()
                except Exception:
                    pass
            if delete_db_file and os.path.exists(task.db_path):
                try:
                    os.remove(task.db_path)
                    shutil_wal = task.db_path + "-wal"
                    shutil_shm = task.db_path + "-shm"
                    if os.path.exists(shutil_wal):
                        os.remove(shutil_wal)
                    if os.path.exists(shutil_shm):
                        os.remove(shutil_shm)
                except OSError:
                    pass
            return True

    def _scan_storage_refresh(self):
        """Scans storage directories for existing .db files and registers them."""
        with self._lock:
            candidate_dirs = [self.scans_dir]
            home = os.path.expanduser("~")
            fallback_dir = os.path.join(home, ".local/share", "dupeGuru", "scans")
            if os.path.exists(fallback_dir) and fallback_dir not in candidate_dirs:
                candidate_dirs.append(fallback_dir)

            for scans_directory in candidate_dirs:
                if not os.path.exists(scans_directory):
                    continue
                try:
                    for fname in os.listdir(scans_directory):
                        if fname.endswith(".db"):
                            db_path = os.path.join(scans_directory, fname)
                            existing = any(t.db_path == db_path for t in self.tasks.values())
                            if not existing:
                                task_id = fname.replace(".db", "")
                                name = task_id.rsplit("_", 1)[0] if "_" in task_id else task_id
                                task = ScanTask(task_id=task_id, name=name, db_path=db_path, directories=[])
                                task.status = ScanTaskStatus.COMPLETED

                                try:
                                    import sqlite3

                                    conn = sqlite3.connect(db_path)
                                    cur = conn.cursor()
                                    cur.execute("SELECT COUNT(*) FROM files")
                                    task.file_count = cur.fetchone()[0]

                                    cur.execute("SELECT path FROM scanned_directories")
                                    saved_dirs = [r[0] for r in cur.fetchall()]
                                    if saved_dirs:
                                        task.directories = minimize_directories(saved_dirs)

                                    try:
                                        cur.execute("SELECT key, value FROM scan_metadata")
                                        meta = dict(cur.fetchall())
                                        if "match_count" in meta:
                                            task.match_count = int(meta["match_count"])
                                        if "dupe_count" in meta:
                                            task.dupe_count = int(meta["dupe_count"])
                                        if "status" in meta and meta["status"] == "completed":
                                            task.status = ScanTaskStatus.COMPLETED
                                            task.is_loaded = True
                                    except Exception:
                                        pass

                                    conn.close()
                                except Exception:
                                    pass

                                self.tasks[task_id] = task
                except Exception as e:
                    import logging

                    logging.error(f"Error refreshing scan storage in {scans_directory}: {e}")
