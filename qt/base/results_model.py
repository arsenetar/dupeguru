# Created By: Virgil Dupras
# Created On: 2009-04-23
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QBrush, QFont, QTableView, QColor, QItemSelectionModel, QItemSelection

from qtlib.table import Table

from core.gui.result_table import ResultTable as ResultTableModel

class ResultsModel(Table):
    def __init__(self, app, view):
        model = ResultTableModel(self, app)
        self._app = app
        self._data = app.data
        self._delta_columns = app.data.DELTA_COLUMNS
        Table.__init__(self, model, view)
        self.model.connect()
    
    def columnCount(self, parent):
        return len(self._data.COLUMNS)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        row = self.model[index.row()]
        if role == Qt.DisplayRole:
            data = row.data_delta if self.model.delta_values else row.data
            return data[index.column()]
        elif role == Qt.CheckStateRole:
            if index.column() == 0 and row.markable:
                return Qt.Checked if row.marked else Qt.Unchecked
        elif role == Qt.ForegroundRole:
            if row.isref:
                return QBrush(Qt.blue)
            elif self.model.delta_values and index.column() in self._delta_columns:
                return QBrush(QColor(255, 142, 40)) # orange
        elif role == Qt.FontRole:
            isBold = row.isref
            font = QFont(self.view.font())
            font.setBold(isBold)
            return font
        elif role == Qt.EditRole:
            if index.column() == 0:
                return row.data[index.column()]
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            flags |= Qt.ItemIsEditable
            row = self.model[index.row()]
            if row.markable:
                flags |= Qt.ItemIsUserCheckable
        return flags
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self._data.COLUMNS):
            return self._data.COLUMNS[section].display
        return None
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        row = self.model[index.row()]
        if role == Qt.CheckStateRole:
            if index.column() == 0:
                self._app.mark_dupe(row._dupe, value.toBool())
                return True
        elif role == Qt.EditRole:
            if index.column() == 0:
                value = str(value.toString())
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
    
    #--- model --> view
    def invalidate_markings(self):
        # redraw view
        # HACK. this is the only way I found to update the widget without reseting everything
        self.view.scroll(0, 1)
        self.view.scroll(0, -1)
    

class ResultsView(QTableView):
    #--- Override
    def keyPressEvent(self, event):
        if event.text() == ' ':
            self.emit(SIGNAL('spacePressed()'))
            return
        QTableView.keyPressEvent(self, event)
    
    def mouseDoubleClickEvent(self, event):
        self.emit(SIGNAL('doubleClicked()'))
        # We don't call the superclass' method because the default behavior is to rename the cell.
    
