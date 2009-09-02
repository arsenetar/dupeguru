# Created By: Virgil Dupras
# Created On: 2009-05-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging

from AppKit import *

from hsfs.phys import Directory as DirectoryBase
from hsfs.phys.bundle import Bundle
from hsutil.path import Path
from hsutil.misc import extract
from hsutil.str import get_file_ext

from . import app_cocoa, data
from .directories import Directories as DirectoriesBase, STATE_EXCLUDED

def is_bundle(path):
    sw = NSWorkspace.sharedWorkspace()
    uti, error = sw.typeOfFile_error_(path)
    if error is not None:
        logging.warning(u'There was an error trying to detect the UTI of %s', path)
    return sw.type_conformsToType_(uti, 'com.apple.bundle') or sw.type_conformsToType_(uti, 'com.apple.package')

class DGDirectory(DirectoryBase):
    def _create_sub_file(self, name, with_parent=True):
        ext = get_file_ext(name)
        if is_bundle(unicode(self.path + name)):
            parent = self if with_parent else None
            return Bundle(parent, name)
        else:
            return super(DGDirectory, self)._create_sub_file(name, with_parent)
    
    def _fetch_subitems(self):
        subdirs, subfiles = super(DGDirectory, self)._fetch_subitems()
        apps, normal_dirs = extract(lambda name: is_bundle(unicode(self.path + name)), subdirs)
        subfiles += apps
        return normal_dirs, subfiles
    

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
    
