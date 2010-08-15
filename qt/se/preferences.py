# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.scanner import ScanType

from base.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    # (width, is_visible)
    COLUMNS_DEFAULT_ATTRS = [ 
        (200, True), # name
        (180, True), # path
        (60, True), # size
        (40, False), # Kind
        (120, False), # modification
        (60, True), # match %
        (120, False), # Words Used
        (80, False), # dupe count
    ]
    
    def _load_specific(self, settings):
        get = self.get_value
        self.scan_type = get('ScanType', self.scan_type)
        self.word_weighting = get('WordWeighting', self.word_weighting)
        self.match_similar = get('MatchSimilar', self.match_similar)
        self.ignore_small_files = get('IgnoreSmallFiles', self.ignore_small_files)
        self.small_file_threshold = get('SmallFileThreshold', self.small_file_threshold)
    
    def _reset_specific(self):
        self.filter_hardness = 80
        self.scan_type = ScanType.Contents
        self.word_weighting = True
        self.match_similar = False
        self.ignore_small_files = True
        self.small_file_threshold = 10 # KB
    
    def _save_specific(self, settings):
        set_ = self.set_value
        set_('ScanType', self.scan_type)
        set_('WordWeighting', self.word_weighting)
        set_('MatchSimilar', self.match_similar)
        set_('IgnoreSmallFiles', self.ignore_small_files)
        set_('SmallFileThreshold', self.small_file_threshold)
    
