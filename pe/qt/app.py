#!/usr/bin/env python
# Unit Name: app
# Created By: Virgil Dupras
# Created On: 2009-04-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import os.path as op

from PyQt4.QtGui import QImage
import PIL.Image

from hs import fs
from hs.fs import phys
from hs.utils.str import get_file_ext

from dupeguru import data_pe
from dupeguru.picture.cache import Cache
from dupeguru.picture.matchbase import AsyncMatchFactory

from block import getblocks
from base.app import DupeGuru as DupeGuruBase
from details_dialog import DetailsDialog
from main_window import MainWindow
from preferences import Preferences
from preferences_dialog import PreferencesDialog

class File(phys.File):
    cls_info_map = {
        'size': fs.IT_ATTRS,
        'ctime': fs.IT_ATTRS,
        'mtime': fs.IT_ATTRS,
        'md5': fs.IT_MD5,
        'md5partial': fs.IT_MD5,
        'dimensions': fs.IT_EXTRA,
    }
    
    def _initialize_info(self, section):
        super(File, self)._initialize_info(section)
        if section == fs.IT_EXTRA:
            self._info.update({
                'dimensions': (0,0),
            })
    
    def _read_info(self, section):
        super(File, self)._read_info(section)
        if section == fs.IT_EXTRA:
            im = PIL.Image.open(unicode(self.path))
            self._info['dimensions'] = im.size
    
    def get_blocks(self, block_count_per_side):
        image = QImage(unicode(self.path))
        image = image.convertToFormat(QImage.Format_RGB888)
        return getblocks(image, block_count_per_side)
    

class Directory(phys.Directory):
    cls_file_class = File
    cls_supported_exts = ('png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff')
    
    def _fetch_subitems(self):
        subdirs, subfiles = super(Directory, self)._fetch_subitems() 
        return subdirs, [name for name in subfiles if get_file_ext(name) in self.cls_supported_exts]
    

class DupeGuru(DupeGuruBase):
    LOGO_NAME = 'logo_pe'
    NAME = 'dupeGuru Picture Edition'
    VERSION = '1.7.2'
    DELTA_COLUMNS = frozenset([2, 5, 6])
    
    def __init__(self):
        DupeGuruBase.__init__(self, data_pe, appid=5)
    
    def _setup(self):
        self.scanner.match_factory = AsyncMatchFactory()
        self.directories.dirclass = Directory
        self.scanner.match_factory.cached_blocks = Cache(op.join(self.appdata, 'cached_pictures.db'))
        DupeGuruBase._setup(self)
    
    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.scanner.match_factory.match_scaled = self.prefs.match_scaled
        self.scanner.match_factory.threshold = self.prefs.filter_hardness
    
    def _create_details_dialog(self, parent):
        return DetailsDialog(parent, self)
    
    def _create_main_window(self):
        return MainWindow(app=self)
    
    def _create_preferences(self):
        return Preferences()
    
    def _create_preferences_dialog(self, parent):
        return PreferencesDialog(parent, self)
    
