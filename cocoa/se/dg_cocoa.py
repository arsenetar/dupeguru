# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.cocoa import signature

from core import scanner
from core.app_cocoa_inter import PyDupeGuruBase, PyDetailsPanel
from core_se.app_cocoa import DupeGuru

# Fix py2app imports with chokes on relative imports
from core_se import fs, data

class PyDupeGuru(PyDupeGuruBase):
    def init(self):
        self = super(PyDupeGuru,self).init()
        self.app = DupeGuru()
        return self
    
    #---Properties
    def setMinMatchPercentage_(self,percentage):
        self.app.scanner.min_match_percentage = int(percentage)
    
    def setScanType_(self,scan_type):
        try:
            self.app.scanner.scan_type = [
                scanner.SCAN_TYPE_FILENAME,
                scanner.SCAN_TYPE_CONTENT
            ][scan_type]
        except IndexError:
            pass
    
    def setWordWeighting_(self,words_are_weighted):
        self.app.scanner.word_weighting = words_are_weighted
    
    def setMatchSimilarWords_(self,match_similar_words):
        self.app.scanner.match_similar_words = match_similar_words
    
    @signature('v@:i')
    def setSizeThreshold_(self, size_threshold):
        self.app.scanner.size_threshold = size_threshold
    
    #---Registration
    def appName(self):
        return "dupeGuru"
    
