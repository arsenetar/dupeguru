# Created By: Virgil Dupras
# Created On: 2010-07-25
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import copy

from .base import GUIObject

class Column:
    def __init__(self, name, display='', visible=True, optional=False):
        self.name = name
        self.logical_index = 0
        self.ordered_index = 0
        self.width = 0
        self.default_width = 0
        self.display = display
        self.visible = visible
        self.default_visible = visible
        self.optional = optional
    

class Columns(GUIObject):
    def __init__(self, table, prefaccess=None, savename=None):
        GUIObject.__init__(self)
        self.table = table
        self.prefaccess = prefaccess
        self.savename = savename
        # We use copy here for test isolation. If we don't, changing a column affects all tests.
        self.column_list = list(map(copy.copy, table.COLUMNS))
        for i, column in enumerate(self.column_list):
            column.logical_index = i
            column.ordered_index = i
        self.coldata = {col.name: col for col in self.column_list}
    
    #--- Private
    def _get_colname_attr(self, colname, attrname, default):
        try:
            return getattr(self.coldata[colname], attrname)
        except KeyError:
            return default
    
    def _set_colname_attr(self, colname, attrname, value):
        try:
            col = self.coldata[colname]
            setattr(col, attrname, value)
        except KeyError:
            pass
    
    def _optional_columns(self):
        return [c for c in self.column_list if c.optional]
    
    #--- Override
    def _view_updated(self):
        self.restore_columns()
    
    #--- Public
    def column_by_index(self, index):
        return self.column_list[index]
    
    def column_by_name(self, name):
        return self.coldata[name]
    
    def columns_count(self):
        return len(self.column_list)
    
    def column_display(self, colname):
        return self._get_colname_attr(colname, 'display', '')
    
    def column_is_visible(self, colname):
        return self._get_colname_attr(colname, 'visible', True)
    
    def column_width(self, colname):
        return self._get_colname_attr(colname, 'width', 0)
    
    def columns_to_right(self, colname):
        column = self.coldata[colname]
        index = column.ordered_index
        return [col.name for col in self.column_list if (col.visible and col.ordered_index > index)]
    
    def menu_items(self):
        # Returns a list of (display_name, marked) items for each optional column in the current
        # view (marked means that it's visible).
        return [(c.display, c.visible) for c in self._optional_columns()]
    
    def move_column(self, colname, index):
        colnames = self.colnames
        colnames.remove(colname)
        colnames.insert(index, colname)
        self.set_column_order(colnames)
    
    def reset_to_defaults(self):
        self.set_column_order([col.name for col in self.column_list])
        for col in self._optional_columns():
            col.visible = col.default_visible
            col.width = col.default_width
        self.view.restore_columns()
    
    def resize_column(self, colname, newwidth):
        self._set_colname_attr(colname, 'width', newwidth)
    
    def restore_columns(self):
        if not (self.prefaccess and self.savename and self.coldata):
            if (not self.savename) and (self.coldata):
                # This is a table that will not have its coldata saved/restored. we should
                # "restore" its default column attributes.
                self.view.restore_columns()
            return
        for col in self.column_list:
            pref_name = '{}.Columns.{}'.format(self.savename, col.name)
            coldata = self.prefaccess.get_default(pref_name, fallback_value={})
            if 'index' in coldata:
                col.ordered_index = coldata['index']
            if 'width' in coldata:
                col.width = coldata['width']
            if col.optional and 'visible' in coldata:
                col.visible = coldata['visible']
        self.view.restore_columns()
    
    def save_columns(self):
        if not (self.prefaccess and self.savename and self.coldata):
            return
        for col in self.column_list:
            pref_name = '{}.Columns.{}'.format(self.savename, col.name)
            coldata = {'index': col.ordered_index, 'width': col.width}
            if col.optional:
                coldata['visible'] = col.visible
            self.prefaccess.set_default(pref_name, coldata)
    
    def set_column_order(self, colnames):
        colnames = (name for name in colnames if name in self.coldata)
        for i, colname in enumerate(colnames):
            col = self.coldata[colname]
            col.ordered_index = i
    
    def set_column_visible(self, colname, visible):
        self.table.save_edits() # the table on the GUI side will stop editing when the columns change
        self._set_colname_attr(colname, 'visible', visible)
        self.view.set_column_visible(colname, visible)
    
    def set_default_width(self, colname, width):
        self._set_colname_attr(colname, 'default_width', width)
    
    def toggle_menu_item(self, index):
        col = self._optional_columns()[index]
        self.set_column_visible(col.name, not col.visible)
        return col.visible
    
    #--- Properties
    @property
    def ordered_columns(self):
        return [col for col in sorted(self.column_list, key=lambda col: col.ordered_index)]
    
    @property
    def colnames(self):
        return [col.name for col in self.ordered_columns]
    
