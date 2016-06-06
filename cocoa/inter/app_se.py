# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

import logging
import os.path as op

from hscommon.path import Path, pathify
from cocoa import proxy

from core.directories import Directories as DirectoriesBase, DirectoryState
import core.pe.photo
from core.pe import _block_osx
from core.pe.photo import Photo as PhotoBase
from core.app import DupeGuru as DupeGuruBase, AppMode
from core.se import fs
from .app import PyDupeGuruBase

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
    

class Photo(PhotoBase):
    HANDLED_EXTS = PhotoBase.HANDLED_EXTS.copy()
    HANDLED_EXTS.update({'psd', 'nef', 'cr2', 'orf'})
    
    def _plat_get_dimensions(self):
        return _block_osx.get_image_size(str(self.path))
    
    def _plat_get_blocks(self, block_count_per_side, orientation):
        try:
            blocks = _block_osx.getblocks(str(self.path), block_count_per_side, orientation)
        except Exception as e:
            raise IOError('The reading of "%s" failed with "%s"' % (str(self.path), str(e)))
        if not blocks:
            raise IOError('The picture %s could not be read' % str(self.path))
        return blocks
    
    def _get_exif_timestamp(self):
        exifdata = proxy.readExifData_(str(self.path))
        if exifdata:
            try:
                return exifdata['{Exif}']['DateTimeOriginal']
            except KeyError:
                return ''
        else:
            return ''


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
    

class DupeGuru(DupeGuruBase):
    def __init__(self, view):
        DupeGuruBase.__init__(self, view)
        self.directories = Directories()
    
    def selected_dupe_path(self):
        if not self.selected_dupes:
            return None
        return self.selected_dupes[0].path
    
    def selected_dupe_ref_path(self):
        if not self.selected_dupes:
            return None
        ref = self.results.get_group_of_duplicate(self.selected_dupes[0]).ref
        if ref is self.selected_dupes[0]: # we don't want the same pic to be displayed on both sides
            return None
        return ref.path
    
    def _get_fileclasses(self):
        result = DupeGuruBase._get_fileclasses(self)
        if self.app_mode == AppMode.Standard:
            result = [Bundle] + result
        return result

class PyDupeGuru(PyDupeGuruBase):
    def __init__(self):
        core.pe.photo.PLAT_SPECIFIC_PHOTO_CLASS = Photo
        self._init(DupeGuru)

    
