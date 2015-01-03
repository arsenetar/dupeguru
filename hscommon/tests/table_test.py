# Created By: Virgil Dupras
# Created On: 2008-08-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import CallLogger, eq_
from ..gui.table import Table, GUITable, Row

class TestRow(Row):
    def __init__(self, table, index, is_new=False):
        Row.__init__(self, table)
        self.is_new = is_new
        self._index = index
    
    def load(self):
        pass
    
    def save(self):
        self.is_new = False
    
    @property
    def index(self):
        return self._index
    

class TestGUITable(GUITable):
    def __init__(self, rowcount):
        GUITable.__init__(self)
        self.view = CallLogger()
        self.rowcount = rowcount
        self.updated_rows = None
    
    def _do_add(self):
        return TestRow(self, len(self), is_new=True), len(self)
    
    def _is_edited_new(self):
        return self.edited is not None and self.edited.is_new
    
    def _fill(self):
        for i in range(self.rowcount):
            self.append(TestRow(self, i))
    
    def _update_selection(self):
        self.updated_rows = self.selected_rows[:]
    

def table_with_footer():
    table = Table()
    table.append(TestRow(table, 0))
    footer = TestRow(table, 1)
    table.footer = footer
    return table, footer

def table_with_header():
    table = Table()
    table.append(TestRow(table, 1))
    header = TestRow(table, 0)
    table.header = header
    return table, header

#--- Tests
def test_allow_edit_when_attr_is_property_with_fset():
    # When a row has a property that has a fset, by default, make that cell editable.
    class TestRow(Row):
        @property
        def foo(self):
            pass
        @property
        def bar(self):
            pass
        @bar.setter
        def bar(self, value):
            pass
    
    row = TestRow(Table())
    assert row.can_edit_cell('bar')
    assert not row.can_edit_cell('foo')
    assert not row.can_edit_cell('baz') # doesn't exist, can't edit

def test_can_edit_prop_has_priority_over_fset_checks():
    # When a row has a cen_edit_* property, it's the result of that property that is used, not the
    # result of a fset check.
    class TestRow(Row):
        @property
        def bar(self):
            pass
        @bar.setter
        def bar(self, value):
            pass
        can_edit_bar = False
    
    row = TestRow(Table())
    assert not row.can_edit_cell('bar')

def test_in():
    # When a table is in a list, doing "in list" with another instance returns false, even if
    # they're the same as lists.
    table = Table()
    some_list = [table]
    assert Table() not in some_list

def test_footer_del_all():
    # Removing all rows doesn't crash when doing the footer check.
    table, footer = table_with_footer()
    del table[:]
    assert table.footer is None

def test_footer_del_row():
    # Removing the footer row sets it to None
    table, footer = table_with_footer()
    del table[-1]
    assert table.footer is None
    eq_(len(table), 1)

def test_footer_is_appened_to_table():
    # A footer is appended at the table's bottom
    table, footer = table_with_footer()
    eq_(len(table), 2)
    assert table[1] is footer

def test_footer_remove():
    # remove() on footer sets it to None
    table, footer = table_with_footer()
    table.remove(footer)
    assert table.footer is None

def test_footer_replaces_old_footer():
    table, footer = table_with_footer()
    other = Row(table)
    table.footer = other
    assert table.footer is other
    eq_(len(table), 2)
    assert table[1] is other

def test_footer_rows_and_row_count():
    # rows() and row_count() ignore footer.
    table, footer = table_with_footer()
    eq_(table.row_count, 1)
    eq_(table.rows, table[:-1])

def test_footer_setting_to_none_removes_old_one():
    table, footer = table_with_footer()
    table.footer = None
    assert table.footer is None
    eq_(len(table), 1)

def test_footer_stays_there_on_append():
    # Appending another row puts it above the footer
    table, footer = table_with_footer()
    table.append(Row(table))
    eq_(len(table), 3)
    assert table[2] is footer

def test_footer_stays_there_on_insert():
    # Inserting another row puts it above the footer
    table, footer = table_with_footer()
    table.insert(3, Row(table))
    eq_(len(table), 3)
    assert table[2] is footer

def test_header_del_all():
    # Removing all rows doesn't crash when doing the header check.
    table, header = table_with_header()
    del table[:]
    assert table.header is None

def test_header_del_row():
    # Removing the header row sets it to None
    table, header = table_with_header()
    del table[0]
    assert table.header is None
    eq_(len(table), 1)

def test_header_is_inserted_in_table():
    # A header is inserted at the table's top
    table, header = table_with_header()
    eq_(len(table), 2)
    assert table[0] is header

def test_header_remove():
    # remove() on header sets it to None
    table, header = table_with_header()
    table.remove(header)
    assert table.header is None

def test_header_replaces_old_header():
    table, header = table_with_header()
    other = Row(table)
    table.header = other
    assert table.header is other
    eq_(len(table), 2)
    assert table[0] is other

def test_header_rows_and_row_count():
    # rows() and row_count() ignore header.
    table, header = table_with_header()
    eq_(table.row_count, 1)
    eq_(table.rows, table[1:])

def test_header_setting_to_none_removes_old_one():
    table, header = table_with_header()
    table.header = None
    assert table.header is None
    eq_(len(table), 1)

def test_header_stays_there_on_insert():
    # Inserting another row at the top puts it below the header
    table, header = table_with_header()
    table.insert(0, Row(table))
    eq_(len(table), 3)
    assert table[0] is header

def test_refresh_view_on_refresh():
    # If refresh_view is not False, we refresh the table's view on refresh()
    table = TestGUITable(1)
    table.refresh()
    table.view.check_gui_calls(['refresh'])
    table.view.clear_calls()
    table.refresh(refresh_view=False)
    table.view.check_gui_calls([])

def test_restore_selection():
    # By default, after a refresh, selection goes on the last row
    table = TestGUITable(10)
    table.refresh()
    eq_(table.selected_indexes, [9])

def test_restore_selection_after_cancel_edits():
    # _restore_selection() is called after cancel_edits(). Previously, only _update_selection would
    # be called.
    class MyTable(TestGUITable):
        def _restore_selection(self, previous_selection):
            self.selected_indexes = [6]
    
    table = MyTable(10)
    table.refresh()
    table.add()
    table.cancel_edits()
    eq_(table.selected_indexes, [6])

def test_restore_selection_with_previous_selection():
    # By default, we try to restore the selection that was there before a refresh
    table = TestGUITable(10)
    table.refresh()
    table.selected_indexes = [2, 4]
    table.refresh()
    eq_(table.selected_indexes, [2, 4])

def test_restore_selection_custom():
    # After a _fill() called, the virtual _restore_selection() is called so that it's possible for a
    # GUITable subclass to customize its post-refresh selection behavior.
    class MyTable(TestGUITable):
        def _restore_selection(self, previous_selection):
            self.selected_indexes = [6]
        
    table = MyTable(10)
    table.refresh()
    eq_(table.selected_indexes, [6])

def test_row_cell_value():
    # *_cell_value() correctly mangles attrnames that are Python reserved words.
    row = Row(Table())
    row.from_ = 'foo'
    eq_(row.get_cell_value('from'), 'foo')
    row.set_cell_value('from', 'bar')
    eq_(row.get_cell_value('from'), 'bar')

def test_sort_table_also_tries_attributes_without_underscores():
    # When determining a sort key, after having unsuccessfully tried the attribute with the,
    # underscore, try the one without one.
    table = Table()
    row1 = Row(table)
    row1._foo = 'a' # underscored attr must be checked first
    row1.foo = 'b'
    row1.bar = 'c'
    row2 = Row(table)
    row2._foo = 'b'
    row2.foo = 'a'
    row2.bar = 'b'
    table.append(row1)
    table.append(row2)
    table.sort_by('foo')
    assert table[0] is row1
    assert table[1] is row2
    table.sort_by('bar')
    assert table[0] is row2
    assert table[1] is row1

def test_sort_table_updates_selection():
    table = TestGUITable(10)
    table.refresh()
    table.select([2, 4])
    table.sort_by('index', desc=True)
    # Now, the updated rows should be 7 and 5
    eq_(len(table.updated_rows), 2)
    r1, r2 = table.updated_rows
    eq_(r1.index, 7)
    eq_(r2.index, 5)

def test_sort_table_with_footer():
    # Sorting a table with a footer keeps it at the bottom
    table, footer = table_with_footer()
    table.sort_by('index', desc=True)
    assert table[-1] is footer

def test_sort_table_with_header():
    # Sorting a table with a header keeps it at the top
    table, header = table_with_header()
    table.sort_by('index', desc=True)
    assert table[0] is header