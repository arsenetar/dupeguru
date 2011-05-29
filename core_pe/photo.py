# Created By: Virgil Dupras
# Created On: 2011-05-29
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import get_file_ext
from core import fs

class Photo(fs.File):
    INITIAL_INFO = fs.File.INITIAL_INFO.copy()
    INITIAL_INFO.update({
        'dimensions': (0,0),
    })
    # These extensions are supported on all platforms
    HANDLED_EXTS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif'}
    
    @classmethod
    def can_handle(cls, path):
        return fs.File.can_handle(path) and get_file_ext(path[-1]) in cls.HANDLED_EXTS
    
    def get_blocks(self, block_count_per_side):
        raise NotImplementedError()
    
