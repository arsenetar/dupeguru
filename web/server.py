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
from typing import Any, Dict, List, Optional

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

from core.domain.models import TaskStatus  # noqa: E402
from core.paths import get_appdata_path, get_cache_path  # noqa: E402
from core.service.deletion import FileDeletionService  # noqa: E402
from core.service.task_runner import TaskRunner  # noqa: E402
from core.storage.task_repo import TaskRepository  # noqa: E402
from hscommon.util import format_size  # noqa: E402

# Backward-compatibility alias
get_appdata_pure_python = get_appdata_path
special_folder_path_pure_python = get_cache_path


# Thread-safe server state manager
class ServerState:
    """Thread-safe synchronization wrapper for server execution state and target directories."""

    def __init__(self):
        self._lock = threading.RLock()
        self._state = {
            "status": "idle",
            "scanning": False,
            "progress": 0,
            "progress_msg": "",
            "messages": [],
            "active_task_id": None,
            "deleting": False,
            "delete_progress": 0,
            "delete_total": 0,
            "cross_matching": False,
            "cross_scan_msg": "",
        }
        self._directories: List[str] = []

    def __getitem__(self, key: str) -> Any:
        with self._lock:
            return self._state[key]

    def __setitem__(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = value

    def update(self, *args, **kwargs) -> None:
        with self._lock:
            if args:
                self._state.update(args[0])
            self._state.update(kwargs)

    def get_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def get_directories(self) -> List[str]:
        with self._lock:
            return list(self._directories)

    def add_directory(self, path_str: str, clear_existing: bool = False) -> List[str]:
        with self._lock:
            norm_path = os.path.normpath(path_str.strip().strip("'\""))
            if clear_existing:
                self._directories.clear()
            if norm_path and norm_path not in self._directories:
                self._directories.append(norm_path)
            return list(self._directories)

    def remove_directory_by_path(self, path_str: str) -> List[str]:
        with self._lock:
            norm_path = os.path.normpath(path_str.strip().strip("'\""))
            if norm_path in self._directories:
                self._directories.remove(norm_path)
            return list(self._directories)

    def remove_directory_by_index(self, index: int) -> List[str]:
        with self._lock:
            if 0 <= index < len(self._directories):
                self._directories.pop(index)
            return list(self._directories)

    def clear_directories(self) -> List[str]:
        with self._lock:
            self._directories.clear()
            return list(self._directories)


server_state = ServerState()
# Backward-compatibility alias
app_state = server_state

appdata_dir = get_appdata_pure_python()
scans_dir = os.path.join(appdata_dir, "scans")
task_repository = TaskRepository(scans_dir)
task_runner = TaskRunner(task_repository)
file_deletion_service = FileDeletionService()


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


def is_safe_task_id(task_id: Any) -> bool:
    """Validate that task_id is a non-empty string without path traversal or null bytes."""
    if not isinstance(task_id, str) or not task_id:
        return False
    if "\0" in task_id or "/" in task_id or "\\" in task_id or ".." in task_id:
        return False
    return True


def sanitize_registered_db_path(p: Any) -> Optional[str]:
    """Validate that a DB path is a canonical, existing .db file registered in task_repository."""
    if not isinstance(p, str) or "\0" in p or not p:
        return None
    try:
        resolved_p = Path(p).resolve(strict=True)
        if resolved_p.suffix.lower() != ".db" or not resolved_p.is_file():
            return None
        valid_paths = {Path(t.db_path).resolve(strict=True) for t in task_repository.refresh()}
        return str(resolved_p) if resolved_p in valid_paths else None
    except (OSError, ValueError):
        return None


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
        if not isinstance(file_path, str) or "\0" in file_path:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")
            return

        unquoted_path = urllib.parse.unquote(file_path).lstrip("/")
        static_dir = (PROJECT_ROOT / "web" / "static").resolve()
        try:
            target_path = (static_dir / unquoted_path).resolve(strict=True)
        except (OSError, ValueError):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        if not target_path.is_relative_to(static_dir) or not target_path.is_file():
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
            active_id = server_state.get("active_task_id")

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

            is_deleting = server_state.get("deleting", False)
            is_cross_matching = server_state.get("cross_matching", False)
            if is_deleting:
                status_str = "deleting"
                progress = server_state.get("delete_progress", 0)
                progress_msg = server_state.get("progress_msg", "Deleting duplicate files...")
            elif is_cross_matching:
                status_str = "cross_matching"
                progress_msg = server_state.get("cross_scan_msg", "Comparing cross-database duplicate matches...")

            response = {
                "status": status_str,
                "scanning": scanning or is_cross_matching,
                "deleting": is_deleting,
                "cross_matching": is_cross_matching,
                "delete_progress": server_state.get("delete_progress", 0),
                "delete_total": server_state.get("delete_total", 0),
                "progress": progress,
                "progress_msg": progress_msg,
                "messages": server_state.get("messages", []),
                "targets": server_state.get_directories(),
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
            if not is_safe_task_id(task_id):
                self.wfile.write(json.dumps({"error": "Invalid task ID"}).encode())
            else:
                task = task_repository.get_task(task_id)
                if task:
                    self.wfile.write(json.dumps(task.to_dict()).encode())
                else:
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())

        elif path == "/api/directories":
            dirs = [{"path": d, "state": 0} for d in server_state.get_directories()]
            self.wfile.write(json.dumps(dirs).encode())

        elif path == "/api/browse":
            target_dir = query.get("path", [str(Path.home())])[0]
            if not isinstance(target_dir, str) or "\0" in target_dir:
                self.wfile.write(json.dumps({"error": "Invalid path specified"}).encode())
                return
            try:
                p = Path(target_dir).expanduser().resolve(strict=True)
                if not p.is_dir():
                    self.wfile.write(json.dumps({"error": "Path is not a directory"}).encode())
                    return
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
            active_id = server_state.get("active_task_id")
            if active_id:
                execution = task_runner.get_or_create_execution(active_id)
                if execution and execution.db_engine:
                    total_count, raw_files = execution.db_engine.get_files_page(
                        search=search if search else None, limit=limit, offset=offset
                    )
                    for r in raw_files:
                        files_list.append(
                            {
                                "path": r["path"],
                                "size": format_size(r["size"], 0, 1, False) if r["size"] is not None else "0 B",
                                "entry_dt": r["entry_dt"] or "",
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
            req_task_id = query.get("task_id", [None])[0]
            active_id = (
                req_task_id
                if is_safe_task_id(req_task_id)
                else (server_state.get("active_task_id") if not req_task_id else None)
            )
            total_groups = 0
            total_marked = 0
            batch_groups = []

            if active_id and is_safe_task_id(active_id):
                execution = task_runner.get_or_create_execution(active_id)
                if execution and execution.db_engine:
                    if execution.results_groups is not None:
                        # Scan just finished in memory or results already cached in RAM
                        groups = execution.results_groups
                        total_groups = len(groups)
                        batch_groups = groups[offset : offset + limit]
                        total_marked = (
                            sum(len(g.duplicates) for g in groups if hasattr(g, "duplicates"))
                            if groups and hasattr(groups[0], "duplicates")
                            else 0
                        )
                    else:
                        # Lazy paginated load directly from SQLite index
                        total_groups, total_marked, batch_groups = execution.db_engine.get_duplicate_groups_page(
                            limit=limit, offset=offset
                        )

            for g_idx, g in enumerate(batch_groups):
                if hasattr(g, "serialize_to_dict"):
                    groups_data.append(g.serialize_to_dict(group_index=offset + g_idx))
                elif hasattr(g, "pivot"):
                    pivot = g.pivot
                    files_data = [
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
                    ]
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
            raw_dirs = data.get("directories", [])
            if not raw_dirs:
                raw_dirs = server_state.get_directories()

            directories_list = [os.path.normpath(d.strip().strip("'\"")) for d in raw_dirs if d and d.strip()]

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

            task_dto = task_repository.create_task(name=name, directories=directories_list, overwrite=overwrite)
            server_state["active_task_id"] = task_dto.task_id

            execution = task_runner.start_task(task_dto.task_id)
            if execution:
                self.wfile.write(
                    json.dumps(sanitize_utf8({"success": True, "task": execution.get_dto().to_dict()})).encode()
                )
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Failed to launch task execution"}).encode())

        elif path == "/api/scans/rescan":
            task_id = data.get("task_id")
            if not is_safe_task_id(task_id):
                self.wfile.write(json.dumps({"success": False, "error": "Invalid or missing task_id"}).encode())
                return

            server_state.update(
                active_task_id=task_id,
                status=TaskStatus.SCANNING.value,
                scanning=True,
                progress=0,
                progress_msg=f"Re-scanning task '{task_id}'...",
            )

            execution = task_runner.rescan_task(task_id)
            if execution:
                self.wfile.write(
                    json.dumps(sanitize_utf8({"success": True, "task": execution.get_dto().to_dict()})).encode()
                )
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Task not found"}).encode())

        elif path == "/api/scans/load":
            task_id = data.get("task_id")
            if not is_safe_task_id(task_id):
                self.wfile.write(json.dumps({"success": False, "error": "Invalid or missing task_id"}).encode())
                return

            server_state["active_task_id"] = task_id
            execution = task_runner.get_or_create_execution(task_id)
            if execution:
                dto = execution.get_dto()

                is_active = (execution.thread and execution.thread.is_alive()) or dto.status in [
                    TaskStatus.DISCOVERING,
                    TaskStatus.HASHING,
                    TaskStatus.SCANNING,
                ]

                if is_active:
                    server_state.update(
                        status=dto.status.value if isinstance(dto.status, TaskStatus) else str(dto.status),
                        scanning=True,
                    )
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
                    server_state.update(
                        status=TaskStatus.HASHING.value,
                        scanning=True,
                        progress_msg=f"Hashing candidate files for '{dto.name}'...",
                    )
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

                server_state.update(
                    status=TaskStatus.COMPLETED.value,
                    scanning=False,
                    progress_msg="",
                )

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

        elif path == "/api/scans/delete":
            task_id = data.get("task_id")
            if not is_safe_task_id(task_id):
                self.wfile.write(json.dumps({"success": False, "error": "Invalid or missing task_id"}).encode())
                return
            deleted = task_repository.delete_task(task_id)
            self.wfile.write(json.dumps(sanitize_utf8({"success": deleted})).encode())

        elif path == "/api/cross_scan":
            raw_db_paths = data.get("db_paths", [])
            limit = int(data.get("limit", 500))
            offset = int(data.get("offset", 0))
            if raw_db_paths is None:
                raw_db_paths = []
            if not isinstance(raw_db_paths, list):
                self.wfile.write(
                    json.dumps(
                        {"success": False, "error": "db_paths must be a list of registered database paths"}
                    ).encode()
                )
                return

            # Build canonical allowlist from server-side registered tasks
            registered_canonical_paths = {}
            for t in task_repository.refresh():
                try:
                    canonical = str(Path(t.db_path).resolve(strict=True))
                    if canonical.endswith(".db"):
                        registered_canonical_paths[canonical] = canonical
                except (OSError, ValueError, TypeError):
                    continue

            if not raw_db_paths:
                db_paths = list(registered_canonical_paths.values())
            else:
                validated_db_paths = []
                for p in raw_db_paths:
                    if not isinstance(p, str) or "\0" in p or not p:
                        continue
                    try:
                        requested = str(Path(p).resolve(strict=True))
                    except (OSError, ValueError, TypeError):
                        continue
                    canonical = registered_canonical_paths.get(requested)
                    if canonical:
                        validated_db_paths.append(canonical)
                db_paths = validated_db_paths

            server_state.update(
                cross_matching=True,
                cross_scan_msg=f"Comparing cross-database duplicate matches across {len(db_paths)} databases...",
            )
            try:
                from core.pipeline.cross_matcher import CrossDBMatcher

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
            finally:
                server_state.update(cross_matching=False, cross_scan_msg="")

        elif path == "/api/directories":
            path_str = data.get("path")
            clear_existing = data.get("clear_existing", False)
            if path_str:
                current_dirs = server_state.add_directory(path_str, clear_existing=clear_existing)
            else:
                current_dirs = server_state.get_directories()
            dirs = [{"path": d, "state": 0} for d in current_dirs]
            self.wfile.write(json.dumps(dirs).encode())

        elif path == "/api/directories/remove":
            path_str = data.get("path")
            if path_str:
                current_dirs = server_state.remove_directory_by_path(path_str)
            else:
                current_dirs = server_state.get_directories()
            dirs = [{"path": d, "state": 0} for d in current_dirs]
            self.wfile.write(json.dumps(dirs).encode())

        elif path == "/api/scan":
            active_id = server_state.get("active_task_id")
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
            active_id = server_state.get("active_task_id")
            cancelled = task_runner.cancel_task(active_id) if active_id else False
            server_state.update(
                scanning=False,
                status=TaskStatus.CANCELLED.value,
            )
            self.wfile.write(json.dumps({"success": cancelled}).encode())

        elif path == "/api/results/mark":
            self.wfile.write(json.dumps({"success": True}).encode())

        elif path == "/api/results/delete":
            task_id = data.get("task_id") or server_state.get("active_task_id")
            if task_id and not is_safe_task_id(task_id):
                self.wfile.write(json.dumps({"success": False, "error": "Invalid task_id"}).encode())
                return

            paths_to_del = data.get("paths", [])
            delete_all_marked = data.get("delete_all_marked", False)

            execution = task_runner.get_or_create_execution(task_id) if task_id else None

            if delete_all_marked or not paths_to_del:
                collected_paths = []
                if execution and execution.db_engine:
                    collected_paths = execution.db_engine.get_all_duplicate_file_paths()
                if not collected_paths and execution and execution.results_groups:
                    for g in execution.results_groups:
                        for d in g.duplicates:
                            collected_paths.append(d.path)
                if collected_paths:
                    paths_to_del = collected_paths

            raw_db_paths = data.get("db_paths", [])
            db_paths = []
            for p in raw_db_paths:
                sanitized = sanitize_registered_db_path(p)
                if sanitized:
                    db_paths.append(sanitized)

            if not paths_to_del:
                self.wfile.write(
                    json.dumps(
                        sanitize_utf8(
                            {
                                "success": True,
                                "deleting": False,
                                "deleted_count": 0,
                                "task_id": task_id,
                            }
                        )
                    ).encode()
                )
                return

            def _run_deletion_pipeline(target_task_id, target_paths, target_db_paths):
                server_state.update(
                    status="deleting",
                    deleting=True,
                    delete_progress=0,
                    delete_total=len(target_paths),
                    progress_msg=f"Deleting 0 / {len(target_paths):,} marked duplicate files...",
                )

                def on_delete_progress(current, total, msg):
                    pct = int((current / total) * 100) if total else 100
                    server_state.update(delete_progress=pct, progress_msg=msg)

                try:
                    db_engines = []
                    task_exec = task_runner.get_or_create_execution(target_task_id) if target_task_id else None
                    if task_exec and task_exec.db_engine:
                        db_engines.append(task_exec.db_engine)

                    if target_db_paths:
                        from core.storage.db_engine import DBEngine

                        for db_p in target_db_paths:
                            if os.path.exists(db_p) and not any(e.db_path == db_p for e in db_engines):
                                try:
                                    db_engines.append(DBEngine(db_p))
                                except Exception as e:
                                    logging.error(f"Failed to load DB '{db_p}' for deletion purge: {e}")

                    active_groups = task_exec.results_groups if task_exec else None

                    count, _, updated_groups = file_deletion_service.delete_files(
                        target_paths=target_paths,
                        progress_callback=on_delete_progress,
                        db_engines=db_engines,
                        active_duplicate_groups=active_groups,
                    )

                    if task_exec and active_groups is not None:
                        task_exec.results_groups = updated_groups

                    logging.info(f"Deletion complete: removed {count} files for task '{target_task_id}'.")
                    return count
                finally:
                    server_state.update(
                        status="idle",
                        deleting=False,
                        delete_progress=100,
                        progress_msg="",
                    )

            if len(paths_to_del) <= 50:
                count = _run_deletion_pipeline(task_id, paths_to_del, db_paths)
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
            else:
                t = threading.Thread(
                    target=_run_deletion_pipeline,
                    args=(task_id, paths_to_del, db_paths),
                    daemon=True,
                )
                t.start()

                self.wfile.write(
                    json.dumps(
                        sanitize_utf8(
                            {
                                "success": True,
                                "in_background": True,
                                "deleting": True,
                                "total": len(paths_to_del),
                                "task_id": task_id,
                                "message": f"Deleting {len(paths_to_del):,} duplicate files in background...",
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
                current_dirs = server_state.clear_directories()
            else:
                index_str = query.get("index", ["-1"])[0]
                try:
                    idx = int(index_str)
                    current_dirs = server_state.remove_directory_by_index(idx)
                except ValueError:
                    current_dirs = server_state.get_directories()
            dirs = [{"path": d, "state": 0} for d in current_dirs]
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
