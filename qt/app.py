# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import sys
import os.path as op

from PyQt5.QtCore import QTimer, QObject, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QMessageBox

from hscommon.trans import trget
from hscommon import desktop

from qtlib.about_box import AboutBox
from qtlib.recent import Recent
from qtlib.util import createActions
from qtlib.progress_window import ProgressWindow

from core.app import AppMode, DupeGuru as DupeGuruModel
import core.pe.photo
from . import platform
from .preferences import Preferences
from .result_window import ResultWindow
from .directories_dialog import DirectoriesDialog
from .problem_dialog import ProblemDialog
from .ignore_list_dialog import IgnoreListDialog
from .deletion_options import DeletionOptions
from .se.details_dialog import DetailsDialog as DetailsDialogStandard
from .me.details_dialog import DetailsDialog as DetailsDialogMusic
from .pe.details_dialog import DetailsDialog as DetailsDialogPicture
from .se.preferences_dialog import PreferencesDialog as PreferencesDialogStandard
from .me.preferences_dialog import PreferencesDialog as PreferencesDialogMusic
from .pe.preferences_dialog import PreferencesDialog as PreferencesDialogPicture
from .pe.photo import File as PlatSpecificPhoto

tr = trget('ui')

class DupeGuru(QObject):
    LOGO_NAME = 'logo_se'
    NAME = 'dupeGuru'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefs = Preferences()
        self.prefs.load()
        self.model = DupeGuruModel(view=self)
        self._setup()

    #--- Private
    def _setup(self):
        core.pe.photo.PLAT_SPECIFIC_PHOTO_CLASS = PlatSpecificPhoto
        self._setupActions()
        self._update_options()
        self.recentResults = Recent(self, 'recentResults')
        self.recentResults.mustOpenItem.connect(self.model.load_from)
        self.resultWindow = None
        self.details_dialog = None
        self.directories_dialog = DirectoriesDialog(self)
        self.progress_window = ProgressWindow(self.directories_dialog, self.model.progress_window)
        self.problemDialog = ProblemDialog(parent=self.directories_dialog, model=self.model.problem_dialog)
        self.ignoreListDialog = IgnoreListDialog(parent=self.directories_dialog, model=self.model.ignore_list_dialog)
        self.deletionOptions = DeletionOptions(parent=self.directories_dialog, model=self.model.deletion_options)
        self.about_box = AboutBox(self.directories_dialog, self)

        self.directories_dialog.show()
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
            ('actionQuit', 'Ctrl+Q', '', tr("Quit"), self.quitTriggered),
            ('actionPreferences', 'Ctrl+P', '', tr("Options"), self.preferencesTriggered),
            ('actionIgnoreList', '', '', tr("Ignore List"), self.ignoreListTriggered),
            ('actionClearPictureCache', 'Ctrl+Shift+P', '', tr("Clear Picture Cache"), self.clearPictureCacheTriggered),
            ('actionShowHelp', 'F1', '', tr("dupeGuru Help"), self.showHelpTriggered),
            ('actionAbout', '', '', tr("About dupeGuru"), self.showAboutBoxTriggered),
            ('actionOpenDebugLog', '', '', tr("Open Debug Log"), self.openDebugLogTriggered),
        ]
        createActions(ACTIONS, self)

    def _update_options(self):
        self.model.options['mix_file_kind'] = self.prefs.mix_file_kind
        self.model.options['escape_filter_regexp'] = not self.prefs.use_regexp
        self.model.options['clean_empty_dirs'] = self.prefs.remove_empty_folders
        self.model.options['ignore_hardlink_matches'] = self.prefs.ignore_hardlink_matches
        self.model.options['copymove_dest_type'] = self.prefs.destination_type
        self.model.options['scan_type'] = self.prefs.get_scan_type(self.model.app_mode)
        self.model.options['min_match_percentage'] = self.prefs.filter_hardness
        self.model.options['word_weighting'] = self.prefs.word_weighting
        self.model.options['match_similar_words'] = self.prefs.match_similar
        threshold = self.prefs.small_file_threshold if self.prefs.ignore_small_files else 0
        self.model.options['size_threshold'] = threshold * 1024 # threshold is in KB. the scanner wants bytes
        scanned_tags = set()
        if self.prefs.scan_tag_track:
            scanned_tags.add('track')
        if self.prefs.scan_tag_artist:
            scanned_tags.add('artist')
        if self.prefs.scan_tag_album:
            scanned_tags.add('album')
        if self.prefs.scan_tag_title:
            scanned_tags.add('title')
        if self.prefs.scan_tag_genre:
            scanned_tags.add('genre')
        if self.prefs.scan_tag_year:
            scanned_tags.add('year')
        self.model.options['scanned_tags'] = scanned_tags
        self.model.options['match_scaled'] = self.prefs.match_scaled
        self.model.options['picture_cache_type'] = self.prefs.picture_cache_type

    #--- Private
    def _get_details_dialog_class(self):
        if self.model.app_mode == AppMode.Picture:
            return DetailsDialogPicture
        elif self.model.app_mode == AppMode.Music:
            return DetailsDialogMusic
        else:
            return DetailsDialogStandard

    def _get_preferences_dialog_class(self):
        if self.model.app_mode == AppMode.Picture:
            return PreferencesDialogPicture
        elif self.model.app_mode == AppMode.Music:
            return PreferencesDialogMusic
        else:
            return PreferencesDialogStandard

    #--- Public
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
            self.details_dialog.show()

    def showResultsWindow(self):
        if self.resultWindow is not None:
            self.resultWindow.show()

    def shutdown(self):
        self.willSavePrefs.emit()
        self.prefs.save()
        self.model.save()
        QApplication.quit()

    #--- Signals
    willSavePrefs = pyqtSignal()
    SIGTERM = pyqtSignal()

    #--- Events
    def finishedLaunching(self):
        if sys.getfilesystemencoding() == 'ascii':
            # No need to localize this, it's a debugging message.
            msg = "Something is wrong with the way your system locale is set. If the files you're "\
                "scanning have accented letters, you'll probably get a crash. It is advised that "\
                "you set your system locale properly."
            QMessageBox.warning(self.directories_dialog, "Wrong Locale", msg)

    def clearPictureCacheTriggered(self):
        title = tr("Clear Picture Cache")
        msg = tr("Do you really want to remove all your cached picture analysis?")
        if self.confirm(title, msg, QMessageBox.No):
            self.model.clear_picture_cache()
            active = QApplication.activeWindow()
            QMessageBox.information(active, title, tr("Picture cache cleared."))

    def ignoreListTriggered(self):
        self.model.ignore_list_dialog.show()

    def openDebugLogTriggered(self):
        debugLogPath = op.join(self.model.appdata, 'debug.log')
        desktop.open_path(debugLogPath)

    def preferencesTriggered(self):
        preferences_dialog = self._get_preferences_dialog_class()(self.directories_dialog, self)
        preferences_dialog.load()
        result = preferences_dialog.exec()
        if result == QDialog.Accepted:
            preferences_dialog.save()
            self.prefs.save()
            self._update_options()
        preferences_dialog.setParent(None)

    def quitTriggered(self):
        self.directories_dialog.close()

    def showAboutBoxTriggered(self):
        self.about_box.show()

    def showHelpTriggered(self):
        base_path = platform.HELP_PATH
        url = QUrl.fromLocalFile(op.abspath(op.join(base_path, 'index.html')))
        QDesktopServices.openUrl(url)

    def handleSIGTERM(self):
        self.shutdown()

    #--- model --> view
    def get_default(self, key):
        return self.prefs.get_value(key)

    def set_default(self, key, value):
        self.prefs.set_value(key, value)

    def show_message(self, msg):
        window = QApplication.activeWindow()
        QMessageBox.information(window, '', msg)

    def ask_yes_no(self, prompt):
        return self.confirm('', prompt)

    def create_results_window(self):
        """Creates resultWindow and details_dialog depending on the selected ``app_mode``.
        """
        if self.details_dialog is not None:
            self.details_dialog.close()
            self.details_dialog.setParent(None)
        if self.resultWindow is not None:
            self.resultWindow.close()
            self.resultWindow.setParent(None)
        self.resultWindow = ResultWindow(self.directories_dialog, self)
        self.details_dialog = self._get_details_dialog_class()(self.resultWindow, self)

    def show_results_window(self):
        self.showResultsWindow()

    def show_problem_dialog(self):
        self.problemDialog.show()

    def select_dest_folder(self, prompt):
        flags = QFileDialog.ShowDirsOnly
        return QFileDialog.getExistingDirectory(self.resultWindow, prompt, '', flags)

    def select_dest_file(self, prompt, extension):
        files = tr("{} file (*.{})").format(extension.upper(), extension)
        destination, chosen_filter = QFileDialog.getSaveFileName(self.resultWindow, prompt, '', files)
        if not destination.endswith('.{}'.format(extension)):
            destination = '{}.{}'.format(destination, extension)
        return destination
