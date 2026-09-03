# Unit tests for pywebview desktop shell and port resolution

import unittest
from run_desktop import DesktopApp, find_available_port


class TestDesktopShell(unittest.TestCase):
    def test_find_available_port(self):
        port = find_available_port(start_port=18000)
        self.assertIsInstance(port, int)
        self.assertGreaterEqual(port, 18000)

    def test_desktop_app_backend_lifecycle(self):
        port = find_available_port(start_port=18500)
        app = DesktopApp(port=port)
        try:
            app.start_backend()
            self.assertIsNotNone(app.server)
            self.assertTrue(app.server_thread.is_alive())
        finally:
            app.stop_backend()


if __name__ == "__main__":
    unittest.main()
