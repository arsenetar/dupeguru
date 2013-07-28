# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import os.path as op

from hscommon import io
from hscommon.path import Path
from cocoa import proxy

from core.scanner import ScanType
from core import fs
from core.directories import Directories as DirectoriesBase, DirectoryState
from core_se.app import DupeGuru as DupeGuruBase
from core_se.fs import File
from .app import PyDupeGuruBase

def is_bundle(str_path):
    uti = proxy.getUTI_(str_path)
    if uti is None:
        logging.warning('There was an error trying to detect the UTI of %s', str_path)
    return proxy.type_conformsToType_(uti, 'com.apple.bundle') or proxy.type_conformsToType_(uti, 'com.apple.package')

class Bundle(fs.Folder):
    @classmethod
    def can_handle(cls, path):
        return not io.islink(path) and io.isdir(path) and is_bundle(str(path))
    

class Directories(DirectoriesBase):
    ROOT_PATH_TO_EXCLUDE = list(map(Path, ['/Library', '/Volumes', '/System', '/bin', '/sbin', '/opt', '/private', '/dev']))
    HOME_PATH_TO_EXCLUDE = [Path('Library')]
    def __init__(self):
        DirectoriesBase.__init__(self, fileclasses=[Bundle, File])
    
    def _default_state_for_path(self, path):
        result = DirectoriesBase._default_state_for_path(self, path)
        if result is not None:
            return result
        if path in self.ROOT_PATH_TO_EXCLUDE:
            return DirectoryState.Excluded
        if path[:2] == Path('/Users') and path[3:] in self.HOME_PATH_TO_EXCLUDE:
            return DirectoryState.Excluded
    
    def _get_folders(self, from_folder, j):
        # We don't want to scan bundle's subfolder even in Folders mode. Bundle's integrity has to
        # stay intact.
        if is_bundle(str(from_folder.path)):
            # just yield the current folder and bail
            state = self.get_state(from_folder.path)
            if state != DirectoryState.Excluded:
                from_folder.is_ref = state == DirectoryState.Reference
                yield from_folder
            return
        else:
            for folder in DirectoriesBase._get_folders(self, from_folder, j):
                yield folder
    
    @staticmethod
    def get_subfolders(path):
        result = DirectoriesBase.get_subfolders(path)
        return [p for p in result if not is_bundle(str(p))]
    

class DupeGuru(DupeGuruBase):
    def __init__(self, view, appdata):
        appdata = op.join(appdata, 'dupeGuru')
        DupeGuruBase.__init__(self, view, appdata)
        self.directories = Directories()
    

class PyDupeGuru(PyDupeGuruBase):
    def __init__(self):
        self._init(DupeGuru)
    
    #---Properties
    def setMinMatchPercentage_(self, percentage: int):
        self.model.scanner.min_match_percentage = int(percentage)
    
    def setScanType_(self, scan_type: int):
        try:
            self.model.scanner.scan_type = [
                ScanType.Filename,
                ScanType.Contents,
                ScanType.Folders,
            ][scan_type]
        except IndexError:
            pass
    
    def setWordWeighting_(self, words_are_weighted: bool):
        self.model.scanner.word_weighting = words_are_weighted
    
    def setMatchSimilarWords_(self, match_similar_words: bool):
        self.model.scanner.match_similar_words = match_similar_words
    
    def setSizeThreshold_(self, size_threshold: int):
        self.model.scanner.size_threshold = size_threshold
    
