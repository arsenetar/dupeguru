# Created By: Eric Mc Sween
# Created On: 2008-05-29
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from collections import MutableSequence, namedtuple

from .base import GUIObject
from .selectable_list import Selectable

# We used to directly subclass list, but it caused problems at some point with deepcopy
class Table(MutableSequence, Selectable):
    """Sortable and selectable sequence of :class:`Row`.
    
    In fact, the Table is very similar to :class:`.SelectableList` in
    practice and differs mostly in principle. Their difference lies in the nature of their items
    they manage. With the Table, rows usually have many properties, presented in columns, and they
    have to subclass :class:`Row`.
    
    Usually used with :class:`~hscommon.gui.column.Column`.
    
    Subclasses :class:`.Selectable`.
    """
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
        """Appends ``item`` at the end of the table.
        
        If there's a footer, the item is inserted before it.
        """
        if self._footer is not None:
            self._rows.insert(-1, item)
        else:
            self._rows.append(item)
    
    def insert(self, index, item):
        """Inserts ``item`` at ``index`` in the table.
        
        If there's a header, will make sure we don't insert before it, and if there's a footer, will
        make sure that we don't insert after it.
        """
        if (self._header is not None) and (index == 0):
            index = 1
        if (self._footer is not None) and (index >= len(self)):
            index = len(self) - 1
        self._rows.insert(index, item)
    
    def remove(self, row):
        """Removes ``row`` from table.
        
        If ``row`` is a header or footer, that header or footer will be set to ``None``.
        """
        if row is self._header:
            self._header = None
        if row is self._footer:
            self._footer = None
        self._rows.remove(row)
        self._check_selection_range()
    
    def sort_by(self, column_name, desc=False):
        """Sort table by ``column_name``.
        
        Sort key for each row is computed from :meth:`Row.sort_key_for_column`.
        
        If ``desc`` is ``True``, sort order is reversed.
        
        If present, header and footer will always be first and last, respectively.
        """
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
        """If set, a row that always stay at the bottom of the table.
        
        :class:`Row`. *get/set*.
        
        When set to something else than ``None``, ``header`` and ``footer`` represent rows that will
        always be kept in first and/or last position, regardless of sorting. ``len()`` and indexing
        will include them, which means that if there's a header, ``table[0]`` returns it and if
        there's a footer, ``table[-1]`` returns it. To make things short, all list-like functions
        work with header and footer "on". But things get fuzzy for ``append()`` and ``insert()``
        because these will ensure that no "normal" row gets inserted before the header or after the
        footer.
        
        Adding and removing footer here and there might seem (and is) hackish, but it's much simpler
        than the alternative (when, of course, you need such a feature), which is to override magic
        methods and adjust the results. When we do that, there the slice stuff that we have to
        implement and it gets quite complex. Moreover, the most frequent operation on a table is
        ``__getitem__``, and making checks to know whether the key is a header or footer at each
        call would make that operation, which is the most used, slower.
        """
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
        """If set, a row that always stay at the bottom of the table.
        
        See :attr:`footer` for details.
        """
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
        """Number or rows in the table (without counting header and footer).
        
        *int*. *read-only*.
        """
        result = len(self)
        if self._footer is not None:
            result -= 1
        if self._header is not None:
            result -= 1
        return result
    
    @property
    def rows(self):
        """List of rows in the table, excluding header and footer.
        
        List of :class:`Row`. *read-only*.
        """
        start = None
        end = None
        if self._footer is not None:
            end = -1
        if self._header is not None:
            start = 1
        return self[start:end]
    
    @property
    def selected_row(self):
        """Selected row according to :attr:`.selected_index`.
        
        :class:`Row`. *get/set*.
        
        When setting this attribute, we look up the index of the row and set the selected index from
        there. If the row isn't in the list, selection isn't changed.
        """
        return self[self.selected_index] if self.selected_index is not None else None
    
    @selected_row.setter
    def selected_row(self, value):
        try:
            self.selected_index = self.index(value)
        except ValueError:
            pass
    
    @property
    def selected_rows(self):
        """List of selected rows based on :attr:`.selected_indexes`.
        
        List of :class:`Row`. *read-only*.
        """
        return [self[index] for index in self.selected_indexes]


class GUITableView:
    """Expected interface for :class:`GUITable`'s view.
    
    *Not actually used in the code. For documentation purposes only.*
    
    Our view, some kind of table view, is expected to sync with the table's contents by
    appropriately behave to all callbacks in this interface.
    
    When in edit mode, the content types by the user is expected to be sent as soon as possible
    to the :class:`Row`.
    
    Whenever the user changes the selection, we expect the view to call :meth:`Table.select`.
    """
    def refresh(self):
        """Refreshes the contents of the table widget.
        
        Ensures that the contents of the table widget is synced with the model. This includes
        selection.
        """
    
    def start_editing(self):
        """Start editing the currently selected row.
        
        Begin whatever inline editing support that the view supports.
        """
    
    def stop_editing(self):
        """Stop editing if there's an inline editing in effect.
        
        There's no "aborting" implied in this call, so it's appropriate to send whatever the user
        has typed and might not have been sent down to the :class:`Row` yet. After you've done that,
        stop the editing mechanism.
        """
    

SortDescriptor = namedtuple('SortDescriptor', 'column desc')
class GUITable(Table, GUIObject):
    """Cross-toolkit GUI-enabled table view.
    
    Represents a UI element presenting the user with a sortable, selectable, possibly editable,
    table view.
    
    Behaves like the :class:`Table` which it subclasses, but is more focused on being the presenter
    of some model data to its :attr:`.GUIObject.view`. There's a :meth:`refresh`
    mechanism which ensures fresh data while preserving sorting order and selection. There's also an
    editing mechanism which tracks whether (and which) row is being edited (or added) and
    save/cancel edits when appropriate.
    
    Subclasses :class:`Table` and :class:`.GUIObject`. Expected view:
    :class:`GUITableView`.
    """
    def __init__(self):
        GUIObject.__init__(self)
        Table.__init__(self)
        #: The row being currently edited by the user. ``None`` if no edit is taking place.
        self.edited = None
        self._sort_descriptor = None
    
    #--- Virtual
    def _do_add(self):
        """(Virtual) Creates a new row, adds it in the table.
        
        Returns ``(row, insert_index)``.
        """
        raise NotImplementedError()
    
    def _do_delete(self):
        """(Virtual) Delete the selected rows.
        """
        pass
    
    def _fill(self):
        """(Virtual/Required) Fills the table with all the rows that this table is supposed to have.
        
        Called by :meth:`refresh`. Does nothing by default.
        """
        pass
    
    def _is_edited_new(self):
        """(Virtual) Returns whether the currently edited row should be considered "new".
        
        This is used in :meth:`cancel_edits` to know whether the cancellation of the edit means a
        revert of the row's value or the removal of the row.
        
        By default, always false.
        """
        return False
    
    def _restore_selection(self, previous_selection):
        """(Virtual) Restores row selection after a contents-changing operation.
        
        Before each contents changing operation, we store our previously selected indexes because in
        many cases, such as in :meth:`refresh`, our selection will be lost. After the operation is
        over, we call this method with our previously selected indexes (in ``previous_selection``).
        
        The default behavior is (if we indeed have an empty :attr:`.selected_indexes`) to re-select
        ``previous_selection``. If it was empty, we select the last row of the table.
        
        This behavior can, of course, be overriden.
        """
        if not self.selected_indexes:
            if previous_selection:
                self.select(previous_selection)
            else:
                self.select([len(self) - 1])
    
    #--- Public
    def add(self):
        """Add a new row in edit mode.
        
        Requires :meth:`do_add` to be implemented. The newly added row will be selected and in edit
        mode.
        """
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
        """Returns whether the cell at ``row_index`` and ``column_name`` can be edited.
        
        A row is, by default, editable as soon as it has an attr with the same name as `column`.
        If :meth:`Row.can_edit` returns False, the row is not editable at all. You can set
        editability of rows at the attribute level with can_edit_* properties.
        
        Mostly just a shortcut to :meth:`Row.can_edit_cell`.
        """
        row = self[row_index]
        return row.can_edit_cell(column_name)
    
    def cancel_edits(self):
        """Cancels the current edit operation.
        
        If there's an :attr:`edited` row, it will be re-initialized (with :meth:`Row.load`).
        """
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
        """Delete the currently selected rows.
        
        Requires :meth:`_do_delete` for this to have any effect on the model. Cancels editing if
        relevant.
        """
        self.view.stop_editing()
        if self.edited is not None:
            self.cancel_edits()
            return
        if self:
            self._do_delete()
    
    def refresh(self, refresh_view=True):
        """Empty the table and re-create its rows.
        
        :meth:`_fill` is called after we emptied the table to create our rows. Previous sort order
        will be preserved, regardless of the order in which the rows were filled. If there was any
        edit operation taking place, it's cancelled.
        
        :param bool refresh_view: Whether we tell our view to refresh after our refill operation.
                                  Most of the time, it's what we want, but there's some cases where
                                  we don't.
        """
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
        """Commit user edits to the model.
        
        This is done by calling :meth:`Row.save`.
        """
        if self.edited is None:
            return
        row = self.edited
        self.edited = None
        row.save()
    
    def sort_by(self, column_name, desc=False):
        """Sort table by ``column_name``.
        
        Overrides :meth:`Table.sort_by`. After having performed sorting, calls
        :meth:`~.Selectable._update_selection` to give you the chance,
        if appropriate, to update your selected indexes according to, maybe, the selection that you
        have in your model.
        
        Then, we refresh our view.
        """
        Table.sort_by(self, column_name=column_name, desc=desc)
        self._sort_descriptor = SortDescriptor(column_name, desc)
        self._update_selection()
        self.view.refresh()
    

class Row:
    """Represents a row in a :class:`Table`.
    
    It holds multiple values to be represented through columns. It's its role to prepare data
    fetched from model instances into ready-to-present-in-a-table fashion. You will do this in
    :meth:`load`.
    
    When you do this, you'll put the result into arbitrary attributes, which will later be fetched
    by your table for presentation to the user.
    
    You can organize your attributes in whatever way you want, but there's a convention you can
    follow if you want to minimize subclassing and use default behavior:
    
    1. Attribute name = column name. If your attribute is ``foobar``, whenever we refer to
       ``column_name``, you refer to that attribute with the column name ``foobar``.
    2. Public attributes are for *formatted* value, that is, user readable strings.
    3. Underscore prefix is the unformatted (computable) value. For example, you could have
       ``_foobar`` at ``42`` and ``foobar`` at ``"42 seconds"`` (what you present to the user).
    4. Unformatted values are used for sorting.
    5. If your column name is a python keyword, add an underscore suffix (``from_``).
    
    Of course, this is only default behavior. This can be overriden.
    """
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
        """(Virtual) Whether the whole row can be edited.
        
        By default, always returns ``True``. This is for the *whole* row. For individual cells, it's
        :meth:`can_edit_cell`.
        """
        return True
    
    def load(self):
        """(Virtual/Required) Loads up values from the model to be presented in the table.
        
        Usually, our model instances contain values that are not quite ready for display. If you
        have number formatting, display calculations and other whatnots to perform, you do it here
        and then you put the result in an arbitrary attribute of the row.
        """
        raise NotImplementedError()
    
    def save(self):
        """(Virtual/Required) Saves user edits into your model.
        
        If your table is editable, this is called when the user commits his changes. Usually, these
        are typed up stuff, or selected indexes. You have to do proper parsing and reference
        linking, and save that stuff into your model.
        """
        raise NotImplementedError()
    
    def sort_key_for_column(self, column_name):
        """(Virtual) Return the value that is to be used to sort by column ``column_name``.
        
        By default, looks for an attribute with the same name as ``column_name``, but with an
        underscore prefix ("unformatted value"). If there's none, tries without the underscore. If
        there's none, raises ``AttributeError``.
        """
        try:
            return getattr(self, '_' + column_name)
        except AttributeError:
            return getattr(self, column_name)
    
    #--- Public
    def can_edit_cell(self, column_name):
        """Returns whether cell for column ``column_name`` can be edited.
        
        By the default, the check is done in many steps:
        
        1. We check whether the whole row can be edited with :meth:`can_edit`. If it can't, the cell
           can't either.
        2. If the column doesn't exist as an attribute, we can't edit.
        3. If we have an attribute ``can_edit_<column_name>``, return that.
        4. Check if our attribute is a property. If it's not, it's not editable.
        5. If our attribute is in fact a property, check whether the property is "settable" (has a
           ``fset`` method). The cell is editable only if the property is "settable".
        """
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
        """Get cell value for ``attrname``.
        
        By default, does a simple ``getattr()``, but it is used to allow subclasses to have
        alternative value storage mechanisms.
        """
        if attrname == 'from':
           attrname = 'from_'
        return getattr(self, attrname)
    
    def set_cell_value(self, attrname, value):
        """Set cell value to ``value`` for ``attrname``.
        
        By default, does a simple ``setattr()``, but it is used to allow subclasses to have
        alternative value storage mechanisms.
        """
        if attrname == 'from':
            attrname = 'from_'
        setattr(self, attrname, value)
    
