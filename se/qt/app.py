# Created By: Virgil Dupras
# Created On: 2009-05-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from dupeguru import data
from dupeguru.directories import Directories as DirectoriesBase, STATE_EXCLUDED

from base.app import DupeGuru as DupeGuruBase
from details_dialog import DetailsDialog
from preferences import Preferences
from preferences_dialog import PreferencesDialog

class Directories(DirectoriesBase):
    ROOT_PATH_TO_EXCLUDE = frozenset(['windows', 'program files'])
    def _default_state_for_path(self, path):
        result = DirectoriesBase._default_state_for_path(self, path)
        if result is not None:
            return result
        if len(path) == 2 and path[1].lower() in self.ROOT_PATH_TO_EXCLUDE:
            return STATE_EXCLUDED

class DupeGuru(DupeGuruBase):
    LOGO_NAME = 'logo_se'
    NAME = 'dupeGuru'
    VERSION = '2.8.2'
    DELTA_COLUMNS = frozenset([2, 4, 5])
    
    def __init__(self):
        DupeGuruBase.__init__(self, data, appid=4)
    
    def _setup(self):
        self.directories = Directories()
        DupeGuruBase._setup(self)
    
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
    
