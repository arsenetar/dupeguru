# Created By: Virgil Dupras
# Created On: 2009-10-22
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This is a fork from hsfs. The reason for this fork is that hsfs has been designed for musicGuru
# and was re-used for dupeGuru. The problem is that hsfs is way over-engineered for dupeGuru,
# resulting needless complexity and memory usage. It's been a while since I wanted to do that fork,
# and I'm doing it now.

import logging
import os
import sqlite3
from math import floor
from pathlib import Path
from sys import platform
from threading import Lock
from typing import Any, AnyStr, Callable, Union

try:
    from .dupeguru_rust import RustFilesDB

    HAS_RUST = True
except ImportError:
    try:
        from dupeguru_rust import RustFilesDB

        HAS_RUST = True
    except ImportError:
        HAS_RUST = False


from hscommon.util import get_file_ext, nonone

hasher: Callable
try:
    import xxhash

    hasher = xxhash.xxh128
except ImportError:
    import hashlib

    hasher = hashlib.md5

__all__ = [
    "File",
    "Folder",
    "get_file",
    "get_files",
    "FSError",
    "AlreadyExistsError",
    "InvalidPath",
    "InvalidDestinationError",
    "OperationError",
]

NOT_SET = object()

# The goal here is to not run out of memory on really big files. However, the chunk
# size has to be large enough so that the python loop isn't too costly in terms of
# CPU.
CHUNK_SIZE = 1024 * 1024  # 1 MiB

# Minimum size below which partial hashing is not used
MIN_FILE_SIZE = 3 * CHUNK_SIZE  # 3MiB, because we take 3 samples

# Partial hashing offset and size
PARTIAL_OFFSET_SIZE = (0x4000, 0x4000)


class FSError(Exception):
    cls_message = "An error has occured on '{name}' in '{parent}'"

    def __init__(self, fsobject, parent=None):
        message = self.cls_message
        if isinstance(fsobject, str):
            name = fsobject
        elif isinstance(fsobject, File):
            name = fsobject.name
        else:
            name = ""
        parentname = str(parent) if parent is not None else ""
        Exception.__init__(self, message.format(name=name, parent=parentname))


class AlreadyExistsError(FSError):
    "The directory or file name we're trying to add already exists"

    cls_message = "'{name}' already exists in '{parent}'"


class InvalidPath(FSError):
    "The path of self is invalid, and cannot be worked with."

    cls_message = "'{name}' is invalid."


class InvalidDestinationError(FSError):
    """A copy/move operation has been called, but the destination is invalid."""

    cls_message = "'{name}' is an invalid destination for this operation."


class OperationError(FSError):
    """A copy/move/delete operation has been called, but the checkup after the
    operation shows that it didn't work."""

    cls_message = "Operation on '{name}' failed."


class CacheEngine:
    def connect(self, path: Union[AnyStr, os.PathLike]) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def commit(self) -> None:
        raise NotImplementedError()

    def mark_directory_scanned(self, dir_path: Path) -> None:
        raise NotImplementedError()

    def is_directory_scanned(self, dir_path: Path) -> bool:
        raise NotImplementedError()

    def snapshot_file(self, path: Path, size: int, mtime: float) -> None:
        raise NotImplementedError()

    def get_files_in_directory(self, dir_path: Path):
        raise NotImplementedError()

    def get_candidate_sizes(self):
        raise NotImplementedError()

    def get_files_by_sizes(self, sizes):
        raise NotImplementedError()

    def get(self, path: Path, key: str, ignore_mtime: bool) -> Union[bytes, None]:
        raise NotImplementedError()

    def put(self, path: Path, key: str, value: Any) -> None:
        raise NotImplementedError()

    def get_cache_viewer_files(self, search: str = None, limit: int = 20, offset: int = 0):
        raise NotImplementedError()


class SQLiteCacheEngine(CacheEngine):
    schema_version = 1
    schema_version_description = "Changed from md5 to xxhash if available."

    create_table_query = """CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, size INTEGER, mtime_ns INTEGER,
        entry_dt DATETIME, digest BLOB, digest_partial BLOB, digest_samples BLOB)"""
    drop_table_query = "DROP TABLE IF EXISTS files;"
    create_dir_table_query = (
        """CREATE TABLE IF NOT EXISTS scanned_directories (path TEXT PRIMARY KEY, scan_dt DATETIME)"""
    )
    drop_dir_table_query = "DROP TABLE IF EXISTS scanned_directories;"
    select_query = "SELECT {key} FROM files WHERE path=:path AND size=:size and mtime_ns=:mtime_ns"
    select_query_ignore_mtime = "SELECT {key} FROM files WHERE path=:path AND size=:size"
    insert_query = """
        INSERT INTO files (path, size, mtime_ns, entry_dt, {key})
        VALUES (:path, :size, :mtime_ns, datetime('now'), :value)
        ON CONFLICT(path) DO UPDATE SET size=:size, mtime_ns=:mtime_ns, entry_dt=datetime('now'), {key}=:value;
    """

    def __init__(self, db_path: Union[AnyStr, os.PathLike], outer_db):
        self.db_path = db_path
        self.outer_db = outer_db
        self.conn = None
        self.lock = Lock()
        self.connect(db_path)

    def connect(self, path: Union[AnyStr, os.PathLike]) -> None:
        if platform.startswith("gnu0"):
            self.conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None, timeout=30.0)
        else:
            self.conn = sqlite3.connect(path, check_same_thread=False, timeout=30.0)

        # Enable Write-Ahead Log (WAL) mode for concurrent read/write resilience
        try:
            self.conn.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass

        # Check if the index needs to be created on a large database and warn the user
        try:
            cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_files_size'")
            if not cursor.fetchone():
                db_size_mb = 0
                if os.path.exists(path):
                    db_size_mb = os.path.getsize(path) / (1024 * 1024)
                if db_size_mb > 50:
                    print(
                        f"[de-dup] Optimizing database cache index (size: {db_size_mb:.1f} MB) "
                        "for the first time. Please wait...",
                        flush=True,
                    )
                    logging.info(f"Optimizing database cache index (size: {db_size_mb:.1f} MB) for the first time.")
        except Exception:
            pass

        self._check_upgrade()

    def _check_upgrade(self) -> None:
        with self.lock, self.conn as conn:
            has_schema = conn.execute(
                "SELECT NAME FROM sqlite_master WHERE type='table' AND name='schema_version'"
            ).fetchall()
            version = None
            if has_schema:
                version = conn.execute("SELECT version FROM schema_version ORDER BY version DESC").fetchone()[0]
            else:
                conn.execute("CREATE TABLE schema_version (version int PRIMARY KEY, description TEXT)")
            if version != self.schema_version:
                conn.execute(self.drop_table_query)
                conn.execute(self.drop_dir_table_query)
                conn.execute(
                    "INSERT OR REPLACE INTO schema_version VALUES (:version, :description)",
                    {"version": self.schema_version, "description": self.schema_version_description},
                )
            conn.execute(self.create_table_query)
            conn.execute(self.create_dir_table_query)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files (size)")

    def close(self) -> None:
        with self.lock:
            if self.conn:
                try:
                    self.conn.commit()
                except Exception:
                    pass
                self.conn.close()

    def clear(self) -> None:
        with self.lock:
            if self.conn:
                try:
                    self.conn.execute("DELETE FROM files;")
                    self.conn.execute("DELETE FROM scanned_directories;")
                    self.conn.execute("VACUUM;")
                    self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                except Exception as e:
                    logging.warning(f"Error clearing SQLite cache via VACUUM: {e}")
                    try:
                        self.conn.execute(self.drop_table_query)
                        self.conn.execute(self.drop_dir_table_query)
                        self.conn.execute(self.create_table_query)
                        self.conn.execute(self.create_dir_table_query)
                        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files (size)")
                    except Exception:
                        pass

    def commit(self) -> None:
        with self.lock:
            if self.conn:
                self.conn.commit()

    def mark_directory_scanned(self, dir_path: Path) -> None:
        try:
            with self.lock, self.conn as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO scanned_directories (path, scan_dt) VALUES (?, datetime('now'))",
                    (str(dir_path),),
                )
        except Exception as e:
            logging.error(f"Error marking directory scanned: {e}")

    def set_metadata(self, key: str, value: Any) -> None:
        try:
            with self.lock, self.conn as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS scan_metadata (key TEXT PRIMARY KEY, value TEXT)")
                conn.execute("INSERT OR REPLACE INTO scan_metadata (key, value) VALUES (?, ?)", (key, str(value)))
        except Exception as e:
            logging.error(f"Error setting metadata {key}={value}: {e}")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        try:
            with self.lock, self.conn as conn:
                has_table = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='scan_metadata'"
                ).fetchone()
                if not has_table:
                    return default
                row = conn.execute("SELECT value FROM scan_metadata WHERE key = ?", (key,)).fetchone()
                return row[0] if row else default
        except Exception:
            return default

    def is_directory_scanned(self, dir_path: Path) -> bool:
        try:
            with self.lock, self.conn as conn:
                row = conn.execute("SELECT 1 FROM scanned_directories WHERE path = ?", (str(dir_path),)).fetchone()
                if not row:
                    return False
                prefix = str(dir_path) + os.sep
                unhashed = conn.execute(
                    "SELECT 1 FROM files WHERE (path = ? OR path LIKE ?) AND (digest IS NULL OR digest = '') LIMIT 1",
                    (str(dir_path), prefix + "%"),
                ).fetchone()
                return unhashed is None
        except Exception:
            return False

    def snapshot_file(self, path: Path, size: int, mtime: float) -> None:
        try:
            mtime_ns = int(mtime * 1e9)
            with self.lock, self.conn as conn:
                conn.execute(
                    """INSERT INTO files (path, size, mtime_ns, entry_dt)
                       VALUES (:path, :size, :mtime_ns, datetime('now'))
                       ON CONFLICT(path) DO UPDATE SET size=:size, mtime_ns=:mtime_ns""",
                    {"path": str(path), "size": size, "mtime_ns": mtime_ns},
                )
                self.outer_db._checkpoint_counter += 1
                if (
                    self.outer_db.checkpoint_frequency > 0
                    and self.outer_db._checkpoint_counter >= self.outer_db.checkpoint_frequency
                ):
                    conn.commit()
                    self.outer_db._checkpoint_counter = 0
        except Exception as e:
            logging.error(f"Error snapshotting file: {e}")

    def get_files_in_directory(self, dir_path: Path):
        prefix = str(dir_path) + os.sep
        dir_str = str(dir_path)
        try:
            limit = 5000
            last_path = ""
            while True:
                with self.lock:
                    cursor = self.conn.execute(
                        """SELECT path, size, mtime_ns FROM files
                           WHERE (path = ? OR path LIKE ?) AND path > ?
                           ORDER BY path
                           LIMIT ?""",
                        (dir_str, prefix + "%", last_path, limit),
                    )
                    rows = cursor.fetchall()
                if not rows:
                    break
                for row in rows:
                    yield {"path": row[0], "size": row[1], "mtime_ns": row[2]}
                last_path = rows[-1][0]
        except Exception as e:
            logging.error(f"Error getting cached files in directory: {e}")

    def get_candidate_sizes(self):
        try:
            with self.lock:
                rows = self.conn.execute(
                    "SELECT size FROM files GROUP BY size HAVING COUNT(*) > 1 AND size > 0"
                ).fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            logging.error(f"Error getting candidate sizes: {e}")
            return []

    def get_files_by_sizes(self, sizes):
        if not sizes:
            return
        placeholders = ",".join("?" for _ in sizes)
        try:
            with self.lock:
                cursor = self.conn.execute(
                    f"SELECT path, size, mtime_ns FROM files WHERE size IN ({placeholders})",
                    sizes,
                )
                for row in cursor:
                    yield {"path": row[0], "size": row[1], "mtime_ns": row[2]}
        except Exception as e:
            logging.error(f"Error getting files by sizes: {e}")

    def get(self, path: Path, key: str, ignore_mtime: bool) -> Union[bytes, None]:
        stat = path.stat()
        size = stat.st_size
        mtime_ns = stat.st_mtime_ns
        try:
            with self.conn as conn:
                if ignore_mtime:
                    cursor = conn.execute(
                        self.select_query_ignore_mtime.format(key=key), {"path": str(path), "size": size}
                    )
                else:
                    cursor = conn.execute(
                        self.select_query.format(key=key),
                        {"path": str(path), "size": size, "mtime_ns": mtime_ns},
                    )
                result = cursor.fetchone()
                cursor.close()

            if result:
                self.outer_db.hit_paths.add(str(path))
                return result[0]
        except Exception as ex:
            logging.warning(f"Couldn't get {key} for {path} w/{size}, {mtime_ns}: {ex}")

        return None

    def put(self, path: Path, key: str, value: Any) -> None:
        stat = path.stat()
        size = stat.st_size
        mtime_ns = stat.st_mtime_ns
        try:
            with self.lock:
                self.conn.execute(
                    self.insert_query.format(key=key),
                    {"path": str(path), "size": size, "mtime_ns": mtime_ns, "value": value},
                )
                path_str = str(path)
                self.outer_db.last_scanned_path = path_str
                if path_str not in self.outer_db.scanned_paths:
                    self.outer_db.scanned_paths.add(path_str)
                    self.outer_db.scanned_count += 1
                self.outer_db._checkpoint_counter += 1
                if (
                    self.outer_db.checkpoint_frequency > 0
                    and self.outer_db._checkpoint_counter >= self.outer_db.checkpoint_frequency
                ):
                    self.conn.commit()
                    self.outer_db._checkpoint_counter = 0
        except Exception as ex:
            logging.warning(f"Couldn't put {key} for {path} w/{size}, {mtime_ns}: {ex}")

    def get_cache_viewer_files(self, search: str = None, limit: int = 20, offset: int = 0):
        with self.lock:
            if search:
                count_row = self.conn.execute(
                    "SELECT COUNT(*) FROM files WHERE path LIKE ?", (f"%{search}%",)
                ).fetchone()
                rows = self.conn.execute(
                    "SELECT path, size, entry_dt FROM files WHERE path LIKE ? "
                    "ORDER BY entry_dt DESC LIMIT ? OFFSET ?",
                    (f"%{search}%", limit, offset),
                ).fetchall()
            else:
                count_row = self.conn.execute("SELECT COUNT(*) FROM files").fetchone()
                rows = self.conn.execute(
                    "SELECT path, size, entry_dt FROM files ORDER BY entry_dt DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
            total_count = count_row[0] if count_row else 0
            files_list = []
            for row in rows:
                files_list.append({"path": row[0], "size": row[1], "entry_dt": row[2]})
            return total_count, files_list


def valkey_retry(func):
    def wrapper(self, *args, **kwargs):
        import time
        import redis.exceptions

        retries = 8
        backoff = 0.5
        for attempt in range(retries):
            try:
                return func(self, *args, **kwargs)
            except (
                redis.exceptions.ConnectionError,
                redis.exceptions.TimeoutError,
                redis.exceptions.BusyLoadingError,
            ) as e:
                if attempt == retries - 1:
                    logging.error(f"Valkey operation failed after {retries} retries: {e}")
                    raise
                logging.warning(
                    f"Valkey connection/loading error: {e}. Retrying in {backoff}s (attempt {attempt + 1}/{retries})..."
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, 4.0)

    return wrapper


class ValkeyCacheEngine(CacheEngine):
    def __init__(self, url: str, outer_db):
        self.url = url
        self.outer_db = outer_db
        try:
            import redis
        except ImportError:
            raise ImportError(
                "The 'redis' package is required to use Valkey/Redis caching. "
                "Please install it using 'pip install redis' to continue."
            )
        # Note: Do not decode_responses=True to preserve raw bytes for digest blobs
        self.client = redis.Redis.from_url(url)
        self.lock = Lock()

    def connect(self, path: Union[AnyStr, os.PathLike]) -> None:
        pass

    def close(self) -> None:
        pass

    @valkey_retry
    def clear(self) -> None:
        with self.lock:
            try:
                self.client.flushdb()
            except Exception:
                keys = []
                for key in self.client.scan_iter("dg:*"):
                    keys.append(key)
                    if len(keys) >= 1000:
                        self.client.delete(*keys)
                        keys = []
                if keys:
                    self.client.delete(*keys)

    def commit(self) -> None:
        pass

    @valkey_retry
    def mark_directory_scanned(self, dir_path: Path) -> None:
        try:
            with self.lock:
                self.client.sadd("dg:scanned_dirs", str(dir_path))
        except Exception as e:
            logging.error(f"Error marking directory scanned in Valkey: {e}")

    @valkey_retry
    def is_directory_scanned(self, dir_path: Path) -> bool:
        try:
            with self.lock:
                return bool(self.client.sismember("dg:scanned_dirs", str(dir_path)))
        except Exception:
            return False

    @valkey_retry
    def snapshot_file(self, path: Path, size: int, mtime: float) -> None:
        try:
            path_str = str(path)
            mtime_ns = int(mtime * 1e9)
            file_key = f"dg:file:{path_str}"
            import datetime

            with self.lock:
                # Track size change to keep indices accurate
                old_size_bytes = self.client.hget(file_key, "size")
                old_size = int(old_size_bytes) if old_size_bytes is not None else None

                now_str = datetime.datetime.now().isoformat()
                self.client.hset(file_key, mapping={"size": size, "mtime_ns": mtime_ns, "entry_dt": now_str})
                self.client.zadd("dg:files_by_path", {path_str: 0})
                self.client.zadd("dg:files_by_entry_dt", {path_str: mtime})

                if old_size != size:
                    if old_size is not None:
                        self.client.srem(f"dg:size_files:{old_size}", path_str)
                        new_count = self.client.hincrby("dg:size_counts", str(old_size), -1)
                        if new_count < 2:
                            self.client.srem("dg:candidate_sizes", str(old_size))

                    self.client.sadd(f"dg:size_files:{size}", path_str)
                    new_count = self.client.hincrby("dg:size_counts", str(size), 1)
                    if new_count >= 2:
                        self.client.sadd("dg:candidate_sizes", str(size))
        except Exception as e:
            logging.error(f"Error snapshotting file in Valkey: {e}")

    def get_files_in_directory(self, dir_path: Path):
        dir_str = str(dir_path)
        prefix = dir_str + os.sep

        # Check the directory itself
        @valkey_retry
        def check_dir(self):
            with self.lock:
                return self.client.exists(f"dg:file:{dir_str}")

        try:
            if check_dir(self):

                @valkey_retry
                def fetch_meta_dir(self):
                    with self.lock:
                        return self.client.hmget(f"dg:file:{dir_str}", ["size", "mtime_ns"])

                meta = fetch_meta_dir(self)
                if meta and meta[0] is not None:
                    yield {
                        "path": dir_str,
                        "size": int(meta[0]),
                        "mtime_ns": int(meta[1]) if meta[1] is not None else 0,
                    }

            limit = 5000
            offset = 0
            while True:

                @valkey_retry
                def fetch_paths_page(self, off):
                    with self.lock:
                        path_bytes_list = self.client.zrangebylex(
                            "dg:files_by_path", f"[{prefix}", f"[{prefix}\xff", start=off, num=limit
                        )
                        return [p.decode("utf-8") for p in path_bytes_list]

                paths = fetch_paths_page(self, offset)
                if not paths:
                    break

                for path_str in paths:

                    @valkey_retry
                    def fetch_meta(self, p_str):
                        with self.lock:
                            return self.client.hmget(f"dg:file:{p_str}", ["size", "mtime_ns"])

                    meta = fetch_meta(self, path_str)
                    if meta and meta[0] is not None:
                        yield {
                            "path": path_str,
                            "size": int(meta[0]),
                            "mtime_ns": int(meta[1]) if meta[1] is not None else 0,
                        }
                offset += len(paths)
        except Exception as e:
            logging.error(f"Error getting cached files in Valkey: {e}")

    @valkey_retry
    def get_candidate_sizes(self):
        try:
            with self.lock:
                sizes = self.client.smembers("dg:candidate_sizes")
                return [int(s) for s in sizes]
        except Exception as e:
            logging.error(f"Error getting candidate sizes in Valkey: {e}")
            return []

    def get_files_by_sizes(self, sizes):
        if not sizes:
            return

        try:
            for size in sizes:

                @valkey_retry
                def fetch_size_paths(self, sz):
                    with self.lock:
                        return [p.decode("utf-8") for p in self.client.smembers(f"dg:size_files:{sz}")]

                paths = fetch_size_paths(self, size)
                for path_str in paths:

                    @valkey_retry
                    def fetch_meta(self, p_str):
                        with self.lock:
                            return self.client.hmget(f"dg:file:{p_str}", ["size", "mtime_ns"])

                    meta = fetch_meta(self, path_str)
                    if meta and meta[0] is not None:
                        yield {
                            "path": path_str,
                            "size": int(meta[0]),
                            "mtime_ns": int(meta[1]) if meta[1] is not None else 0,
                        }
        except Exception as e:
            logging.error(f"Error getting files by sizes in Valkey: {e}")

    @valkey_retry
    def get(self, path: Path, key: str, ignore_mtime: bool) -> Union[bytes, None]:
        path_str = str(path)
        file_key = f"dg:file:{path_str}"
        try:
            with self.lock:
                meta = self.client.hmget(file_key, ["size", "mtime_ns", key])
                if not meta or meta[0] is None:
                    return None

                size = int(meta[0])
                mtime_ns = int(meta[1]) if meta[1] is not None else 0
                val = meta[2]

                stat = path.stat()
                if stat.st_size != size:
                    return None
                if not ignore_mtime and stat.st_mtime_ns != mtime_ns:
                    return None

                if val:
                    self.outer_db.hit_paths.add(path_str)
                    return val
        except Exception as ex:
            logging.warning(f"Couldn't get {key} for {path} in Valkey: {ex}")
        return None

    @valkey_retry
    def put(self, path: Path, key: str, value: Any) -> None:
        path_str = str(path)
        stat = path.stat()
        size = stat.st_size
        mtime_ns = stat.st_mtime_ns
        file_key = f"dg:file:{path_str}"
        import datetime

        try:
            with self.lock:
                now_str = datetime.datetime.now().isoformat()
                self.client.hset(
                    file_key, mapping={"size": size, "mtime_ns": mtime_ns, "entry_dt": now_str, key: value}
                )
                self.client.zadd("dg:files_by_path", {path_str: 0})
                self.client.zadd("dg:files_by_entry_dt", {path_str: stat.st_mtime})

                self.outer_db.last_scanned_path = path_str
                if path_str not in self.outer_db.scanned_paths:
                    self.outer_db.scanned_paths.add(path_str)
                    self.outer_db.scanned_count += 1
        except Exception as ex:
            logging.warning(f"Couldn't put {key} for {path} in Valkey: {ex}")

    @valkey_retry
    def get_cache_viewer_files(self, search: str = None, limit: int = 20, offset: int = 0):
        with self.lock:
            if search:
                all_paths_bytes = self.client.zrange("dg:files_by_entry_dt", 0, -1, desc=True)
                matched_paths = []
                for p in all_paths_bytes:
                    path_str = p.decode("utf-8")
                    if search in path_str:
                        matched_paths.append(path_str)
                total_count = len(matched_paths)
                batch = matched_paths[offset : offset + limit]
            else:
                total_count = self.client.zcard("dg:files_by_entry_dt")
                path_bytes_list = self.client.zrange("dg:files_by_entry_dt", offset, offset + limit - 1, desc=True)
                batch = [p.decode("utf-8") for p in path_bytes_list]

            files_list = []
            for path_str in batch:
                file_key = f"dg:file:{path_str}"
                meta = self.client.hmget(file_key, ["size", "entry_dt"])
                files_list.append(
                    {
                        "path": path_str,
                        "size": int(meta[0]) if meta[0] is not None else 0,
                        "entry_dt": meta[1].decode("utf-8") if meta[1] is not None else "",
                    }
                )
            return total_count, files_list


def _clean_path_str(path) -> str:
    s = str(path)
    return s.encode("utf-8", errors="surrogateescape").decode("utf-8", errors="replace")


class FilesDB:
    ignore_mtime = False
    enable_directory_cache = False

    def __init__(self):
        self.engine = None
        self.checkpoint_frequency = 100
        self._checkpoint_counter = 0
        self.scanned_count = 0
        self.last_scanned_path = None
        self.scanned_paths = set()
        self.hit_paths = set()
        self.lock = Lock()
        self._is_rust = False

    def connect(self, path: Union[AnyStr, os.PathLike]) -> None:
        path_str = _clean_path_str(path)
        if HAS_RUST:
            try:
                self.engine = RustFilesDB(path_str)
                self._is_rust = True
                logging.info("Using high-performance Rust cache database engine.")
                return
            except Exception as e:
                logging.warning(f"Failed to load Rust engine: {e}. Falling back to Python engine.")

        self._is_rust = False
        if path_str.startswith("redis://") or path_str.startswith("valkey://"):
            self.engine = ValkeyCacheEngine(path_str, self)
        else:
            self.engine = SQLiteCacheEngine(path_str, self)

    @property
    def conn(self):
        if not self._is_rust and hasattr(self.engine, "conn"):
            return self.engine.conn
        return None

    def close(self) -> None:
        if self.engine:
            self.engine.close()

    def clear(self) -> None:
        if self.engine:
            self.engine.clear()

    def commit(self) -> None:
        if self.engine:
            self.engine.commit()

    def set_metadata(self, key: str, value: Any) -> None:
        if self.engine and hasattr(self.engine, "set_metadata"):
            self.engine.set_metadata(key, value)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        if self.engine and hasattr(self.engine, "get_metadata"):
            return self.engine.get_metadata(key, default)
        return default

    def mark_directory_scanned(self, dir_path: Path) -> None:
        if self.engine:
            if self._is_rust:
                self.engine.mark_directory_scanned(_clean_path_str(dir_path))
            else:
                self.engine.mark_directory_scanned(dir_path)

    def is_directory_scanned(self, dir_path: Path) -> bool:
        if self.engine:
            if self._is_rust:
                return self.engine.is_directory_scanned(_clean_path_str(dir_path))
            else:
                return self.engine.is_directory_scanned(dir_path)
            return False

    def snapshot_file(self, path: Path, size: int, mtime: float) -> None:
        if self.engine:
            if self._is_rust:
                self.engine.snapshot_file(_clean_path_str(path), size, mtime)
            else:
                self.engine.snapshot_file(path, size, mtime)

    def snapshot_files_batch(self, batch) -> None:
        if self.engine:
            if self._is_rust:
                rust_batch = [(_clean_path_str(item[0]), item[1], item[2]) for item in batch]
                self.engine.snapshot_files_batch(rust_batch)
            else:
                for path, size, mtime in batch:
                    self.engine.snapshot_file(path, size, mtime)
                self.engine.commit()

    def get_files_in_directory(self, dir_path: Path):
        if self.engine:
            if self._is_rust:
                last_path = ""
                clean_dir = _clean_path_str(dir_path)
                while True:
                    page = self.engine.get_files_in_directory_page(clean_dir, last_path, 2000)
                    if not page:
                        break
                    yield from page
                    last_path = page[-1]["path"]
            else:
                yield from self.engine.get_files_in_directory(dir_path)

    def get_candidate_sizes(self):
        if self.engine:
            return self.engine.get_candidate_sizes()
        return []

    def get_files_by_sizes(self, sizes):
        if self.engine:
            if self._is_rust:
                last_path = ""
                limit = 5000
                while True:
                    page = self.engine.get_files_by_sizes_page(sizes, last_path, limit)
                    if not page:
                        break
                    yield from page
                    last_path = page[-1]["path"]
            else:
                yield from self.engine.get_files_by_sizes(sizes)

    def get(self, path: Path, key: str) -> Union[bytes, None]:
        if self.engine:
            if self._is_rust:
                try:
                    stat = path.stat()
                    return self.engine.get(
                        _clean_path_str(path), key, stat.st_size, stat.st_mtime_ns, self.ignore_mtime
                    )
                except (OSError, InvalidPath):
                    return None
            else:
                return self.engine.get(path, key, self.ignore_mtime)
        return None

    def set(self, path: Path, key: str, value: bytes) -> None:
        if self.engine:
            if self._is_rust:
                try:
                    stat = path.stat()
                    self.engine.set(_clean_path_str(path), key, value, stat.st_size, stat.st_mtime_ns)
                except (OSError, InvalidPath):
                    pass
            else:
                self.engine.set(path, key, value)

    def get_cache_viewer_files(self, search: str = None, limit: int = 20, offset: int = 0):
        if self.engine:
            return self.engine.get_cache_viewer_files(search, limit, offset)
        return 0, []


filesdb = FilesDB()  # Singleton


class File:
    """Represents a file and holds metadata to be used for scanning."""

    INITIAL_INFO = {"size": 0, "mtime": 0, "digest": b"", "digest_partial": b"", "digest_samples": b""}
    # Slots for File make us save quite a bit of memory. In a memory test I've made with a lot of
    # files, I saved 35% memory usage with "unread" files (no _read_info() call) and gains become
    # even greater when we take into account read attributes (70%!). Yeah, it's worth it.
    __slots__ = ("path", "is_ref", "words") + tuple(INITIAL_INFO.keys())

    def __init__(self, path):
        for attrname in self.INITIAL_INFO:
            setattr(self, attrname, NOT_SET)
        if type(path) is os.DirEntry:
            self.path = Path(path.path)
            self.size = nonone(path.stat().st_size, 0)
            self.mtime = nonone(path.stat().st_mtime, 0)
        else:
            self.path = path

    @property
    def unicode_path(self):
        return str(self.path) if self.path else ""

    def __repr__(self):
        return f"<{self.__class__.__name__} {str(self.path)}>"

    def __getattribute__(self, attrname):
        result = object.__getattribute__(self, attrname)
        if result is NOT_SET:
            try:
                self._read_info(attrname)
            except Exception as e:
                logging.warning("An error '%s' was raised while decoding '%s'", e, repr(self.path))
            result = object.__getattribute__(self, attrname)
            if result is NOT_SET:
                result = self.INITIAL_INFO[attrname]
        return result

    def _calc_digest(self):
        # type: () -> bytes

        with self.path.open("rb") as fp:
            file_hash = hasher()
            # The goal here is to not run out of memory on really big files. However, the chunk
            # size has to be large enough so that the python loop isn't too costly in terms of
            # CPU.
            CHUNK_SIZE = 1024 * 1024  # 1 mb
            filedata = fp.read(CHUNK_SIZE)
            while filedata:
                file_hash.update(filedata)
                filedata = fp.read(CHUNK_SIZE)
            return file_hash.digest()

    def _calc_digest_partial(self):
        # type: () -> bytes
        with self.path.open("rb") as fp:
            fp.seek(PARTIAL_OFFSET_SIZE[0])
            partial_data = fp.read(PARTIAL_OFFSET_SIZE[1])
            return hasher(partial_data).digest()

    def _calc_digest_samples(self) -> bytes:
        size = self.size
        with self.path.open("rb") as fp:
            # Chunk at 25% of the file
            fp.seek(floor(size * 25 / 100), 0)
            file_data = fp.read(CHUNK_SIZE)
            file_hash = hasher(file_data)

            # Chunk at 60% of the file
            fp.seek(floor(size * 60 / 100), 0)
            file_data = fp.read(CHUNK_SIZE)
            file_hash.update(file_data)

            # Last chunk of the file
            fp.seek(-CHUNK_SIZE, 2)
            file_data = fp.read(CHUNK_SIZE)
            file_hash.update(file_data)
            return file_hash.digest()

    def _read_info(self, field):
        # print(f"_read_info({field}) for {self}")
        if field in ("size", "mtime"):
            stats = self.path.stat()
            self.size = nonone(stats.st_size, 0)
            self.mtime = nonone(stats.st_mtime, 0)
        elif field == "digest_partial":
            self.digest_partial = filesdb.get(self.path, "digest_partial")
            if self.digest_partial is None:
                # If file is smaller than partial requirements just use the full digest
                if self.size < PARTIAL_OFFSET_SIZE[0] + PARTIAL_OFFSET_SIZE[1]:
                    self.digest_partial = self.digest
                else:
                    self.digest_partial = self._calc_digest_partial()
                filesdb.put(self.path, "digest_partial", self.digest_partial)
        elif field == "digest":
            self.digest = filesdb.get(self.path, "digest")
            if self.digest is None:
                self.digest = self._calc_digest()
                filesdb.put(self.path, "digest", self.digest)
        elif field == "digest_samples":
            size = self.size
            # Might as well hash such small files entirely.
            if size <= MIN_FILE_SIZE:
                self.digest_samples = self.digest
                return
            self.digest_samples = filesdb.get(self.path, "digest_samples")
            if self.digest_samples is None:
                self.digest_samples = self._calc_digest_samples()
                filesdb.put(self.path, "digest_samples", self.digest_samples)

    def _read_all_info(self, attrnames=None):
        """Cache all possible info.

        If `attrnames` is not None, caches only attrnames.
        """
        if attrnames is None:
            attrnames = self.INITIAL_INFO.keys()
        for attrname in attrnames:
            getattr(self, attrname)

    # --- Public
    @classmethod
    def can_handle(cls, path):
        """Returns whether this file wrapper class can handle ``path``."""
        return not path.is_symlink() and path.is_file()

    def exists(self) -> bool:
        """Safely check if the underlying file exists, treat error as non-existent"""
        try:
            return self.path.exists()
        except OSError as ex:
            logging.warning(f"Checking {self.path} raised: {ex}")
            return False

    def rename(self, newname):
        if newname == self.name:
            return
        destpath = self.path.parent.joinpath(newname)
        if destpath.exists():
            raise AlreadyExistsError(newname, self.path.parent)
        try:
            self.path.rename(destpath)
        except OSError:
            raise OperationError(self)
        if not destpath.exists():
            raise OperationError(self)
        self.path = destpath

    def get_display_info(self, group, delta):
        """Returns a display-ready dict of dupe's data."""
        raise NotImplementedError()

    # --- Properties
    @property
    def extension(self):
        return get_file_ext(self.name)

    @property
    def name(self):
        return self.path.name

    @property
    def folder_path(self):
        return self.path.parent


class Folder(File):
    """A wrapper around a folder path.

    It has the size/digest info of a File, but its value is the sum of its subitems.
    """

    __slots__ = File.__slots__ + ("_subfolders",)

    def __init__(self, path):
        File.__init__(self, path)
        self.size = NOT_SET
        self._subfolders = None

    def _all_items(self):
        folders = self.subfolders
        files = get_files(self.path)
        return folders + files

    def _read_info(self, field):
        # print(f"_read_info({field}) for Folder {self}")
        if field in {"size", "mtime"}:
            size = sum((f.size for f in self._all_items()), 0)
            self.size = size
            stats = self.path.stat()
            self.mtime = nonone(stats.st_mtime, 0)
        elif field in {"digest", "digest_partial", "digest_samples"}:
            # What's sensitive here is that we must make sure that subfiles'
            # digest are always added up in the same order, but we also want a
            # different digest if a file gets moved in a different subdirectory.

            def get_dir_digest_concat():
                items = self._all_items()
                items.sort(key=lambda f: f.path)
                digests = [getattr(f, field) for f in items]
                return b"".join(digests)

            digest = hasher(get_dir_digest_concat()).digest()
            setattr(self, field, digest)

    @property
    def subfolders(self):
        if self._subfolders is None:
            with os.scandir(self.path) as iter:
                subfolders = [p for p in iter if not p.is_symlink() and p.is_dir()]
            self._subfolders = [self.__class__(p) for p in subfolders]
        return self._subfolders

    @classmethod
    def can_handle(cls, path):
        return not path.is_symlink() and path.is_dir()


def get_file(path, fileclasses=[File], skip_disk_check=False):
    """Wraps ``path`` around its appropriate :class:`File` class.

    Whether a class is "appropriate" is decided by :meth:`File.can_handle`

    :param Path path: path to wrap
    :param fileclasses: List of candidate :class:`File` classes
    """
    for fileclass in fileclasses:
        if skip_disk_check:
            if hasattr(fileclass, "HANDLED_EXTS"):
                if get_file_ext(path.name) in fileclass.HANDLED_EXTS:
                    return fileclass(path)
            elif hasattr(fileclass, "SUPPORTED_EXTS"):
                if get_file_ext(path.name) in fileclass.SUPPORTED_EXTS:
                    return fileclass(path)
            else:
                if fileclass.__name__ == "File" or len(fileclasses) == 1:
                    return fileclass(path)
        else:
            if fileclass.can_handle(path):
                return fileclass(path)


def get_files(path, fileclasses=[File]):
    """Returns a list of :class:`File` for each file contained in ``path``.

    :param Path path: path to scan
    :param fileclasses: List of candidate :class:`File` classes
    """
    assert all(issubclass(fileclass, File) for fileclass in fileclasses)
    try:
        result = []
        with os.scandir(path) as iter:
            for item in iter:
                file = get_file(item, fileclasses=fileclasses)
                if file is not None:
                    result.append(file)
        return result
    except OSError:
        raise InvalidPath(path)
