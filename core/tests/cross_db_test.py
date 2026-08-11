import os
import sqlite3
import tempfile

from core.cross_db import CrossDBMatcher


def create_mock_db(db_path, files):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE files (path TEXT PRIMARY KEY, size INTEGER, mtime_ns INTEGER, "
        "entry_dt DATETIME, digest BLOB, digest_partial BLOB, digest_samples BLOB)"
    )
    for path, size, mtime, digest in files:
        conn.execute(
            "INSERT INTO files (path, size, mtime_ns, entry_dt, digest) VALUES (?, ?, ?, datetime('now'), ?)",
            (path, size, mtime, digest),
        )
    conn.commit()
    conn.close()


def test_cross_db_matcher():
    with tempfile.TemporaryDirectory() as tmpdir:
        db1_path = os.path.join(tmpdir, "db1.db")
        db2_path = os.path.join(tmpdir, "db2.db")

        # DB 1 files
        create_mock_db(
            db1_path,
            [
                ("/photos/file1.jpg", 1024, 1600000000000, b"hash_abc"),
                ("/photos/unique1.jpg", 2048, 1600000000000, b"hash_xyz"),
            ],
        )

        # DB 2 files (containing duplicate of file1.jpg)
        create_mock_db(
            db2_path,
            [
                ("/backup/file1_copy.jpg", 1024, 1600000000000, b"hash_abc"),
                ("/backup/unique2.jpg", 4096, 1600000000000, b"hash_123"),
            ],
        )

        matcher = CrossDBMatcher([db1_path, db2_path])
        groups = matcher.find_cross_duplicates()

        assert len(groups) == 1
        group = groups[0]
        assert group["size"] == 1024
        assert group["match_count"] == 2

        matched_paths = {f["path"] for f in group["files"]}
        assert "/photos/file1.jpg" in matched_paths
        assert "/backup/file1_copy.jpg" in matched_paths


def test_cross_db_matcher_caching_and_invalidation():
    with tempfile.TemporaryDirectory() as tmpdir:
        db1_path = os.path.join(tmpdir, "db1.db")
        db2_path = os.path.join(tmpdir, "db2.db")
        cache_dir = os.path.join(tmpdir, "cache")

        create_mock_db(db1_path, [("/dir1/a.txt", 100, 1000, b"h1")])
        create_mock_db(db2_path, [("/dir2/a.txt", 100, 1000, b"h1")])

        matcher = CrossDBMatcher([db1_path, db2_path], cache_dir=cache_dir)

        # 1. Initial calculation
        g1 = matcher.find_cross_duplicates()
        assert len(g1) == 1

        # 2. Subsequent call with unchanged DB files hits cache
        g2 = matcher.find_cross_duplicates()
        assert len(g2) == 1
        assert g1 == g2

        # 3. Modify DB file -> invalidates fingerprint
        import time

        time.sleep(0.01)
        conn = sqlite3.connect(db1_path)
        conn.execute(
            "INSERT INTO files (path, size, mtime_ns, digest) VALUES (?, ?, ?, ?)",
            ("/dir1/b.txt", 200, 2000, b"h2"),
        )
        conn.commit()
        conn.close()

        # Touch timestamp to ensure stat mtime_ns changes
        os.utime(db1_path, None)

        g3 = matcher.find_cross_duplicates()
        assert len(g3) == 1
