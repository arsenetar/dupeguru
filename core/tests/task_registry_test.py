import os
import tempfile

from core.task_registry import ScanTaskRegistry, ScanTaskStatus


def test_task_registry_crud():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ScanTaskRegistry(tmpdir)

        # Test creation
        task = registry.create_task("Test Scan", ["/tmp/dir1"], db_filename="test_scan.db")
        assert task.name == "Test Scan"
        assert task.directories == ["/tmp/dir1"]
        assert task.status == ScanTaskStatus.IDLE
        assert os.path.basename(task.db_path) == "test_scan.db"

        # Test get_task
        retrieved = registry.get_task(task.task_id)
        assert retrieved is not None
        assert retrieved.task_id == task.task_id

        # Test list_tasks
        tasks_list = registry.list_tasks()
        assert len(tasks_list) == 1
        assert tasks_list[0]["task_id"] == task.task_id

        # Create mock DB file
        with open(task.db_path, "w") as f:
            f.write("mock db content")

        assert os.path.exists(task.db_path)

        # Test delete_task
        deleted = registry.delete_task(task.task_id, delete_db_file=True)
        assert deleted is True
        assert not os.path.exists(task.db_path)
        assert registry.get_task(task.task_id) is None
