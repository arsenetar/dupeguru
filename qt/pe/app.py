# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging

from PyQt5.QtGui import QImage, QImageReader, QTransform

from core_pe import __appname__
from core_pe.photo import Photo as PhotoBase
from core_pe.app import DupeGuru as DupeGuruModel

from ..base.app import DupeGuru as DupeGuruBase
from .block import getblocks
from .details_dialog import DetailsDialog
from .result_window import ResultWindow
from .results_model import ResultsModel
from .preferences import Preferences
from .preferences_dialog import PreferencesDialog

class File(PhotoBase):
    def _plat_get_dimensions(self):
        try:
            ir = QImageReader(str(self.path))
            size = ir.size()
            if size.isValid():
                return (size.width(), size.height())
            else:
                return (0, 0)
        except EnvironmentError:
            logging.warning("Could not read image '%s'", str(self.path))
            return (0, 0)

    def _plat_get_blocks(self, block_count_per_side, orientation):
        image = QImage(str(self.path))
        image = image.convertToFormat(QImage.Format_RGB888)
        # MYSTERY TO SOLVE: For reasons I cannot explain, orientations 5 and 7 don't work for
        # duplicate scanning. The transforms seems to work fine (if I try to save the image after
        # the transform, we see that the image has been correctly flipped and rotated), but the
        # analysis part yields wrong blocks. I spent enought time with this feature, so I'll leave
        # like that for now. (by the way, orientations 5 and 7 work fine under Cocoa)
        if 2 <= orientation <= 8:
            t = QTransform()
            if orientation == 2:
                t.scale(-1, 1)
            elif orientation == 3:
                t.rotate(180)
            elif orientation == 4:
                t.scale(1, -1)
            elif orientation == 5:
                t.scale(-1, 1)
                t.rotate(90)
            elif orientation == 6:
                t.rotate(90)
            elif orientation == 7:
                t.scale(-1, 1)
                t.rotate(270)
            elif orientation == 8:
                t.rotate(270)
            image = image.transformed(t)
        return getblocks(image, block_count_per_side)


class DupeGuru(DupeGuruBase):
    MODELCLASS = DupeGuruModel
    EDITION = 'pe'
    LOGO_NAME = 'logo_pe'
    NAME = __appname__

    DETAILS_DIALOG_CLASS = DetailsDialog
    RESULT_WINDOW_CLASS = ResultWindow
    RESULT_MODEL_CLASS = ResultsModel
    PREFERENCES_CLASS = Preferences
    PREFERENCES_DIALOG_CLASS = PreferencesDialog

    def _setup(self):
        self.model.directories.fileclasses = [File]
        DupeGuruBase._setup(self)
        self.directories_dialog.menuFile.insertAction(
            self.directories_dialog.actionLoadResults, self.resultWindow.actionClearPictureCache
        )

    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.model.options['scan_type'] = self.prefs.scan_type
        self.model.options['match_scaled'] = self.prefs.match_scaled
        self.model.options['threshold'] = self.prefs.filter_hardness

