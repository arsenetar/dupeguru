# Created By: Virgil Dupras
# Created On: 2009-04-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import (QBrush, QStyledItemDelegate, QFont, QTreeView, QColor, QItemSelectionModel,
    QItemSelection)

from qtlib.tree_model import TreeModel, RefNode

from core.gui.result_tree import ResultTree as ResultTreeModel

class ResultsDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        QStyledItemDelegate.initStyleOption(self, option, index)
        node = index.internalPointer()
        ref = node.ref
        if ref._group.ref is ref._dupe:
            newfont = QFont(option.font)
            newfont.setBold(True)
            option.font = newfont
    

class ResultsModel(TreeModel):
    def __init__(self, app, view):
        TreeModel.__init__(self)
        self.view = view
        self._app = app
        self._data = app.data
        self._delta_columns = app.DELTA_COLUMNS
        self.resultsDelegate = ResultsDelegate()
        self.model = ResultTreeModel(self, app)
        self.view.setItemDelegate(self.resultsDelegate)
        self.view.setModel(self)
        self.model.connect()
        
        self.connect(self.view.selectionModel(), SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged)
    
    def _createNode(self, ref, row):
        return RefNode(self, None, ref, row)
    
    def _getChildren(self):
        return list(self.model)
    
    def _updateSelection(self):
        selectedIndexes = []
        for path in self.model.selected_paths:
            modelIndex = self.findIndex(path)
            if modelIndex.isValid():
                selectedIndexes.append(modelIndex)
        if selectedIndexes:
            selection = QItemSelection()
            for modelIndex in selectedIndexes:
                selection.select(modelIndex, modelIndex)
            flags = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            self.view.selectionModel().select(selection, flags)
            flags = QItemSelectionModel.Rows
            self.view.selectionModel().setCurrentIndex(selectedIndexes[0], flags)
            self.view.scrollTo(selectedIndexes[0])
        else:
            self.view.selectionModel().clear()
    
    def columnCount(self, parent):
        return len(self._data.COLUMNS)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        ref = node.ref
        if role == Qt.DisplayRole:
            data = ref.data_delta if self.model.delta_values else ref.data
            return data[index.column()]
        elif role == Qt.CheckStateRole:
            if index.column() == 0 and ref.markable:
                return Qt.Checked if ref.marked else Qt.Unchecked
        elif role == Qt.ForegroundRole:
            if ref._dupe is ref._group.ref or ref._dupe.is_ref:
                return QBrush(Qt.blue)
            elif self.model.delta_values and index.column() in self._delta_columns:
                return QBrush(QColor(255, 142, 40)) # orange
        elif role == Qt.EditRole:
            if index.column() == 0:
                return ref.data[index.column()]
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self._data.COLUMNS):
            return self._data.COLUMNS[section]['display']
        return None
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        node = index.internalPointer()
        ref = node.ref
        if role == Qt.CheckStateRole:
            if index.column() == 0:
                self._app.mark_dupe(ref._dupe, value.toBool())
                return True
        if role == Qt.EditRole:
            if index.column() == 0:
                value = unicode(value.toString())
                return self.model.rename_selected(value)
        return False
    
    def sort(self, column, order):
        self.model.sort(column, order == Qt.AscendingOrder)
    
    #--- Properties
    @property
    def power_marker(self):
        return self.model.power_marker
    
    @power_marker.setter
    def power_marker(self, value):
        self.model.power_marker = value
    
    @property
    def delta_values(self):
        return self.model.delta_values
    
    @delta_values.setter
    def delta_values(self, value):
        self.model.delta_values = value
    
    #--- Events
    def selectionChanged(self, selected, deselected):
        indexes = self.view.selectionModel().selectedRows()
        nodes = [index.internalPointer() for index in indexes]
        self.model.selected_nodes = [node.ref for node in nodes]
    
    #--- model --> view
    def refresh(self):
        self.reset()
        self.view.expandAll()
        self._updateSelection()
    
    def invalidate_markings(self):
        # redraw view
        # HACK. this is the only way I found to update the widget without reseting everything
        self.view.scroll(0, 1)
        self.view.scroll(0, -1)
    

class ResultsView(QTreeView):
    #--- Override
    def keyPressEvent(self, event):
        if event.text() == ' ':
            self.emit(SIGNAL('spacePressed()'))
            return
        QTreeView.keyPressEvent(self, event)
    
    def mouseDoubleClickEvent(self, event):
        self.emit(SIGNAL('doubleClicked()'))
        # We don't call the superclass' method because the default behavior is to rename the cell.
    
