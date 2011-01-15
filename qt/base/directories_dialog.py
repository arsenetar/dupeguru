# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QSize, QRect
from PyQt4.QtGui import (QWidget, QFileDialog, QHeaderView, QVBoxLayout, QHBoxLayout, QTreeView,
    QAbstractItemView, QSpacerItem, QSizePolicy, QPushButton, QApplication, QMessageBox, QMainWindow,
    QMenuBar, QMenu)

from core.app import NoScannableFileError

from . import platform
from .directories_model import DirectoriesModel, DirectoriesDelegate
from .util import createActions

class DirectoriesDialog(QMainWindow):
    def __init__(self, parent, app):
        QMainWindow.__init__(self, None)
        self.app = app
        self.lastAddedFolder = platform.INITIAL_FOLDER_IN_DIALOGS
        self.directoriesModel = DirectoriesModel(self.app)
        self.directoriesDelegate = DirectoriesDelegate()
        self._setupUi()
        self._updateRemoveButton()
        
        self.scanButton.clicked.connect(self.scanButtonClicked)
        self.addButton.clicked.connect(self.addButtonClicked)
        self.removeButton.clicked.connect(self.removeButtonClicked)
        self.treeView.selectionModel().selectionChanged.connect(self.selectionChanged)
        self.app.willSavePrefs.connect(self.appWillSavePrefs)
    
    def _setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            ('actionLoadResults', 'Ctrl+L', '', "Load Results...", self.loadResultsTriggered),
            ('actionShowResultsWindow', '', '', "Results Window", self.app.showResultsWindow),
        ]
        createActions(ACTIONS, self)
    
    def _setupMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 42, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setTitle("File")
        self.menuView = QMenu(self.menubar)
        self.menuView.setTitle("View")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setTitle("Help")
        self.menuLoadRecent = QMenu(self.menuFile)
        self.menuLoadRecent.setTitle("Load Recent Results")
        self.setMenuBar(self.menubar)
        
        self.menuFile.addAction(self.actionLoadResults)
        self.menuFile.addAction(self.menuLoadRecent.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.app.actionQuit)
        self.menuView.addAction(self.app.actionPreferences)
        self.menuView.addAction(self.actionShowResultsWindow)
        self.menuHelp.addAction(self.app.actionShowHelp)
        self.menuHelp.addAction(self.app.actionRegister)
        self.menuHelp.addAction(self.app.actionCheckForUpdate)
        self.menuHelp.addAction(self.app.actionOpenDebugLog)
        self.menuHelp.addAction(self.app.actionAbout)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
    
    def _setupUi(self):
        self.setWindowTitle(self.app.NAME)
        self.resize(420, 338)
        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.treeView = QTreeView(self.centralwidget)
        self.treeView.setItemDelegate(self.directoriesDelegate)
        self.treeView.setModel(self.directoriesModel)
        self.treeView.setAcceptDrops(True)
        triggers = QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed\
            |QAbstractItemView.SelectedClicked
        self.treeView.setEditTriggers(triggers)
        self.treeView.setDragDropOverwriteMode(True)
        self.treeView.setDragDropMode(QAbstractItemView.DropOnly)
        self.treeView.setUniformRowHeights(True)
        header = self.treeView.header()
        header.setStretchLastSection(False)
        header.setResizeMode(0, QHeaderView.Stretch)
        header.setResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 100)
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.removeButton = QPushButton(self.centralwidget)
        self.removeButton.setText("Remove")
        self.removeButton.setShortcut("Del")
        self.removeButton.setMinimumSize(QSize(91, 0))
        self.removeButton.setMaximumSize(QSize(16777215, 32))
        self.horizontalLayout.addWidget(self.removeButton)
        self.addButton = QPushButton(self.centralwidget)
        self.addButton.setText("Add")
        self.addButton.setMinimumSize(QSize(91, 0))
        self.addButton.setMaximumSize(QSize(16777215, 32))
        self.horizontalLayout.addWidget(self.addButton)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.scanButton = QPushButton(self.centralwidget)
        self.scanButton.setText("Scan")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scanButton.sizePolicy().hasHeightForWidth())
        self.scanButton.setSizePolicy(sizePolicy)
        self.scanButton.setMinimumSize(QSize(91, 0))
        self.scanButton.setMaximumSize(QSize(16777215, 32))
        self.scanButton.setDefault(True)
        self.horizontalLayout.addWidget(self.scanButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)
        
        self._setupActions()
        self._setupMenu()
                
        if self.app.prefs.directoriesWindowRect is not None:
            self.setGeometry(self.app.prefs.directoriesWindowRect)
    
    def _updateRemoveButton(self):
        indexes = self.treeView.selectedIndexes()
        if not indexes:
            self.removeButton.setEnabled(False)
            return
        self.removeButton.setEnabled(True)
        index = indexes[0]
        node = index.internalPointer()
        # label = 'Remove' if node.parent is None else 'Exclude'
    
    #--- QWidget overrides
    def closeEvent(self, event):
        event.accept()
        if self.app.results.is_modified:
            title = "Unsaved results"
            msg = "You have unsaved results, do you really want to quit?"
            if not self.app.confirm(title, msg):
                event.ignore()
        if event.isAccepted():
            QApplication.quit()
    
    #--- Events
    def addButtonClicked(self):
        title = "Select a directory to add to the scanning list"
        flags = QFileDialog.ShowDirsOnly
        dirpath = str(QFileDialog.getExistingDirectory(self, title, self.lastAddedFolder, flags))
        if not dirpath:
            return
        self.lastAddedFolder = dirpath
        self.app.add_directory(dirpath)
    
    def appWillSavePrefs(self):
        self.app.prefs.directoriesWindowRect = self.geometry()
    
    def loadResultsTriggered(self):
        title = "Select a results file to load"
        files = "dupeGuru Results (*.dupeguru)"
        destination = QFileDialog.getOpenFileName(self, title, '', files)
        if destination:
            self.app.load_from(destination)
            self.app.recentResults.insertItem(destination)
    
    def removeButtonClicked(self):
        indexes = self.treeView.selectedIndexes()
        if not indexes:
            return
        index = indexes[0]
        node = index.internalPointer()
        if node.parent is None:
            row = index.row()
            self.app.remove_directory(row)
    
    def scanButtonClicked(self):
        title = "Start a new scan"
        if len(self.app.results.groups) > 0:
            msg = "Are you sure you want to start a new duplicate scan?"
            if not self.app.confirm(title, msg):
                return
        try:
            self.app.start_scanning()
        except NoScannableFileError:
            msg = "The selected directories contain no scannable file."
            QMessageBox.warning(self, title, msg)
    
    def selectionChanged(self, selected, deselected):
        self._updateRemoveButton()
    

if __name__ == '__main__':
    import sys
    from ..testapp import TestApp
    app = QApplication([])
    dgapp = TestApp()
    dialog = DirectoriesDialog(None, dgapp)
    dialog.show()
    sys.exit(app.exec_())