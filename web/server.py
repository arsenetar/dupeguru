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

from core.app import DupeGuru  # noqa: E402
from core import fs  # noqa: E402
from core.task_registry import ScanTaskRegistry, ScanTaskStatus  # noqa: E402
from hscommon.trans import install_gettext_trans  # noqa: E402
from hscommon.util import format_size  # noqa: E402


class WebProgressView:
    def __init__(self, state):
        self.state = state

    def show(self):
        self.state["scanning"] = True
        self.state["status"] = "scanning"

    def close(self):
        self.state["scanning"] = False
        if model.progress_window.job_cancelled:
            self.state["status"] = "idle"
        else:
            self.state["status"] = "completed"

    def set_progress(self, progress):
        self.state["progress"] = progress


class WebViewAdapter:
    def __init__(self, state):
        self.state = state
        self.preferences = {
            "FilterHardness": 95,
            "MixFileKind": True,
            "UseRegexp": False,
            "IgnoreHardlinkMatches": False,
            "RemoveEmptyFolders": False,
            "RehashIgnoreMTime": False,
            "IncludeExistsCheck": True,
            "DebugMode": False,
            "CheckpointFrequency": 100,
            "ScanType": 5,
        }

    def get_default(self, key_name, default=None):
        return self.preferences.get(key_name, default)

    def set_default(self, key_name, value):
        self.preferences[key_name] = value

    def load_preferences(self, appdata_dir):
        # Fallback to json (Bypass QSettings in web context to avoid PyQt5 segfaults)
        self.prefs_file = os.path.join(appdata_dir, "web_settings.json")
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, "r") as f:
                    saved = json.load(f)
                    self.preferences.update(saved)
            except Exception as e:
                logging.error(f"Failed to load preferences: {e}")

    def save_preferences(self):
        if hasattr(self, "prefs_file"):
            try:
                with open(self.prefs_file, "w") as f:
                    json.dump(self.preferences, f, indent=4)
                logging.info("Preferences successfully saved to web_settings.json.")
            except Exception as e:
                logging.error(f"Failed to save preferences: {e}")

    def show_message(self, msg):
        self.state["messages"].append(msg)
        print(f"[Web UI Message]: {msg}")

    def open_url(self, url):
        pass

    def open_path(self, path):
        pass

    def reveal_path(self, path):
        pass

    def ask_yes_no(self, prompt):
        return True

    def create_results_window(self):
        self.state["status"] = "completed"

    def show_results_window(self):
        self.state["status"] = "completed"

    def show_problem_dialog(self):
        pass

    def select_dest_folder(self, prompt):
        return ""

    def select_dest_file(self, prompt, ext):
        return ""


# Global state
app_state = {
    "status": "idle",  # idle, scanning, completed
    "scanning": False,
    "progress": 0,
    "progress_msg": "",
    "messages": [],
}

# Initialize view adapter first
web_view = WebViewAdapter(app_state)

# Load preferences first to get the CacheURL from web_settings.json
appdata_dir = get_appdata_pure_python()
web_view.load_preferences(appdata_dir)

# Initialize multi-scan task registry
scans_dir = os.path.join(appdata_dir, "scans")
task_registry = ScanTaskRegistry(scans_dir)

# Initialize model with the view (which now has CacheURL populated!)
model = DupeGuru(web_view)

# Bind progress view
progress_view = WebProgressView(app_state)
model.progress_window.view = progress_view


def sync_preferences_to_model():
    model.options["mix_file_kind"] = web_view.get_default("MixFileKind", True)
    model.options["escape_filter_regexp"] = not web_view.get_default("UseRegexp", False)
    model.options["checkpoint_frequency"] = int(web_view.get_default("CheckpointFrequency", 100))
    model.options["clean_empty_dirs"] = web_view.get_default("RemoveEmptyFolders", False)
    model.options["ignore_hardlink_matches"] = web_view.get_default("IgnoreHardlinkMatches", False)
    model.options["min_match_percentage"] = int(web_view.get_default("FilterHardness", 95))
    model.options["rehash_ignore_mtime"] = web_view.get_default("RehashIgnoreMTime", False)
    model.options["include_exists_check"] = web_view.get_default("IncludeExistsCheck", True)
    model.options["scan_type"] = int(web_view.get_default("ScanType", 5))


def save_selected_directories():
    paths = [str(d) for d in model.directories]
    web_view.set_default("SelectedDirectories", paths)
    web_view.save_preferences()


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


def load_selected_directories():
    stored = web_view.get_default("SelectedDirectories")
    if stored and isinstance(stored, list):
        for path_str in stored:
            if safe_path_exists(path_str, timeout=1.0):
                try:
                    from core.directories import AlreadyThereError

                    model.directories.add_path(Path(path_str))
                except AlreadyThereError:
                    pass
                except Exception as e:
                    logging.error(f"Failed to restore directory {path_str}: {e}")


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


def pulse_loop(stop_event):
    """Background loop to pulse the job progress window."""
    has_job_started = False
    wait_ticks = 0
    while not stop_event.is_set():
        if app_state["scanning"]:
            try:
                if model.progress_window._job_running:
                    has_job_started = True
                    wait_ticks = 0
                    model.progress_window.pulse()
                    raw_msg = model.progress_window.progressdesc_textfield.value or "Processing..."
                    app_state["progress_msg"] = sanitize_utf8(raw_msg)
                    app_state["progress"] = model.progress_window.last_progress
                elif has_job_started:
                    has_job_started = False
                    model.progress_window.pulse()
                    app_state["scanning"] = False
                    if app_state.get("status") == "scanning":
                        app_state["status"] = "completed"

                    active_task_id = app_state.get("active_task_id")
                    if active_task_id:
                        task = task_registry.get_task(active_task_id)
                        if task:
                            task.status = ScanTaskStatus.COMPLETED
                            task.completed_at = time.time()
                            task.file_count = model.discarded_file_count
                            task.match_count = len(model.results.groups)
                            task.dupe_count = len(model.results.dupes)
                            task.results_groups = model.results.groups
                else:
                    wait_ticks += 1
                    if wait_ticks > 30:  # 3 seconds fallback
                        app_state["scanning"] = False
                        if app_state.get("status") == "scanning":
                            app_state["status"] = "completed" if model.results.groups else "idle"
                        active_task_id = app_state.get("active_task_id")
                        if active_task_id:
                            task = task_registry.get_task(active_task_id)
                            if task:
                                task.status = ScanTaskStatus.COMPLETED if model.results.groups else ScanTaskStatus.IDLE
                                task.completed_at = time.time()
                                task.file_count = model.discarded_file_count
                                task.match_count = len(model.results.groups)
                                task.dupe_count = len(model.results.dupes)
                                task.results_groups = model.results.groups
            except Exception as e:
                logging.error(f"Error in pulse_loop: {e}")
                app_state["scanning"] = False
                app_state["status"] = "error"
                app_state["error"] = sanitize_utf8(str(e))
        else:
            has_job_started = False
            wait_ticks = 0
        time.sleep(0.1)


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
            targets = [str(d) for d in model.directories]
            active_id = app_state.get("active_task_id")
            if not active_id:
                all_tasks = task_registry.list_tasks()
                if all_tasks:
                    active_id = all_tasks[-1]["task_id"]

            response = {
                "status": app_state["status"],
                "scanning": app_state["scanning"],
                "progress": app_state["progress"],
                "progress_msg": app_state["progress_msg"],
                "messages": app_state["messages"],
                "targets": targets,
                "active_task_id": active_id,
                "has_results": len(model.results.groups) > 0,
            }
            sanitized = sanitize_utf8(response)
            self.wfile.write(json.dumps(sanitized).encode("utf-8", errors="replace"))

        elif path == "/api/config":
            self.wfile.write(json.dumps(web_view.preferences).encode())

        elif path == "/api/scans":
            self.wfile.write(json.dumps(task_registry.list_tasks()).encode())

        elif path.startswith("/api/scans/"):
            task_id = path.replace("/api/scans/", "")
            task = task_registry.get_task(task_id)
            if task:
                self.wfile.write(json.dumps(task.to_dict()).encode())
            else:
                self.wfile.write(json.dumps({"error": "Task not found"}).encode())

        elif path == "/api/directories":
            dirs = []
            for d in model.directories:
                dirs.append({"path": str(d), "state": model.directories.get_state(d)})
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
            try:
                with fs.filesdb.lock:
                    total_count, rows = fs.filesdb.get_cache_viewer_files(search, limit, offset)
                    for row in rows:
                        files_list.append(
                            {
                                "path": row["path"],
                                "size": format_size(row["size"], 0, 1, False) if row["size"] is not None else "0 B",
                                "entry_dt": row["entry_dt"],
                            }
                        )
            except Exception as e:
                logging.error(f"Error querying cache files: {e}")

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
            total_groups = len(model.results.groups)
            batch_groups = model.results.groups[offset : offset + limit]

            for g_idx, g in enumerate(batch_groups):
                files_data = []
                for d in g:
                    display_info = model.get_display_info(d, g, delta=False)
                    files_data.append(
                        {
                            "path": str(d.path),
                            "name": display_info.get("name", d.name),
                            "folder": display_info.get("folder_path", str(d.folder_path)),
                            "size": display_info.get("size", ""),
                            "mtime": display_info.get("mtime", ""),
                            "percentage": display_info.get("percentage", ""),
                            "is_ref": d is g.ref,
                            "marked": model.results.is_marked(d),
                            "markable": model.results.is_markable(d),
                        }
                    )
                groups_data.append(
                    {
                        "id": offset + g_idx,
                        "percentage": g.percentage,
                        "files": files_data,
                    }
                )
            total_marked = sum(1 for d in model.results.dupes if model.results.is_marked(d))
            response_data = {
                "success": True,
                "groups": groups_data,
                "total": total_groups,
                "total_marked": total_marked,
                "limit": limit,
                "offset": offset,
            }
            self.wfile.write(json.dumps(response_data).encode())

    def do_POST(self):
        path = self.path
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode()
        data = json.loads(post_data) if post_data else {}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if path == "/api/config":
            for k, v in data.items():
                if k in web_view.preferences:
                    if isinstance(web_view.preferences[k], bool):
                        web_view.preferences[k] = bool(v)
                    elif isinstance(web_view.preferences[k], int):
                        web_view.preferences[k] = int(v)
                    else:
                        web_view.preferences[k] = v
            web_view.save_preferences()
            sync_preferences_to_model()
            self.wfile.write(json.dumps({"success": True, "config": web_view.preferences}).encode())

        elif path == "/api/scans/create":
            name = data.get("name", "Scan").strip() or f"Scan_{time.strftime('%Y%m%d_%H%M%S')}"
            directories_list = data.get("directories", [])
            if not directories_list and model.directories:
                directories_list = [str(d) for d in model.directories]

            if not directories_list:
                self.wfile.write(
                    json.dumps(sanitize_utf8({"success": False, "error": "No directory path specified"})).encode()
                )
                return

            # Clear existing model directories and set target paths
            model.directories.clear()
            for d_path in directories_list:
                try:
                    from core.directories import AlreadyThereError

                    model.directories.add_path(Path(d_path))
                except AlreadyThereError:
                    pass
                except Exception as e:
                    logging.warning(f"Error adding path {d_path}: {e}")

            save_selected_directories()

            overwrite = data.get("overwrite", False)
            existing_task = task_registry.get_task_by_name(name)
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

            task = task_registry.create_task(name, directories_list, overwrite=overwrite)
            app_state["active_task_id"] = task.task_id

            def run_scan_async():
                task.status = ScanTaskStatus.RUNNING
                try:
                    print(
                        f"[Web Server] Starting scan thread for task '{name}' on DB '{task.db_path}'...",
                        flush=True,
                    )
                    fs.filesdb.connect(task.db_path)
                    fs.filesdb.enable_directory_cache = True
                    print("[Web Server] Launching duplicate scan engine...", flush=True)
                    model.start_scanning()
                    print("[Web Server] Scan engine execution completed.", flush=True)

                    task.status = ScanTaskStatus.COMPLETED
                    task.completed_at = time.time()
                    task.file_count = model.discarded_file_count
                    task.match_count = len(model.results.groups)
                    task.dupe_count = len(model.results.dupes)
                    task.results_groups = model.results.groups

                    if not model.progress_window._job_running:
                        app_state["scanning"] = False
                        if app_state.get("status") == "scanning":
                            app_state["status"] = "completed" if model.results.groups else "idle"
                except Exception as e:
                    print(f"[Web Server ERROR] Scan thread failed: {e}", flush=True)
                    logging.error(f"Error in run_scan_async: {e}", exc_info=True)
                    task.status = ScanTaskStatus.FAILED
                    task.error_message = str(e)
                    app_state["scanning"] = False
                    app_state["status"] = "error"
                    app_state["error"] = str(e)

            app_state["status"] = "scanning"
            app_state["scanning"] = True
            app_state["progress"] = 0
            app_state["progress_msg"] = f"Starting scan for '{name}'..."

            scan_thread = threading.Thread(target=run_scan_async, daemon=True)
            task._thread = scan_thread
            scan_thread.start()

            self.wfile.write(json.dumps(sanitize_utf8({"success": True, "task": task.to_dict()})).encode())

        elif path == "/api/scans/load":
            task_id = data.get("task_id")
            task = task_registry.get_task(task_id)
            if task and os.path.exists(task.db_path):
                try:
                    fs.filesdb.connect(task.db_path)
                    fs.filesdb.enable_directory_cache = True
                    app_state["active_task_id"] = task.task_id

                    if not task.directories:
                        try:
                            import sqlite3

                            conn = sqlite3.connect(task.db_path)
                            cur = conn.cursor()
                            cur.execute("SELECT path FROM scanned_directories")
                            task.directories = [r[0] for r in cur.fetchall()]
                            conn.close()
                        except Exception:
                            pass

                    if hasattr(task, "results_groups") and task.results_groups is not None:
                        model.results.groups = task.results_groups
                        model._recreate_result_table()
                    else:
                        model.directories.clear()
                        for d in task.directories:
                            try:
                                model.directories.add_path(Path(d))
                            except Exception:
                                pass
                        model.start_scanning()
                        start_wait = time.time()
                        while model.progress_window._job_running and (time.time() - start_wait < 10.0):
                            time.sleep(0.05)
                        try:
                            if fs.filesdb and fs.filesdb.conn:
                                fs.filesdb.conn.commit()
                        except Exception:
                            pass
                        task.results_groups = model.results.groups

                    self.wfile.write(json.dumps(sanitize_utf8({"success": True, "task": task.to_dict()})).encode())
                except Exception as e:
                    self.wfile.write(json.dumps(sanitize_utf8({"success": False, "error": str(e)})).encode())
            else:
                self.wfile.write(
                    json.dumps(sanitize_utf8({"success": False, "error": "Database task not found"})).encode()
                )

        elif path == "/api/scans/delete":
            task_id = data.get("task_id")
            deleted = task_registry.delete_task(task_id, delete_db_file=True)
            self.wfile.write(json.dumps(sanitize_utf8({"success": deleted})).encode())

        elif path == "/api/cross_scan":
            db_paths = data.get("db_paths", [])
            if not db_paths:
                db_paths = [t["db_path"] for t in task_registry.list_tasks()]

            try:
                from core.cross_db import CrossDBMatcher

                matcher = CrossDBMatcher(db_paths)
                results = matcher.find_cross_duplicates()
                self.wfile.write(
                    json.dumps({"success": True, "groups": results, "total_groups": len(results)}).encode()
                )
            except Exception as e:
                logging.error(f"Error in cross_scan endpoint: {e}")
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

        elif path == "/api/directories":
            path_str = data.get("path")
            if path_str:
                path_str = path_str.strip().strip("'\"")
                try:
                    from core.directories import AlreadyThereError, InvalidPathError

                    model.directories.add_path(Path(path_str))
                    save_selected_directories()
                    self.wfile.write(json.dumps({"success": True}).encode())
                except AlreadyThereError:
                    self.wfile.write(
                        json.dumps({"success": False, "error": "Directory is already in the list"}).encode()
                    )
                except InvalidPathError:
                    import traceback

                    print(
                        f"InvalidPathError: path_str={repr(path_str)} "
                        f"exists={os.path.exists(path_str)} "
                        f"isdir={os.path.isdir(path_str)}"
                    )
                    traceback.print_exc()
                    self.wfile.write(json.dumps({"success": False, "error": "Invalid or non-existent path"}).encode())
                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Invalid path"}).encode())

        elif path == "/api/scan":
            if not model.progress_window._job_running:
                app_state["scanning"] = False
                app_state["status"] = "idle"

            if not app_state["scanning"]:
                if model.progress_window._job_running:
                    self.wfile.write(
                        json.dumps(
                            {
                                "success": False,
                                "error": "Previous job still running. Please wait a few seconds.",
                            }
                        ).encode()
                    )
                    return

                if not model.directories or len(model.directories) == 0:
                    self.wfile.write(
                        json.dumps({"success": False, "error": "No directories selected to scan."}).encode()
                    )
                    return

                clear_cache_requested = data.get("clear_cache", False)
                scan_name = data.get("name", "").strip() or f"Scan_{time.strftime('%Y%m%d_%H%M%S')}"
                directories_list = [str(d) for d in model.directories]

                # Create task in registry for tracking
                task = task_registry.create_task(scan_name, directories_list)
                app_state["active_task_id"] = task.task_id

                def run_scan_async():
                    task.status = ScanTaskStatus.RUNNING
                    try:
                        print(
                            f"[Web Server] Starting scan thread for task '{scan_name}' on DB '{task.db_path}'...",
                            flush=True,
                        )
                        fs.filesdb.connect(task.db_path)
                        if clear_cache_requested:
                            print("[Web Server] Clearing database hash cache...", flush=True)
                            t0 = time.time()
                            model.clear_hash_cache()
                            print(
                                f"[Web Server] Database cache cleared in {(time.time() - t0) * 1000:.2f} ms.",
                                flush=True,
                            )
                        fs.filesdb.enable_directory_cache = True
                        print("[Web Server] Launching duplicate scan engine...", flush=True)
                        model.start_scanning()
                        print("[Web Server] Scan engine execution completed.", flush=True)

                        task.status = ScanTaskStatus.COMPLETED
                        task.completed_at = time.time()
                        task.file_count = model.discarded_file_count
                        task.match_count = len(model.results.groups)
                        task.dupe_count = len(model.results.dupes)

                        # If background job finished immediately (e.g. no files or quick scan)
                        if not model.progress_window._job_running:
                            app_state["scanning"] = False
                            if app_state.get("status") == "scanning":
                                app_state["status"] = "completed" if model.results.groups else "idle"
                    except Exception as e:
                        print(f"[Web Server ERROR] Scan thread failed: {e}", flush=True)
                        logging.error(f"Error in run_scan_async: {e}", exc_info=True)
                        task.status = ScanTaskStatus.FAILED
                        task.error_message = str(e)
                        app_state["scanning"] = False
                        app_state["status"] = "error"
                        app_state["error"] = str(e)

                app_state["status"] = "scanning"
                app_state["scanning"] = True
                app_state["progress"] = 0
                app_state["progress_msg"] = "Starting scan..."

                scan_thread = threading.Thread(target=run_scan_async, daemon=True)
                task._thread = scan_thread
                scan_thread.start()

                self.wfile.write(json.dumps({"success": True, "task_id": task.task_id}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Scan in progress"}).encode())

        elif path == "/api/scan/cancel":
            scanned_count = len(fs.filesdb.scanned_paths)
            reused_count = len(fs.filesdb.hit_paths - fs.filesdb.scanned_paths)
            last_file = fs.filesdb.last_scanned_path
            model.progress_window.cancel()
            self.wfile.write(
                json.dumps(
                    {
                        "success": True,
                        "scanned_count": scanned_count,
                        "reused_count": reused_count,
                        "last_file": last_file,
                    }
                ).encode()
            )

        elif path == "/api/results/mark":
            file_path = data.get("path")
            marked = data.get("marked", False)
            # Find the duplicate file in the results
            found = False
            for group in model.results.groups:
                for file_entry in group:
                    if str(file_entry.path) == file_path:
                        model.results.set_marked(file_entry, marked)
                        found = True
                if found:
                    break
            total_marked = sum(1 for d in model.results.dupes if model.results.is_marked(d))
            self.wfile.write(json.dumps({"success": found, "total_marked": total_marked}).encode())

        elif path == "/api/results/delete":
            # Direct delete or send to trash depending on backend
            # We bypass the Qt deletion dialog and run the delete job directly
            args = [
                False,  # link_deleted
                False,  # use_hardlinks
                True,  # direct delete (no trash dialog required)
            ]
            model._start_job(model.JobType.DELETE, model._do_delete, args=args)
            self.wfile.write(json.dumps({"success": True}).encode())

        elif path == "/api/results/save":
            filename = data.get("path")
            if app_state["status"] != "completed":
                self.wfile.write(
                    json.dumps(
                        {
                            "success": False,
                            "error": "No scan results available to save. Run a scan to completion first.",
                        }
                    ).encode()
                )
            elif filename:
                try:
                    model.save_as(filename)
                    self.wfile.write(json.dumps({"success": True}).encode())
                except Exception as e:
                    self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Missing filename"}).encode())

        elif path == "/api/results/load":
            filename = data.get("path")
            if filename and os.path.exists(filename):
                try:
                    model.load_from(filename)
                    app_state["status"] = "completed"
                    self.wfile.write(json.dumps({"success": True}).encode())
                except Exception as e:
                    self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Invalid or missing file"}).encode())

    def do_DELETE(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if path == "/api/directories":
            index = int(query.get("index", [-1])[0])
            if 0 <= index < len(model.directories):
                del model.directories[index]
                save_selected_directories()
                self.wfile.write(json.dumps({"success": True}).encode())
            else:
                self.wfile.write(json.dumps({"success": False, "error": "Invalid index"}).encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_server(port=8080):
    # Ensure locales and other config directories exist
    locale_folder = PROJECT_ROOT / "locale"
    import locale as py_locale

    try:
        lang = py_locale.getlocale()[0] or py_locale.getdefaultlocale()[0]
        lang = lang[:2] if lang else "en"
    except Exception:
        lang = "en"
    install_gettext_trans(str(locale_folder), lang)

    server = ThreadedHTTPServer(("localhost", port), DupeGuruHTTPHandler)
    print(f"Starting de-dup HTML Web Server on http://localhost:{port}", flush=True)

    # Restore selected directories asynchronously in background so server binds immediately
    restore_thread = threading.Thread(target=load_selected_directories, daemon=True)
    restore_thread.start()

    stop_event = threading.Event()
    pulse_thread = threading.Thread(target=pulse_loop, args=(stop_event,), daemon=True)
    pulse_thread.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        pulse_thread.join(timeout=1.0)
        server.server_close()
        print("Server stopped.", flush=True)


if __name__ == "__main__":
    start_server()
