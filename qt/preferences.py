# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from hscommon import trans
from hscommon.plat import ISLINUX
from core.app import AppMode
from core.scanner import ScanType
from qtlib.preferences import Preferences as PreferencesBase


class Preferences(PreferencesBase):
    def _load_values(self, settings):
        get = self.get_value
        self.filter_hardness = get("FilterHardness", self.filter_hardness)
        self.mix_file_kind = get("MixFileKind", self.mix_file_kind)
        self.ignore_hardlink_matches = get(
            "IgnoreHardlinkMatches", self.ignore_hardlink_matches
        )
        self.use_regexp = get("UseRegexp", self.use_regexp)
        self.remove_empty_folders = get("RemoveEmptyFolders", self.remove_empty_folders)
        self.debug_mode = get("DebugMode", self.debug_mode)
        self.destination_type = get("DestinationType", self.destination_type)
        self.custom_command = get("CustomCommand", self.custom_command)
        self.language = get("Language", self.language)
        if not self.language and trans.installed_lang:
            self.language = trans.installed_lang

        self.tableFontSize = get("TableFontSize", self.tableFontSize)
        self.reference_bold_font = get("ReferenceBoldFont", self.reference_bold_font)
        self.details_dialog_titlebar_enabled = get("DetailsDialogTitleBarEnabled",
                                                   self.details_dialog_titlebar_enabled)
        self.details_dialog_vertical_titlebar = get("DetailsDialogVerticalTitleBar",
                                                    self.details_dialog_vertical_titlebar)
        # On Windows and MacOS, use internal icons by default
        self.details_dialog_override_theme_icons =\
            get("DetailsDialogOverrideThemeIcons",
                self.details_dialog_override_theme_icons) if ISLINUX else True
        self.details_table_delta_foreground_color =\
            get("DetailsTableDeltaForegroundColor", self.details_table_delta_foreground_color)
        self.details_dialog_viewers_show_scrollbars =\
            get("DetailsDialogViewersShowScrollbars", self.details_dialog_viewers_show_scrollbars)

        self.result_table_ref_foreground_color =\
            get("ResultTableRefForegroundColor", self.result_table_ref_foreground_color)
        self.result_table_ref_background_color =\
            get("ResultTableRefBackgroundColor", self.result_table_ref_background_color)
        self.result_table_delta_foreground_color =\
            get("ResultTableDeltaForegroundColor", self.result_table_delta_foreground_color)

        self.resultWindowIsMaximized = get(
            "ResultWindowIsMaximized", self.resultWindowIsMaximized
        )
        self.resultWindowRect = self.get_rect("ResultWindowRect", self.resultWindowRect)
        self.mainWindowIsMaximized = get(
            "MainWindowIsMaximized", self.mainWindowIsMaximized
        )
        self.mainWindowRect = self.get_rect("MainWindowRect", self.mainWindowRect)
        self.directoriesWindowRect = self.get_rect(
            "DirectoriesWindowRect", self.directoriesWindowRect
        )

        self.recentResults = get("RecentResults", self.recentResults)
        self.recentFolders = get("RecentFolders", self.recentFolders)
        self.tabs_default_pos = get("TabsDefaultPosition", self.tabs_default_pos)
        self.word_weighting = get("WordWeighting", self.word_weighting)
        self.match_similar = get("MatchSimilar", self.match_similar)
        self.ignore_small_files = get("IgnoreSmallFiles", self.ignore_small_files)
        self.small_file_threshold = get("SmallFileThreshold", self.small_file_threshold)
        self.scan_tag_track = get("ScanTagTrack", self.scan_tag_track)
        self.scan_tag_artist = get("ScanTagArtist", self.scan_tag_artist)
        self.scan_tag_album = get("ScanTagAlbum", self.scan_tag_album)
        self.scan_tag_title = get("ScanTagTitle", self.scan_tag_title)
        self.scan_tag_genre = get("ScanTagGenre", self.scan_tag_genre)
        self.scan_tag_year = get("ScanTagYear", self.scan_tag_year)
        self.match_scaled = get("MatchScaled", self.match_scaled)
        self.picture_cache_type = get("PictureCacheType", self.picture_cache_type)

    def reset(self):
        self.filter_hardness = 95
        self.mix_file_kind = True
        self.use_regexp = False
        self.ignore_hardlink_matches = False
        self.remove_empty_folders = False
        self.debug_mode = False
        self.destination_type = 1
        self.custom_command = ""
        self.language = trans.installed_lang if trans.installed_lang else ""

        self.tableFontSize = QApplication.font().pointSize()
        self.reference_bold_font = True
        self.details_dialog_titlebar_enabled = True
        self.details_dialog_vertical_titlebar = True
        self.details_table_delta_foreground_color = QColor(250, 20, 20)  # red
        # By default use internal icons on platforms other than Linux for now
        self.details_dialog_override_theme_icons = False if not ISLINUX else True
        self.details_dialog_viewers_show_scrollbars = True
        self.result_table_ref_foreground_color = QColor(Qt.blue)
        self.result_table_ref_background_color = QColor(Qt.darkGray)
        self.result_table_delta_foreground_color = QColor(255, 142, 40)  # orange
        self.resultWindowIsMaximized = False
        self.resultWindowRect = None
        self.directoriesWindowRect = None
        self.mainWindowRect = None
        self.mainWindowIsMaximized = False
        self.recentResults = []
        self.recentFolders = []

        self.tabs_default_pos = True
        self.word_weighting = True
        self.match_similar = False
        self.ignore_small_files = True
        self.small_file_threshold = 10  # KB
        self.scan_tag_track = False
        self.scan_tag_artist = True
        self.scan_tag_album = True
        self.scan_tag_title = True
        self.scan_tag_genre = False
        self.scan_tag_year = False
        self.match_scaled = False
        self.picture_cache_type = "sqlite"

    def _save_values(self, settings):
        set_ = self.set_value
        set_("FilterHardness", self.filter_hardness)
        set_("MixFileKind", self.mix_file_kind)
        set_("IgnoreHardlinkMatches", self.ignore_hardlink_matches)
        set_("UseRegexp", self.use_regexp)
        set_("RemoveEmptyFolders", self.remove_empty_folders)
        set_("DebugMode", self.debug_mode)
        set_("DestinationType", self.destination_type)
        set_("CustomCommand", self.custom_command)
        set_("Language", self.language)

        set_("TableFontSize", self.tableFontSize)
        set_("ReferenceBoldFont", self.reference_bold_font)
        set_("DetailsDialogTitleBarEnabled", self.details_dialog_titlebar_enabled)
        set_("DetailsDialogVerticalTitleBar", self.details_dialog_vertical_titlebar)
        set_("DetailsDialogOverrideThemeIcons", self.details_dialog_override_theme_icons)
        set_("DetailsDialogViewersShowScrollbars", self.details_dialog_viewers_show_scrollbars)
        set_("DetailsTableDeltaForegroundColor", self.details_table_delta_foreground_color)
        set_("ResultTableRefForegroundColor", self.result_table_ref_foreground_color)
        set_("ResultTableRefBackgroundColor", self.result_table_ref_background_color)
        set_("ResultTableDeltaForegroundColor", self.result_table_delta_foreground_color)
        set_("ResultWindowIsMaximized", self.resultWindowIsMaximized)
        set_("MainWindowIsMaximized", self.mainWindowIsMaximized)
        self.set_rect("ResultWindowRect", self.resultWindowRect)
        self.set_rect("MainWindowRect", self.mainWindowRect)
        self.set_rect("DirectoriesWindowRect", self.directoriesWindowRect)
        set_("RecentResults", self.recentResults)
        set_("RecentFolders", self.recentFolders)

        set_("TabsDefaultPosition", self.tabs_default_pos)
        set_("WordWeighting", self.word_weighting)
        set_("MatchSimilar", self.match_similar)
        set_("IgnoreSmallFiles", self.ignore_small_files)
        set_("SmallFileThreshold", self.small_file_threshold)
        set_("ScanTagTrack", self.scan_tag_track)
        set_("ScanTagArtist", self.scan_tag_artist)
        set_("ScanTagAlbum", self.scan_tag_album)
        set_("ScanTagTitle", self.scan_tag_title)
        set_("ScanTagGenre", self.scan_tag_genre)
        set_("ScanTagYear", self.scan_tag_year)
        set_("MatchScaled", self.match_scaled)
        set_("PictureCacheType", self.picture_cache_type)

    # scan_type is special because we save it immediately when we set it.
    def get_scan_type(self, app_mode):
        if app_mode == AppMode.Picture:
            return self.get_value("ScanTypePicture", ScanType.FuzzyBlock)
        elif app_mode == AppMode.Music:
            return self.get_value("ScanTypeMusic", ScanType.Tag)
        else:
            return self.get_value("ScanTypeStandard", ScanType.Contents)

    def set_scan_type(self, app_mode, value):
        if app_mode == AppMode.Picture:
            self.set_value("ScanTypePicture", value)
        elif app_mode == AppMode.Music:
            self.set_value("ScanTypeMusic", value)
        else:
            self.set_value("ScanTypeStandard", value)
