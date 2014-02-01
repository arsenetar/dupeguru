# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import Sequence, MutableSequence

from .base import GUIObject

class Selectable(Sequence):
    """Mix-in for a ``Sequence`` that manages its selection status.
    
    When mixed in with a ``Sequence``, we enable it to manage its selection status. The selection
    is held as a list of ``int`` indexes. Multiple selection is supported.
    """
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
        """(Virtual) Updates the model's selection appropriately.
        
        Called after selection has been updated. Takes the table's selection and does appropriates
        updates on the view and/or model. Common sense would dictate that when the selection doesn't
        change, we don't update anything (and thus don't call ``_update_selection()`` at all), but
        there are cases where it's false. For example, if our list updates its items but doesn't
        change its selection, we probably want to update the model's selection.
        
        By default, does nothing.
        
        Important note: This is only called on :meth:`select`, not on changes to
        :attr:`selected_indexes`.
        """
        # A redesign of how this whole thing works is probably in order, but not now, there's too
        # much breakage at once involved.
    
    #--- Public
    def select(self, indexes):
        """Update selection to ``indexes``.
        
        :meth:`_update_selection` is called afterwards.
        
        :param list indexes: List of ``int`` that is to become the new selection.
        """
        if isinstance(indexes, int):
            indexes = [indexes]
        self.selected_indexes = indexes
        self._update_selection()
    
    #--- Properties
    @property
    def selected_index(self):
        """Points to the first selected index.
        
        *int*. *get/set*. 
        
        Thin wrapper around :attr:`selected_indexes`. ``None`` if selection is empty. Using this
        property only makes sense if your selectable sequence supports single selection only.
        """
        return self._selected_indexes[0] if self._selected_indexes else None
    
    @selected_index.setter
    def selected_index(self, value):
        self.selected_indexes = [value]
    
    @property
    def selected_indexes(self):
        """List of selected indexes.
        
        *list of int*. *get/set*.
        
        When setting the value, automatically removes out-of-bounds indexes. The list is kept
        sorted.
        """
        return self._selected_indexes
    
    @selected_indexes.setter
    def selected_indexes(self, value):
        self._selected_indexes = value
        self._selected_indexes.sort()
        self._check_selection_range()


class SelectableList(MutableSequence, Selectable):
    """A list that can manage selection of its items.
    
    Subclasses :class:`Selectable`. Behaves like a ``list``.
    """
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
        """(Virtual) Called whenever the contents of the list changes.
        
        By default, does nothing.
        """
    
    #--- Public
    def search_by_prefix(self, prefix):
        # XXX Why the heck is this method here?
        prefix = prefix.lower()
        for index, s in enumerate(self):
            if s.lower().startswith(prefix):
                return index
        return -1
    

class GUISelectableListView:
    """Expected interface for :class:`GUISelectableList`'s view.
    
    *Not actually used in the code. For documentation purposes only.*
    
    Our view, some kind of list view or combobox, is expected to sync with the list's contents by
    appropriately behave to all callbacks in this interface.
    """
    def refresh(self):
        """Refreshes the contents of the list widget.
        
        Ensures that the contents of the list widget is synced with the model.
        """
    
    def update_selection(self):
        """Update selection status.
        
        Ensures that the list widget's selection is in sync with the model.
        """

class GUISelectableList(SelectableList, GUIObject):
    """Cross-toolkit GUI-enabled list view.
    
    Represents a UI element presenting the user with a selectable list of items.
    
    Subclasses :class:`SelectableList` and :class:`.GUIObject`. Expected view:
    :class:`GUISelectableListView`.
    
    :param iterable items: If specified, items to fill the list with initially.
    """
    def __init__(self, items=None):
        SelectableList.__init__(self, items)
        GUIObject.__init__(self)
    
    def _view_updated(self):
        """Refreshes the view contents with :meth:`GUISelectableListView.refresh`.
        
        Overrides :meth:`~hscommon.gui.base.GUIObject._view_updated`.
        """
        self.view.refresh()
    
    def _update_selection(self):
        """Refreshes the view selection with :meth:`GUISelectableListView.update_selection`.
        
        Overrides :meth:`Selectable._update_selection`.
        """
        self.view.update_selection()
    
    def _on_change(self):
        """Refreshes the view contents with :meth:`GUISelectableListView.refresh`.
        
        Overrides :meth:`SelectableList._on_change`.
        """
        self.view.refresh()
