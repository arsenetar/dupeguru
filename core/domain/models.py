# Copyright 2026 Tin Le (https://github.com/TinLe/de-dup)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file.

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    IDLE = "idle"
    DISCOVERING = "discovering"
    HASHING = "hashing"
    SCANNING = "scanning"
    NEEDS_HASHING = "needs_hashing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True)
class FileDTO:
    path: str
    size: int
    mtime_ns: int = 0
    digest_partial: Optional[bytes] = None
    digest: Optional[bytes] = None
    is_ref: bool = False

    @property
    def name(self) -> str:
        return self.path.split("/")[-1] if "/" in self.path else self.path


@dataclass(frozen=True)
class DuplicateGroupDTO:
    group_id: int
    pivot: FileDTO
    duplicates: List[FileDTO] = field(default_factory=list)
    saved_bytes: int = 0

    @property
    def total_files(self) -> int:
        return 1 + len(self.duplicates)

    def serialize_to_dict(self, group_index: int = 0) -> Dict[str, Any]:
        from hscommon.util import format_size
        import os

        files_data = [
            {
                "path": self.pivot.path,
                "name": self.pivot.name,
                "folder": os.path.dirname(self.pivot.path),
                "size": format_size(self.pivot.size, 0, 1, False),
                "mtime": "",
                "percentage": "100%",
                "is_ref": True,
                "marked": False,
                "markable": False,
            }
        ]
        for d in self.duplicates:
            files_data.append(
                {
                    "path": d.path,
                    "name": d.name,
                    "folder": os.path.dirname(d.path),
                    "size": format_size(d.size, 0, 1, False),
                    "mtime": "",
                    "percentage": "100%",
                    "is_ref": False,
                    "marked": True,
                    "markable": True,
                }
            )

        return {
            "id": group_index,
            "percentage": 100,
            "files": files_data,
        }


@dataclass
class ScanTaskDTO:
    task_id: str
    name: str
    db_path: str
    directories: List[str]
    status: TaskStatus = TaskStatus.IDLE
    file_count: int = 0
    hashed_count: int = 0
    match_count: int = 0
    dupe_count: int = 0
    progress_percentage: int = 0
    progress_message: str = ""
    error_message: Optional[str] = None
    db_size_bytes: int = 0
    created_at: float = 0.0
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "db_path": self.db_path,
            "directories": self.directories,
            "status": self.status.value if isinstance(self.status, TaskStatus) else str(self.status),
            "progress_percentage": self.progress_percentage,
            "progress_message": self.progress_message,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "file_count": self.file_count,
            "hashed_count": self.hashed_count,
            "match_count": self.match_count,
            "dupe_count": self.dupe_count,
            "db_size_bytes": self.db_size_bytes,
        }
