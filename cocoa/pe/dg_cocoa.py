# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import install_cocoa_trans
install_cocoa_trans()

from core.app_cocoa_inter import PyDupeGuruBase, PyDetailsPanel
from core_pe import app_cocoa as app_pe_cocoa, __appname__
from core.scanner import ScanType

class PyDupeGuru(PyDupeGuruBase):
    def init(self):
        self = super(PyDupeGuru, self).init()
        self.py = app_pe_cocoa.DupeGuruPE()
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
    
    #---Registration
    def appName(self):
        return __appname__
    
