# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import (QWidget, QFileDialog, QHeaderView, QVBoxLayout, QHBoxLayout, QTreeView,
    QAbstractItemView, QSpacerItem, QSizePolicy, QPushButton, QMainWindow, QMenuBar, QMenu, QLabel,
    QApplication)
from PyQt5.QtGui import QPixmap, QIcon

from hscommon.trans import trget
from qtlib.recent import Recent
from qtlib.util import moveToScreenCenter, createActions

from . import platform
from .directories_model import DirectoriesModel, DirectoriesDelegate

tr = trget('ui')

class DirectoriesDialog(QMainWindow):
    def __init__(self, parent, app):
        QMainWindow.__init__(self, None)
        self.app = app
        self.lastAddedFolder = platform.INITIAL_FOLDER_IN_DIALOGS
        self.recentFolders = Recent(self.app, 'recentFolders')
        self._setupUi()
        self.directoriesModel = DirectoriesModel(self.app.model.directory_tree, view=self.treeView)
        self.directoriesDelegate = DirectoriesDelegate()
        self.treeView.setItemDelegate(self.directoriesDelegate)
        self._setupColumns()
        self.app.recentResults.addMenu(self.menuLoadRecent)
        self.app.recentResults.addMenu(self.menuRecentResults)
        self.recentFolders.addMenu(self.menuRecentFolders)
        self._updateAddButton()
        self._updateRemoveButton()
        self._updateLoadResultsButton()
        self._setupBindings()
    
    def _setupBindings(self):
        self.scanButton.clicked.connect(self.scanButtonClicked)
        self.loadResultsButton.clicked.connect(self.actionLoadResults.trigger)
        self.addFolderButton.clicked.connect(self.actionAddFolder.trigger)
        self.removeFolderButton.clicked.connect(self.removeFolderButtonClicked)
        self.treeView.selectionModel().selectionChanged.connect(self.selectionChanged)
        self.app.recentResults.itemsChanged.connect(self._updateLoadResultsButton)
        self.recentFolders.itemsChanged.connect(self._updateAddButton)
        self.recentFolders.mustOpenItem.connect(self.app.model.add_directory)
        self.directoriesModel.foldersAdded.connect(self.directoriesModelAddedFolders)
        self.app.willSavePrefs.connect(self.appWillSavePrefs)
        
    def _setupActions(self):
        # (name, shortcut, icon, desc, func)
        ACTIONS = [
            ('actionLoadResults', 'Ctrl+L', '', tr("Load Results..."), self.loadResultsTriggered),
            ('actionShowResultsWindow', '', '', tr("Results Window"), self.app.showResultsWindow),
            ('actionAddFolder', '', '', tr("Add Folder..."), self.addFolderTriggered),
        ]
        createActions(ACTIONS, self)
    
    def _setupMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 42, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setTitle(tr("File"))
        self.menuView = QMenu(self.menubar)
        self.menuView.setTitle(tr("View"))
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setTitle(tr("Help"))
        self.menuLoadRecent = QMenu(self.menuFile)
        self.menuLoadRecent.setTitle(tr("Load Recent Results"))
        self.setMenuBar(self.menubar)
        
        self.menuFile.addAction(self.actionLoadResults)
        self.menuFile.addAction(self.menuLoadRecent.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.app.actionQuit)
        self.menuView.addAction(self.app.actionPreferences)
        self.menuView.addAction(self.actionShowResultsWindow)
        self.menuView.addAction(self.app.actionIgnoreList)
        self.menuHelp.addAction(self.app.actionShowHelp)
        self.menuHelp.addAction(self.app.actionRegister)
        self.menuHelp.addAction(self.app.actionCheckForUpdate)
        self.menuHelp.addAction(self.app.actionOpenDebugLog)
        self.menuHelp.addAction(self.app.actionAbout)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
        # Recent folders menu
        self.menuRecentFolders = QMenu()
        self.menuRecentFolders.addAction(self.actionAddFolder)
        self.menuRecentFolders.addSeparator()
        
        # Recent results menu
        self.menuRecentResults = QMenu()
        self.menuRecentResults.addAction(self.actionLoadResults)
        self.menuRecentResults.addSeparator()
    
    def _setupUi(self):
        self.setWindowTitle(self.app.NAME)
        self.resize(420, 338)
        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.promptLabel = QLabel(tr("Select folders to scan and press \"Scan\"."), self.centralwidget)
        self.verticalLayout.addWidget(self.promptLabel)
        self.treeView = QTreeView(self.centralwidget)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treeView.setAcceptDrops(True)
        triggers = QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed\
            |QAbstractItemView.SelectedClicked
        self.treeView.setEditTriggers(triggers)
        self.treeView.setDragDropOverwriteMode(True)
        self.treeView.setDragDropMode(QAbstractItemView.DropOnly)
        self.treeView.setUniformRowHeights(True)
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout = QHBoxLayout()
        self.removeFolderButton = QPushButton(self.centralwidget)
        self.removeFolderButton.setIcon(QIcon(QPixmap(":/minus")))
        self.removeFolderButton.setShortcut("Del")
        self.horizontalLayout.addWidget(self.removeFolderButton)
        self.addFolderButton = QPushButton(self.centralwidget)
        self.addFolderButton.setIcon(QIcon(QPixmap(":/plus")))
        self.horizontalLayout.addWidget(self.addFolderButton)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.loadResultsButton = QPushButton(self.centralwidget)
        self.loadResultsButton.setText(tr("Load Results"))
        self.horizontalLayout.addWidget(self.loadResultsButton)
        self.scanButton = QPushButton(self.centralwidget)
        self.scanButton.setText(tr("Scan"))
        self.scanButton.setDefault(True)
        self.horizontalLayout.addWidget(self.scanButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)
        
        self._setupActions()
        self._setupMenu()
        
        if self.app.prefs.directoriesWindowRect is not None:
            self.setGeometry(self.app.prefs.directoriesWindowRect)
        else:
            moveToScreenCenter(self)
    
    def _setupColumns(self):
        header = self.treeView.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 100)
    
    def _updateAddButton(self):
        if self.recentFolders.isEmpty():
            self.addFolderButton.setMenu(None)
        else:
            self.addFolderButton.setMenu(self.menuRecentFolders)
    
    def _updateRemoveButton(self):
        indexes = self.treeView.selectedIndexes()
        if not indexes:
            self.removeFolderButton.setEnabled(False)
            return
        self.removeFolderButton.setEnabled(True)
    
    def _updateLoadResultsButton(self):
        if self.app.recentResults.isEmpty():
            self.loadResultsButton.setMenu(None)
        else:
            self.loadResultsButton.setMenu(self.menuRecentResults)
    
    #--- QWidget overrides
    def closeEvent(self, event):
        event.accept()
        if self.app.model.results.is_modified:
            title = tr("Unsaved results")
            msg = tr("You have unsaved results, do you really want to quit?")
            if not self.app.confirm(title, msg):
                event.ignore()
        if event.isAccepted():
            QApplication.quit()
    
    #--- Events
    def addFolderTriggered(self):
        title = tr("Select a folder to add to the scanning list")
        flags = QFileDialog.ShowDirsOnly
        dirpath = str(QFileDialog.getExistingDirectory(self, title, self.lastAddedFolder, flags))
        if not dirpath:
            return
        self.lastAddedFolder = dirpath
        self.app.model.add_directory(dirpath)
        self.recentFolders.insertItem(dirpath)
    
    def appWillSavePrefs(self):
        self.app.prefs.directoriesWindowRect = self.geometry()
    
    def directoriesModelAddedFolders(self, folders):
        for folder in folders:
            self.recentFolders.insertItem(folder)
    
    def loadResultsTriggered(self):
        title = tr("Select a results file to load")
        files = ';;'.join([tr("dupeGuru Results (*.dupeguru)"), tr("All Files (*.*)")])
        destination = QFileDialog.getOpenFileName(self, title, '', files)
        if destination:
            self.app.model.load_from(destination)
            self.app.recentResults.insertItem(destination)
    
    def removeFolderButtonClicked(self):
        self.directoriesModel.model.remove_selected()
    
    def scanButtonClicked(self):
        if self.app.model.results.is_modified:
            title = tr("Start a new scan")
            msg = tr("You have unsaved results, do you really want to continue?")
            if not self.app.confirm(title, msg):
                return
        self.app.model.start_scanning()
    
    def selectionChanged(self, selected, deselected):
        self._updateRemoveButton()
    

if __name__ == '__main__':
    import sys
    from . import dg_rc
    from ..testapp import TestApp
    app = QApplication([])
    dgapp = TestApp()
    dialog = DirectoriesDialog(None, dgapp)
    dialog.show()
    sys.exit(app.exec_())