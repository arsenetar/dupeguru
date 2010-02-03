# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.app_cocoa_inter import PyDupeGuruBase
from core_pe import app_cocoa as app_pe_cocoa

# Fix py2app imports which chokes on relative imports
from core_pe import block, cache, matchbase, data

class PyDupeGuru(PyDupeGuruBase):
    def init(self):
        self = super(PyDupeGuru, self).init()
        self.app = app_pe_cocoa.DupeGuruPE()
        return self
    
    def clearPictureCache(self):
        self.app.scanner.clear_picture_cache()
    
    #---Information    
    def getSelectedDupePath(self):
        return unicode(self.app.selected_dupe_path())
    
    def getSelectedDupeRefPath(self):
        return unicode(self.app.selected_dupe_ref_path())
    
    #---Properties
    def setMatchScaled_(self,match_scaled):
        self.app.scanner.match_scaled = match_scaled
    
    def setMinMatchPercentage_(self,percentage):
        self.app.scanner.threshold = int(percentage)
    
    #---Registration
    def appName(self):
        return "dupeGuru Picture Edition"
    
