import time

import pytest

from hscommon.jobprogress.job import nulljob
from hscommon.testutil import eq_

from core import app as app_module
from core.app import DestType
from core.scanner import ScanType
from core.tests.base import TestApp
from core.tests.results_test import GetTestGroups


@pytest.fixture
def tapp():
    tapp = TestApp()
    tapp.app.options["allow_marking_refs"] = True
    objects, matches, groups = GetTestGroups()
    tapp.app.results.groups = groups
    tapp.rtable.refresh()
    return tapp


def ref_row(tapp, group_index=0):
    group = tapp.app.results.groups[group_index]
    return next(row for row in tapp.rtable if row._dupe is group.ref)


class TestMarking:
    def test_off_by_default(self, tapp):
        tapp.app.options["allow_marking_refs"] = False
        row = ref_row(tapp)
        assert not row.markable
        row.marked = True
        assert not row.marked
        eq_(tapp.app.results.marked_refs, [])

    def test_mark_a_reference(self, tapp):
        row = ref_row(tapp)
        assert row.markable
        row.marked = True
        assert row.marked
        eq_(tapp.app.results.marked_refs, [row._dupe])
        eq_(tapp.app.results.marked_file_count, 1)
        row.marked = False
        assert not row.marked

    def test_mark_all_and_invert_leave_references_alone(self, tapp):
        app = tapp.app
        app.mark_all()
        eq_(app.results.marked_refs, [])
        app.mark_invert()
        app.mark_invert()
        eq_(app.results.marked_refs, [])

    def test_space_marks_selected_references(self, tapp):
        app = tapp.app
        group = app.results.groups[0]
        app.selected_dupes = [group.ref, group.dupes[0]]
        app.toggle_selected_mark_state()
        eq_(app.results.marked_refs, [group.ref])
        assert app.results.is_marked(group.dupes[0])
        app.toggle_selected_mark_state()
        eq_(app.results.marked_refs, [])
        assert not app.results.is_marked(group.dupes[0])
        # mixed marks: everything selected gets marked
        app.results.mark(group.dupes[0])
        app.toggle_selected_mark_state()
        eq_(app.results.marked_refs, [group.ref])
        assert app.results.is_marked(group.dupes[0])

    def test_space_leaves_references_alone_with_marking_off(self, tapp):
        app = tapp.app
        app.options["allow_marking_refs"] = False
        group = app.results.groups[0]
        app.selected_dupes = [group.ref, group.dupes[0]]
        app.toggle_selected_mark_state()
        eq_(app.results.marked_refs, [])
        assert app.results.is_marked(group.dupes[0])

    def test_mark_none_clears_references(self, tapp):
        ref_row(tapp).marked = True
        tapp.app.mark_none()
        eq_(tapp.app.results.marked_refs, [])

    def test_reference_folder_files_are_never_markable(self, tapp):
        row = ref_row(tapp)
        row._dupe.is_ref = True
        assert not row.markable
        row.marked = True
        assert not row.marked

    def test_losing_the_reference_position_drops_the_mark(self, tapp):
        app = tapp.app
        group = app.results.groups[0]
        old_ref = group.ref
        ref_row(tapp).marked = True
        app.selected_dupes = [group.dupes[0]]
        app.make_selected_reference()
        assert not app.results.is_marked(old_ref)
        app.selected_dupes = [old_ref]
        app.make_selected_reference()
        assert group.ref is old_ref
        assert not app.results.is_ref_marked(old_ref)

    def test_reprioritizing_drops_moved_marks(self, tapp):
        app = tapp.app
        group = app.results.groups[0]
        old_ref = group.ref
        ref_row(tapp).marked = True
        app.reprioritize_groups(lambda f: 0 if f is group.dupes[-1] else 1)
        assert group.ref is not old_ref
        app.reprioritize_groups(lambda f: 0 if f is old_ref else 1)
        assert group.ref is old_ref
        assert not app.results.is_ref_marked(old_ref)

    def test_stat_line(self, tapp):
        ref_row(tapp).marked = True
        assert "Reference files marked: 1 " in tapp.app.stat_line


def wait_for_job(app):
    window = app.progress_window
    deadline = time.monotonic() + 30
    while window.last_progress is not None:
        assert time.monotonic() < deadline, "job didn't finish"
        time.sleep(0.01)
    window.reraise_if_error()


@pytest.fixture
def scanned(tmp_path, monkeypatch):
    """Two groups of real files: three that match, and a pair."""
    folder = tmp_path / "scanned"
    folder.mkdir()
    for name, content in [("a1", b"aaa"), ("a2", b"aaa"), ("a3", b"aaa"), ("b1", b"bbbb"), ("b2", b"bbbb")]:
        (folder / name).write_bytes(content)
    app = TestApp().app
    app.options["allow_marking_refs"] = True
    app.directories.add_path(folder)
    app.options["scan_type"] = ScanType.CONTENTS
    app.start_scanning()
    wait_for_job(app)
    eq_(sorted(len(g) for g in app.results.groups), [2, 3])

    def run_now(jobid, func, args=()):
        func(nulljob, *args)
        app._results_changed()

    monkeypatch.setattr(app, "_start_job", run_now)
    app.deletion_options._link_deleted = False

    def show(count):
        app.deletion_options.direct = True  # nothing goes to the real Recycle Bin
        return True

    monkeypatch.setattr(app.deletion_options, "show", show)
    return app, tmp_path


def group_of(app, size):
    return next(g for g in app.results.groups if len(g) == size)


class TestActions:
    def test_delete_a_reference_and_a_duplicate(self, scanned):
        app, _ = scanned
        group = group_of(app, 3)
        ref, dupe, kept = group.ordered
        app.results.mark_ref(ref)
        app.results.mark(dupe)
        app.delete_marked()
        eq_(app.view.messages[-1], "1 of the 2 marked files are reference files!")
        assert not ref.path.exists() and not dupe.path.exists() and kept.path.exists()
        # the group was left with one file
        eq_(len(app.results.groups), 1)
        assert app.results.get_group_of_duplicate(kept) is None

    def test_delete_a_whole_group(self, scanned):
        app, _ = scanned
        group = group_of(app, 2)
        ref, dupe = group.ordered
        app.results.mark_ref(ref)
        app.results.mark(dupe)
        app.delete_marked()
        assert not ref.path.exists() and not dupe.path.exists()
        eq_([len(g) for g in app.results.groups], [3])
        assert app.stat_line.startswith("0 / 2 ")

    def test_delete_only_the_reference(self, scanned):
        app, _ = scanned
        group = group_of(app, 3)
        ref, first, second = group.ordered
        app.results.mark_ref(ref)
        app.delete_marked()
        assert not ref.path.exists()
        eq_(group.ordered, [first, second])
        eq_(app.results.marked_refs, [])
        assert not app.results.is_marked(first)
        assert app.stat_line.startswith("0 / 2 ")  # second, and the other group's duplicate

    def test_cancel(self, scanned):
        app, _ = scanned
        app.view.proceed = False
        ref = group_of(app, 2).ref
        app.results.mark_ref(ref)
        app.delete_marked()
        assert ref.path.exists()
        eq_(app.results.marked_refs, [ref])

    def test_no_warning_without_marked_references(self, scanned):
        app, _ = scanned
        dupe = group_of(app, 2).dupes[0]
        app.results.mark(dupe)
        app.delete_marked()
        assert not dupe.path.exists()
        eq_(app.view.messages, [])

    def test_no_links_to_deleted_references(self, scanned):
        app, _ = scanned
        group = group_of(app, 2)
        app.results.mark_ref(group.ref)
        app.results.mark(group.dupes[0])
        app.deletion_options._link_deleted = True
        app.delete_marked()
        assert group.ref.path.exists() and group.dupes[0].path.exists()
        eq_(app.view.messages[-1], app_module.MSG_NO_LINKS_TO_MARKED_REFERENCES)

    def test_move_a_reference(self, scanned, monkeypatch):
        app, tmp_path = scanned
        dest = tmp_path / "dest"
        dest.mkdir()
        monkeypatch.setattr(app.view, "select_dest_folder", lambda prompt: str(dest), raising=False)
        app.options["copymove_dest_type"] = DestType.DIRECT
        group = group_of(app, 3)
        ref = group.ref
        app.results.mark_ref(ref)
        app.copy_or_move_marked(False)
        eq_(app.view.messages[-1], "1 of the 1 marked files are reference files!")
        assert not ref.path.exists() and (dest / ref.path.name).exists()
        eq_(len(group), 2)

    def test_custom_command_asks_when_references_are_selected(self, scanned, monkeypatch):
        app, _ = scanned
        calls = []

        class FakePopen:
            def __init__(self, cmd, **kwargs):
                calls.append(cmd)
                self.stdout = self

            def read(self):
                return b""

        monkeypatch.setattr(app_module.subprocess, "Popen", FakePopen)
        monkeypatch.setattr(app.view, "get_default", lambda key: "cmd %d %r" if key == "CustomCommand" else None)
        group = group_of(app, 3)
        app.selected_dupes = [group.ref, group.dupes[0]]
        app.view.proceed = False
        app.invoke_custom_command()
        eq_(app.view.messages[-1], "1 of the 2 selected files are reference files!")
        eq_(calls, [])
        app.view.proceed = True
        app.invoke_custom_command()
        eq_(len(calls), 2)
        app.view.messages.clear()
        app.selected_dupes = [group.dupes[0]]
        app.invoke_custom_command()
        eq_(app.view.messages, [])
        eq_(len(calls), 3)

    def test_custom_command_asks_even_with_marking_off(self, scanned, monkeypatch):
        app, _ = scanned
        app.options["allow_marking_refs"] = False
        monkeypatch.setattr(app.view, "get_default", lambda key: "cmd %d" if key == "CustomCommand" else None)
        app.view.proceed = False
        app.selected_dupes = [group_of(app, 2).ref]
        app.invoke_custom_command()
        eq_(app.view.messages[-1], "1 of the 1 selected files are reference files!")
