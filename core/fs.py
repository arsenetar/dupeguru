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

import os

from math import floor
import logging
import sqlite3
from threading import Lock
from typing import Any, AnyStr, Union, Callable

from pathlib import Path
from hscommon.util import nonone, get_file_ext

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


class FilesDB:
    schema_version = 1
    schema_version_description = "Changed from md5 to xxhash if available."

    create_table_query = "CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, size INTEGER, mtime_ns INTEGER, entry_dt DATETIME, digest BLOB, digest_partial BLOB, digest_samples BLOB)"
    drop_table_query = "DROP TABLE IF EXISTS files;"
    select_query = "SELECT {key} FROM files WHERE path=:path AND size=:size and mtime_ns=:mtime_ns"
    insert_query = """
        INSERT INTO files (path, size, mtime_ns, entry_dt, {key}) VALUES (:path, :size, :mtime_ns, datetime('now'), :value)
        ON CONFLICT(path) DO UPDATE SET size=:size, mtime_ns=:mtime_ns, entry_dt=datetime('now'), {key}=:value;
    """

    def __init__(self):
        self.conn = None
        self.cur = None
        self.lock = None

    def connect(self, path: Union[AnyStr, os.PathLike]) -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.lock = Lock()
        self._check_upgrade()

    def _check_upgrade(self) -> None:
        with self.lock:
            has_schema = self.cur.execute(
                "SELECT NAME FROM sqlite_master WHERE type='table' AND name='schema_version'"
            ).fetchall()
            version = None
            if has_schema:
                version = self.cur.execute("SELECT version FROM schema_version ORDER BY version DESC").fetchone()[0]
            else:
                self.cur.execute("CREATE TABLE schema_version (version int PRIMARY KEY, description TEXT)")
            if version != self.schema_version:
                self.cur.execute(self.drop_table_query)
                self.cur.execute(
                    "INSERT OR REPLACE INTO schema_version VALUES (:version, :description)",
                    {"version": self.schema_version, "description": self.schema_version_description},
                )
            self.cur.execute(self.create_table_query)
            self.conn.commit()

    def clear(self) -> None:
        with self.lock:
            self.cur.execute(self.drop_table_query)
            self.cur.execute(self.create_table_query)

    def get(self, path: Path, key: str) -> Union[bytes, None]:
        stat = path.stat()
        size = stat.st_size
        mtime_ns = stat.st_mtime_ns
        try:
            with self.lock:
                self.cur.execute(
                    self.select_query.format(key=key), {"path": str(path), "size": size, "mtime_ns": mtime_ns}
                )
                result = self.cur.fetchone()

            if result:
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
                self.cur.execute(
                    self.insert_query.format(key=key),
                    {"path": str(path), "size": size, "mtime_ns": mtime_ns, "value": value},
                )
        except Exception as ex:
            logging.warning(f"Couldn't put {key} for {path} w/{size}, {mtime_ns}: {ex}")

    def commit(self) -> None:
        with self.lock:
            self.conn.commit()

    def close(self) -> None:
        with self.lock:
            self.cur.close()
            self.conn.close()


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

        # This offset is where we should start reading the file to get a partial hash
        # For audio file, it should be where audio data starts
        offset, size = (0x4000, 0x4000)

        with self.path.open("rb") as fp:
            fp.seek(offset)
            partial_data = fp.read(size)
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
                setattr(self, field, self.digest)
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


def get_file(path, fileclasses=[File]):
    """Wraps ``path`` around its appropriate :class:`File` class.

    Whether a class is "appropriate" is decided by :meth:`File.can_handle`

    :param Path path: path to wrap
    :param fileclasses: List of candidate :class:`File` classes
    """
    for fileclass in fileclasses:
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
