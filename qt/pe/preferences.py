# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from core.scanner import ScanType

from ..base.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    DEFAULT_SCAN_TYPE = ScanType.FuzzyBlock

    def _load_specific(self, settings):
        get = self.get_value
        self.match_scaled = get('MatchScaled', self.match_scaled)

    def _reset_specific(self):
        self.filter_hardness = 95
        self.match_scaled = False

    def _save_specific(self, settings):
        set_ = self.set_value
        set_('MatchScaled', self.match_scaled)

