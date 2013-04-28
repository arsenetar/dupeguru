# Created By: Virgil Dupras
# Created On: 2009-05-17
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.scanner import ScanType

from ..base.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    def _load_specific(self, settings):
        get = self.get_value
        self.scan_type = get('ScanType', self.scan_type)
        self.match_scaled = get('MatchScaled', self.match_scaled)
    
    def _reset_specific(self):
        self.scan_type = ScanType.FuzzyBlock
        self.filter_hardness = 95
        self.match_scaled = False
    
    def _save_specific(self, settings):
        set_ = self.set_value
        set_('ScanType', self.scan_type)
        set_('MatchScaled', self.match_scaled)
    
