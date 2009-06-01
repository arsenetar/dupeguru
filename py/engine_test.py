#!/usr/bin/env python
"""
Unit Name: dupeguru.engine_test
Created By: Virgil Dupras
Created On: 2006/01/29
Last modified by:$Author: virgil $
Last modified on:$Date: $
                 $Revision: $
Copyright 2004-2008 Hardcoded Software (http://www.hardcoded.net)
"""
import unittest
import sys

from hsutil import job
from hsutil.decorators import log_calls
from hsutil.testcase import TestCase

from . import engine
from .engine import *

class NamedObject(object):
    def __init__(self, name="foobar", with_words=False):
        self.name = name
        if with_words:
            self.words = getwords(name)
    

def get_match_triangle():
    o1 = NamedObject(with_words=True)
    o2 = NamedObject(with_words=True)
    o3 = NamedObject(with_words=True)
    m1 = get_match(o1,o2)
    m2 = get_match(o1,o3)
    m3 = get_match(o2,o3)
    return [m1, m2, m3]

def get_test_group():
    m1, m2, m3 = get_match_triangle()
    result = Group()
    result.add_match(m1)
    result.add_match(m2)
    result.add_match(m3)
    return result

class TCgetwords(TestCase):
    def test_spaces(self):
        self.assertEqual(['a', 'b', 'c', 'd'], getwords("a b c d"))
        self.assertEqual(['a', 'b', 'c', 'd'], getwords(" a  b  c d "))
    
    def test_splitter_chars(self):
        self.assertEqual(
            [chr(i) for i in xrange(ord('a'),ord('z')+1)],
            getwords("a-b_c&d+e(f)g;h\\i[j]k{l}m:n.o,p<q>r/s?t~u!v@w#x$y*z")
        )
    
    def test_joiner_chars(self):
        self.assertEqual(["aec"], getwords(u"a'e\u0301c"))
    
    def test_empty(self):
        self.assertEqual([], getwords(''))
        
    def test_returns_lowercase(self):
        self.assertEqual(['foo', 'bar'], getwords('FOO BAR'))
    
    def test_decompose_unicode(self):
        self.assertEqual(getwords(u'foo\xe9bar'), ['fooebar'])
    

class TCgetfields(TestCase):
    def test_simple(self):
        self.assertEqual([['a', 'b'], ['c', 'd', 'e']], getfields('a b - c d e'))
    
    def test_empty(self):
        self.assertEqual([], getfields(''))
        
    def test_cleans_empty_fields(self):
        expected = [['a', 'bc', 'def']]
        actual = getfields(' - a bc def')
        self.assertEqual(expected, actual)
        expected = [['bc', 'def']]
    

class TCunpack_fields(TestCase):
    def test_with_fields(self):
        expected = ['a', 'b', 'c', 'd', 'e', 'f']
        actual = unpack_fields([['a'], ['b', 'c'], ['d', 'e', 'f']])
        self.assertEqual(expected, actual)
    
    def test_without_fields(self):
        expected = ['a', 'b', 'c', 'd', 'e', 'f']
        actual = unpack_fields(['a', 'b', 'c', 'd', 'e', 'f'])
        self.assertEqual(expected, actual)
    
    def test_empty(self):
        self.assertEqual([], unpack_fields([]))
    

class TCWordCompare(TestCase):
    def test_list(self):
        self.assertEqual(100, compare(['a', 'b', 'c', 'd'],['a', 'b', 'c', 'd']))
        self.assertEqual(86, compare(['a', 'b', 'c', 'd'],['a', 'b', 'c']))
    
    def test_unordered(self):
        #Sometimes, users don't want fuzzy matching too much When they set the slider
        #to 100, they don't expect a filename with the same words, but not the same order, to match.
        #Thus, we want to return 99 in that case.
        self.assertEqual(99, compare(['a', 'b', 'c', 'd'], ['d', 'b', 'c', 'a']))
    
    def test_word_occurs_twice(self):
        #if a word occurs twice in first, but once in second, we want the word to be only counted once
        self.assertEqual(89, compare(['a', 'b', 'c', 'd', 'a'], ['d', 'b', 'c', 'a']))
    
    def test_uses_copy_of_lists(self):
        first = ['foo', 'bar']
        second = ['bar', 'bleh']
        compare(first, second)
        self.assertEqual(['foo', 'bar'], first)
        self.assertEqual(['bar', 'bleh'], second)
    
    def test_word_weight(self):
        self.assertEqual(int((6.0 / 13.0) * 100), compare(['foo', 'bar'], ['bar', 'bleh'], (WEIGHT_WORDS, )))
    
    def test_similar_words(self):
        self.assertEqual(100, compare(['the', 'white', 'stripes'],['the', 'whites', 'stripe'], (MATCH_SIMILAR_WORDS, )))
    
    def test_empty(self):
        self.assertEqual(0, compare([], []))
    
    def test_with_fields(self):
        self.assertEqual(67, compare([['a', 'b'], ['c', 'd', 'e']], [['a', 'b'], ['c', 'd', 'f']]))
    
    def test_propagate_flags_with_fields(self):
        def mock_compare(first, second, flags):
            self.assertEqual((0, 1, 2, 3, 5), flags)
        
        self.mock(engine, 'compare_fields', mock_compare)
        compare([['a']], [['a']], (0, 1, 2, 3, 5))
    

class TCWordCompareWithFields(TestCase):
    def test_simple(self):
        self.assertEqual(67, compare_fields([['a', 'b'], ['c', 'd', 'e']], [['a', 'b'], ['c', 'd', 'f']]))
    
    def test_empty(self):
        self.assertEqual(0, compare_fields([], []))
    
    def test_different_length(self):
        self.assertEqual(0, compare_fields([['a'], ['b']], [['a'], ['b'], ['c']]))
    
    def test_propagates_flags(self):
        def mock_compare(first, second, flags):
            self.assertEqual((0, 1, 2, 3, 5), flags)
        
        self.mock(engine, 'compare_fields', mock_compare)
        compare_fields([['a']], [['a']],(0, 1, 2, 3, 5))
    
    def test_order(self):
        first = [['a', 'b'], ['c', 'd', 'e']]
        second = [['c', 'd', 'f'], ['a', 'b']]
        self.assertEqual(0, compare_fields(first, second))
    
    def test_no_order(self):
        first = [['a','b'],['c','d','e']]
        second = [['c','d','f'],['a','b']]
        self.assertEqual(67, compare_fields(first, second, (NO_FIELD_ORDER, )))
        first = [['a','b'],['a','b']] #a field can only be matched once.
        second = [['c','d','f'],['a','b']]
        self.assertEqual(0, compare_fields(first, second, (NO_FIELD_ORDER, )))
        first = [['a','b'],['a','b','c']] 
        second = [['c','d','f'],['a','b']]
        self.assertEqual(33, compare_fields(first, second, (NO_FIELD_ORDER, )))
    
    def test_compare_fields_without_order_doesnt_alter_fields(self):
        #The NO_ORDER comp type altered the fields!
        first = [['a','b'],['c','d','e']]
        second = [['c','d','f'],['a','b']]
        self.assertEqual(67, compare_fields(first, second, (NO_FIELD_ORDER, )))
        self.assertEqual([['a','b'],['c','d','e']],first)
        self.assertEqual([['c','d','f'],['a','b']],second)
    

class TCbuild_word_dict(TestCase):
    def test_with_standard_words(self):
        l = [NamedObject('foo bar',True)]
        l.append(NamedObject('bar baz',True))
        l.append(NamedObject('baz bleh foo',True))
        d = build_word_dict(l)
        self.assertEqual(4,len(d))
        self.assertEqual(2,len(d['foo']))
        self.assert_(l[0] in d['foo'])
        self.assert_(l[2] in d['foo'])
        self.assertEqual(2,len(d['bar']))
        self.assert_(l[0] in d['bar'])
        self.assert_(l[1] in d['bar'])
        self.assertEqual(2,len(d['baz']))
        self.assert_(l[1] in d['baz'])
        self.assert_(l[2] in d['baz'])
        self.assertEqual(1,len(d['bleh']))
        self.assert_(l[2] in d['bleh'])
    
    def test_unpack_fields(self):
        o = NamedObject('')
        o.words = [['foo','bar'],['baz']]
        d = build_word_dict([o])
        self.assertEqual(3,len(d))
        self.assertEqual(1,len(d['foo']))
    
    def test_words_are_unaltered(self):
        o = NamedObject('')
        o.words = [['foo','bar'],['baz']]
        d = build_word_dict([o])
        self.assertEqual([['foo','bar'],['baz']],o.words)
    
    def test_object_instances_can_only_be_once_in_words_object_list(self):
        o = NamedObject('foo foo',True)
        d = build_word_dict([o])
        self.assertEqual(1,len(d['foo']))
    
    def test_job(self):
        def do_progress(p,d=''):
            self.log.append(p)
            return True
        
        j = job.Job(1,do_progress)
        self.log = []
        s = "foo bar"
        build_word_dict([NamedObject(s, True), NamedObject(s, True), NamedObject(s, True)], j)
        self.assertEqual(0,self.log[0])
        self.assertEqual(33,self.log[1])
        self.assertEqual(66,self.log[2])
        self.assertEqual(100,self.log[3])
    

class TCmerge_similar_words(TestCase):
    def test_some_similar_words(self):
        d = {
            'foobar':set([1]),
            'foobar1':set([2]),
            'foobar2':set([3]),
        }
        merge_similar_words(d)
        self.assertEqual(1,len(d))
        self.assertEqual(3,len(d['foobar']))
    
    

class TCreduce_common_words(TestCase):
    def test_typical(self):
        d = {
            'foo': set([NamedObject('foo bar',True) for i in range(50)]),
            'bar': set([NamedObject('foo bar',True) for i in range(49)])
        }
        reduce_common_words(d, 50)
        self.assert_('foo' not in d)
        self.assertEqual(49,len(d['bar']))
    
    def test_dont_remove_objects_with_only_common_words(self):
        d = {
            'common': set([NamedObject("common uncommon",True) for i in range(50)] + [NamedObject("common",True)]),
            'uncommon': set([NamedObject("common uncommon",True)])
        }
        reduce_common_words(d, 50)
        self.assertEqual(1,len(d['common']))
        self.assertEqual(1,len(d['uncommon']))
    
    def test_values_still_are_set_instances(self):
        d = {
            'common': set([NamedObject("common uncommon",True) for i in range(50)] + [NamedObject("common",True)]),
            'uncommon': set([NamedObject("common uncommon",True)])
        }
        reduce_common_words(d, 50)
        self.assert_(isinstance(d['common'],set))
        self.assert_(isinstance(d['uncommon'],set))
    
    def test_dont_raise_KeyError_when_a_word_has_been_removed(self):
        #If a word has been removed by the reduce, an object in a subsequent common word that
        #contains the word that has been removed would cause a KeyError.
        d = {
            'foo': set([NamedObject('foo bar baz',True) for i in range(50)]),
            'bar': set([NamedObject('foo bar baz',True) for i in range(50)]),
            'baz': set([NamedObject('foo bar baz',True) for i in range(49)])
        }
        try:
            reduce_common_words(d, 50)
        except KeyError:
            self.fail()
    
    def test_unpack_fields(self):
        #object.words may be fields.
        def create_it():
            o = NamedObject('')
            o.words = [['foo','bar'],['baz']]
            return o
        
        d = {
            'foo': set([create_it() for i in range(50)])
        }
        try:
            reduce_common_words(d, 50)
        except TypeError:
            self.fail("must support fields.")
    
    def test_consider_a_reduced_common_word_common_even_after_reduction(self):
        #There was a bug in the code that causeda word that has already been reduced not to
        #be counted as a common word for subsequent words. For example, if 'foo' is processed
        #as a common word, keeping a "foo bar" file in it, and the 'bar' is processed, "foo bar"
        #would not stay in 'bar' because 'foo' is not a common word anymore.
        only_common = NamedObject('foo bar',True)
        d = {
            'foo': set([NamedObject('foo bar baz',True) for i in range(49)] + [only_common]),
            'bar': set([NamedObject('foo bar baz',True) for i in range(49)] + [only_common]),
            'baz': set([NamedObject('foo bar baz',True) for i in range(49)])
        }
        reduce_common_words(d, 50)
        self.assertEqual(1,len(d['foo']))
        self.assertEqual(1,len(d['bar']))
        self.assertEqual(49,len(d['baz']))
    

class TCget_match(TestCase):
    def test_simple(self):
        o1 = NamedObject("foo bar",True)
        o2 = NamedObject("bar bleh",True)
        m = get_match(o1,o2)
        self.assertEqual(50,m.percentage)
        self.assertEqual(['foo','bar'],m.first.words)
        self.assertEqual(['bar','bleh'],m.second.words)
        self.assert_(m.first is o1)
        self.assert_(m.second is o2)
    
    def test_in(self):
        o1 = NamedObject("foo",True)
        o2 = NamedObject("bar",True)
        m = get_match(o1,o2)
        self.assert_(o1 in m)
        self.assert_(o2 in m)
        self.assert_(object() not in m)
    
    def test_word_weight(self):
        self.assertEqual(int((6.0 / 13.0) * 100),get_match(NamedObject("foo bar",True),NamedObject("bar bleh",True),(WEIGHT_WORDS,)).percentage)
    

class TCMatchFactory(TestCase):
    def test_empty(self):
        self.assertEqual([],MatchFactory().getmatches([]))
    
    def test_defaults(self):
        mf = MatchFactory()
        self.assertEqual(50,mf.common_word_threshold)
        self.assertEqual(False,mf.weight_words)
        self.assertEqual(False,mf.match_similar_words)
        self.assertEqual(False,mf.no_field_order)
        self.assertEqual(0,mf.min_match_percentage)
    
    def test_simple(self):
        l = [NamedObject("foo bar"),NamedObject("bar bleh"),NamedObject("a b c foo")]
        r = MatchFactory().getmatches(l)
        self.assertEqual(2,len(r))
        seek = [m for m in r if m.percentage == 50] #"foo bar" and "bar bleh"
        m = seek[0]
        self.assertEqual(['foo','bar'],m.first.words)
        self.assertEqual(['bar','bleh'],m.second.words)
        seek = [m for m in r if m.percentage == 33] #"foo bar" and "a b c foo"
        m = seek[0]
        self.assertEqual(['foo','bar'],m.first.words)
        self.assertEqual(['a','b','c','foo'],m.second.words)
    
    def test_null_and_unrelated_objects(self):
        l = [NamedObject("foo bar"),NamedObject("bar bleh"),NamedObject(""),NamedObject("unrelated object")]
        r = MatchFactory().getmatches(l)
        self.assertEqual(1,len(r))
        m = r[0]
        self.assertEqual(50,m.percentage)
        self.assertEqual(['foo','bar'],m.first.words)
        self.assertEqual(['bar','bleh'],m.second.words)
    
    def test_twice_the_same_word(self):
        l = [NamedObject("foo foo bar"),NamedObject("bar bleh")]
        r = MatchFactory().getmatches(l)
        self.assertEqual(1,len(r))
    
    def test_twice_the_same_word_when_preworded(self):
        l = [NamedObject("foo foo bar",True),NamedObject("bar bleh",True)]
        r = MatchFactory().getmatches(l)
        self.assertEqual(1,len(r))
    
    def test_two_words_match(self):
        l = [NamedObject("foo bar"),NamedObject("foo bar bleh")]
        r = MatchFactory().getmatches(l)
        self.assertEqual(1,len(r))
    
    def test_match_files_with_only_common_words(self):
        #If a word occurs more than 50 times, it is excluded from the matching process
        #The problem with the common_word_threshold is that the files containing only common
        #words will never be matched together. We *should* match them.
        mf = MatchFactory()
        mf.common_word_threshold = 50
        l = [NamedObject("foo") for i in range(50)]
        r = mf.getmatches(l)
        self.assertEqual(1225,len(r))
    
    def test_use_words_already_there_if_there(self):
        o1 = NamedObject('foo')
        o2 = NamedObject('bar')
        o2.words = ['foo']
        self.assertEqual(1,len(MatchFactory().getmatches([o1,o2])))
    
    def test_job(self):
        def do_progress(p,d=''):
            self.log.append(p)
            return True
        
        j = job.Job(1,do_progress)
        self.log = []
        s = "foo bar"
        MatchFactory().getmatches([NamedObject(s),NamedObject(s),NamedObject(s)],j)
        self.assert_(len(self.log) > 2)
        self.assertEqual(0,self.log[0])
        self.assertEqual(100,self.log[-1])
    
    def test_weight_words(self):
        mf = MatchFactory()
        mf.weight_words = True
        l = [NamedObject("foo bar"),NamedObject("bar bleh")]
        m = mf.getmatches(l)[0]
        self.assertEqual(int((6.0 / 13.0) * 100),m.percentage)
    
    def test_similar_word(self):
        mf = MatchFactory()
        mf.match_similar_words = True
        l = [NamedObject("foobar"),NamedObject("foobars")]
        self.assertEqual(1,len(mf.getmatches(l)))
        self.assertEqual(100,mf.getmatches(l)[0].percentage)
        l = [NamedObject("foobar"),NamedObject("foo")]
        self.assertEqual(0,len(mf.getmatches(l))) #too far
        l = [NamedObject("bizkit"),NamedObject("bizket")]
        self.assertEqual(1,len(mf.getmatches(l)))
        l = [NamedObject("foobar"),NamedObject("foosbar")]
        self.assertEqual(1,len(mf.getmatches(l)))
    
    def test_single_object_with_similar_words(self):
        mf = MatchFactory()
        mf.match_similar_words = True
        l = [NamedObject("foo foos")]
        self.assertEqual(0,len(mf.getmatches(l)))
    
    def test_double_words_get_counted_only_once(self):
        mf = MatchFactory()
        l = [NamedObject("foo bar foo bleh"),NamedObject("foo bar bleh bar")]
        m = mf.getmatches(l)[0]
        self.assertEqual(75,m.percentage)
    
    def test_with_fields(self):
        mf = MatchFactory()
        o1 = NamedObject("foo bar - foo bleh")
        o2 = NamedObject("foo bar - bleh bar")
        o1.words = getfields(o1.name)
        o2.words = getfields(o2.name)
        m = mf.getmatches([o1, o2])[0]
        self.assertEqual(50, m.percentage)
    
    def test_with_fields_no_order(self):
        mf = MatchFactory()
        mf.no_field_order = True
        o1 = NamedObject("foo bar - foo bleh")
        o2 = NamedObject("bleh bang - foo bar")
        o1.words = getfields(o1.name)
        o2.words = getfields(o2.name)
        m = mf.getmatches([o1, o2])[0]
        self.assertEqual(50 ,m.percentage)
    
    def test_only_match_similar_when_the_option_is_set(self):
        mf = MatchFactory()
        mf.match_similar_words = False
        l = [NamedObject("foobar"),NamedObject("foobars")]
        self.assertEqual(0,len(mf.getmatches(l)))
    
    def test_dont_recurse_do_match(self):
        # with nosetests, the stack is increased. The number has to be high enough not to be failing falsely
        sys.setrecursionlimit(100)
        mf = MatchFactory()
        files = [NamedObject('foo bar') for i in range(101)]
        try:
            mf.getmatches(files)
        except RuntimeError:
            self.fail()
        finally:
            sys.setrecursionlimit(1000)
    
    def test_min_match_percentage(self):
        l = [NamedObject("foo bar"),NamedObject("bar bleh"),NamedObject("a b c foo")]
        mf = MatchFactory()
        mf.min_match_percentage = 50
        r = mf.getmatches(l)
        self.assertEqual(1,len(r)) #Only "foo bar" / "bar bleh" should match
    
    def test_limit(self):
        l = [NamedObject(),NamedObject(),NamedObject()]
        mf = MatchFactory()
        mf.limit = 2
        r = mf.getmatches(l)
        self.assertEqual(2,len(r))
    
    def test_MemoryError(self):
        @log_calls
        def mocked_match(first, second, flags):
            if len(mocked_match.calls) > 42:
                raise MemoryError()
            return Match(first, second, 0)
        
        objects = [NamedObject() for i in range(10)] # results in 45 matches
        self.mock(engine, 'get_match', mocked_match)
        mf = MatchFactory()
        try:
            r = mf.getmatches(objects)
        except MemoryError:
            self.fail('MemorryError must be handled')
        self.assertEqual(42, len(r))
    

class TCGroup(TestCase):
    def test_empy(self):
        g = Group()
        self.assertEqual(None,g.ref)
        self.assertEqual([],g.dupes)
        self.assertEqual(0,len(g.matches))
    
    def test_add_match(self):
        g = Group()
        m = get_match(NamedObject("foo",True),NamedObject("bar",True))
        g.add_match(m)
        self.assert_(g.ref is m.first)
        self.assertEqual([m.second],g.dupes)
        self.assertEqual(1,len(g.matches))
        self.assert_(m in g.matches)
    
    def test_multiple_add_match(self):
        g = Group()
        o1 = NamedObject("a",True)
        o2 = NamedObject("b",True)
        o3 = NamedObject("c",True)
        o4 = NamedObject("d",True)
        g.add_match(get_match(o1,o2))
        self.assert_(g.ref is o1)
        self.assertEqual([o2],g.dupes)
        self.assertEqual(1,len(g.matches))
        g.add_match(get_match(o1,o3))
        self.assertEqual([o2],g.dupes)
        self.assertEqual(2,len(g.matches))
        g.add_match(get_match(o2,o3))
        self.assertEqual([o2,o3],g.dupes)
        self.assertEqual(3,len(g.matches))
        g.add_match(get_match(o1,o4))
        self.assertEqual([o2,o3],g.dupes)
        self.assertEqual(4,len(g.matches))
        g.add_match(get_match(o2,o4))
        self.assertEqual([o2,o3],g.dupes)
        self.assertEqual(5,len(g.matches))
        g.add_match(get_match(o3,o4))
        self.assertEqual([o2,o3,o4],g.dupes)
        self.assertEqual(6,len(g.matches))
    
    def test_len(self):
        g = Group()
        self.assertEqual(0,len(g))
        g.add_match(get_match(NamedObject("foo",True),NamedObject("bar",True)))
        self.assertEqual(2,len(g))
    
    def test_add_same_match_twice(self):
        g = Group()
        m = get_match(NamedObject("foo",True),NamedObject("foo",True))
        g.add_match(m)
        self.assertEqual(2,len(g))
        self.assertEqual(1,len(g.matches))
        g.add_match(m)
        self.assertEqual(2,len(g))
        self.assertEqual(1,len(g.matches))
    
    def test_in(self):
        g = Group()
        o1 = NamedObject("foo",True)
        o2 = NamedObject("bar",True)
        self.assert_(o1 not in g)
        g.add_match(get_match(o1,o2))
        self.assert_(o1 in g)
        self.assert_(o2 in g)
    
    def test_remove(self):
        g = Group()
        o1 = NamedObject("foo",True)
        o2 = NamedObject("bar",True)
        o3 = NamedObject("bleh",True)
        g.add_match(get_match(o1,o2))
        g.add_match(get_match(o1,o3))
        g.add_match(get_match(o2,o3))
        self.assertEqual(3,len(g.matches))
        self.assertEqual(3,len(g))
        g.remove_dupe(o3)
        self.assertEqual(1,len(g.matches))
        self.assertEqual(2,len(g))
        g.remove_dupe(o1)
        self.assertEqual(0,len(g.matches))
        self.assertEqual(0,len(g))
    
    def test_remove_with_ref_dupes(self):
        g = Group()
        o1 = NamedObject("foo",True)
        o2 = NamedObject("bar",True)
        o3 = NamedObject("bleh",True)
        g.add_match(get_match(o1,o2))
        g.add_match(get_match(o1,o3))
        g.add_match(get_match(o2,o3))
        o1.is_ref = True
        o2.is_ref = True
        g.remove_dupe(o3)
        self.assertEqual(0,len(g))
    
    def test_switch_ref(self):
        o1 = NamedObject(with_words=True)
        o2 = NamedObject(with_words=True)
        g = Group()
        g.add_match(get_match(o1,o2))
        self.assert_(o1 is g.ref)
        g.switch_ref(o2)
        self.assert_(o2 is g.ref)
        self.assertEqual([o1],g.dupes)
        g.switch_ref(o2)
        self.assert_(o2 is g.ref)
        g.switch_ref(NamedObject('',True))
        self.assert_(o2 is g.ref)
    
    def test_get_match_of(self):
        g = Group()
        for m in get_match_triangle():
            g.add_match(m)
        o = g.dupes[0]
        m = g.get_match_of(o)
        self.assert_(g.ref in m)
        self.assert_(o in m)
        self.assert_(g.get_match_of(NamedObject('',True)) is None)
        self.assert_(g.get_match_of(g.ref) is None)
    
    def test_percentage(self):
        #percentage should return the avg percentage in relation to the ref
        m1,m2,m3 = get_match_triangle()
        m1 = Match(m1[0], m1[1], 100)
        m2 = Match(m2[0], m2[1], 50)
        m3 = Match(m3[0], m3[1], 33)
        g = Group()
        g.add_match(m1)
        g.add_match(m2)
        g.add_match(m3)
        self.assertEqual(75,g.percentage)
        g.switch_ref(g.dupes[0])
        self.assertEqual(66,g.percentage)
        g.remove_dupe(g.dupes[0])
        self.assertEqual(33,g.percentage)
        g.add_match(m1)
        g.add_match(m2)
        self.assertEqual(66,g.percentage)
    
    def test_percentage_on_empty_group(self):
        g = Group()
        self.assertEqual(0,g.percentage)
    
    def test_prioritize(self):
        m1,m2,m3 = get_match_triangle()
        o1 = m1.first
        o2 = m1.second
        o3 = m2.second
        o1.name = 'c'
        o2.name = 'b'
        o3.name = 'a'
        g = Group()
        g.add_match(m1)
        g.add_match(m2)
        g.add_match(m3)
        self.assert_(o1 is g.ref)
        g.prioritize(lambda x:x.name)
        self.assert_(o3 is g.ref)
    
    def test_prioritize_with_tie_breaker(self):
        # if the ref has the same key as one or more of the dupe, run the tie_breaker func among them
        g = get_test_group()
        o1, o2, o3 = g.ordered
        tie_breaker = lambda ref, dupe: dupe is o3
        g.prioritize(lambda x:0, tie_breaker)
        self.assertTrue(g.ref is o3)
    
    def test_prioritize_with_tie_breaker_runs_on_all_dupes(self):
        # Even if a dupe is chosen to switch with ref with a tie breaker, we still run the tie breaker 
        # with other dupes and the newly chosen ref
        g = get_test_group()
        o1, o2, o3 = g.ordered
        o1.foo = 1
        o2.foo = 2
        o3.foo = 3
        tie_breaker = lambda ref, dupe: dupe.foo > ref.foo
        g.prioritize(lambda x:0, tie_breaker)
        self.assertTrue(g.ref is o3)
    
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
        key_func = lambda x: -x.foo
        tie_breaker = lambda ref, dupe: dupe.bar > ref.bar
        g.prioritize(key_func, tie_breaker)
        self.assertTrue(g.ref is o2)
    
    def test_list_like(self):
        g = Group()
        o1,o2 = (NamedObject("foo",True),NamedObject("bar",True))
        g.add_match(get_match(o1,o2))
        self.assert_(g[0] is o1)
        self.assert_(g[1] is o2)
    
    def test_clean_matches(self):
        g = Group()
        o1,o2,o3 = (NamedObject("foo",True),NamedObject("bar",True),NamedObject("baz",True))
        g.add_match(get_match(o1,o2))
        g.add_match(get_match(o1,o3))
        g.clean_matches()
        self.assertEqual(1,len(g.matches))
        self.assertEqual(0,len(g.candidates))
    

class TCget_groups(TestCase):
    def test_empty(self):
        r = get_groups([])
        self.assertEqual([],r)
    
    def test_simple(self):
        l = [NamedObject("foo bar"),NamedObject("bar bleh")]
        matches = MatchFactory().getmatches(l)
        m = matches[0]
        r = get_groups(matches)
        self.assertEqual(1,len(r))
        g = r[0]
        self.assert_(g.ref is m.first)
        self.assertEqual([m.second],g.dupes)
    
    def test_group_with_multiple_matches(self):
        #This results in 3 matches
        l = [NamedObject("foo"),NamedObject("foo"),NamedObject("foo")]
        matches = MatchFactory().getmatches(l)
        r = get_groups(matches)
        self.assertEqual(1,len(r))
        g = r[0]
        self.assertEqual(3,len(g))
    
    def test_must_choose_a_group(self):
        l = [NamedObject("a b"),NamedObject("a b"),NamedObject("b c"),NamedObject("c d"),NamedObject("c d")]
        #There will be 2 groups here: group "a b" and group "c d"
        #"b c" can go either of them, but not both.
        matches = MatchFactory().getmatches(l)
        r = get_groups(matches)
        self.assertEqual(2,len(r))
        self.assertEqual(5,len(r[0])+len(r[1]))
    
    def test_should_all_go_in_the_same_group(self):
        l = [NamedObject("a b"),NamedObject("a b"),NamedObject("a b"),NamedObject("a b")]
        #There will be 2 groups here: group "a b" and group "c d"
        #"b c" can fit in both, but it must be in only one of them
        matches = MatchFactory().getmatches(l)
        r = get_groups(matches)
        self.assertEqual(1,len(r))
    
    def test_give_priority_to_matches_with_higher_percentage(self):
        o1 = NamedObject(with_words=True)
        o2 = NamedObject(with_words=True)
        o3 = NamedObject(with_words=True)
        m1 = Match(o1, o2, 1)
        m2 = Match(o2, o3, 2)
        r = get_groups([m1,m2])
        self.assertEqual(1,len(r))
        g = r[0]
        self.assertEqual(2,len(g))
        self.assert_(o1 not in g)
        self.assert_(o2 in g)
        self.assert_(o3 in g)
    
    def test_four_sized_group(self):
        l = [NamedObject("foobar") for i in xrange(4)]
        m = MatchFactory().getmatches(l)
        r = get_groups(m)
        self.assertEqual(1,len(r))
        self.assertEqual(4,len(r[0]))
    
    def test_referenced_by_ref2(self):
        o1 = NamedObject(with_words=True)
        o2 = NamedObject(with_words=True)
        o3 = NamedObject(with_words=True)
        m1 = get_match(o1,o2)
        m2 = get_match(o3,o1)
        m3 = get_match(o3,o2)
        r = get_groups([m1,m2,m3])
        self.assertEqual(3,len(r[0]))
    
    def test_job(self):
        def do_progress(p,d=''):
            self.log.append(p)
            return True
        
        self.log = []
        j = job.Job(1,do_progress)
        m1,m2,m3 = get_match_triangle()
        #101%: To make sure it is processed first so the job test works correctly
        m4 = Match(NamedObject('a',True), NamedObject('a',True), 101)
        get_groups([m1,m2,m3,m4],j)
        self.assertEqual(0,self.log[0])
        self.assertEqual(100,self.log[-1])
    

if __name__ == "__main__":
    unittest.main()
