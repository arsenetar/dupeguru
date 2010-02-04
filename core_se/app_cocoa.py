# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

import logging

from hsutil import io
from hsutil.path import Path
from hsutil.cocoa.objcmin import NSWorkspace

from core import fs
from core.app_cocoa import DupeGuru as DupeGuruBase
from core.directories import Directories as DirectoriesBase, STATE_EXCLUDED
from . import data
from .fs import Bundle as BundleBase

def is_bundle(str_path):
    sw = NSWorkspace.sharedWorkspace()
    uti, error = sw.typeOfFile_error_(str_path, None)
    if error is not None:
        logging.warning(u'There was an error trying to detect the UTI of %s', str_path)
    return sw.type_conformsToType_(uti, 'com.apple.bundle') or sw.type_conformsToType_(uti, 'com.apple.package')

class Bundle(BundleBase):
    @classmethod
    def can_handle(cls, path):
        return not io.islink(path) and io.isdir(path) and is_bundle(unicode(path))
    

class Directories(DirectoriesBase):
    ROOT_PATH_TO_EXCLUDE = map(Path, ['/Library', '/Volumes', '/System', '/bin', '/sbin', '/opt', '/private', '/dev'])
    HOME_PATH_TO_EXCLUDE = [Path('Library')]
    def __init__(self):
        DirectoriesBase.__init__(self, fileclasses=[Bundle, fs.File])
    
    def _default_state_for_path(self, path):
        result = DirectoriesBase._default_state_for_path(self, path)
        if result is not None:
            return result
        if path in self.ROOT_PATH_TO_EXCLUDE:
            return STATE_EXCLUDED
        if path[:2] == Path('/Users') and path[3:] in self.HOME_PATH_TO_EXCLUDE:
            return STATE_EXCLUDED
    

class DupeGuru(DupeGuruBase):
    def __init__(self):
        DupeGuruBase.__init__(self, data, 'dupeGuru', appid=4)
        self.directories = Directories()
    
