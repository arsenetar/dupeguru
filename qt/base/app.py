# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license



import logging
import os
import os.path as op

from PyQt4.QtCore import QTimer, QObject, QCoreApplication, QUrl, SIGNAL, pyqtSignal
from PyQt4.QtGui import QDesktopServices, QFileDialog, QDialog, QMessageBox

from jobprogress import job
from jobprogress.qt import Progress

from core.app import DupeGuru as DupeGuruBase, JOB_SCAN, JOB_LOAD, JOB_MOVE, JOB_COPY, JOB_DELETE
    
from qtlib.about_box import AboutBox
from qtlib.reg import Registration

from . import platform

from .main_window import MainWindow
from .directories_dialog import DirectoriesDialog
from .problem_dialog import ProblemDialog

JOBID2TITLE = {
    JOB_SCAN: "Scanning for duplicates",
    JOB_LOAD: "Loading",
    JOB_MOVE: "Moving",
    JOB_COPY: "Copying",
    JOB_DELETE: "Sending files to the recycle bin",
}

class DupeGuru(DupeGuruBase, QObject):
    LOGO_NAME = '<replace this>'
    NAME = '<replace this>'
    DELTA_COLUMNS = frozenset()
    
    def __init__(self, data_module):
        appdata = str(QDesktopServices.storageLocation(QDesktopServices.DataLocation))
        if not op.exists(appdata):
            os.makedirs(appdata)
        # For basicConfig() to work, we have to be sure that no logging has taken place before this call.
        logging.basicConfig(filename=op.join(appdata, 'debug.log'), level=logging.WARNING)
        DupeGuruBase.__init__(self, data_module, appdata)
        QObject.__init__(self)
        self._setup()
    
    #--- Private
    def _setup(self):
        self.prefs = self._create_preferences()
        self.prefs.load()
        self._update_options()
        self.main_window = self._create_main_window()
        self._progress = Progress(self.main_window)
        self.directories_dialog = DirectoriesDialog(self.main_window, self)
        self.details_dialog = self._create_details_dialog(self.main_window)
        self.problemDialog = ProblemDialog(parent=self.main_window, app=self)
        self.preferences_dialog = self._create_preferences_dialog(self.main_window)
        self.about_box = AboutBox(self.main_window, self)
        
        self.reg = Registration(self)
        self.set_registration(self.prefs.registration_code, self.prefs.registration_email)
        if not self.registered and self.unpaid_hours >= 1:
            # The timer scheme is because if the nag is not shown before the application is 
            # completely initialized, the nag will be shown before the app shows up in the task bar
            # In some circumstances, the nag is hidden by other window, which may make the user think
            # that the application haven't launched.
            QTimer.singleShot(0, self.reg.show_nag)
        if self.prefs.mainWindowIsMaximized:
            self.main_window.showMaximized()
        else:
            self.main_window.show()
        self.load()
        
        self.connect(QCoreApplication.instance(), SIGNAL('aboutToQuit()'), self.application_will_terminate)
        self.connect(self._progress, SIGNAL('finished(QString)'), self.job_finished)
    
    def _setup_as_registered(self):
        self.prefs.registration_code = self.registration_code
        self.prefs.registration_email = self.registration_email
        self.main_window.actionRegister.setVisible(False)
        self.about_box.registerButton.hide()
        self.about_box.registeredEmailLabel.setText(self.prefs.registration_email)
    
    def _update_options(self):
        self.scanner.mix_file_kind = self.prefs.mix_file_kind
        self.options['escape_filter_regexp'] = self.prefs.use_regexp
        self.options['clean_empty_dirs'] = self.prefs.remove_empty_folders
        self.options['ignore_hardlink_matches'] = self.prefs.ignore_hardlink_matches
    
    #--- Virtual
    def _create_details_dialog(self, parent):
        raise NotImplementedError()
    
    def _create_main_window(self):
        return MainWindow(app=self)
    
    def _create_preferences(self):
        raise NotImplementedError()
    
    def _create_preferences_dialog(self, parent):
        raise NotImplementedError()
    
    #--- Override
    @staticmethod
    def _open_path(path):
        url = QUrl.fromLocalFile(str(path))
        QDesktopServices.openUrl(url)
    
    @staticmethod
    def _reveal_path(path):
        DupeGuru._open_path(path[:-1])
    
    def _start_job(self, jobid, func, *args):
        title = JOBID2TITLE[jobid]
        try:
            j = self._progress.create_job()
            args = tuple([j] + list(args))
            self._progress.run(jobid, title, func, args=args)
        except job.JobInProgressError:
            msg = "A previous action is still hanging in there. You can't start a new one yet. Wait a few seconds, then try again."
            QMessageBox.information(self.main_window, 'Action in progress', msg)
    
    def add_selected_to_ignore_list(self):
        dupes = self.without_ref(self.selected_dupes)
        if not dupes:
            return
        title = "Add to Ignore List"
        msg = "All selected {0} matches are going to be ignored in all subsequent scans. Continue?".format(len(dupes))
        if self.main_window._confirm(title, msg):
            DupeGuruBase.add_selected_to_ignore_list(self)
    
    def copy_or_move_marked(self, copy):
        opname = 'copy' if copy else 'move'
        title = "Select a directory to {0} marked files to".format(opname)
        flags = QFileDialog.ShowDirsOnly
        destination = str(QFileDialog.getExistingDirectory(self.main_window, title, '', flags))
        if not destination:
            return
        recreate_path = self.prefs.destination_type
        DupeGuruBase.copy_or_move_marked(self, copy, destination, recreate_path)
    
    def remove_selected(self):
        dupes = self.without_ref(self.selected_dupes)
        if not dupes:
            return
        title = "Remove duplicates"
        msg = "You are about to remove {0} files from results. Continue?".format(len(dupes))
        if self.main_window._confirm(title, msg):
            DupeGuruBase.remove_selected(self)
    
    #--- Public
    def askForRegCode(self):
        self.reg.ask_for_code()
    
    def invokeCustomCommand(self):
        cmd = self.prefs.custom_command
        if cmd:
            self.invoke_command(cmd)
        else:
            msg = "You have no custom command set up. Please, set it up in your preferences."
            QMessageBox.warning(self.main_window, 'Custom Command', msg)
    
    def openDebugLog(self):
        debugLogPath = op.join(self.appdata, 'debug.log')
        self._open_path(debugLogPath)
    
    def show_about_box(self):
        self.about_box.show()
    
    def show_details(self):
        self.details_dialog.show()
    
    def show_directories(self):
        self.directories_dialog.show()
    
    def show_help(self):
        base_path = platform.HELP_PATH.format(self.EDITION)
        url = QUrl.fromLocalFile(op.abspath(op.join(base_path, 'intro.htm')))
        QDesktopServices.openUrl(url)
    
    def show_preferences(self):
        self.preferences_dialog.load()
        result = self.preferences_dialog.exec_()
        if result == QDialog.Accepted:
            self.preferences_dialog.save()
            self.prefs.save()
            self._update_options()
    
    #--- Signals
    willSavePrefs = pyqtSignal()
    
    #--- Events
    def application_will_terminate(self):
        self.willSavePrefs.emit()
        self.prefs.save()
        self.save()
        self.save_ignore_list()
    
    def job_finished(self, jobid):
        self._job_completed(jobid)
        if jobid in (JOB_MOVE, JOB_COPY, JOB_DELETE):
            if self.results.problems:
                self.problemDialog.show()
            else:
                msg = "All files were processed successfully."
                QMessageBox.information(self.main_window, 'Operation Complete', msg)
        elif jobid == JOB_SCAN:
            if not self.results.groups:
                title = "Scanning complete"
                msg = "No duplicates found."
                QMessageBox.information(self.main_window, title, msg)
    
