# Created By: Virgil Dupras
# Created On: 2009-04-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import QModelIndex, Qt, QRect, QEvent, QPoint
from PyQt4.QtGui import QComboBox, QStyledItemDelegate, QMouseEvent, QApplication, QBrush

from qtlib.tree_model import TreeNode, TreeModel

HEADERS = ['Name', 'State']
STATES = ['Normal', 'Reference', 'Excluded']

class DirectoriesDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent);
        editor.addItems(STATES)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setCurrentIndex(value);
        press = QMouseEvent(QEvent.MouseButtonPress, QPoint(0, 0), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        release = QMouseEvent(QEvent.MouseButtonRelease, QPoint(0, 0), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(editor, press)
        QApplication.sendEvent(editor, release)
        # editor.showPopup() # this causes a weird glitch. the ugly workaround is above.
    
    def setModelData(self, editor, model, index):
        value = editor.currentIndex()
        model.setData(index, value, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    

class DirectoryNode(TreeNode):
    def __init__(self, model, parent, ref, row):
        TreeNode.__init__(self, model, parent, row)
        self.ref = ref
    
    def _createNode(self, ref, row):
        return DirectoryNode(self.model, self, ref, row)
    
    def _getChildren(self):
        return self.model._dirs.get_subfolders(self.ref)
    
    @property
    def name(self):
        if self.parent is not None:
            return self.ref[-1]
        else:
            return unicode(self.ref)
    

class DirectoriesModel(TreeModel):
    def __init__(self, app):
        self._dirs = app.directories
        TreeModel.__init__(self)
    
    def _createNode(self, ref, row):
        return DirectoryNode(self, None, ref, row)
    
    def _getChildren(self):
        return self._dirs
    
    def columnCount(self, parent):
        return 2
    
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return node.name
            else:
                return STATES[self._dirs.get_state(node.ref)]
        elif role == Qt.EditRole and index.column() == 1:
            return self._dirs.get_state(node.ref)
        elif role == Qt.ForegroundRole:
            state = self._dirs.get_state(node.ref)
            if state == 1:
                return QBrush(Qt.blue)
            elif state == 2:
                return QBrush(Qt.red)
        return None
    
    def flags(self, index):
        if not index.isValid():
            return 0
        result = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 1:
            result |= Qt.ItemIsEditable
        return result
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole and section < len(HEADERS):
                return HEADERS[section]
        return None
    
    def setData(self, index, value, role):
        if not index.isValid() or role != Qt.EditRole or index.column() != 1:
            return False
        node = index.internalPointer()
        self._dirs.set_state(node.ref, value)
        return True
    
