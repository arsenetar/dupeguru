# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging

from pytest import raises, skip
from hscommon.testutil import eq_

try:
    from core.pe.cache import colors_to_string, string_to_colors
    from core.pe.cache_sqlite import SqliteCache
    from core.pe.cache_shelve import ShelveCache
except ImportError:
    skip("Can't import the cache module, probably hasn't been compiled.")


class TestCaseColorsToString:
    def test_no_color(self):
        eq_("", colors_to_string([]))

    def test_single_color(self):
        eq_("000000", colors_to_string([(0, 0, 0)]))
        eq_("010101", colors_to_string([(1, 1, 1)]))
        eq_("0a141e", colors_to_string([(10, 20, 30)]))

    def test_two_colors(self):
        eq_("000102030405", colors_to_string([(0, 1, 2), (3, 4, 5)]))


class TestCaseStringToColors:
    def test_empty(self):
        eq_([], string_to_colors(""))

    def test_single_color(self):
        eq_([(0, 0, 0)], string_to_colors("000000"))
        eq_([(2, 3, 4)], string_to_colors("020304"))
        eq_([(10, 20, 30)], string_to_colors("0a141e"))

    def test_two_colors(self):
        eq_([(10, 20, 30), (40, 50, 60)], string_to_colors("0a141e28323c"))

    def test_incomplete_color(self):
        # don't return anything if it's not a complete color
        eq_([], string_to_colors("102"))


class BaseTestCaseCache:
    def get_cache(self, dbname=None):
        raise NotImplementedError()

    def test_empty(self):
        c = self.get_cache()
        eq_(0, len(c))
        with raises(KeyError):
            c["foo"]

    def test_set_then_retrieve_blocks(self):
        c = self.get_cache()
        b = [(0, 0, 0), (1, 2, 3)]
        c["foo"] = b
        eq_(b, c["foo"])

    def test_delitem(self):
        c = self.get_cache()
        c["foo"] = ""
        del c["foo"]
        assert "foo" not in c
        with raises(KeyError):
            del c["foo"]

    def test_persistance(self, tmpdir):
        DBNAME = tmpdir.join("hstest.db")
        c = self.get_cache(str(DBNAME))
        c["foo"] = [(1, 2, 3)]
        del c
        c = self.get_cache(str(DBNAME))
        eq_([(1, 2, 3)], c["foo"])

    def test_filter(self):
        c = self.get_cache()
        c["foo"] = ""
        c["bar"] = ""
        c["baz"] = ""
        c.filter(lambda p: p != "bar")  # only 'bar' is removed
        eq_(2, len(c))
        assert "foo" in c
        assert "baz" in c
        assert "bar" not in c

    def test_clear(self):
        c = self.get_cache()
        c["foo"] = ""
        c["bar"] = ""
        c["baz"] = ""
        c.clear()
        eq_(0, len(c))
        assert "foo" not in c
        assert "baz" not in c
        assert "bar" not in c

    def test_by_id(self):
        # it's possible to use the cache by referring to the files by their row_id
        c = self.get_cache()
        b = [(0, 0, 0), (1, 2, 3)]
        c["foo"] = b
        foo_id = c.get_id("foo")
        eq_(c[foo_id], b)


class TestCaseSqliteCache(BaseTestCaseCache):
    def get_cache(self, dbname=None):
        if dbname:
            return SqliteCache(dbname)
        else:
            return SqliteCache()

    def test_corrupted_db(self, tmpdir, monkeypatch):
        # If we don't do this monkeypatching, we get a weird exception about trying to flush a
        # closed file. I've tried setting logging level and stuff, but nothing worked. So, there we
        # go, a dirty monkeypatch.
        monkeypatch.setattr(logging, "warning", lambda *args, **kw: None)
        dbname = str(tmpdir.join("foo.db"))
        fp = open(dbname, "w")
        fp.write("invalid sqlite content")
        fp.close()
        c = self.get_cache(dbname)  # should not raise a DatabaseError
        c["foo"] = [(1, 2, 3)]
        del c
        c = self.get_cache(dbname)
        eq_(c["foo"], [(1, 2, 3)])


class TestCaseShelveCache(BaseTestCaseCache):
    def get_cache(self, dbname=None):
        return ShelveCache(dbname)


class TestCaseCacheSQLEscape:
    def get_cache(self):
        return SqliteCache()

    def test_contains(self):
        c = self.get_cache()
        assert "foo'bar" not in c

    def test_getitem(self):
        c = self.get_cache()
        with raises(KeyError):
            c["foo'bar"]

    def test_setitem(self):
        c = self.get_cache()
        c["foo'bar"] = []

    def test_delitem(self):
        c = self.get_cache()
        c["foo'bar"] = []
        try:
            del c["foo'bar"]
        except KeyError:
            assert False
