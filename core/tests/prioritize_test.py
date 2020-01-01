# Created By: Virgil Dupras
# Created On: 2011/09/07
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os.path as op
from itertools import combinations

from .base import TestApp, NamedObject, with_app, eq_
from ..engine import Group, Match

no = NamedObject


def app_with_dupes(dupes):
    # Creates an app with specified dupes. dupes is a list of lists, each list in the list being
    # a dupe group. We cheat a little bit by creating dupe groups manually instead of running a
    # dupe scan, but it simplifies the test code quite a bit
    app = TestApp()
    groups = []
    for dupelist in dupes:
        g = Group()
        for dupe1, dupe2 in combinations(dupelist, 2):
            g.add_match(Match(dupe1, dupe2, 100))
        groups.append(g)
    app.app.results.groups = groups
    app.app._results_changed()
    return app


# ---
def app_normal_results():
    # Just some results, with different extensions and size, for good measure.
    dupes = [
        [
            no("foo1.ext1", size=1, folder="folder1"),
            no("foo2.ext2", size=2, folder="folder2"),
        ],
    ]
    return app_with_dupes(dupes)


@with_app(app_normal_results)
def test_kind_subcrit(app):
    # The subcriteria of the "Kind" criteria is a list of extensions contained in the dupes.
    app.select_pri_criterion("Kind")
    eq_(app.pdialog.criteria_list[:], ["ext1", "ext2"])


@with_app(app_normal_results)
def test_kind_reprioritization(app):
    # Just a simple test of the system as a whole.
    # select a criterion, and perform re-prioritization and see if it worked.
    app.select_pri_criterion("Kind")
    app.pdialog.criteria_list.select([1])  # ext2
    app.pdialog.add_selected()
    app.pdialog.perform_reprioritization()
    eq_(app.rtable[0].data["name"], "foo2.ext2")


@with_app(app_normal_results)
def test_folder_subcrit(app):
    app.select_pri_criterion("Folder")
    eq_(app.pdialog.criteria_list[:], ["folder1", "folder2"])


@with_app(app_normal_results)
def test_folder_reprioritization(app):
    app.select_pri_criterion("Folder")
    app.pdialog.criteria_list.select([1])  # folder2
    app.pdialog.add_selected()
    app.pdialog.perform_reprioritization()
    eq_(app.rtable[0].data["name"], "foo2.ext2")


@with_app(app_normal_results)
def test_prilist_display(app):
    # The prioritization list displays selected criteria correctly.
    app.select_pri_criterion("Kind")
    app.pdialog.criteria_list.select([1])  # ext2
    app.pdialog.add_selected()
    app.select_pri_criterion("Folder")
    app.pdialog.criteria_list.select([1])  # folder2
    app.pdialog.add_selected()
    app.select_pri_criterion("Size")
    app.pdialog.criteria_list.select([1])  # Lowest
    app.pdialog.add_selected()
    expected = [
        "Kind (ext2)",
        "Folder (folder2)",
        "Size (Lowest)",
    ]
    eq_(app.pdialog.prioritization_list[:], expected)


@with_app(app_normal_results)
def test_size_subcrit(app):
    app.select_pri_criterion("Size")
    eq_(app.pdialog.criteria_list[:], ["Highest", "Lowest"])


@with_app(app_normal_results)
def test_size_reprioritization(app):
    app.select_pri_criterion("Size")
    app.pdialog.criteria_list.select([0])  # highest
    app.pdialog.add_selected()
    app.pdialog.perform_reprioritization()
    eq_(app.rtable[0].data["name"], "foo2.ext2")


@with_app(app_normal_results)
def test_reorder_prioritizations(app):
    app.add_pri_criterion("Kind", 0)  # ext1
    app.add_pri_criterion("Kind", 1)  # ext2
    app.pdialog.prioritization_list.move_indexes([1], 0)
    expected = [
        "Kind (ext2)",
        "Kind (ext1)",
    ]
    eq_(app.pdialog.prioritization_list[:], expected)


@with_app(app_normal_results)
def test_remove_crit_from_list(app):
    app.add_pri_criterion("Kind", 0)
    app.add_pri_criterion("Kind", 1)
    app.pdialog.prioritization_list.select(0)
    app.pdialog.remove_selected()
    expected = [
        "Kind (ext2)",
    ]
    eq_(app.pdialog.prioritization_list[:], expected)


@with_app(app_normal_results)
def test_add_crit_without_selection(app):
    # Adding a criterion without having made a selection doesn't cause a crash.
    app.pdialog.add_selected()  # no crash


# ---
def app_one_name_ends_with_number():
    dupes = [
        [no("foo.ext"), no("foo1.ext")],
    ]
    return app_with_dupes(dupes)


@with_app(app_one_name_ends_with_number)
def test_filename_reprioritization(app):
    app.add_pri_criterion("Filename", 0)  # Ends with a number
    app.pdialog.perform_reprioritization()
    eq_(app.rtable[0].data["name"], "foo1.ext")


# ---
def app_with_subfolders():
    dupes = [
        [no("foo1", folder="baz"), no("foo2", folder="foo/bar")],
        [no("foo3", folder="baz"), no("foo4", folder="foo")],
    ]
    return app_with_dupes(dupes)


@with_app(app_with_subfolders)
def test_folder_crit_is_sorted(app):
    # Folder subcriteria are sorted.
    app.select_pri_criterion("Folder")
    eq_(app.pdialog.criteria_list[:], ["baz", "foo", op.join("foo", "bar")])


@with_app(app_with_subfolders)
def test_folder_crit_includes_subfolders(app):
    # When selecting a folder crit, dupes in a subfolder are also considered as affected by that
    # crit.
    app.add_pri_criterion("Folder", 1)  # foo
    app.pdialog.perform_reprioritization()
    # Both foo and foo/bar dupes will be prioritized
    eq_(app.rtable[0].data["name"], "foo2")
    eq_(app.rtable[2].data["name"], "foo4")


@with_app(app_with_subfolders)
def test_display_something_on_empty_extensions(app):
    # When there's no extension, display "None" instead of nothing at all.
    app.select_pri_criterion("Kind")
    eq_(app.pdialog.criteria_list[:], ["None"])


# ---
def app_one_name_longer_than_the_other():
    dupes = [
        [no("shortest.ext"), no("loooongest.ext")],
    ]
    return app_with_dupes(dupes)


@with_app(app_one_name_longer_than_the_other)
def test_longest_filename_prioritization(app):
    app.add_pri_criterion("Filename", 2)  # Longest
    app.pdialog.perform_reprioritization()
    eq_(app.rtable[0].data["name"], "loooongest.ext")
