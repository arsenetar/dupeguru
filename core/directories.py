# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
import os
import time
from pathlib import Path
from xml.etree import ElementTree as ET

from core import fs
from hscommon.jobprogress import job
from hscommon.trans import tr
from hscommon.util import FileOrPath

__all__ = [
    "Directories",
    "DirectoryState",
    "AlreadyThereError",
    "InvalidPathError",
]


class DirectoryState:
    """Enum describing how a folder should be considered.

    * DirectoryState.Normal: Scan all files normally
    * DirectoryState.Reference: Scan files, but make sure never to delete any of them
    * DirectoryState.Excluded: Don't scan this folder
    """

    NORMAL = 0
    REFERENCE = 1
    EXCLUDED = 2


class AlreadyThereError(Exception):
    """The path being added is already in the directory list"""


class InvalidPathError(Exception):
    """The path being added is invalid"""


class Directories:
    """Holds user folder selection.

    Manages the selection that the user make through the folder selection dialog. It also manages
    folder states, and how recursion applies to them.

    Then, when the user starts the scan, :meth:`get_files` is called to retrieve all files (wrapped
    in :mod:`core.fs`) that have to be scanned according to the chosen folders/states.
    """

    # ---Override
    def __init__(self, exclude_list=None):
        self._dirs = []
        # {path: state}
        self.states = {}
        self._exclude_list = exclude_list

    def __contains__(self, path):
        for p in self._dirs:
            if path == p or p in path.parents:
                return True
        return False

    def __delitem__(self, key):
        self._dirs.__delitem__(key)

    def __getitem__(self, key):
        return self._dirs.__getitem__(key)

    def __len__(self):
        return len(self._dirs)

    # ---Private
    def _default_state_for_path(self, path):
        # New logic with regex filters
        if self._exclude_list is not None and self._exclude_list.mark_count > 0:
            # We iterate even if we only have one item here
            for denied_path_re in self._exclude_list.compiled:
                if denied_path_re.match(str(path.name)):
                    return DirectoryState.EXCLUDED
            return DirectoryState.NORMAL
        # Override this in subclasses to specify the state of some special folders.
        if path.name.startswith("."):
            return DirectoryState.EXCLUDED
        return DirectoryState.NORMAL

    def _get_files(self, from_path, fileclasses, j=job.nulljob, batch_buf=None, counter_buf=None):
        root_path = Path(from_path)
        is_top_level = batch_buf is None
        if is_top_level:
            batch_buf = []
            counter_buf = [0]

        def flush_batch():
            if batch_buf:
                fs.filesdb.snapshot_files_batch(batch_buf)
                batch_buf.clear()

        if is_top_level and fs.filesdb._is_rust and fs.filesdb.enable_directory_cache:
            try:
                from core import dupeguru_rust

                rust_files = dupeguru_rust.collect_files_parallel([str(from_path)], 0, None)
                if rust_files:
                    fs.filesdb.snapshot_files_batch(rust_files)
                    fs.filesdb.mark_directory_scanned(root_path)
            except Exception as e:
                logging.warning(f"Rust parallel crawler fallback: {e}")

        if fs.filesdb.enable_directory_cache and fs.filesdb.is_directory_scanned(root_path):
            cache_count = 0
            for f_data in fs.filesdb.get_files_in_directory(root_path):
                cache_count += 1
                if cache_count % 1000 == 0:
                    j.check_if_cancelled()
                    j.set_progress(-1, tr("Loading cached files: {}...").format(cache_count))
                p = fs.Path(f_data["path"])
                file = fs.get_file(p, fileclasses=fileclasses, skip_disk_check=True)
                if file:
                    file.size = f_data["size"]
                    file.mtime = f_data["mtime_ns"] / 1e9
                    state = self.get_state(root_path)
                    file.is_ref = state == DirectoryState.REFERENCE
                    yield file
            return

        try:
            with os.scandir(from_path) as iter:
                state = self.get_state(root_path)
                # if we have no un-excluded dirs under this directory skip going deeper
                skip_dirs = state == DirectoryState.EXCLUDED and not any(
                    p.parts[: len(root_path.parts)] == root_path.parts for p in self.states
                )
                count = 0
                for item in iter:
                    j.check_if_cancelled()
                    try:
                        if item.is_dir():
                            if skip_dirs:
                                continue
                            yield from self._get_files(
                                item.path, fileclasses, j, batch_buf=batch_buf, counter_buf=counter_buf
                            )
                            continue
                        elif state == DirectoryState.EXCLUDED:
                            continue
                        # File excluding or not
                        if (
                            self._exclude_list is None
                            or not self._exclude_list.mark_count
                            or not self._exclude_list.is_excluded(str(from_path), item.name)
                        ):
                            file = fs.get_file(item, fileclasses=fileclasses)
                            if file:
                                file.is_ref = state == DirectoryState.REFERENCE
                                if fs.filesdb.enable_directory_cache:
                                    batch_buf.append((file.path, file.size, file.mtime))
                                    if len(batch_buf) >= 1000:
                                        flush_batch()
                                count += 1
                                counter_buf[0] += 1
                                if counter_buf[0] % 1000 == 0:
                                    j.set_progress(-1, tr("Scanning: Collected {} files...").format(counter_buf[0]))
                                yield file
                    except (OSError, fs.InvalidPath):
                        pass

                if is_top_level:
                    flush_batch()

                if fs.filesdb.enable_directory_cache:
                    fs.filesdb.mark_directory_scanned(root_path)
                logging.debug(
                    "Collected %d files in folder %s",
                    count,
                    str(root_path),
                )
        except OSError:
            pass
        finally:
            if is_top_level:
                flush_batch()

    def _get_folders(self, from_folder, j):
        j.check_if_cancelled()
        try:
            for subfolder in from_folder.subfolders:
                yield from self._get_folders(subfolder, j)
            state = self.get_state(from_folder.path)
            if state != DirectoryState.EXCLUDED:
                from_folder.is_ref = state == DirectoryState.REFERENCE
                logging.debug("Yielding Folder %r state: %d", from_folder, state)
                yield from_folder
        except (OSError, fs.InvalidPath):
            pass

    # ---Public
    def add_path(self, path):
        """Adds ``path`` to self, if not already there.

        Raises :exc:`AlreadyThereError` if ``path`` is already in self. If path is a directory
        containing some of the directories already present in self, ``path`` will be added, but all
        directories under it will be removed. Can also raise :exc:`InvalidPathError` if ``path``
        does not exist.

        :param Path path: path to add
        """
        if path in self:
            raise AlreadyThereError()
        if not path.exists():
            raise InvalidPathError()
        removed = [p for p in self._dirs if path in p.parents]
        self._dirs = [p for p in self._dirs if p not in removed]
        for r in removed:
            self.states.pop(r, None)
        self._dirs.append(path)

    def clear(self):
        """Removes all directories and reset state mappings."""
        self._dirs = []
        self._states = {}

    @staticmethod
    def get_subfolders(path):
        """Returns a sorted list of paths corresponding to subfolders in ``path``.

        :param Path path: get subfolders from there
        :rtype: list of Path
        """
        try:
            subpaths = [p for p in path.glob("*") if p.is_dir()]
            subpaths.sort(key=lambda x: x.name.lower())
            return subpaths
        except OSError:
            return []

    def get_files(self, fileclasses=None, j=job.nulljob):
        """Returns a list of all files that are not excluded."""
        if fileclasses is None:
            fileclasses = [fs.File]

        for path in self._dirs:
            if fs.filesdb.enable_directory_cache and fs.filesdb.is_directory_scanned(path):
                cache_count = 0
                for f_data in fs.filesdb.get_files_in_directory(path):
                    cache_count += 1
                    if cache_count % 1000 == 0:
                        j.check_if_cancelled()
                        j.set_progress(-1, tr("Loading cached files: {}...").format(cache_count))
                    p = fs.Path(f_data["path"])
                    file = fs.get_file(p, fileclasses=fileclasses, skip_disk_check=True)
                    if file:
                        file.size = f_data["size"]
                        file.mtime = f_data["mtime_ns"] / 1e9
                        file.is_ref = self.get_state(path) == DirectoryState.REFERENCE
                        yield file
            else:
                for file in self._get_files(path, fileclasses=fileclasses, j=j):
                    yield file

    def populate_cache(self, j=job.nulljob):
        """Populate SQLite database cache for all target directories in parallel using Rust."""
        if not fs.filesdb.enable_directory_cache:
            return

        unscanned_dirs = [str(d) for d in self._dirs if not fs.filesdb.is_directory_scanned(d)]
        if not unscanned_dirs:
            return

        j.set_progress(-1, tr("Collecting files in parallel across {} directories...").format(len(unscanned_dirs)))
        if fs.filesdb._is_rust:
            try:
                from core import dupeguru_rust

                t0 = time.time()
                rust_files = dupeguru_rust.collect_files_parallel(unscanned_dirs, 0, None)
                if rust_files:
                    fs.filesdb.snapshot_files_batch(rust_files)
                    for d in self._dirs:
                        fs.filesdb.mark_directory_scanned(d)
                    logging.info(
                        "Parallel collected %d files across %d dirs in %.2fs",
                        len(rust_files),
                        len(unscanned_dirs),
                        time.time() - t0,
                    )
                    return
            except Exception as e:
                logging.warning(f"Rust multi-dir parallel crawler fallback: {e}")

        # Fallback python collection
        for path in self._dirs:
            if not fs.filesdb.is_directory_scanned(path):
                for _ in self._get_files(path, fileclasses=[fs.File], j=j):
                    pass

    def get_folders(self, folderclass=None, j=job.nulljob):
        """Returns a list of all folders that are not excluded.

        Returned folders also have their ``is_ref`` attr set if applicable.
        """
        if folderclass is None:
            folderclass = fs.Folder
        folder_count = 0
        for path in self._dirs:
            from_folder = folderclass(path)
            for folder in self._get_folders(from_folder, j):
                folder_count += 1
                if not isinstance(j, job.NullJob):
                    j.set_progress(-1, tr("Scanning {}: Collected {} folders...").format(path.name, folder_count))
                yield folder

    def get_state(self, path):
        """Returns the state of ``path``.

        :rtype: :class:`DirectoryState`
        """
        # direct match? easy result.
        if path in self.states:
            return self.states[path]
        state = self._default_state_for_path(path)
        # Save non-default states in cache, necessary for _get_files()
        if state != DirectoryState.NORMAL:
            self.states[path] = state
            return state
        # find the longest parent path that is in states and return that state if found
        # NOTE: path.parents is ordered longest to shortest
        for parent_path in path.parents:
            if parent_path in self.states:
                return self.states[parent_path]
        return state

    def has_any_file(self, fileclasses=None):
        """Returns whether selected folders contain any file quickly without triggering full directory crawls."""
        if fs.filesdb.enable_directory_cache:
            try:
                with fs.filesdb.lock, fs.filesdb.conn as conn:
                    row = conn.execute("SELECT 1 FROM files LIMIT 1").fetchone()
                    if row:
                        return True
            except Exception:
                pass
        for path in self._dirs:
            try:
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file() or entry.is_dir():
                            return True
            except OSError:
                pass
        return False

    def load_from_file(self, infile):
        """Load folder selection from ``infile``.

        :param file infile: path or file pointer to XML generated through :meth:`save_to_file`
        """
        try:
            root = ET.parse(infile).getroot()
        except Exception:
            return
        for rdn in root.iter("root_directory"):
            attrib = rdn.attrib
            if "path" not in attrib:
                continue
            path = attrib["path"]
            try:
                self.add_path(Path(path))
            except (AlreadyThereError, InvalidPathError):
                pass
        for sn in root.iter("state"):
            attrib = sn.attrib
            if not ("path" in attrib and "value" in attrib):
                continue
            path = attrib["path"]
            state = attrib["value"]
            self.states[Path(path)] = int(state)

    def save_to_file(self, outfile):
        """Save folder selection as XML to ``outfile``.

        :param file outfile: path or file pointer to XML file to save to.
        """
        with FileOrPath(outfile, "wb") as fp:
            root = ET.Element("directories")
            for root_path in self:
                root_path_node = ET.SubElement(root, "root_directory")
                root_path_node.set("path", str(root_path))
            for path, state in self.states.items():
                state_node = ET.SubElement(root, "state")
                state_node.set("path", str(path))
                state_node.set("value", str(state))
            tree = ET.ElementTree(root)
            tree.write(fp, encoding="utf-8")

    def set_state(self, path, state):
        """Set the state of folder at ``path``.

        :param Path path: path of the target folder
        :param state: state to set folder to
        :type state: :class:`DirectoryState`
        """
        if self.get_state(path) == state:
            return
        for iter_path in list(self.states.keys()):
            if path in iter_path.parents:
                del self.states[iter_path]
        self.states[path] = state
