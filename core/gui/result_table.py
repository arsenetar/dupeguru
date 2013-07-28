# Created By: Virgil Dupras
# Created On: 2010-02-11
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from operator import attrgetter

from hscommon.gui.table import GUITable, Row
from hscommon.gui.column import Columns

from .base import DupeGuruGUIObject

class DupeRow(Row):
    def __init__(self, table, group, dupe):
        Row.__init__(self, table)
        self._app = table.app
        self._group = group
        self._dupe = dupe
        self._data = None
        self._data_delta = None
        self._delta_columns = None
    
    def is_cell_delta(self, column_name):
        """Returns whether a cell is in delta mode (orange color).
        
        If the result table is in delta mode, returns True if the column is one of the "delta
        columns", that is, one of the columns that display a a differential value rather than an
        absolute value.
        
        If not, returns True if the dupe's value is different from its ref value.
        """
        if not self.table.delta_values:
            return False
        if self.isref:
            return False
        if self._delta_columns is None:
            # table.DELTA_COLUMNS are always "delta"
            self._delta_columns = self.table.DELTA_COLUMNS.copy()
            dupe_info = self.data
            ref_info = self._group.ref.get_display_info(group=self._group, delta=False)
            for key, value in dupe_info.items():
                if ref_info[key] != value:
                    self._delta_columns.add(key)
        return column_name in self._delta_columns
    
    @property
    def data(self):
        if self._data is None:
            self._data = self._app.get_display_info(self._dupe, self._group, False)
        return self._data
    
    @property
    def data_delta(self):
        if self._data_delta is None:
            self._data_delta = self._app.get_display_info(self._dupe, self._group, True)
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
    

class ResultTable(GUITable, DupeGuruGUIObject):
    def __init__(self, app):
        GUITable.__init__(self)
        DupeGuruGUIObject.__init__(self, app)
        self.columns = Columns(self, prefaccess=app, savename='ResultTable')
        self._power_marker = False
        self._delta_values = False
        self._sort_descriptors = ('name', True)
    
    #--- Override
    def _view_updated(self):
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
        if row is None:
            # There's all kinds of way the current row can be swept off during rename. When it
            # happens, selected_row will be None.
            return False
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
        self.refresh(refresh_view=False)
        self.select(indexes)
        self.view.refresh()
    
    def save_session(self):
        self.columns.save_columns()
    
