# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QCoreApplication, QProcess, SIGNAL, QUrl
from PyQt4.QtGui import (QMainWindow, QMenu, QPixmap, QIcon, QToolButton, QLabel, QHeaderView,
    QMessageBox, QInputDialog, QLineEdit, QItemSelectionModel, QDesktopServices)

from hsutil.misc import nonone

from core.app import NoScannableFileError, AllFilesAreRefError

import dg_rc
from main_window_ui import Ui_MainWindow
from results_model import ResultsDelegate, ResultsModel

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app):
        QMainWindow.__init__(self, None)
        self.app = app
        self._last_filter = None
        self._setupUi()
        self.resultsDelegate = ResultsDelegate() 
        self.resultsModel = ResultsModel(self.app) 
        self.resultsView.setModel(self.resultsModel) 
        self.resultsView.setItemDelegate(self.resultsDelegate) 
        self._load_columns()
        self._update_column_actions_status()
        self.resultsView.expandAll()
        self._update_status_line()
        
        self.connect(self.app, SIGNAL('resultsChanged()'), self.resultsChanged)
        self.connect(self.app, SIGNAL('dupeMarkingChanged()'), self.dupeMarkingChanged)
        self.connect(self.actionQuit, SIGNAL('triggered()'), QCoreApplication.instance().quit)
        self.connect(self.resultsView.selectionModel(), SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged)
        self.connect(self.menuColumns, SIGNAL('triggered(QAction*)'), self.columnToggled)
        self.connect(QCoreApplication.instance(), SIGNAL('aboutToQuit()'), self.application_will_terminate)
        self.connect(self.resultsModel, SIGNAL('modelReset()'), self.resultsReset)
        self.connect(self.resultsView, SIGNAL('doubleClicked()'), self.resultsDoubleClicked)
    
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
    
    #--- Private
    def _confirm(self, title, msg, default_button=QMessageBox.Yes):
        buttons = QMessageBox.Yes | QMessageBox.No
        answer = QMessageBox.question(self, title, msg, buttons, default_button)
        return answer == QMessageBox.Yes
    
    def _load_columns(self):
        h = self.resultsView.header()
        h.setResizeMode(QHeaderView.Interactive)
        prefs = self.app.prefs
        attrs = zip(prefs.columns_width, prefs.columns_visible)
        for index, (width, visible) in enumerate(attrs):
            h.resizeSection(index, width)
            h.setSectionHidden(index, not visible)
        h.setResizeMode(0, QHeaderView.Stretch)
    
    def _redraw_results(self):
        # HACK. this is the only way I found to update the widget without reseting everything
        self.resultsView.scroll(0, 1)
        self.resultsView.scroll(0, -1)
    
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
    
    def _update_status_line(self):
        self.statusLabel.setText(self.app.stat_line)
    
    #--- Actions
    def aboutTriggered(self):
        self.app.show_about_box()
    
    def actionsTriggered(self):
        self.actionsButton.showMenu()
    
    def addToIgnoreListTriggered(self):
        dupes = self.resultsView.selectedDupes()
        if not dupes:
            return
        title = "Add to Ignore List"
        msg = "All selected {0} matches are going to be ignored in all subsequent scans. Continue?".format(len(dupes))
        if self._confirm(title, msg):
            self.app.add_dupes_to_ignore_list(dupes)
    
    def applyFilterTriggered(self):
        title = "Apply Filter"
        msg = "Type the filter you want to apply on your results. See help for details."
        text = nonone(self._last_filter, '[*]')
        answer, ok = QInputDialog.getText(self, title, msg, QLineEdit.Normal, text)
        if not ok:
            return
        answer = unicode(answer)
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
        self.resultsModel.delta = self.actionDelta.isChecked()
        self._redraw_results()
    
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
    
    def makeReferenceTriggered(self):
        self.app.make_reference(self.resultsView.selectedDupes())
    
    def markAllTriggered(self):
        self.app.mark_all()
    
    def markInvertTriggered(self):
        self.app.mark_invert()
    
    def markNoneTriggered(self):
        self.app.mark_none()
    
    def markSelectedTriggered(self):
        dupes = self.resultsView.selectedDupes()
        self.app.toggle_marking_for_dupes(dupes)
    
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
            self.app.remove_marked_duplicates()
    
    def removeSelectedTriggered(self):
        dupes = self.resultsView.selectedDupes()
        if not dupes:
            return
        title = "Remove duplicates"
        msg = "You are about to remove {0} files from results. Continue?".format(len(dupes))
        if self._confirm(title, msg):
            self.app.remove_duplicates(dupes)
    
    def renameTriggered(self):
        self.resultsView.edit(self.resultsView.selectionModel().currentIndex())
    
    def revealTriggered(self):
        self.app.reveal_selected()
    
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
    
    def dupeMarkingChanged(self):
        self._redraw_results()
        self._update_status_line()
    
    def resultsChanged(self):
        self.resultsView.model().reset()
    
    def resultsDoubleClicked(self):
        self.app.open_selected()
    
    def resultsReset(self):
        self.resultsView.expandAll()
        dupe = self.app.selected_dupe
        if dupe is not None:
            [modelIndex] = self.resultsModel.indexesForDupes([dupe])
            if modelIndex.isValid():
                flags = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
                self.resultsView.selectionModel().setCurrentIndex(modelIndex, flags)
        self._update_status_line()
    
    def selectionChanged(self, selected, deselected):
        index = self.resultsView.selectionModel().currentIndex()
        dupe = index.internalPointer().dupe if index.isValid() else None
        self.app.select_duplicate(dupe)
    
