#!/usr/bin/env python
# Unit Name: tree_model
# Created By: Virgil Dupras
# Created On: 2009-05-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from PyQt4.QtCore import Qt, QAbstractItemModel, QVariant, QModelIndex

class TreeNode(object):
    def __init__(self, parent, row):
        self.parent = parent
        self.row = row
        self._children = None
    
    def _get_children(self):
        raise NotImplementedError()
    
    @property
    def children(self):
        if self._children is None:
            self._children = self._get_children()
        return self._children
    

class TreeModel(QAbstractItemModel):
    def __init__(self):
        QAbstractItemModel.__init__(self)
        self._nodes = None
    
    def _root_nodes(self):
        raise NotImplementedError()
    
    def index(self, row, column, parent):
        if not self.nodes:
            return QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, self.nodes[row])
        node = parent.internalPointer()
        return self.createIndex(row, column, node.children[row])
    
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        else:
            return self.createIndex(node.parent.row, 0, node.parent)
    
    def reset(self):
        self._nodes = None
        QAbstractItemModel.reset(self)
    
    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.nodes)
        node = parent.internalPointer()
        return len(node.children)
    
    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = self._root_nodes()
        return self._nodes
    
