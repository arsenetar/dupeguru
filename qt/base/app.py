# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import logging
import os
import os.path as op
import io

from PyQt4.QtCore import QTimer, QObject, QCoreApplication, QUrl, QProcess, SIGNAL, pyqtSignal
from PyQt4.QtGui import QDesktopServices, QFileDialog, QDialog, QMessageBox, QApplication

from jobprogress import job
from jobprogress.qt import Progress
from hscommon.trans import tr, trmsg

from core.app import DupeGuru as DupeGuruModel, JOB_SCAN, JOB_LOAD, JOB_MOVE, JOB_COPY, JOB_DELETE

from qtlib.about_box import AboutBox
from qtlib.recent import Recent
from qtlib.reg import Registration

from . import platform
from .extra_fairware_reminder import ExtraFairwareReminder
from .result_window import ResultWindow
from .directories_dialog import DirectoriesDialog
from .problem_dialog import ProblemDialog
from .util import createActions

JOBID2TITLE = {
    JOB_SCAN: tr("Scanning for duplicates"),
    JOB_LOAD: tr("Loading"),
    JOB_MOVE: tr("Moving"),
    JOB_COPY: tr("Copying"),
    JOB_DELETE: tr("Sending files to the recycle bin"),
}

class SysWrapper(io.IOBase):
    def write(self, s):
        if s.strip(): # don't log empty stuff
            logging.warning(s)

class DupeGuru(QObject):
    MODELCLASS = None
    LOGO_NAME = '<replace this>'
    NAME = '<replace this>'
    
    def __init__(self):
        QObject.__init__(self)
        appdata = str(QDesktopServices.storageLocation(QDesktopServices.DataLocation))
        if not op.exists(appdata):
            os.makedirs(appdata)
        # For basicConfig() to work, we have to be sure that no logging has taken place before this call.
        logging.basicConfig(filename=op.join(appdata, 'debug.log'), level=logging.WARNING,
            format='%(asctime)s - %(levelname)s - %(message)s')
        if sys.stderr is None: # happens under a cx_freeze environment
            sys.stderr = SysWrapper()
        if sys.stdout is None:
            sys.stdout = SysWrapper()
        self.prefs = self._create_preferences()
        self.prefs.load()
        self.model = self.MODELCLASS(view=self, appdata=appdata)
        self._setup()
    
    #--- Private
    def _setup(self):
        self._setupActions()
        self._update_options()
        self.recentResults = Recent(self, 'recentResults')
        self.recentResults.mustOpenItem.connect(self.model.load_from)
        self.resultWindow = self._create_result_window()
        self._progress = Progress(self.resultWindow)
        self.directories_dialog = DirectoriesDialog(self.resultWindow, self)
        self.details_dialog = self._create_details_dialog(self.resultWindow)
        self.problemDialog = ProblemDialog(parent=self.resultWindow, app=self)
        self.preferences_dialog = self._create_preferences_dialog(self.resultWindow)
        self.about_box = AboutBox(self.resultWindow, self)
        
        
        self.reg = Registration(self.model)
        self.model.set_registration(self.prefs.registration_code, self.prefs.registration_email)
        if self.model.should_show_fairware_reminder:
            # The timer scheme is because if the nag is not shown before the application is 
            # completely initialized, the nag will be shown before the app shows up in the task bar
            # In some circumstances, the nag is hidden by other window, which may make the user think
            # that the application haven't launched.
            QTimer.singleShot(0, self.reg.show_nag)
        self.directories_dialog.show()
        self.model.load()
        
        self.connect(QCoreApplication.instance(), SIGNAL('aboutToQuit()'), self.application_will_terminate)
        self.connect(self._progress, SIGNAL('finished(QString)'), self.job_finished)
    
    def _setupActions(self):
        # Setup actions that are common to both the directory dialog and the results window.
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            ('actionQuit', 'Ctrl+Q', '', tr("Quit"), self.quitTriggered),
            ('actionPreferences', 'Ctrl+P', '', tr("Preferences"), self.preferencesTriggered),
            ('actionShowHelp', 'F1', '', tr("dupeGuru Help"), self.showHelpTriggered),
            ('actionAbout', '', '', tr("About dupeGuru"), self.showAboutBoxTriggered),
            ('actionRegister', '', '', tr("Register dupeGuru"), self.registerTriggered),
            ('actionCheckForUpdate', '', '', tr("Check for Update"), self.checkForUpdateTriggered),
            ('actionOpenDebugLog', '', '', tr("Open Debug Log"), self.openDebugLogTriggered),
        ]
        createActions(ACTIONS, self)
        
        if sys.platform == 'linux2':
            self.actionCheckForUpdate.setVisible(False) # This only works on Windows
    
    def _setup_as_registered(self):
        self.prefs.registration_code = self.registration_code
        self.prefs.registration_email = self.registration_email
        self.actionRegister.setVisible(False)
        self.about_box.registerButton.hide()
        self.about_box.registeredEmailLabel.setText(self.prefs.registration_email)
    
    def _update_options(self):
        self.model.scanner.mix_file_kind = self.prefs.mix_file_kind
        self.model.options['escape_filter_regexp'] = self.prefs.use_regexp
        self.model.options['clean_empty_dirs'] = self.prefs.remove_empty_folders
        self.model.options['ignore_hardlink_matches'] = self.prefs.ignore_hardlink_matches
    
    #--- Virtual
    def _create_details_dialog(self, parent):
        raise NotImplementedError()
    
    def _create_result_window(self):
        return ResultWindow(app=self)
    
    def _create_preferences(self):
        raise NotImplementedError()
    
    def _create_preferences_dialog(self, parent):
        raise NotImplementedError()
    
    #--- Public
    def add_selected_to_ignore_list(self):
        dupes = self.model.without_ref(self.model.selected_dupes)
        if not dupes:
            return
        title = tr("Add to Ignore List")
        msg = trmsg("IgnoreConfirmMsg").format(len(dupes))
        if self.confirm(title, msg):
            self.model.add_selected_to_ignore_list(self)
    
    def copy_or_move_marked(self, copy):
        opname = tr("copy") if copy else tr("move")
        title = trmsg("SelectCopyOrMoveDestinationMsg").format(opname)
        flags = QFileDialog.ShowDirsOnly
        destination = str(QFileDialog.getExistingDirectory(self.resultWindow, title, '', flags))
        if not destination:
            return
        recreate_path = self.prefs.destination_type
        self.model.copy_or_move_marked(self, copy, destination, recreate_path)
    
    def remove_selected(self):
        dupes = self.model.without_ref(self.model.selected_dupes)
        if not dupes:
            return
        title = tr("Remove duplicates")
        msg = trmsg("FileRemovalConfirmMsg").format(len(dupes))
        if self.confirm(title, msg):
            self.model.remove_selected(self)
    
    def askForRegCode(self):
        self.reg.ask_for_code()
    
    def confirm(self, title, msg, default_button=QMessageBox.Yes):
        active = QApplication.activeWindow()
        buttons = QMessageBox.Yes | QMessageBox.No
        answer = QMessageBox.question(active, title, msg, buttons, default_button)
        return answer == QMessageBox.Yes
    
    def invokeCustomCommand(self):
        cmd = self.prefs.custom_command
        if cmd:
            self.model.invoke_command(cmd)
        else:
            msg = trmsg("NoCustomCommandMsg")
            QMessageBox.warning(self.resultWindow, tr("Custom Command"), msg)
    
    def show_details(self):
        self.details_dialog.show()
    
    def showResultsWindow(self):
        self.resultWindow.show()
    
    #--- Signals
    willSavePrefs = pyqtSignal()
    
    #--- Events
    def application_will_terminate(self):
        self.willSavePrefs.emit()
        self.prefs.save()
        self.model.save()
    
    def checkForUpdateTriggered(self):
        QProcess.execute('updater.exe', ['/checknow'])
    
    def job_finished(self, jobid):
        self.model._job_completed(jobid)
        if jobid in (JOB_MOVE, JOB_COPY, JOB_DELETE):
            if self.model.results.problems:
                self.problemDialog.show()
            else:
                msg = trmsg("OperationSuccessMsg")
                QMessageBox.information(self.resultWindow, tr("Operation Complete"), msg)
        elif jobid == JOB_SCAN:
            if not self.model.results.groups:
                title = tr("Scan complete")
                msg = trmsg("NoDuplicateFoundMsg")
                QMessageBox.information(self.resultWindow, title, msg)
            else:
                self.showResultsWindow()
        elif jobid == JOB_LOAD:
            self.showResultsWindow()
    
    def openDebugLogTriggered(self):
        debugLogPath = op.join(self.model.appdata, 'debug.log')
        self.open_path(debugLogPath)
    
    def preferencesTriggered(self):
        self.preferences_dialog.load()
        result = self.preferences_dialog.exec()
        if result == QDialog.Accepted:
            self.preferences_dialog.save()
            self.prefs.save()
            self._update_options()
    
    def quitTriggered(self):
        self.directories_dialog.close()
    
    def registerTriggered(self):
        self.reg.ask_for_code()
    
    def showAboutBoxTriggered(self):
        self.about_box.show()
    
    def showHelpTriggered(self):
        base_path = platform.HELP_PATH.format(self.EDITION)
        url = QUrl.fromLocalFile(op.abspath(op.join(base_path, 'index.html')))
        QDesktopServices.openUrl(url)
    
    #--- model --> view
    @staticmethod
    def open_path(path):
        url = QUrl.fromLocalFile(str(path))
        QDesktopServices.openUrl(url)
    
    @staticmethod
    def reveal_path(path):
        DupeGuru.open_path(path[:-1])
    
    def start_job(self, jobid, func, args=()):
        title = JOBID2TITLE[jobid]
        try:
            j = self._progress.create_job()
            args = (j, ) + tuple(args)
            self._progress.run(jobid, title, func, args=args)
        except job.JobInProgressError:
            msg = trmsg("TaskHangingMsg")
            QMessageBox.information(self.resultWindow, 'Action in progress', msg)
    
    def get_default(self, key):
        return self.prefs.get_value(key)
    
    def set_default(self, key, value):
        self.prefs.set_value(key, value)
    
    def show_extra_fairware_reminder(self):
        dialog = ExtraFairwareReminder(self.directories_dialog, self)
        dialog.exec()
    
