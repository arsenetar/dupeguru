# Created By: Virgil Dupras
# Created On: 2006/02/27
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import time
import tempfile
import shutil

from pytest import raises
from hscommon import io
from hscommon.path import Path
from hscommon.testutil import eq_

from ..directories import *

def create_fake_fs(rootpath):
    # We have it as a separate function because other units are using it.
    rootpath = rootpath + 'fs'
    io.mkdir(rootpath)
    io.mkdir(rootpath + 'dir1')
    io.mkdir(rootpath + 'dir2')
    io.mkdir(rootpath + 'dir3')
    fp = io.open(rootpath + 'file1.test', 'w')
    fp.write('1')
    fp.close()
    fp = io.open(rootpath + 'file2.test', 'w')
    fp.write('12')
    fp.close()
    fp = io.open(rootpath + 'file3.test', 'w')
    fp.write('123')
    fp.close()
    fp = io.open(rootpath + ('dir1', 'file1.test'), 'w')
    fp.write('1')
    fp.close()
    fp = io.open(rootpath + ('dir2', 'file2.test'), 'w')
    fp.write('12')
    fp.close()
    fp = io.open(rootpath + ('dir3', 'file3.test'), 'w')
    fp.write('123')
    fp.close()
    return rootpath

def setup_module(module):
    # In this unit, we have tests depending on two directory structure. One with only one file in it
    # and another with a more complex structure.
    testpath = Path(tempfile.mkdtemp())
    module.testpath = testpath
    rootpath = testpath + 'onefile'
    io.mkdir(rootpath)
    fp = io.open(rootpath + 'test.txt', 'w')
    fp.write('test_data')
    fp.close()
    create_fake_fs(testpath)

def teardown_module(module):
    shutil.rmtree(str(module.testpath))

def test_empty():
    d = Directories()
    eq_(len(d), 0)
    assert 'foobar' not in d

def test_add_path():
    d = Directories()
    p = testpath + 'onefile'
    d.add_path(p)
    eq_(1,len(d))
    assert p in d
    assert (p + 'foobar') in d
    assert p[:-1] not in d
    p = testpath + 'fs'
    d.add_path(p)
    eq_(2,len(d))
    assert p in d

def test_AddPath_when_path_is_already_there():
    d = Directories()
    p = testpath + 'onefile'
    d.add_path(p)
    with raises(AlreadyThereError):
        d.add_path(p)
    with raises(AlreadyThereError):
        d.add_path(p + 'foobar')
    eq_(1, len(d))

def test_add_path_containing_paths_already_there():
    d = Directories()
    d.add_path(testpath + 'onefile')
    eq_(1, len(d))
    d.add_path(testpath)
    eq_(len(d), 1)
    eq_(d[0], testpath)

def test_AddPath_non_latin(tmpdir):
	p = Path(str(tmpdir))
	to_add = p + 'unicode\u201a'
	os.mkdir(str(to_add))
	d = Directories()
	try:
		d.add_path(to_add)
	except UnicodeDecodeError:
		assert False

def test_del():
    d = Directories()
    d.add_path(testpath + 'onefile')
    try:
        del d[1]
        assert False
    except IndexError:
        pass
    d.add_path(testpath + 'fs')
    del d[1]
    eq_(1, len(d))

def test_states():
    d = Directories()
    p = testpath + 'onefile'
    d.add_path(p)
    eq_(STATE_NORMAL,d.get_state(p))
    d.set_state(p,STATE_REFERENCE)
    eq_(STATE_REFERENCE,d.get_state(p))
    eq_(STATE_REFERENCE,d.get_state(p + 'dir1'))
    eq_(1,len(d.states))
    eq_(p,list(d.states.keys())[0])
    eq_(STATE_REFERENCE,d.states[p])

def test_get_state_with_path_not_there():
    # When the path's not there, just return STATE_NORMAL
    d = Directories()
    d.add_path(testpath + 'onefile')
    eq_(d.get_state(testpath), STATE_NORMAL)

def test_states_remain_when_larger_directory_eat_smaller_ones():
    d = Directories()
    p = testpath + 'onefile'
    d.add_path(p)
    d.set_state(p,STATE_EXCLUDED)
    d.add_path(testpath)
    d.set_state(testpath,STATE_REFERENCE)
    eq_(STATE_EXCLUDED,d.get_state(p))
    eq_(STATE_EXCLUDED,d.get_state(p + 'dir1'))
    eq_(STATE_REFERENCE,d.get_state(testpath))

def test_set_state_keep_state_dict_size_to_minimum():
    d = Directories()
    p = testpath + 'fs'
    d.add_path(p)
    d.set_state(p,STATE_REFERENCE)
    d.set_state(p + 'dir1',STATE_REFERENCE)
    eq_(1,len(d.states))
    eq_(STATE_REFERENCE,d.get_state(p + 'dir1'))
    d.set_state(p + 'dir1',STATE_NORMAL)
    eq_(2,len(d.states))
    eq_(STATE_NORMAL,d.get_state(p + 'dir1'))
    d.set_state(p + 'dir1',STATE_REFERENCE)
    eq_(1,len(d.states))
    eq_(STATE_REFERENCE,d.get_state(p + 'dir1'))

def test_get_files():
    d = Directories()
    p = testpath + 'fs'
    d.add_path(p)
    d.set_state(p + 'dir1',STATE_REFERENCE)
    d.set_state(p + 'dir2',STATE_EXCLUDED)
    files = list(d.get_files())
    eq_(5, len(files))
    for f in files:
        if f.path[:-1] == p + 'dir1':
            assert f.is_ref
        else:
            assert not f.is_ref

def test_get_files_with_inherited_exclusion():
    d = Directories()
    p = testpath + 'onefile'
    d.add_path(p)
    d.set_state(p,STATE_EXCLUDED)
    eq_([], list(d.get_files()))

def test_save_and_load(tmpdir):
    d1 = Directories()
    d2 = Directories()
    p1 = Path(str(tmpdir.join('p1')))
    io.mkdir(p1)
    p2 = Path(str(tmpdir.join('p2')))
    io.mkdir(p2)
    d1.add_path(p1)
    d1.add_path(p2)
    d1.set_state(p1, STATE_REFERENCE)
    d1.set_state(p1 + 'dir1',STATE_EXCLUDED)
    tmpxml = str(tmpdir.join('directories_testunit.xml'))
    d1.save_to_file(tmpxml)
    d2.load_from_file(tmpxml)
    eq_(2, len(d2))
    eq_(STATE_REFERENCE,d2.get_state(p1))
    eq_(STATE_EXCLUDED,d2.get_state(p1 + 'dir1'))

def test_invalid_path():
    d = Directories()
    p = Path('does_not_exist')
    with raises(InvalidPathError):
        d.add_path(p)
    eq_(0, len(d))

def test_set_state_on_invalid_path():
    d = Directories()
    try:
        d.set_state(Path('foobar',),STATE_NORMAL)
    except LookupError:
        assert False

def test_load_from_file_with_invalid_path(tmpdir):
    #This test simulates a load from file resulting in a
    #InvalidPath raise. Other directories must be loaded.
    d1 = Directories()
    d1.add_path(testpath + 'onefile')
    #Will raise InvalidPath upon loading
    p = Path(str(tmpdir.join('toremove')))
    io.mkdir(p)
    d1.add_path(p)
    io.rmdir(p)
    tmpxml = str(tmpdir.join('directories_testunit.xml'))
    d1.save_to_file(tmpxml)
    d2 = Directories()
    d2.load_from_file(tmpxml)
    eq_(1, len(d2))

def test_unicode_save(tmpdir):
    d = Directories()
    p1 = Path(str(tmpdir)) + 'hello\xe9'
    io.mkdir(p1)
    io.mkdir(p1 + 'foo\xe9')
    d.add_path(p1)
    d.set_state(p1 + 'foo\xe9', STATE_EXCLUDED)
    tmpxml = str(tmpdir.join('directories_testunit.xml'))
    try:
        d.save_to_file(tmpxml)
    except UnicodeDecodeError:
        assert False

def test_get_files_refreshes_its_directories():
    d = Directories()
    p = testpath + 'fs'
    d.add_path(p)
    files = d.get_files()
    eq_(6, len(list(files)))
    time.sleep(1)
    os.remove(str(p + ('dir1','file1.test')))
    files = d.get_files()
    eq_(5, len(list(files)))

def test_get_files_does_not_choke_on_non_existing_directories(tmpdir):
    d = Directories()
    p = Path(str(tmpdir))
    d.add_path(p)
    io.rmtree(p)
    eq_([], list(d.get_files()))

def test_get_state_returns_excluded_by_default_for_hidden_directories(tmpdir):
    d = Directories()
    p = Path(str(tmpdir))
    hidden_dir_path = p + '.foo'
    io.mkdir(p + '.foo')
    d.add_path(p)
    eq_(d.get_state(hidden_dir_path), STATE_EXCLUDED)
    # But it can be overriden
    d.set_state(hidden_dir_path, STATE_NORMAL)
    eq_(d.get_state(hidden_dir_path), STATE_NORMAL)

def test_default_path_state_override(tmpdir):
    # It's possible for a subclass to override the default state of a path
    class MyDirectories(Directories):
        def _default_state_for_path(self, path):
            if 'foobar' in path:
                return STATE_EXCLUDED
    
    d = MyDirectories()
    p1 = Path(str(tmpdir))
    io.mkdir(p1 + 'foobar')
    io.open(p1 + 'foobar/somefile', 'w').close()
    io.mkdir(p1 + 'foobaz')
    io.open(p1 + 'foobaz/somefile', 'w').close()
    d.add_path(p1)
    eq_(d.get_state(p1 + 'foobaz'), STATE_NORMAL)
    eq_(d.get_state(p1 + 'foobar'), STATE_EXCLUDED)
    eq_(len(list(d.get_files())), 1) # only the 'foobaz' file is there
    # However, the default state can be changed
    d.set_state(p1 + 'foobar', STATE_NORMAL)
    eq_(d.get_state(p1 + 'foobar'), STATE_NORMAL)
    eq_(len(list(d.get_files())), 2)

