# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import sys
import os.path as op

from PyQt5.QtCore import QTimer, QObject, QUrl, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QDesktopServices, QPalette
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QMessageBox, QStyleFactory, QToolTip

from hscommon.trans import trget
from hscommon import desktop, plat

from qtlib.about_box import AboutBox
from qtlib.recent import Recent
from qtlib.util import create_actions
from qtlib.progress_window import ProgressWindow

from core.app import AppMode, DupeGuru as DupeGuruModel
import core.pe.photo
from . import platform
from .preferences import Preferences
from .result_window import ResultWindow
from .directories_dialog import DirectoriesDialog
from .problem_dialog import ProblemDialog
from .ignore_list_dialog import IgnoreListDialog
from .exclude_list_dialog import ExcludeListDialog
from .deletion_options import DeletionOptions
from .se.details_dialog import DetailsDialog as DetailsDialogStandard
from .me.details_dialog import DetailsDialog as DetailsDialogMusic
from .pe.details_dialog import DetailsDialog as DetailsDialogPicture
from .se.preferences_dialog import PreferencesDialog as PreferencesDialogStandard
from .me.preferences_dialog import PreferencesDialog as PreferencesDialogMusic
from .pe.preferences_dialog import PreferencesDialog as PreferencesDialogPicture
from .pe.photo import File as PlatSpecificPhoto
from .tabbed_window import TabBarWindow, TabWindow

tr = trget("ui")


class DupeGuru(QObject):
    LOGO_NAME = "logo_se"
    NAME = "dupeGuru"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefs = Preferences()
        self.prefs.load()
        # Enable tabs instead of separate floating windows for each dialog
        # Could be passed as an argument to this class if we wanted
        self.use_tabs = True
        self.model = DupeGuruModel(view=self, portable=self.prefs.portable)
        self._setup()

    # --- Private
    def _setup(self):
        core.pe.photo.PLAT_SPECIFIC_PHOTO_CLASS = PlatSpecificPhoto
        self._setupActions()
        self.details_dialog = None
        self._update_options()
        self.recentResults = Recent(self, "recentResults")
        self.recentResults.mustOpenItem.connect(self.model.load_from)
        self.resultWindow = None
        if self.use_tabs:
            self.main_window = TabBarWindow(self) if not self.prefs.tabs_default_pos else TabWindow(self)
            parent_window = self.main_window
            self.directories_dialog = self.main_window.createPage("DirectoriesDialog", app=self)
            self.main_window.addTab(self.directories_dialog, tr("Directories"), switch=False)
            self.actionDirectoriesWindow.setEnabled(False)
        else:  # floating windows only
            self.main_window = None
            self.directories_dialog = DirectoriesDialog(self)
            parent_window = self.directories_dialog

        self.progress_window = ProgressWindow(parent_window, self.model.progress_window)
        self.problemDialog = ProblemDialog(parent=parent_window, model=self.model.problem_dialog)
        if self.use_tabs:
            self.ignoreListDialog = self.main_window.createPage(
                "IgnoreListDialog",
                parent=self.main_window,
                model=self.model.ignore_list_dialog,
            )

            self.excludeListDialog = self.main_window.createPage(
                "ExcludeListDialog",
                app=self,
                parent=self.main_window,
                model=self.model.exclude_list_dialog,
            )
        else:
            self.ignoreListDialog = IgnoreListDialog(parent=parent_window, model=self.model.ignore_list_dialog)
            self.excludeDialog = ExcludeListDialog(app=self, parent=parent_window, model=self.model.exclude_list_dialog)

        self.deletionOptions = DeletionOptions(parent=parent_window, model=self.model.deletion_options)
        self.about_box = AboutBox(parent_window, self)

        parent_window.show()
        self.model.load()

        self.SIGTERM.connect(self.handleSIGTERM)

        # The timer scheme is because if the nag is not shown before the application is
        # completely initialized, the nag will be shown before the app shows up in the task bar
        # In some circumstances, the nag is hidden by other window, which may make the user think
        # that the application haven't launched.
        QTimer.singleShot(0, self.finishedLaunching)

    def _setupActions(self):
        # Setup actions that are common to both the directory dialog and the results window.
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            ("actionQuit", "Ctrl+Q", "", tr("Quit"), self.quitTriggered),
            (
                "actionPreferences",
                "Ctrl+P",
                "",
                tr("Options"),
                self.preferencesTriggered,
            ),
            ("actionIgnoreList", "", "", tr("Ignore List"), self.ignoreListTriggered),
            (
                "actionDirectoriesWindow",
                "",
                "",
                tr("Directories"),
                self.showDirectoriesWindow,
            ),
            (
                "actionClearCache",
                "Ctrl+Shift+P",
                "",
                tr("Clear Cache"),
                self.clearCacheTriggered,
            ),
            (
                "actionExcludeList",
                "",
                "",
                tr("Exclusion Filters"),
                self.excludeListTriggered,
            ),
            ("actionShowHelp", "F1", "", tr("dupeGuru Help"), self.showHelpTriggered),
            ("actionAbout", "", "", tr("About dupeGuru"), self.showAboutBoxTriggered),
            (
                "actionOpenDebugLog",
                "",
                "",
                tr("Open Debug Log"),
                self.openDebugLogTriggered,
            ),
        ]
        create_actions(ACTIONS, self)

    def _update_options(self):
        self.model.options["mix_file_kind"] = self.prefs.mix_file_kind
        self.model.options["escape_filter_regexp"] = not self.prefs.use_regexp
        self.model.options["clean_empty_dirs"] = self.prefs.remove_empty_folders
        self.model.options["ignore_hardlink_matches"] = self.prefs.ignore_hardlink_matches
        self.model.options["copymove_dest_type"] = self.prefs.destination_type
        self.model.options["scan_type"] = self.prefs.get_scan_type(self.model.app_mode)
        self.model.options["min_match_percentage"] = self.prefs.filter_hardness
        self.model.options["word_weighting"] = self.prefs.word_weighting
        self.model.options["match_similar_words"] = self.prefs.match_similar
        threshold = self.prefs.small_file_threshold if self.prefs.ignore_small_files else 0
        self.model.options["size_threshold"] = threshold * 1024  # threshold is in KB. The scanner wants bytes
        large_threshold = self.prefs.large_file_threshold if self.prefs.ignore_large_files else 0
        self.model.options["large_size_threshold"] = (
            large_threshold * 1024 * 1024
        )  # threshold is in MB. The Scanner wants bytes
        big_file_size_threshold = self.prefs.big_file_size_threshold if self.prefs.big_file_partial_hashes else 0
        self.model.options["big_file_size_threshold"] = (
            big_file_size_threshold
            * 1024
            * 1024
            # threshold is in MiB. The scanner wants bytes
        )
        scanned_tags = set()
        if self.prefs.scan_tag_track:
            scanned_tags.add("track")
        if self.prefs.scan_tag_artist:
            scanned_tags.add("artist")
        if self.prefs.scan_tag_album:
            scanned_tags.add("album")
        if self.prefs.scan_tag_title:
            scanned_tags.add("title")
        if self.prefs.scan_tag_genre:
            scanned_tags.add("genre")
        if self.prefs.scan_tag_year:
            scanned_tags.add("year")
        self.model.options["scanned_tags"] = scanned_tags
        self.model.options["match_scaled"] = self.prefs.match_scaled
        self.model.options["picture_cache_type"] = self.prefs.picture_cache_type

        if self.details_dialog:
            self.details_dialog.update_options()

        self._set_style("dark" if self.prefs.use_dark_style else "light")

    # --- Private
    def _get_details_dialog_class(self):
        if self.model.app_mode == AppMode.PICTURE:
            return DetailsDialogPicture
        elif self.model.app_mode == AppMode.MUSIC:
            return DetailsDialogMusic
        else:
            return DetailsDialogStandard

    def _get_preferences_dialog_class(self):
        if self.model.app_mode == AppMode.PICTURE:
            return PreferencesDialogPicture
        elif self.model.app_mode == AppMode.MUSIC:
            return PreferencesDialogMusic
        else:
            return PreferencesDialogStandard

    def _set_style(self, style="light"):
        # Only support this feature on windows for now
        if not plat.ISWINDOWS:
            return
        if style == "dark":
            QApplication.setStyle(QStyleFactory.create("Fusion"))
            palette = QApplication.style().standardPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.black)
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(164, 166, 168))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(164, 166, 168))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(164, 166, 168))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(164, 166, 168))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(68, 68, 68))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(68, 68, 68))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(68, 68, 68))
        else:
            QApplication.setStyle(QStyleFactory.create("windowsvista" if plat.ISWINDOWS else "Fusion"))
            palette = QApplication.style().standardPalette()
        QToolTip.setPalette(palette)
        QApplication.setPalette(palette)

    # --- Public
    def add_selected_to_ignore_list(self):
        self.model.add_selected_to_ignore_list()

    def remove_selected(self):
        self.model.remove_selected(self)

    def confirm(self, title, msg, default_button=QMessageBox.Yes):
        active = QApplication.activeWindow()
        buttons = QMessageBox.Yes | QMessageBox.No
        answer = QMessageBox.question(active, title, msg, buttons, default_button)
        return answer == QMessageBox.Yes

    def invokeCustomCommand(self):
        self.model.invoke_custom_command()

    def show_details(self):
        if self.details_dialog is not None:
            if not self.details_dialog.isVisible():
                self.details_dialog.show()
            else:
                self.details_dialog.hide()

    def showResultsWindow(self):
        if self.resultWindow is not None:
            if self.use_tabs:
                if self.main_window.indexOfWidget(self.resultWindow) < 0:
                    self.main_window.addTab(self.resultWindow, tr("Results"), switch=True)
                    return
                self.main_window.showTab(self.resultWindow)
            else:
                self.resultWindow.show()

    def showDirectoriesWindow(self):
        if self.directories_dialog is not None:
            if self.use_tabs:
                self.main_window.showTab(self.directories_dialog)
            else:
                self.directories_dialog.show()

    def shutdown(self):
        self.willSavePrefs.emit()
        self.prefs.save()
        self.model.save()
        self.model.close()
        # Workaround for #857, hide() or close().
        if self.details_dialog is not None:
            self.details_dialog.close()
        QApplication.quit()

    # --- Signals
    willSavePrefs = pyqtSignal()
    SIGTERM = pyqtSignal()

    # --- Events
    def finishedLaunching(self):
        if sys.getfilesystemencoding() == "ascii":
            # No need to localize this, it's a debugging message.
            msg = (
                "Something is wrong with the way your system locale is set. If the files you're "
                "scanning have accented letters, you'll probably get a crash. It is advised that "
                "you set your system locale properly."
            )
            QMessageBox.warning(
                self.main_window if self.main_window else self.directories_dialog,
                "Wrong Locale",
                msg,
            )
        # Load results on open if passed a .dupeguru file
        if len(sys.argv) > 1:
            results = sys.argv[1]
            if results.endswith(".dupeguru"):
                self.model.load_from(results)
                self.recentResults.insertItem(results)

    def clearCacheTriggered(self):
        title = tr("Clear Cache")
        msg = tr("Do you really want to clear the cache? This will remove all cached file hashes and picture analysis.")
        if self.confirm(title, msg, QMessageBox.No):
            self.model.clear_picture_cache()
            self.model.clear_hash_cache()
            active = QApplication.activeWindow()
            QMessageBox.information(active, title, tr("Cache cleared."))

    def ignoreListTriggered(self):
        if self.use_tabs:
            self.showTriggeredTabbedDialog(self.ignoreListDialog, tr("Ignore List"))
        else:  # floating windows
            self.model.ignore_list_dialog.show()

    def excludeListTriggered(self):
        if self.use_tabs:
            self.showTriggeredTabbedDialog(self.excludeListDialog, tr("Exclusion Filters"))
        else:  # floating windows
            self.model.exclude_list_dialog.show()

    def showTriggeredTabbedDialog(self, dialog, desc_string):
        """Add tab for dialog, name the tab with desc_string, then show it."""
        index = self.main_window.indexOfWidget(dialog)
        # Create the tab if it doesn't exist already
        if index < 0:  # or (not dialog.isVisible() and not self.main_window.isTabVisible(index)):
            index = self.main_window.addTab(dialog, desc_string, switch=True)
        # Show the tab for that widget
        self.main_window.setCurrentIndex(index)

    def openDebugLogTriggered(self):
        debug_log_path = op.join(self.model.appdata, "debug.log")
        desktop.open_path(debug_log_path)

    def preferencesTriggered(self):
        preferences_dialog = self._get_preferences_dialog_class()(
            self.main_window if self.main_window else self.directories_dialog, self
        )
        preferences_dialog.load()
        result = preferences_dialog.exec()
        if result == QDialog.Accepted:
            preferences_dialog.save()
            self.prefs.save()
            self._update_options()
        preferences_dialog.setParent(None)

    def quitTriggered(self):
        if self.details_dialog is not None:
            self.details_dialog.close()

        if self.main_window:
            self.main_window.close()
        else:
            self.directories_dialog.close()

    def showAboutBoxTriggered(self):
        self.about_box.show()

    def showHelpTriggered(self):
        base_path = platform.HELP_PATH
        help_path = op.abspath(op.join(base_path, "index.html"))
        if op.exists(help_path):
            url = QUrl.fromLocalFile(help_path)
        else:
            url = QUrl("https://dupeguru.voltaicideas.net/help/en/")
        QDesktopServices.openUrl(url)

    def handleSIGTERM(self):
        self.shutdown()

    # --- model --> view
    def get_default(self, key):
        return self.prefs.get_value(key)

    def set_default(self, key, value):
        self.prefs.set_value(key, value)

    def show_message(self, msg):
        window = QApplication.activeWindow()
        QMessageBox.information(window, "", msg)

    def ask_yes_no(self, prompt):
        return self.confirm("", prompt)

    def create_results_window(self):
        """Creates resultWindow and details_dialog depending on the selected ``app_mode``."""
        if self.details_dialog is not None:
            # The object is not deleted entirely, avoid saving its geometry in the future
            # self.willSavePrefs.disconnect(self.details_dialog.appWillSavePrefs)
            # or simply delete it on close which is probably cleaner:
            self.details_dialog.setAttribute(Qt.WA_DeleteOnClose)
            self.details_dialog.close()
            # if we don't do the following, Qt will crash when we recreate the Results dialog
            self.details_dialog.setParent(None)
        if self.resultWindow is not None:
            self.resultWindow.close()
            # This is better for tabs, as it takes care of duplicate items in menu bar
            self.resultWindow.deleteLater() if self.use_tabs else self.resultWindow.setParent(None)
        if self.use_tabs:
            self.resultWindow = self.main_window.createPage("ResultWindow", parent=self.main_window, app=self)
        else:  # We don't use a tab widget, regular floating QMainWindow
            self.resultWindow = ResultWindow(self.directories_dialog, self)
            self.directories_dialog._updateActionsState()
        self.details_dialog = self._get_details_dialog_class()(self.resultWindow, self)

    def show_results_window(self):
        self.showResultsWindow()

    def show_problem_dialog(self):
        self.problemDialog.show()

    def select_dest_folder(self, prompt):
        flags = QFileDialog.ShowDirsOnly
        return QFileDialog.getExistingDirectory(self.resultWindow, prompt, "", flags)

    def select_dest_file(self, prompt, extension):
        files = tr("{} file (*.{})").format(extension.upper(), extension)
        destination, chosen_filter = QFileDialog.getSaveFileName(self.resultWindow, prompt, "", files)
        if not destination.endswith(".{}".format(extension)):
            destination = "{}.{}".format(destination, extension)
        return destination
