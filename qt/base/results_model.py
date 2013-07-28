# Created By: Virgil Dupras
# Created On: 2009-04-23
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QBrush, QFont, QFontMetrics, QTableView, QColor

from qtlib.table import Table

class ResultsModel(Table):
    def __init__(self, app, view):
        model = app.model.result_table
        Table.__init__(self, model, view)
        view.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)
        
        app.prefsChanged.connect(self.appPrefsChanged)
        app.willSavePrefs.connect(self.appWillSavePrefs)
    
    def _getData(self, row, column, role):
        if column.name == 'marked':
            if role == Qt.CheckStateRole and row.markable:    
                return Qt.Checked if row.marked else Qt.Unchecked
            return None
        if role == Qt.DisplayRole:
            data = row.data_delta if self.model.delta_values else row.data
            return data[column.name]
        elif role == Qt.ForegroundRole:
            if row.isref:
                return QBrush(Qt.blue)
            elif row.is_cell_delta(column.name):
                return QBrush(QColor(255, 142, 40)) # orange
        elif role == Qt.FontRole:
            isBold = row.isref
            font = QFont(self.view.font())
            font.setBold(isBold)
            return font
        elif role == Qt.EditRole:
            if column.name == 'name':
                return row.data[column.name]
        return None
    
    def _getFlags(self, row, column):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if column.name == 'marked':
            if row.markable:
                flags |= Qt.ItemIsUserCheckable
        elif column.name == 'name':
            flags |= Qt.ItemIsEditable
        return flags
    
    def _setData(self, row, column, value, role):
        if role == Qt.CheckStateRole:
            if column.name == 'marked':
                row.marked = bool(value)
                return True
        elif role == Qt.EditRole:
            if column.name == 'name':
                return self.model.rename_selected(value)
        return False
    
    def sort(self, column, order):
        column = self.model.COLUMNS[column]
        self.model.sort(column.name, order == Qt.AscendingOrder)
    
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
    def appPrefsChanged(self, prefs):
        font = self.view.font()
        font.setPointSize(prefs.tableFontSize)
        self.view.setFont(font)
        fm = QFontMetrics(font)
        self.view.verticalHeader().setDefaultSectionSize(fm.height()+2)
    
    def appWillSavePrefs(self):
        self.model.columns.save_columns()
    
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
            self.spacePressed.emit()
            return
        QTableView.keyPressEvent(self, event)
    
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(None)
        # We don't call the superclass' method because the default behavior is to rename the cell.
    
    #--- Signals
    spacePressed = pyqtSignal()
