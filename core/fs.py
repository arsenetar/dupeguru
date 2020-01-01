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

import hashlib
import logging

from hscommon.util import nonone, get_file_ext

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


class File:
    """Represents a file and holds metadata to be used for scanning.
    """

    INITIAL_INFO = {
        "size": 0,
        "mtime": 0,
        "md5": "",
        "md5partial": "",
    }
    # Slots for File make us save quite a bit of memory. In a memory test I've made with a lot of
    # files, I saved 35% memory usage with "unread" files (no _read_info() call) and gains become
    # even greater when we take into account read attributes (70%!). Yeah, it's worth it.
    __slots__ = ("path", "is_ref", "words") + tuple(INITIAL_INFO.keys())

    def __init__(self, path):
        self.path = path
        for attrname in self.INITIAL_INFO:
            setattr(self, attrname, NOT_SET)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, str(self.path))

    def __getattribute__(self, attrname):
        result = object.__getattribute__(self, attrname)
        if result is NOT_SET:
            try:
                self._read_info(attrname)
            except Exception as e:
                logging.warning(
                    "An error '%s' was raised while decoding '%s'", e, repr(self.path)
                )
            result = object.__getattribute__(self, attrname)
            if result is NOT_SET:
                result = self.INITIAL_INFO[attrname]
        return result

    # This offset is where we should start reading the file to get a partial md5
    # For audio file, it should be where audio data starts
    def _get_md5partial_offset_and_size(self):
        return (0x4000, 0x4000)  # 16Kb

    def _read_info(self, field):
        if field in ("size", "mtime"):
            stats = self.path.stat()
            self.size = nonone(stats.st_size, 0)
            self.mtime = nonone(stats.st_mtime, 0)
        elif field == "md5partial":
            try:
                fp = self.path.open("rb")
                offset, size = self._get_md5partial_offset_and_size()
                fp.seek(offset)
                partialdata = fp.read(size)
                md5 = hashlib.md5(partialdata)
                self.md5partial = md5.digest()
                fp.close()
            except Exception:
                pass
        elif field == "md5":
            try:
                fp = self.path.open("rb")
                md5 = hashlib.md5()
                # The goal here is to not run out of memory on really big files. However, the chunk
                # size has to be large enough so that the python loop isn't too costly in terms of
                # CPU.
                CHUNK_SIZE = 1024 * 1024  # 1 mb
                filedata = fp.read(CHUNK_SIZE)
                while filedata:
                    md5.update(filedata)
                    filedata = fp.read(CHUNK_SIZE)
                self.md5 = md5.digest()
                fp.close()
            except Exception:
                pass

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
        """Returns whether this file wrapper class can handle ``path``.
        """
        return not path.islink() and path.isfile()

    def rename(self, newname):
        if newname == self.name:
            return
        destpath = self.path.parent()[newname]
        if destpath.exists():
            raise AlreadyExistsError(newname, self.path.parent())
        try:
            self.path.rename(destpath)
        except EnvironmentError:
            raise OperationError(self)
        if not destpath.exists():
            raise OperationError(self)
        self.path = destpath

    def get_display_info(self, group, delta):
        """Returns a display-ready dict of dupe's data.
        """
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
        return self.path.parent()


class Folder(File):
    """A wrapper around a folder path.

    It has the size/md5 info of a File, but it's value are the sum of its subitems.
    """

    __slots__ = File.__slots__ + ("_subfolders",)

    def __init__(self, path):
        File.__init__(self, path)
        self._subfolders = None

    def _all_items(self):
        folders = self.subfolders
        files = get_files(self.path)
        return folders + files

    def _read_info(self, field):
        if field in {"size", "mtime"}:
            size = sum((f.size for f in self._all_items()), 0)
            self.size = size
            stats = self.path.stat()
            self.mtime = nonone(stats.st_mtime, 0)
        elif field in {"md5", "md5partial"}:
            # What's sensitive here is that we must make sure that subfiles'
            # md5 are always added up in the same order, but we also want a
            # different md5 if a file gets moved in a different subdirectory.
            def get_dir_md5_concat():
                items = self._all_items()
                items.sort(key=lambda f: f.path)
                md5s = [getattr(f, field) for f in items]
                return b"".join(md5s)

            md5 = hashlib.md5(get_dir_md5_concat())
            digest = md5.digest()
            setattr(self, field, digest)

    @property
    def subfolders(self):
        if self._subfolders is None:
            subfolders = [
                p for p in self.path.listdir() if not p.islink() and p.isdir()
            ]
            self._subfolders = [self.__class__(p) for p in subfolders]
        return self._subfolders

    @classmethod
    def can_handle(cls, path):
        return not path.islink() and path.isdir()


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
        for path in path.listdir():
            file = get_file(path, fileclasses=fileclasses)
            if file is not None:
                result.append(file)
        return result
    except EnvironmentError:
        raise InvalidPath(path)
