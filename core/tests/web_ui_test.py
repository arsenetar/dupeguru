# Unit tests for Web UI Frontend, JavaScript Syntax, HTML DOM Integrity, and Server Endpoints

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
import unittest

from web.server import DupeGuruHTTPHandler, ThreadedHTTPServer


class TestWebUIIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.js_file = os.path.join(cls.project_root, "web", "static", "app.js")
        cls.html_file = os.path.join(cls.project_root, "web", "static", "index.html")
        cls.css_file = os.path.join(cls.project_root, "web", "static", "app.css")

    def test_javascript_syntax_integrity(self):
        """Verifies that web/static/app.js contains no syntax errors using node --check or Python parser."""
        self.assertTrue(os.path.exists(self.js_file), f"JS file missing at {self.js_file}")

        node_cmd = shutil.which("node")
        if node_cmd:
            res = subprocess.run([node_cmd, "--check", self.js_file], capture_output=True, text=True)
            self.assertEqual(
                res.returncode,
                0,
                f"JavaScript syntax error found in app.js:\n{res.stderr}",
            )

        with open(self.js_file, "r", encoding="utf-8") as f:
            js_text = f.read()

        # Structural check for balanced curly braces and brackets
        open_braces = js_text.count("{")
        close_braces = js_text.count("}")
        self.assertEqual(
            open_braces,
            close_braces,
            f"Unbalanced curly braces in app.js: {open_braces} '{{' vs {close_braces} '}}'",
        )

        open_parens = js_text.count("(")
        close_parens = js_text.count(")")
        self.assertEqual(
            open_parens,
            close_parens,
            f"Unbalanced parentheses in app.js: {open_parens} '(' vs {close_parens} ')'",
        )

    def test_html_dom_id_alignment(self):
        """Verifies that all document.getElementById references in app.js exist in index.html."""
        with open(self.js_file, "r", encoding="utf-8") as f:
            js_text = f.read()
        with open(self.html_file, "r", encoding="utf-8") as f:
            html_text = f.read()

        js_ids = set(re.findall(r'getElementById\s*\(\s*["\']([^"\']+)["\']\s*\)', js_text))
        html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html_text))

        missing_ids = js_ids - html_ids
        self.assertEqual(
            len(missing_ids),
            0,
            f"The following element IDs referenced in app.js are missing in index.html: {missing_ids}",
        )

    def test_static_asset_existence(self):
        """Verifies that all static web console assets exist and are non-empty."""
        self.assertTrue(os.path.exists(self.js_file))
        self.assertGreater(os.path.getsize(self.js_file), 1000)

        self.assertTrue(os.path.exists(self.html_file))
        self.assertGreater(os.path.getsize(self.html_file), 1000)

        self.assertTrue(os.path.exists(self.css_file))
        self.assertGreater(os.path.getsize(self.css_file), 1000)


class TestWebServerEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.server = ThreadedHTTPServer(("127.0.0.1", 0), DupeGuruHTTPHandler)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        import threading

        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_server_static_file_endpoints(self):
        """Tests that HTTP GET requests serve index.html, app.css, and app.js correctly."""
        with urllib.request.urlopen(f"{self.base_url}/") as response:
            self.assertEqual(response.status, 200)
            content = response.read().decode("utf-8")
            self.assertIn("<title>de-dup Web Console</title>", content)

        with urllib.request.urlopen(f"{self.base_url}/static/app.css") as response:
            self.assertEqual(response.status, 200)
            self.assertIn("text/css", response.headers.get("Content-Type", ""))

        with urllib.request.urlopen(f"{self.base_url}/static/app.js") as response:
            self.assertEqual(response.status, 200)
            self.assertIn("javascript", response.headers.get("Content-Type", "").lower())

    def test_server_rest_api_status_and_scans(self):
        """Tests REST API status and multi-scan endpoints."""
        with urllib.request.urlopen(f"{self.base_url}/api/status") as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertIn("status", data)
            self.assertIn("scanning", data)
            self.assertIn("active_task_id", data)

        with urllib.request.urlopen(f"{self.base_url}/api/scans") as response:
            self.assertEqual(response.status, 200)
            tasks = json.loads(response.read().decode("utf-8"))
            self.assertIsInstance(tasks, list)

    def test_server_rest_api_directories_and_browse(self):
        """Tests directory adding, browsing, and clearing REST endpoints."""
        req_post = urllib.request.Request(
            f"{self.base_url}/api/directories",
            data=json.dumps({"path": self.temp_dir}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_post) as response:
            self.assertEqual(response.status, 200)
            dirs = json.loads(response.read().decode("utf-8"))
            self.assertTrue(any(d["path"] == self.temp_dir for d in dirs))

        browse_url = f"{self.base_url}/api/browse?path={urllib.parse.quote(self.temp_dir)}"
        with urllib.request.urlopen(browse_url) as response:
            self.assertEqual(response.status, 200)
            browse_data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(browse_data.get("current"), self.temp_dir)

        req_del = urllib.request.Request(
            f"{self.base_url}/api/directories?clear_all=true",
            method="DELETE",
        )
        with urllib.request.urlopen(req_del) as response:
            self.assertEqual(response.status, 200)
            result = json.loads(response.read().decode("utf-8"))
            self.assertIsInstance(result, list)

    def test_server_rest_api_results_delete_with_payload(self):
        """Tests POST /api/results/delete with marked file paths deletes files on disk and updates task state."""
        dummy_file = os.path.join(self.temp_dir, "dummy_dupe.tmp")
        with open(dummy_file, "w") as f:
            f.write("duplicate content")

        self.assertTrue(os.path.exists(dummy_file))

        req_post = urllib.request.Request(
            f"{self.base_url}/api/results/delete",
            data=json.dumps({"task_id": "test_task", "paths": [dummy_file]}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_post) as response:
            self.assertEqual(response.status, 200)
            res = json.loads(response.read().decode("utf-8"))
            self.assertTrue(res.get("success"))
            self.assertEqual(res.get("deleted_count"), 1)

        time.sleep(0.2)
        self.assertFalse(os.path.exists(dummy_file))

    def test_server_rest_api_cache_files_endpoint(self):
        """Tests GET /api/cache/files executes valid SQL without file_mtime column errors."""
        cache_url = f"{self.base_url}/api/cache/files?search=&limit=20&offset=0"
        with urllib.request.urlopen(cache_url) as response:
            self.assertEqual(response.status, 200)
            res = json.loads(response.read().decode("utf-8"))
            self.assertTrue(res.get("success"))
            self.assertIsInstance(res.get("files"), list)

    def test_server_state_thread_safety_and_path_normalization(self):
        """Verifies ServerState normalizes trailing slashes and deduplicates targets."""
        from web.server import server_state

        server_state.clear_directories()
        server_state.add_directory("/path/to/dir/")
        server_state.add_directory("/path/to/dir")
        dirs = server_state.get_directories()
        self.assertEqual(len(dirs), 1)
        self.assertEqual(dirs[0], "/path/to/dir")

        server_state.set("active_task_id", "test_id_123")
        self.assertEqual(server_state.get("active_task_id"), "test_id_123")
        self.assertEqual(server_state["active_task_id"], "test_id_123")

    def test_server_rest_api_cross_scan_endpoint(self):
        """Verifies POST /api/cross_scan reports cross_matching state and returns paginated matches."""
        req_post = urllib.request.Request(
            f"{self.base_url}/api/cross_scan",
            data=json.dumps({"db_paths": [], "limit": 10, "offset": 0}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_post) as response:
            self.assertEqual(response.status, 200)
            res = json.loads(response.read().decode("utf-8"))
            self.assertTrue(res.get("success"))
            self.assertIn("groups", res)
            self.assertIn("total_groups", res)


if __name__ == "__main__":
    unittest.main()
