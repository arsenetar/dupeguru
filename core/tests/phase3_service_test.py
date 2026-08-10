# Unit tests for Phase 3 Service Layer (TaskExecution and TaskRunner)

import os
import tempfile
import time
import unittest
from core.domain.models import ScanTaskDTO, TaskStatus
from core.service.task_runner import TaskExecution, TaskRunner
from core.storage.db_engine import DBEngine
from core.storage.task_repo import TaskRepository


class TestPhase3Service(unittest.TestCase):
    def test_task_execution_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test_task1.db")
            engine = DBEngine(db_path)
            engine.init_schema()

            # Seed synthetic file data
            with engine.transaction() as conn:
                conn.execute(
                    "INSERT INTO files (path, size, mtime_ns, digest_partial, digest) VALUES (?, ?, ?, ?, ?)",
                    ("/tmp/file1.txt", 1000, 100, b"p_hash1", b"f_hash1"),
                )
                conn.execute(
                    "INSERT INTO files (path, size, mtime_ns, digest_partial, digest) VALUES (?, ?, ?, ?, ?)",
                    ("/tmp/file2.txt", 1000, 100, b"p_hash1", b"f_hash1"),
                )

            task_dto = ScanTaskDTO(
                task_id="test_task1",
                name="test_task1",
                db_path=db_path,
                directories=["/tmp"],
                status=TaskStatus.IDLE,
            )

            repo = TaskRepository(temp_dir)
            repo.save_task_metadata(task_dto)

            execution = TaskExecution(task_dto, task_repo=repo)
            execution.start()

            # Wait for execution thread to finish
            start_t = time.time()
            while execution.thread and execution.thread.is_alive() and (time.time() - start_t < 5.0):
                time.sleep(0.05)

            dto = execution.get_dto()
            self.assertEqual(dto.status, TaskStatus.COMPLETED)
            self.assertEqual(dto.match_count, 1)
            self.assertEqual(dto.file_count, 2)
            self.assertEqual(dto.hashed_count, 2)
            self.assertEqual(len(execution.results_groups), 1)

    def test_task_runner_concurrent_isolation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = TaskRepository(temp_dir)

            db1 = os.path.join(temp_dir, "task1_111.db")
            db2 = os.path.join(temp_dir, "task2_222.db")

            e1 = DBEngine(db1)
            e1.init_schema()
            with e1.transaction() as conn:
                conn.execute("INSERT INTO files (path, size) VALUES (?, ?)", ("/tmp/a1.txt", 500))
                conn.execute("INSERT INTO files (path, size) VALUES (?, ?)", ("/tmp/a2.txt", 500))

            e2 = DBEngine(db2)
            e2.init_schema()
            with e2.transaction() as conn:
                conn.execute("INSERT INTO files (path, size) VALUES (?, ?)", ("/tmp/b1.txt", 900))
                conn.execute("INSERT INTO files (path, size) VALUES (?, ?)", ("/tmp/b2.txt", 900))

            t1 = ScanTaskDTO(task_id="task1_111", name="task1", db_path=db1, directories=["/tmp"])
            t2 = ScanTaskDTO(task_id="task2_222", name="task2", db_path=db2, directories=["/tmp"])

            repo.save_task_metadata(t1)
            repo.save_task_metadata(t2)

            runner = TaskRunner(repo)
            exec1 = runner.start_task("task1_111")
            exec2 = runner.start_task("task2_222")

            self.assertIsNotNone(exec1)
            self.assertIsNotNone(exec2)

            start_t = time.time()
            while ((exec1.thread and exec1.thread.is_alive()) or (exec2.thread and exec2.thread.is_alive())) and (
                time.time() - start_t < 5.0
            ):
                time.sleep(0.05)

            dto1 = exec1.get_dto()
            dto2 = exec2.get_dto()

            self.assertEqual(dto1.task_id, "task1_111")
            self.assertEqual(dto2.task_id, "task2_222")
            self.assertEqual(dto1.status, TaskStatus.COMPLETED)
            self.assertEqual(dto2.status, TaskStatus.COMPLETED)

    def test_task_execution_cancellation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "cancel_task.db")
            engine = DBEngine(db_path)
            engine.init_schema()

            task_dto = ScanTaskDTO(
                task_id="cancel_task",
                name="cancel_task",
                db_path=db_path,
                directories=["/tmp"],
            )

            execution = TaskExecution(task_dto)
            execution.cancel()

            dto = execution.get_dto()
            self.assertEqual(dto.status, TaskStatus.CANCELLED)


if __name__ == "__main__":
    unittest.main()
