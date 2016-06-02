# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import trget

from core.scanner import ScanType
from core_me.app import DupeGuru as DupeGuruME
from .app import PyDupeGuruBase

tr = trget('ui')

class PyDupeGuru(PyDupeGuruBase):
    def __init__(self):
        self._init(DupeGuruME)
    
    #---Properties
    def setMinMatchPercentage_(self, percentage: int):
        self.model.options['min_match_percentage'] = percentage
    
    def setScanType_(self, scan_type: int):
        try:
            self.model.options['scan_type'] = [
                ScanType.Filename,
                ScanType.Fields,
                ScanType.FieldsNoOrder,
                ScanType.Tag,
                ScanType.Contents,
                ScanType.ContentsAudio,
            ][scan_type]
        except IndexError:
            pass
    
    def setWordWeighting_(self, words_are_weighted: bool):
        self.model.options['word_weighting'] = words_are_weighted
    
    def setMatchSimilarWords_(self, match_similar_words: bool):
        self.model.options['match_similar_words'] = match_similar_words
    
    def enable_scanForTag_(self, enable: bool, scan_tag: str):
        if 'scanned_tags' not in self.model.options:
            self.model.options['scanned_tags'] = set()
        if enable:
            self.model.options['scanned_tags'].add(scan_tag)
        else:
            self.model.options['scanned_tags'].discard(scan_tag)
