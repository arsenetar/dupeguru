# Unit tests for Phase 2 Pipeline Modules (Discovery, Hasher, Matcher)

import os
import tempfile
import unittest
from core.domain.models import FileDTO
from core.pipeline.discovery import FileDiscovery
from core.pipeline.hasher import ContentHasher, calc_partial_hash, calc_full_hash
from core.pipeline.matcher import DuplicateMatcher
from core.storage.db_engine import DBEngine


class TestPhase2Pipeline(unittest.TestCase):
    def test_file_discovery_and_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            f1 = os.path.join(temp_dir, "file1.txt")
            f2 = os.path.join(temp_dir, "file2.txt")

            with open(f1, "w") as fp:
                fp.write("Hello World 1")
            with open(f2, "w") as fp:
                fp.write("Hello World 2")

            engine = DBEngine(":memory:")
            discovery = FileDiscovery(engine)

            files = discovery.collect_files([temp_dir], enable_cache=False)
            self.assertEqual(len(files), 2)

            # Test reading directly from cache
            cached_files = discovery.collect_files([temp_dir], enable_cache=True)
            self.assertEqual(len(cached_files), 2)

    def test_content_hasher(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            f1 = os.path.join(temp_dir, "file1.txt")
            with open(f1, "wb") as fp:
                fp.write(b"Same Content Data")

            p_hash = calc_partial_hash(f1)
            f_hash = calc_full_hash(f1)
            self.assertIsNotNone(p_hash)
            self.assertIsNotNone(f_hash)

            engine = DBEngine(":memory:")
            engine.init_schema()

            dto = FileDTO(path=f1, size=len(b"Same Content Data"))
            hasher = ContentHasher(engine)
            hashed_dtos = hasher.hash_candidate_files([dto])
            self.assertEqual(len(hashed_dtos), 1)
            self.assertIsNotNone(hashed_dtos[0].digest_partial)

    def test_duplicate_matcher_synthetic_dtos(self):
        engine = DBEngine(":memory:")
        engine.init_schema()

        # Insert candidate files directly into database
        with engine.transaction() as conn:
            conn.execute(
                "INSERT INTO files (path, size, mtime_ns, digest_partial, digest) VALUES (?, ?, ?, ?, ?)",
                ("/tmp/fileA.txt", 1000, 100, b"hash_p1", b"hash_f1"),
            )
            conn.execute(
                "INSERT INTO files (path, size, mtime_ns, digest_partial, digest) VALUES (?, ?, ?, ?, ?)",
                ("/tmp/fileB.txt", 1000, 100, b"hash_p1", b"hash_f1"),
            )
            conn.execute(
                "INSERT INTO files (path, size, mtime_ns, digest_partial, digest) VALUES (?, ?, ?, ?, ?)",
                ("/tmp/fileC.txt", 500, 100, b"hash_p2", b"hash_f2"),
            )

        matcher = DuplicateMatcher(engine)
        groups = matcher.find_duplicates()

        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group.pivot.path, "/tmp/fileA.txt")
        self.assertEqual(len(group.duplicates), 1)
        self.assertEqual(group.duplicates[0].path, "/tmp/fileB.txt")
        self.assertEqual(group.saved_bytes, 1000)


if __name__ == "__main__":
    unittest.main()
