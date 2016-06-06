# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from cocoa import proxy
from core.pe import _block_osx
from core.pe.photo import Photo as PhotoBase

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