# Created By: Virgil Dupras
# Created On: 2009-05-17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.scanner import ScanType

from base.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    # (width, is_visible)
    COLUMNS_DEFAULT_ATTRS = [ 
        (200, True), # name
        (180, True), # path
        (60, True), # size
        (60, True), # Time
        (50, True), # Bitrate
        (60, False), # Sample Rate
        (40, False), # Kind
        (120, False), # modification
        (120, False), # Title
        (120, False), # Artist
        (120, False), # Album
        (80, False), # Genre
        (40, False), # Year
        (40, False), # Track Number
        (120, False), # Comment
        (60, True), # match %
        (120, False), # Words Used
        (80, False), # dupe count
    ]
    
    def _load_specific(self, settings):
        get = self.get_value
        self.scan_type = get('ScanType', self.scan_type)
        self.word_weighting = get('WordWeighting', self.word_weighting)
        self.match_similar = get('MatchSimilar', self.match_similar)
        self.scan_tag_track = get('ScanTagTrack', self.scan_tag_track)
        self.scan_tag_artist = get('ScanTagArtist', self.scan_tag_artist)
        self.scan_tag_album = get('ScanTagAlbum', self.scan_tag_album)
        self.scan_tag_title = get('ScanTagTitle', self.scan_tag_title)
        self.scan_tag_genre = get('ScanTagGenre', self.scan_tag_genre)
        self.scan_tag_year = get('ScanTagYear', self.scan_tag_year)
    
    def _reset_specific(self):
        self.filter_hardness = 80
        self.scan_type = ScanType.Tag
        self.word_weighting = True
        self.match_similar = False
        self.scan_tag_track = False
        self.scan_tag_artist = True
        self.scan_tag_album = True
        self.scan_tag_title = True
        self.scan_tag_genre = False
        self.scan_tag_year = False
    
    def _save_specific(self, settings):
        set_ = self.set_value
        set_('ScanType', self.scan_type)
        set_('WordWeighting', self.word_weighting)
        set_('MatchSimilar', self.match_similar)
        set_('ScanTagTrack', self.scan_tag_track)
        set_('ScanTagArtist', self.scan_tag_artist)
        set_('ScanTagAlbum', self.scan_tag_album)
        set_('ScanTagTitle', self.scan_tag_title)
        set_('ScanTagGenre', self.scan_tag_genre)
        set_('ScanTagYear', self.scan_tag_year)
    
