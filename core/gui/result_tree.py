# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from operator import attrgetter

from hsgui.tree import Tree, Node

from .base import GUIObject

class DupeNode(Node):
    def __init__(self, app, group, dupe):
        Node.__init__(self, '')
        self._app = app
        self._group = group
        self._dupe = dupe
        self._data = None
        self._data_delta = None
    
    @property
    def data(self):
        if self._data is None:
            self._data = self._app._get_display_info(self._dupe, self._group, False)
        return self._data
    
    @property
    def data_delta(self):
        if self._data_delta is None:
            self._data_delta = self._app._get_display_info(self._dupe, self._group, True)
        return self._data_delta
    
    @property
    def markable(self):
        return self._app.results.is_markable(self._dupe)
    
    @property
    def marked(self):
        return self._app.results.is_marked(self._dupe)
    
    @marked.setter
    def marked(self, value):
        self._app.mark_dupe(self._dupe, value)
    

class ResultTree(GUIObject, Tree):
    def __init__(self, view, app):
        GUIObject.__init__(self, view, app)
        Tree.__init__(self)
        self._power_marker = False
        self._delta_values = False
        self._sort_descriptors = (0, True)
        self.connect()
        self._refresh()
        self.view.refresh()
    
    #--- Override
    def _select_nodes(self, nodes):
        Tree._select_nodes(self, nodes)
        self.app._select_dupes(map(attrgetter('_dupe'), nodes))
    
    #--- Private
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
            to_find = set(self.app.selected_dupes)
            nodes = list(self.findall(lambda n: n is not self and n._dupe in to_find))
            self.selected_nodes = nodes
    
    #--- Public
    def get_node_value(self, path, column):
        try:
            node = self.get_node(path)
        except IndexError:
            return '---'
        if self.delta_values:
            return node.data_delta[column]
        else:
            return node.data[column]
    
    def root_children_counts(self):
        # This is a speed optimization for cases where there's a lot of results so that there is
        # not thousands of children_count queries when expandAll is called.
        return [len(node) for node in self]
    
    def sort(self, key, asc):
        if self.power_marker:
            self.app.results.sort_dupes(key, asc, self.delta_values)
        else:
            self.app.results.sort_groups(key, asc)
        self._sort_descriptors = (key, asc)
        self._refresh()
        self.view.refresh()
    
    #--- Properties
    @property
    def power_marker(self):
        return self._power_marker
    
    @power_marker.setter
    def power_marker(self, value):
        if value == self._power_marker:
            return
        self._power_marker = value
        key, asc = self._sort_descriptors
        self.sort(key, asc)
        self._refresh()
        self.view.refresh()
    
    @property
    def delta_values(self):
        return self._delta_values
    
    @delta_values.setter
    def delta_values(self, value):
        if value == self._delta_values:
            return
        self._delta_values = value
        self._refresh()
        self.view.refresh()
    
    #--- Event Handlers
    def marking_changed(self):
        self.view.invalidate_markings()
    
    def results_changed(self):
        self._refresh()
        self.view.refresh()
    
