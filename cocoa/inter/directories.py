# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from cocoa import proxy
from hscommon.path import Path, pathify
from core.se import fs
from core.directories import Directories as DirectoriesBase, DirectoryState

def is_bundle(str_path):
    uti = proxy.getUTI_(str_path)
    if uti is None:
        logging.warning('There was an error trying to detect the UTI of %s', str_path)
    return proxy.type_conformsToType_(uti, 'com.apple.bundle') or proxy.type_conformsToType_(uti, 'com.apple.package')

class Bundle(fs.Folder):
    @classmethod
    @pathify
    def can_handle(cls, path: Path):
        return not path.islink() and path.isdir() and is_bundle(str(path))

class Directories(DirectoriesBase):
    ROOT_PATH_TO_EXCLUDE = list(map(Path, ['/Library', '/Volumes', '/System', '/bin', '/sbin', '/opt', '/private', '/dev']))
    HOME_PATH_TO_EXCLUDE = [Path('Library')]

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
            yield from DirectoriesBase._get_folders(self, from_folder, j)
    
    @staticmethod
    def get_subfolders(path):
        result = DirectoriesBase.get_subfolders(path)
        return [p for p in result if not is_bundle(str(p))]
