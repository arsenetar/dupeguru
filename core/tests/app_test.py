# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import os.path as op
import logging

import pytest
from pathlib import Path
import hscommon.conflict
import hscommon.util
from hscommon.testutil import eq_, log_calls
from hscommon.jobprogress.job import Job

from .base import TestApp
from .results_test import GetTestGroups
from .. import app, fs, engine
from ..scanner import ScanType


def add_fake_files_to_directories(directories, files):
    directories.get_files = lambda j=None: iter(files)
    directories._dirs.append("this is just so Scan() doesn't return 3")


class TestCaseDupeGuru:
    def test_apply_filter_calls_results_apply_filter(self, monkeypatch):
        dgapp = TestApp().app
        monkeypatch.setattr(dgapp.results, "apply_filter", log_calls(dgapp.results.apply_filter))
        dgapp.apply_filter("foo")
        eq_(2, len(dgapp.results.apply_filter.calls))
        call = dgapp.results.apply_filter.calls[0]
        assert call["filter_str"] is None
        call = dgapp.results.apply_filter.calls[1]
        eq_("foo", call["filter_str"])

    def test_apply_filter_escapes_regexp(self, monkeypatch):
        dgapp = TestApp().app
        monkeypatch.setattr(dgapp.results, "apply_filter", log_calls(dgapp.results.apply_filter))
        dgapp.apply_filter("()[]\\.|+?^abc")
        call = dgapp.results.apply_filter.calls[1]
        eq_("\\(\\)\\[\\]\\\\\\.\\|\\+\\?\\^abc", call["filter_str"])
        dgapp.apply_filter("(*)")  # In "simple mode", we want the * to behave as a wildcard
        call = dgapp.results.apply_filter.calls[3]
        eq_(r"\(.*\)", call["filter_str"])
        dgapp.options["escape_filter_regexp"] = False
        dgapp.apply_filter("(abc)")
        call = dgapp.results.apply_filter.calls[5]
        eq_("(abc)", call["filter_str"])

    def test_copy_or_move(self, tmpdir, monkeypatch):
        # The goal here is just to have a test for a previous blowup I had. I know my test coverage
        # for this unit is pathetic. What's done is done. My approach now is to add tests for
        # every change I want to make. The blowup was caused by a missing import.
        p = Path(str(tmpdir))
        p.joinpath("foo").touch()
        monkeypatch.setattr(
            hscommon.conflict,
            "smart_copy",
            log_calls(lambda source_path, dest_path: None),
        )
        # XXX This monkeypatch is temporary. will be fixed in a better monkeypatcher.
        monkeypatch.setattr(app, "smart_copy", hscommon.conflict.smart_copy)
        monkeypatch.setattr(os, "makedirs", lambda path: None)  # We don't want the test to create that fake directory
        dgapp = TestApp().app
        dgapp.directories.add_path(p)
        [f] = dgapp.directories.get_files()
        dgapp.copy_or_move(f, True, "some_destination", 0)
        eq_(1, len(hscommon.conflict.smart_copy.calls))
        call = hscommon.conflict.smart_copy.calls[0]
        eq_(call["dest_path"], Path("some_destination", "foo"))
        eq_(call["source_path"], f.path)

    def test_copy_or_move_clean_empty_dirs(self, tmpdir, monkeypatch):
        tmppath = Path(str(tmpdir))
        sourcepath = tmppath.joinpath("source")
        sourcepath.mkdir()
        sourcepath.joinpath("myfile").touch()
        app = TestApp().app
        app.directories.add_path(tmppath)
        [myfile] = app.directories.get_files()
        monkeypatch.setattr(app, "clean_empty_dirs", log_calls(lambda path: None))
        app.copy_or_move(myfile, False, tmppath.joinpath("dest"), 0)
        calls = app.clean_empty_dirs.calls
        eq_(1, len(calls))
        eq_(sourcepath, calls[0]["path"])

    def test_scan_with_objects_evaluating_to_false(self):
        class FakeFile(fs.File):
            def __bool__(self):
                return False

        # At some point, any() was used in a wrong way that made Scan() wrongly return 1
        app = TestApp().app
        f1, f2 = [FakeFile("foo") for _ in range(2)]
        f1.is_ref, f2.is_ref = (False, False)
        assert not (bool(f1) and bool(f2))
        add_fake_files_to_directories(app.directories, [f1, f2])
        app.start_scanning()  # no exception

    @pytest.mark.skipif("not hasattr(os, 'link')")
    def test_ignore_hardlink_matches(self, tmpdir):
        # If the ignore_hardlink_matches option is set, don't match files hardlinking to the same
        # inode.
        tmppath = Path(str(tmpdir))
        tmppath.joinpath("myfile").open("wt").write("foo")
        os.link(str(tmppath.joinpath("myfile")), str(tmppath.joinpath("hardlink")))
        app = TestApp().app
        app.directories.add_path(tmppath)
        app.options["scan_type"] = ScanType.CONTENTS
        app.options["ignore_hardlink_matches"] = True
        app.start_scanning()
        eq_(len(app.results.groups), 0)

    def test_rename_when_nothing_is_selected(self):
        # Issue #140
        # It's possible that rename operation has its selected row swept off from under it, thus
        # making the selected row None. Don't crash when it happens.
        dgapp = TestApp().app
        # selected_row is None because there's no result.
        assert not dgapp.result_table.rename_selected("foo")  # no crash


class TestCaseDupeGuruCleanEmptyDirs:
    @pytest.fixture
    def do_setup(self, request):
        monkeypatch = request.getfixturevalue("monkeypatch")
        monkeypatch.setattr(
            hscommon.util,
            "delete_if_empty",
            log_calls(lambda path, files_to_delete=[]: None),
        )
        # XXX This monkeypatch is temporary. will be fixed in a better monkeypatcher.
        monkeypatch.setattr(app, "delete_if_empty", hscommon.util.delete_if_empty)
        self.app = TestApp().app

    def test_option_off(self, do_setup):
        self.app.clean_empty_dirs(Path("/foo/bar"))
        eq_(0, len(hscommon.util.delete_if_empty.calls))

    def test_option_on(self, do_setup):
        self.app.options["clean_empty_dirs"] = True
        self.app.clean_empty_dirs(Path("/foo/bar"))
        calls = hscommon.util.delete_if_empty.calls
        eq_(1, len(calls))
        eq_(Path("/foo/bar"), calls[0]["path"])
        eq_([".DS_Store"], calls[0]["files_to_delete"])

    def test_recurse_up(self, do_setup, monkeypatch):
        # delete_if_empty must be recursively called up in the path until it returns False
        @log_calls
        def mock_delete_if_empty(path, files_to_delete=[]):
            return len(path.parts) > 1

        monkeypatch.setattr(hscommon.util, "delete_if_empty", mock_delete_if_empty)
        # XXX This monkeypatch is temporary. will be fixed in a better monkeypatcher.
        monkeypatch.setattr(app, "delete_if_empty", mock_delete_if_empty)
        self.app.options["clean_empty_dirs"] = True
        self.app.clean_empty_dirs(Path("not-empty/empty/empty"))
        calls = hscommon.util.delete_if_empty.calls
        eq_(3, len(calls))
        eq_(Path("not-empty/empty/empty"), calls[0]["path"])
        eq_(Path("not-empty/empty"), calls[1]["path"])
        eq_(Path("not-empty"), calls[2]["path"])


class TestCaseDupeGuruWithResults:
    @pytest.fixture
    def do_setup(self, request):
        app = TestApp()
        self.app = app.app
        self.objects, self.matches, self.groups = GetTestGroups()
        self.app.results.groups = self.groups
        self.dpanel = app.dpanel
        self.dtree = app.dtree
        self.rtable = app.rtable
        self.rtable.refresh()
        tmpdir = request.getfixturevalue("tmpdir")
        tmppath = Path(str(tmpdir))
        tmppath.joinpath("foo").mkdir()
        tmppath.joinpath("bar").mkdir()
        self.app.directories.add_path(tmppath)

    def test_get_objects(self, do_setup):
        objects = self.objects
        groups = self.groups
        r = self.rtable[0]
        assert r._group is groups[0]
        assert r._dupe is objects[0]
        r = self.rtable[1]
        assert r._group is groups[0]
        assert r._dupe is objects[1]
        r = self.rtable[4]
        assert r._group is groups[1]
        assert r._dupe is objects[4]

    def test_get_objects_after_sort(self, do_setup):
        objects = self.objects
        groups = self.groups[:]  # we need an un-sorted reference
        self.rtable.sort("name", False)
        r = self.rtable[1]
        assert r._group is groups[1]
        assert r._dupe is objects[4]

    def test_selected_result_node_paths_after_deletion(self, do_setup):
        # cases where the selected dupes aren't there are correctly handled
        self.rtable.select([1, 2, 3])
        self.app.remove_selected()
        # The first 2 dupes have been removed. The 3rd one is a ref. it stays there, in first pos.
        eq_(self.rtable.selected_indexes, [1])  # no exception

    def test_select_result_node_paths(self, do_setup):
        app = self.app
        objects = self.objects
        self.rtable.select([1, 2])
        eq_(len(app.selected_dupes), 2)
        assert app.selected_dupes[0] is objects[1]
        assert app.selected_dupes[1] is objects[2]

    def test_select_result_node_paths_with_ref(self, do_setup):
        app = self.app
        objects = self.objects
        self.rtable.select([1, 2, 3])
        eq_(len(app.selected_dupes), 3)
        assert app.selected_dupes[0] is objects[1]
        assert app.selected_dupes[1] is objects[2]
        assert app.selected_dupes[2] is self.groups[1].ref

    def test_select_result_node_paths_after_sort(self, do_setup):
        app = self.app
        objects = self.objects
        groups = self.groups[:]  # To keep the old order in memory
        self.rtable.sort("name", False)  # 0
        # Now, the group order is supposed to be reversed
        self.rtable.select([1, 2, 3])
        eq_(len(app.selected_dupes), 3)
        assert app.selected_dupes[0] is objects[4]
        assert app.selected_dupes[1] is groups[0].ref
        assert app.selected_dupes[2] is objects[1]

    def test_selected_powermarker_node_paths(self, do_setup):
        # app.selected_dupes is correctly converted into paths
        self.rtable.power_marker = True
        self.rtable.select([0, 1, 2])
        self.rtable.power_marker = False
        eq_(self.rtable.selected_indexes, [1, 2, 4])

    def test_selected_powermarker_node_paths_after_deletion(self, do_setup):
        # cases where the selected dupes aren't there are correctly handled
        app = self.app
        self.rtable.power_marker = True
        self.rtable.select([0, 1, 2])
        app.remove_selected()
        eq_(self.rtable.selected_indexes, [])  # no exception

    def test_select_powermarker_rows_after_sort(self, do_setup):
        app = self.app
        objects = self.objects
        self.rtable.power_marker = True
        self.rtable.sort("name", False)
        self.rtable.select([0, 1, 2])
        eq_(len(app.selected_dupes), 3)
        assert app.selected_dupes[0] is objects[4]
        assert app.selected_dupes[1] is objects[2]
        assert app.selected_dupes[2] is objects[1]

    def test_toggle_selected_mark_state(self, do_setup):
        app = self.app
        objects = self.objects
        app.toggle_selected_mark_state()
        eq_(app.results.mark_count, 0)
        self.rtable.select([1, 4])
        app.toggle_selected_mark_state()
        eq_(app.results.mark_count, 2)
        assert not app.results.is_marked(objects[0])
        assert app.results.is_marked(objects[1])
        assert not app.results.is_marked(objects[2])
        assert not app.results.is_marked(objects[3])
        assert app.results.is_marked(objects[4])

    def test_toggle_selected_mark_state_with_different_selected_state(self, do_setup):
        # When marking selected dupes with a heterogenous selection, mark all selected dupes. When
        # it's homogenous, simply toggle.
        app = self.app
        self.rtable.select([1])
        app.toggle_selected_mark_state()
        # index 0 is unmarkable, but we throw it in the bunch to be sure that it doesn't make the
        # selection heterogenoug when it shouldn't.
        self.rtable.select([0, 1, 4])
        app.toggle_selected_mark_state()
        eq_(app.results.mark_count, 2)
        app.toggle_selected_mark_state()
        eq_(app.results.mark_count, 0)

    def test_refresh_details_with_selected(self, do_setup):
        self.rtable.select([1, 4])
        eq_(self.dpanel.row(0), ("Filename", "bar bleh", "foo bar"))
        self.dpanel.view.check_gui_calls(["refresh"])
        self.rtable.select([])
        eq_(self.dpanel.row(0), ("Filename", "---", "---"))
        self.dpanel.view.check_gui_calls(["refresh"])

    def test_make_selected_reference(self, do_setup):
        app = self.app
        objects = self.objects
        groups = self.groups
        self.rtable.select([1, 4])
        app.make_selected_reference()
        assert groups[0].ref is objects[1]
        assert groups[1].ref is objects[4]

    def test_make_selected_reference_by_selecting_two_dupes_in_the_same_group(self, do_setup):
        app = self.app
        objects = self.objects
        groups = self.groups
        self.rtable.select([1, 2, 4])
        # Only [0, 0] and [1, 0] must go ref, not [0, 1] because it is a part of the same group
        app.make_selected_reference()
        assert groups[0].ref is objects[1]
        assert groups[1].ref is objects[4]

    def test_remove_selected(self, do_setup):
        app = self.app
        self.rtable.select([1, 4])
        app.remove_selected()
        eq_(len(app.results.dupes), 1)  # the first path is now selected
        app.remove_selected()
        eq_(len(app.results.dupes), 0)

    def test_add_directory_simple(self, do_setup):
        # There's already a directory in self.app, so adding another once makes 2 of em
        app = self.app
        # any other path that isn't a parent or child of the already added path
        otherpath = Path(op.dirname(__file__))
        app.add_directory(otherpath)
        eq_(len(app.directories), 2)

    def test_add_directory_already_there(self, do_setup):
        app = self.app
        otherpath = Path(op.dirname(__file__))
        app.add_directory(otherpath)
        app.add_directory(otherpath)
        eq_(len(app.view.messages), 1)
        assert "already" in app.view.messages[0]

    def test_add_directory_does_not_exist(self, do_setup):
        app = self.app
        app.add_directory("/does_not_exist")
        eq_(len(app.view.messages), 1)
        assert "exist" in app.view.messages[0]

    def test_ignore(self, do_setup):
        app = self.app
        self.rtable.select([4])  # The dupe of the second, 2 sized group
        app.add_selected_to_ignore_list()
        eq_(len(app.ignore_list), 1)
        self.rtable.select([1])  # first dupe of the 3 dupes group
        app.add_selected_to_ignore_list()
        # BOTH the ref and the other dupe should have been added
        eq_(len(app.ignore_list), 3)

    def test_purge_ignorelist(self, do_setup, tmpdir):
        app = self.app
        p1 = str(tmpdir.join("file1"))
        p2 = str(tmpdir.join("file2"))
        open(p1, "w").close()
        open(p2, "w").close()
        dne = "/does_not_exist"
        app.ignore_list.ignore(dne, p1)
        app.ignore_list.ignore(p2, dne)
        app.ignore_list.ignore(p1, p2)
        app.purge_ignore_list()
        eq_(1, len(app.ignore_list))
        assert app.ignore_list.are_ignored(p1, p2)
        assert not app.ignore_list.are_ignored(dne, p1)

    def test_only_unicode_is_added_to_ignore_list(self, do_setup):
        def fake_ignore(first, second):
            if not isinstance(first, str):
                self.fail()
            if not isinstance(second, str):
                self.fail()

        app = self.app
        app.ignore_list.ignore = fake_ignore
        self.rtable.select([4])
        app.add_selected_to_ignore_list()

    def test_cancel_scan_with_previous_results(self, do_setup):
        # When doing a scan with results being present prior to the scan, correctly invalidate the
        # results table.
        app = self.app
        app.JOB = Job(1, lambda *args, **kw: False)  # Cancels the task
        add_fake_files_to_directories(app.directories, self.objects)  # We want the scan to at least start
        app.start_scanning()  # will be cancelled immediately
        eq_(len(app.result_table), 0)

    def test_selected_dupes_after_removal(self, do_setup):
        # Purge the app's `selected_dupes` attribute when removing dupes, or else it might cause a
        # crash later with None refs.
        app = self.app
        app.results.mark_all()
        self.rtable.select([0, 1, 2, 3, 4])
        app.remove_marked()
        eq_(len(self.rtable), 0)
        eq_(app.selected_dupes, [])

    def test_dont_crash_on_delta_powermarker_dupecount_sort(self, do_setup):
        # Don't crash when sorting by dupe count or percentage while delta+powermarker are enabled.
        # Ref #238
        self.rtable.delta_values = True
        self.rtable.power_marker = True
        self.rtable.sort("dupe_count", False)
        # don't crash
        self.rtable.sort("percentage", False)
        # don't crash


class TestCaseDupeGuruRenameSelected:
    @pytest.fixture
    def do_setup(self, request):
        tmpdir = request.getfixturevalue("tmpdir")
        p = Path(str(tmpdir))
        p.joinpath("foo bar 1").touch()
        p.joinpath("foo bar 2").touch()
        p.joinpath("foo bar 3").touch()
        files = fs.get_files(p)
        for f in files:
            f.is_ref = False
        matches = engine.getmatches(files)
        groups = engine.get_groups(matches)
        g = groups[0]
        g.prioritize(lambda x: x.name)
        app = TestApp()
        app.app.results.groups = groups
        self.app = app.app
        self.rtable = app.rtable
        self.rtable.refresh()
        self.groups = groups
        self.p = p
        self.files = files

    def test_simple(self, do_setup):
        app = self.app
        g = self.groups[0]
        self.rtable.select([1])
        assert app.rename_selected("renamed")
        names = [p.name for p in self.p.glob("*")]
        assert "renamed" in names
        assert "foo bar 2" not in names
        eq_(g.dupes[0].name, "renamed")

    def test_none_selected(self, do_setup, monkeypatch):
        app = self.app
        g = self.groups[0]
        self.rtable.select([])
        monkeypatch.setattr(logging, "warning", log_calls(lambda msg: None))
        assert not app.rename_selected("renamed")
        msg = logging.warning.calls[0]["msg"]
        eq_("dupeGuru Warning: list index out of range", msg)
        names = [p.name for p in self.p.glob("*")]
        assert "renamed" not in names
        assert "foo bar 2" in names
        eq_(g.dupes[0].name, "foo bar 2")

    def test_name_already_exists(self, do_setup, monkeypatch):
        app = self.app
        g = self.groups[0]
        self.rtable.select([1])
        monkeypatch.setattr(logging, "warning", log_calls(lambda msg: None))
        assert not app.rename_selected("foo bar 1")
        msg = logging.warning.calls[0]["msg"]
        assert msg.startswith("dupeGuru Warning: 'foo bar 1' already exists in")
        names = [p.name for p in self.p.glob("*")]
        assert "foo bar 1" in names
        assert "foo bar 2" in names
        eq_(g.dupes[0].name, "foo bar 2")


class TestAppWithDirectoriesInTree:
    @pytest.fixture
    def do_setup(self, request):
        tmpdir = request.getfixturevalue("tmpdir")
        p = Path(str(tmpdir))
        p.joinpath("sub1").mkdir()
        p.joinpath("sub2").mkdir()
        p.joinpath("sub3").mkdir()
        app = TestApp()
        self.app = app.app
        self.dtree = app.dtree
        self.dtree.add_directory(p)
        self.dtree.view.clear_calls()

    def test_set_root_as_ref_makes_subfolders_ref_as_well(self, do_setup):
        # Setting a node state to something also affect subnodes. These subnodes must be correctly
        # refreshed.
        node = self.dtree[0]
        eq_(len(node), 3)  # a len() call is required for subnodes to be loaded
        node.state = 1  # the state property is a state index
        node = self.dtree[0]
        eq_(len(node), 3)
        subnode = node[0]
        eq_(subnode.state, 1)
        self.dtree.view.check_gui_calls(["refresh_states"])
