# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtWidgets import QApplication, QDockWidget
from PyQt5.QtCore import Qt, QRect, QObject, pyqtSignal
from PyQt5.QtGui import QColor

from hscommon import trans
from hscommon.plat import ISLINUX
from core.app import AppMode
from core.scanner import ScanType
from hscommon.util import tryint
from qt.util import create_qsettings


def get_langnames():
    tr = trans.trget("ui")
    return {
        "cs": tr("Czech"),
        "de": tr("German"),
        "el": tr("Greek"),
        "en": tr("English"),
        "es": tr("Spanish"),
        "fr": tr("French"),
        "hy": tr("Armenian"),
        "it": tr("Italian"),
        "ja": tr("Japanese"),
        "ko": tr("Korean"),
        "ms": tr("Malay"),
        "nl": tr("Dutch"),
        "pl_PL": tr("Polish"),
        "pt_BR": tr("Brazilian"),
        "ru": tr("Russian"),
        "tr": tr("Turkish"),
        "uk": tr("Ukrainian"),
        "vi": tr("Vietnamese"),
        "zh_CN": tr("Chinese (Simplified)"),
    }


def _normalize_for_serialization(v):
    # QSettings doesn't consider set/tuple as "native" typs for serialization, so if we don't
    # change them into a list, we get a weird serialized QVariant value which isn't a very
    # "portable" value.
    if isinstance(v, (set, tuple)):
        v = list(v)
    if isinstance(v, list):
        v = [_normalize_for_serialization(item) for item in v]
    return v


def _adjust_after_deserialization(v):
    # In some cases, when reading from prefs, we end up with strings that are supposed to be
    # bool or int. Convert these.
    if isinstance(v, list):
        return [_adjust_after_deserialization(sub) for sub in v]
    if isinstance(v, str):
        # might be bool or int, try them
        if v == "true":
            return True
        elif v == "false":
            return False
        else:
            return tryint(v, v)
    return v


class PreferencesBase(QObject):
    prefsChanged = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.reset()
        self._settings = create_qsettings()

    def _load_values(self, settings):
        # Implemented in subclasses
        pass

    def get_rect(self, name, default=None):
        r = self.get_value(name, default)
        if r is not None:
            return QRect(*r)
        else:
            return None

    def get_value(self, name, default=None):
        if self._settings.contains(name):
            result = _adjust_after_deserialization(self._settings.value(name))
            if result is not None:
                return result
            else:
                # If result is None, but still present in self._settings, it usually means a value
                # like "@Invalid".
                return default
        else:
            return default

    def load(self):
        self.reset()
        self._load_values(self._settings)

    def reset(self):
        # Implemented in subclasses
        pass

    def _save_values(self, settings):
        # Implemented in subclasses
        pass

    def save(self):
        self._save_values(self._settings)
        self._settings.sync()

    def set_rect(self, name, r):
        # About QRect conversion:
        # I think Qt supports putting basic structures like QRect directly in QSettings, but I prefer not
        # to rely on it and stay with generic structures.
        if isinstance(r, QRect):
            rect_as_list = [r.x(), r.y(), r.width(), r.height()]
            self.set_value(name, rect_as_list)

    def set_value(self, name, value):
        self._settings.setValue(name, _normalize_for_serialization(value))

    def saveGeometry(self, name, widget):
        # We save geometry under a 7-sized int array: first item is a flag
        # for whether the widget is maximized, second item is a flag for whether
        # the widget is docked, third item is a Qt::DockWidgetArea enum value,
        # and the other 4 are (x, y, w, h).
        m = 1 if widget.isMaximized() else 0
        d = 1 if isinstance(widget, QDockWidget) and not widget.isFloating() else 0
        area = widget.parent.dockWidgetArea(widget) if d else 0
        r = widget.geometry()
        rect_as_list = [r.x(), r.y(), r.width(), r.height()]
        self.set_value(name, [m, d, area] + rect_as_list)

    def restoreGeometry(self, name, widget):
        geometry = self.get_value(name)
        if geometry and len(geometry) == 7:
            m, d, area, x, y, w, h = geometry
            if m:
                widget.setWindowState(Qt.WindowMaximized)
            else:
                r = QRect(x, y, w, h)
                widget.setGeometry(r)
                if isinstance(widget, QDockWidget):
                    # Inform of the previous dock state and the area used
                    return bool(d), area
        return False, 0


class Preferences(PreferencesBase):
    def _load_values(self, settings):
        get = self.get_value
        self.filter_hardness = get("FilterHardness", self.filter_hardness)
        self.mix_file_kind = get("MixFileKind", self.mix_file_kind)
        self.ignore_hardlink_matches = get("IgnoreHardlinkMatches", self.ignore_hardlink_matches)
        self.use_regexp = get("UseRegexp", self.use_regexp)
        self.remove_empty_folders = get("RemoveEmptyFolders", self.remove_empty_folders)
        self.debug_mode = get("DebugMode", self.debug_mode)
        self.profile_scan = get("ProfileScan", self.profile_scan)
        self.destination_type = get("DestinationType", self.destination_type)
        self.custom_command = get("CustomCommand", self.custom_command)
        self.language = get("Language", self.language)
        if not self.language and trans.installed_lang:
            self.language = trans.installed_lang
        self.portable = get("Portable", False)
        self.use_dark_style = get("UseDarkStyle", False)
        self.use_native_dialogs = get("UseNativeDialogs", True)

        self.tableFontSize = get("TableFontSize", self.tableFontSize)
        self.reference_bold_font = get("ReferenceBoldFont", self.reference_bold_font)
        self.details_dialog_titlebar_enabled = get("DetailsDialogTitleBarEnabled", self.details_dialog_titlebar_enabled)
        self.details_dialog_vertical_titlebar = get(
            "DetailsDialogVerticalTitleBar", self.details_dialog_vertical_titlebar
        )
        # On Windows and MacOS, use internal icons by default
        self.details_dialog_override_theme_icons = (
            get("DetailsDialogOverrideThemeIcons", self.details_dialog_override_theme_icons) if ISLINUX else True
        )
        self.details_table_delta_foreground_color = get(
            "DetailsTableDeltaForegroundColor", self.details_table_delta_foreground_color
        )
        self.details_dialog_viewers_show_scrollbars = get(
            "DetailsDialogViewersShowScrollbars", self.details_dialog_viewers_show_scrollbars
        )

        self.result_table_ref_foreground_color = get(
            "ResultTableRefForegroundColor", self.result_table_ref_foreground_color
        )
        self.result_table_ref_background_color = get(
            "ResultTableRefBackgroundColor", self.result_table_ref_background_color
        )
        self.result_table_delta_foreground_color = get(
            "ResultTableDeltaForegroundColor", self.result_table_delta_foreground_color
        )

        self.resultWindowIsMaximized = get("ResultWindowIsMaximized", self.resultWindowIsMaximized)
        self.resultWindowRect = self.get_rect("ResultWindowRect", self.resultWindowRect)
        self.mainWindowIsMaximized = get("MainWindowIsMaximized", self.mainWindowIsMaximized)
        self.mainWindowRect = self.get_rect("MainWindowRect", self.mainWindowRect)
        self.directoriesWindowRect = self.get_rect("DirectoriesWindowRect", self.directoriesWindowRect)

        self.recentResults = get("RecentResults", self.recentResults)
        self.recentFolders = get("RecentFolders", self.recentFolders)
        self.tabs_default_pos = get("TabsDefaultPosition", self.tabs_default_pos)
        self.word_weighting = get("WordWeighting", self.word_weighting)
        self.match_similar = get("MatchSimilar", self.match_similar)
        self.ignore_small_files = get("IgnoreSmallFiles", self.ignore_small_files)
        self.small_file_threshold = get("SmallFileThreshold", self.small_file_threshold)
        self.ignore_large_files = get("IgnoreLargeFiles", self.ignore_large_files)
        self.large_file_threshold = get("LargeFileThreshold", self.large_file_threshold)
        self.big_file_partial_hashes = get("BigFilePartialHashes", self.big_file_partial_hashes)
        self.big_file_size_threshold = get("BigFileSizeThreshold", self.big_file_size_threshold)
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
        self.profile_scan = False
        self.destination_type = 1
        self.custom_command = ""
        self.language = trans.installed_lang if trans.installed_lang else ""
        self.use_dark_style = False
        self.use_native_dialogs = True

        self.tableFontSize = QApplication.font().pointSize()
        self.reference_bold_font = True
        self.details_dialog_titlebar_enabled = True
        self.details_dialog_vertical_titlebar = True
        self.details_table_delta_foreground_color = QColor(250, 20, 20)  # red
        # By default use internal icons on platforms other than Linux for now
        self.details_dialog_override_theme_icons = False if not ISLINUX else True
        self.details_dialog_viewers_show_scrollbars = True
        self.result_table_ref_foreground_color = QColor(Qt.blue)
        self.result_table_ref_background_color = QColor(Qt.lightGray)
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
        self.ignore_large_files = False
        self.large_file_threshold = 1000  # MB
        self.big_file_partial_hashes = False
        self.big_file_size_threshold = 100  # MB
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
        set_("ProfileScan", self.profile_scan)
        set_("DestinationType", self.destination_type)
        set_("CustomCommand", self.custom_command)
        set_("Language", self.language)
        set_("Portable", self.portable)
        set_("UseDarkStyle", self.use_dark_style)
        set_("UseNativeDialogs", self.use_native_dialogs)

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
        set_("IgnoreLargeFiles", self.ignore_large_files)
        set_("LargeFileThreshold", self.large_file_threshold)
        set_("BigFilePartialHashes", self.big_file_partial_hashes)
        set_("BigFileSizeThreshold", self.big_file_size_threshold)
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
        if app_mode == AppMode.PICTURE:
            return self.get_value("ScanTypePicture", ScanType.FUZZYBLOCK)
        elif app_mode == AppMode.MUSIC:
            return self.get_value("ScanTypeMusic", ScanType.TAG)
        else:
            return self.get_value("ScanTypeStandard", ScanType.CONTENTS)

    def set_scan_type(self, app_mode, value):
        if app_mode == AppMode.PICTURE:
            self.set_value("ScanTypePicture", value)
        elif app_mode == AppMode.MUSIC:
            self.set_value("ScanTypeMusic", value)
        else:
            self.set_value("ScanTypeStandard", value)
