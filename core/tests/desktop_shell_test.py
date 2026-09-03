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

    def test_desktop_bridge_api(self):
        from run_desktop import DesktopBridgeAPI

        app = DesktopApp()
        bridge = DesktopBridgeAPI(app)

        sys_info = bridge.get_system_info()
        self.assertIn("appname", sys_info)
        self.assertIn("version", sys_info)
        self.assertIn("system", sys_info)

        # When window is None (headless/test mode), folder dialog returns None/empty list safely
        self.assertIsNone(bridge.select_folder())
        self.assertEqual(bridge.select_multiple_folders(), [])


if __name__ == "__main__":
    unittest.main()
