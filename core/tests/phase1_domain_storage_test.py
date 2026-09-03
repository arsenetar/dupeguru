# Unit tests for Phase 1 Domain DTOs and Storage Layer

import os
import tempfile
import unittest
from core.domain.models import FileDTO, DuplicateGroupDTO, ScanTaskDTO, TaskStatus
from core.storage.db_engine import DBEngine
from core.storage.task_repo import TaskRepository


class TestPhase1DomainStorage(unittest.TestCase):
    def test_file_dto_immutability(self):
        f = FileDTO(path="/tmp/test.txt", size=1024, mtime_ns=1000)
        self.assertEqual(f.name, "test.txt")
        self.assertEqual(f.size, 1024)
        self.assertFalse(f.is_ref)
        with self.assertRaises(AttributeError):
            f.size = 2048  # frozen dataclass

    def test_duplicate_group_dto(self):
        pivot = FileDTO(path="/tmp/f1.txt", size=500)
        dupe = FileDTO(path="/tmp/f2.txt", size=500)
        group = DuplicateGroupDTO(group_id=1, pivot=pivot, duplicates=[dupe], saved_bytes=500)
        self.assertEqual(group.total_files, 2)
        self.assertEqual(group.saved_bytes, 500)

    def test_db_engine_in_memory_schema_and_counts(self):
        engine = DBEngine(":memory:")
        engine.init_schema()

        file_count, hashed_count = engine.get_file_counts()
        self.assertEqual(file_count, 0)
        self.assertEqual(hashed_count, 0)

        with engine.transaction() as conn:
            conn.execute(
                "INSERT INTO files (path, size, mtime_ns, digest_partial) VALUES (?, ?, ?, ?)",
                ("/tmp/file1.txt", 200, 100, b"hash1"),
            )
            conn.execute(
                "INSERT INTO files (path, size, mtime_ns) VALUES (?, ?, ?)",
                ("/tmp/file2.txt", 200, 100),
            )

        file_count, hashed_count = engine.get_file_counts()
        self.assertEqual(file_count, 2)
        self.assertEqual(hashed_count, 1)

        candidate_sizes = engine.get_candidate_sizes()
        self.assertEqual(candidate_sizes, [200])

        candidates = engine.get_files_by_sizes([200])
        self.assertEqual(len(candidates), 2)

        engine.set_metadata("match_count", "5")
        meta = engine.get_metadata()
        self.assertEqual(meta.get("match_count"), "5")

    def test_task_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = TaskRepository(temp_dir)

            db_path = os.path.join(temp_dir, "test_task_123.db")
            engine = DBEngine(db_path)
            engine.init_schema()

            with engine.transaction() as conn:
                conn.execute(
                    "INSERT INTO files (path, size, digest) VALUES (?, ?, ?)",
                    ("/tmp/a.txt", 100, b"digest_a"),
                )

            task = ScanTaskDTO(
                task_id="test_task_123",
                name="test_task",
                db_path=db_path,
                directories=["/tmp"],
                status=TaskStatus.COMPLETED,
                match_count=1,
            )
            repo.save_task_metadata(task)

            tasks = repo.refresh()
            self.assertEqual(len(tasks), 1)
            loaded_task = repo.get_task("test_task_123")
            self.assertIsNotNone(loaded_task)
            self.assertEqual(loaded_task.file_count, 1)
            self.assertEqual(loaded_task.hashed_count, 1)
            self.assertEqual(loaded_task.match_count, 1)

    def test_duplicate_groups_pagination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "page_test.db")
            engine = DBEngine(db_path)
            engine.init_schema()

            f1 = FileDTO(path="/tmp/f1.txt", size=1000)
            f2 = FileDTO(path="/tmp/f2.txt", size=1000)
            f3 = FileDTO(path="/tmp/f3.txt", size=2000)
            f4 = FileDTO(path="/tmp/f4.txt", size=2000)

            with engine.transaction() as conn:
                for f in [f1, f2, f3, f4]:
                    conn.execute("INSERT INTO files (path, size) VALUES (?, ?)", (f.path, f.size))

            group1 = DuplicateGroupDTO(group_id=1, pivot=f1, duplicates=[f2], saved_bytes=1000)
            group2 = DuplicateGroupDTO(group_id=2, pivot=f3, duplicates=[f4], saved_bytes=2000)
            engine.save_duplicate_groups([group1, group2])

            total_groups, total_marked, page1 = engine.get_duplicate_groups_page(limit=1, offset=0)
            self.assertEqual(total_groups, 2)
            self.assertEqual(total_marked, 2)
            self.assertEqual(len(page1), 1)
            self.assertEqual(page1[0].group_id, 1)
            self.assertEqual(page1[0].pivot.path, "/tmp/f1.txt")
            self.assertEqual(len(page1[0].duplicates), 1)

            _, _, page2 = engine.get_duplicate_groups_page(limit=1, offset=1)
            self.assertEqual(len(page2), 1)
            self.assertEqual(page2[0].group_id, 2)
            self.assertEqual(page2[0].pivot.path, "/tmp/f3.txt")


if __name__ == "__main__":
    unittest.main()
