#!/usr/bin/env python3
"""
de-dup Desktop Application (pywebview Native Shell)
Launches the background HTTP engine and displays the HTML/CSS/JS UI inside
a lightweight native desktop window across macOS, Windows 11, and Linux.
Provides native file dialogs and OS desktop integrations via pywebview JS-API.
"""

import argparse
import os
import socket
import sys
import threading
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure PyQt5 does not initialize
sys.modules["PyQt5"] = None
sys.modules["PyQt5.QtCore"] = None
sys.modules["PyQt5.QtGui"] = None
sys.modules["PyQt5.QtWidgets"] = None

from core import __appname__, __version__  # noqa: E402
from hscommon.desktop import open_path, reveal_path  # noqa: E402
from web.server import ThreadedHTTPServer, DupeGuruHTTPHandler  # noqa: E402


def find_available_port(start_port=8080):
    """Find an open TCP port on localhost starting at start_port."""
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
            port += 1
    return start_port


class DesktopBridgeAPI:
    """JS-to-Python Native Bridge exposed to frontend via window.pywebview.api."""

    def __init__(self, app):
        self.app = app

    def select_folder(self, initial_dir=None):
        """Open native OS folder selection dialog."""
        import webview

        if not self.app.window:
            return None
        res = self.app.window.create_file_dialog(
            webview.FOLDER_DIALOG,
            directory=initial_dir or os.path.expanduser("~"),
            allow_multiple=False,
        )
        if res and len(res) > 0:
            return res[0]
        return None

    def select_multiple_folders(self, initial_dir=None):
        """Open native OS multiple folder selection dialog."""
        import webview

        if not self.app.window:
            return []
        res = self.app.window.create_file_dialog(
            webview.FOLDER_DIALOG,
            directory=initial_dir or os.path.expanduser("~"),
            allow_multiple=True,
        )
        return list(res) if res else []

    def reveal_in_file_manager(self, path):
        """Open folder and highlight file in native file browser (Explorer/Finder/Nautilus)."""
        reveal_path(path)
        return True

    def open_in_default_app(self, path):
        """Open file using system default application."""
        open_path(path)
        return True

    def get_system_info(self):
        """Return runtime platform information."""
        import platform

        return {
            "appname": __appname__,
            "version": __version__,
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        }


class DesktopApp:
    """Desktop shell embedding the de-dup web console using native OS WebViews."""

    def __init__(self, port=None, width=1280, height=850, debug=False):
        self.port = port or find_available_port()
        self.width = width
        self.height = height
        self.debug = debug
        self.server = None
        self.server_thread = None
        self.window = None
        self.api = DesktopBridgeAPI(self)

    def start_backend(self):
        """Starts the backend HTTP server in a daemon thread."""
        self.server = ThreadedHTTPServer(("127.0.0.1", self.port), DupeGuruHTTPHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

    def stop_backend(self):
        """Stops the backend HTTP server."""
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass

    def run(self):
        """Launches backend and opens native desktop window."""
        self.start_backend()
        url = f"http://127.0.0.1:{self.port}"

        try:
            import webview

            self.window = webview.create_window(
                title=f"{__appname__} v{__version__}",
                url=url,
                js_api=self.api,
                width=self.width,
                height=self.height,
                min_size=(900, 600),
                text_select=True,
                confirm_close=False,
            )

            # webview.start is blocking and runs the OS native window message loop
            webview.start(debug=self.debug)
        except ImportError as e:
            print(f"pywebview is not installed or GUI backend unavailable: {e}", file=sys.stderr)
            print(f"Falling back to external browser at {url}...", file=sys.stderr)
            import webbrowser

            webbrowser.open(url)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        finally:
            self.stop_backend()


def main():
    parser = argparse.ArgumentParser(description="de-dup native desktop application (pywebview).")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Custom port for internal web server (default: auto-detect)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable WebView developer tools / inspection",
    )
    args = parser.parse_args()

    app = DesktopApp(port=args.port, debug=args.debug)
    app.run()


if __name__ == "__main__":
    main()
