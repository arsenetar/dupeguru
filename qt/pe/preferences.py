# Created By: Virgil Dupras
# Created On: 2009-05-17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QSettings, QVariant

from ..base.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    # (width, is_visible)
    COLUMNS_DEFAULT_ATTRS = [ 
        (200, True), # name
        (180, True), # path
        (60, True), # size
        (40, False), # kind
        (100, True), # dimensions
        (120, False), # modification
        (60, True), # match %
        (80, False), # dupe count
    ]
    
    def _load_specific(self, settings):
        self.match_scaled = self.get_value('MatchScaled', self.match_scaled)
    
    def _reset_specific(self):
        self.filter_hardness = 95
        self.match_scaled = False
    
    def _save_specific(self, settings):
        self.set_value('MatchScaled', self.match_scaled)
    
