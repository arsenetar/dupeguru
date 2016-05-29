# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core.scanner import ScanType

from ..base.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    DEFAULT_SCAN_TYPE = ScanType.Contents

    def _load_specific(self, settings):
        get = self.get_value
        self.word_weighting = get('WordWeighting', self.word_weighting)
        self.match_similar = get('MatchSimilar', self.match_similar)
        self.ignore_small_files = get('IgnoreSmallFiles', self.ignore_small_files)
        self.small_file_threshold = get('SmallFileThreshold', self.small_file_threshold)

    def _reset_specific(self):
        self.filter_hardness = 80
        self.word_weighting = True
        self.match_similar = False
        self.ignore_small_files = True
        self.small_file_threshold = 10 # KB

    def _save_specific(self, settings):
        set_ = self.set_value
        set_('WordWeighting', self.word_weighting)
        set_('MatchSimilar', self.match_similar)
        set_('IgnoreSmallFiles', self.ignore_small_files)
        set_('SmallFileThreshold', self.small_file_threshold)

