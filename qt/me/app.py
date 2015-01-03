# Created By: Virgil Dupras
# Created On: 2009-05-21
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from core_me import __appname__
from core_me.app import DupeGuru as DupeGuruModel

from ..base.app import DupeGuru as DupeGuruBase
from .details_dialog import DetailsDialog
from .results_model import ResultsModel
from .preferences import Preferences
from .preferences_dialog import PreferencesDialog

class DupeGuru(DupeGuruBase):
    MODELCLASS = DupeGuruModel
    EDITION = 'me'
    LOGO_NAME = 'logo_me'
    NAME = __appname__
    
    DETAILS_DIALOG_CLASS = DetailsDialog
    RESULT_MODEL_CLASS = ResultsModel
    PREFERENCES_CLASS = Preferences
    PREFERENCES_DIALOG_CLASS = PreferencesDialog
    
    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.model.scanner.min_match_percentage = self.prefs.filter_hardness
        self.model.scanner.scan_type = self.prefs.scan_type
        self.model.scanner.word_weighting = self.prefs.word_weighting
        self.model.scanner.match_similar_words = self.prefs.match_similar
        scanned_tags = set()
        if self.prefs.scan_tag_track:
            scanned_tags.add('track')
        if self.prefs.scan_tag_artist:
            scanned_tags.add('artist')
        if self.prefs.scan_tag_album:
            scanned_tags.add('album')
        if self.prefs.scan_tag_title:
            scanned_tags.add('title')
        if self.prefs.scan_tag_genre:
            scanned_tags.add('genre')
        if self.prefs.scan_tag_year:
            scanned_tags.add('year')
        self.model.scanner.scanned_tags = scanned_tags
    
