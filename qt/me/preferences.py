# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core.scanner import ScanType

from ..base.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    DEFAULT_SCAN_TYPE = ScanType.Tag

    def _load_specific(self, settings):
        get = self.get_value
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
        set_('WordWeighting', self.word_weighting)
        set_('MatchSimilar', self.match_similar)
        set_('ScanTagTrack', self.scan_tag_track)
        set_('ScanTagArtist', self.scan_tag_artist)
        set_('ScanTagAlbum', self.scan_tag_album)
        set_('ScanTagTitle', self.scan_tag_title)
        set_('ScanTagGenre', self.scan_tag_genre)
        set_('ScanTagYear', self.scan_tag_year)

