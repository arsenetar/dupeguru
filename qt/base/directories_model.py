# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import urllib

from PyQt4.QtCore import QModelIndex, Qt, QRect, QEvent, QPoint, QUrl
from PyQt4.QtGui import (QComboBox, QStyledItemDelegate, QMouseEvent, QApplication, QBrush, QStyle,
    QStyleOptionComboBox, QStyleOptionViewItemV4)

from qtlib.tree_model import TreeNode, TreeModel

HEADERS = ['Name', 'State']
STATES = ['Normal', 'Reference', 'Excluded']

class DirectoriesDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent);
        editor.addItems(STATES)
        return editor
    
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        # No idea why, but this cast is required if we want to have access to the V4 valuess
        option = QStyleOptionViewItemV4(option)
        if (index.column() == 1) and (option.state & QStyle.State_Selected):
            cboption = QStyleOptionComboBox()
            cboption.rect = option.rect
            # On OS X (with Qt4.6.0), adding State_Enabled to the flags causes the whole drawing to
            # fail (draw nothing), but it's an OS X only glitch. On Windows, it works alright.
            cboption.state |= QStyle.State_Enabled
            QApplication.style().drawComplexControl(QStyle.CC_ComboBox, cboption, painter)
            painter.setBrush(option.palette.text())
            rect = QRect(option.rect)
            rect.setLeft(rect.left()+4)
            painter.drawText(rect, Qt.AlignLeft, option.text)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
    
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
        return self.model.dirs.get_subfolders(self.ref)
    
    @property
    def name(self):
        if self.parent is not None:
            return self.ref[-1]
        else:
            return unicode(self.ref)
    

class DirectoriesModel(TreeModel):
    def __init__(self, app):
        self.app = app
        self.dirs = app.directories
        TreeModel.__init__(self)
    
    def _createNode(self, ref, row):
        return DirectoryNode(self, None, ref, row)
    
    def _getChildren(self):
        return self.dirs
    
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
                return STATES[self.dirs.get_state(node.ref)]
        elif role == Qt.EditRole and index.column() == 1:
            return self.dirs.get_state(node.ref)
        elif role == Qt.ForegroundRole:
            state = self.dirs.get_state(node.ref)
            if state == 1:
                return QBrush(Qt.blue)
            elif state == 2:
                return QBrush(Qt.red)
        return None
    
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        # the data in mimeData is urlencoded **in utf-8**!!! which means that urllib.unquote has
        # to be called on the utf-8 encoded string, and *only then*, decoded to unicode.
        if not mimeData.hasFormat('text/uri-list'):
            return False
        data = str(mimeData.data('text/uri-list'))
        unquoted = urllib.unquote(data)
        urls = unicode(unquoted, 'utf-8').split('\r\n')
        paths = [unicode(QUrl(url).toLocalFile()) for url in urls if url]
        for path in paths:
            self.app.add_directory(path)
        self.reset()
        return True
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        result = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
        if index.column() == 1:
            result |= Qt.ItemIsEditable
        return result
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole and section < len(HEADERS):
                return HEADERS[section]
        return None
    
    def mimeTypes(self):
        return ['text/uri-list']
    
    def setData(self, index, value, role):
        if not index.isValid() or role != Qt.EditRole or index.column() != 1:
            return False
        node = index.internalPointer()
        self.dirs.set_state(node.ref, value)
        return True
    
    def supportedDropActions(self):
        # Normally, the correct action should be ActionLink, but the drop doesn't work. It doesn't
        # work with ActionMove either. So screw that, and accept anything.
        return Qt.ActionMask
    
