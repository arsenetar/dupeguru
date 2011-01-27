# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import urllib.parse

from PyQt4.QtCore import pyqtSignal, Qt, QRect, QEvent, QPoint, QUrl
from PyQt4.QtGui import (QComboBox, QStyledItemDelegate, QMouseEvent, QApplication, QBrush, QStyle,
    QStyleOptionComboBox, QStyleOptionViewItemV4)

from hscommon.trans import tr
from qtlib.tree_model import RefNode, TreeModel

from core.gui.directory_tree import DirectoryTree

HEADERS = [tr("Name"), tr("State")]
STATES = [tr("Normal"), tr("Reference"), tr("Excluded")]

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
    

class DirectoriesModel(TreeModel):
    def __init__(self, app):
        TreeModel.__init__(self)
        self.model = DirectoryTree(self, app)
        self.model.connect()
    
    def _createNode(self, ref, row):
        return RefNode(self, None, ref, row)
    
    def _getChildren(self):
        return list(self.model)
    
    def columnCount(self, parent):
        return 2
    
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        ref = node.ref
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return ref.name
            else:
                return STATES[ref.state]
        elif role == Qt.EditRole and index.column() == 1:
            return ref.state
        elif role == Qt.ForegroundRole:
            state = ref.state
            if state == 1:
                return QBrush(Qt.blue)
            elif state == 2:
                return QBrush(Qt.red)
        return None
    
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        # the data in mimeData is urlencoded **in utf-8**!!! What we do is to decode, the mime data
        # with 'ascii', which works since it's urlencoded. Then, we pass that to urllib.
        if not mimeData.hasFormat('text/uri-list'):
            return False
        data = bytes(mimeData.data('text/uri-list')).decode('ascii')
        unquoted = urllib.parse.unquote(data)
        urls = unquoted.split('\r\n')
        paths = [str(QUrl(url).toLocalFile()) for url in urls if url]
        for path in paths:
            self.model.add_directory(path)
        self.foldersAdded.emit(paths)
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
        ref = node.ref
        ref.state = value
        return True
    
    def supportedDropActions(self):
        # Normally, the correct action should be ActionLink, but the drop doesn't work. It doesn't
        # work with ActionMove either. So screw that, and accept anything.
        return Qt.ActionMask
    
    #--- Signals
    foldersAdded = pyqtSignal(list)
    #--- model --> view
    def refresh(self):
        self.reset()
    
