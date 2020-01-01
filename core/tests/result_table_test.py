# Created By: Virgil Dupras
# Created On: 2013-07-28
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from .base import TestApp, GetTestGroups


def app_with_results():
    app = TestApp()
    objects, matches, groups = GetTestGroups()
    app.app.results.groups = groups
    app.rtable.refresh()
    return app


def test_delta_flags_delta_mode_off():
    app = app_with_results()
    # When the delta mode is off, we never have delta values flags
    app.rtable.delta_values = False
    # Ref file, always false anyway
    assert not app.rtable[0].is_cell_delta("size")
    # False because delta mode is off
    assert not app.rtable[1].is_cell_delta("size")


def test_delta_flags_delta_mode_on_delta_columns():
    # When the delta mode is on, delta columns always have a delta flag, except for ref rows
    app = app_with_results()
    app.rtable.delta_values = True
    # Ref file, always false anyway
    assert not app.rtable[0].is_cell_delta("size")
    # But for a dupe, the flag is on
    assert app.rtable[1].is_cell_delta("size")


def test_delta_flags_delta_mode_on_non_delta_columns():
    # When the delta mode is on, non-delta columns have a delta flag if their value differs from
    # their ref.
    app = app_with_results()
    app.rtable.delta_values = True
    # "bar bleh" != "foo bar", flag on
    assert app.rtable[1].is_cell_delta("name")
    # "ibabtu" row, but it's a ref, flag off
    assert not app.rtable[3].is_cell_delta("name")
    # "ibabtu" == "ibabtu", flag off
    assert not app.rtable[4].is_cell_delta("name")


def test_delta_flags_delta_mode_on_non_delta_columns_case_insensitive():
    # Comparison that occurs for non-numeric columns to check whether they're delta is case
    # insensitive
    app = app_with_results()
    app.app.results.groups[1].ref.name = "ibAbtu"
    app.app.results.groups[1].dupes[0].name = "IBaBTU"
    app.rtable.delta_values = True
    # "ibAbtu" == "IBaBTU", flag off
    assert not app.rtable[4].is_cell_delta("name")
