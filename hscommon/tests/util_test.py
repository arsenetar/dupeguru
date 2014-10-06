# Created By: Virgil Dupras
# Created On: 2011-01-11
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

from io import StringIO

from pytest import raises

from ..testutil import eq_
from ..path import Path
from ..util import *

def test_nonone():
    eq_('foo', nonone('foo', 'bar'))
    eq_('bar', nonone(None, 'bar'))

def test_tryint():
    eq_(42,tryint('42'))
    eq_(0,tryint('abc'))
    eq_(0,tryint(None))
    eq_(42,tryint(None, 42))

def test_minmax():
    eq_(minmax(2, 1, 3), 2)
    eq_(minmax(0, 1, 3), 1)
    eq_(minmax(4, 1, 3), 3)

#--- Sequence

def test_first():
    eq_(first([3, 2, 1]), 3)
    eq_(first(i for i in [3, 2, 1] if i < 3), 2)

def test_flatten():
    eq_([1,2,3,4],flatten([[1,2],[3,4]]))
    eq_([],flatten([]))

def test_dedupe():
    reflist = [0,7,1,2,3,4,4,5,6,7,1,2,3]
    eq_(dedupe(reflist),[0,7,1,2,3,4,5,6])

def test_stripfalse():
    eq_([1, 2, 3], stripfalse([None, 0, 1, 2, 3, None]))

def test_extract():
    wheat, shaft = extract(lambda n: n % 2 == 0, list(range(10)))
    eq_(wheat, [0, 2, 4, 6, 8])
    eq_(shaft, [1, 3, 5, 7, 9])

def test_allsame():
    assert allsame([42, 42, 42])
    assert not allsame([42, 43, 42])
    assert not allsame([43, 42, 42])
    # Works on non-sequence as well
    assert allsame(iter([42, 42, 42]))

def test_trailiter():
    eq_(list(trailiter([])), [])
    eq_(list(trailiter(['foo'])), [(None, 'foo')])
    eq_(list(trailiter(['foo', 'bar'])), [(None, 'foo'), ('foo', 'bar')])
    eq_(list(trailiter(['foo', 'bar'], skipfirst=True)), [('foo', 'bar')])
    eq_(list(trailiter([], skipfirst=True)), []) # no crash

def test_iterconsume():
    # We just want to make sure that we return *all* items and that we're not mistakenly skipping
    # one.
    eq_(list(range(2500)), list(iterconsume(list(range(2500)))))
    eq_(list(reversed(range(2500))), list(iterconsume(list(range(2500)), reverse=False)))

#--- String

def test_escape():
    eq_('f\\o\\ob\\ar', escape('foobar', 'oa'))
    eq_('f*o*ob*ar', escape('foobar', 'oa', '*'))
    eq_('f*o*ob*ar', escape('foobar', set('oa'), '*'))

def test_get_file_ext():
    eq_(get_file_ext("foobar"), "")
    eq_(get_file_ext("foo.bar"), "bar")
    eq_(get_file_ext("foobar."), "")
    eq_(get_file_ext(".foobar"), "foobar")

def test_rem_file_ext():
    eq_(rem_file_ext("foobar"), "foobar")
    eq_(rem_file_ext("foo.bar"), "foo")
    eq_(rem_file_ext("foobar."), "foobar")
    eq_(rem_file_ext(".foobar"), "")

def test_pluralize():
    eq_('0 song', pluralize(0,'song'))
    eq_('1 song', pluralize(1,'song'))
    eq_('2 songs', pluralize(2,'song'))
    eq_('1 song', pluralize(1.1,'song'))
    eq_('2 songs', pluralize(1.5,'song'))
    eq_('1.1 songs', pluralize(1.1,'song',1))
    eq_('1.5 songs', pluralize(1.5,'song',1))
    eq_('2 entries', pluralize(2,'entry', plural_word='entries'))

def test_format_time():
    eq_(format_time(0),'00:00:00')
    eq_(format_time(1),'00:00:01')
    eq_(format_time(23),'00:00:23')
    eq_(format_time(60),'00:01:00')
    eq_(format_time(101),'00:01:41')
    eq_(format_time(683),'00:11:23')
    eq_(format_time(3600),'01:00:00')
    eq_(format_time(3754),'01:02:34')
    eq_(format_time(36000),'10:00:00')
    eq_(format_time(366666),'101:51:06')
    eq_(format_time(0, with_hours=False),'00:00')
    eq_(format_time(1, with_hours=False),'00:01')
    eq_(format_time(23, with_hours=False),'00:23')
    eq_(format_time(60, with_hours=False),'01:00')
    eq_(format_time(101, with_hours=False),'01:41')
    eq_(format_time(683, with_hours=False),'11:23')
    eq_(format_time(3600, with_hours=False),'60:00')
    eq_(format_time(6036, with_hours=False),'100:36')
    eq_(format_time(60360, with_hours=False),'1006:00')

def test_format_time_decimal():
    eq_(format_time_decimal(0), '0.0 second')
    eq_(format_time_decimal(1), '1.0 second')
    eq_(format_time_decimal(23), '23.0 seconds')
    eq_(format_time_decimal(60), '1.0 minute')
    eq_(format_time_decimal(101), '1.7 minutes')
    eq_(format_time_decimal(683), '11.4 minutes')
    eq_(format_time_decimal(3600), '1.0 hour')
    eq_(format_time_decimal(6036), '1.7 hours')
    eq_(format_time_decimal(86400), '1.0 day')
    eq_(format_time_decimal(160360), '1.9 days')

def test_format_size():
    eq_(format_size(1024), '1 KB')
    eq_(format_size(1024,2), '1.00 KB')
    eq_(format_size(1024,0,2), '1 MB')
    eq_(format_size(1024,2,2), '0.01 MB')
    eq_(format_size(1024,3,2), '0.001 MB')
    eq_(format_size(1024,3,2,False), '0.001')
    eq_(format_size(1023), '1023 B')
    eq_(format_size(1023,0,1), '1 KB')
    eq_(format_size(511,0,1), '1 KB')
    eq_(format_size(9), '9 B')
    eq_(format_size(99), '99 B')
    eq_(format_size(999), '999 B')
    eq_(format_size(9999), '10 KB')
    eq_(format_size(99999), '98 KB')
    eq_(format_size(999999), '977 KB')
    eq_(format_size(9999999), '10 MB')
    eq_(format_size(99999999), '96 MB')
    eq_(format_size(999999999), '954 MB')
    eq_(format_size(9999999999), '10 GB')
    eq_(format_size(99999999999), '94 GB')
    eq_(format_size(999999999999), '932 GB')
    eq_(format_size(9999999999999), '10 TB')
    eq_(format_size(99999999999999), '91 TB')
    eq_(format_size(999999999999999), '910 TB')
    eq_(format_size(9999999999999999), '9 PB')
    eq_(format_size(99999999999999999), '89 PB')
    eq_(format_size(999999999999999999), '889 PB')
    eq_(format_size(9999999999999999999), '9 EB')
    eq_(format_size(99999999999999999999), '87 EB')
    eq_(format_size(999999999999999999999), '868 EB')
    eq_(format_size(9999999999999999999999), '9 ZB')
    eq_(format_size(99999999999999999999999), '85 ZB')
    eq_(format_size(999999999999999999999999), '848 ZB')

def test_remove_invalid_xml():
    eq_(remove_invalid_xml('foo\0bar\x0bbaz'), 'foo bar baz')
    # surrogate blocks have to be replaced, but not the rest
    eq_(remove_invalid_xml('foo\ud800bar\udfffbaz\ue000'), 'foo bar baz\ue000')
    # replace with something else
    eq_(remove_invalid_xml('foo\0baz', replace_with='bar'), 'foobarbaz')

def test_multi_replace():
    eq_('136',multi_replace('123456',('2','45')))
    eq_('1 3 6',multi_replace('123456',('2','45'),' '))
    eq_('1 3  6',multi_replace('123456','245',' '))
    eq_('173896',multi_replace('123456','245','789'))
    eq_('173896',multi_replace('123456','245',('7','8','9')))
    eq_('17386',multi_replace('123456',('2','45'),'78'))
    eq_('17386',multi_replace('123456',('2','45'),('7','8')))
    with raises(ValueError):
        multi_replace('123456',('2','45'),('7','8','9'))
    eq_('17346',multi_replace('12346',('2','45'),'78'))

#--- Files

class TestCase_modified_after:
    def test_first_is_modified_after(self, monkeyplus):
        monkeyplus.patch_osstat('first', st_mtime=42)
        monkeyplus.patch_osstat('second', st_mtime=41)
        assert modified_after('first', 'second')

    def test_second_is_modified_after(self, monkeyplus):
        monkeyplus.patch_osstat('first', st_mtime=42)
        monkeyplus.patch_osstat('second', st_mtime=43)
        assert not modified_after('first', 'second')

    def test_same_mtime(self, monkeyplus):
        monkeyplus.patch_osstat('first', st_mtime=42)
        monkeyplus.patch_osstat('second', st_mtime=42)
        assert not modified_after('first', 'second')

    def test_first_file_does_not_exist(self, monkeyplus):
        # when the first file doesn't exist, we return False
        monkeyplus.patch_osstat('second', st_mtime=42)
        assert not modified_after('does_not_exist', 'second') # no crash

    def test_second_file_does_not_exist(self, monkeyplus):
        # when the second file doesn't exist, we return True
        monkeyplus.patch_osstat('first', st_mtime=42)
        assert modified_after('first', 'does_not_exist') # no crash

    def test_first_file_is_none(self, monkeyplus):
        # when the first file is None, we return False
        monkeyplus.patch_osstat('second', st_mtime=42)
        assert not modified_after(None, 'second') # no crash

    def test_second_file_is_none(self, monkeyplus):
        # when the second file is None, we return True
        monkeyplus.patch_osstat('first', st_mtime=42)
        assert modified_after('first', None) # no crash


class TestCase_delete_if_empty:
    def test_is_empty(self, tmpdir):
        testpath = Path(str(tmpdir))
        assert delete_if_empty(testpath)
        assert not testpath.exists()

    def test_not_empty(self, tmpdir):
        testpath = Path(str(tmpdir))
        testpath['foo'].mkdir()
        assert not delete_if_empty(testpath)
        assert testpath.exists()

    def test_with_files_to_delete(self, tmpdir):
        testpath = Path(str(tmpdir))
        testpath['foo'].open('w')
        testpath['bar'].open('w')
        assert delete_if_empty(testpath, ['foo', 'bar'])
        assert not testpath.exists()

    def test_directory_in_files_to_delete(self, tmpdir):
        testpath = Path(str(tmpdir))
        testpath['foo'].mkdir()
        assert not delete_if_empty(testpath, ['foo'])
        assert testpath.exists()

    def test_delete_files_to_delete_only_if_dir_is_empty(self, tmpdir):
        testpath = Path(str(tmpdir))
        testpath['foo'].open('w')
        testpath['bar'].open('w')
        assert not delete_if_empty(testpath, ['foo'])
        assert testpath.exists()
        assert testpath['foo'].exists()

    def test_doesnt_exist(self):
        # When the 'path' doesn't exist, just do nothing.
        delete_if_empty(Path('does_not_exist')) # no crash

    def test_is_file(self, tmpdir):
        # When 'path' is a file, do nothing.
        p = Path(str(tmpdir)) + 'filename'
        p.open('w').close()
        delete_if_empty(p) # no crash

    def test_ioerror(self, tmpdir, monkeypatch):
        # if an IO error happens during the operation, ignore it.
        def do_raise(*args, **kw):
            raise OSError()

        monkeypatch.setattr(Path, 'rmdir', do_raise)
        delete_if_empty(Path(str(tmpdir))) # no crash


class TestCase_open_if_filename:
    def test_file_name(self, tmpdir):
        filepath = str(tmpdir.join('test.txt'))
        open(filepath, 'wb').write(b'test_data')
        file, close = open_if_filename(filepath)
        assert close
        eq_(b'test_data', file.read())
        file.close()

    def test_opened_file(self):
        sio = StringIO()
        sio.write('test_data')
        sio.seek(0)
        file, close = open_if_filename(sio)
        assert not close
        eq_('test_data', file.read())

    def test_mode_is_passed_to_open(self, tmpdir):
        filepath = str(tmpdir.join('test.txt'))
        open(filepath, 'w').close()
        file, close = open_if_filename(filepath, 'a')
        eq_('a', file.mode)
        file.close()


class TestCase_FileOrPath:
    def test_path(self, tmpdir):
        filepath = str(tmpdir.join('test.txt'))
        open(filepath, 'wb').write(b'test_data')
        with FileOrPath(filepath) as fp:
            eq_(b'test_data', fp.read())

    def test_opened_file(self):
        sio = StringIO()
        sio.write('test_data')
        sio.seek(0)
        with FileOrPath(sio) as fp:
            eq_('test_data', fp.read())

    def test_mode_is_passed_to_open(self, tmpdir):
        filepath = str(tmpdir.join('test.txt'))
        open(filepath, 'w').close()
        with FileOrPath(filepath, 'a') as fp:
            eq_('a', fp.mode)

