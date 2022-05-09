# Created By: Virgil Dupras
# Created On: 2009-04-25
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import pyqtSignal, Qt, QRect, QUrl, QModelIndex, QItemSelection
from PyQt5.QtWidgets import (
    QComboBox,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionComboBox,
    QStyleOptionViewItem,
    QApplication,
)
from PyQt5.QtGui import QBrush

from hscommon.trans import trget
from qt.tree_model import RefNode, TreeModel

tr = trget("ui")

HEADERS = [tr("Name"), tr("State")]
STATES = [tr("Normal"), tr("Reference"), tr("Excluded")]


class DirectoriesDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(STATES)
        return editor

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        # No idea why, but this cast is required if we want to have access to the V4 valuess
        option = QStyleOptionViewItem(option)
        if (index.column() == 1) and (option.state & QStyle.State_Selected):
            cboption = QStyleOptionComboBox()
            cboption.rect = option.rect
            # On OS X (with Qt4.6.0), adding State_Enabled to the flags causes the whole drawing to
            # fail (draw nothing), but it's an OS X only glitch. On Windows, it works alright.
            cboption.state |= QStyle.State_Enabled
            QApplication.style().drawComplexControl(QStyle.CC_ComboBox, cboption, painter)
            painter.setBrush(option.palette.text())
            rect = QRect(option.rect)
            rect.setLeft(rect.left() + 4)
            painter.drawText(rect, Qt.AlignLeft, option.text)
        else:
            super().paint(painter, option, index)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setCurrentIndex(value)
        editor.showPopup()

    def setModelData(self, editor, model, index):
        value = editor.currentIndex()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class DirectoriesModel(TreeModel):
    MIME_TYPE_FORMAT = "text/uri-list"

    def __init__(self, model, view, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.model.view = self
        self.view = view
        self.view.setModel(self)

        self.view.selectionModel().selectionChanged[(QItemSelection, QItemSelection)].connect(self.selectionChanged)

    def _create_node(self, ref, row):
        return RefNode(self, None, ref, row)

    def _get_children(self):
        return list(self.model)

    def columnCount(self, parent=QModelIndex()):
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

    def dropMimeData(self, mime_data, action, row, column, parent_index):
        # the data in mimeData is urlencoded **in utf-8**
        if not mime_data.hasFormat(self.MIME_TYPE_FORMAT):
            return False
        data = bytes(mime_data.data(self.MIME_TYPE_FORMAT)).decode("ascii")
        urls = data.split("\r\n")
        paths = [QUrl(url).toLocalFile() for url in urls if url]
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
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(HEADERS):
            return HEADERS[section]
        return None

    def mimeTypes(self):
        return [self.MIME_TYPE_FORMAT]

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

    # --- Events
    def selectionChanged(self, selected, deselected):
        new_nodes = [modelIndex.internalPointer().ref for modelIndex in self.view.selectionModel().selectedRows()]
        self.model.selected_nodes = new_nodes

    # --- Signals
    foldersAdded = pyqtSignal(list)

    # --- model --> view
    def refresh(self):
        self.reset()

    def refresh_states(self):
        self.refreshData()
