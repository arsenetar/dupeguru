# Created By: Virgil Dupras
# Created On: 2009-10-23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import typing
from os import urandom
from pathlib import Path

from core import fs
from core.tests.directories_test import create_fake_fs
from hscommon.testutil import eq_

hasher: typing.Callable
try:
    import xxhash

    hasher = xxhash.xxh128
except ImportError:
    import hashlib

    hasher = hashlib.md5


def create_fake_fs_with_random_data(rootpath):
    rootpath = rootpath.joinpath("fs")
    rootpath.mkdir()
    rootpath.joinpath("dir1").mkdir()
    rootpath.joinpath("dir2").mkdir()
    rootpath.joinpath("dir3").mkdir()
    data1 = urandom(200 * 1024)  # 200KiB
    data2 = urandom(1024 * 1024)  # 1MiB
    data3 = urandom(10 * 1024 * 1024)  # 10MiB
    with rootpath.joinpath("file1.test").open("wb") as fp:
        fp.write(data1)
    with rootpath.joinpath("file2.test").open("wb") as fp:
        fp.write(data2)
    with rootpath.joinpath("file3.test").open("wb") as fp:
        fp.write(data3)
    with rootpath.joinpath("dir1", "file1.test").open("wb") as fp:
        fp.write(data1)
    with rootpath.joinpath("dir2", "file2.test").open("wb") as fp:
        fp.write(data2)
    with rootpath.joinpath("dir3", "file3.test").open("wb") as fp:
        fp.write(data3)
    return rootpath


def test_size_aggregates_subfiles(tmpdir):
    p = create_fake_fs(Path(str(tmpdir)))
    b = fs.Folder(p)
    eq_(b.size, 12)


def test_digest_aggregate_subfiles_sorted(tmpdir):
    # dir.allfiles can return child in any order. Thus, bundle.digest must aggregate
    # all files' digests it contains, but it must make sure that it does so in the
    # same order everytime.
    p = create_fake_fs_with_random_data(Path(str(tmpdir)))
    b = fs.Folder(p)
    digest1 = fs.File(p.joinpath("dir1", "file1.test")).digest
    digest2 = fs.File(p.joinpath("dir2", "file2.test")).digest
    digest3 = fs.File(p.joinpath("dir3", "file3.test")).digest
    digest4 = fs.File(p.joinpath("file1.test")).digest
    digest5 = fs.File(p.joinpath("file2.test")).digest
    digest6 = fs.File(p.joinpath("file3.test")).digest
    # The expected digest is the hash of digests for folders and the direct digest for files
    folder_digest1 = hasher(digest1).digest()
    folder_digest2 = hasher(digest2).digest()
    folder_digest3 = hasher(digest3).digest()
    digest = hasher(folder_digest1 + folder_digest2 + folder_digest3 + digest4 + digest5 + digest6).digest()
    eq_(b.digest, digest)


def test_partial_digest_aggregate_subfile_sorted(tmpdir):
    p = create_fake_fs_with_random_data(Path(str(tmpdir)))
    b = fs.Folder(p)
    digest1 = fs.File(p.joinpath("dir1", "file1.test")).digest_partial
    digest2 = fs.File(p.joinpath("dir2", "file2.test")).digest_partial
    digest3 = fs.File(p.joinpath("dir3", "file3.test")).digest_partial
    digest4 = fs.File(p.joinpath("file1.test")).digest_partial
    digest5 = fs.File(p.joinpath("file2.test")).digest_partial
    digest6 = fs.File(p.joinpath("file3.test")).digest_partial
    # The expected digest is the hash of digests for folders and the direct digest for files
    folder_digest1 = hasher(digest1).digest()
    folder_digest2 = hasher(digest2).digest()
    folder_digest3 = hasher(digest3).digest()
    digest = hasher(folder_digest1 + folder_digest2 + folder_digest3 + digest4 + digest5 + digest6).digest()
    eq_(b.digest_partial, digest)

    digest1 = fs.File(p.joinpath("dir1", "file1.test")).digest_samples
    digest2 = fs.File(p.joinpath("dir2", "file2.test")).digest_samples
    digest3 = fs.File(p.joinpath("dir3", "file3.test")).digest_samples
    digest4 = fs.File(p.joinpath("file1.test")).digest_samples
    digest5 = fs.File(p.joinpath("file2.test")).digest_samples
    digest6 = fs.File(p.joinpath("file3.test")).digest_samples
    # The expected digest is the digest of digests for folders and the direct digest for files
    folder_digest1 = hasher(digest1).digest()
    folder_digest2 = hasher(digest2).digest()
    folder_digest3 = hasher(digest3).digest()
    digest = hasher(folder_digest1 + folder_digest2 + folder_digest3 + digest4 + digest5 + digest6).digest()
    eq_(b.digest_samples, digest)


def test_has_file_attrs(tmpdir):
    # a Folder must behave like a file, so it must have mtime attributes
    b = fs.Folder(Path(str(tmpdir)))
    assert b.mtime > 0
    eq_(b.extension, "")


def test_filesdb_directory_cache(tmpdir):
    db_path = Path(str(tmpdir)).joinpath("test_cache.db")
    db = fs.FilesDB()
    db.connect(db_path)

    # Test directory mark & check
    path1 = Path("/some/scanned/dir")
    path2 = Path("/another/unscanned/dir")

    assert not db.is_directory_scanned(path1)
    db.mark_directory_scanned(path1)
    assert db.is_directory_scanned(path1)
    assert not db.is_directory_scanned(path2)

    # Test snapshot file and get_files_in_directory
    file1 = path1.joinpath("file1.txt")
    file2 = path1.joinpath("file2.txt")
    file3 = path2.joinpath("file3.txt")

    db.snapshot_file(file1, 1024, 1234567.89)
    db.snapshot_file(file2, 2048, 9876543.21)
    db.snapshot_file(file3, 512, 1111111.11)

    files = list(db.get_files_in_directory(path1))
    assert len(files) == 2
    paths = {f["path"] for f in files}
    assert str(file1) in paths
    assert str(file2) in paths

    # Check sizes and mtimes
    file1_data = next(f for f in files if f["path"] == str(file1))
    assert file1_data["size"] == 1024
    assert file1_data["mtime_ns"] == int(1234567.89 * 1e9)

    # Test clearing DB
    db.clear()
    assert not db.is_directory_scanned(path1)
    assert len(list(db.get_files_in_directory(path1))) == 0


def test_valkey_cache_engine():
    import pytest

    try:
        import redis  # noqa: F401
    except ImportError:
        pytest.skip("redis library is not installed")

    # Connect to a local test redis instance or skip
    db = fs.FilesDB()
    try:
        db.connect("redis://localhost:6379/15")
        # Ping to check if server is responsive
        db.engine.client.ping()
    except Exception:
        pytest.skip("Redis server is not running on localhost:6379/15")

    try:
        # Clean up database partition before run
        db.clear()

        # Test directory mark & check
        path1 = Path("/some/scanned/dir")
        path2 = Path("/another/unscanned/dir")

        assert not db.is_directory_scanned(path1)
        db.mark_directory_scanned(path1)
        assert db.is_directory_scanned(path1)
        assert not db.is_directory_scanned(path2)

        # Test snapshot file and get_files_in_directory
        file1 = path1.joinpath("file1.txt")
        file2 = path1.joinpath("file2.txt")
        file3 = path2.joinpath("file3.txt")

        db.snapshot_file(file1, 1024, 1234567.89)
        db.snapshot_file(file2, 2048, 9876543.21)
        db.snapshot_file(file3, 512, 1111111.11)

        files = list(db.get_files_in_directory(path1))
        assert len(files) == 2
        paths = {f["path"] for f in files}
        assert str(file1) in paths
        assert str(file2) in paths

        # Check sizes and mtimes
        file1_data = next(f for f in files if f["path"] == str(file1))
        assert file1_data["size"] == 1024
        assert file1_data["mtime_ns"] == int(1234567.89 * 1e9)

        # Test Candidate sizes & get_files_by_sizes
        assert db.get_candidate_sizes() == []  # All unique sizes (1024, 2048, 512)

        # Add another file of size 1024 to trigger duplicate size
        file4 = path2.joinpath("file4.txt")
        db.snapshot_file(file4, 1024, 1234567.89)
        eq_(db.get_candidate_sizes(), [1024])

        by_sizes = list(db.get_files_by_sizes([1024]))
        assert len(by_sizes) == 2
        by_sizes_paths = {f["path"] for f in by_sizes}
        assert str(file1) in by_sizes_paths
        assert str(file4) in by_sizes_paths

        # Test put/get operations
        db.put(file1, "digest", b"fake_digest_bytes")
        eq_(db.get(file1, "digest"), b"fake_digest_bytes")

        # Test get_cache_viewer_files
        total, rows = db.get_cache_viewer_files(limit=10)
        assert total == 4  # file1, file2, file3, file4
        assert len(rows) == 4

        total_search, rows_search = db.get_cache_viewer_files(search="file1", limit=10)
        assert total_search == 1
        assert rows_search[0]["path"] == str(file1)

        # Test clearing DB
        db.clear()
        assert not db.is_directory_scanned(path1)
        assert len(list(db.get_files_in_directory(path1))) == 0
    finally:
        # Flush DB to leave it clean
        db.clear()
        db.close()
