# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsgui.tree import Tree, Node

from .base import GUIObject

class DupeNode(Node):
    def __init__(self, app, group, dupe):
        Node.__init__(self, '')
        self._app = app
        self._group = group
        self._dupe = dupe
        self.data = app._get_display_info(dupe, group, False)
        self.data_delta = app._get_display_info(dupe, group, True)
    
    @property
    def markable(self):
        return self._app.results.is_markable(self._dupe)
    
    @property
    def marked(self):
        return self._app.results.is_marked(self._dupe)
    

class ResultTree(GUIObject, Tree):
    def __init__(self, view, app):
        GUIObject.__init__(self, view, app)
        Tree.__init__(self)
        self._power_marker = False
        self.connect()
        self._refresh()
        self.view.refresh()
    
    def _refresh(self):
        self.clear()
        if not self.power_marker:
            for group in self.app.results.groups:
                group_node = DupeNode(self.app, group, group.ref)
                self.append(group_node)
                for dupe in group.dupes:
                    group_node.append(DupeNode(self.app, group, dupe))
        else:
            for dupe in self.app.results.dupes:
                group = self.app.results.get_group_of_duplicate(dupe)
                self.append(DupeNode(self.app, group, dupe))
        if self.app.selected_dupes:
            to_find = self.app.selected_dupes[0]
            node = self.find(lambda n: n is not self and n._dupe is to_find)
            self.selected = node
    
    def get_node_value(self, path, column):
        try:
            node = self.get_node(path)
        except IndexError:
            return '---'
        if self.app.display_delta_values:
            return node.data_delta[column]
        else:
            return node.data[column]
    
    def sort(self, key, asc):
        if self.power_marker:
            self.app.sort_dupes(key, asc)
        else:
            self.app.sort_groups(key, asc)
    
    @property
    def power_marker(self):
        return self._power_marker
    
    @power_marker.setter
    def power_marker(self, value):
        if value == self._power_marker:
            return
        self._power_marker = value
        self._refresh()
        self.view.refresh()
    
    @Tree.selected.setter
    def selected(self, node):
        self._selected = node
        if node is None:
            self.app._select_dupes([])
        else:
            self.app._select_dupes([node._dupe])
    
    #--- Event Handlers
    def results_changed(self):
        self._refresh()
        self.view.refresh()
    
