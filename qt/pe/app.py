# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
import logging

from PyQt4.QtGui import QImage, QImageReader

from core_pe import data as data_pe, __appname__
from core_pe.photo import Photo as PhotoBase
from core_pe.scanner import ScannerPE

from ..base.app import DupeGuru as DupeGuruBase
from .block import getblocks
from .details_dialog import DetailsDialog
from .result_window import ResultWindow
from .preferences import Preferences
from .preferences_dialog import PreferencesDialog

class File(PhotoBase):
    def _read_info(self, field):
        PhotoBase._read_info(self, field)
        if field == 'dimensions':
            try:
                ir = QImageReader(str(self.path))
                size = ir.size()
                if size.isValid():
                    self.dimensions = (size.width(), size.height())
                else:
                    self.dimensions = (0, 0)
            except EnvironmentError:
                self.dimensions = (0, 0)
                logging.warning("Could not read image '%s'", str(self.path))
    
    def get_blocks(self, block_count_per_side):
        image = QImage(str(self.path))
        image = image.convertToFormat(QImage.Format_RGB888)
        return getblocks(image, block_count_per_side)
    

class DupeGuru(DupeGuruBase):
    EDITION = 'pe'
    LOGO_NAME = 'logo_pe'
    NAME = __appname__
    
    def __init__(self):
        DupeGuruBase.__init__(self, data_pe)
    
    def _setup(self):
        self.scanner = ScannerPE()
        self.directories.fileclasses = [File]
        self.scanner.cache_path = op.join(self.appdata, 'cached_pictures.db')
        DupeGuruBase._setup(self)
    
    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.scanner.scan_type = self.prefs.scan_type
        self.scanner.match_scaled = self.prefs.match_scaled
        self.scanner.threshold = self.prefs.filter_hardness
    
    def _create_details_dialog(self, parent):
        return DetailsDialog(parent, self)
    
    def _create_result_window(self):
        return ResultWindow(app=self)
    
    def _create_preferences(self):
        return Preferences()
    
    def _create_preferences_dialog(self, parent):
        return PreferencesDialog(parent, self)
    
