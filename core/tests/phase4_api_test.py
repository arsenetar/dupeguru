# Unit tests for Phase 4 REST API Router and TaskRunner Web Integration

import os
import tempfile
import unittest
from core.domain.models import ScanTaskDTO, TaskStatus
from core.service.task_runner import TaskRunner
from core.storage.db_engine import DBEngine
from core.storage.task_repo import TaskRepository


class TestPhase4WebAPI(unittest.TestCase):
    def test_api_scans_list_schema(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = TaskRepository(temp_dir)
            db1 = os.path.join(temp_dir, "api_task1.db")
            engine = DBEngine(db1)
            engine.init_schema()

            task = ScanTaskDTO(
                task_id="api_task1",
                name="api_task1",
                db_path=db1,
                directories=["/tmp"],
                status=TaskStatus.COMPLETED,
            )
            repo.save_task_metadata(task)

            tasks = repo.refresh()
            self.assertEqual(len(tasks), 1)

            task_dict = tasks[0].to_dict()
            self.assertIn("task_id", task_dict)
            self.assertIn("db_path", task_dict)
            self.assertIn("directories", task_dict)
            self.assertIn("status", task_dict)
            self.assertIn("file_count", task_dict)
            self.assertIn("hashed_count", task_dict)
            self.assertIn("match_count", task_dict)
            self.assertIn("dupe_count", task_dict)
            self.assertEqual(task_dict["status"], "completed")

    def test_task_runner_status_response_schema(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "status_test.db")
            engine = DBEngine(db_path)
            engine.init_schema()

            task = ScanTaskDTO(
                task_id="status_test",
                name="status_test",
                db_path=db_path,
                directories=["/tmp"],
            )

            repo = TaskRepository(temp_dir)
            repo.save_task_metadata(task)

            runner = TaskRunner(repo)
            execution = runner.get_or_create_execution("status_test")
            self.assertIsNotNone(execution)

            dto = execution.get_dto()
            status_response = {
                "status": dto.status.value if isinstance(dto.status, TaskStatus) else str(dto.status),
                "scanning": dto.status in [TaskStatus.DISCOVERING, TaskStatus.HASHING, TaskStatus.SCANNING],
                "progress": dto.progress_percentage,
                "progress_msg": dto.progress_message,
                "active_task_id": dto.task_id,
                "has_results": dto.match_count > 0,
            }

            self.assertEqual(status_response["status"], "idle")
            self.assertFalse(status_response["scanning"])
            self.assertEqual(status_response["progress"], 0)
            self.assertEqual(status_response["active_task_id"], "status_test")

    def test_duplicate_group_dto_serialization(self):
        from core.domain.models import DuplicateGroupDTO, FileDTO

        pivot = FileDTO(path="/path/to/pivot.txt", size=1024)
        dup = FileDTO(path="/path/to/dup.txt", size=1024)
        group = DuplicateGroupDTO(group_id=1, pivot=pivot, duplicates=[dup], saved_bytes=1024)

        serialized = group.serialize_to_dict(group_index=5)
        self.assertEqual(serialized["id"], 5)
        self.assertEqual(serialized["percentage"], 100)
        self.assertEqual(len(serialized["files"]), 2)
        self.assertTrue(serialized["files"][0]["is_ref"])
        self.assertFalse(serialized["files"][0]["marked"])
        self.assertEqual(serialized["files"][0]["path"], "/path/to/pivot.txt")
        self.assertFalse(serialized["files"][1]["is_ref"])
        self.assertTrue(serialized["files"][1]["marked"])
        self.assertEqual(serialized["files"][1]["path"], "/path/to/dup.txt")


if __name__ == "__main__":
    unittest.main()
