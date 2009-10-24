# Created By: Virgil Dupras
# Created On: 2009-04-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op

from PyQt4.QtGui import QImage
import PIL.Image

from hsutil.str import get_file_ext

from dupeguru import fs
from dupeguru_pe import data as data_pe
from dupeguru_pe.cache import Cache
from dupeguru_pe.scanner import ScannerPE

from block import getblocks
from base.app import DupeGuru as DupeGuruBase
from details_dialog import DetailsDialog
from main_window import MainWindow
from preferences import Preferences
from preferences_dialog import PreferencesDialog

class File(fs.File):
    INITIAL_INFO = fs.File.INITIAL_INFO.copy()
    INITIAL_INFO.update({
        'dimensions': (0,0),
    })
    HANDLED_EXTS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif'])
    
    @classmethod
    def can_handle(cls, path):
        return fs.File.can_handle(path) and get_file_ext(path[-1]) in cls.HANDLED_EXTS
    
    def _read_info(self, field):
        fs.File._read_info(self, field)
        if field == 'dimensions':
            im = PIL.Image.open(unicode(self.path))
            self.dimensions = im.size
    
    def get_blocks(self, block_count_per_side):
        image = QImage(unicode(self.path))
        image = image.convertToFormat(QImage.Format_RGB888)
        return getblocks(image, block_count_per_side)
    

class DupeGuru(DupeGuruBase):
    LOGO_NAME = 'logo_pe'
    NAME = 'dupeGuru Picture Edition'
    VERSION = '1.7.7'
    DELTA_COLUMNS = frozenset([2, 5, 6])
    
    def __init__(self):
        DupeGuruBase.__init__(self, data_pe, appid=5)
    
    def _setup(self):
        self.scanner = ScannerPE()
        self.directories.fileclasses = [File]
        self.scanner.cached_blocks = Cache(op.join(self.appdata, 'cached_pictures.db'))
        DupeGuruBase._setup(self)
    
    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.scanner.match_scaled = self.prefs.match_scaled
        self.scanner.threshold = self.prefs.filter_hardness
    
    def _create_details_dialog(self, parent):
        return DetailsDialog(parent, self)
    
    def _create_main_window(self):
        return MainWindow(app=self)
    
    def _create_preferences(self):
        return Preferences()
    
    def _create_preferences_dialog(self, parent):
        return PreferencesDialog(parent, self)
    
