import json
import logging
import os
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from pathlib import Path

# Prevent PyQt5 from being imported to avoid loading C-extensions in a multi-threaded
# web server context, which can cause C-level segmentation faults.
sys.modules["PyQt5"] = None
sys.modules["PyQt5.QtCore"] = None
sys.modules["PyQt5.QtGui"] = None
sys.modules["PyQt5.QtWidgets"] = None

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import platform  # noqa: E402


# Pure Python fallback for AppData and Cache paths to avoid instantiating PyQt5
# QCoreApplication in a multi-threaded web server context, which causes segfaults.
def get_appdata_pure_python(portable=False):
    if portable:
        return os.path.join(str(PROJECT_ROOT), "data")

    system = platform.system()
    home = os.path.expanduser("~")
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        base = os.path.join(appdata, "de-dup") if appdata else os.path.join(home, "AppData", "Roaming", "de-dup")
        old_base = (
            os.path.join(appdata, "dupeGuru") if appdata else os.path.join(home, "AppData", "Roaming", "dupeGuru")
        )
    elif system == "Darwin":
        base = os.path.join(home, "Library", "Application Support", "de-dup")
        old_base = os.path.join(home, "Library", "Application Support", "dupeGuru")
    else:
        data_home = os.environ.get("XDG_DATA_HOME")
        base = os.path.join(data_home, "de-dup") if data_home else os.path.join(home, ".local/share", "de-dup")
        old_base = os.path.join(data_home, "dupeGuru") if data_home else os.path.join(home, ".local/share", "dupeGuru")

    if not os.path.exists(base) and os.path.exists(old_base):
        return old_base
    return base


def special_folder_path_pure_python(special_folder, portable=False):
    from hscommon.desktop import SpecialFolder

    if special_folder == SpecialFolder.CACHE:
        system = platform.system()
        home = os.path.expanduser("~")
        if system == "Windows":
            localappdata = os.environ.get("LOCALAPPDATA")
            if localappdata:
                return os.path.join(localappdata, "de-dup", "cache")
            return os.path.join(home, "AppData", "Local", "de-dup", "cache")
        elif system == "Darwin":
            return os.path.join(home, "Library", "Caches", "de-dup")
        else:
            cache_home = os.environ.get("XDG_CACHE_HOME")
            if cache_home:
                return os.path.join(cache_home, "de-dup")
            return os.path.join(home, ".cache", "de-dup")
    else:
        return get_appdata_pure_python(portable)


# Apply monkey patches to bypass PyQt5 AppDataLocation resolution in server
try:
    import qt.util  # noqa: E402

    qt.util.get_appdata = get_appdata_pure_python
except ImportError:
    pass

import hscommon.desktop  # noqa: E402

hscommon.desktop.special_folder_path = special_folder_path_pure_python
hscommon.desktop._special_folder_path = special_folder_path_pure_python

from core.domain.models import ScanTaskDTO, TaskStatus  # noqa: E402
from core.service.task_runner import TaskRunner  # noqa: E402
from core.storage.task_repo import TaskRepository  # noqa: E402
from hscommon.util import format_size  # noqa: E402

# Global state and synchronization lock
state_lock = threading.Lock()

app_state = {
    "status": "idle",  # idle, scanning, completed
    "scanning": False,
    "progress": 0,
    "progress_msg": "",
    "messages": [],
    "active_task_id": None,
}

appdata_dir = get_appdata_pure_python()
scans_dir = os.path.join(appdata_dir, "scans")
task_repository = TaskRepository(scans_dir)
task_runner = TaskRunner(task_repository)
selected_directories = []


def safe_path_exists(path_str, timeout=1.0):
    """Check path existence in a thread with a strict timeout to prevent hangs on stale network mounts."""
    result = [False]

    def check():
        try:
            result[0] = os.path.exists(path_str)
        except Exception:
            result[0] = False

    t = threading.Thread(target=check, daemon=True)
    t.start()
    t.join(timeout=timeout)
    return result[0]


def sanitize_utf8(obj):
    """Recursively clean surrogate escapes and non-UTF-8 characters in strings, lists, and dicts."""
    if isinstance(obj, str):
        return obj.encode("utf-8", errors="surrogateescape").decode("utf-8", errors="replace")
    elif isinstance(obj, dict):
        return {sanitize_utf8(k): sanitize_utf8(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_utf8(x) for x in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_utf8(x) for x in obj)
    return obj


# Setup basic logging
logging.basicConfig(level=logging.INFO)


class DupeGuruHTTPHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def serve_static(self, file_path):
        """Helper to serve static HTML, CSS, and JS files."""
        static_dir = PROJECT_ROOT / "web" / "static"
        target_path = (static_dir / file_path).resolve()

        if not target_path.is_relative_to(static_dir) or not target_path.exists():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        # Determine Content-Type
        content_type = "text/plain"
        if target_path.suffix == ".html":
            content_type = "text/html"
        elif target_path.suffix == ".css":
            content_type = "text/css"
        elif target_path.suffix == ".js":
            content_type = "application/javascript"
        elif target_path.suffix == ".png":
            content_type = "image/png"
        elif target_path.suffix == ".svg":
            content_type = "image/svg+xml"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        with open(target_path, "rb") as f:
            self.wfile.write(f.read())

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Serve UI files
        if path == "/" or path == "/index.html":
            self.serve_static("index.html")
            return
        elif path.startswith("/static/"):
            self.serve_static(path[8:])
            return

        # REST API endpoints
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()

        if path == "/api/status":
            active_id = app_state.get("active_task_id")

            status_str = "idle"
            scanning = False
            progress = 0
            progress_msg = ""
            has_results = False

            if active_id:
                execution = task_runner.get_or_create_execution(active_id)
                if execution:
                    dto = execution.get_dto()
                    status_str = dto.status.value if isinstance(dto.status, TaskStatus) else str(dto.status)
                    scanning = dto.status in [TaskStatus.DISCOVERING, TaskStatus.HASHING, TaskStatus.SCANNING]
                    progress = dto.progress_percentage
                    progress_msg = dto.progress_message
                    has_results = dto.match_count > 0

            response = {
                "status": status_str,
                "scanning": scanning,
                "progress": progress,
                "progress_msg": progress_msg,
                "messages": app_state.get("messages", []),
                "targets": selected_directories,
                "active_task_id": active_id,
                "has_results": has_results,
            }
            sanitized = sanitize_utf8(response)
            self.wfile.write(json.dumps(sanitized).encode("utf-8", errors="replace"))

        elif path == "/api/config":
            self.wfile.write(json.dumps({}).encode())

        elif path == "/api/scans":
            tasks = task_repository.refresh()
            self.wfile.write(json.dumps([t.to_dict() for t in tasks]).encode())

        elif path.startswith("/api/scans/"):
            task_id = path.replace("/api/scans/", "")
            task = task_repository.get_task(task_id)
            if task:
                self.wfile.write(json.dumps(task.to_dict()).encode())
            else:
                self.wfile.write(json.dumps({"error": "Task not found"}).encode())

        elif path == "/api/directories":
            dirs = [{"path": d, "state": 0} for d in selected_directories]
            self.wfile.write(json.dumps(dirs).encode())

        elif path == "/api/browse":
            target_dir = query.get("path", [str(Path.home())])[0]
            try:
                p = Path(target_dir).expanduser().resolve()
                contents = []
                with os.scandir(str(p)) as it:
                    for entry in it:
                        try:
                            if entry.is_dir(follow_symlinks=False) and not entry.name.startswith("."):
                                contents.append({"name": entry.name, "path": entry.path})
                        except Exception:
                            pass
                contents.sort(key=lambda x: x["name"].lower())
                self.wfile.write(
                    json.dumps(
                        sanitize_utf8(
                            {
                                "current": str(p),
                                "parent": str(p.parent) if p.parent != p else None,
                                "folders": contents,
                            }
                        )
                    ).encode()
                )
            except Exception as e:
                self.wfile.write(json.dumps(sanitize_utf8({"error": str(e)})).encode())

        elif path == "/api/cache/files":
            search = query.get("search", [""])[0]
            limit = int(query.get("limit", [100])[0])
            offset = int(query.get("offset", [0])[0])

            files_list = []
            total_count = 0
            active_id = app_state.get("active_task_id")
            if active_id:
                execution = task_runner.get_or_create_execution(active_id)
                if execution:
                    conn = execution.db_engine.get_connection()
                    cur = conn.cursor()
                    if search:
                        cur.execute("SELECT COUNT(*) FROM files WHERE path LIKE ?", (f"%{search}%",))
                        total_count = cur.fetchone()[0]
                        cur.execute(
                            "SELECT path, size, COALESCE(entry_dt, datetime(mtime_ns/1000000000, 'unixepoch')) "
                            "FROM files WHERE path LIKE ? LIMIT ? OFFSET ?",
                            (f"%{search}%", limit, offset),
                        )
                    else:
                        cur.execute("SELECT COUNT(*) FROM files")
                        total_count = cur.fetchone()[0]
                        cur.execute(
                            "SELECT path, size, COALESCE(entry_dt, datetime(mtime_ns/1000000000, 'unixepoch')) "
                            "FROM files LIMIT ? OFFSET ?",
                            (limit, offset),
                        )
                    rows = cur.fetchall()
                    for r in rows:
                        files_list.append(
                            {
                                "path": r[0],
                                "size": format_size(r[1], 0, 1, False) if r[1] is not None else "0 B",
                                "entry_dt": r[2] or "",
                            }
                        )

            self.wfile.write(
                json.dumps(
                    {
                        "success": True,
                        "files": files_list,
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                    }
                ).encode()
            )

        elif path == "/api/results":
            limit = 50
            offset = 0
            try:
                if "limit" in query:
                    limit = int(query["limit"][0])
                if "offset" in query:
                    offset = int(query["offset"][0])
            except Exception:
                pass

            groups_data = []
            active_id = app_state.get("active_task_id")
            groups = []

            if active_id:
                execution = task_runner.get_or_create_execution(active_id)
                if execution:
                    if not execution.results_groups:
                        if execution.db_engine.has_saved_duplicate_groups():
                            execution.results_groups = execution.db_engine.load_duplicate_groups()
                    groups = execution.results_groups or []

            total_groups = len(groups)
            batch_groups = groups[offset : offset + limit]

            for g_idx, g in enumerate(batch_groups):
                files_data = []
                if hasattr(g, "pivot"):
                    pivot = g.pivot
                    files_data.append(
                        {
                            "path": pivot.path,
                            "name": pivot.name,
                            "folder": os.path.dirname(pivot.path),
                            "size": format_size(pivot.size, 0, 1, False),
                            "mtime": "",
                            "percentage": "100%",
                            "is_ref": True,
                            "marked": False,
                            "markable": False,
                        }
                    )
                    for d in g.duplicates:
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

                groups_data.append(
                    {
                        "id": offset + g_idx,
                        "percentage": getattr(g, "percentage", 100),
                        "files": files_data,
                    }
                )

            total_marked = (
                sum(len(g.duplicates) for g in groups if hasattr(g, "duplicates"))
                if groups and hasattr(groups[0], "duplicates")
                else 0
            )
            response_data = {
                "success": True,
                "total": total_groups,
                "groups": groups_data,
                "total_marked": total_marked,
                "limit": limit,
                "offset": offset,
            }
            self.wfile.write(json.dumps(sanitize_utf8(response_data)).encode())

    def do_POST(self):
        path = self.path
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""
            data = json.loads(post_data) if post_data else {}
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": f"Invalid JSON payload: {e}"}).encode())
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if path == "/api/config":
            self.wfile.write(json.dumps({"success": True}).encode())

        elif path == "/api/scans/create":
            name = data.get("name", "Scan").strip() or f"Scan_{time.strftime('%Y%m%d_%H%M%S')}"
            directories_list = data.get("directories", [])
            if not directories_list:
                directories_list = list(selected_directories)

            if not directories_list:
                self.wfile.write(
                    json.dumps(sanitize_utf8({"success": False, "error": "No directory path specified"})).encode()
                )
                return

            overwrite = data.get("overwrite", False)
            existing_task = task_repository.get_task(name)
            if existing_task and not overwrite:
                self.wfile.write(
                    json.dumps(
                        sanitize_utf8(
                            {
                                "success": False,
                                "exists": True,
                                "task_name": name,
                                "existing_task": existing_task.to_dict(),
                                "error": f"A scan database named '{name}' already exists.",
                            }
                        )
                    ).encode()
                )
                return

            import uuid

            task_id = f"{name}_{uuid.uuid4().hex[:8]}"
            db_path = os.path.join(scans_dir, f"{task_id}.db")

            task_dto = ScanTaskDTO(
                task_id=task_id,
                name=name,
                db_path=db_path,
                directories=directories_list,
                status=TaskStatus.IDLE,
            )
            task_repository.save_task_metadata(task_dto)
            app_state["active_task_id"] = task_id

            execution = task_runner.start_task(task_id)
            if execution:
                self.wfile.write(
                    json.dumps(sanitize_utf8({"success": True, "task": execution.get_dto().to_dict()})).encode()
                )
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Failed to launch task execution"}).encode())

        elif path == "/api/scans/rescan":
            task_id = data.get("task_id")
            if task_id:
                app_state["active_task_id"] = task_id
                app_state["status"] = "scanning"
                app_state["scanning"] = True
                app_state["progress"] = 0
                app_state["progress_msg"] = f"Re-scanning task '{task_id}'..."

                execution = task_runner.rescan_task(task_id)
                if execution:
                    self.wfile.write(
                        json.dumps(sanitize_utf8({"success": True, "task": execution.get_dto().to_dict()})).encode()
                    )
                else:
                    self.wfile.write(json.dumps({"success": False, "error": "Task not found"}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Missing task_id"}).encode())

        elif path == "/api/scans/load":
            task_id = data.get("task_id")
            if task_id:
                app_state["active_task_id"] = task_id
                execution = task_runner.get_or_create_execution(task_id)
                if execution:
                    dto = execution.get_dto()

                    is_active = (execution.thread and execution.thread.is_alive()) or dto.status in [
                        TaskStatus.DISCOVERING,
                        TaskStatus.HASHING,
                        TaskStatus.SCANNING,
                    ]

                    if is_active:
                        app_state["status"] = (
                            dto.status.value if isinstance(dto.status, TaskStatus) else str(dto.status)
                        )
                        app_state["scanning"] = True
                        self.wfile.write(
                            json.dumps(
                                sanitize_utf8(
                                    {
                                        "success": True,
                                        "is_scanning": True,
                                        "task": dto.to_dict(),
                                    }
                                )
                            ).encode()
                        )
                        return

                    if (
                        dto.file_count > 0
                        and dto.hashed_count < dto.file_count
                        and not execution.db_engine.has_saved_duplicate_groups()
                    ):
                        execution.start(rescan=False)
                        app_state["status"] = "hashing"
                        app_state["scanning"] = True
                        app_state["progress_msg"] = f"Hashing candidate files for '{dto.name}'..."
                        self.wfile.write(
                            json.dumps(
                                sanitize_utf8(
                                    {
                                        "success": True,
                                        "is_scanning": True,
                                        "task": dto.to_dict(),
                                    }
                                )
                            ).encode()
                        )
                        return

                    if not execution.results_groups:
                        try:
                            from core.pipeline.matcher import DuplicateMatcher

                            execution.results_groups = DuplicateMatcher(execution.db_engine).load_or_find_duplicates()
                        except Exception as e:
                            logging.error(f"Error matching candidate duplicates on load: {e}")

                    app_state["status"] = "completed"
                    app_state["scanning"] = False
                    app_state["progress_msg"] = ""

                    self.wfile.write(
                        json.dumps(
                            sanitize_utf8(
                                {
                                    "success": True,
                                    "is_scanning": False,
                                    "task": dto.to_dict(),
                                }
                            )
                        ).encode()
                    )
                else:
                    self.wfile.write(json.dumps({"success": False, "error": "Task not found"}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Missing task_id"}).encode())

        elif path == "/api/scans/delete":
            task_id = data.get("task_id")
            deleted = task_repository.delete_task(task_id)
            self.wfile.write(json.dumps(sanitize_utf8({"success": deleted})).encode())

        elif path == "/api/cross_scan":
            db_paths = data.get("db_paths", [])
            limit = int(data.get("limit", 500))
            offset = int(data.get("offset", 0))
            if not db_paths:
                db_paths = [t.db_path for t in task_repository.refresh()]

            try:
                from core.cross_db import CrossDBMatcher

                matcher = CrossDBMatcher(db_paths)
                results = matcher.find_cross_duplicates()
                paginated_results = results[offset : offset + limit] if limit > 0 else results
                self.wfile.write(
                    json.dumps(
                        {
                            "success": True,
                            "groups": paginated_results,
                            "total_groups": len(results),
                            "limit": limit,
                            "offset": offset,
                        }
                    ).encode()
                )
            except Exception as e:
                logging.error(f"Error in cross_scan endpoint: {e}")
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

        elif path == "/api/directories":
            path_str = data.get("path")
            clear_existing = data.get("clear_existing", False)
            if path_str:
                path_str = path_str.strip().strip("'\"")
                if clear_existing:
                    selected_directories.clear()
                if path_str not in selected_directories:
                    selected_directories.append(path_str)

            dirs = [{"path": d, "state": 0} for d in selected_directories]
            self.wfile.write(json.dumps(dirs).encode())

        elif path == "/api/directories/remove":
            path_str = data.get("path")
            if path_str and path_str in selected_directories:
                selected_directories.remove(path_str)
            dirs = [{"path": d, "state": 0} for d in selected_directories]
            self.wfile.write(json.dumps(dirs).encode())

        elif path == "/api/scan":
            active_id = app_state.get("active_task_id")
            if active_id:
                execution = task_runner.start_task(active_id)
                if execution:
                    self.wfile.write(
                        json.dumps(sanitize_utf8({"success": True, "task": execution.get_dto().to_dict()})).encode()
                    )
                else:
                    self.wfile.write(json.dumps({"success": False, "error": "Task execution failed"}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "No active task to scan"}).encode())

        elif path == "/api/scan/cancel":
            active_id = app_state.get("active_task_id")
            cancelled = task_runner.cancel_task(active_id) if active_id else False
            app_state["scanning"] = False
            app_state["status"] = "cancelled"
            self.wfile.write(json.dumps({"success": cancelled}).encode())

        elif path == "/api/results/mark":
            self.wfile.write(json.dumps({"success": True}).encode())

        elif path == "/api/results/delete":
            task_id = data.get("task_id") or app_state.get("active_task_id")
            paths_to_del = data.get("paths", [])

            execution = task_runner.get_or_create_execution(task_id) if task_id else None

            if not paths_to_del and execution and execution.results_groups:
                for g in execution.results_groups:
                    for d in g.duplicates:
                        if getattr(d, "marked", False) and os.path.exists(d.path):
                            paths_to_del.append(d.path)

            count = 0
            successful_paths = []
            for p in paths_to_del:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                        count += 1
                        successful_paths.append(p)
                    except OSError as e:
                        logging.error(f"Failed to delete file {p}: {e}")
                else:
                    successful_paths.append(p)

            db_paths = data.get("db_paths", [])

            if task_id and successful_paths:
                task_exec = task_runner.get_or_create_execution(task_id)
                if task_exec and task_exec.db_engine:
                    task_exec.db_engine.delete_files_by_paths(successful_paths)
                    if task_exec.results_groups:
                        from core.domain.models import DuplicateGroupDTO

                        filtered_groups = []
                        for g in task_exec.results_groups:
                            rem_dupes = [d for d in g.duplicates if d.path not in successful_paths]
                            if rem_dupes:
                                new_saved = sum(d.size for d in rem_dupes)
                                filtered_groups.append(
                                    DuplicateGroupDTO(
                                        group_id=g.group_id,
                                        pivot=g.pivot,
                                        duplicates=rem_dupes,
                                        saved_bytes=new_saved,
                                    )
                                )
                        task_exec.results_groups = filtered_groups

            if db_paths and successful_paths:
                from core.storage.db_engine import DBEngine

                for db_p in db_paths:
                    if os.path.exists(db_p):
                        try:
                            engine = DBEngine(db_p)
                            engine.delete_files_by_paths(successful_paths)
                        except Exception as e:
                            logging.error(f"Failed to purge deleted files from DB '{db_p}': {e}")

            logging.info(f"Deletion complete: removed {count} files for task '{task_id}'.")

            self.wfile.write(
                json.dumps(
                    sanitize_utf8(
                        {
                            "success": True,
                            "deleting": False,
                            "deleted_count": count,
                            "task_id": task_id,
                        }
                    )
                ).encode()
            )

        elif path == "/api/results/save":
            self.wfile.write(json.dumps({"success": True}).encode())
        else:
            self.wfile.write(json.dumps({"success": False, "error": "Endpoint not found"}).encode())

    def do_DELETE(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if path == "/api/directories":
            clear_all = query.get("clear_all", ["false"])[0].lower() == "true"
            if clear_all:
                selected_directories.clear()
            else:
                index_str = query.get("index", ["-1"])[0]
                try:
                    idx = int(index_str)
                    if 0 <= idx < len(selected_directories):
                        selected_directories.pop(idx)
                except ValueError:
                    pass
            dirs = [{"path": d, "state": 0} for d in selected_directories]
            self.wfile.write(json.dumps(dirs).encode())
        else:
            self.wfile.write(json.dumps({"success": False, "error": "Endpoint not found"}).encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_server(port=8080):
    server = ThreadedHTTPServer(("localhost", port), DupeGuruHTTPHandler)
    print(f"Starting de-dup HTML Web Server on http://localhost:{port}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Server stopped.", flush=True)


if __name__ == "__main__":
    start_server()
