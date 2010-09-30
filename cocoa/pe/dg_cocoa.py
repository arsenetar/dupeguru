# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.app_cocoa_inter import PyDupeGuruBase, PyDetailsPanel
from core_pe import app_cocoa as app_pe_cocoa

# Fix py2app imports which chokes on relative imports and other stuff
import hsutil.conflict
import core.engine, core.fs, core.app
import core_pe.block, core_pe.cache, core_pe.matchbase, core_pe.data, core_pe._block_osx
import xml.etree.ElementPath
import gzip
import aem.kae
import appscript.defaultterminology

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
    def setMatchScaled_(self,match_scaled):
        self.py.scanner.match_scaled = match_scaled
    
    def setMinMatchPercentage_(self,percentage):
        self.py.scanner.threshold = int(percentage)
    
    #---Registration
    def appName(self):
        return "dupeGuru Picture Edition"
    
