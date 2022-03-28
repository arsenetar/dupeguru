# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
from xml.etree import ElementTree as ET
import logging
from pathlib import Path

from hscommon.jobprogress import job
from hscommon.util import FileOrPath
from hscommon.trans import tr

from . import fs

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
            # return # We still use the old logic to force state on hidden dirs
        # Override this in subclasses to specify the state of some special folders.
        if path.name.startswith("."):
            return DirectoryState.EXCLUDED

    def _get_files(self, from_path, fileclasses, j):
        for root, dirs, files in os.walk(str(from_path)):
            j.check_if_cancelled()
            root_path = Path(root)
            state = self.get_state(root_path)
            if state == DirectoryState.EXCLUDED and not any(
                p.parts[: len(root_path.parts)] == root_path.parts for p in self.states
            ):
                # Recursively get files from folders with lots of subfolder is expensive. However, there
                # might be a subfolder in this path that is not excluded. What we want to do is to skim
                # through self.states and see if we must continue, or we can stop right here to save time
                del dirs[:]
            try:
                if state != DirectoryState.EXCLUDED:
                    # Old logic
                    if self._exclude_list is None or not self._exclude_list.mark_count:
                        found_files = [fs.get_file(root_path.joinpath(f), fileclasses=fileclasses) for f in files]
                    else:
                        found_files = []
                        # print(f"len of files: {len(files)} {files}")
                        for f in files:
                            if not self._exclude_list.is_excluded(root, f):
                                found_files.append(fs.get_file(root_path.joinpath(f), fileclasses=fileclasses))
                    found_files = [f for f in found_files if f is not None]
                    # In some cases, directories can be considered as files by dupeGuru, which is
                    # why we have this line below. In fact, there only one case: Bundle files under
                    # OS X... In other situations, this forloop will do nothing.
                    for d in dirs[:]:
                        f = fs.get_file(root_path.joinpath(d), fileclasses=fileclasses)
                        if f is not None:
                            found_files.append(f)
                            dirs.remove(d)
                    logging.debug(
                        "Collected %d files in folder %s",
                        len(found_files),
                        str(root_path),
                    )
                    for file in found_files:
                        file.is_ref = state == DirectoryState.REFERENCE
                        yield file
            except (EnvironmentError, fs.InvalidPath):
                pass

    def _get_folders(self, from_folder, j):
        j.check_if_cancelled()
        try:
            for subfolder in from_folder.subfolders:
                for folder in self._get_folders(subfolder, j):
                    yield folder
            state = self.get_state(from_folder.path)
            if state != DirectoryState.EXCLUDED:
                from_folder.is_ref = state == DirectoryState.REFERENCE
                logging.debug("Yielding Folder %r state: %d", from_folder, state)
                yield from_folder
        except (EnvironmentError, fs.InvalidPath):
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
        self._dirs = [p for p in self._dirs if path not in p.parents]
        self._dirs.append(path)

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
        except EnvironmentError:
            return []

    def get_files(self, fileclasses=None, j=job.nulljob):
        """Returns a list of all files that are not excluded.

        Returned files also have their ``is_ref`` attr set if applicable.
        """
        if fileclasses is None:
            fileclasses = [fs.File]
        file_count = 0
        for path in self._dirs:
            for file in self._get_files(path, fileclasses=fileclasses, j=j):
                file_count += 1
                if type(j) != job.NullJob:
                    j.set_progress(-1, tr("Collected {} files to scan").format(file_count))
                yield file

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
                if type(j) != job.NullJob:
                    j.set_progress(-1, tr("Collected {} folders to scan").format(folder_count))
                yield folder

    def get_state(self, path):
        """Returns the state of ``path``.

        :rtype: :class:`DirectoryState`
        """
        # direct match? easy result.
        if path in self.states:
            return self.states[path]
        state = self._default_state_for_path(path) or DirectoryState.NORMAL
        # Save non-default states in cache, necessary for _get_files()
        if state != DirectoryState.NORMAL:
            self.states[path] = state
            return state

        prevlen = 0
        # we loop through the states to find the longest matching prefix
        # if the parent has a state in cache, return that state
        for p, s in self.states.items():
            if p in path.parents and len(p.parts) > prevlen:
                prevlen = len(p.parts)
                state = s
        return state

    def has_any_file(self):
        """Returns whether selected folders contain any file.

        Because it stops at the first file it finds, it's much faster than get_files().

        :rtype: bool
        """
        try:
            next(self.get_files())
            return True
        except StopIteration:
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
