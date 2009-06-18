#!/usr/bin/env python
# Unit Name: directories_model
# Created By: Virgil Dupras
# Created On: 2009-04-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from PyQt4.QtCore import QVariant, QModelIndex, Qt, QRect, QEvent, QPoint
from PyQt4.QtGui import QComboBox, QStyledItemDelegate, QMouseEvent, QApplication, QBrush

from tree_model import TreeNode, TreeModel

HEADERS = ['Name', 'State']
STATES = ['Normal', 'Reference', 'Excluded']

class DirectoriesDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent);
        editor.addItems(STATES)
        return editor
    
    def setEditorData(self, editor, index):
        value, ok = index.model().data(index, Qt.EditRole).toInt()
        assert ok
        editor.setCurrentIndex(value);
        press = QMouseEvent(QEvent.MouseButtonPress, QPoint(0, 0), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        release = QMouseEvent(QEvent.MouseButtonRelease, QPoint(0, 0), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(editor, press)
        QApplication.sendEvent(editor, release)
        # editor.showPopup() # this causes a weird glitch. the ugly workaround is above.
    
    def setModelData(self, editor, model, index):
        value = QVariant(editor.currentIndex())
        model.setData(index, value, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    

class DirectoryNode(TreeNode):
    def __init__(self, parent, ref, row):
        TreeNode.__init__(self, parent, row)
        self.ref = ref
    
    def _get_children(self):
        children = []
        for index, directory in enumerate(self.ref.dirs):
            node = DirectoryNode(self, directory, index)
            children.append(node)
        return children
    

class DirectoriesModel(TreeModel):
    def __init__(self, app):
        self._dirs = app.directories
        TreeModel.__init__(self)
    
    def _root_nodes(self):
        nodes = []
        for index, directory in enumerate(self._dirs):
            nodes.append(DirectoryNode(None, directory, index))
        return nodes
    
    def columnCount(self, parent):
        return 2
    
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return QVariant(node.ref.name)
            else:
                return QVariant(STATES[self._dirs.get_state(node.ref.path)])
        elif role == Qt.EditRole and index.column() == 1:
            return QVariant(self._dirs.get_state(node.ref.path))
        elif role == Qt.ForegroundRole:
            state = self._dirs.get_state(node.ref.path)
            if state == 1:
                return QVariant(QBrush(Qt.blue))
            elif state == 2:
                return QVariant(QBrush(Qt.red))
        return QVariant()
    
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
                return QVariant(HEADERS[section])
        return QVariant()
    
    def setData(self, index, value, role):
        if not index.isValid() or role != Qt.EditRole or index.column() != 1:
            return False
        node = index.internalPointer()
        state, ok = value.toInt()
        assert ok
        self._dirs.set_state(node.ref.path, state)
        return True
    
