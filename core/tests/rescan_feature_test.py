# Unit tests for Refresh Scan feature across modified and deleted files

import os
import tempfile
import time
import unittest
from core.domain.models import ScanTaskDTO
from core.pipeline.discovery import FileDiscovery
from core.service.task_runner import TaskRunner
from core.storage.db_engine import DBEngine
from core.storage.task_repo import TaskRepository


class TestRescanFeature(unittest.TestCase):
    def test_discovery_rescan_added_modified_deleted_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            f1 = os.path.join(temp_dir, "f1.txt")
            f2 = os.path.join(temp_dir, "f2.txt")

            with open(f1, "wb") as fp:
                fp.write(b"Original Content 1")
            with open(f2, "wb") as fp:
                fp.write(b"Original Content 2")

            engine = DBEngine(":memory:")
            discovery = FileDiscovery(engine)

            # Initial scan
            files_initial = discovery.collect_files([temp_dir], enable_cache=False)
            self.assertEqual(len(files_initial), 2)

            # Modify f1, delete f2, add f3
            with open(f1, "wb") as fp:
                fp.write(b"Modified Content 1 with extra data")

            os.remove(f2)

            f3 = os.path.join(temp_dir, "f3.txt")
            with open(f3, "wb") as fp:
                fp.write(b"New File Content 3")

            # Perform rescan
            files_rescanned = discovery.rescan_directories([temp_dir])
            self.assertEqual(len(files_rescanned), 2)

            paths = {f.path for f in files_rescanned}
            self.assertIn(f1, paths)
            self.assertIn(f3, paths)
            self.assertNotIn(f2, paths)

    def test_task_runner_rescan_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            scan_folder = os.path.join(temp_dir, "target")
            os.makedirs(scan_folder, exist_ok=True)

            f1 = os.path.join(scan_folder, "dup1.txt")
            f2 = os.path.join(scan_folder, "dup2.txt")

            with open(f1, "wb") as fp:
                fp.write(b"Identical Data")
            with open(f2, "wb") as fp:
                fp.write(b"Identical Data")

            db_path = os.path.join(temp_dir, "rescan_task.db")
            engine = DBEngine(db_path)
            engine.init_schema()

            task = ScanTaskDTO(
                task_id="rescan_task",
                name="rescan_task",
                db_path=db_path,
                directories=[scan_folder],
            )

            repo = TaskRepository(temp_dir)
            repo.save_task_metadata(task)

            runner = TaskRunner(repo)
            exec_initial = runner.start_task("rescan_task")

            start_t = time.time()
            while exec_initial.thread and exec_initial.thread.is_alive() and (time.time() - start_t < 5.0):
                time.sleep(0.05)

            dto_initial = exec_initial.get_dto()
            self.assertEqual(dto_initial.match_count, 1)

            # Add third duplicate
            f3 = os.path.join(scan_folder, "dup3.txt")
            with open(f3, "wb") as fp:
                fp.write(b"Identical Data")

            exec_rescan = runner.rescan_task("rescan_task")

            start_t = time.time()
            while exec_rescan.thread and exec_rescan.thread.is_alive() and (time.time() - start_t < 5.0):
                time.sleep(0.05)

            dto_rescanned = exec_rescan.get_dto()
            self.assertEqual(dto_rescanned.file_count, 3)
            self.assertEqual(dto_rescanned.match_count, 1)
            self.assertEqual(dto_rescanned.dupe_count, 2)


if __name__ == "__main__":
    unittest.main()
