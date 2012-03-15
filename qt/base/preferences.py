# Created By: Virgil Dupras
# Created On: 2009-05-03
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtGui import QApplication

from hscommon import trans
from qtlib.preferences import Preferences as PreferencesBase

class Preferences(PreferencesBase):
    def _load_specific(self, settings):
        # load prefs specific to the dg edition
        pass
    
    def _load_values(self, settings):
        get = self.get_value
        self.filter_hardness = get('FilterHardness', self.filter_hardness)
        self.mix_file_kind = get('MixFileKind', self.mix_file_kind)
        self.ignore_hardlink_matches = get('IgnoreHardlinkMatches', self.ignore_hardlink_matches)
        self.use_regexp = get('UseRegexp', self.use_regexp)
        self.remove_empty_folders = get('RemoveEmptyFolders', self.remove_empty_folders)
        self.debug_mode = get('DebugMode', self.debug_mode)
        self.destination_type = get('DestinationType', self.destination_type)
        self.custom_command = get('CustomCommand', self.custom_command)
        self.language = get('Language', self.language)
        if not self.language and trans.installed_lang:
            self.language = trans.installed_lang
        
        self.tableFontSize = get('TableFontSize', self.tableFontSize)
        self.resultWindowIsMaximized = get('ResultWindowIsMaximized', self.resultWindowIsMaximized)
        self.resultWindowRect = self.get_rect('ResultWindowRect', self.resultWindowRect)
        self.detailsWindowRect = self.get_rect('DetailsWindowRect', self.detailsWindowRect)
        self.directoriesWindowRect = self.get_rect('DirectoriesWindowRect', self.directoriesWindowRect)
        self.recentResults = get('RecentResults', self.recentResults)
        self.recentFolders = get('RecentFolders', self.recentFolders)
        
        self._load_specific(settings)
    
    def _reset_specific(self):
        # reset prefs specific to the dg edition
        pass
    
    def reset(self):
        self.filter_hardness = 95
        self.mix_file_kind = True
        self.use_regexp = False
        self.ignore_hardlink_matches = False
        self.remove_empty_folders = False
        self.debug_mode = False
        self.destination_type = 1
        self.custom_command = ''
        self.language = trans.installed_lang if trans.installed_lang else ''
        
        self.tableFontSize = QApplication.font().pointSize()
        self.resultWindowIsMaximized = False
        self.resultWindowRect = None
        self.detailsWindowRect = None
        self.directoriesWindowRect = None
        self.recentResults = []
        self.recentFolders = []
        
        self._reset_specific()
    
    def _save_specific(self, settings):
        # save prefs specific to the dg edition
        pass
    
    def _save_values(self, settings):
        set_ = self.set_value
        set_('FilterHardness', self.filter_hardness)
        set_('MixFileKind', self.mix_file_kind)
        set_('IgnoreHardlinkMatches', self.ignore_hardlink_matches)
        set_('UseRegexp', self.use_regexp)
        set_('RemoveEmptyFolders', self.remove_empty_folders)
        set_('DebugMode', self.debug_mode)
        set_('DestinationType', self.destination_type)
        set_('CustomCommand', self.custom_command)
        set_('Language', self.language)
        
        set_('TableFontSize', self.tableFontSize)
        set_('ResultWindowIsMaximized', self.resultWindowIsMaximized)
        self.set_rect('ResultWindowRect', self.resultWindowRect)
        self.set_rect('DetailsWindowRect', self.detailsWindowRect)
        self.set_rect('DirectoriesWindowRect', self.directoriesWindowRect)
        set_('RecentResults', self.recentResults)
        set_('RecentFolders', self.recentFolders)
        
        self._save_specific(settings)
    
