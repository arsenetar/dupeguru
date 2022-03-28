# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import sys

from hscommon.jobprogress import job
from hscommon.util import first
from hscommon.testutil import eq_, log_calls

from .base import NamedObject
from .. import engine
from ..engine import (
    get_match,
    getwords,
    Group,
    getfields,
    unpack_fields,
    compare_fields,
    compare,
    WEIGHT_WORDS,
    MATCH_SIMILAR_WORDS,
    NO_FIELD_ORDER,
    build_word_dict,
    get_groups,
    getmatches,
    Match,
    getmatches_by_contents,
    merge_similar_words,
    reduce_common_words,
)

no = NamedObject


def get_match_triangle():
    o1 = NamedObject(with_words=True)
    o2 = NamedObject(with_words=True)
    o3 = NamedObject(with_words=True)
    m1 = get_match(o1, o2)
    m2 = get_match(o1, o3)
    m3 = get_match(o2, o3)
    return [m1, m2, m3]


def get_test_group():
    m1, m2, m3 = get_match_triangle()
    result = Group()
    result.add_match(m1)
    result.add_match(m2)
    result.add_match(m3)
    return result


def assert_match(m, name1, name2):
    # When testing matches, whether objects are in first or second position very often doesn't
    # matter. This function makes this test more convenient.
    if m.first.name == name1:
        eq_(m.second.name, name2)
    else:
        eq_(m.first.name, name2)
        eq_(m.second.name, name1)


class TestCasegetwords:
    def test_spaces(self):
        eq_(["a", "b", "c", "d"], getwords("a b c d"))
        eq_(["a", "b", "c", "d"], getwords(" a  b  c d "))

    def test_unicode(self):
        eq_(["e", "c", "0", "a", "o", "u", "e", "u"], getwords("é ç 0 à ö û è ¤ ù"))
        eq_(["02", "君のこころは輝いてるかい？", "国木田花丸", "solo", "ver"], getwords("02 君のこころは輝いてるかい？ 国木田花丸 Solo Ver"))

    def test_splitter_chars(self):
        eq_(
            [chr(i) for i in range(ord("a"), ord("z") + 1)],
            getwords("a-b_c&d+e(f)g;h\\i[j]k{l}m:n.o,p<q>r/s?t~u!v@w#x$y*z"),
        )

    def test_joiner_chars(self):
        eq_(["aec"], getwords("a'e\u0301c"))

    def test_empty(self):
        eq_([], getwords(""))

    def test_returns_lowercase(self):
        eq_(["foo", "bar"], getwords("FOO BAR"))

    def test_decompose_unicode(self):
        eq_(["fooebar"], getwords("foo\xe9bar"))


class TestCasegetfields:
    def test_simple(self):
        eq_([["a", "b"], ["c", "d", "e"]], getfields("a b - c d e"))

    def test_empty(self):
        eq_([], getfields(""))

    def test_cleans_empty_fields(self):
        expected = [["a", "bc", "def"]]
        actual = getfields(" - a bc def")
        eq_(expected, actual)


class TestCaseUnpackFields:
    def test_with_fields(self):
        expected = ["a", "b", "c", "d", "e", "f"]
        actual = unpack_fields([["a"], ["b", "c"], ["d", "e", "f"]])
        eq_(expected, actual)

    def test_without_fields(self):
        expected = ["a", "b", "c", "d", "e", "f"]
        actual = unpack_fields(["a", "b", "c", "d", "e", "f"])
        eq_(expected, actual)

    def test_empty(self):
        eq_([], unpack_fields([]))


class TestCaseWordCompare:
    def test_list(self):
        eq_(100, compare(["a", "b", "c", "d"], ["a", "b", "c", "d"]))
        eq_(86, compare(["a", "b", "c", "d"], ["a", "b", "c"]))

    def test_unordered(self):
        # Sometimes, users don't want fuzzy matching too much When they set the slider
        # to 100, they don't expect a filename with the same words, but not the same order, to match.
        # Thus, we want to return 99 in that case.
        eq_(99, compare(["a", "b", "c", "d"], ["d", "b", "c", "a"]))

    def test_word_occurs_twice(self):
        # if a word occurs twice in first, but once in second, we want the word to be only counted once
        eq_(89, compare(["a", "b", "c", "d", "a"], ["d", "b", "c", "a"]))

    def test_uses_copy_of_lists(self):
        first = ["foo", "bar"]
        second = ["bar", "bleh"]
        compare(first, second)
        eq_(["foo", "bar"], first)
        eq_(["bar", "bleh"], second)

    def test_word_weight(self):
        eq_(
            int((6.0 / 13.0) * 100),
            compare(["foo", "bar"], ["bar", "bleh"], (WEIGHT_WORDS,)),
        )

    def test_similar_words(self):
        eq_(
            100,
            compare(
                ["the", "white", "stripes"],
                ["the", "whites", "stripe"],
                (MATCH_SIMILAR_WORDS,),
            ),
        )

    def test_empty(self):
        eq_(0, compare([], []))

    def test_with_fields(self):
        eq_(67, compare([["a", "b"], ["c", "d", "e"]], [["a", "b"], ["c", "d", "f"]]))

    def test_propagate_flags_with_fields(self, monkeypatch):
        def mock_compare(first, second, flags):
            eq_((0, 1, 2, 3, 5), flags)

        monkeypatch.setattr(engine, "compare_fields", mock_compare)
        compare([["a"]], [["a"]], (0, 1, 2, 3, 5))


class TestCaseWordCompareWithFields:
    def test_simple(self):
        eq_(
            67,
            compare_fields([["a", "b"], ["c", "d", "e"]], [["a", "b"], ["c", "d", "f"]]),
        )

    def test_empty(self):
        eq_(0, compare_fields([], []))

    def test_different_length(self):
        eq_(0, compare_fields([["a"], ["b"]], [["a"], ["b"], ["c"]]))

    def test_propagates_flags(self, monkeypatch):
        def mock_compare(first, second, flags):
            eq_((0, 1, 2, 3, 5), flags)

        monkeypatch.setattr(engine, "compare_fields", mock_compare)
        compare_fields([["a"]], [["a"]], (0, 1, 2, 3, 5))

    def test_order(self):
        first = [["a", "b"], ["c", "d", "e"]]
        second = [["c", "d", "f"], ["a", "b"]]
        eq_(0, compare_fields(first, second))

    def test_no_order(self):
        first = [["a", "b"], ["c", "d", "e"]]
        second = [["c", "d", "f"], ["a", "b"]]
        eq_(67, compare_fields(first, second, (NO_FIELD_ORDER,)))
        first = [["a", "b"], ["a", "b"]]  # a field can only be matched once.
        second = [["c", "d", "f"], ["a", "b"]]
        eq_(0, compare_fields(first, second, (NO_FIELD_ORDER,)))
        first = [["a", "b"], ["a", "b", "c"]]
        second = [["c", "d", "f"], ["a", "b"]]
        eq_(33, compare_fields(first, second, (NO_FIELD_ORDER,)))

    def test_compare_fields_without_order_doesnt_alter_fields(self):
        # The NO_ORDER comp type altered the fields!
        first = [["a", "b"], ["c", "d", "e"]]
        second = [["c", "d", "f"], ["a", "b"]]
        eq_(67, compare_fields(first, second, (NO_FIELD_ORDER,)))
        eq_([["a", "b"], ["c", "d", "e"]], first)
        eq_([["c", "d", "f"], ["a", "b"]], second)


class TestCaseBuildWordDict:
    def test_with_standard_words(self):
        item_list = [NamedObject("foo bar", True)]
        item_list.append(NamedObject("bar baz", True))
        item_list.append(NamedObject("baz bleh foo", True))
        d = build_word_dict(item_list)
        eq_(4, len(d))
        eq_(2, len(d["foo"]))
        assert item_list[0] in d["foo"]
        assert item_list[2] in d["foo"]
        eq_(2, len(d["bar"]))
        assert item_list[0] in d["bar"]
        assert item_list[1] in d["bar"]
        eq_(2, len(d["baz"]))
        assert item_list[1] in d["baz"]
        assert item_list[2] in d["baz"]
        eq_(1, len(d["bleh"]))
        assert item_list[2] in d["bleh"]

    def test_unpack_fields(self):
        o = NamedObject("")
        o.words = [["foo", "bar"], ["baz"]]
        d = build_word_dict([o])
        eq_(3, len(d))
        eq_(1, len(d["foo"]))

    def test_words_are_unaltered(self):
        o = NamedObject("")
        o.words = [["foo", "bar"], ["baz"]]
        build_word_dict([o])
        eq_([["foo", "bar"], ["baz"]], o.words)

    def test_object_instances_can_only_be_once_in_words_object_list(self):
        o = NamedObject("foo foo", True)
        d = build_word_dict([o])
        eq_(1, len(d["foo"]))

    def test_job(self):
        def do_progress(p, d=""):
            self.log.append(p)
            return True

        j = job.Job(1, do_progress)
        self.log = []
        s = "foo bar"
        build_word_dict([NamedObject(s, True), NamedObject(s, True), NamedObject(s, True)], j)
        # We don't have intermediate log because iter_with_progress is called with every > 1
        eq_(0, self.log[0])
        eq_(100, self.log[1])


class TestCaseMergeSimilarWords:
    def test_some_similar_words(self):
        d = {
            "foobar": set([1]),
            "foobar1": set([2]),
            "foobar2": set([3]),
        }
        merge_similar_words(d)
        eq_(1, len(d))
        eq_(3, len(d["foobar"]))


class TestCaseReduceCommonWords:
    def test_typical(self):
        d = {
            "foo": set([NamedObject("foo bar", True) for _ in range(50)]),
            "bar": set([NamedObject("foo bar", True) for _ in range(49)]),
        }
        reduce_common_words(d, 50)
        assert "foo" not in d
        eq_(49, len(d["bar"]))

    def test_dont_remove_objects_with_only_common_words(self):
        d = {
            "common": set([NamedObject("common uncommon", True) for _ in range(50)] + [NamedObject("common", True)]),
            "uncommon": set([NamedObject("common uncommon", True)]),
        }
        reduce_common_words(d, 50)
        eq_(1, len(d["common"]))
        eq_(1, len(d["uncommon"]))

    def test_values_still_are_set_instances(self):
        d = {
            "common": set([NamedObject("common uncommon", True) for _ in range(50)] + [NamedObject("common", True)]),
            "uncommon": set([NamedObject("common uncommon", True)]),
        }
        reduce_common_words(d, 50)
        assert isinstance(d["common"], set)
        assert isinstance(d["uncommon"], set)

    def test_dont_raise_keyerror_when_a_word_has_been_removed(self):
        # If a word has been removed by the reduce, an object in a subsequent common word that
        # contains the word that has been removed would cause a KeyError.
        d = {
            "foo": set([NamedObject("foo bar baz", True) for _ in range(50)]),
            "bar": set([NamedObject("foo bar baz", True) for _ in range(50)]),
            "baz": set([NamedObject("foo bar baz", True) for _ in range(49)]),
        }
        try:
            reduce_common_words(d, 50)
        except KeyError:
            self.fail()

    def test_unpack_fields(self):
        # object.words may be fields.
        def create_it():
            o = NamedObject("")
            o.words = [["foo", "bar"], ["baz"]]
            return o

        d = {"foo": set([create_it() for _ in range(50)])}
        try:
            reduce_common_words(d, 50)
        except TypeError:
            self.fail("must support fields.")

    def test_consider_a_reduced_common_word_common_even_after_reduction(self):
        # There was a bug in the code that causeda word that has already been reduced not to
        # be counted as a common word for subsequent words. For example, if 'foo' is processed
        # as a common word, keeping a "foo bar" file in it, and the 'bar' is processed, "foo bar"
        # would not stay in 'bar' because 'foo' is not a common word anymore.
        only_common = NamedObject("foo bar", True)
        d = {
            "foo": set([NamedObject("foo bar baz", True) for _ in range(49)] + [only_common]),
            "bar": set([NamedObject("foo bar baz", True) for _ in range(49)] + [only_common]),
            "baz": set([NamedObject("foo bar baz", True) for _ in range(49)]),
        }
        reduce_common_words(d, 50)
        eq_(1, len(d["foo"]))
        eq_(1, len(d["bar"]))
        eq_(49, len(d["baz"]))


class TestCaseGetMatch:
    def test_simple(self):
        o1 = NamedObject("foo bar", True)
        o2 = NamedObject("bar bleh", True)
        m = get_match(o1, o2)
        eq_(50, m.percentage)
        eq_(["foo", "bar"], m.first.words)
        eq_(["bar", "bleh"], m.second.words)
        assert m.first is o1
        assert m.second is o2

    def test_in(self):
        o1 = NamedObject("foo", True)
        o2 = NamedObject("bar", True)
        m = get_match(o1, o2)
        assert o1 in m
        assert o2 in m
        assert object() not in m

    def test_word_weight(self):
        m = get_match(NamedObject("foo bar", True), NamedObject("bar bleh", True), (WEIGHT_WORDS,))
        eq_(m.percentage, int((6.0 / 13.0) * 100))


class TestCaseGetMatches:
    def test_empty(self):
        eq_(getmatches([]), [])

    def test_simple(self):
        item_list = [
            NamedObject("foo bar"),
            NamedObject("bar bleh"),
            NamedObject("a b c foo"),
        ]
        r = getmatches(item_list)
        eq_(2, len(r))
        m = first(m for m in r if m.percentage == 50)  # "foo bar" and "bar bleh"
        assert_match(m, "foo bar", "bar bleh")
        m = first(m for m in r if m.percentage == 33)  # "foo bar" and "a b c foo"
        assert_match(m, "foo bar", "a b c foo")

    def test_null_and_unrelated_objects(self):
        item_list = [
            NamedObject("foo bar"),
            NamedObject("bar bleh"),
            NamedObject(""),
            NamedObject("unrelated object"),
        ]
        r = getmatches(item_list)
        eq_(len(r), 1)
        m = r[0]
        eq_(m.percentage, 50)
        assert_match(m, "foo bar", "bar bleh")

    def test_twice_the_same_word(self):
        item_list = [NamedObject("foo foo bar"), NamedObject("bar bleh")]
        r = getmatches(item_list)
        eq_(1, len(r))

    def test_twice_the_same_word_when_preworded(self):
        item_list = [NamedObject("foo foo bar", True), NamedObject("bar bleh", True)]
        r = getmatches(item_list)
        eq_(1, len(r))

    def test_two_words_match(self):
        item_list = [NamedObject("foo bar"), NamedObject("foo bar bleh")]
        r = getmatches(item_list)
        eq_(1, len(r))

    def test_match_files_with_only_common_words(self):
        # If a word occurs more than 50 times, it is excluded from the matching process
        # The problem with the common_word_threshold is that the files containing only common
        # words will never be matched together. We *should* match them.
        # This test assumes that the common word threshold const is 50
        item_list = [NamedObject("foo") for _ in range(50)]
        r = getmatches(item_list)
        eq_(1225, len(r))

    def test_use_words_already_there_if_there(self):
        o1 = NamedObject("foo")
        o2 = NamedObject("bar")
        o2.words = ["foo"]
        eq_(1, len(getmatches([o1, o2])))

    def test_job(self):
        def do_progress(p, d=""):
            self.log.append(p)
            return True

        j = job.Job(1, do_progress)
        self.log = []
        s = "foo bar"
        getmatches([NamedObject(s), NamedObject(s), NamedObject(s)], j=j)
        assert len(self.log) > 2
        eq_(0, self.log[0])
        eq_(100, self.log[-1])

    def test_weight_words(self):
        item_list = [NamedObject("foo bar"), NamedObject("bar bleh")]
        m = getmatches(item_list, weight_words=True)[0]
        eq_(int((6.0 / 13.0) * 100), m.percentage)

    def test_similar_word(self):
        item_list = [NamedObject("foobar"), NamedObject("foobars")]
        eq_(len(getmatches(item_list, match_similar_words=True)), 1)
        eq_(getmatches(item_list, match_similar_words=True)[0].percentage, 100)
        item_list = [NamedObject("foobar"), NamedObject("foo")]
        eq_(len(getmatches(item_list, match_similar_words=True)), 0)  # too far
        item_list = [NamedObject("bizkit"), NamedObject("bizket")]
        eq_(len(getmatches(item_list, match_similar_words=True)), 1)
        item_list = [NamedObject("foobar"), NamedObject("foosbar")]
        eq_(len(getmatches(item_list, match_similar_words=True)), 1)

    def test_single_object_with_similar_words(self):
        item_list = [NamedObject("foo foos")]
        eq_(len(getmatches(item_list, match_similar_words=True)), 0)

    def test_double_words_get_counted_only_once(self):
        item_list = [NamedObject("foo bar foo bleh"), NamedObject("foo bar bleh bar")]
        m = getmatches(item_list)[0]
        eq_(75, m.percentage)

    def test_with_fields(self):
        o1 = NamedObject("foo bar - foo bleh")
        o2 = NamedObject("foo bar - bleh bar")
        o1.words = getfields(o1.name)
        o2.words = getfields(o2.name)
        m = getmatches([o1, o2])[0]
        eq_(50, m.percentage)

    def test_with_fields_no_order(self):
        o1 = NamedObject("foo bar - foo bleh")
        o2 = NamedObject("bleh bang - foo bar")
        o1.words = getfields(o1.name)
        o2.words = getfields(o2.name)
        m = getmatches([o1, o2], no_field_order=True)[0]
        eq_(m.percentage, 50)

    def test_only_match_similar_when_the_option_is_set(self):
        item_list = [NamedObject("foobar"), NamedObject("foobars")]
        eq_(len(getmatches(item_list, match_similar_words=False)), 0)

    def test_dont_recurse_do_match(self):
        # with nosetests, the stack is increased. The number has to be high enough not to be failing falsely
        sys.setrecursionlimit(200)
        files = [NamedObject("foo bar") for _ in range(201)]
        try:
            getmatches(files)
        except RuntimeError:
            self.fail()
        finally:
            sys.setrecursionlimit(1000)

    def test_min_match_percentage(self):
        item_list = [
            NamedObject("foo bar"),
            NamedObject("bar bleh"),
            NamedObject("a b c foo"),
        ]
        r = getmatches(item_list, min_match_percentage=50)
        eq_(1, len(r))  # Only "foo bar" / "bar bleh" should match

    def test_memory_error(self, monkeypatch):
        @log_calls
        def mocked_match(first, second, flags):
            if len(mocked_match.calls) > 42:
                raise MemoryError()
            return Match(first, second, 0)

        objects = [NamedObject() for _ in range(10)]  # results in 45 matches
        monkeypatch.setattr(engine, "get_match", mocked_match)
        try:
            r = getmatches(objects)
        except MemoryError:
            self.fail("MemoryError must be handled")
        eq_(42, len(r))


class TestCaseGetMatchesByContents:
    def test_big_file_partial_hashing(self):
        smallsize = 1
        bigsize = 100 * 1024 * 1024  # 100MB
        f = [
            no("bigfoo", size=bigsize),
            no("bigbar", size=bigsize),
            no("smallfoo", size=smallsize),
            no("smallbar", size=smallsize),
        ]
        f[0].digest = f[0].digest_partial = f[0].digest_samples = "foobar"
        f[1].digest = f[1].digest_partial = f[1].digest_samples = "foobar"
        f[2].digest = f[2].digest_partial = "bleh"
        f[3].digest = f[3].digest_partial = "bleh"
        r = getmatches_by_contents(f, bigsize=bigsize)
        eq_(len(r), 2)
        # User disabled optimization for big files, compute digests as usual
        r = getmatches_by_contents(f, bigsize=0)
        eq_(len(r), 2)
        # Other file is now slightly different, digest_partial is still the same
        f[1].digest = f[1].digest_samples = "foobardiff"
        r = getmatches_by_contents(f, bigsize=bigsize)
        # Successfully filter it out
        eq_(len(r), 1)
        r = getmatches_by_contents(f, bigsize=0)
        eq_(len(r), 1)


class TestCaseGroup:
    def test_empty(self):
        g = Group()
        eq_(None, g.ref)
        eq_([], g.dupes)
        eq_(0, len(g.matches))

    def test_add_match(self):
        g = Group()
        m = get_match(NamedObject("foo", True), NamedObject("bar", True))
        g.add_match(m)
        assert g.ref is m.first
        eq_([m.second], g.dupes)
        eq_(1, len(g.matches))
        assert m in g.matches

    def test_multiple_add_match(self):
        g = Group()
        o1 = NamedObject("a", True)
        o2 = NamedObject("b", True)
        o3 = NamedObject("c", True)
        o4 = NamedObject("d", True)
        g.add_match(get_match(o1, o2))
        assert g.ref is o1
        eq_([o2], g.dupes)
        eq_(1, len(g.matches))
        g.add_match(get_match(o1, o3))
        eq_([o2], g.dupes)
        eq_(2, len(g.matches))
        g.add_match(get_match(o2, o3))
        eq_([o2, o3], g.dupes)
        eq_(3, len(g.matches))
        g.add_match(get_match(o1, o4))
        eq_([o2, o3], g.dupes)
        eq_(4, len(g.matches))
        g.add_match(get_match(o2, o4))
        eq_([o2, o3], g.dupes)
        eq_(5, len(g.matches))
        g.add_match(get_match(o3, o4))
        eq_([o2, o3, o4], g.dupes)
        eq_(6, len(g.matches))

    def test_len(self):
        g = Group()
        eq_(0, len(g))
        g.add_match(get_match(NamedObject("foo", True), NamedObject("bar", True)))
        eq_(2, len(g))

    def test_add_same_match_twice(self):
        g = Group()
        m = get_match(NamedObject("foo", True), NamedObject("foo", True))
        g.add_match(m)
        eq_(2, len(g))
        eq_(1, len(g.matches))
        g.add_match(m)
        eq_(2, len(g))
        eq_(1, len(g.matches))

    def test_in(self):
        g = Group()
        o1 = NamedObject("foo", True)
        o2 = NamedObject("bar", True)
        assert o1 not in g
        g.add_match(get_match(o1, o2))
        assert o1 in g
        assert o2 in g

    def test_remove(self):
        g = Group()
        o1 = NamedObject("foo", True)
        o2 = NamedObject("bar", True)
        o3 = NamedObject("bleh", True)
        g.add_match(get_match(o1, o2))
        g.add_match(get_match(o1, o3))
        g.add_match(get_match(o2, o3))
        eq_(3, len(g.matches))
        eq_(3, len(g))
        g.remove_dupe(o3)
        eq_(1, len(g.matches))
        eq_(2, len(g))
        g.remove_dupe(o1)
        eq_(0, len(g.matches))
        eq_(0, len(g))

    def test_remove_with_ref_dupes(self):
        g = Group()
        o1 = NamedObject("foo", True)
        o2 = NamedObject("bar", True)
        o3 = NamedObject("bleh", True)
        g.add_match(get_match(o1, o2))
        g.add_match(get_match(o1, o3))
        g.add_match(get_match(o2, o3))
        o1.is_ref = True
        o2.is_ref = True
        g.remove_dupe(o3)
        eq_(0, len(g))

    def test_switch_ref(self):
        o1 = NamedObject(with_words=True)
        o2 = NamedObject(with_words=True)
        g = Group()
        g.add_match(get_match(o1, o2))
        assert o1 is g.ref
        g.switch_ref(o2)
        assert o2 is g.ref
        eq_([o1], g.dupes)
        g.switch_ref(o2)
        assert o2 is g.ref
        g.switch_ref(NamedObject("", True))
        assert o2 is g.ref

    def test_switch_ref_from_ref_dir(self):
        # When the ref dupe is from a ref dir, switch_ref() does nothing
        o1 = no(with_words=True)
        o2 = no(with_words=True)
        o1.is_ref = True
        g = Group()
        g.add_match(get_match(o1, o2))
        g.switch_ref(o2)
        assert o1 is g.ref

    def test_get_match_of(self):
        g = Group()
        for m in get_match_triangle():
            g.add_match(m)
        o = g.dupes[0]
        m = g.get_match_of(o)
        assert g.ref in m
        assert o in m
        assert g.get_match_of(NamedObject("", True)) is None
        assert g.get_match_of(g.ref) is None

    def test_percentage(self):
        # percentage should return the avg percentage in relation to the ref
        m1, m2, m3 = get_match_triangle()
        m1 = Match(m1[0], m1[1], 100)
        m2 = Match(m2[0], m2[1], 50)
        m3 = Match(m3[0], m3[1], 33)
        g = Group()
        g.add_match(m1)
        g.add_match(m2)
        g.add_match(m3)
        eq_(75, g.percentage)
        g.switch_ref(g.dupes[0])
        eq_(66, g.percentage)
        g.remove_dupe(g.dupes[0])
        eq_(33, g.percentage)
        g.add_match(m1)
        g.add_match(m2)
        eq_(66, g.percentage)

    def test_percentage_on_empty_group(self):
        g = Group()
        eq_(0, g.percentage)

    def test_prioritize(self):
        m1, m2, m3 = get_match_triangle()
        o1 = m1.first
        o2 = m1.second
        o3 = m2.second
        o1.name = "c"
        o2.name = "b"
        o3.name = "a"
        g = Group()
        g.add_match(m1)
        g.add_match(m2)
        g.add_match(m3)
        assert o1 is g.ref
        assert g.prioritize(lambda x: x.name)
        assert o3 is g.ref

    def test_prioritize_with_tie_breaker(self):
        # if the ref has the same key as one or more of the dupe, run the tie_breaker func among them
        g = get_test_group()
        o1, o2, o3 = g.ordered
        g.prioritize(lambda x: 0, lambda ref, dupe: dupe is o3)
        assert g.ref is o3

    def test_prioritize_with_tie_breaker_runs_on_all_dupes(self):
        # Even if a dupe is chosen to switch with ref with a tie breaker, we still run the tie breaker
        # with other dupes and the newly chosen ref
        g = get_test_group()
        o1, o2, o3 = g.ordered
        o1.foo = 1
        o2.foo = 2
        o3.foo = 3
        g.prioritize(lambda x: 0, lambda ref, dupe: dupe.foo > ref.foo)
        assert g.ref is o3

    def test_prioritize_with_tie_breaker_runs_only_on_tie_dupes(self):
        # The tie breaker only runs on dupes that had the same value for the key_func
        g = get_test_group()
        o1, o2, o3 = g.ordered
        o1.foo = 2
        o2.foo = 2
        o3.foo = 1
        o1.bar = 1
        o2.bar = 2
        o3.bar = 3
        g.prioritize(lambda x: -x.foo, lambda ref, dupe: dupe.bar > ref.bar)
        assert g.ref is o2

    def test_prioritize_with_ref_dupe(self):
        # when the ref dupe of a group is from a ref dir, make it stay on top.
        g = get_test_group()
        o1, o2, o3 = g
        o1.is_ref = True
        o2.size = 2
        g.prioritize(lambda x: -x.size)
        assert g.ref is o1

    def test_prioritize_nothing_changes(self):
        # prioritize() returns False when nothing changes in the group.
        g = get_test_group()
        g[0].name = "a"
        g[1].name = "b"
        g[2].name = "c"
        assert not g.prioritize(lambda x: x.name)

    def test_list_like(self):
        g = Group()
        o1, o2 = (NamedObject("foo", True), NamedObject("bar", True))
        g.add_match(get_match(o1, o2))
        assert g[0] is o1
        assert g[1] is o2

    def test_discard_matches(self):
        g = Group()
        o1, o2, o3 = (
            NamedObject("foo", True),
            NamedObject("bar", True),
            NamedObject("baz", True),
        )
        g.add_match(get_match(o1, o2))
        g.add_match(get_match(o1, o3))
        g.discard_matches()
        eq_(1, len(g.matches))
        eq_(0, len(g.candidates))


class TestCaseGetGroups:
    def test_empty(self):
        r = get_groups([])
        eq_([], r)

    def test_simple(self):
        item_list = [NamedObject("foo bar"), NamedObject("bar bleh")]
        matches = getmatches(item_list)
        m = matches[0]
        r = get_groups(matches)
        eq_(1, len(r))
        g = r[0]
        assert g.ref is m.first
        eq_([m.second], g.dupes)

    def test_group_with_multiple_matches(self):
        # This results in 3 matches
        item_list = [NamedObject("foo"), NamedObject("foo"), NamedObject("foo")]
        matches = getmatches(item_list)
        r = get_groups(matches)
        eq_(1, len(r))
        g = r[0]
        eq_(3, len(g))

    def test_must_choose_a_group(self):
        item_list = [
            NamedObject("a b"),
            NamedObject("a b"),
            NamedObject("b c"),
            NamedObject("c d"),
            NamedObject("c d"),
        ]
        # There will be 2 groups here: group "a b" and group "c d"
        # "b c" can go either of them, but not both.
        matches = getmatches(item_list)
        r = get_groups(matches)
        eq_(2, len(r))
        eq_(5, len(r[0]) + len(r[1]))

    def test_should_all_go_in_the_same_group(self):
        item_list = [
            NamedObject("a b"),
            NamedObject("a b"),
            NamedObject("a b"),
            NamedObject("a b"),
        ]
        # There will be 2 groups here: group "a b" and group "c d"
        # "b c" can fit in both, but it must be in only one of them
        matches = getmatches(item_list)
        r = get_groups(matches)
        eq_(1, len(r))

    def test_give_priority_to_matches_with_higher_percentage(self):
        o1 = NamedObject(with_words=True)
        o2 = NamedObject(with_words=True)
        o3 = NamedObject(with_words=True)
        m1 = Match(o1, o2, 1)
        m2 = Match(o2, o3, 2)
        r = get_groups([m1, m2])
        eq_(1, len(r))
        g = r[0]
        eq_(2, len(g))
        assert o1 not in g
        assert o2 in g
        assert o3 in g

    def test_four_sized_group(self):
        item_list = [NamedObject("foobar") for _ in range(4)]
        m = getmatches(item_list)
        r = get_groups(m)
        eq_(1, len(r))
        eq_(4, len(r[0]))

    def test_referenced_by_ref2(self):
        o1 = NamedObject(with_words=True)
        o2 = NamedObject(with_words=True)
        o3 = NamedObject(with_words=True)
        m1 = get_match(o1, o2)
        m2 = get_match(o3, o1)
        m3 = get_match(o3, o2)
        r = get_groups([m1, m2, m3])
        eq_(3, len(r[0]))

    def test_group_admissible_discarded_dupes(self):
        # If, with a (A, B, C, D) set, all match with A, but C and D don't match with B and that the
        # (A, B) match is the highest (thus resulting in an (A, B) group), still match C and D
        # in a separate group instead of discarding them.
        A, B, C, D = [NamedObject() for _ in range(4)]
        m1 = Match(A, B, 90)  # This is the strongest "A" match
        m2 = Match(A, C, 80)  # Because C doesn't match with B, it won't be in the group
        m3 = Match(A, D, 80)  # Same thing for D
        m4 = Match(C, D, 70)  # However, because C and D match, they should have their own group.
        groups = get_groups([m1, m2, m3, m4])
        eq_(len(groups), 2)
        g1, g2 = groups
        assert A in g1
        assert B in g1
        assert C in g2
        assert D in g2
