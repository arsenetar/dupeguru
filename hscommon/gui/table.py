# Created By: Eric Mc Sween
# Created On: 2008-05-29
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import MutableSequence, namedtuple

from .base import GUIObject
from .selectable_list import Selectable

# We used to directly subclass list, but it caused problems at some point with deepcopy

# Adding and removing footer here and there might seem (and is) hackish, but it's much simpler than
# the alternative, which is to override magic methods and adjust the results. When we do that, there
# the slice stuff that we have to implement and it gets quite complex.
# Moreover, the most frequent operation on a table is __getitem__, and making checks to know whether
# the key is a header or footer at each call would make that operation, which is the most used,
# slower.
class Table(MutableSequence, Selectable):
    def __init__(self):
        Selectable.__init__(self)
        self._rows = []
        self._header = None
        self._footer = None
    
    def __delitem__(self, key):
        self._rows.__delitem__(key)
        if self._header is not None and ((not self) or (self[0] is not self._header)):
            self._header = None
        if self._footer is not None and ((not self) or (self[-1] is not self._footer)):
            self._footer = None
        self._check_selection_range()
    
    def __getitem__(self, key):
        return self._rows.__getitem__(key)
    
    def __len__(self):
        return len(self._rows)
    
    def __setitem__(self, key, value):
        self._rows.__setitem__(key, value)
    
    def append(self, item):
        if self._footer is not None:
            self._rows.insert(-1, item)
        else:
            self._rows.append(item)
    
    def insert(self, index, item):
        if (self._header is not None) and (index == 0):
            index = 1
        if (self._footer is not None) and (index >= len(self)):
            index = len(self) - 1
        self._rows.insert(index, item)
    
    def remove(self, row):
        if row is self._header:
            self._header = None
        if row is self._footer:
            self._footer = None
        self._rows.remove(row)
        self._check_selection_range()
    
    def sort_by(self, column_name, desc=False):
        if self._header is not None:
            self._rows.pop(0)
        if self._footer is not None:
            self._rows.pop()
        key = lambda row: row.sort_key_for_column(column_name)
        self._rows.sort(key=key, reverse=desc)
        if self._header is not None:
            self._rows.insert(0, self._header)
        if self._footer is not None:
            self._rows.append(self._footer)
    
    #--- Properties
    @property
    def footer(self):
        return self._footer
    
    @footer.setter
    def footer(self, value):
        if self._footer is not None:
            self._rows.pop()
        if value is not None:
            self._rows.append(value)
        self._footer = value
    
    @property
    def header(self):
        return self._header
    
    @header.setter
    def header(self, value):
        if self._header is not None:
            self._rows.pop(0)
        if value is not None:
            self._rows.insert(0, value)
        self._header = value
    
    @property
    def row_count(self):
        result = len(self)
        if self._footer is not None:
            result -= 1
        if self._header is not None:
            result -= 1
        return result
    
    @property
    def rows(self):
        start = None
        end = None
        if self._footer is not None:
            end = -1
        if self._header is not None:
            start = 1
        return self[start:end]
    
    @property
    def selected_row(self):
        return self[self.selected_index] if self.selected_index is not None else None
    
    @selected_row.setter
    def selected_row(self, value):
        try:
            self.selected_index = self.index(value)
        except ValueError:
            pass
    
    @property
    def selected_rows(self):
        return [self[index] for index in self.selected_indexes]


SortDescriptor = namedtuple('SortDescriptor', 'column desc')
class GUITable(Table, GUIObject):
    def __init__(self):
        GUIObject.__init__(self)
        Table.__init__(self)
        self.edited = None
        self._sort_descriptor = None
    
    #--- Virtual
    def _do_add(self):
        # Creates a new row, adds it in the table and returns (row, insert_index)
        raise NotImplementedError()
    
    def _do_delete(self):
        # Delete the selected rows
        pass
    
    def _fill(self):
        # Called by refresh()
        # Fills the table with all the rows that this table is supposed to have.
        pass
    
    def _is_edited_new(self):
        return False
    
    def _restore_selection(self, previous_selection):
        if not self.selected_indexes:
            if previous_selection:
                self.select(previous_selection)
            else:
                self.select([len(self) - 1])
    
    #--- Public
    def add(self):
        self.view.stop_editing()
        if self.edited is not None:
            self.save_edits()
        row, insert_index = self._do_add()
        self.insert(insert_index, row)
        self.select([insert_index])
        self.edited = row
        self.view.refresh()
        self.view.start_editing()
    
    def can_edit_cell(self, column_name, row_index):
        # A row is, by default, editable as soon as it has an attr with the same name as `column`.
        # If can_edit() returns False, the row is not editable at all. You can set editability of
        # rows at the attribute level with can_edit_* properties
        row = self[row_index]
        return row.can_edit_cell(column_name)
    
    def cancel_edits(self):
        if self.edited is None:
            return
        self.view.stop_editing()
        if self._is_edited_new():
            previous_selection = self.selected_indexes
            self.remove(self.edited)
            self._restore_selection(previous_selection)
            self._update_selection()
        else:
            self.edited.load()
        self.edited = None
        self.view.refresh()
    
    def delete(self):
        self.view.stop_editing()
        if self.edited is not None:
            self.cancel_edits()
            return
        if self:
            self._do_delete()
    
    def refresh(self, refresh_view=True):
        self.cancel_edits()
        previous_selection = self.selected_indexes
        del self[:]
        self._fill()
        sd = self._sort_descriptor
        if sd is not None:
            Table.sort_by(self, column_name=sd.column, desc=sd.desc)
        self._restore_selection(previous_selection)
        if refresh_view:
            self.view.refresh()
    
    def save_edits(self):
        if self.edited is None:
            return
        row = self.edited
        self.edited = None
        row.save()
    
    def sort_by(self, column_name, desc=False):
        Table.sort_by(self, column_name=column_name, desc=desc)
        self._sort_descriptor = SortDescriptor(column_name, desc)
        self._update_selection()
        self.view.refresh()
    

class Row:
    def __init__(self, table):
        super(Row, self).__init__()
        self.table = table
    
    def _edit(self):
        if self.table.edited is self:
            return
        assert self.table.edited is None
        self.table.edited = self
    
    #--- Virtual
    def can_edit(self):
        return True
    
    def load(self):
        raise NotImplementedError()
    
    def save(self):
        raise NotImplementedError()
    
    def sort_key_for_column(self, column_name):
        # Most of the time, the adequate sort key for a column is the column name with '_' prepended
        # to it. This member usually corresponds to the unformated version of the column. If it's
        # not there, we try the column_name without underscores
        # Of course, override for exceptions.
        try:
            return getattr(self, '_' + column_name)
        except AttributeError:
            return getattr(self, column_name)
    
    #--- Public
    def can_edit_cell(self, column_name):
        if not self.can_edit():
            return False
        # '_' is in case column is a python keyword
        if not hasattr(self, column_name):
            if hasattr(self, column_name + '_'):
                column_name = column_name + '_'
            else:
                return False
        if hasattr(self, 'can_edit_' + column_name):
            return getattr(self, 'can_edit_' + column_name)
        # If the row has a settable property, we can edit the cell
        rowclass = self.__class__
        prop = getattr(rowclass, column_name, None)
        if prop is None:
            return False
        return bool(getattr(prop, 'fset', None))
    
    def get_cell_value(self, attrname):
        if attrname == 'from':
           attrname = 'from_'
        return getattr(self, attrname)
    
    def set_cell_value(self, attrname, value):
        if attrname == 'from':
            attrname = 'from_'
        setattr(self, attrname, value)
    
