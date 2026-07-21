#!/usr/bin/env python3
"""
dupeGuru Web Console Entrypoint
Launches the HTTP web server and automatically opens the user's browser.
"""

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Insert project directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from web.server import start_server  # noqa: E402


def open_browser(url):
    """Wait for server to boot and open default web browser."""
    time.sleep(1.0)
    print(f"Opening web browser at {url}...", flush=True)
    webbrowser.open(url)


def main():
    parser = argparse.ArgumentParser(description="Start the dupeGuru HTML Web interface.")
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the local HTTP web server on (default: 8080)",
    )
    args = parser.parse_args()

    url = f"http://localhost:{args.port}"

    # Spawn browser launcher in a daemon thread so it doesn't block the server boot
    launcher_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
    launcher_thread.start()

    # Start HTTPServer (blocks until KeyboardInterrupt)
    start_server(port=args.port)


if __name__ == "__main__":
    main()
