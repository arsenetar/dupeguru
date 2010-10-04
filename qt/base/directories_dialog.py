# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import SIGNAL, Qt, QSize
from PyQt4.QtGui import (QDialog, QFileDialog, QHeaderView, QVBoxLayout, QHBoxLayout, QTreeView,
    QAbstractItemView, QSpacerItem, QSizePolicy, QPushButton, QApplication)

from . import platform
from .directories_model import DirectoriesModel, DirectoriesDelegate

class DirectoriesDialog(QDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.app = app
        self.lastAddedFolder = platform.INITIAL_FOLDER_IN_DIALOGS
        self.directoriesModel = DirectoriesModel(self.app)
        self.directoriesDelegate = DirectoriesDelegate()
        self._setupUi()
        self._updateRemoveButton()
        
        self.connect(self.doneButton, SIGNAL('clicked()'), self.doneButtonClicked)
        self.connect(self.addButton, SIGNAL('clicked()'), self.addButtonClicked)
        self.connect(self.removeButton, SIGNAL('clicked()'), self.removeButtonClicked)
        self.connect(self.treeView.selectionModel(), SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged)
        self.app.willSavePrefs.connect(self.appWillSavePrefs)
    
    def _setupUi(self):
        self.setWindowTitle("Directories")
        self.resize(420, 338)
        self.verticalLayout = QVBoxLayout(self)
        self.treeView = QTreeView(self)
        self.treeView.setItemDelegate(self.directoriesDelegate)
        self.treeView.setModel(self.directoriesModel)
        self.treeView.setAcceptDrops(True)
        self.treeView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
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
        self.removeButton = QPushButton(self)
        self.removeButton.setText("Remove")
        self.removeButton.setShortcut("Del")
        self.removeButton.setMinimumSize(QSize(91, 0))
        self.removeButton.setMaximumSize(QSize(16777215, 32))
        self.horizontalLayout.addWidget(self.removeButton)
        self.addButton = QPushButton(self)
        self.addButton.setText("Add")
        self.addButton.setMinimumSize(QSize(91, 0))
        self.addButton.setMaximumSize(QSize(16777215, 32))
        self.horizontalLayout.addWidget(self.addButton)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.doneButton = QPushButton(self)
        self.doneButton.setText("Done")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doneButton.sizePolicy().hasHeightForWidth())
        self.doneButton.setSizePolicy(sizePolicy)
        self.doneButton.setMinimumSize(QSize(91, 0))
        self.doneButton.setMaximumSize(QSize(16777215, 32))
        self.doneButton.setDefault(True)
        self.horizontalLayout.addWidget(self.doneButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
                
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
    
    def doneButtonClicked(self):
        self.hide()
    
    def removeButtonClicked(self):
        indexes = self.treeView.selectedIndexes()
        if not indexes:
            return
        index = indexes[0]
        node = index.internalPointer()
        if node.parent is None:
            row = index.row()
            self.app.remove_directory(row)
    
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