# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from operator import attrgetter

from hsgui.table import GUITable, Row

from .base import GUIObject

class DupeRow(Row):
    def __init__(self, table, group, dupe):
        Row.__init__(self, table)
        self._app = table.app
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
    def isref(self):
        return self._dupe is self._group.ref
    
    @property
    def markable(self):
        return self._app.results.is_markable(self._dupe)
    
    @property
    def marked(self):
        return self._app.results.is_marked(self._dupe)
    
    @marked.setter
    def marked(self, value):
        self._app.mark_dupe(self._dupe, value)
    

class ResultTable(GUIObject, GUITable):
    def __init__(self, view, app):
        GUIObject.__init__(self, view, app)
        GUITable.__init__(self)
        self._power_marker = False
        self._delta_values = False
        self._sort_descriptors = (0, True)
    
    #--- Override
    def connect(self):
        GUIObject.connect(self)
        self._refresh_with_view()
    
    def _restore_selection(self, previous_selection):
        if self.app.selected_dupes:
            to_find = set(self.app.selected_dupes)
            indexes = [i for i, r in enumerate(self) if r._dupe in to_find]
            self.selected_indexes = indexes
    
    def _update_selection(self):
        rows = self.selected_rows
        self.app._select_dupes(list(map(attrgetter('_dupe'), rows)))
    
    def _fill(self):
        if not self.power_marker:
            for group in self.app.results.groups:
                self.append(DupeRow(self, group, group.ref))
                for dupe in group.dupes:
                    self.append(DupeRow(self, group, dupe))
        else:
            for dupe in self.app.results.dupes:
                group = self.app.results.get_group_of_duplicate(dupe)
                self.append(DupeRow(self, group, dupe))
    
    def _refresh_with_view(self):
        self.refresh()
        self.view.refresh()
        self.view.show_selected_row()
    
    #--- Public
    def get_row_value(self, index, column):
        try:
            row = self[index]
        except IndexError:
            return '---'
        if self.delta_values:
            return row.data_delta[column]
        else:
            return row.data[column]
    
    def rename_selected(self, newname):
        row = self.selected_row
        row._data = None
        row._data_delta = None
        return self.app.rename_selected(newname)
    
    def sort(self, key, asc):
        if self.power_marker:
            self.app.results.sort_dupes(key, asc, self.delta_values)
        else:
            self.app.results.sort_groups(key, asc)
        self._sort_descriptors = (key, asc)
        self._refresh_with_view()
    
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
        # no need to refresh, it has happened in sort()
    
    @property
    def delta_values(self):
        return self._delta_values
    
    @delta_values.setter
    def delta_values(self, value):
        if value == self._delta_values:
            return
        self._delta_values = value
        self.refresh()
        self.view.refresh()
    
    @property
    def selected_dupe_count(self):
        return sum(1 for row in self.selected_rows if not row.isref)
    
    #--- Event Handlers
    def marking_changed(self):
        self.view.invalidate_markings()
    
    def results_changed(self):
        self._refresh_with_view()
    
    def results_changed_but_keep_selection(self):
        # What we want to to here is that instead of restoring selected *dupes* after refresh, we
        # restore selected *paths*.
        indexes = self.selected_indexes
        self.refresh()
        self.select(indexes)
        self.view.refresh()
    
