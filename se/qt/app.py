#!/usr/bin/env python
# Unit Name: app
# Created By: Virgil Dupras
# Created On: 2009-05-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from dupeguru import data

from base.app import DupeGuru as DupeGuruBase
from details_dialog import DetailsDialog
from preferences import Preferences
from preferences_dialog import PreferencesDialog

class DupeGuru(DupeGuruBase):
    LOGO_NAME = 'logo_se'
    NAME = 'dupeGuru'
    VERSION = '2.7.1'
    DELTA_COLUMNS = frozenset([2, 4, 5])
    
    def __init__(self):
        DupeGuruBase.__init__(self, data, appid=4)
    
    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.scanner.min_match_percentage = self.prefs.filter_hardness
        self.scanner.scan_type = self.prefs.scan_type
        self.scanner.word_weighting = self.prefs.word_weighting
        self.scanner.match_similar_words = self.prefs.match_similar
        threshold = self.prefs.small_file_threshold if self.prefs.ignore_small_files else 0
        self.scanner.size_threshold = threshold * 1024 # threshold is in KB. the scanner wants bytes
    
    def _create_details_dialog(self, parent):
        return DetailsDialog(parent, self)
    
    def _create_preferences(self):
        return Preferences()
    
    def _create_preferences_dialog(self, parent):
        return PreferencesDialog(parent, self)
    
