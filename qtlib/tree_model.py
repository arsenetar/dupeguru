# Created By: Virgil Dupras
# Created On: 2009-09-14
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging

from PyQt5.QtCore import QAbstractItemModel, QModelIndex

class NodeContainer:
    def __init__(self):
        self._subnodes = None
        self._ref2node = {}
    
    #--- Protected
    def _createNode(self, ref, row):
        # This returns a TreeNode instance from ref
        raise NotImplementedError()
    
    def _getChildren(self):
        # This returns a list of ref instances, not TreeNode instances
        raise NotImplementedError()
    
    #--- Public
    def invalidate(self):
        # Invalidates cached data and list of subnodes without resetting ref2node.
        self._subnodes = None
    
    #--- Properties
    @property
    def subnodes(self):
        if self._subnodes is None:
            children = self._getChildren()
            self._subnodes = []
            for index, child in enumerate(children):
                if child in self._ref2node:
                    node = self._ref2node[child]
                    node.row = index
                else:
                    node = self._createNode(child, index)
                    self._ref2node[child] = node
                self._subnodes.append(node)
        return self._subnodes
    

class TreeNode(NodeContainer):
    def __init__(self, model, parent, row):
        NodeContainer.__init__(self)
        self.model = model
        self.parent = parent
        self.row = row
    
    @property
    def index(self):
        return self.model.createIndex(self.row, 0, self)
    

class RefNode(TreeNode):
    """Node pointing to a reference node.
    
    Use this if your Qt model wraps around a tree model that has iterable nodes.
    """
    def __init__(self, model, parent, ref, row):
        TreeNode.__init__(self, model, parent, row)
        self.ref = ref
    
    def _createNode(self, ref, row):
        return RefNode(self.model, self, ref, row)
    
    def _getChildren(self):
        return list(self.ref)
    

# We use a specific TreeNode subclass to easily spot dummy nodes, especially in exception tracebacks.
class DummyNode(TreeNode):
    pass

class TreeModel(QAbstractItemModel, NodeContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dummyNodes = set() # dummy nodes' reference have to be kept to avoid segfault
    
    #--- Private
    def _createDummyNode(self, parent, row):
        # In some cases (drag & drop row removal, to be precise), there's a temporary discrepancy
        # between a node's subnodes and what the model think it has. This leads to invalid indexes
        # being queried. Rather than going through complicated row removal crap, it's simpler to
        # just have rows with empty data replacing removed rows for the millisecond that the drag &
        # drop lasts. Override this to return a node of the correct type.
        return DummyNode(self, parent, row)
    
    def _lastIndex(self):
        """Index of the very last item in the tree.
        """
        currentIndex = QModelIndex()
        rowCount = self.rowCount(currentIndex)
        while rowCount > 0:
            currentIndex = self.index(rowCount-1, 0, currentIndex)
            rowCount = self.rowCount(currentIndex)
        return currentIndex
    
    #--- Overrides
    def index(self, row, column, parent):
        if not self.subnodes:
            return QModelIndex()
        node = parent.internalPointer() if parent.isValid() else self
        try:
            return self.createIndex(row, column, node.subnodes[row])
        except IndexError:
            logging.debug("Wrong tree index called (%r, %r, %r). Returning DummyNode",
                row, column, node)
            parentNode = parent.internalPointer() if parent.isValid() else None
            dummy = self._createDummyNode(parentNode, row)
            self._dummyNodes.add(dummy)
            return self.createIndex(row, column, dummy)
    
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        else:
            return self.createIndex(node.parent.row, 0, node.parent)
    
    def reset(self):
        super().beginResetModel()
        self.invalidate()
        self._ref2node = {}
        self._dummyNodes = set()
        super().endResetModel()
    
    def rowCount(self, parent=QModelIndex()):
        node = parent.internalPointer() if parent.isValid() else self
        return len(node.subnodes)
    
    #--- Public
    def findIndex(self, rowPath):
        """Returns the QModelIndex at `rowPath`
        
        `rowPath` is a sequence of node rows. For example, [1, 2, 1] is the 2nd child of the
        3rd child of the 2nd child of the root.
        """
        result = QModelIndex()
        for row in rowPath:
            result = self.index(row, 0, result)
        return result
    
    @staticmethod
    def pathForIndex(index):
        reversedPath = []
        while index.isValid():
            reversedPath.append(index.row())
            index = index.parent()
        return list(reversed(reversedPath))
    
    def refreshData(self):
        """Updates the data on all nodes, but without having to perform a full reset.
        
        A full reset on a tree makes us lose selection and expansion states. When all we ant to do
        is to refresh the data on the nodes without adding or removing a node, a call on
        dataChanged() is better. But of course, Qt makes our life complicated by asking us topLeft
        and bottomRight indexes. This is a convenience method refreshing the whole tree.
        """
        columnCount = self.columnCount()
        topLeft = self.index(0, 0, QModelIndex())
        bottomLeft = self._lastIndex()
        bottomRight = self.sibling(bottomLeft.row(), columnCount-1, bottomLeft)
        self.dataChanged.emit(topLeft, bottomRight)
    
