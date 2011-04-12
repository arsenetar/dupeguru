# Created By: Virgil Dupras
# Created On: 2009-05-21
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core_me import data, scanner, fs, __appname__

from ..base.app import DupeGuru as DupeGuruBase
from .details_dialog import DetailsDialog
from .preferences import Preferences
from .preferences_dialog import PreferencesDialog

class DupeGuru(DupeGuruBase):
    EDITION = 'me'
    LOGO_NAME = 'logo_me'
    NAME = __appname__
    
    def __init__(self):
        DupeGuruBase.__init__(self, data)
    
    def _setup(self):
        self.scanner = scanner.ScannerME()
        self.directories.fileclasses = [fs.MusicFile]
        DupeGuruBase._setup(self)
    
    def _update_options(self):
        DupeGuruBase._update_options(self)
        self.scanner.min_match_percentage = self.prefs.filter_hardness
        self.scanner.scan_type = self.prefs.scan_type
        self.scanner.word_weighting = self.prefs.word_weighting
        self.scanner.match_similar_words = self.prefs.match_similar
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
        self.scanner.scanned_tags = scanned_tags
    
    def _create_details_dialog(self, parent):
        return DetailsDialog(parent, self)
    
    def _create_preferences(self):
        return Preferences()
    
    def _create_preferences_dialog(self, parent):
        return PreferencesDialog(parent, self)
    
