# Created By: Virgil Dupras
# Created On: 2006/09/14
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
import os

from hsutil.testcase import TestCase

from ..cache import *

class TCcolors_to_string(TestCase):
    def test_no_color(self):
        self.assertEqual('',colors_to_string([]))
    
    def test_single_color(self):
        self.assertEqual('000000',colors_to_string([(0,0,0)]))
        self.assertEqual('010101',colors_to_string([(1,1,1)]))
        self.assertEqual('0a141e',colors_to_string([(10,20,30)]))
    
    def test_two_colors(self):
        self.assertEqual('000102030405',colors_to_string([(0,1,2),(3,4,5)]))
    

class TCstring_to_colors(TestCase):
    def test_empty(self):
        self.assertEqual([],string_to_colors(''))
    
    def test_single_color(self):
        self.assertEqual([(0,0,0)],string_to_colors('000000'))
        self.assertEqual([(2,3,4)],string_to_colors('020304'))
        self.assertEqual([(10,20,30)],string_to_colors('0a141e'))
    
    def test_two_colors(self):
        self.assertEqual([(10,20,30),(40,50,60)],string_to_colors('0a141e28323c'))
    
    def test_incomplete_color(self):
        # don't return anything if it's not a complete color
        self.assertEqual([],string_to_colors('102'))
    

class TCCache(TestCase):
    def test_empty(self):
        c = Cache()
        self.assertEqual(0,len(c))
        self.assertRaises(KeyError,c.__getitem__,'foo')
    
    def test_set_then_retrieve_blocks(self):
        c = Cache()
        b = [(0,0,0),(1,2,3)]
        c['foo'] = b
        self.assertEqual(b,c['foo'])
    
    def test_delitem(self):
        c = Cache()
        c['foo'] = ''
        del c['foo']
        self.assert_('foo' not in c)
        self.assertRaises(KeyError,c.__delitem__,'foo')
    
    def test_persistance(self):
        DBNAME = op.join(self.tmpdir(), 'hstest.db')
        c = Cache(DBNAME)
        c['foo'] = [(1,2,3)]
        del c
        c = Cache(DBNAME)
        self.assertEqual([(1,2,3)],c['foo'])
        del c
        os.remove(DBNAME)
    
    def test_filter(self):
        c = Cache()
        c['foo'] = ''
        c['bar'] = ''
        c['baz'] = ''
        c.filter(lambda p:p != 'bar') #only 'bar' is removed
        self.assertEqual(2,len(c))
        self.assert_('foo' in c)
        self.assert_('baz' in c)
        self.assert_('bar' not in c)
    
    def test_clear(self):
        c = Cache()
        c['foo'] = ''
        c['bar'] = ''
        c['baz'] = ''
        c.clear()
        self.assertEqual(0,len(c))
        self.assert_('foo' not in c)
        self.assert_('baz' not in c)
        self.assert_('bar' not in c)
    
    def test_corrupted_db(self):
        dbname = op.join(self.tmpdir(), 'foo.db')
        fp = open(dbname, 'w')
        fp.write('invalid sqlite content')
        fp.close()
        c = Cache(dbname) # should not raise a DatabaseError
        c['foo'] = [(1, 2, 3)]
        del c
        c = Cache(dbname)
        self.assertEqual(c['foo'], [(1, 2, 3)])
    
    def test_by_id(self):
        # it's possible to use the cache by referring to the files by their row_id
        c = Cache()
        b = [(0,0,0),(1,2,3)]
        c['foo'] = b
        foo_id = c.get_id('foo')
        self.assertEqual(c[foo_id], b)
    

class TCCacheSQLEscape(TestCase):
    def test_contains(self):
        c = Cache()
        self.assert_("foo'bar" not in c)
    
    def test_getitem(self):
        c = Cache()
        self.assertRaises(KeyError, c.__getitem__, "foo'bar")
    
    def test_setitem(self):
        c = Cache()
        c["foo'bar"] = []
    
    def test_delitem(self):
        c = Cache()
        c["foo'bar"] = []
        try:
            del c["foo'bar"]
        except KeyError:
            self.fail()
    
