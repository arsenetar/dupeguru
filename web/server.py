import json
import logging
import os
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtCore import QCoreApplication  # noqa: E402

if not QCoreApplication.instance():
    _qapp = QCoreApplication([])
QCoreApplication.setApplicationName("dupeGuru")
QCoreApplication.setOrganizationName("dupeGuru")

from core.app import DupeGuru  # noqa: E402
from core import fs  # noqa: E402
from hscommon.trans import install_gettext_trans_under_qt  # noqa: E402


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
        # Try loading from QSettings (shared with Qt UI)
        try:
            from qt.util import create_qsettings

            settings = create_qsettings()
            for key in self.preferences.keys():
                val = settings.value(key)
                if val is not None:
                    if val == "true" or val is True:
                        self.preferences[key] = True
                    elif val == "false" or val is False:
                        self.preferences[key] = False
                    elif str(val).isdigit():
                        self.preferences[key] = int(val)
                    else:
                        self.preferences[key] = val
            logging.info("Preferences successfully loaded from QSettings (shared with Qt UI).")
            return
        except Exception as e:
            logging.warning(f"Could not load preferences from QSettings: {e}. Falling back to web_settings.json.")

        self.prefs_file = os.path.join(appdata_dir, "web_settings.json")
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, "r") as f:
                    saved = json.load(f)
                    self.preferences.update(saved)
            except Exception as e:
                logging.error(f"Failed to load preferences: {e}")

    def save_preferences(self):
        # Try saving to QSettings (shared with Qt UI)
        try:
            from qt.util import create_qsettings

            settings = create_qsettings()
            for key, val in self.preferences.items():
                settings.setValue(key, val)
            settings.sync()
            logging.info("Preferences successfully saved to QSettings (shared with Qt UI).")
            return
        except Exception as e:
            logging.warning(f"Could not save preferences to QSettings: {e}. Falling back to web_settings.json.")

        if hasattr(self, "prefs_file"):
            try:
                with open(self.prefs_file, "w") as f:
                    json.dump(self.preferences, f, indent=4)
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

# Initialize model with the view
model = DupeGuru(web_view)

# Bind progress view
progress_view = WebProgressView(app_state)
model.progress_window.view = progress_view

# Load and synchronize configuration
web_view.load_preferences(model.appdata)


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


sync_preferences_to_model()


def save_selected_directories():
    paths = [str(d) for d in model.directories]
    web_view.set_default("SelectedDirectories", paths)
    web_view.save_preferences()


def load_selected_directories():
    stored = web_view.get_default("SelectedDirectories")
    if stored and isinstance(stored, list):
        for path_str in stored:
            if os.path.exists(path_str):
                try:
                    from core.directories import AlreadyThereError

                    model.directories.add_path(Path(path_str))
                except AlreadyThereError:
                    pass
                except Exception as e:
                    logging.error(f"Failed to restore directory {path_str}: {e}")


load_selected_directories()

# Setup basic logging
logging.basicConfig(level=logging.INFO)


def pulse_loop(stop_event):
    """Background loop to pulse the job progress window."""
    while not stop_event.is_set():
        if app_state["scanning"]:
            model.progress_window.pulse()
            app_state["progress_msg"] = model.progress_window.progressdesc_textfield.value or "Processing..."
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
            response = {
                "status": app_state["status"],
                "scanning": app_state["scanning"],
                "progress": app_state["progress"],
                "progress_msg": app_state["progress_msg"],
                "messages": app_state["messages"],
                "targets": targets,
            }
            self.wfile.write(json.dumps(response).encode())

        elif path == "/api/config":
            self.wfile.write(json.dumps(web_view.preferences).encode())

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
                for entry in p.iterdir():
                    if entry.is_dir() and not entry.name.startswith("."):
                        contents.append({"name": entry.name, "path": str(entry)})
                contents.sort(key=lambda x: x["name"].lower())
                self.wfile.write(
                    json.dumps(
                        {
                            "current": str(p),
                            "parent": str(p.parent) if p.parent != p else None,
                            "folders": contents,
                        }
                    ).encode()
                )
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif path == "/api/results":
            groups_data = []
            for g_idx, g in enumerate(model.results.groups):
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
                        "id": g_idx,
                        "percentage": g.percentage,
                        "files": files_data,
                    }
                )
            self.wfile.write(json.dumps(groups_data).encode())

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
            if not app_state["scanning"]:
                if not model.directories.has_any_file():
                    self.wfile.write(
                        json.dumps(
                            {"success": False, "error": "The selected directories contain no scannable file."}
                        ).encode()
                    )
                    return

                # Clear cache if requested
                if data.get("clear_cache", False):
                    model.clear_hash_cache()

                app_state["status"] = "scanning"
                app_state["scanning"] = True
                app_state["progress"] = 0
                app_state["progress_msg"] = "Starting scan..."
                # Run scan in model (which handles threads itself)
                model.start_scanning()
                self.wfile.write(json.dumps({"success": True}).encode())
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
                        break
                if found:
                    break
            self.wfile.write(json.dumps({"success": found}).encode())

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


def start_server(port=8080):
    # Ensure locales and other config directories exist
    locale_folder = PROJECT_ROOT / "locale"
    install_gettext_trans_under_qt(str(locale_folder), "")

    server = HTTPServer(("localhost", port), DupeGuruHTTPHandler)
    print(f"Starting dupeGuru HTML Web Server on http://localhost:{port}")

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
        print("Server stopped.")


if __name__ == "__main__":
    start_server()
