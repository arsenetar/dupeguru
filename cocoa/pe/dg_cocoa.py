# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import install_gettext_trans_under_cocoa
install_gettext_trans_under_cocoa()

from core.scanner import ScanType

from inter.app import PyDupeGuruBase
from inter.details_panel import PyDetailsPanel
from inter.directory_outline import PyDirectoryOutline
from inter.extra_fairware_reminder import PyExtraFairwareReminder
from inter.prioritize_dialog import PyPrioritizeDialog
from inter.problem_dialog import PyProblemDialog
from inter.problem_table import PyProblemTable
from inter.result_table import PyResultTable
from inter.stats_label import PyStatsLabel
from inter.app_pe import DupeGuruPE

class PyDupeGuru(PyDupeGuruBase):
    def init(self):
        self = super(PyDupeGuru, self).init()
        self._init(DupeGuruPE)
        return self
    
    def clearPictureCache(self):
        self.py.scanner.clear_picture_cache()
    
    #---Information    
    def getSelectedDupePath(self):
        return str(self.py.selected_dupe_path())
    
    def getSelectedDupeRefPath(self):
        return str(self.py.selected_dupe_ref_path())
    
    #---Properties
    def setScanType_(self, scan_type):
        try:
            self.py.scanner.scan_type = [
                ScanType.FuzzyBlock,
                ScanType.ExifTimestamp,
            ][scan_type]
        except IndexError:
            pass
    
    def setMatchScaled_(self,match_scaled):
        self.py.scanner.match_scaled = match_scaled
    
    def setMinMatchPercentage_(self,percentage):
        self.py.scanner.threshold = int(percentage)
    
