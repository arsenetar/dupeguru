# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QItemSelectionModel, QItemSelection

from .column import Columns

class Table(QAbstractTableModel):
    # Flags you want when index.isValid() is False. In those cases, _getFlags() is never called.
    INVALID_INDEX_FLAGS = Qt.ItemIsEnabled
    COLUMNS = []
    
    def __init__(self, model, view, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.view = view
        self.view.setModel(self)
        self.model.view = self
        if hasattr(self.model, 'columns'):
            self.columns = Columns(self.model.columns, self.COLUMNS, view.horizontalHeader())
        
        self.view.selectionModel().selectionChanged[(QItemSelection, QItemSelection)].connect(self.selectionChanged)
    
    def _updateModelSelection(self):
        # Takes the selection on the view's side and update the model with it.
        # an _updateViewSelection() call will normally result in an _updateModelSelection() call.
        # to avoid infinite loops, we check that the selection will actually change before calling
        # model.select()
        newIndexes = [modelIndex.row() for modelIndex in self.view.selectionModel().selectedRows()]
        if newIndexes != self.model.selected_indexes:
            self.model.select(newIndexes)
    
    def _updateViewSelection(self):
        # Takes the selection on the model's side and update the view with it.
        newSelection = QItemSelection()
        columnCount = self.columnCount(QModelIndex())
        for index in self.model.selected_indexes:
            newSelection.select(self.createIndex(index, 0), self.createIndex(index, columnCount-1))
        self.view.selectionModel().select(newSelection, QItemSelectionModel.ClearAndSelect)
        if len(newSelection.indexes()):
            currentIndex = newSelection.indexes()[0]
            self.view.selectionModel().setCurrentIndex(currentIndex, QItemSelectionModel.Current)
            self.view.scrollTo(currentIndex)
    
    #--- Data Model methods
    # Virtual
    def _getData(self, row, column, role):
        if role in (Qt.DisplayRole, Qt.EditRole):
            attrname = column.name
            return row.get_cell_value(attrname)
        elif role == Qt.TextAlignmentRole:
            return column.alignment
        return None
    
    # Virtual
    def _getFlags(self, row, column):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if row.can_edit_cell(column.name):
            flags |= Qt.ItemIsEditable
        return flags
    
    # Virtual
    def _setData(self, row, column, value, role):
        if role == Qt.EditRole:
            attrname = column.name
            if attrname == 'from':
                attrname = 'from_'
            setattr(row, attrname, value)
            return True
        return False
    
    def columnCount(self, index):
        return self.model.columns.columns_count()
    
    def data(self, index, role):
        if not index.isValid():
            return None
        row = self.model[index.row()]
        column = self.model.columns.column_by_index(index.column())
        return self._getData(row, column, role)
    
    def flags(self, index):
        if not index.isValid():
            return self.INVALID_INDEX_FLAGS
        row = self.model[index.row()]
        column = self.model.columns.column_by_index(index.column())
        return self._getFlags(row, column)
    
    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal:
            return None
        if section >= self.model.columns.columns_count():
            return None
        column = self.model.columns.column_by_index(section)
        if role == Qt.DisplayRole:
            return column.display
        elif role == Qt.TextAlignmentRole:
            return column.alignment
        else:
            return None
    
    def revert(self):
        self.model.cancel_edits()
    
    def rowCount(self, index):
        if index.isValid():
            return 0
        return len(self.model)
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        row = self.model[index.row()]
        column = self.model.columns.column_by_index(index.column())
        return self._setData(row, column, value, role)
    
    def sort(self, section, order):
        column = self.model.columns.column_by_index(section)
        attrname = column.name
        self.model.sort_by(attrname, desc=order==Qt.DescendingOrder)
    
    def submit(self):
        self.model.save_edits()
        return True
    
    #--- Events
    def selectionChanged(self, selected, deselected):
        self._updateModelSelection()
    
    #--- model --> view
    def refresh(self):
        self.beginResetModel()
        self.endResetModel()
        self._updateViewSelection()
    
    def show_selected_row(self):
        if self.model.selected_index is not None:
            self.view.showRow(self.model.selected_index)
    
    def start_editing(self):
        self.view.editSelected()
    
    def stop_editing(self):
        self.view.setFocus() # enough to stop editing
    
    def update_selection(self):
        self._updateViewSelection()
