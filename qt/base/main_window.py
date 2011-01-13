# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys

from PyQt4.QtCore import Qt, QCoreApplication, QProcess, SIGNAL, QUrl, QRect
from PyQt4.QtGui import (QMainWindow, QMenu, QPixmap, QIcon, QToolButton, QLabel, QHeaderView,
    QMessageBox, QInputDialog, QLineEdit, QDesktopServices, QFileDialog, QAction, QMenuBar,
    QToolBar, QWidget, QVBoxLayout, QAbstractItemView, QStatusBar)

from hscommon.util import nonone
from qtlib.recent import Recent

from core.app import NoScannableFileError

from . import dg_rc
from .results_model import ResultsModel, ResultsView
from .stats_label import StatsLabel

class MainWindow(QMainWindow):
    def __init__(self, app):
        QMainWindow.__init__(self, None)
        self.app = app
        self._last_filter = None
        self._setupUi()
        self.resultsModel = ResultsModel(self.app, self.resultsView) 
        self.stats = StatsLabel(app, self.statusLabel)
        self._load_columns()
        self._update_column_actions_status()
        
        self.connect(self.menuColumns, SIGNAL('triggered(QAction*)'), self.columnToggled)
        self.connect(self.resultsView, SIGNAL('doubleClicked()'), self.resultsDoubleClicked)
        self.connect(self.resultsView, SIGNAL('spacePressed()'), self.resultsSpacePressed)
        self.app.willSavePrefs.connect(self.appWillSavePrefs)
    
    def _setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            ('actionScan', 'Ctrl+T', self.app.LOGO_NAME, "Start Scan", self.scanTriggered),
            ('actionDirectories', 'Ctrl+4', 'folder', "Directories", self.directoriesTriggered),
            ('actionDetails', 'Ctrl+3', 'details', "Details", self.detailsTriggered),
            ('actionActions', '', 'actions', "Actions", self.actionsTriggered),
            ('actionPreferences', 'Ctrl+5', 'preferences', "Preferences", self.preferencesTriggered),
            ('actionDelta', 'Ctrl+2', 'delta', "Delta Values", self.deltaTriggered),
            ('actionPowerMarker', 'Ctrl+1', 'power_marker', "Power Marker", self.powerMarkerTriggered),
            ('actionDeleteMarked', 'Ctrl+D', '', "Send Marked to Recycle Bin", self.deleteTriggered),
            ('actionHardlinkMarked', 'Ctrl+Shift+D', '', "Delete Marked and Replace with Hardlinks", self.hardlinkTriggered),
            ('actionMoveMarked', 'Ctrl+M', '', "Move Marked to...", self.moveTriggered),
            ('actionCopyMarked', 'Ctrl+Shift+M', '', "Copy Marked to...", self.copyTriggered),
            ('actionRemoveMarked', 'Ctrl+R', '', "Remove Marked from Results", self.removeMarkedTriggered),
            ('actionRemoveSelected', 'Ctrl+Del', '', "Remove Selected from Results", self.removeSelectedTriggered),
            ('actionIgnoreSelected', 'Ctrl+Shift+Del', '', "Add Selected to Ignore List", self.addToIgnoreListTriggered),
            ('actionMakeSelectedReference', 'Ctrl+Space', '', "Make Selected Reference", self.makeReferenceTriggered),
            ('actionOpenSelected', 'Ctrl+O', '', "Open Selected with Default Application", self.openTriggered),
            ('actionRevealSelected', 'Ctrl+Shift+O', '', "Open Containing Folder of Selected", self.revealTriggered),
            ('actionRenameSelected', 'F2', '', "Rename Selected", self.renameTriggered),
            ('actionMarkAll', 'Ctrl+A', '', "Mark All", self.markAllTriggered),
            ('actionMarkNone', 'Ctrl+Shift+A', '', "Mark None", self.markNoneTriggered),
            ('actionInvertMarking', 'Ctrl+Alt+A', '', "Invert Marking", self.markInvertTriggered),
            ('actionMarkSelected', '', '', "Mark Selected", self.markSelectedTriggered),
            ('actionClearIgnoreList', '', '', "Clear Ignore List", self.clearIgnoreListTriggered),
            ('actionQuit', 'Ctrl+Q', '', "Quit", self.close),
            ('actionApplyFilter', 'Ctrl+F', '', "Apply Filter", self.applyFilterTriggered),
            ('actionCancelFilter', 'Ctrl+Shift+F', '', "Cancel Filter", self.cancelFilterTriggered),
            ('actionShowHelp', 'F1', '', "dupeGuru Help", self.showHelpTriggered),
            ('actionAbout', '', '', "About dupeGuru", self.aboutTriggered),
            ('actionRegister', '', '', "Register dupeGuru", self.registerTrigerred),
            ('actionCheckForUpdate', '', '', "Check for Update", self.checkForUpdateTriggered),
            ('actionExport', '', '', "Export To HTML", self.exportTriggered),
            ('actionLoadResults', 'Ctrl+L', '', "Load Results...", self.loadResultsTriggered),
            ('actionSaveResults', 'Ctrl+S', '', "Save Results...", self.saveResultsTriggered),
            ('actionOpenDebugLog', '', '', "Open Debug Log", self.openDebugLogTriggered),
            ('actionInvokeCustomCommand', 'Ctrl+I', '', "Invoke Custom Command", self.app.invokeCustomCommand),
        ]
        for name, shortcut, icon, desc, func in ACTIONS:
            action = QAction(self)
            if icon:
                action.setIcon(QIcon(QPixmap(':/' + icon)))
            if shortcut:
                action.setShortcut(shortcut)
            action.setText(desc)
            action.triggered.connect(func)
            setattr(self, name, action)
        self.actionDelta.setCheckable(True)
        self.actionPowerMarker.setCheckable(True)
    
    def _setupMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 630, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setTitle("File")
        self.menuMark = QMenu(self.menubar)
        self.menuMark.setTitle("Mark")
        self.menuActions = QMenu(self.menubar)
        self.menuActions.setTitle("Actions")
        self.menuColumns = QMenu(self.menubar)
        self.menuColumns.setTitle("Columns")
        self.menuModes = QMenu(self.menubar)
        self.menuModes.setTitle("Modes")
        self.menuWindow = QMenu(self.menubar)
        self.menuWindow.setTitle("Windows")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setTitle("Help")
        self.menuLoadRecent = QMenu(self.menuFile)
        self.menuLoadRecent.setTitle("Load Recent Results")
        self.setMenuBar(self.menubar)
        
        self.menuActions.addAction(self.actionDeleteMarked)
        self.menuActions.addAction(self.actionHardlinkMarked)
        self.menuActions.addAction(self.actionMoveMarked)
        self.menuActions.addAction(self.actionCopyMarked)
        self.menuActions.addAction(self.actionRemoveMarked)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.actionRemoveSelected)
        self.menuActions.addAction(self.actionIgnoreSelected)
        self.menuActions.addAction(self.actionMakeSelectedReference)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.actionOpenSelected)
        self.menuActions.addAction(self.actionRevealSelected)
        self.menuActions.addAction(self.actionInvokeCustomCommand)
        self.menuActions.addAction(self.actionRenameSelected)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.actionApplyFilter)
        self.menuActions.addAction(self.actionCancelFilter)
        self.menuMark.addAction(self.actionMarkAll)
        self.menuMark.addAction(self.actionMarkNone)
        self.menuMark.addAction(self.actionInvertMarking)
        self.menuMark.addAction(self.actionMarkSelected)
        self.menuModes.addAction(self.actionPowerMarker)
        self.menuModes.addAction(self.actionDelta)
        self.menuWindow.addAction(self.actionDetails)
        self.menuWindow.addAction(self.actionDirectories)
        self.menuWindow.addAction(self.actionPreferences)
        self.menuHelp.addAction(self.actionShowHelp)
        self.menuHelp.addAction(self.actionRegister)
        self.menuHelp.addAction(self.actionCheckForUpdate)
        self.menuHelp.addAction(self.actionOpenDebugLog)
        self.menuHelp.addAction(self.actionAbout)
        self.menuFile.addAction(self.actionScan)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoadResults)
        self.menuFile.addAction(self.menuLoadRecent.menuAction())
        self.menuFile.addAction(self.actionSaveResults)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionClearIgnoreList)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuMark.menuAction())
        self.menubar.addAction(self.menuActions.menuAction())
        self.menubar.addAction(self.menuColumns.menuAction())
        self.menubar.addAction(self.menuModes.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
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
        actionMenu = QMenu('Actions', self.menubar)
        actionMenu.setIcon(QIcon(QPixmap(":/actions")))
        actionMenu.addAction(self.actionDeleteMarked)
        actionMenu.addAction(self.actionHardlinkMarked)
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
    
    def _setupToolbar(self):
        self.toolBar = QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolBar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea(Qt.TopToolBarArea), self.toolBar)
        
        self.toolBar.addAction(self.actionScan)
        button = QToolButton(self.toolBar)
        button.setDefaultAction(self.actionActions.menu().menuAction())
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.actionsButton = button
        self.toolBar.addWidget(button)
        self.toolBar.addAction(self.actionDirectories)
        self.toolBar.addAction(self.actionDetails)
        self.toolBar.addAction(self.actionPreferences)
        self.toolBar.addAction(self.actionDelta)
        self.toolBar.addAction(self.actionPowerMarker)
    
    def _setupUi(self):
        self.setWindowTitle(QCoreApplication.instance().applicationName())
        self.resize(630, 514)
        self.centralwidget = QWidget(self)
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setMargin(0)
        self.resultsView = ResultsView(self.centralwidget)
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsView.setSortingEnabled(True)
        self.resultsView.verticalHeader().setVisible(False)
        self.resultsView.verticalHeader().setDefaultSectionSize(18)
        h = self.resultsView.horizontalHeader()
        h.setHighlightSections(False)
        h.setMovable(True)
        h.setStretchLastSection(False)
        h.setDefaultAlignment(Qt.AlignLeft)
        self.verticalLayout_2.addWidget(self.resultsView)
        self.setCentralWidget(self.centralwidget)
        self._setupActions()
        self._setupMenu()
        self._setupToolbar()
        self.recentResults = Recent(self.app, self.menuLoadRecent, 'recentResults')
        self.recentResults.mustOpenItem.connect(self.app.load_from)
        self.statusbar = QStatusBar(self)
        self.statusbar.setSizeGripEnabled(True)
        self.setStatusBar(self.statusbar)
        self.statusLabel = QLabel(self)
        self.statusbar.addPermanentWidget(self.statusLabel, 1)
        
        if self.app.prefs.mainWindowRect is not None and not self.app.prefs.mainWindowIsMaximized:
            self.setGeometry(self.app.prefs.mainWindowRect)
        
        # Platform-specific setup
        if sys.platform == 'linux2':
            self.actionCheckForUpdate.setVisible(False) # This only works on Windows
        if sys.platform not in {'darwin', 'linux2'}:
            self.actionHardlinkMarked.setVisible(False)
    
    #--- Private
    def _confirm(self, title, msg, default_button=QMessageBox.Yes):
        buttons = QMessageBox.Yes | QMessageBox.No
        answer = QMessageBox.question(self, title, msg, buttons, default_button)
        return answer == QMessageBox.Yes
    
    def _load_columns(self):
        h = self.resultsView.horizontalHeader()
        h.setResizeMode(QHeaderView.Interactive)
        prefs = self.app.prefs
        attrs = list(zip(prefs.columns_width, prefs.columns_visible))
        for index, (width, visible) in enumerate(attrs):
            h.resizeSection(index, width)
            h.setSectionHidden(index, not visible)
        h.setResizeMode(0, QHeaderView.Stretch)
    
    def _update_column_actions_status(self):
        h = self.resultsView.horizontalHeader()
        for action in self._column_actions:
            colid = action.column_index
            action.setChecked(not h.isSectionHidden(colid))
    
    #--- QWidget overrides
    def closeEvent(self, event):
        event.accept()
        if self.app.results.is_modified:
            title = "Unsaved results"
            msg = "You have unsaved results, do you really want to quit?"
            if not self._confirm(title, msg):
                event.ignore()
    
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
        h = self.resultsView.horizontalHeader()
        column_ids = []
        for i in range(len(self.app.data.COLUMNS)):
            if not h.isSectionHidden(i):
                column_ids.append(str(i))
        exported_path = self.app.export_to_xhtml(column_ids)
        url = QUrl.fromLocalFile(exported_path)
        QDesktopServices.openUrl(url)
    
    def hardlinkTriggered(self):
        count = self.app.results.mark_count
        if not count:
            return
        title = "Delete and hardlink duplicates"
        msg = "You are about to send {0} files to the trash and hardlink them afterwards. Continue?".format(count)
        if self._confirm(title, msg):
            self.app.delete_marked(replace_with_hardlinks=True)
    
    def loadResultsTriggered(self):
        title = "Select a results file to load"
        files = "dupeGuru Results (*.dupeguru)"
        destination = QFileDialog.getOpenFileName(self, title, '', files)
        if destination:
            self.app.load_from(destination)
            self.recentResults.insertItem(destination)
    
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
        self.app.reg.ask_for_code()
    
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
            self.recentResults.insertItem(destination)
    
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
    
    def showHelpTriggered(self):
        self.app.show_help()
    
    #--- Events
    def appWillSavePrefs(self):
        prefs = self.app.prefs
        h = self.resultsView.horizontalHeader()
        widths = []
        visible = []
        for i in range(len(self.app.data.COLUMNS)):
            widths.append(h.sectionSize(i))
            visible.append(not h.isSectionHidden(i))
        prefs.columns_width = widths
        prefs.columns_visible = visible
        prefs.mainWindowIsMaximized = self.isMaximized()
        prefs.mainWindowRect = self.geometry()
    
    def columnToggled(self, action):
        colid = action.column_index
        if colid == -1:
            self.app.prefs.reset_columns()
            self._load_columns()
        else:
            h = self.resultsView.horizontalHeader()
            h.setSectionHidden(colid, not h.isSectionHidden(colid))
        self._update_column_actions_status()
    
    def contextMenuEvent(self, event):
        self.actionActions.menu().exec_(event.globalPos())
    
    def resultsDoubleClicked(self):
        self.app.open_selected()
    
    def resultsSpacePressed(self):
        self.app.toggle_selected_mark_state()
    
