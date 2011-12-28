# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import install_gettext_trans_under_cocoa
install_gettext_trans_under_cocoa()

from hscommon.cocoa.inter import signature

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
from inter.app_me import DupeGuruME

class PyDupeGuru(PyDupeGuruBase):
    def init(self):
        self = super(PyDupeGuru,self).init()
        self._init(DupeGuruME)
        return self
    
    def removeDeadTracks(self):
        self.py.remove_dead_tracks()
    
    def scanDeadTracks(self):
        self.py.scan_dead_tracks()
    
    #---Information
    @signature('i@:')
    def deadTrackCount(self):
        return len(self.py.dead_tracks)
    
    #---Properties
    def setMinMatchPercentage_(self, percentage):
        self.py.scanner.min_match_percentage = int(percentage)
    
    def setScanType_(self, scan_type):
        try:
            self.py.scanner.scan_type = [
                ScanType.Filename,
                ScanType.Fields,
                ScanType.FieldsNoOrder,
                ScanType.Tag,
                ScanType.Contents,
                ScanType.ContentsAudio,
            ][scan_type]
        except IndexError:
            pass
    
    def setWordWeighting_(self, words_are_weighted):
        self.py.scanner.word_weighting = words_are_weighted
    
    def setMatchSimilarWords_(self, match_similar_words):
        self.py.scanner.match_similar_words = match_similar_words
    
    def enable_scanForTag_(self, enable, scan_tag):
        if enable:
            self.py.scanner.scanned_tags.add(scan_tag)
        else:
            self.py.scanner.scanned_tags.discard(scan_tag)
    
