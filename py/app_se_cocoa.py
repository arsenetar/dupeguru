#!/usr/bin/env python
# Unit Name: app_se_cocoa
# Created By: Virgil Dupras
# Created On: 2009-05-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from hsfs.phys import Directory as DirectoryBase
from hsfs.phys.bundle import Bundle
from hsutil.path import Path
from hsutil.str import get_file_ext


from . import app_cocoa, data
from .directories import Directories as DirectoriesBase, STATE_EXCLUDED

class DGDirectory(DirectoryBase):
    def _create_sub_dir(self, name, with_parent = True):
        ext = get_file_ext(name)
        if ext == 'app':
            parent = self if with_parent else None
            return Bundle(parent, name)
        else:
            return super(DGDirectory, self)._create_sub_dir(name, with_parent)
    

class Directories(DirectoriesBase):
    ROOT_PATH_TO_EXCLUDE = map(Path, ['/Library', '/Volumes', '/System', '/bin', '/sbin', '/opt', '/private'])
    HOME_PATH_TO_EXCLUDE = [Path('Library')]
    def __init__(self):
        DirectoriesBase.__init__(self)
        self.dirclass = DGDirectory
    
    def _default_state_for_path(self, path):
        result = DirectoriesBase._default_state_for_path(self, path)
        if result is not None:
            return result
        if path in self.ROOT_PATH_TO_EXCLUDE:
            return STATE_EXCLUDED
        if path[:2] == Path('/Users') and path[3:] in self.HOME_PATH_TO_EXCLUDE:
            return STATE_EXCLUDED
    

class DupeGuru(app_cocoa.DupeGuru):
    def __init__(self):
        app_cocoa.DupeGuru.__init__(self, data, 'dupeguru', appid=4)
        self.directories = Directories()
    
