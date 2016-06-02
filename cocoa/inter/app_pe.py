# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from cocoa import proxy

from core.scanner import ScanType
from core_pe import _block_osx
from core_pe.photo import Photo as PhotoBase
from core_pe.app import DupeGuru as DupeGuruBase
from .app import PyDupeGuruBase


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


class DupeGuruPE(DupeGuruBase):
    def __init__(self, view):
        DupeGuruBase.__init__(self, view)
        self.fileclasses = [Photo]

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


class PyDupeGuru(PyDupeGuruBase):
    def __init__(self):
        self._init(DupeGuruPE)
    
    def clearPictureCache(self):
        self.model.clear_picture_cache()
    
    #---Information    
    def getSelectedDupePath(self) -> str:
        return str(self.model.selected_dupe_path())
    
    def getSelectedDupeRefPath(self) -> str:
        return str(self.model.selected_dupe_ref_path())
    
    #---Properties
    def setScanType_(self, scan_type: int):
        try:
            self.model.options['scan_type'] = [
                ScanType.FuzzyBlock,
                ScanType.ExifTimestamp,
            ][scan_type]
        except IndexError:
            pass
    
    def setMatchScaled_(self, match_scaled: bool):
        self.model.options['match_scaled'] = match_scaled
    
    def setMinMatchPercentage_(self, percentage: int):
        self.model.options['threshold'] = percentage
