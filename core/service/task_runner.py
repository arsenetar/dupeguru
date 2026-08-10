# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

import logging
import os
import threading
import time
from typing import Dict, List, Optional

from core.domain.models import DuplicateGroupDTO, ScanTaskDTO, TaskStatus
from core.pipeline.discovery import FileDiscovery
from core.pipeline.hasher import ContentHasher
from core.pipeline.matcher import DuplicateMatcher
from core.storage.db_engine import DBEngine
from core.storage.task_repo import TaskRepository


class TaskExecution:
    """Encapsulates an isolated execution context for a single ScanTaskDTO."""

    def __init__(self, task_dto: ScanTaskDTO, task_repo: Optional[TaskRepository] = None):
        self.task = task_dto
        self.task_repo = task_repo
        self.db_engine = DBEngine(task_dto.db_path)
        self.thread: Optional[threading.Thread] = None
        self.stop_requested = False
        self.results_groups: List[DuplicateGroupDTO] = []
        self._file_count_cache = 0
        self._hashed_count_cache = 0
        self._lock = threading.Lock()

    def start(self, rescan: bool = False) -> None:
        with self._lock:
            if self.thread and self.thread.is_alive():
                return
            self.stop_requested = False
            self.thread = threading.Thread(target=self._run, args=(rescan,), daemon=True)
            self.thread.start()

    def cancel(self) -> None:
        self.stop_requested = True
        with self._lock:
            self.task.status = TaskStatus.CANCELLED
            self.task.progress_message = "Scan task cancelled by user."

    def get_dto(self) -> ScanTaskDTO:
        with self._lock:
            if self.thread and self.thread.is_alive():
                self.task.file_count = self._file_count_cache or self.task.file_count
                self.task.hashed_count = self._hashed_count_cache or self.task.hashed_count
            else:
                file_count, hashed_count = self.db_engine.get_file_counts()
                self._file_count_cache = file_count
                self._hashed_count_cache = hashed_count
                self.task.file_count = file_count
                self.task.hashed_count = hashed_count
            if os.path.exists(self.task.db_path):
                self.task.db_size_bytes = os.path.getsize(self.task.db_path)
            return self.task

    def _run(self, rescan: bool = False) -> None:
        try:
            with self._lock:
                self.task.status = TaskStatus.DISCOVERING
                self.task.progress_percentage = 0
                self.task.progress_message = (
                    f"Re-scanning target directories for '{self.task.name}'..."
                    if rescan
                    else f"Discovering files for '{self.task.name}'..."
                )

            discovery = FileDiscovery(self.db_engine)
            if rescan:
                file_dtos = discovery.rescan_directories(
                    self.task.directories,
                    progress_callback=self._on_discovery_progress,
                )
            else:
                file_dtos = discovery.collect_files(
                    self.task.directories,
                    enable_cache=True,
                    progress_callback=self._on_discovery_progress,
                )

            if self.stop_requested:
                return

            with self._lock:
                self.task.status = TaskStatus.HASHING
                self.task.file_count = len(file_dtos)
                self._file_count_cache = len(file_dtos)

            hasher = ContentHasher(self.db_engine)
            candidate_dtos = self.db_engine.get_candidate_duplicate_files()
            unhashed_candidates = [f for f in candidate_dtos if not f.digest_partial and not f.digest]
            if unhashed_candidates:
                hasher.hash_candidate_files(
                    unhashed_candidates,
                    progress_callback=self._on_hashing_progress,
                    stop_checker=lambda: self.stop_requested,
                )

            if self.stop_requested:
                return

            with self._lock:
                self.task.status = TaskStatus.SCANNING
                self.task.progress_message = f"Comparing duplicates for '{self.task.name}'..."

            matcher = DuplicateMatcher(self.db_engine)
            groups = matcher.find_duplicates(progress_callback=self._on_matching_progress)
            self.db_engine.save_duplicate_groups(groups)

            with self._lock:
                self.results_groups = groups
                self.task.match_count = len(groups)
                self.task.dupe_count = sum(len(g.duplicates) for g in groups)
                self.task.status = TaskStatus.COMPLETED
                self.task.progress_percentage = 100
                self.task.progress_message = f"Scan completed. Found {len(groups):,} duplicate groups."
                self.task.completed_at = time.time()

                if self.task_repo:
                    self.task_repo.save_task_metadata(self.task)
        except Exception as e:
            logging.error(f"TaskExecution failure for {self.task.task_id}: {e}", exc_info=True)
            with self._lock:
                self.task.status = TaskStatus.FAILED
                self.task.error_message = str(e)
                self.task.progress_message = f"Task failed: {e}"
        finally:
            self.db_engine.close()

    def _on_discovery_progress(self, count: int, msg: str) -> None:
        with self._lock:
            self.task.progress_message = msg

    def _on_hashing_progress(self, current: int, total: int, msg: str) -> None:
        with self._lock:
            self._hashed_count_cache = current
            if total > 0:
                self.task.progress_percentage = int((current / total) * 50)
            self.task.progress_message = msg

    def _on_matching_progress(self, current: int, total: int, msg: str) -> None:
        with self._lock:
            if total > 0:
                self.task.progress_percentage = 50 + int((current / total) * 50)
            else:
                self.task.progress_percentage = 100
            self.task.progress_message = msg


class TaskRunner:
    """Thread-safe task registry managing non-singleton TaskExecution instances."""

    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo
        self._executions: Dict[str, TaskExecution] = {}
        self._lock = threading.Lock()

    def get_or_create_execution(self, task_id: str) -> Optional[TaskExecution]:
        with self._lock:
            if task_id in self._executions:
                return self._executions[task_id]

            task_dto = self.task_repo.get_task(task_id)
            if not task_dto:
                return None

            execution = TaskExecution(task_dto, task_repo=self.task_repo)
            self._executions[task_id] = execution
            return execution

    def start_task(self, task_id: str) -> Optional[TaskExecution]:
        execution = self.get_or_create_execution(task_id)
        if execution:
            execution.start(rescan=False)
        return execution

    def rescan_task(self, task_id: str) -> Optional[TaskExecution]:
        execution = self.get_or_create_execution(task_id)
        if execution:
            execution.start(rescan=True)
        return execution

    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            execution = self._executions.get(task_id)
            if execution:
                execution.cancel()
                return True
        return False

    def list_active_executions(self) -> List[ScanTaskDTO]:
        with self._lock:
            return [exec_obj.get_dto() for exec_obj in self._executions.values()]
