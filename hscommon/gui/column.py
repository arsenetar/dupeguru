# Created By: Virgil Dupras
# Created On: 2010-07-25
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import copy

from .base import GUIObject

class Column:
    """Holds column attributes such as its name, width, visibility, etc.
    
    These attributes are then used to correctly configure the column on the "view" side.
    """
    def __init__(self, name, display='', visible=True, optional=False):
        #: "programmatical" (not for display) name. Used as a reference in a couple of place, such
        #: as :meth:`Columns.column_by_name`.
        self.name = name
        #: Immutable index of the column. Doesn't change even when columns are re-ordered. Used in
        #: :meth:`Columns.column_by_index`.
        self.logical_index = 0
        #: Index of the column in the ordered set of columns.
        self.ordered_index = 0
        #: Width of the column.
        self.width = 0
        #: Default width of the column. This value usually depends on the platform and is set on
        #: columns initialisation. It will be used if column restoration doesn't contain any
        #: "remembered" widths.
        self.default_width = 0
        #: Display name (title) of the column.
        self.display = display
        #: Whether the column is visible.
        self.visible = visible
        #: Whether the column is visible by default. It will be used if column restoration doesn't
        #: contain any "remembered" widths.
        self.default_visible = visible
        #: Whether the column can have :attr:`visible` set to false.
        self.optional = optional
    
class ColumnsView:
    """Expected interface for :class:`Columns`'s view.
    
    *Not actually used in the code. For documentation purposes only.*
    
    Our view, the columns controller of a table or outline, is expected to properly respond to
    callbacks.
    """
    def restore_columns(self):
        """Update all columns according to the model.
        
        When this is called, our view has to update the columns title, order and visibility of all
        columns.
        """
    
    def set_column_visible(self, colname, visible):
        """Update visibility of column ``colname``.
        
        Called when the user toggles the visibility of a column, we must update the column
        ``colname``'s visibility status to ``visible``.
        """

class PrefAccessInterface:
    """Expected interface for :class:`Columns`'s prefaccess.
    
    *Not actually used in the code. For documentation purposes only.*
    """
    def get_default(self, key, fallback_value):
        """Retrieve the value for ``key`` in the currently running app's preference store.
        
        If the key doesn't exist, return ``fallback_value``.
        """
    
    def set_default(self, key, value):
        """Set the value ``value`` for ``key`` in the currently running app's preference store.
        """
    
class Columns(GUIObject):
    """Cross-toolkit GUI-enabled column set for tables or outlines.
    
    Manages a column set's order, visibility and width. We also manage the persistence of these
    attributes so that we can restore them on the next run.
    
    Subclasses :class:`.GUIObject`. Expected view: :class:`ColumnsView`.
    
    :param table: The table the columns belong to. It's from there that we retrieve our column
                  configuration and it must have a ``COLUMNS`` attribute which is a list of
                  :class:`Column`. We also call :meth:`~.GUITable.save_edits` on it from time to
                  time. Technically, this argument can also be a tree, but there's probably some
                  sorting in the code to do to support this option cleanly.
    :param prefaccess: An object giving access to user preferences for the currently running app.
                       We use this to make column attributes persistent. Must follow
                       :class:`PrefAccessInterface`.
    :param str savename: The name under which column preferences will be saved. This name is in fact
                         a prefix. Preferences are saved under more than one name, but they will all
                         have that same prefix.
    """
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
        """Return the :class:`Column` having the :attr:`~Column.logical_index` ``index``.
        """
        return self.column_list[index]
    
    def column_by_name(self, name):
        """Return the :class:`Column` having the :attr:`~Column.name` ``name``.
        """
        return self.coldata[name]
    
    def columns_count(self):
        """Returns the number of columns in our set.
        """
        return len(self.column_list)
    
    def column_display(self, colname):
        """Returns display name for column named ``colname``, or ``''`` if there's none.
        """
        return self._get_colname_attr(colname, 'display', '')
    
    def column_is_visible(self, colname):
        """Returns visibility for column named ``colname``, or ``True`` if there's none.
        """
        return self._get_colname_attr(colname, 'visible', True)
    
    def column_width(self, colname):
        """Returns width for column named ``colname``, or ``0`` if there's none.
        """
        return self._get_colname_attr(colname, 'width', 0)
    
    def columns_to_right(self, colname):
        """Returns the list of all columns to the right of ``colname``.
        
        "right" meaning "having a higher :attr:`Column.ordered_index`" in our left-to-right
        civilization.
        """
        column = self.coldata[colname]
        index = column.ordered_index
        return [col.name for col in self.column_list if (col.visible and col.ordered_index > index)]
    
    def menu_items(self):
        """Returns a list of items convenient for quick visibility menu generation.
        
        Returns a list of ``(display_name, is_marked)`` items for each optional column in the
        current view (``is_marked`` means that it's visible).
        
        You can use this to generate a menu to let the user toggle the visibility of an optional
        column. That is why we only show optional column, because the visibility of mandatory
        columns can't be toggled.
        """
        return [(c.display, c.visible) for c in self._optional_columns()]
    
    def move_column(self, colname, index):
        """Moves column ``colname`` to ``index``.
        
        The column will be placed just in front of the column currently having that index, or to the
        end of the list if there's none.
        """
        colnames = self.colnames
        colnames.remove(colname)
        colnames.insert(index, colname)
        self.set_column_order(colnames)
    
    def reset_to_defaults(self):
        """Reset all columns' width and visibility to their default values.
        """
        self.set_column_order([col.name for col in self.column_list])
        for col in self._optional_columns():
            col.visible = col.default_visible
            col.width = col.default_width
        self.view.restore_columns()
    
    def resize_column(self, colname, newwidth):
        """Set column ``colname``'s width to ``newwidth``.
        """
        self._set_colname_attr(colname, 'width', newwidth)
    
    def restore_columns(self):
        """Restore's column persistent attributes from the last :meth:`save_columns`.
        """
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
        """Save column attributes in persistent storage for restoration in :meth:`restore_columns`.
        """
        if not (self.prefaccess and self.savename and self.coldata):
            return
        for col in self.column_list:
            pref_name = '{}.Columns.{}'.format(self.savename, col.name)
            coldata = {'index': col.ordered_index, 'width': col.width}
            if col.optional:
                coldata['visible'] = col.visible
            self.prefaccess.set_default(pref_name, coldata)
    
    def set_column_order(self, colnames):
        """Change the columns order so it matches the order in ``colnames``.
        
        :param colnames: A list of column names in the desired order.
        """
        colnames = (name for name in colnames if name in self.coldata)
        for i, colname in enumerate(colnames):
            col = self.coldata[colname]
            col.ordered_index = i
    
    def set_column_visible(self, colname, visible):
        """Set the visibility of column ``colname``.
        """
        self.table.save_edits() # the table on the GUI side will stop editing when the columns change
        self._set_colname_attr(colname, 'visible', visible)
        self.view.set_column_visible(colname, visible)
    
    def set_default_width(self, colname, width):
        """Set the default width or column ``colname``.
        """
        self._set_colname_attr(colname, 'default_width', width)
    
    def toggle_menu_item(self, index):
        """Toggles the visibility of an optional column.
        
        You know, that optional column menu you've generated in :meth:`menu_items`? Well, ``index``
        is the index of them menu item in *that* menu that the user has clicked on to toggle it.
        
        Returns whether the column in question ends up being visible or not.
        """
        col = self._optional_columns()[index]
        self.set_column_visible(col.name, not col.visible)
        return col.visible
    
    #--- Properties
    @property
    def ordered_columns(self):
        """List of :class:`Column` in visible order.
        """
        return [col for col in sorted(self.column_list, key=lambda col: col.ordered_index)]
    
    @property
    def colnames(self):
        """List of column names in visible order.
        """
        return [col.name for col in self.ordered_columns]
    
