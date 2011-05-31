# Created By: Virgil Dupras
# Created On: 2011-05-29
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon import io
from hscommon.util import get_file_ext
from core import fs
from . import exif

class Photo(fs.File):
    INITIAL_INFO = fs.File.INITIAL_INFO.copy()
    INITIAL_INFO.update({
        'dimensions': (0,0),
    })
    # These extensions are supported on all platforms
    HANDLED_EXTS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif'}
    
    def _plat_get_dimensions(self):
        raise NotImplementedError()
    
    def _plat_get_blocks(self, block_count_per_side, orientation):
        raise NotImplementedError()
    
    def _get_orientation(self):
        if not hasattr(self, '_cached_orientation'):
            try:
                with io.open(self.path, 'rb') as fp:
                    exifdata = exif.get_fields(fp)
                    # the value is a list (probably one-sized) of ints
                    orientations = exifdata['Orientation']
                    self._cached_orientation = orientations[0]
            except Exception: # Couldn't read EXIF data, no transforms
                self._cached_orientation = 0
        return self._cached_orientation
    
    @classmethod
    def can_handle(cls, path):
        return fs.File.can_handle(path) and get_file_ext(path[-1]) in cls.HANDLED_EXTS
    
    def _read_info(self, field):
        fs.File._read_info(self, field)
        if field == 'dimensions':
            self.dimensions = self._plat_get_dimensions()
            if self._get_orientation() in {5, 6, 7, 8}:
                self.dimensions = (self.dimensions[1], self.dimensions[0])
    
    def get_blocks(self, block_count_per_side):
        return self._plat_get_blocks(block_count_per_side, self._get_orientation())
    
