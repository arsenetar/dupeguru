# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import io
import os.path as op

from xml.etree import ElementTree as ET

from pytest import raises
from hscommon.testutil import eq_
from hscommon.util import first

from .. import engine
from .base import NamedObject, GetTestGroups, DupeGuru
from ..results import Results


class TestCaseResultsEmpty:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.results = self.app.results

    def test_apply_invalid_filter(self):
        # If the applied filter is an invalid regexp, just ignore the filter.
        self.results.apply_filter("[")  # invalid
        self.test_stat_line()  # make sure that the stats line isn't saying we applied a '[' filter

    def test_stat_line(self):
        eq_("0 / 0 (0.00 B / 0.00 B) duplicates marked.", self.results.stat_line)

    def test_groups(self):
        eq_(0, len(self.results.groups))

    def test_get_group_of_duplicate(self):
        assert self.results.get_group_of_duplicate("foo") is None

    def test_save_to_xml(self):
        f = io.BytesIO()
        self.results.save_to_xml(f)
        f.seek(0)
        doc = ET.parse(f)
        root = doc.getroot()
        eq_("results", root.tag)

    def test_is_modified(self):
        assert not self.results.is_modified

    def test_is_modified_after_setting_empty_group(self):
        # Don't consider results as modified if they're empty
        self.results.groups = []
        assert not self.results.is_modified

    def test_save_to_same_name_as_folder(self, tmpdir):
        # Issue #149
        # When saving to a filename that already exists, the file is overwritten. However, when
        # the name exists but that it's a folder, then there used to be a crash. The proper fix
        # would have been some kind of feedback to the user, but the work involved for something
        # that simply never happens (I never received a report of this crash, I experienced it
        # while fooling around) is too much. Instead, use standard name conflict resolution.
        folderpath = tmpdir.join("foo")
        folderpath.mkdir()
        self.results.save_to_xml(str(folderpath))  # no crash
        assert tmpdir.join("[000] foo").check()


class TestCaseResultsWithSomeGroups:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.results = self.app.results
        self.objects, self.matches, self.groups = GetTestGroups()
        self.results.groups = self.groups

    def test_stat_line(self):
        eq_("0 / 3 (0.00 B / 1.01 KB) duplicates marked.", self.results.stat_line)

    def test_groups(self):
        eq_(2, len(self.results.groups))

    def test_get_group_of_duplicate(self):
        for o in self.objects:
            g = self.results.get_group_of_duplicate(o)
            assert isinstance(g, engine.Group)
            assert o in g
        assert self.results.get_group_of_duplicate(self.groups[0]) is None

    def test_remove_duplicates(self):
        g1, g2 = self.results.groups
        self.results.remove_duplicates([g1.dupes[0]])
        eq_(2, len(g1))
        assert g1 in self.results.groups
        self.results.remove_duplicates([g1.ref])
        eq_(2, len(g1))
        assert g1 in self.results.groups
        self.results.remove_duplicates([g1.dupes[0]])
        eq_(0, len(g1))
        assert g1 not in self.results.groups
        self.results.remove_duplicates([g2.dupes[0]])
        eq_(0, len(g2))
        assert g2 not in self.results.groups
        eq_(0, len(self.results.groups))

    def test_remove_duplicates_with_ref_files(self):
        g1, g2 = self.results.groups
        self.objects[0].is_ref = True
        self.objects[1].is_ref = True
        self.results.remove_duplicates([self.objects[2]])
        eq_(0, len(g1))
        assert g1 not in self.results.groups

    def test_make_ref(self):
        g = self.results.groups[0]
        d = g.dupes[0]
        self.results.make_ref(d)
        assert d is g.ref

    def test_sort_groups(self):
        self.results.make_ref(self.objects[1])  # We want to make the 1024 sized object to go ref.
        g1, g2 = self.groups
        self.results.sort_groups("size")
        assert self.results.groups[0] is g2
        assert self.results.groups[1] is g1
        self.results.sort_groups("size", False)
        assert self.results.groups[0] is g1
        assert self.results.groups[1] is g2

    def test_set_groups_when_sorted(self):
        self.results.make_ref(self.objects[1])  # We want to make the 1024 sized object to go ref.
        self.results.sort_groups("size")
        objects, matches, groups = GetTestGroups()
        g1, g2 = groups
        g1.switch_ref(objects[1])
        self.results.groups = groups
        assert self.results.groups[0] is g2
        assert self.results.groups[1] is g1

    def test_get_dupe_list(self):
        eq_([self.objects[1], self.objects[2], self.objects[4]], self.results.dupes)

    def test_dupe_list_is_cached(self):
        assert self.results.dupes is self.results.dupes

    def test_dupe_list_cache_is_invalidated_when_needed(self):
        o1, o2, o3, o4, o5 = self.objects
        eq_([o2, o3, o5], self.results.dupes)
        self.results.make_ref(o2)
        eq_([o1, o3, o5], self.results.dupes)
        objects, matches, groups = GetTestGroups()
        o1, o2, o3, o4, o5 = objects
        self.results.groups = groups
        eq_([o2, o3, o5], self.results.dupes)

    def test_dupe_list_sort(self):
        o1, o2, o3, o4, o5 = self.objects
        o1.size = 5
        o2.size = 4
        o3.size = 3
        o4.size = 2
        o5.size = 1
        self.results.sort_dupes("size")
        eq_([o5, o3, o2], self.results.dupes)
        self.results.sort_dupes("size", False)
        eq_([o2, o3, o5], self.results.dupes)

    def test_dupe_list_remember_sort(self):
        o1, o2, o3, o4, o5 = self.objects
        o1.size = 5
        o2.size = 4
        o3.size = 3
        o4.size = 2
        o5.size = 1
        self.results.sort_dupes("size")
        self.results.make_ref(o2)
        eq_([o5, o3, o1], self.results.dupes)

    def test_dupe_list_sort_delta_values(self):
        o1, o2, o3, o4, o5 = self.objects
        o1.size = 10
        o2.size = 2  # -8
        o3.size = 3  # -7
        o4.size = 20
        o5.size = 1  # -19
        self.results.sort_dupes("size", delta=True)
        eq_([o5, o2, o3], self.results.dupes)

    def test_sort_empty_list(self):
        # There was an infinite loop when sorting an empty list.
        app = DupeGuru()
        r = app.results
        r.sort_dupes("name")
        eq_([], r.dupes)

    def test_dupe_list_update_on_remove_duplicates(self):
        o1, o2, o3, o4, o5 = self.objects
        eq_(3, len(self.results.dupes))
        self.results.remove_duplicates([o2])
        eq_(2, len(self.results.dupes))

    def test_is_modified(self):
        # Changing the groups sets the modified flag
        assert self.results.is_modified

    def test_is_modified_after_save_and_load(self):
        # Saving/Loading a file sets the modified flag back to False
        def get_file(path):
            return [f for f in self.objects if str(f.path) == path][0]

        f = io.BytesIO()
        self.results.save_to_xml(f)
        assert not self.results.is_modified
        self.results.groups = self.groups  # sets the flag back
        f.seek(0)
        self.results.load_from_xml(f, get_file)
        assert not self.results.is_modified

    def test_is_modified_after_removing_all_results(self):
        # Removing all results sets the is_modified flag to false.
        self.results.mark_all()
        self.results.perform_on_marked(lambda x: None, True)
        assert not self.results.is_modified

    def test_group_of_duplicate_after_removal(self):
        # removing a duplicate also removes it from the dupe:group map.
        dupe = self.results.groups[1].dupes[0]
        ref = self.results.groups[1].ref
        self.results.remove_duplicates([dupe])
        assert self.results.get_group_of_duplicate(dupe) is None
        # also remove group ref
        assert self.results.get_group_of_duplicate(ref) is None

    def test_dupe_list_sort_delta_values_nonnumeric(self):
        # When sorting dupes in delta mode on a non-numeric column, our first sort criteria is if
        # the string is the same as its ref.
        g1r, g1d1, g1d2, g2r, g2d1 = self.objects
        # "aaa" makes our dupe go first in alphabetical order, but since we have the same value as
        # ref, we're going last.
        g2r.name = g2d1.name = "aaa"
        self.results.sort_dupes("name", delta=True)
        eq_("aaa", self.results.dupes[2].name)

    def test_dupe_list_sort_delta_values_nonnumeric_case_insensitive(self):
        # Non-numeric delta sorting comparison is case insensitive
        g1r, g1d1, g1d2, g2r, g2d1 = self.objects
        g2r.name = "AaA"
        g2d1.name = "aAa"
        self.results.sort_dupes("name", delta=True)
        eq_("aAa", self.results.dupes[2].name)


class TestCaseResultsWithSavedResults:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.results = self.app.results
        self.objects, self.matches, self.groups = GetTestGroups()
        self.results.groups = self.groups
        self.f = io.BytesIO()
        self.results.save_to_xml(self.f)
        self.f.seek(0)

    def test_is_modified(self):
        # Saving a file sets the modified flag back to False
        assert not self.results.is_modified

    def test_is_modified_after_load(self):
        # Loading a file sets the modified flag back to False
        def get_file(path):
            return [f for f in self.objects if str(f.path) == path][0]

        self.results.groups = self.groups  # sets the flag back
        self.results.load_from_xml(self.f, get_file)
        assert not self.results.is_modified

    def test_is_modified_after_remove(self):
        # Removing dupes sets the modified flag
        self.results.remove_duplicates([self.results.groups[0].dupes[0]])
        assert self.results.is_modified

    def test_is_modified_after_make_ref(self):
        # Making a dupe ref sets the modified flag
        self.results.make_ref(self.results.groups[0].dupes[0])
        assert self.results.is_modified


class TestCaseResultsMarkings:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.results = self.app.results
        self.objects, self.matches, self.groups = GetTestGroups()
        self.results.groups = self.groups

    def test_stat_line(self):
        eq_("0 / 3 (0.00 B / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.mark(self.objects[1])
        eq_("1 / 3 (1.00 KB / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.mark_invert()
        eq_("2 / 3 (2.00 B / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.mark_invert()
        self.results.unmark(self.objects[1])
        self.results.mark(self.objects[2])
        self.results.mark(self.objects[4])
        eq_("2 / 3 (2.00 B / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.mark(self.objects[0])  # this is a ref, it can't be counted
        eq_("2 / 3 (2.00 B / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.groups = self.groups
        eq_("0 / 3 (0.00 B / 1.01 KB) duplicates marked.", self.results.stat_line)

    def test_with_ref_duplicate(self):
        self.objects[1].is_ref = True
        self.results.groups = self.groups
        assert not self.results.mark(self.objects[1])
        self.results.mark(self.objects[2])
        eq_("1 / 2 (1.00 B / 2.00 B) duplicates marked.", self.results.stat_line)

    def test_perform_on_marked(self):
        def log_object(o):
            log.append(o)
            return True

        log = []
        self.results.mark_all()
        self.results.perform_on_marked(log_object, False)
        assert self.objects[1] in log
        assert self.objects[2] in log
        assert self.objects[4] in log
        eq_(3, len(log))
        log = []
        self.results.mark_none()
        self.results.mark(self.objects[4])
        self.results.perform_on_marked(log_object, True)
        eq_(1, len(log))
        assert self.objects[4] in log
        eq_(1, len(self.results.groups))

    def test_perform_on_marked_with_problems(self):
        def log_object(o):
            log.append(o)
            if o is self.objects[1]:
                raise EnvironmentError("foobar")

        log = []
        self.results.mark_all()
        assert self.results.is_marked(self.objects[1])
        self.results.perform_on_marked(log_object, True)
        eq_(len(log), 3)
        eq_(len(self.results.groups), 1)
        eq_(len(self.results.groups[0]), 2)
        assert self.objects[1] in self.results.groups[0]
        assert not self.results.is_marked(self.objects[2])
        assert self.results.is_marked(self.objects[1])
        eq_(len(self.results.problems), 1)
        dupe, msg = self.results.problems[0]
        assert dupe is self.objects[1]
        eq_(msg, "foobar")

    def test_perform_on_marked_with_ref(self):
        def log_object(o):
            log.append(o)
            return True

        log = []
        self.objects[0].is_ref = True
        self.objects[1].is_ref = True
        self.results.mark_all()
        self.results.perform_on_marked(log_object, True)
        assert self.objects[1] not in log
        assert self.objects[2] in log
        assert self.objects[4] in log
        eq_(2, len(log))
        eq_(0, len(self.results.groups))

    def test_perform_on_marked_remove_objects_only_at_the_end(self):
        def check_groups(o):
            eq_(3, len(g1))
            eq_(2, len(g2))
            return True

        g1, g2 = self.results.groups
        self.results.mark_all()
        self.results.perform_on_marked(check_groups, True)
        eq_(0, len(g1))
        eq_(0, len(g2))
        eq_(0, len(self.results.groups))

    def test_remove_duplicates(self):
        g1 = self.results.groups[0]
        self.results.mark(g1.dupes[0])
        eq_("1 / 3 (1.00 KB / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.remove_duplicates([g1.dupes[1]])
        eq_("1 / 2 (1.00 KB / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.remove_duplicates([g1.dupes[0]])
        eq_("0 / 1 (0.00 B / 1.00 B) duplicates marked.", self.results.stat_line)

    def test_make_ref(self):
        g = self.results.groups[0]
        d = g.dupes[0]
        self.results.mark(d)
        eq_("1 / 3 (1.00 KB / 1.01 KB) duplicates marked.", self.results.stat_line)
        self.results.make_ref(d)
        eq_("0 / 3 (0.00 B / 3.00 B) duplicates marked.", self.results.stat_line)
        self.results.make_ref(d)
        eq_("0 / 3 (0.00 B / 3.00 B) duplicates marked.", self.results.stat_line)

    def test_save_xml(self):
        self.results.mark(self.objects[1])
        self.results.mark_invert()
        f = io.BytesIO()
        self.results.save_to_xml(f)
        f.seek(0)
        doc = ET.parse(f)
        root = doc.getroot()
        g1, g2 = root.iter("group")
        d1, d2, d3 = g1.iter("file")
        eq_("n", d1.get("marked"))
        eq_("n", d2.get("marked"))
        eq_("y", d3.get("marked"))
        d1, d2 = g2.iter("file")
        eq_("n", d1.get("marked"))
        eq_("y", d2.get("marked"))

    def test_load_xml(self):
        def get_file(path):
            return [f for f in self.objects if str(f.path) == path][0]

        self.objects[4].name = "ibabtu 2"  # we can't have 2 files with the same path
        self.results.mark(self.objects[1])
        self.results.mark_invert()
        f = io.BytesIO()
        self.results.save_to_xml(f)
        f.seek(0)
        app = DupeGuru()
        r = Results(app)
        r.load_from_xml(f, get_file)
        assert not r.is_marked(self.objects[0])
        assert not r.is_marked(self.objects[1])
        assert r.is_marked(self.objects[2])
        assert not r.is_marked(self.objects[3])
        assert r.is_marked(self.objects[4])


class TestCaseResultsXML:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.results = self.app.results
        self.objects, self.matches, self.groups = GetTestGroups()
        self.results.groups = self.groups

    def get_file(self, path):  # use this as a callback for load_from_xml
        return [o for o in self.objects if str(o.path) == path][0]

    def test_save_to_xml(self):
        self.objects[0].is_ref = True
        self.objects[0].words = [["foo", "bar"]]
        f = io.BytesIO()
        self.results.save_to_xml(f)
        f.seek(0)
        doc = ET.parse(f)
        root = doc.getroot()
        eq_("results", root.tag)
        eq_(2, len(root))
        eq_(2, len([c for c in root if c.tag == "group"]))
        g1, g2 = root
        eq_(6, len(g1))
        eq_(3, len([c for c in g1 if c.tag == "file"]))
        eq_(3, len([c for c in g1 if c.tag == "match"]))
        d1, d2, d3 = [c for c in g1 if c.tag == "file"]
        eq_(op.join("basepath", "foo bar"), d1.get("path"))
        eq_(op.join("basepath", "bar bleh"), d2.get("path"))
        eq_(op.join("basepath", "foo bleh"), d3.get("path"))
        eq_("y", d1.get("is_ref"))
        eq_("n", d2.get("is_ref"))
        eq_("n", d3.get("is_ref"))
        eq_("foo,bar", d1.get("words"))
        eq_("bar,bleh", d2.get("words"))
        eq_("foo,bleh", d3.get("words"))
        eq_(3, len(g2))
        eq_(2, len([c for c in g2 if c.tag == "file"]))
        eq_(1, len([c for c in g2 if c.tag == "match"]))
        d1, d2 = [c for c in g2 if c.tag == "file"]
        eq_(op.join("basepath", "ibabtu"), d1.get("path"))
        eq_(op.join("basepath", "ibabtu"), d2.get("path"))
        eq_("n", d1.get("is_ref"))
        eq_("n", d2.get("is_ref"))
        eq_("ibabtu", d1.get("words"))
        eq_("ibabtu", d2.get("words"))

    def test_load_xml(self):
        def get_file(path):
            return [f for f in self.objects if str(f.path) == path][0]

        self.objects[0].is_ref = True
        self.objects[4].name = "ibabtu 2"  # we can't have 2 files with the same path
        f = io.BytesIO()
        self.results.save_to_xml(f)
        f.seek(0)
        app = DupeGuru()
        r = Results(app)
        r.load_from_xml(f, get_file)
        eq_(2, len(r.groups))
        g1, g2 = r.groups
        eq_(3, len(g1))
        assert g1[0].is_ref
        assert not g1[1].is_ref
        assert not g1[2].is_ref
        assert g1[0] is self.objects[0]
        assert g1[1] is self.objects[1]
        assert g1[2] is self.objects[2]
        eq_(["foo", "bar"], g1[0].words)
        eq_(["bar", "bleh"], g1[1].words)
        eq_(["foo", "bleh"], g1[2].words)
        eq_(2, len(g2))
        assert not g2[0].is_ref
        assert not g2[1].is_ref
        assert g2[0] is self.objects[3]
        assert g2[1] is self.objects[4]
        eq_(["ibabtu"], g2[0].words)
        eq_(["ibabtu"], g2[1].words)

    def test_load_xml_with_filename(self, tmpdir):
        def get_file(path):
            return [f for f in self.objects if str(f.path) == path][0]

        filename = str(tmpdir.join("dupeguru_results.xml"))
        self.objects[4].name = "ibabtu 2"  # we can't have 2 files with the same path
        self.results.save_to_xml(filename)
        app = DupeGuru()
        r = Results(app)
        r.load_from_xml(filename, get_file)
        eq_(2, len(r.groups))

    def test_load_xml_with_some_files_that_dont_exist_anymore(self):
        def get_file(path):
            if path.endswith("ibabtu 2"):
                return None
            return [f for f in self.objects if str(f.path) == path][0]

        self.objects[4].name = "ibabtu 2"  # we can't have 2 files with the same path
        f = io.BytesIO()
        self.results.save_to_xml(f)
        f.seek(0)
        app = DupeGuru()
        r = Results(app)
        r.load_from_xml(f, get_file)
        eq_(1, len(r.groups))
        eq_(3, len(r.groups[0]))

    def test_load_xml_missing_attributes_and_bogus_elements(self):
        def get_file(path):
            return [f for f in self.objects if str(f.path) == path][0]

        root = ET.Element("foobar")  # The root element shouldn't matter, really.
        group_node = ET.SubElement(root, "group")
        dupe_node = ET.SubElement(group_node, "file")  # Perfectly correct file
        dupe_node.set("path", op.join("basepath", "foo bar"))
        dupe_node.set("is_ref", "y")
        dupe_node.set("words", "foo, bar")
        dupe_node = ET.SubElement(group_node, "file")  # is_ref missing, default to 'n'
        dupe_node.set("path", op.join("basepath", "foo bleh"))
        dupe_node.set("words", "foo, bleh")
        dupe_node = ET.SubElement(group_node, "file")  # words are missing, valid.
        dupe_node.set("path", op.join("basepath", "bar bleh"))
        dupe_node = ET.SubElement(group_node, "file")  # path is missing, invalid.
        dupe_node.set("words", "foo, bleh")
        dupe_node = ET.SubElement(group_node, "foobar")  # Invalid element name
        dupe_node.set("path", op.join("basepath", "bar bleh"))
        dupe_node.set("is_ref", "y")
        dupe_node.set("words", "bar, bleh")
        match_node = ET.SubElement(group_node, "match")  # match pointing to a bad index
        match_node.set("first", "42")
        match_node.set("second", "45")
        match_node = ET.SubElement(group_node, "match")  # match with missing attrs
        match_node = ET.SubElement(group_node, "match")  # match with non-int values
        match_node.set("first", "foo")
        match_node.set("second", "bar")
        match_node.set("percentage", "baz")
        group_node = ET.SubElement(root, "foobar")  # invalid group
        group_node = ET.SubElement(root, "group")  # empty group
        f = io.BytesIO()
        tree = ET.ElementTree(root)
        tree.write(f, encoding="utf-8")
        f.seek(0)
        app = DupeGuru()
        r = Results(app)
        r.load_from_xml(f, get_file)
        eq_(1, len(r.groups))
        eq_(3, len(r.groups[0]))

    def test_xml_non_ascii(self):
        def get_file(path):
            if path == op.join("basepath", "\xe9foo bar"):
                return objects[0]
            if path == op.join("basepath", "bar bleh"):
                return objects[1]

        objects = [NamedObject("\xe9foo bar", True), NamedObject("bar bleh", True)]
        matches = engine.getmatches(objects)  # we should have 5 matches
        groups = engine.get_groups(matches)  # We should have 2 groups
        for g in groups:
            g.prioritize(lambda x: objects.index(x))  # We want the dupes to be in the same order as the list is
        app = DupeGuru()
        results = Results(app)
        results.groups = groups
        f = io.BytesIO()
        results.save_to_xml(f)
        f.seek(0)
        app = DupeGuru()
        r = Results(app)
        r.load_from_xml(f, get_file)
        g = r.groups[0]
        eq_("\xe9foo bar", g[0].name)
        eq_(["efoo", "bar"], g[0].words)

    def test_load_invalid_xml(self):
        f = io.BytesIO()
        f.write(b"<this is invalid")
        f.seek(0)
        app = DupeGuru()
        r = Results(app)
        with raises(ET.ParseError):
            r.load_from_xml(f, None)
        eq_(0, len(r.groups))

    def test_load_non_existant_xml(self):
        app = DupeGuru()
        r = Results(app)
        with raises(IOError):
            r.load_from_xml("does_not_exist.xml", None)
        eq_(0, len(r.groups))

    def test_remember_match_percentage(self):
        group = self.groups[0]
        d1, d2, d3 = group
        fake_matches = set()
        fake_matches.add(engine.Match(d1, d2, 42))
        fake_matches.add(engine.Match(d1, d3, 43))
        fake_matches.add(engine.Match(d2, d3, 46))
        group.matches = fake_matches
        f = io.BytesIO()
        results = self.results
        results.save_to_xml(f)
        f.seek(0)
        app = DupeGuru()
        results = Results(app)
        results.load_from_xml(f, self.get_file)
        group = results.groups[0]
        d1, d2, d3 = group
        match = group.get_match_of(d2)  # d1 - d2
        eq_(42, match[2])
        match = group.get_match_of(d3)  # d1 - d3
        eq_(43, match[2])
        group.switch_ref(d2)
        match = group.get_match_of(d3)  # d2 - d3
        eq_(46, match[2])

    def test_save_and_load(self):
        # previously, when reloading matches, they wouldn't be reloaded as namedtuples
        f = io.BytesIO()
        self.results.save_to_xml(f)
        f.seek(0)
        self.results.load_from_xml(f, self.get_file)
        first(self.results.groups[0].matches).percentage

    def test_apply_filter_works_on_paths(self):
        # apply_filter() searches on the whole path, not just on the filename.
        self.results.apply_filter("basepath")
        eq_(len(self.results.groups), 2)

    def test_save_xml_with_invalid_characters(self):
        # Don't crash when saving files that have invalid xml characters in their path
        self.objects[0].name = "foo\x19"
        self.results.save_to_xml(io.BytesIO())  # don't crash


class TestCaseResultsFilter:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.results = self.app.results
        self.objects, self.matches, self.groups = GetTestGroups()
        self.results.groups = self.groups
        self.results.apply_filter(r"foo")

    def test_groups(self):
        eq_(1, len(self.results.groups))
        assert self.results.groups[0] is self.groups[0]

    def test_dupes(self):
        # There are 2 objects matching. The first one is ref. Only the 3rd one is supposed to be in dupes.
        eq_(1, len(self.results.dupes))
        assert self.results.dupes[0] is self.objects[2]

    def test_cancel_filter(self):
        self.results.apply_filter(None)
        eq_(3, len(self.results.dupes))
        eq_(2, len(self.results.groups))

    def test_dupes_reconstructed_filtered(self):
        # make_ref resets self.__dupes to None. When it's reconstructed, we want it filtered
        dupe = self.results.dupes[0]  # 3rd object
        self.results.make_ref(dupe)
        eq_(1, len(self.results.dupes))
        assert self.results.dupes[0] is self.objects[0]

    def test_include_ref_dupes_in_filter(self):
        # When only the ref of a group match the filter, include it in the group
        self.results.apply_filter(None)
        self.results.apply_filter(r"foo bar")
        eq_(1, len(self.results.groups))
        eq_(0, len(self.results.dupes))

    def test_filters_build_on_one_another(self):
        self.results.apply_filter(r"bar")
        eq_(1, len(self.results.groups))
        eq_(0, len(self.results.dupes))

    def test_stat_line(self):
        expected = "0 / 1 (0.00 B / 1.00 B) duplicates marked. filter: foo"
        eq_(expected, self.results.stat_line)
        self.results.apply_filter(r"bar")
        expected = "0 / 0 (0.00 B / 0.00 B) duplicates marked. filter: foo --> bar"
        eq_(expected, self.results.stat_line)
        self.results.apply_filter(None)
        expected = "0 / 3 (0.00 B / 1.01 KB) duplicates marked."
        eq_(expected, self.results.stat_line)

    def test_mark_count_is_filtered_as_well(self):
        self.results.apply_filter(None)
        # We don't want to perform mark_all() because we want the mark list to contain objects
        for dupe in self.results.dupes:
            self.results.mark(dupe)
        self.results.apply_filter(r"foo")
        expected = "1 / 1 (1.00 B / 1.00 B) duplicates marked. filter: foo"
        eq_(expected, self.results.stat_line)

    def test_mark_all_only_affects_filtered_items(self):
        # When performing actions like mark_all() and mark_none in a filtered environment, only mark
        # items that are actually in the filter.
        self.results.mark_all()
        self.results.apply_filter(None)
        eq_(self.results.mark_count, 1)

    def test_sort_groups(self):
        self.results.apply_filter(None)
        self.results.make_ref(self.objects[1])  # to have the 1024 b obkect as ref
        g1, g2 = self.groups
        self.results.apply_filter("a")  # Matches both group
        self.results.sort_groups("size")
        assert self.results.groups[0] is g2
        assert self.results.groups[1] is g1
        self.results.apply_filter(None)
        assert self.results.groups[0] is g2
        assert self.results.groups[1] is g1
        self.results.sort_groups("size", False)
        self.results.apply_filter("a")
        assert self.results.groups[1] is g2
        assert self.results.groups[0] is g1

    def test_set_group(self):
        # We want the new group to be filtered
        self.objects, self.matches, self.groups = GetTestGroups()
        self.results.groups = self.groups
        eq_(1, len(self.results.groups))
        assert self.results.groups[0] is self.groups[0]

    def test_load_cancels_filter(self, tmpdir):
        def get_file(path):
            return [f for f in self.objects if str(f.path) == path][0]

        filename = str(tmpdir.join("dupeguru_results.xml"))
        self.objects[4].name = "ibabtu 2"  # we can't have 2 files with the same path
        self.results.save_to_xml(filename)
        app = DupeGuru()
        r = Results(app)
        r.apply_filter("foo")
        r.load_from_xml(filename, get_file)
        eq_(2, len(r.groups))

    def test_remove_dupe(self):
        self.results.remove_duplicates([self.results.dupes[0]])
        self.results.apply_filter(None)
        eq_(2, len(self.results.groups))
        eq_(2, len(self.results.dupes))
        self.results.apply_filter("ibabtu")
        self.results.remove_duplicates([self.results.dupes[0]])
        self.results.apply_filter(None)
        eq_(1, len(self.results.groups))
        eq_(1, len(self.results.dupes))

    def test_filter_is_case_insensitive(self):
        self.results.apply_filter(None)
        self.results.apply_filter("FOO")
        eq_(1, len(self.results.dupes))

    def test_make_ref_on_filtered_out_doesnt_mess_stats(self):
        # When filtered, a group containing filtered out dupes will display them as being reference.
        # When calling make_ref on such a dupe, the total size and dupecount stats gets messed up
        # because they are *not* counted in the stats in the first place.
        g1, g2 = self.groups
        bar_bleh = g1[1]  # The "bar bleh" dupe is filtered out
        self.results.make_ref(bar_bleh)
        # Now the stats should display *2* markable dupes (instead of 1)
        expected = "0 / 2 (0.00 B / 2.00 B) duplicates marked. filter: foo"
        eq_(expected, self.results.stat_line)
        self.results.apply_filter(None)  # Now let's make sure our unfiltered results aren't fucked up
        expected = "0 / 3 (0.00 B / 3.00 B) duplicates marked."
        eq_(expected, self.results.stat_line)


class TestCaseResultsRefFile:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.results = self.app.results
        self.objects, self.matches, self.groups = GetTestGroups()
        self.objects[0].is_ref = True
        self.objects[1].is_ref = True
        self.results.groups = self.groups

    def test_stat_line(self):
        expected = "0 / 2 (0.00 B / 2.00 B) duplicates marked."
        eq_(expected, self.results.stat_line)
