# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import eq_, callcounter, CallLogger
from ..gui.selectable_list import SelectableList, GUISelectableList

def test_in():
    # When a SelectableList is in a list, doing "in list" with another instance returns false, even
    # if they're the same as lists.
    sl = SelectableList()
    some_list = [sl]
    assert SelectableList() not in some_list

def test_selection_range():
    # selection is correctly adjusted on deletion
    sl = SelectableList(['foo', 'bar', 'baz'])
    sl.selected_index = 3
    eq_(sl.selected_index, 2)
    del sl[2]
    eq_(sl.selected_index, 1)

def test_update_selection_called():
    # _update_selection_is called after a change in selection. However, we only do so on select()
    # calls. I follow the old behavior of the Table class. At the moment, I don't quite remember
    # why there was a specific select() method for triggering _update_selection(), but I think I
    # remember there was a reason, so I keep it that way.
    sl = SelectableList(['foo', 'bar'])
    sl._update_selection = callcounter()
    sl.select(1)
    eq_(sl._update_selection.callcount, 1)
    sl.selected_index = 0
    eq_(sl._update_selection.callcount, 1) # no call

def test_guicalls():
    # A GUISelectableList appropriately calls its view.
    sl = GUISelectableList(['foo', 'bar'])
    sl.view = CallLogger()
    sl.view.check_gui_calls(['refresh']) # Upon setting the view, we get a call to refresh()
    sl[1] = 'baz'
    sl.view.check_gui_calls(['refresh'])
    sl.append('foo')
    sl.view.check_gui_calls(['refresh'])
    del sl[2]
    sl.view.check_gui_calls(['refresh'])
    sl.remove('baz')
    sl.view.check_gui_calls(['refresh'])
    sl.insert(0, 'foo')
    sl.view.check_gui_calls(['refresh'])
    sl.select(1)
    sl.view.check_gui_calls(['update_selection'])
    # XXX We have to give up on this for now because of a breakage it causes in the tables.
    # sl.select(1) # don't update when selection stays the same
    # gui.check_gui_calls([])

def test_search_by_prefix():
    sl = SelectableList(['foo', 'bAr', 'baZ'])
    eq_(sl.search_by_prefix('b'), 1)
    eq_(sl.search_by_prefix('BA'), 1)
    eq_(sl.search_by_prefix('BAZ'), 2)
    eq_(sl.search_by_prefix('BAZZ'), -1)