# Created By: Virgil Dupras
# Created On: 2006/09/14
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging

from pytest import raises, skip
from hscommon.testutil import eq_

try:
    from ..cache import Cache, colors_to_string, string_to_colors
except ImportError:
    skip("Can't import the cache module, probably hasn't been compiled.")

class TestCasecolors_to_string:
    def test_no_color(self):
        eq_('',colors_to_string([]))
    
    def test_single_color(self):
        eq_('000000',colors_to_string([(0,0,0)]))
        eq_('010101',colors_to_string([(1,1,1)]))
        eq_('0a141e',colors_to_string([(10,20,30)]))
    
    def test_two_colors(self):
        eq_('000102030405',colors_to_string([(0,1,2),(3,4,5)]))
    

class TestCasestring_to_colors:
    def test_empty(self):
        eq_([],string_to_colors(''))
    
    def test_single_color(self):
        eq_([(0,0,0)],string_to_colors('000000'))
        eq_([(2,3,4)],string_to_colors('020304'))
        eq_([(10,20,30)],string_to_colors('0a141e'))
    
    def test_two_colors(self):
        eq_([(10,20,30),(40,50,60)],string_to_colors('0a141e28323c'))
    
    def test_incomplete_color(self):
        # don't return anything if it's not a complete color
        eq_([],string_to_colors('102'))
    

class TestCaseCache:
    def test_empty(self):
        c = Cache()
        eq_(0,len(c))
        with raises(KeyError):
            c['foo']
    
    def test_set_then_retrieve_blocks(self):
        c = Cache()
        b = [(0,0,0),(1,2,3)]
        c['foo'] = b
        eq_(b,c['foo'])
    
    def test_delitem(self):
        c = Cache()
        c['foo'] = ''
        del c['foo']
        assert 'foo' not in c
        with raises(KeyError):
            del c['foo']
    
    def test_persistance(self, tmpdir):
        DBNAME = tmpdir.join('hstest.db')
        c = Cache(str(DBNAME))
        c['foo'] = [(1,2,3)]
        del c
        c = Cache(str(DBNAME))
        eq_([(1,2,3)],c['foo'])
    
    def test_filter(self):
        c = Cache()
        c['foo'] = ''
        c['bar'] = ''
        c['baz'] = ''
        c.filter(lambda p:p != 'bar') #only 'bar' is removed
        eq_(2,len(c))
        assert 'foo' in c
        assert 'baz' in c
        assert 'bar' not in c
    
    def test_clear(self):
        c = Cache()
        c['foo'] = ''
        c['bar'] = ''
        c['baz'] = ''
        c.clear()
        eq_(0,len(c))
        assert 'foo' not in c
        assert 'baz' not in c
        assert 'bar' not in c
    
    def test_corrupted_db(self, tmpdir, monkeypatch):
        # If we don't do this monkeypatching, we get a weird exception about trying to flush a
        # closed file. I've tried setting logging level and stuff, but nothing worked. So, there we
        # go, a dirty monkeypatch.
        monkeypatch.setattr(logging, 'warning', lambda *args, **kw: None)
        dbname = str(tmpdir.join('foo.db'))
        fp = open(dbname, 'w')
        fp.write('invalid sqlite content')
        fp.close()
        c = Cache(dbname) # should not raise a DatabaseError
        c['foo'] = [(1, 2, 3)]
        del c
        c = Cache(dbname)
        eq_(c['foo'], [(1, 2, 3)])
    
    def test_by_id(self):
        # it's possible to use the cache by referring to the files by their row_id
        c = Cache()
        b = [(0,0,0),(1,2,3)]
        c['foo'] = b
        foo_id = c.get_id('foo')
        eq_(c[foo_id], b)
    

class TestCaseCacheSQLEscape:
    def test_contains(self):
        c = Cache()
        assert "foo'bar" not in c
    
    def test_getitem(self):
        c = Cache()
        with raises(KeyError):
            c["foo'bar"]
    
    def test_setitem(self):
        c = Cache()
        c["foo'bar"] = []
    
    def test_delitem(self):
        c = Cache()
        c["foo'bar"] = []
        try:
            del c["foo'bar"]
        except KeyError:
            assert False
    
