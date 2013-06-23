# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import Sequence, MutableSequence

from .base import GUIObject

class Selectable(Sequence):
    def __init__(self):
        self._selected_indexes = []
    
    #--- Private
    def _check_selection_range(self):
        if not self:
            self._selected_indexes = []
        if not self._selected_indexes:
            return
        self._selected_indexes = [index for index in self._selected_indexes if index < len(self)]
        if not self._selected_indexes:
            self._selected_indexes = [len(self) - 1]
    
    #--- Virtual
    def _update_selection(self):
        # Takes the table's selection and does appropriates updates on the view and/or model, when
        # appropriate. Common sense would dictate that when the selection doesn't change, we don't
        # update anything (and thus don't call _update_selection() at all), but there are cases
        # where it's false. For example, if our list updates its items but doesn't change its
        # selection, we probably want to update the model's selection. A redesign of how this whole
        # thing works is probably in order, but not now, there's too much breakage at once involved.
        pass
    
    #--- Public
    def select(self, indexes):
        if isinstance(indexes, int):
            indexes = [indexes]
        self.selected_indexes = indexes
        self._update_selection()
    
    #--- Properties
    @property
    def selected_index(self):
        return self._selected_indexes[0] if self._selected_indexes else None
    
    @selected_index.setter
    def selected_index(self, value):
        self.selected_indexes = [value]
    
    @property
    def selected_indexes(self):
        return self._selected_indexes
    
    @selected_indexes.setter
    def selected_indexes(self, value):
        self._selected_indexes = value
        self._selected_indexes.sort()
        self._check_selection_range()


class SelectableList(MutableSequence, Selectable):
    def __init__(self, items=None):
        Selectable.__init__(self)
        if items:
            self._items = list(items)
        else:
            self._items = []
    
    def __delitem__(self, key):
        self._items.__delitem__(key)
        self._check_selection_range()
        self._on_change()
    
    def __getitem__(self, key):
        return self._items.__getitem__(key)
    
    def __len__(self):
        return len(self._items)
    
    def __setitem__(self, key, value):
        self._items.__setitem__(key, value)
        self._on_change()
    
    #--- Override
    def append(self, item):
        self._items.append(item)
        self._on_change()
    
    def insert(self, index, item):
        self._items.insert(index, item)
        self._on_change()
    
    def remove(self, row):
        self._items.remove(row)
        self._check_selection_range()
        self._on_change()
    
    #--- Virtual
    def _on_change(self):
        pass
    
    #--- Public
    def search_by_prefix(self, prefix):
        prefix = prefix.lower()
        for index, s in enumerate(self):
            if s.lower().startswith(prefix):
                return index
        return -1
    

class GUISelectableList(SelectableList, GUIObject):
    #--- View interface
    # refresh()
    # update_selection()
    #
    
    def __init__(self, items=None):
        SelectableList.__init__(self, items)
        GUIObject.__init__(self)
    
    def _view_updated(self):
        self.view.refresh()
    
    def _update_selection(self):
        self.view.update_selection()
    
    def _on_change(self):
        self.view.refresh()
