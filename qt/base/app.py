# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

import logging
import os
import os.path as op

from PyQt4.QtCore import QTimer, QObject, QCoreApplication, QUrl, SIGNAL
from PyQt4.QtGui import QDesktopServices, QFileDialog, QDialog, QMessageBox

from hsutil import job
from hsutil.reg import RegistrationRequired

from core.app import DupeGuru as DupeGuruBase, JOB_SCAN, JOB_LOAD, JOB_MOVE, JOB_COPY, JOB_DELETE
    
from qtlib.about_box import AboutBox
from qtlib.progress import Progress
from qtlib.reg import Registration

from . import platform

from .main_window import MainWindow
from .directories_dialog import DirectoriesDialog

JOBID2TITLE = {
    JOB_SCAN: "Scanning for duplicates",
    JOB_LOAD: "Loading",
    JOB_MOVE: "Moving",
    JOB_COPY: "Copying",
    JOB_DELETE: "Sending files to the recycle bin",
}

def demo_method(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except RegistrationRequired:
            msg = "The demo version of dupeGuru only allows 10 actions (delete/move/copy) per session."
            QMessageBox.information(self.main_window, 'Demo', msg)
    
    return wrapper

class DupeGuru(DupeGuruBase, QObject):
    LOGO_NAME = '<replace this>'
    NAME = '<replace this>'
    DELTA_COLUMNS = frozenset()
    
    def __init__(self, data_module, appid):
        appdata = unicode(QDesktopServices.storageLocation(QDesktopServices.DataLocation))
        if not op.exists(appdata):
            os.makedirs(appdata)
        # For basicConfig() to work, we have to be sure that no logging has taken place before this call.
        logging.basicConfig(filename=op.join(appdata, 'debug.log'), level=logging.WARNING)
        DupeGuruBase.__init__(self, data_module, appdata, appid)
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
        self.preferences_dialog = self._create_preferences_dialog(self.main_window)
        self.about_box = AboutBox(self.main_window, self)
        
        self.reg = Registration(self)
        self.set_registration(self.prefs.registration_code, self.prefs.registration_email)
        if not self.registered:
            # The timer scheme is because if the nag is not shown before the application is 
            # completely initialized, the nag will be shown before the app shows up in the task bar
            # In some circumstances, the nag is hidden by other window, which may make the user think
            # that the application haven't launched.
            self._nagTimer = QTimer()
            self.connect(self._nagTimer, SIGNAL('timeout()'), self.mustShowNag)
            self._nagTimer.start(0)
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
        url = QUrl.fromLocalFile(unicode(path))
        QDesktopServices.openUrl(url)
    
    @staticmethod
    def _reveal_path(path):
        DupeGuru._open_path(path[:-1])
    
    def _start_job(self, jobid, func):
        title = JOBID2TITLE[jobid]
        try:
            j = self._progress.create_job()
            self._progress.run(jobid, title, func, args=(j, ))
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
    
    @demo_method
    def copy_or_move_marked(self, copy):
        opname = 'copy' if copy else 'move'
        title = "Select a directory to {0} marked files to".format(opname)
        flags = QFileDialog.ShowDirsOnly
        destination = unicode(QFileDialog.getExistingDirectory(self.main_window, title, '', flags))
        if not destination:
            return
        recreate_path = self.prefs.destination_type
        DupeGuruBase.copy_or_move_marked(self, copy, destination, recreate_path)
    
    delete_marked = demo_method(DupeGuruBase.delete_marked)
    
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
    
    #--- Events
    def application_will_terminate(self):
        self.save()
        self.save_ignore_list()
    
    def mustShowNag(self):
        self._nagTimer.stop() # must be shown only once
        self.reg.show_nag()
    
    def job_finished(self, jobid):
        self._job_completed(jobid)
        if jobid in (JOB_MOVE, JOB_COPY, JOB_DELETE) and self.last_op_error_count > 0:
            msg = "{0} files could not be processed.".format(self.results.mark_count)
            QMessageBox.warning(self.main_window, 'Warning', msg)
        elif jobid == JOB_SCAN:
            if not self.results.groups:
                title = "Scanning complete"
                msg = "No duplicates found."
                QMessageBox.information(self.main_window, title, msg)
    
