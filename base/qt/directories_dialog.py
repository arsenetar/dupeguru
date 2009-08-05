# Created By: Virgil Dupras
# Created On: 2009-04-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QDialog, QFileDialog, QHeaderView

from directories_dialog_ui import Ui_DirectoriesDialog
from directories_model import DirectoriesModel, DirectoriesDelegate

class DirectoriesDialog(QDialog, Ui_DirectoriesDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.app = app
        self._setupUi()
        self._updateRemoveButton()
        
        self.connect(self.doneButton, SIGNAL('clicked()'), self.doneButtonClicked)
        self.connect(self.addButton, SIGNAL('clicked()'), self.addButtonClicked)
        self.connect(self.removeButton, SIGNAL('clicked()'), self.removeButtonClicked)
        self.connect(self.treeView.selectionModel(), SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged)
        self.connect(self.app, SIGNAL('directoriesChanged()'), self.directoriesChanged)
    
    def _setupUi(self):
        self.setupUi(self)
        # Stuff that can't be done in the Designer
        self.directoriesModel = DirectoriesModel(self.app)
        self.directoriesDelegate = DirectoriesDelegate()
        self.treeView.setItemDelegate(self.directoriesDelegate)
        self.treeView.setModel(self.directoriesModel)
        
        header = self.treeView.header()
        header.setStretchLastSection(False)
        header.setResizeMode(0, QHeaderView.Stretch)
        header.setResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 100)
    
    def _updateRemoveButton(self):
        indexes = self.treeView.selectedIndexes()
        if not indexes:
            self.removeButton.setEnabled(False)
            return
        self.removeButton.setEnabled(True)
        index = indexes[0]
        node = index.internalPointer()
        # label = 'Remove' if node.parent is None else 'Exclude'
    
    def addButtonClicked(self):
        title = u"Select a directory to add to the scanning list"
        flags = QFileDialog.ShowDirsOnly
        dirpath = unicode(QFileDialog.getExistingDirectory(self, title, '', flags))
        if not dirpath:
            return
        self.app.add_directory(dirpath)
        self.directoriesModel.reset()
    
    def directoriesChanged(self):
        self.directoriesModel.reset()
    
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
            del self.app.directories[row]
            self.directoriesModel.reset()
    
    def selectionChanged(self, selected, deselected):
        self._updateRemoveButton()
    
