# Created By: Virgil Dupras
# Created On: 2009-04-23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL, Qt, QAbstractItemModel, QModelIndex, QRect
from PyQt4.QtGui import QBrush, QStyledItemDelegate, QFont, QTreeView, QColor

from qtlib.tree_model import TreeNode, TreeModel

class ResultNode(TreeNode):
    def __init__(self, model, parent, row, dupe, group):
        TreeNode.__init__(self, model, parent, row)
        self.dupe = dupe
        self.group = group
        self._normalData = None
        self._deltaData = None
    
    def _createNode(self, ref, row):
        return ResultNode(self.model, self, row, ref, self.group)
    
    def _getChildren(self):
        return self.group.dupes if self.dupe is self.group.ref else []
    
    def invalidate(self):
        self._normalData = None
        self._deltaData = None
        TreeNode.invalidate(self)
    
    @property
    def normalData(self):
        if self._normalData is None:
            self._normalData = self.model._app._get_display_info(self.dupe, self.group, delta=False)
        return self._normalData
    
    @property
    def deltaData(self):
        if self._deltaData is None:
            self._deltaData = self.model._app._get_display_info(self.dupe, self.group, delta=True)
        return self._deltaData
    

class ResultsDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        QStyledItemDelegate.initStyleOption(self, option, index)
        node = index.internalPointer()
        if node.group.ref is node.dupe:
            newfont = QFont(option.font)
            newfont.setBold(True)
            option.font = newfont
    

class ResultsModel(TreeModel):
    def __init__(self, app):
        self._app = app
        self._results = app.results
        self._data = app.data
        self._delta_columns = app.DELTA_COLUMNS
        self.delta = False
        self._power_marker = False
        TreeModel.__init__(self)
    
    def _createNode(self, ref, row):
        if self.power_marker:
            # ref is a dupe
            group = self._results.get_group_of_duplicate(ref)
            return ResultNode(self, None, row, ref, group)
        else:
            # ref is a group
            return ResultNode(self, None, row, ref.ref, ref)
    
    def _getChildren(self):
        return self._results.dupes if self.power_marker else self._results.groups
    
    def columnCount(self, parent):
        return len(self._data.COLUMNS)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            data = node.deltaData if self.delta else node.normalData
            return data[index.column()]
        elif role == Qt.CheckStateRole:
            if index.column() == 0 and node.dupe is not node.group.ref:
                state = Qt.Checked if self._results.is_marked(node.dupe) else Qt.Unchecked
                return state
        elif role == Qt.ForegroundRole:
            if node.dupe is node.group.ref or node.dupe.is_ref:
                return QBrush(Qt.blue)
            elif self.delta and index.column() in self._delta_columns:
                return QBrush(QColor(255, 142, 40)) # orange
        elif role == Qt.EditRole:
            if index.column() == 0:
                return node.normalData[index.column()]
        return None
    
    def dupesForIndexes(self, indexes):
        nodes = [index.internalPointer() for index in indexes]
        return [node.dupe for node in nodes]
    
    def indexesForDupes(self, dupes):
        def index(dupe):
            try:
                if self.power_marker:
                    row = self._results.dupes.index(dupe)
                    node = self.subnodes[row]
                    assert node.dupe is dupe
                    return self.createIndex(row, 0, node)
                else:
                    group = self._results.get_group_of_duplicate(dupe)
                    row = self._results.groups.index(group)
                    node = self.subnodes[row]
                    if dupe is group.ref:
                        assert node.dupe is dupe
                        return self.createIndex(row, 0, node)
                    subrow = group.dupes.index(dupe)
                    subnode = node.subnodes[subrow]
                    assert subnode.dupe is dupe
                    return self.createIndex(subrow, 0, subnode)
            except ValueError: # the dupe is not there anymore
                return QModelIndex()
        
        return map(index, dupes)
    
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
        if role == Qt.CheckStateRole:
            if index.column() == 0:
                self._app.toggle_marking_for_dupes([node.dupe])
                return True
        if role == Qt.EditRole:
            if index.column() == 0:
                value = unicode(value.toString())
                if self._app.rename_dupe(node.dupe, value):
                    node.invalidate()
                    return True
        return False
    
    def sort(self, column, order):
        if self.power_marker:
            self._results.sort_dupes(column, order == Qt.AscendingOrder, self.delta)
        else:
            self._results.sort_groups(column, order == Qt.AscendingOrder)
        self.reset()
    
    def toggleMarked(self, indexes):
        assert indexes
        dupes = self.dupesForIndexes(indexes)
        self._app.toggle_marking_for_dupes(dupes)
    
    #--- Properties
    @property
    def power_marker(self):
        return self._power_marker
    
    @power_marker.setter
    def power_marker(self, value):
        if value == self._power_marker:
            return
        self._power_marker = value
        self.reset()
    

class ResultsView(QTreeView):
    #--- Override
    def keyPressEvent(self, event):
        if event.text() == ' ':
            self.model().toggleMarked(self.selectionModel().selectedRows())
            return
        QTreeView.keyPressEvent(self, event)
    
    def mouseDoubleClickEvent(self, event):
        self.emit(SIGNAL('doubleClicked()'))
        # We don't call the superclass' method because the default behavior is to rename the cell.
    
    def setModel(self, model):
        assert isinstance(model, ResultsModel)
        QTreeView.setModel(self, model)
    
    #--- Public
    def selectedDupes(self):
        return self.model().dupesForIndexes(self.selectionModel().selectedRows())
    
