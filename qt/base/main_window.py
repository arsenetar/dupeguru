# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys

from PyQt4.QtCore import Qt, QCoreApplication, QProcess, SIGNAL, QUrl
from PyQt4.QtGui import (QMainWindow, QMenu, QPixmap, QIcon, QToolButton, QLabel, QHeaderView,
    QMessageBox, QInputDialog, QLineEdit, QDesktopServices, QFileDialog)

from hsutil.misc import nonone

from core.app import NoScannableFileError, AllFilesAreRefError

from . import dg_rc
from .main_window_ui import Ui_MainWindow
from .results_model import ResultsModel
from .stats_label import StatsLabel

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app):
        QMainWindow.__init__(self, None)
        self.app = app
        self._last_filter = None
        self._setupUi()
        self.resultsModel = ResultsModel(self.app, self.resultsView) 
        self.stats = StatsLabel(app, self.statusLabel)
        self._load_columns()
        self._update_column_actions_status()
        
        self.connect(self.actionQuit, SIGNAL('triggered()'), QCoreApplication.instance().quit)
        self.connect(self.menuColumns, SIGNAL('triggered(QAction*)'), self.columnToggled)
        self.connect(QCoreApplication.instance(), SIGNAL('aboutToQuit()'), self.application_will_terminate)
        self.connect(self.resultsView, SIGNAL('doubleClicked()'), self.resultsDoubleClicked)
        self.connect(self.resultsView, SIGNAL('spacePressed()'), self.resultsSpacePressed)
        
        # Actions (the vast majority of them are connected in the UI file, but I'm trying to
        # phase away from those, and these connections are harder to maintain than through simple
        # code
        self.actionInvokeCustomCommand.triggered.connect(self.app.invokeCustomCommand)
        self.actionLoadResults.triggered.connect(self.loadResultsTriggered)
        self.actionSaveResults.triggered.connect(self.saveResultsTriggered)
    
    def _setupUi(self):
        self.setupUi(self)
        # Stuff that can't be setup in the Designer
        h = self.resultsView.header()
        h.setHighlightSections(False)
        h.setMovable(True)
        h.setStretchLastSection(False)
        h.setDefaultAlignment(Qt.AlignLeft)
        
        self.setWindowTitle(QCoreApplication.instance().applicationName())
        self.actionScan.setIcon(QIcon(QPixmap(':/%s' % self.app.LOGO_NAME)))
        
        # Columns menu
        menu = self.menuColumns
        self._column_actions = []
        for index, column in enumerate(self.app.data.COLUMNS):
            action = menu.addAction(column['display'])
            action.setCheckable(True)
            action.column_index = index
            self._column_actions.append(action)
        menu.addSeparator()
        action = menu.addAction("Reset to Defaults")
        action.column_index = -1
        
        # Action menu
        actionMenu = QMenu('Actions', self.toolBar)
        actionMenu.setIcon(QIcon(QPixmap(":/actions")))
        actionMenu.addAction(self.actionDeleteMarked)
        actionMenu.addAction(self.actionMoveMarked)
        actionMenu.addAction(self.actionCopyMarked)
        actionMenu.addAction(self.actionRemoveMarked)
        actionMenu.addSeparator()
        actionMenu.addAction(self.actionRemoveSelected)
        actionMenu.addAction(self.actionIgnoreSelected)
        actionMenu.addAction(self.actionMakeSelectedReference)
        actionMenu.addSeparator()
        actionMenu.addAction(self.actionOpenSelected)
        actionMenu.addAction(self.actionRevealSelected)
        actionMenu.addAction(self.actionInvokeCustomCommand)
        actionMenu.addAction(self.actionRenameSelected)
        self.actionActions.setMenu(actionMenu)
        button = QToolButton(self.toolBar)
        button.setDefaultAction(actionMenu.menuAction())
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.actionsButton = button
        self.toolBar.insertWidget(self.actionActions, button) # the action is a placeholder
        self.toolBar.removeAction(self.actionActions)
        
        self.statusLabel = QLabel(self)
        self.statusbar.addPermanentWidget(self.statusLabel, 1)
        
        # Linux setup
        if sys.platform == 'linux2':
            self.actionCheckForUpdate.setVisible(False) # This only works on Windows
    
    #--- Private
    def _confirm(self, title, msg, default_button=QMessageBox.Yes):
        buttons = QMessageBox.Yes | QMessageBox.No
        answer = QMessageBox.question(self, title, msg, buttons, default_button)
        return answer == QMessageBox.Yes
    
    def _load_columns(self):
        h = self.resultsView.header()
        h.setResizeMode(QHeaderView.Interactive)
        prefs = self.app.prefs
        attrs = list(zip(prefs.columns_width, prefs.columns_visible))
        for index, (width, visible) in enumerate(attrs):
            h.resizeSection(index, width)
            h.setSectionHidden(index, not visible)
        h.setResizeMode(0, QHeaderView.Stretch)
    
    def _save_columns(self):
        h = self.resultsView.header()
        widths = []
        visible = []
        for i in range(len(self.app.data.COLUMNS)):
            widths.append(h.sectionSize(i))
            visible.append(not h.isSectionHidden(i))
        prefs = self.app.prefs
        prefs.columns_width = widths
        prefs.columns_visible = visible
        prefs.save()
    
    def _update_column_actions_status(self):
        h = self.resultsView.header()
        for action in self._column_actions:
            colid = action.column_index
            action.setChecked(not h.isSectionHidden(colid))
    
    #--- Actions
    def aboutTriggered(self):
        self.app.show_about_box()
    
    def actionsTriggered(self):
        self.actionsButton.showMenu()
    
    def addToIgnoreListTriggered(self):
        self.app.add_selected_to_ignore_list()
    
    def applyFilterTriggered(self):
        title = "Apply Filter"
        msg = "Type the filter you want to apply on your results. See help for details."
        text = nonone(self._last_filter, '[*]')
        answer, ok = QInputDialog.getText(self, title, msg, QLineEdit.Normal, text)
        if not ok:
            return
        answer = str(answer)
        self.app.apply_filter(answer)
        self._last_filter = answer
    
    def cancelFilterTriggered(self):
        self.app.apply_filter('')
    
    def checkForUpdateTriggered(self):
        QProcess.execute('updater.exe', ['/checknow'])
    
    def clearIgnoreListTriggered(self):
        title = "Clear Ignore List"
        count = len(self.app.scanner.ignore_list)
        if not count:
            QMessageBox.information(self, title, "Nothing to clear.")
            return
        msg = "Do you really want to remove all {0} items from the ignore list?".format(count)
        if self._confirm(title, msg, QMessageBox.No):
            self.app.scanner.ignore_list.Clear()
            QMessageBox.information(self, title, "Ignore list cleared.")
    
    def copyTriggered(self):
        self.app.copy_or_move_marked(True)
    
    def deleteTriggered(self):
        count = self.app.results.mark_count
        if not count:
            return
        title = "Delete duplicates"
        msg = "You are about to send {0} files to the recycle bin. Continue?".format(count)
        if self._confirm(title, msg):
            self.app.delete_marked()
    
    def deltaTriggered(self):
        self.resultsModel.delta_values = self.actionDelta.isChecked()
    
    def detailsTriggered(self):
        self.app.show_details()
    
    def directoriesTriggered(self):
        self.app.show_directories()
    
    def exportTriggered(self):
        h = self.resultsView.header()
        column_ids = []
        for i in range(len(self.app.data.COLUMNS)):
            if not h.isSectionHidden(i):
                column_ids.append(str(i))
        exported_path = self.app.export_to_xhtml(column_ids)
        url = QUrl.fromLocalFile(exported_path)
        QDesktopServices.openUrl(url)
    
    def loadResultsTriggered(self):
        title = "Select a results file to load"
        files = "dupeGuru Results (*.dupeguru)"
        destination = QFileDialog.getOpenFileName(self, title, '', files)
        if destination:
            self.app.load_from(destination)
    
    def makeReferenceTriggered(self):
        self.app.make_selected_reference()
    
    def markAllTriggered(self):
        self.app.mark_all()
    
    def markInvertTriggered(self):
        self.app.mark_invert()
    
    def markNoneTriggered(self):
        self.app.mark_none()
    
    def markSelectedTriggered(self):
        self.app.toggle_selected_mark_state()
    
    def moveTriggered(self):
        self.app.copy_or_move_marked(False)
    
    def openDebugLogTriggered(self):
        self.app.openDebugLog()
    
    def openTriggered(self):
        self.app.open_selected()
    
    def powerMarkerTriggered(self):
        self.resultsModel.power_marker = self.actionPowerMarker.isChecked()
    
    def preferencesTriggered(self):
        self.app.show_preferences()
    
    def registerTrigerred(self):
        self.app.ask_for_reg_code()
    
    def removeMarkedTriggered(self):
        count = self.app.results.mark_count
        if not count:
            return
        title = "Remove duplicates"
        msg = "You are about to remove {0} files from results. Continue?".format(count)
        if self._confirm(title, msg):
            self.app.remove_marked()
    
    def removeSelectedTriggered(self):
        self.app.remove_selected()
    
    def renameTriggered(self):
        self.resultsView.edit(self.resultsView.selectionModel().currentIndex())
    
    def revealTriggered(self):
        self.app.reveal_selected()
    
    def saveResultsTriggered(self):
        title = "Select a file to save your results to"
        files = "dupeGuru Results (*.dupeguru)"
        destination = QFileDialog.getSaveFileName(self, title, '', files)
        if destination:
            self.app.save_as(destination)
    
    def scanTriggered(self):
        title = "Start a new scan"
        if len(self.app.results.groups) > 0:
            msg = "Are you sure you want to start a new duplicate scan?"
            if not self._confirm(title, msg):
                return
        try:
            self.app.start_scanning()
        except NoScannableFileError:
            msg = "The selected directories contain no scannable file."
            QMessageBox.warning(self, title, msg)
            self.app.show_directories()
        except AllFilesAreRefError:
            msg = "You cannot make a duplicate scan with only reference directories."
            QMessageBox.warning(self, title, msg)
    
    def showHelpTriggered(self):
        self.app.show_help()
    
    #--- Events
    def application_will_terminate(self):
        self._save_columns()
    
    def columnToggled(self, action):
        colid = action.column_index
        if colid == -1:
            self.app.prefs.reset_columns()
            self._load_columns()
        else:
            h = self.resultsView.header()
            h.setSectionHidden(colid, not h.isSectionHidden(colid))
        self._update_column_actions_status()
    
    def contextMenuEvent(self, event):
        self.actionActions.menu().exec_(event.globalPos())
    
    def resultsDoubleClicked(self):
        self.app.open_selected()
    
    def resultsSpacePressed(self):
        self.app.toggle_selected_mark_state()
    
