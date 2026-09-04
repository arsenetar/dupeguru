# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

"""Compatibility shim for legacy ScanTaskRegistry and ScanTask.

Deprecated:
    Use `core.storage.task_repo.TaskRepository` and `core.domain.models.ScanTaskDTO` instead.
"""

import warnings
from typing import Any, Dict, List, Optional

from core.domain.models import ScanTaskDTO, TaskStatus
from core.storage.task_repo import TaskRepository


class ScanTaskStatus:
    IDLE = TaskStatus.IDLE.value
    RUNNING = TaskStatus.SCANNING.value
    COMPLETED = TaskStatus.COMPLETED.value
    CANCELLED = TaskStatus.CANCELLED.value
    FAILED = TaskStatus.FAILED.value


class ScanTask:
    """Compatibility adapter for legacy ScanTask instances."""

    def __init__(self, dto: ScanTaskDTO):
        self._dto = dto

    @property
    def task_id(self) -> str:
        return self._dto.task_id

    @property
    def name(self) -> str:
        return self._dto.name

    @property
    def db_path(self) -> str:
        return self._dto.db_path

    @property
    def directories(self) -> List[str]:
        return self._dto.directories

    @directories.setter
    def directories(self, value: List[str]) -> None:
        self._dto.directories = value

    @property
    def status(self) -> str:
        return self._dto.status.value if isinstance(self._dto.status, TaskStatus) else str(self._dto.status)

    @status.setter
    def status(self, value: Any) -> None:
        if isinstance(value, TaskStatus):
            self._dto.status = value
        else:
            try:
                self._dto.status = TaskStatus(str(value))
            except ValueError:
                self._dto.status = TaskStatus.IDLE

    @property
    def progress_percentage(self) -> int:
        return self._dto.progress_percentage

    @property
    def progress_message(self) -> str:
        return self._dto.progress_message

    @property
    def error_message(self) -> Optional[str]:
        return self._dto.error_message

    @property
    def file_count(self) -> int:
        return self._dto.file_count

    @property
    def match_count(self) -> int:
        return self._dto.match_count

    @property
    def dupe_count(self) -> int:
        return self._dto.dupe_count

    def to_dict(self) -> Dict[str, Any]:
        return self._dto.to_dict()


class ScanTaskRegistry:
    """Compatibility adapter forwarding to TaskRepository."""

    def __init__(self, scans_dir: str):
        warnings.warn(
            "ScanTaskRegistry is deprecated; use core.storage.task_repo.TaskRepository instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._repo = TaskRepository(scans_dir)

    def create_task(
        self,
        name: str,
        directories: List[str],
        db_filename: Optional[str] = None,
        overwrite: bool = False,
    ) -> ScanTask:
        dto = self._repo.create_task(name=name, directories=directories, db_filename=db_filename, overwrite=overwrite)
        return ScanTask(dto)

    def get_task(self, task_id: str) -> Optional[ScanTask]:
        dto = self._repo.get_task(task_id)
        return ScanTask(dto) if dto else None

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self._repo.refresh()]

    def delete_task(self, task_id: str, delete_db_file: bool = True) -> bool:
        return self._repo.delete_task(task_id)
