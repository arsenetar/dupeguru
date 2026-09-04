# Unit tests for Phase 5 Database Verification, Validation, and Compatibility

import os
import tempfile
import unittest
from core.storage.db_engine import DBEngine
from core.storage.db_verifier import DBVerifier


class TestPhase5DBVerification(unittest.TestCase):
    def test_database_verification_new_db(self):
        engine = DBEngine(":memory:")
        engine.init_schema()

        verifier = DBVerifier(engine)
        res = verifier.verify_database()

        self.assertTrue(res.is_valid)
        self.assertTrue(res.quick_check_ok)
        self.assertIn("files", res.tables_present)
        self.assertIn("scan_metadata", res.tables_present)
        self.assertEqual(len(res.errors), 0)

    def test_database_repair_missing_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "corrupt.db")
            engine = DBEngine(db_path)
            conn = engine.get_connection()
            conn.execute("CREATE TABLE files (path TEXT PRIMARY KEY, size INTEGER);")
            conn.commit()

            verifier = DBVerifier(engine)
            res = verifier.verify_database()

            # Should auto-repair missing tables and pass validation
            self.assertTrue(res.is_valid)
            self.assertTrue(res.repaired)

    def test_real_scan_databases_verification(self):
        scans_dir = os.path.expanduser("~/.local/share/de-dup/scans")
        if not os.path.exists(scans_dir):
            self.skipTest("No local scans directory found.")

        db_files = [os.path.join(scans_dir, f) for f in os.listdir(scans_dir) if f.endswith(".db")]
        if not db_files:
            self.skipTest("No .db scan files found.")

        for db_p in db_files:
            engine = DBEngine(db_p)
            verifier = DBVerifier(engine)
            res = verifier.verify_database()

            self.assertTrue(res.is_valid, f"Verification failed for database {db_p}: {res.errors}")
            self.assertTrue(res.quick_check_ok, f"Integrity check failed for database {db_p}")


if __name__ == "__main__":
    unittest.main()
