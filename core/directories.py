# Created By: Virgil Dupras
# Created On: 2006/02/27
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from xml.etree import ElementTree as ET
import logging

from jobprogress import job
from hscommon.path import Path
from hscommon.util import FileOrPath

from . import fs

__all__ = [
    'Directories',
    'DirectoryState',
    'AlreadyThereError',
    'InvalidPathError',
]

class DirectoryState:
    """Enum describing how a folder should be considered.
    
    * DirectoryState.Normal: Scan all files normally
    * DirectoryState.Reference: Scan files, but make sure never to delete any of them
    * DirectoryState.Excluded: Don't scan this folder
    """
    Normal = 0
    Reference = 1
    Excluded = 2

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
    #---Override
    def __init__(self, fileclasses=[fs.File]):
        self._dirs = []
        self.states = {}
        self.fileclasses = fileclasses
        self.folderclass = fs.Folder
    
    def __contains__(self, path):
        for p in self._dirs:
            if path in p:
                return True
        return False
    
    def __delitem__(self,key):
        self._dirs.__delitem__(key)
    
    def __getitem__(self,key):
        return self._dirs.__getitem__(key)
    
    def __len__(self):
        return len(self._dirs)
    
    #---Private
    def _default_state_for_path(self, path):
        # Override this in subclasses to specify the state of some special folders.
        if path.name.startswith('.'): # hidden
            return DirectoryState.Excluded
    
    def _get_files(self, from_path, j):
        j.check_if_cancelled()
        state = self.get_state(from_path)
        if state == DirectoryState.Excluded:
            # Recursively get files from folders with lots of subfolder is expensive. However, there
            # might be a subfolder in this path that is not excluded. What we want to do is to skim
            # through self.states and see if we must continue, or we can stop right here to save time
            if not any(p[:len(from_path)] == from_path for p in self.states):
                return
        try:
            filepaths = set()
            if state != DirectoryState.Excluded:
                found_files = fs.get_files(from_path, fileclasses=self.fileclasses)
                logging.debug("Collected %d files in folder %s", len(found_files), str(from_path))
                for file in found_files:
                    file.is_ref = state == DirectoryState.Reference
                    filepaths.add(file.path)
                    yield file
            # it's possible that a folder (bundle) gets into the file list. in that case, we don't want to recurse into it
            subfolders = [p for p in from_path.listdir() if not p.islink() and p.isdir() and p not in filepaths]
            for subfolder in subfolders:
                for file in self._get_files(subfolder, j):
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
            if state != DirectoryState.Excluded:
                from_folder.is_ref = state == DirectoryState.Reference
                logging.debug("Yielding Folder %r state: %d", from_folder, state)
                yield from_folder
        except (EnvironmentError, fs.InvalidPath):
            pass
    
    #---Public
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
        self._dirs = [p for p in self._dirs if p not in path]
        self._dirs.append(path)
    
    @staticmethod
    def get_subfolders(path):
        """Returns a sorted list of paths corresponding to subfolders in ``path``.
        
        :param Path path: get subfolders from there
        :rtype: list of Path
        """
        try:
            subpaths = [p for p in path.listdir() if p.isdir()]
            subpaths.sort(key=lambda x:x.name.lower())
            return subpaths
        except EnvironmentError:
            return []
    
    def get_files(self, j=job.nulljob):
        """Returns a list of all files that are not excluded.
        
        Returned files also have their ``is_ref`` attr set if applicable.
        """
        for path in self._dirs:
            for file in self._get_files(path, j):
                yield file
    
    def get_folders(self, j=job.nulljob):
        """Returns a list of all folders that are not excluded.
        
        Returned folders also have their ``is_ref`` attr set if applicable.
        """
        for path in self._dirs:
            from_folder = self.folderclass(path)
            for folder in self._get_folders(from_folder, j):
                yield folder
    
    def get_state(self, path):
        """Returns the state of ``path``.
        
        :rtype: :class:`DirectoryState`
        """
        if path in self.states:
            return self.states[path]
        default_state = self._default_state_for_path(path)
        if default_state is not None:
            return default_state
        parent = path.parent()
        if parent in self:
            return self.get_state(parent)
        else:
            return DirectoryState.Normal
    
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
        for rdn in root.getiterator('root_directory'):
            attrib = rdn.attrib
            if 'path' not in attrib:
                continue
            path = attrib['path']
            try:
                self.add_path(Path(path))
            except (AlreadyThereError, InvalidPathError):
                pass
        for sn in root.getiterator('state'):
            attrib = sn.attrib
            if not ('path' in attrib and 'value' in attrib):
                continue
            path = attrib['path']
            state = attrib['value']
            self.set_state(Path(path), int(state))
    
    def save_to_file(self, outfile):
        """Save folder selection as XML to ``outfile``.
        
        :param file outfile: path or file pointer to XML file to save to.
        """
        with FileOrPath(outfile, 'wb') as fp:
            root = ET.Element('directories')
            for root_path in self:
                root_path_node = ET.SubElement(root, 'root_directory')
                root_path_node.set('path', str(root_path))
            for path, state in self.states.items():
                state_node = ET.SubElement(root, 'state')
                state_node.set('path', str(path))
                state_node.set('value', str(state))
            tree = ET.ElementTree(root)
            tree.write(fp, encoding='utf-8')
    
    def set_state(self, path, state):
        """Set the state of folder at ``path``.
        
        :param Path path: path of the target folder
        :param state: state to set folder to
        :type state: :class:`DirectoryState`
        """
        if self.get_state(path) == state:
            return
        # we don't want to needlessly fill self.states. if get_state returns the same thing
        # without an explicit entry, remove that entry
        if path in self.states:
            del self.states[path]
            if self.get_state(path) == state: # no need for an entry
                return
        self.states[path] = state
    
