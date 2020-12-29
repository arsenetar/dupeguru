# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import io
# import os.path as op

from xml.etree import ElementTree as ET

# from pytest import raises
from hscommon.testutil import eq_
from hscommon.plat import ISWINDOWS

from .base import DupeGuru
from ..exclude import ExcludeList, ExcludeDict, default_regexes, AlreadyThereException

from re import error


# Two slightly different implementations here, one around a list of lists,
# and another around a dictionary.


class TestCaseListXMLLoading:
    def setup_method(self, method):
        self.exclude_list = ExcludeList()

    def test_load_non_existant_file(self):
        # Loads the pre-defined regexes
        self.exclude_list.load_from_xml("non_existant.xml")
        eq_(len(default_regexes), len(self.exclude_list))
        # they should also be marked by default
        eq_(len(default_regexes), self.exclude_list.marked_count)

    def test_save_to_xml(self):
        f = io.BytesIO()
        self.exclude_list.save_to_xml(f)
        f.seek(0)
        doc = ET.parse(f)
        root = doc.getroot()
        eq_("exclude_list", root.tag)

    def test_save_and_load(self, tmpdir):
        e1 = ExcludeList()
        e2 = ExcludeList()
        eq_(len(e1), 0)
        e1.add(r"one")
        e1.mark(r"one")
        e1.add(r"two")
        tmpxml = str(tmpdir.join("exclude_testunit.xml"))
        e1.save_to_xml(tmpxml)
        e2.load_from_xml(tmpxml)
        # We should have the default regexes
        assert r"one" in e2
        assert r"two" in e2
        eq_(len(e2), 2)
        eq_(e2.marked_count, 1)

    def test_load_xml_with_garbage_and_missing_elements(self):
        root = ET.Element("foobar")  # The root element shouldn't matter
        exclude_node = ET.SubElement(root, "bogus")
        exclude_node.set("regex", "None")
        exclude_node.set("marked", "y")

        exclude_node = ET.SubElement(root, "exclude")
        exclude_node.set("regex", "one")
        # marked field invalid
        exclude_node.set("markedddd", "y")

        exclude_node = ET.SubElement(root, "exclude")
        exclude_node.set("regex", "two")
        # missing marked field

        exclude_node = ET.SubElement(root, "exclude")
        exclude_node.set("regex", "three")
        exclude_node.set("markedddd", "pazjbjepo")

        f = io.BytesIO()
        tree = ET.ElementTree(root)
        tree.write(f, encoding="utf-8")
        f.seek(0)
        self.exclude_list.load_from_xml(f)
        print(f"{[x for x in self.exclude_list]}")
        # only the two "exclude" nodes should be added,
        eq_(3, len(self.exclude_list))
        # None should be marked
        eq_(0, self.exclude_list.marked_count)


class TestCaseDictXMLLoading(TestCaseListXMLLoading):
    def setup_method(self, method):
        self.exclude_list = ExcludeDict()


class TestCaseListEmpty:
    def setup_method(self, method):
        self.app = DupeGuru()
        self.app.exclude_list = ExcludeList(union_regex=False)
        self.exclude_list = self.app.exclude_list

    def test_add_mark_and_remove_regex(self):
        regex1 = r"one"
        regex2 = r"two"
        self.exclude_list.add(regex1)
        assert(regex1 in self.exclude_list)
        self.exclude_list.add(regex2)
        self.exclude_list.mark(regex1)
        self.exclude_list.mark(regex2)
        eq_(len(self.exclude_list), 2)
        eq_(len(self.exclude_list.compiled), 2)
        compiled_files = [x for x in self.exclude_list.compiled_files]
        eq_(len(compiled_files), 2)
        self.exclude_list.remove(regex2)
        assert(regex2 not in self.exclude_list)
        eq_(len(self.exclude_list), 1)

    def test_add_duplicate(self):
        self.exclude_list.add(r"one")
        eq_(1 , len(self.exclude_list))
        try:
            self.exclude_list.add(r"one")
        except Exception:
            pass
        eq_(1 , len(self.exclude_list))

    def test_add_not_compilable(self):
        # Trying to add a non-valid regex should not work and raise exception
        regex = r"one))"
        try:
            self.exclude_list.add(regex)
        except Exception as e:
            # Make sure we raise a re.error so that the interface can process it
            eq_(type(e), error)
        added = self.exclude_list.mark(regex)
        eq_(added, False)
        eq_(len(self.exclude_list), 0)
        eq_(len(self.exclude_list.compiled), 0)
        compiled_files = [x for x in self.exclude_list.compiled_files]
        eq_(len(compiled_files), 0)

    def test_force_add_not_compilable(self):
        """Used when loading from XML for example"""
        regex = r"one))"
        try:
            self.exclude_list.add(regex, forced=True)
        except Exception as e:
            # Should not get an exception here unless it's a duplicate regex
            raise e
        marked = self.exclude_list.mark(regex)
        eq_(marked, False)  # can't be marked since not compilable
        eq_(len(self.exclude_list), 1)
        eq_(len(self.exclude_list.compiled), 0)
        compiled_files = [x for x in self.exclude_list.compiled_files]
        eq_(len(compiled_files), 0)
        # adding a duplicate
        regex = r"one))"
        try:
            self.exclude_list.add(regex, forced=True)
        except Exception as e:
            # we should have this exception, and it shouldn't be added
            assert type(e) is AlreadyThereException
        eq_(len(self.exclude_list), 1)
        eq_(len(self.exclude_list.compiled), 0)

    def test_rename_regex(self):
        regex = r"one"
        self.exclude_list.add(regex)
        self.exclude_list.mark(regex)
        regex_renamed = r"one))"
        # Not compilable, can't be marked
        self.exclude_list.rename(regex, regex_renamed)
        assert regex not in self.exclude_list
        assert regex_renamed in self.exclude_list
        eq_(self.exclude_list.is_marked(regex_renamed), False)
        self.exclude_list.mark(regex_renamed)
        eq_(self.exclude_list.is_marked(regex_renamed), False)
        regex_renamed_compilable = r"two"
        self.exclude_list.rename(regex_renamed, regex_renamed_compilable)
        assert regex_renamed_compilable in self.exclude_list
        eq_(self.exclude_list.is_marked(regex_renamed), False)
        self.exclude_list.mark(regex_renamed_compilable)
        eq_(self.exclude_list.is_marked(regex_renamed_compilable), True)
        eq_(len(self.exclude_list), 1)
        # Should still be marked after rename
        regex_compilable = r"three"
        self.exclude_list.rename(regex_renamed_compilable, regex_compilable)
        eq_(self.exclude_list.is_marked(regex_compilable), True)

    def test_restore_default(self):
        """Only unmark previously added regexes and mark the pre-defined ones"""
        regex = r"one"
        self.exclude_list.add(regex)
        self.exclude_list.mark(regex)
        self.exclude_list.restore_defaults()
        eq_(len(default_regexes), self.exclude_list.marked_count)
        # added regex shouldn't be marked
        eq_(self.exclude_list.is_marked(regex), False)
        # added regex shouldn't be in compiled list either
        compiled = [x for x in self.exclude_list.compiled]
        assert regex not in compiled
        # Only default regexes marked and in compiled list
        for re in default_regexes:
            assert self.exclude_list.is_marked(re)
            found = False
            for compiled_re in compiled:
                if compiled_re.pattern == re:
                    found = True
            if not found:
                raise(Exception(f"Default RE {re} not found in compiled list."))
            continue
        eq_(len(default_regexes), len(self.exclude_list.compiled))


class TestCaseDictEmpty(TestCaseListEmpty):
    """Same, but with dictionary implementation"""
    def setup_method(self, method):
        self.app = DupeGuru()
        self.app.exclude_list = ExcludeDict(union_regex=False)
        self.exclude_list = self.app.exclude_list


def split_union(pattern_object):
    """Returns list of strings for each union pattern"""
    return [x for x in pattern_object.pattern.split("|")]


class TestCaseCompiledList():
    """Test consistency between union or and separate versions."""
    def setup_method(self, method):
        self.e_separate = ExcludeList(union_regex=False)
        self.e_separate.restore_defaults()
        self.e_union = ExcludeList(union_regex=True)
        self.e_union.restore_defaults()

    def test_same_number_of_expressions(self):
        # We only get one union Pattern item in a tuple, which is made of however many parts
        eq_(len(split_union(self.e_union.compiled[0])), len(default_regexes))
        # We get as many as there are marked items
        eq_(len(self.e_separate.compiled), len(default_regexes))
        exprs = split_union(self.e_union.compiled[0])
        # We should have the same number and the same expressions
        eq_(len(exprs), len(self.e_separate.compiled))
        for expr in self.e_separate.compiled:
            assert expr.pattern in exprs

    def test_compiled_files(self):
        # is path separator checked properly to yield the output
        if ISWINDOWS:
            regex1 = r"test\\one\\sub"
        else:
            regex1 = r"test/one/sub"
        self.e_separate.add(regex1)
        self.e_separate.mark(regex1)
        self.e_union.add(regex1)
        self.e_union.mark(regex1)
        separate_compiled_dirs = self.e_separate.compiled
        separate_compiled_files = [x for x in self.e_separate.compiled_files]
        # HACK we need to call compiled property FIRST to generate the cache
        union_compiled_dirs = self.e_union.compiled
        # print(f"type: {type(self.e_union.compiled_files[0])}")
        # A generator returning only one item... ugh
        union_compiled_files = [x for x in self.e_union.compiled_files][0]
        print(f"compiled files: {union_compiled_files}")
        # Separate should give several plus the one added
        eq_(len(separate_compiled_dirs), len(default_regexes) + 1)
        # regex1 shouldn't be in the "files" version
        eq_(len(separate_compiled_files), len(default_regexes))
        # Only one Pattern returned, which when split should be however many + 1
        eq_(len(split_union(union_compiled_dirs[0])), len(default_regexes) + 1)
        # regex1 shouldn't be here either
        eq_(len(split_union(union_compiled_files)), len(default_regexes))


class TestCaseCompiledDict(TestCaseCompiledList):
    """Test the dictionary version"""
    def setup_method(self, method):
        self.e_separate = ExcludeDict(union_regex=False)
        self.e_separate.restore_defaults()
        self.e_union = ExcludeDict(union_regex=True)
        self.e_union.restore_defaults()
