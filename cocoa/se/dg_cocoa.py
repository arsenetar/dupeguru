# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.cocoa import signature

from core.scanner import ScanType
from core.app_cocoa_inter import PyDupeGuruBase, PyDetailsPanel
from core_se.app_cocoa import DupeGuru

# Fix py2app imports with chokes on relative imports and other stuff
import hscommon.conflict
import core.engine, core.fs, core.app
import core_se.fs, core_se.data
import xml.etree.ElementPath
import gzip

class PyDupeGuru(PyDupeGuruBase):
    def init(self):
        self = super(PyDupeGuru,self).init()
        self.py = DupeGuru()
        return self
    
    #---Properties
    def setMinMatchPercentage_(self,percentage):
        self.py.scanner.min_match_percentage = int(percentage)
    
    def setScanType_(self,scan_type):
        try:
            self.py.scanner.scan_type = [
                ScanType.Filename,
                ScanType.Contents,
            ][scan_type]
        except IndexError:
            pass
    
    def setWordWeighting_(self,words_are_weighted):
        self.py.scanner.word_weighting = words_are_weighted
    
    def setMatchSimilarWords_(self,match_similar_words):
        self.py.scanner.match_similar_words = match_similar_words
    
    @signature('v@:i')
    def setSizeThreshold_(self, size_threshold):
        self.py.scanner.size_threshold = size_threshold
    
    #---Registration
    def appName(self):
        return "dupeGuru"
    
