# Created By: Virgil Dupras
# Created On: 2006/02/27
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import os
import time

from nose.tools import eq_

from hsutil import io
from hsutil.path import Path
from hsutil.testcase import TestCase

from ..directories import *

testpath = Path(TestCase.datadirpath())

def create_fake_fs(rootpath):
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

class TCDirectories(TestCase):
    def test_empty(self):
        d = Directories()
        self.assertEqual(0,len(d))
        self.assert_('foobar' not in d)
    
    def test_add_path(self):
        d = Directories()
        p = testpath + 'utils'
        d.add_path(p)
        self.assertEqual(1,len(d))
        self.assert_(p in d)
        self.assert_((p + 'foobar') in d)
        self.assert_(p[:-1] not in d)
        p = self.tmppath()
        d.add_path(p)
        self.assertEqual(2,len(d))
        self.assert_(p in d)
    
    def test_AddPath_when_path_is_already_there(self):
        d = Directories()
        p = testpath + 'utils'
        d.add_path(p)
        self.assertRaises(AlreadyThereError, d.add_path, p)
        self.assertRaises(AlreadyThereError, d.add_path, p + 'foobar')
        self.assertEqual(1, len(d))
    
    def test_add_path_containing_paths_already_there(self):
        d = Directories()
        d.add_path(testpath + 'utils')
        self.assertEqual(1, len(d))
        d.add_path(testpath)
        eq_(len(d), 1)
        eq_(d[0], testpath)
    
    def test_AddPath_non_latin(self):
    	p = Path(self.tmpdir())
    	to_add = p + u'unicode\u201a'
    	os.mkdir(unicode(to_add))
    	d = Directories()
    	try:
    		d.add_path(to_add)
    	except UnicodeDecodeError:
    		self.fail()
    
    def test_del(self):
        d = Directories()
        d.add_path(testpath + 'utils')
        try:
            del d[1]
            self.fail()
        except IndexError:
            pass
        d.add_path(self.tmppath())
        del d[1]
        self.assertEqual(1, len(d))
    
    def test_states(self):
        d = Directories()
        p = testpath + 'utils'
        d.add_path(p)
        self.assertEqual(STATE_NORMAL,d.get_state(p))
        d.set_state(p,STATE_REFERENCE)
        self.assertEqual(STATE_REFERENCE,d.get_state(p))
        self.assertEqual(STATE_REFERENCE,d.get_state(p + 'dir1'))
        self.assertEqual(1,len(d.states))
        self.assertEqual(p,d.states.keys()[0])
        self.assertEqual(STATE_REFERENCE,d.states[p])
    
    def test_get_state_with_path_not_there(self):
        # When the path's not there, just return STATE_NORMAL
        d = Directories()
        d.add_path(testpath + 'utils')
        eq_(d.get_state(testpath), STATE_NORMAL)
    
    def test_states_remain_when_larger_directory_eat_smaller_ones(self):
        d = Directories()
        p = testpath + 'utils'
        d.add_path(p)
        d.set_state(p,STATE_EXCLUDED)
        d.add_path(testpath)
        d.set_state(testpath,STATE_REFERENCE)
        self.assertEqual(STATE_EXCLUDED,d.get_state(p))
        self.assertEqual(STATE_EXCLUDED,d.get_state(p + 'dir1'))
        self.assertEqual(STATE_REFERENCE,d.get_state(testpath))
    
    def test_set_state_keep_state_dict_size_to_minimum(self):
        d = Directories()
        p = create_fake_fs(self.tmppath())
        d.add_path(p)
        d.set_state(p,STATE_REFERENCE)
        d.set_state(p + 'dir1',STATE_REFERENCE)
        self.assertEqual(1,len(d.states))
        self.assertEqual(STATE_REFERENCE,d.get_state(p + 'dir1'))
        d.set_state(p + 'dir1',STATE_NORMAL)
        self.assertEqual(2,len(d.states))
        self.assertEqual(STATE_NORMAL,d.get_state(p + 'dir1'))
        d.set_state(p + 'dir1',STATE_REFERENCE)
        self.assertEqual(1,len(d.states))
        self.assertEqual(STATE_REFERENCE,d.get_state(p + 'dir1'))
    
    def test_get_files(self):
        d = Directories()
        p = create_fake_fs(self.tmppath())
        d.add_path(p)
        d.set_state(p + 'dir1',STATE_REFERENCE)
        d.set_state(p + 'dir2',STATE_EXCLUDED)
        files = list(d.get_files())
        self.assertEqual(5, len(files))
        for f in files:
            if f.path[:-1] == p + 'dir1':
                assert f.is_ref
            else:
                assert not f.is_ref
    
    def test_get_files_with_inherited_exclusion(self):
        d = Directories()
        p = testpath + 'utils'
        d.add_path(p)
        d.set_state(p,STATE_EXCLUDED)
        self.assertEqual([], list(d.get_files()))
    
    def test_save_and_load(self):
        d1 = Directories()
        d2 = Directories()
        p1 = self.tmppath()
        p2 = self.tmppath()
        d1.add_path(p1)
        d1.add_path(p2)
        d1.set_state(p1, STATE_REFERENCE)
        d1.set_state(p1 + 'dir1',STATE_EXCLUDED)
        tmpxml = op.join(self.tmpdir(), 'directories_testunit.xml')
        d1.save_to_file(tmpxml)
        d2.load_from_file(tmpxml)
        self.assertEqual(2, len(d2))
        self.assertEqual(STATE_REFERENCE,d2.get_state(p1))
        self.assertEqual(STATE_EXCLUDED,d2.get_state(p1 + 'dir1'))
    
    def test_invalid_path(self):
        d = Directories()
        p = Path('does_not_exist')
        self.assertRaises(InvalidPathError, d.add_path, p)
        self.assertEqual(0, len(d))
    
    def test_set_state_on_invalid_path(self):
        d = Directories()
        try:
            d.set_state(Path('foobar',),STATE_NORMAL)
        except LookupError:
            self.fail()
    
    def test_load_from_file_with_invalid_path(self):
        #This test simulates a load from file resulting in a
        #InvalidPath raise. Other directories must be loaded.
        d1 = Directories()
        d1.add_path(testpath + 'utils')
        #Will raise InvalidPath upon loading
        p = self.tmppath()
        d1.add_path(p)
        io.rmdir(p)
        tmpxml = op.join(self.tmpdir(), 'directories_testunit.xml')
        d1.save_to_file(tmpxml)
        d2 = Directories()
        d2.load_from_file(tmpxml)
        self.assertEqual(1, len(d2))
    
    def test_unicode_save(self):
        d = Directories()
        p1 = self.tmppath() + u'hello\xe9'
        io.mkdir(p1)
        io.mkdir(p1 + u'foo\xe9')
        d.add_path(p1)
        d.set_state(p1 + u'foo\xe9', STATE_EXCLUDED)
        tmpxml = op.join(self.tmpdir(), 'directories_testunit.xml')
        try:
            d.save_to_file(tmpxml)
        except UnicodeDecodeError:
            self.fail()
    
    def test_get_files_refreshes_its_directories(self):
        d = Directories()
        p = create_fake_fs(self.tmppath())
        d.add_path(p)
        files = d.get_files()
        self.assertEqual(6, len(list(files)))
        time.sleep(1)
        os.remove(str(p + ('dir1','file1.test')))
        files = d.get_files()
        self.assertEqual(5, len(list(files)))
    
    def test_get_files_does_not_choke_on_non_existing_directories(self):
        d = Directories()
        p = Path(self.tmpdir())
        d.add_path(p)
        io.rmtree(p)
        self.assertEqual([], list(d.get_files()))
    
    def test_get_state_returns_excluded_by_default_for_hidden_directories(self):
        d = Directories()
        p = Path(self.tmpdir())
        hidden_dir_path = p + '.foo'
        io.mkdir(p + '.foo')
        d.add_path(p)
        self.assertEqual(d.get_state(hidden_dir_path), STATE_EXCLUDED)
        # But it can be overriden
        d.set_state(hidden_dir_path, STATE_NORMAL)
        self.assertEqual(d.get_state(hidden_dir_path), STATE_NORMAL)
    
    def test_default_path_state_override(self):
        # It's possible for a subclass to override the default state of a path
        class MyDirectories(Directories):
            def _default_state_for_path(self, path):
                if 'foobar' in path:
                    return STATE_EXCLUDED
        
        d = MyDirectories()
        p1 = self.tmppath()
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
    
